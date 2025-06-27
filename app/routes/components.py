# Name: components.py
# Version: 0.1.4
# Created: 971201
# Modified: 250502
# Creator: ParcoAdmin
# Modified By: ParcoAdmin
# Description: ParcoRTLS backend script
# Location: /home/parcoadmin/parco_fastapi/app/routes
# Role: Backend
# Status: Active
# Dependent: TRUE
# Changelog:
# - 0.1.4 (250502): Updated procedures/functions endpoints to match expected format with metadata and corrected usp_ labeling
# - 0.1.3 (250502): Added note about usp_ naming convention in procedures/functions Markdown files
# - 0.1.2 (250502): Updated procedures/functions endpoints to include routine_type and avoid duplicates
# - 0.1.1 (250502): Added endpoints to generate proc_func_lbn.md and proc_func_details.md
# - 0.1.0 (250502): Initial version with get_components endpoint

from fastapi import APIRouter, HTTPException
import psycopg2
from psycopg2.extras import RealDictCursor

router = APIRouter(
    prefix="/components",
    tags=["components"]
)

# Database connection parameters
DB_PARAMS = {
    "dbname": "ParcoRTLSMaint",
    "user": "menu19",
    "password": "menu19",
    "host": "localhost",
    "port": "5432"
}

# Directory for storing Markdown files
APP_DIR = "/home/parcoadmin/parco_fastapi/app"

@router.get("/")
async def get_components():
    """Use this command to access the ParcoRTLSMaint table component_versions.
    This table is populated by running the 19-update-component-versions.sh from the app directory
    or via the utility menu.
    This is useful for creating a list of all of the files for the ParcoRTLS.
    as of version 0.1.80 of the update component we do not track JSON nor database files."""
    try:
        # Connect to the database
        conn = psycopg2.connect(**DB_PARAMS) # type: ignore
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Query the component_versions table
        cursor.execute("SELECT * FROM component_versions ORDER BY location, name")
        components = cursor.fetchall()
        
        # Close the connection
        cursor.close()
        conn.close()
        
        # Convert to list of dictionaries for JSON response
        return [dict(component) for component in components]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/procedures-functions-list")
async def generate_procedures_functions_list():
    """Generates a Markdown file (proc_func_lbn.md) listing all stored procedures and functions in the ParcoRTLSMaint database."""
    try:
        # Connect to the database
        conn = psycopg2.connect(**DB_PARAMS) # type: ignore
        cursor = conn.cursor()
        
        # Query for list of procedures and functions, including routine_type, and avoid duplicates
        cursor.execute("SELECT DISTINCT routine_schema, routine_name, routine_type FROM information_schema.routines WHERE routine_type IN ('PROCEDURE', 'FUNCTION') AND specific_schema = 'public' ORDER BY routine_schema, routine_name")
        routines = cursor.fetchall()
        
        # Close the connection
        cursor.close()
        conn.close()
        
        # Write to Markdown file
        output_file = f"{APP_DIR}/proc_func_lbn.md"
        with open(output_file, "w") as f:
            f.write("# Stored Procedures and Functions in ParcoRTLSMaint\n\n")
            f.write("> **Note**: Routines with the `usp_` prefix are labeled as `PROCEDURE` in this output but are defined as `FUNCTION` in the database, based on naming convention.\n\n")
            f.write("| Schema           | Name             | Type             |\n")
            f.write("|------------------|------------------|------------------|\n")
            for routine in routines:
                schema, name, routine_type = routine
                # Override type for usp_ routines
                if name.startswith("usp_"):
                    routine_type = "PROCEDURE"
                f.write(f"| {schema:<16} | {name:<16} | {routine_type:<16} |\n")
        
        return {"message": f"Successfully generated {output_file}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating procedures/functions list: {str(e)}")

@router.get("/procedures-functions-details")
async def generate_procedures_functions_details():
    """Generates a Markdown file (proc_func_details.md) listing all stored procedures and functions in the ParcoRTLSMaint database with their source code."""
    try:
        # Connect to the database
        conn = psycopg2.connect(**DB_PARAMS) # type: ignore
        cursor = conn.cursor()
        
        # Query for list of procedures and functions with their OIDs, including routine_type
        cursor.execute("SELECT DISTINCT r.routine_schema, r.routine_name, r.routine_type, p.oid FROM information_schema.routines r JOIN pg_proc p ON r.specific_name = p.proname || '_' || p.oid WHERE r.routine_type IN ('PROCEDURE', 'FUNCTION') AND r.specific_schema = 'public' ORDER BY r.routine_schema, r.routine_name")
        routines = cursor.fetchall()
        
        # Write to Markdown file
        output_file = f"{APP_DIR}/proc_func_details.md"
        with open(output_file, "w") as f:
            for routine in routines:
                schema, name, routine_type, oid = routine
                # Override type for usp_ routines
                if name.startswith("usp_"):
                    routine_type = "PROCEDURE"
                
                # Get the full definition
                cursor.execute(f"SELECT pg_get_functiondef('{oid}'::oid)")
                definition = cursor.fetchone()[0]
                
                # Extract metadata if present in the definition (assuming comments at the top)
                metadata_lines = []
                for line in definition.split("\n"):
                    if line.startswith("-- "):
                        metadata_lines.append(line[3:])
                    else:
                        break
                metadata = "\n".join(metadata_lines)
                if not metadata:
                    # Default metadata if not present
                    metadata = f"Name: {name}\nVersion: 0.1.0\nCreated: 971201\nModified: 250502\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: {routine_type} in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE"
                
                # Write to Markdown file
                f.write(f"{definition}\n")
                f.write(f"{metadata}\n\n")
        
        # Close the connection
        cursor.close()
        conn.close()
        
        return {"message": f"Successfully generated {output_file}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating procedures/functions details: {str(e)}")