# Name: simulator.py
# Version: 0.1.0
# Created: 971201
# Modified: 250502
# Creator: ParcoAdmin
# Modified By: ParcoAdmin
# Description: ParcoRTLS backend script
# Location: /home/parcoadmin/parco_fastapi/app/routes
# Role: Backend
# Status: Active
# Dependent: TRUE

# simulator.py
# Version: 0.4.1
# RTLS Simulator route for saving and retrieving simulation paths
# Stored in ParcoRTLSData.path_simulations

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import date
import json
from db_config_helper import get_connection
from server_config import load_description

router = APIRouter()
desc = load_description("simulator")

# ====== Pydantic Models ======
class Position(BaseModel):
    x: float
    y: float
    z: float

class PathSimulation(BaseModel):
    x_nm_path: str
    created: Optional[str] = None
    tag_id: str
    i_zn: int
    ping_rate: float
    speed_fps: float
    duration_s: Optional[int] = None
    direction: str  # forward or pingpong
    dwell_secs: float = 0.0
    positions: List[Position]

# ====== POST /simulator/save_path ======
@router.post("/simulator/save_path", tags=["simulator"], description=desc["save_path"])
def save_path(sim: PathSimulation):
    try:
        conn = get_connection("data")
        cur = conn.cursor()
        if not sim.created:
            sim.created = date.today().strftime("%y%m%d")

        if sim.duration_s is None:
            distance = 0
            for i in range(len(sim.positions) - 1):
                a = sim.positions[i]
                b = sim.positions[i + 1]
                dx = b.x - a.x
                dy = b.y - a.y
                distance += (dx ** 2 + dy ** 2) ** 0.5
            sim.duration_s = int(distance / sim.speed_fps) if sim.speed_fps > 0 else 0

        cur.execute("""
            INSERT INTO path_simulations (
                x_nm_path, dt_created, tag_id, i_zn,
                ping_rate, speed_fps, duration_s, direction, dwell_secs, jsn_positions
            ) VALUES (%s, CURRENT_DATE, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            sim.x_nm_path,
            sim.tag_id,
            sim.i_zn,
            sim.ping_rate,
            sim.speed_fps,
            sim.duration_s,
            sim.direction,
            sim.dwell_secs,
            json.dumps([p.dict() for p in sim.positions])
        ))
        conn.commit()
        cur.close()
        conn.close()
        return {"status": "ok", "message": f"Saved path '{sim.x_nm_path}'."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ====== GET /simulator/list_paths ======
@router.get("/simulator/list_paths", tags=["simulator"], description=desc["list_paths"])
def list_paths(i_zn: int = Query(..., description="Zone ID to filter paths")):
    try:
        conn = get_connection("data")
        cur = conn.cursor()
        cur.execute("""
            SELECT i_path, x_nm_path, dt_created, tag_id, ping_rate, speed_fps,
                   direction, dwell_secs, jsn_positions
            FROM path_simulations
            WHERE i_zn = %s
            ORDER BY dt_created DESC, x_nm_path
        """, (i_zn,))
        rows = cur.fetchall()
        cur.close()
        conn.close()

        result = []
        for r in rows:
            result.append({
                "i_path": r[0],
                "x_nm_path": r[1],
                "created": r[2].strftime("%y%m%d"),
                "tag_id": r[3],
                "ping_rate": r[4],
                "speed_fps": r[5],
                "direction": r[6],
                "dwell_secs": r[7],
                "positions": r[8]
            })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ====== GET /simulator/get_path/{i_path} ======
@router.get("/simulator/get_path/{i_path}", tags=["simulator"], description=desc["get_path"])
def get_path(i_path: int):
    try:
        conn = get_connection("data")
        cur = conn.cursor()
        cur.execute("""
            SELECT i_path, x_nm_path, dt_created, tag_id, i_zn, ping_rate,
                   speed_fps, direction, dwell_secs, jsn_positions
            FROM path_simulations
            WHERE i_path = %s
        """, (i_path,))
        row = cur.fetchone()
        cur.close()
        conn.close()

        if not row:
            raise HTTPException(status_code=404, detail="Path not found")

        return {
            "i_path": row[0],
            "x_nm_path": row[1],
            "created": row[2].strftime("%y%m%d"),
            "tag_id": row[3],
            "i_zn": row[4],
            "ping_rate": row[5],
            "speed_fps": row[6],
            "direction": row[7],
            "dwell_secs": row[8],
            "positions": row[9]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
