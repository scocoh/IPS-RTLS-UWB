"""
test_triggers.py
Version: 0.1.0 (Comprehensive API tests for ParcoRTLS trigger management)
// zoneManager.js - Manages Campus (L1) and Building (L2) zone creation
// # VERSION 250316 /home/parcoadmin/parco_fastapi/app/tests/test_triggers.py 0.1.0
// #  
// # ParcoRTLS Middletier Services, ParcoRTLS DLL, ParcoDatabases, ParcoMessaging, and other code
// # Copyright (C) 1999 - 2025 Affiliated Commercial Services Inc.
// # Invented by Scott Cohen & Bertrand Dugal.
// # Coded by Jesse Chunn O.B.M.'24 and Michael Farnsworth and Others
// # Published at GitHub https://github.com/scocoh/IPS-RTLS-UWB
// #
// # Licensed under AGPL-3.0: https://www.gnu.org/licenses/agpl-3.0.en.html

"""

import pytest
import httpx
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"

@pytest.mark.asyncio
async def test_add_trigger():
    """Test adding a new trigger."""
    async with httpx.AsyncClient() as client:
        form_data = {"direction": 1, "name": f"TestTrigger_{int(datetime.now().timestamp())}", "ignore": False}
        response = await client.post(f"{BASE_URL}/api/add_trigger", json=form_data)
    assert response.status_code == 200
    assert "trigger_id" in response.json()

@pytest.mark.asyncio
async def test_fire_trigger():
    """Test firing an existing trigger."""
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/api/fire_trigger/TestTrigger")
    assert response.status_code in [200, 404]
    if response.status_code == 200:
        assert "trigger_id" in response.json()
    else:
        assert response.json()["detail"] == "Trigger 'TestTrigger' not found"

@pytest.mark.asyncio
async def test_list_trigger_directions():
    """Test listing all trigger directions."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/api/list_trigger_directions")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_get_triggers_by_point():
    """Test fetching triggers by coordinates (expect 404 if no triggers exist)."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/api/get_triggers_by_point?x=100.5&y=200.0&z=0.0")
    assert response.status_code in [200, 404]

@pytest.mark.asyncio
async def test_delete_trigger():
    """Test deleting a trigger (only works if trigger exists)."""
    async with httpx.AsyncClient() as client:
        response = await client.delete(f"{BASE_URL}/api/delete_trigger/1")
    assert response.status_code in [200, 500]

if __name__ == "__main__":
    pytest.main()
