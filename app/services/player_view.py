from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    AnnualChronicle,
    AnnualChronicleSection,
    Character,
    CharacterKind,
    CharacterStatus,
    Event,
    EventVisibility,
    Family,
    FamilyMembership,
    GloryLedger,
    KnowledgeScope,
    Location,
    Manor,
    ManorAsset,
    ManorDefenseLayer,
    ManorImprovement,
    ManorImprovementLedger,
    ManorTenure,
)
from app.schemas.player_view import (
    CampaignPlayerView,
    PlayerChronicle,
    PlayerChronicleSection,
    PlayerEvent,
    PlayerFamily,
    PlayerFamilyMember,
    PlayerManor,
    PlayerManorDefense,
    PlayerManorItem,
    PlayerPerson,
)
from app.services.campaigns import get_campaign, get_campaign_by_slug


async def get_player_view(db: AsyncSession, campaign_id: UUID) -> CampaignPlayerView:
    campaign = await get_campaign(db, campaign_id)
    visible_scopes = (KnowledgeScope.PLAYERS, KnowledgeScope.SHARED)

    events = list(
        await db.scalars(
            select(Event)
            .where(
                Event.campaign_id == campaign_id,
                Event.visibility.in_((EventVisibility.PLAYERS, EventVisibility.PUBLIC)),
            )
            .order_by(Event.in_game_year, Event.sequence, Event.recorded_at)
        )
    )

    people = (
        await db.execute(
            select(Character, func.coalesce(func.sum(GloryLedger.amount), 0))
            .outerjoin(
                GloryLedger,
                and_(
                    GloryLedger.character_id == Character.id,
                    GloryLedger.scope.in_(visible_scopes),
                ),
            )
            .where(
                Character.campaign_id == campaign_id,
                Character.kind == CharacterKind.PLAYER_KNIGHT,
                Character.status == CharacterStatus.ALIVE,
                Character.archived_at.is_(None),
            )
            .group_by(Character.id)
            .order_by(Character.name)
        )
    ).all()
    people_rows = [
        PlayerPerson(
            id=character.id,
            name=character.name,
            player_name=character.player_name or "Player unrecorded",
            description=character.public_description,
            glory=glory or 0,
        )
        for character, glory in people
    ]

    families = list(
        await db.scalars(
            select(Family)
            .where(
                Family.campaign_id == campaign_id,
                Family.archived_at.is_(None),
                Family.scope.in_(visible_scopes),
            )
            .order_by(Family.name)
        )
    )
    family_rows = []
    for family in families:
        memberships = (
            await db.execute(
                select(FamilyMembership, Character)
                .join(Character, Character.id == FamilyMembership.character_id)
                .where(
                    FamilyMembership.family_id == family.id,
                    FamilyMembership.scope.in_(visible_scopes),
                )
                .order_by(Character.name)
            )
        ).all()
        origin = (
            await db.get(Location, family.origin_location_id) if family.origin_location_id else None
        )
        family_rows.append(
            PlayerFamily(
                id=family.id,
                name=family.name,
                founding_year=family.founding_year,
                culture=family.culture,
                coat_of_arms=family.coat_of_arms,
                motto=family.motto,
                notes=family.notes,
                origin_location=origin.name if origin else None,
                members=[
                    PlayerFamilyMember(
                        id=c.id,
                        name=c.name,
                        membership_type=m.membership_type,
                        start_year=m.start_year,
                        end_year=m.end_year,
                    )
                    for m, c in memberships
                ],
            )
        )

    manor_pairs = (
        await db.execute(
            select(Manor, Location)
            .join(Location, Location.id == Manor.location_id)
            .where(
                Manor.campaign_id == campaign_id,
                Location.archived_at.is_(None),
                Location.scope.in_(visible_scopes),
            )
            .order_by(Location.name)
        )
    ).all()
    manor_rows = []
    for manor, location in manor_pairs:
        holder = await db.scalar(
            select(Character.name)
            .join(ManorTenure, ManorTenure.holder_character_id == Character.id)
            .where(ManorTenure.manor_id == manor.id, ManorTenure.end_year.is_(None))
        )
        improvements = list(
            await db.scalars(
                select(ManorImprovement)
                .where(ManorImprovement.manor_id == manor.id)
                .order_by(ManorImprovement.name)
            )
        )
        improvement_rows = []
        for item in improvements:
            status = await db.scalar(
                select(ManorImprovementLedger.status)
                .where(ManorImprovementLedger.improvement_id == item.id)
                .order_by(ManorImprovementLedger.effective_year.desc())
                .limit(1)
            )
            improvement_rows.append(
                PlayerManorItem(
                    id=item.id, name=item.name, description=item.description, status=status
                )
            )
        assets = list(
            await db.scalars(
                select(ManorAsset)
                .where(ManorAsset.manor_id == manor.id, ManorAsset.asset_type == "special_feature")
                .order_by(ManorAsset.name)
            )
        )
        defenses = list(
            await db.scalars(
                select(ManorDefenseLayer)
                .where(ManorDefenseLayer.manor_id == manor.id)
                .order_by(ManorDefenseLayer.ring_order)
            )
        )
        manor_rows.append(
            PlayerManor(
                id=manor.id,
                name=location.name,
                description=location.description,
                holder=holder,
                customary_income=manor.customary_income,
                population=manor.population,
                base_defensive_value=manor.base_defensive_value,
                improvements=improvement_rows,
                special_features=[
                    PlayerManorItem(id=a.id, name=a.name, description=a.description) for a in assets
                ],
                defenses=[
                    PlayerManorDefense(id=d.id, name=d.name, defensive_value=d.defensive_value)
                    for d in defenses
                ],
            )
        )

    latest_revisions = (
        select(
            AnnualChronicle.in_game_year.label("year"),
            func.max(AnnualChronicle.revision).label("revision"),
        )
        .where(
            AnnualChronicle.campaign_id == campaign_id,
            AnnualChronicle.status == "published",
        )
        .group_by(AnnualChronicle.in_game_year)
        .subquery()
    )
    chronicles = list(
        await db.scalars(
            select(AnnualChronicle)
            .join(
                latest_revisions,
                (AnnualChronicle.in_game_year == latest_revisions.c.year)
                & (AnnualChronicle.revision == latest_revisions.c.revision),
            )
            .where(AnnualChronicle.campaign_id == campaign_id)
            .order_by(AnnualChronicle.in_game_year)
        )
    )
    chronicle_rows = []
    for chronicle in chronicles:
        sections = list(
            await db.scalars(
                select(AnnualChronicleSection)
                .where(AnnualChronicleSection.chronicle_id == chronicle.id)
                .order_by(AnnualChronicleSection.position)
            )
        )
        chronicle_rows.append(
            PlayerChronicle(
                id=chronicle.id,
                year=chronicle.in_game_year,
                revision=chronicle.revision,
                title=chronicle.title,
                opening=chronicle.opening,
                closing=chronicle.closing,
                sections=[
                    PlayerChronicleSection(
                        character_id=section.character_id,
                        heading=section.heading,
                        body=section.body,
                    )
                    for section in sections
                ],
            )
        )

    return CampaignPlayerView(
        campaign_id=campaign.id,
        campaign_name=campaign.name,
        current_year=campaign.current_year,
        events=[
            PlayerEvent(
                id=e.id,
                year=e.in_game_year,
                date=e.in_game_date,
                event_type=e.event_type,
                title=e.title,
                description=e.description,
            )
            for e in events
        ],
        people=people_rows,
        families=family_rows,
        manors=manor_rows,
        chronicles=chronicle_rows,
    )


async def get_player_view_by_slug(db: AsyncSession, slug: str) -> CampaignPlayerView:
    campaign = await get_campaign_by_slug(db, slug)
    return await get_player_view(db, campaign.id)
