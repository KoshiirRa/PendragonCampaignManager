from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query, status

from app.api.dependencies import DB
from app.schemas.location import (
    LocationCreate,
    LocationRead,
    LocationUpdate,
    ManorCreate,
    ManorImprovementCreate,
    ManorImprovementLedgerCreate,
    ManorImprovementLedgerRead,
    ManorImprovementRead,
    ManorRead,
    ManorTenureCreate,
    ManorTenureRead,
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


@router.post(
    "/manors/{manor_id}/improvements",
    response_model=ManorImprovementRead,
    status_code=status.HTTP_201_CREATED,
)
async def add_improvement(campaign_id: UUID, manor_id: UUID, data: ManorImprovementCreate, db: DB):
    return await service.add_improvement(db, campaign_id, manor_id, data)


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
