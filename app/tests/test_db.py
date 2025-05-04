# Name: test_db.py
# Version: 0.1.0
# Created: 971201
# Modified: 250502
# Creator: ParcoAdmin
# Modified By: ParcoAdmin
# Description: Python script for ParcoRTLS backend
# Location: /home/parcoadmin/parco_fastapi/app/tests
# Role: Backend
# Status: Active
# Dependent: TRUE

import asyncpg
import asyncio

async def test_connection():
    try:
        conn = await asyncpg.connect(
            database="ParcoRTLSMaint",
            user="parcoadmin",
            password="parcoMCSE04106!",
            host="192.168.210.226",
            port=5432
        )
        print("✅ Connected to database!")
        await conn.close()
    except Exception as e:
        print(f"❌ Database connection failed: {e}")

asyncio.run(test_connection())
