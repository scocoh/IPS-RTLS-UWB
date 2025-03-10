"""
test_triggers.py
Version: 0.1.0 (Comprehensive API tests for ParcoRTLS trigger management)
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
