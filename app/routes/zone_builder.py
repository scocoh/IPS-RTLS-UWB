# Name: zone_builder.py
# Version: 0.1.0
# Created: 971201
# Modified: 250502
# Creator: ParcoAdmin
# Modified By: ParcoAdmin
# Description: Python script for ParcoRTLS backend
# Location: /home/parcoadmin/parco_fastapi/app/routes
# Role: Backend
# Status: Active
# Dependent: TRUE

# VERSION 250316 /home/parcoadmin/parco_fastapi/app/routes/zone_builder.py 0P.10B.01
#  
# ParcoRTLS Middletier Services, ParcoRTLS DLL, ParcoDatabases, ParcoMessaging, and other code
# Copyright (C) 1999 - 2025 Affiliated Commercial Services Inc.
# Invented by Scott Cohen & Bertrand Dugal.
# Coded by Jesse Chunn O.B.M.'24 and Michael Farnsworth and Others
# Published at GitHub https://github.com/scocoh/IPS-RTLS-UWB
#
# Licensed under AGPL-3.0: https://www.gnu.org/licenses/agpl-3.0.en.html

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from database.db import get_async_db_pool
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# ✅ Pydantic model for incoming zone data
class ZoneCreate(BaseModel):
    zone_name: str
    map_id: int
    zone_level: int
    parent_zone_id: int | None = None
    vertices: list[dict] = []

# ✅ Get Zone Types from Database
@router.get("/get_zone_types")
async def get_zone_types():
    pool = await get_async_db_pool("data")
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT i_typ_zn, x_dsc_zn FROM tlkzonetypes ORDER BY i_typ_zn;")
    
    if not rows:
        raise HTTPException(status_code=404, detail="No zone types found")

    api_mapping = {1: "/create_zone", 2: "/create_zone", 3: "/create_zone", 4: "/create_zone", 5: "/create_zone", 10: "/create_zone"}
    
    return [{"zone_level": r["i_typ_zn"], "zone_name": r["x_dsc_zn"], "api_endpoint": api_mapping.get(r["i_typ_zn"], "/create_zone")} for r in rows]

# ✅ Create a Zone
@router.post("/create_zone")
async def create_zone(data: ZoneCreate):
    pool = await get_async_db_pool("data")
    async with pool.acquire() as conn:
        async with conn.transaction():
            zone_id = await conn.fetchval(
                """INSERT INTO zones (x_nm_zn, i_typ_zn, i_pnt_zn, i_map) 
                VALUES ($1, $2, $3, $4) RETURNING i_zn;""",
                data.zone_name, data.zone_level, data.parent_zone_id, data.map_id
            )

            # Calculate min/max coordinates
            x_coords = [v.get("n_x", 0) for v in data.vertices]
            y_coords = [v.get("n_y", 0) for v in data.vertices]
            z_coords = [v.get("n_z", 0) for v in data.vertices]

            n_min_x, n_max_x = min(x_coords, default=0), max(x_coords, default=0)
            n_min_y, n_max_y = min(y_coords, default=0), max(y_coords, default=0)
            n_min_z, n_max_z = min(z_coords, default=0), max(z_coords, default=0)

            region_id = await conn.fetchval(
                """INSERT INTO regions (i_zn, x_nm_rgn, n_min_x, n_max_x, n_min_y, n_max_y, n_min_z, n_max_z)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8) RETURNING i_rgn;""",
                zone_id, data.zone_name, n_min_x, n_max_x, n_min_y, n_max_y, n_min_z, n_max_z
            )

            # Insert vertices
            for idx, vertex in enumerate(data.vertices, start=1):
                await conn.execute(
                    "INSERT INTO vertices (i_rgn, n_x, n_y, n_z, n_ord) VALUES ($1, $2, $3, $4, $5);",
                    region_id, vertex["n_x"], vertex["n_y"], vertex["n_z"], idx
                )

            return {"zone_id": zone_id, "message": "Zone created successfully"}
