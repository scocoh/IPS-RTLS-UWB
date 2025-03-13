import asyncpg
import asyncio

async def test_connection():
    try:
        conn = await asyncpg.connect(
            database="ParcoRTLSMaint",
            user="parcoadmin",
            password="parcoMCSE04106!",
            host="192.168.210.231",
            port=5432
        )
        print("✅ Connected to database!")
        await conn.close()
    except Exception as e:
        print(f"❌ Database connection failed: {e}")

asyncio.run(test_connection())
