# Name: test_db.py
# Version: 0.1.0
# Created: 971201
# Modified: 250502
# Creator: ParcoAdmin
# Modified By: ParcoAdmin
# Description: Python script for ParcoRTLS backend
# Location: /home/parcoadmin/parco_fastapi/app
# Role: Backend
# Status: Active
# Dependent: TRUE

import asyncio
from database.db import get_async_db_pool, call_stored_procedure

async def test_db():
    pool = await get_async_db_pool("maint")
    if pool:
        print("Pool created successfully")
        result = await call_stored_procedure("maint", "usp_device_select_all", pool=pool)
        print("Devices:", result)
        await pool.close()
    else:
        print("Failed to create pool")

if __name__ == "__main__":
    asyncio.run(test_db())
    