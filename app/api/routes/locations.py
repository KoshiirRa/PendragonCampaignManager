from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query, status

from app.api.dependencies import DB
from app.schemas.location import (
    DefenseLayerCreate,
    DefenseLayerRead,
    HouseholdEmploymentCreate,
    HouseholdEmploymentRead,
    LocationCreate,
    LocationRead,
    LocationUpdate,
    ManorAnnualResolutionCreate,
    ManorAnnualResolutionRead,
    ManorAssetCreate,
    ManorAssetEntryCreate,
    ManorAssetEntryRead,
    ManorAssetRead,
    ManorCreate,
    ManorImprovementCreate,
    ManorImprovementLedgerCreate,
    ManorImprovementLedgerRead,
    ManorImprovementRead,
    ManorRead,
    ManorTenureCreate,
    ManorTenureRead,
    TreasuryEntryCreate,
    TreasuryEntryRead,
)
from app.services import locations as service

router = APIRouter(prefix="/campaigns/{campaign_id}", tags=["locations"])


@router.get("/locations", response_model=list[LocationRead])
async def list_locations(
    campaign_id: UUID, db: DB, kind: Annotated[str | None, Query(max_length=50)] = None
):
    return await service.list_locations(db, campaign_id, kind)


@router.post("/locations", response_model=LocationRead, status_code=status.HTTP_201_CREATED)
async def create_location(campaign_id: UUID, data: LocationCreate, db: DB):
    return await service.create_location(db, campaign_id, data)


@router.get("/locations/{location_id}", response_model=LocationRead)
async def get_location(campaign_id: UUID, location_id: UUID, db: DB):
    return await service.get_location(db, campaign_id, location_id)


@router.patch("/locations/{location_id}", response_model=LocationRead)
async def update_location(campaign_id: UUID, location_id: UUID, data: LocationUpdate, db: DB):
    return await service.update_location(db, campaign_id, location_id, data)


@router.delete("/locations/{location_id}", status_code=status.HTTP_204_NO_CONTENT)
async def archive_location(campaign_id: UUID, location_id: UUID, db: DB):
    await service.archive_location(db, campaign_id, location_id)


@router.get("/manors", response_model=list[ManorRead])
async def list_manors(campaign_id: UUID, db: DB):
    return await service.list_manors(db, campaign_id)


@router.post("/manors", response_model=ManorRead, status_code=status.HTTP_201_CREATED)
async def create_manor(campaign_id: UUID, data: ManorCreate, db: DB):
    return await service.create_manor(db, campaign_id, data)


@router.post(
    "/manors/{manor_id}/tenures",
    response_model=ManorTenureRead,
    status_code=status.HTTP_201_CREATED,
)
async def add_tenure(campaign_id: UUID, manor_id: UUID, data: ManorTenureCreate, db: DB):
    return await service.add_tenure(db, campaign_id, manor_id, data)


@router.get("/manors/{manor_id}/tenures", response_model=list[ManorTenureRead])
async def list_tenures(campaign_id: UUID, manor_id: UUID, db: DB):
    return await service.list_tenures(db, campaign_id, manor_id)


@router.post(
    "/manors/{manor_id}/improvements",
    response_model=ManorImprovementRead,
    status_code=status.HTTP_201_CREATED,
)
async def add_improvement(campaign_id: UUID, manor_id: UUID, data: ManorImprovementCreate, db: DB):
    return await service.add_improvement(db, campaign_id, manor_id, data)


@router.get("/manors/{manor_id}/improvements", response_model=list[ManorImprovementRead])
async def list_improvements(campaign_id: UUID, manor_id: UUID, db: DB):
    return await service.list_improvements(db, campaign_id, manor_id)


@router.post(
    "/manors/{manor_id}/improvements/{improvement_id}/ledger",
    response_model=ManorImprovementLedgerRead,
    status_code=status.HTTP_201_CREATED,
)
async def add_improvement_entry(
    campaign_id: UUID,
    manor_id: UUID,
    improvement_id: UUID,
    data: ManorImprovementLedgerCreate,
    db: DB,
):
    return await service.add_improvement_entry(db, campaign_id, manor_id, improvement_id, data)


@router.get(
    "/manors/{manor_id}/improvements/{improvement_id}/ledger",
    response_model=list[ManorImprovementLedgerRead],
)
async def list_improvement_ledger(campaign_id: UUID, manor_id: UUID, improvement_id: UUID, db: DB):
    return await service.list_improvement_ledger(db, campaign_id, manor_id, improvement_id)


@router.get("/manors/{manor_id}/annual-resolutions", response_model=list[ManorAnnualResolutionRead])
async def list_annual_resolutions(campaign_id: UUID, manor_id: UUID, db: DB):
    return await service.list_annual_resolutions(db, campaign_id, manor_id)


@router.post(
    "/manors/{manor_id}/annual-resolutions",
    response_model=ManorAnnualResolutionRead,
    status_code=201,
)
async def create_annual_resolution(
    campaign_id: UUID, manor_id: UUID, data: ManorAnnualResolutionCreate, db: DB
):
    return await service.create_annual_resolution(db, campaign_id, manor_id, data)


@router.get("/manors/{manor_id}/treasury", response_model=list[TreasuryEntryRead])
async def list_treasury(campaign_id: UUID, manor_id: UUID, db: DB):
    return await service.list_treasury(db, campaign_id, manor_id)


@router.post("/manors/{manor_id}/treasury", response_model=TreasuryEntryRead, status_code=201)
async def add_treasury_entry(campaign_id: UUID, manor_id: UUID, data: TreasuryEntryCreate, db: DB):
    return await service.add_treasury_entry(db, campaign_id, manor_id, data)


@router.post("/manors/{manor_id}/assets", response_model=ManorAssetRead, status_code=201)
async def add_asset(campaign_id: UUID, manor_id: UUID, data: ManorAssetCreate, db: DB):
    return await service.add_asset(db, campaign_id, manor_id, data)


@router.get("/manors/{manor_id}/assets", response_model=list[ManorAssetRead])
async def list_assets(campaign_id: UUID, manor_id: UUID, db: DB):
    return await service.list_assets(db, campaign_id, manor_id)


@router.post(
    "/manors/{manor_id}/assets/{asset_id}/ledger",
    response_model=ManorAssetEntryRead,
    status_code=201,
)
async def add_asset_entry(
    campaign_id: UUID, manor_id: UUID, asset_id: UUID, data: ManorAssetEntryCreate, db: DB
):
    return await service.add_asset_entry(db, campaign_id, manor_id, asset_id, data)


@router.get("/manors/{manor_id}/assets/{asset_id}/ledger", response_model=list[ManorAssetEntryRead])
async def list_asset_ledger(campaign_id: UUID, manor_id: UUID, asset_id: UUID, db: DB):
    return await service.list_asset_ledger(db, campaign_id, manor_id, asset_id)


@router.post(
    "/manors/{manor_id}/household", response_model=HouseholdEmploymentRead, status_code=201
)
async def add_household_employment(
    campaign_id: UUID, manor_id: UUID, data: HouseholdEmploymentCreate, db: DB
):
    return await service.add_employment(db, campaign_id, manor_id, data)


@router.get("/manors/{manor_id}/household", response_model=list[HouseholdEmploymentRead])
async def list_household_employment(campaign_id: UUID, manor_id: UUID, db: DB):
    return await service.list_employment(db, campaign_id, manor_id)


@router.post("/manors/{manor_id}/defenses", response_model=DefenseLayerRead, status_code=201)
async def add_defense(campaign_id: UUID, manor_id: UUID, data: DefenseLayerCreate, db: DB):
    return await service.add_defense(db, campaign_id, manor_id, data)


@router.get("/manors/{manor_id}/defenses", response_model=list[DefenseLayerRead])
async def list_defenses(campaign_id: UUID, manor_id: UUID, db: DB):
    return await service.list_defenses(db, campaign_id, manor_id)
