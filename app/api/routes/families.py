from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query, status

from app.api.dependencies import DB
from app.schemas.family import (
    FamilyCreate,
    FamilyHistoryCreate,
    FamilyHistoryRead,
    FamilyMembershipCreate,
    FamilyMembershipRead,
    FamilyRead,
    InheritanceCaseCreate,
    InheritanceCaseRead,
    InheritanceHeirCreate,
    InheritanceHeirRead,
    InheritanceTransferCreate,
    InheritanceTransferRead,
    MarriageCreate,
    MarriageRead,
    ParentageCreate,
    ParentageRead,
    SourceReferenceCreate,
    SourceReferenceRead,
)
from app.services import families as service

router = APIRouter(prefix="/campaigns/{campaign_id}", tags=["families"])


@router.get("/families", response_model=list[FamilyRead])
async def list_families(campaign_id: UUID, db: DB):
    return await service.list_families(db, campaign_id)


@router.post("/families", response_model=FamilyRead, status_code=status.HTTP_201_CREATED)
async def create_family(campaign_id: UUID, data: FamilyCreate, db: DB):
    return await service.create_family(db, campaign_id, data)


@router.post(
    "/families/{family_id}/memberships", response_model=FamilyMembershipRead, status_code=201
)
async def add_membership(campaign_id: UUID, family_id: UUID, data: FamilyMembershipCreate, db: DB):
    return await service.add_membership(db, campaign_id, family_id, data)


@router.post("/parentage", response_model=ParentageRead, status_code=201)
async def add_parentage(campaign_id: UUID, data: ParentageCreate, db: DB):
    return await service.add_parentage(db, campaign_id, data)


@router.post("/marriages", response_model=MarriageRead, status_code=201)
async def add_marriage(campaign_id: UUID, data: MarriageCreate, db: DB):
    return await service.add_marriage(db, campaign_id, data)


@router.post("/inheritance-cases", response_model=InheritanceCaseRead, status_code=201)
async def create_inheritance_case(campaign_id: UUID, data: InheritanceCaseCreate, db: DB):
    return await service.create_inheritance_case(db, campaign_id, data)


@router.post(
    "/inheritance-cases/{case_id}/heirs", response_model=InheritanceHeirRead, status_code=201
)
async def add_heir(campaign_id: UUID, case_id: UUID, data: InheritanceHeirCreate, db: DB):
    return await service.add_heir(db, campaign_id, case_id, data)


@router.post(
    "/inheritance-cases/{case_id}/manor-transfers",
    response_model=InheritanceTransferRead,
    status_code=201,
)
async def transfer_manor(campaign_id: UUID, case_id: UUID, data: InheritanceTransferCreate, db: DB):
    return await service.transfer_manor(db, campaign_id, case_id, data)


@router.get("/source-references", response_model=list[SourceReferenceRead])
async def list_sources(campaign_id: UUID, db: DB):
    return await service.list_sources(db, campaign_id)


@router.post("/source-references", response_model=SourceReferenceRead, status_code=201)
async def create_source(campaign_id: UUID, data: SourceReferenceCreate, db: DB):
    return await service.create_source(db, campaign_id, data)


@router.get("/families/{family_id}/history", response_model=list[FamilyHistoryRead])
async def list_history(
    campaign_id: UUID,
    family_id: UUID,
    db: DB,
    before_year: Annotated[int | None, Query(ge=1, le=9999)] = None,
):
    return await service.list_history(db, campaign_id, family_id, before_year)


@router.post("/families/{family_id}/history", response_model=FamilyHistoryRead, status_code=201)
async def add_history(campaign_id: UUID, family_id: UUID, data: FamilyHistoryCreate, db: DB):
    return await service.add_history(db, campaign_id, family_id, data)
