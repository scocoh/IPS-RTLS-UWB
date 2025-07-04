# Name: vertex.py
# Version: 0.1.1
# Created: 971201
# Modified: 250502
# Creator: ParcoAdmin
# Modified By: ParcoAdmin
# Version 0.1.1 Converted to external descriptions using load_description()
# Description: Python script for ParcoRTLS backend
# Location: /home/parcoadmin/parco_fastapi/app/routes
# Role: Backend
# Status: Active
# Dependent: TRUE

"""
/home/parcoadmin/parco_fastapi/app/routes/vertex.py
routes/vertex.py
Version: 0.1.16 (Added tags=["vertices"] to APIRouter for Swagger UI grouping)
Vertex management endpoints for ParcoRTLS FastAPI application.

Vertices are part of regions, stored in the 'vertices' table with a foreign key (i_rgn)
to 'regions(i_rgn)'. Each region typically requires at least 3 vertices to form a valid
2D or 3D shape (e.g., polygon). The endpoints use stored procedures for delete, list,
and select, and raw queries for add/edit (edit updated to match Zone Viewer approach).

# VERSION 250316 /home/parcoadmin/parco_fastapi/app/routes/vertex.py 0.1.15
# CHANGED: Added tags=["vertices"] to APIRouter for Swagger UI grouping, bumped to 0.1.16
# PREVIOUS: Added POST /update_vertices for bulk updates, version 0.1.15
# 
# ParcoRTLS Middletier Services, ParcoRTLS DLL, ParcoDatabases, ParcoMessaging, and other code
# Copyright (C) 1999 - 2025 Affiliated Commercial Services Inc.
# Invented by Scott Cohen & Bertrand Dugal.
# Coded by Jesse Chunn O.B.M.'24 and Michael Farnsworth and Others
# Published at GitHub https://github.com/scocoh/IPS-RTLS-UWB
#
# Licensed under AGPL-3.0: https://www.gnu.org/licenses/agpl-3.0.en.html

"""

from fastapi import APIRouter, HTTPException, Form
from database.db import call_stored_procedure, DatabaseError, execute_raw_query
from typing import List
import logging

from pathlib import Path

logger = logging.getLogger(__name__)

def load_description(endpoint_name: str) -> str:
    """Load endpoint description from external file"""
    try:
        desc_path = Path(__file__).parent.parent / "docs" / "descriptions" / "vertex" / f"{endpoint_name}.txt"
        with open(desc_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        return f"Description for {endpoint_name} not found"
    except Exception as e:
        return f"Error loading description: {str(e)}"

router = APIRouter(tags=["vertices"])

@router.delete(
    "/delete_vertex/{vertex_id}",
    summary="Delete a vertex by ID (i_vtx)",
    description=load_description("delete_vertex"),
    tags=["triggers"]
)
async def delete_vertex(vertex_id: int):
    try:
        # Check if vertex exists before attempting deletion
        vertex_exists = await execute_raw_query("maint", "SELECT i_vtx FROM public.vertices WHERE i_vtx = $1", vertex_id)
        if not vertex_exists:
            logger.warning(f"Vertex ID {vertex_id} not found")
            raise HTTPException(status_code=404, detail=f"Vertex ID {vertex_id} not found")

        logger.debug(f"Calling usp_vertex_delete with vertex_id={vertex_id}")
        result = await call_stored_procedure("maint", "usp_vertex_delete", vertex_id)
        if result is None:  # Assuming usp_vertex_delete returns void on success
            logger.info(f"Vertex ID {vertex_id} deleted successfully")
            return {"message": "Vertex deleted successfully"}
        logger.error(f"Failed to delete vertex_id={vertex_id}")
        raise HTTPException(status_code=500, detail="Failed to delete vertex")
    except DatabaseError as e:
        if "not found" in str(e.message).lower():
            logger.warning(f"Database reported vertex ID {vertex_id} not found")
            raise HTTPException(status_code=404, detail=f"Vertex ID {vertex_id} not found")
        logger.error(f"Database error deleting vertex: {e.message}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Error deleting vertex: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put(
    "/edit_vertex",
    summary="Edit an kobsexisting vertex by ID (i_vtx) using a raw query (inspired by Zone Viewer)",
    description=load_description("edit_vertex"),
    tags=["triggers"]
)
async def edit_vertex(vertex_id: int = Form(...), region_id: int = Form(...), x: float = Form(...), y: float = Form(...), z: float | None = Form(None), order: int = Form(...)):
    try:
        # Check if vertex exists before attempting editing
        vertex_exists = await execute_raw_query("maint", "SELECT i_vtx, i_rgn FROM public.vertices WHERE i_vtx = $1", vertex_id)
        if not vertex_exists:
            logger.warning(f"Vertex ID {vertex_id} not found")
            raise HTTPException(status_code=404, detail=f"Vertex ID {vertex_id} not found")
        
        # Log current region for comparison
        current_region_id = vertex_exists[0]["i_rgn"]
        if current_region_id != region_id:
            logger.info(f"Region ID changing from {current_region_id} to {region_id}")

        # Validate region_id exists before editing
        region_exists = await execute_raw_query("maint", "SELECT i_rgn FROM public.regions WHERE i_rgn = $1", region_id)
        if not region_exists:
            logger.warning(f"Region ID {region_id} not found")
            raise HTTPException(status_code=400, detail=f"Region ID {region_id} does not exist")

        # Use raw query to update vertex
        logger.debug(f"Updating vertex_id={vertex_id} with x={x}, y={y}, z={z}, order={order}, region_id={region_id}")
        query = """
            UPDATE public.vertices
            SET n_x = $1, n_y = $2, n_z = $3, n_ord = $4, i_rgn = $5
            WHERE i_vtx = $6
            RETURNING i_vtx;
        """
        result = await execute_raw_query("maint", query, x, y, z, order, region_id, vertex_id)
        logger.debug(f"Update query result: {result}")

        if result and isinstance(result, list) and result:
            logger.info(f"Vertex ID {vertex_id} edited successfully")
            return {"message": "Vertex edited successfully"}
        logger.error(f"Failed to update vertex_id={vertex_id}: no rows affected")
        raise HTTPException(status_code=500, detail="Failed to edit vertex: no rows updated")
    except DatabaseError as e:
        if "not found" in str(e.message).lower():
            logger.warning(f"Database reported vertex ID {vertex_id} not found")
            raise HTTPException(status_code=404, detail=f"Vertex ID {vertex_id} not found")
        logger.error(f"Database error editing vertex: {e.message}")
        raise HTTPException(status_code=500, detail=str(e))
    except HTTPException as e:
        logger.warning(f"Re-raising HTTPException: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"Error editing vertex: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/get_vertex_by_id/{vertex_id}",
    summary="Fetch vertex details by ID (i_vtx)",
    description=load_description("get_vertex_by_id"),
    tags=["triggers"]
)
async def get_vertex_by_id(vertex_id: int):
    try:
        result = await call_stored_procedure("maint", "usp_vertex_select_by_id", vertex_id)
        if result and isinstance(result, list) and result:
            logger.info(f"Retrieved vertex details for vertex_id={vertex_id}")
            return result[0]  # Returns a dict with i_vtx, n_x, n_y, n_z, n_ord, i_rgn
        logger.warning(f"Vertex ID {vertex_id} not found")
        raise HTTPException(status_code=404, detail="Vertex not found")
    except Exception as e:
        logger.error(f"Error fetching vertex: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/list_vertices",
    summary="Fetch all vertices",
    description=load_description("list_vertices"),
    tags=["triggers"]
)
async def list_vertices():
    try:
        result = await call_stored_procedure("maint", "usp_vertex_list")
        if result and isinstance(result, list) and result:
            logger.info(f"Retrieved {len(result)} vertices")
            return result  # Returns a list of dicts with i_vtx, n_x, n_y, n_z, n_ord, i_rgn
        logger.warning("No vertices found")
        raise HTTPException(status_code=404, detail="No vertices found")
    except Exception as e:
        logger.error(f"Error listing vertices: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post(
    "/add_vertex",
    summary="Add a new vertex using a raw query (since usp_vertex_add is missing)",
    description=load_description("add_vertex"),
    tags=["triggers"]
)
async def add_vertex(region_id: int = Form(...), x: float = Form(...), y: float = Form(...), z: float | None = Form(None), order: int = Form(...)):
    try:
        # Validate region_id exists before adding
        region_exists = await execute_raw_query("maint", "SELECT i_rgn FROM public.regions WHERE i_rgn = $1", region_id)
        if not region_exists:
            logger.warning(f"Region ID {region_id} not found")
            raise HTTPException(status_code=400, detail=f"Region ID {region_id} does not exist")

        # Insert into vertices table with auto-incrementing i_vtx
        query = """
            INSERT INTO public.vertices (i_rgn, n_x, n_y, n_z, n_ord)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING i_vtx;
        """
        result = await execute_raw_query("maint", query, region_id, x, y, z, order)
        if result and isinstance(result, list) and result:
            logger.info(f"Added new vertex with vertex_id={result[0]['i_vtx']}")
            return {"message": "Vertex added successfully", "vertex_id": result[0]["i_vtx"]}
        logger.error("Failed to add vertex: no rows inserted")
        raise HTTPException(status_code=500, detail="Failed to add vertex")
    except DatabaseError as e:
        logger.error(f"Database error adding vertex: {e.message}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Error adding vertex: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post(
    "/update_vertices",
    summary="Update multiple vertices in bulk",
    description=load_description("update_vertices"),
    tags=["triggers"]
)
async def update_vertices(vertices: List[dict]):
    try:
        if not vertices:
            logger.warning("No vertices provided for update")
            raise HTTPException(status_code=400, detail="No vertices provided")

        updated_count = 0
        for vertex in vertices:
            vertex_id = vertex.get("vertex_id")
            x = vertex.get("x")
            y = vertex.get("y")
            z = vertex.get("z", 0)  # Default z to 0 if not provided
            order = vertex.get("order", 1)  # Default order to 1 if not provided
            region_id = vertex.get("region_id")  # Optional region_id for update

            # Validate vertex exists
            vertex_exists = await execute_raw_query("maint", "SELECT i_vtx FROM public.vertices WHERE i_vtx = $1", vertex_id)
            if not vertex_exists:
                logger.warning(f"Vertex ID {vertex_id} not found")
                raise HTTPException(status_code=404, detail=f"Vertex ID {vertex_id} not found")

            # Update vertex using raw query
            query = """
                UPDATE public.vertices
                SET n_x = $1, n_y = $2, n_z = $3, n_ord = $4, i_rgn = COALESCE($5, i_rgn)
                WHERE i_vtx = $6
                RETURNING i_vtx;
            """
            result = await execute_raw_query("maint", query, x, y, z, order, region_id, vertex_id)
            if result and isinstance(result, list) and result:
                updated_count += 1
                logger.debug(f"Updated vertex_id={vertex_id}")

        if updated_count == len(vertices):
            logger.info(f"Successfully updated {updated_count} vertices")
            return {"message": "Vertices updated successfully"}
        logger.error(f"Updated {updated_count} out of {len(vertices)} vertices")
        raise HTTPException(status_code=500, detail=f"Updated {updated_count} out of {len(vertices)} vertices")
    except HTTPException as e:
        logger.warning(f"Re-raising HTTPException: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"Error updating vertices: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))