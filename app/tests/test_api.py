"""
Version: 250226 test_api.py Version 0P.7B.30 (Comprehensive API Testing for ParcoRTLS, Updated Base URL, Expanded Endpoint Tests, Fixed Expectations, Empty Database Handling, Timeout Handling, Updated Text Data/Zone/Assignment Tests)

ParcoRTLS Middletier Services, ParcoRTLS DLL, ParcoDatabases, ParcoMessaging, and other code
Copyright (C) 1999 - 2025 Affiliated Commercial Services Inc.
Invented by Scott Cohen & Bertrand Dugal.
Coded by Jesse Chunn O.B.M.'24, Michael Farnsworth, and Others
Published at GitHub https://github.com/scocoh/IPS-RTLS-UWB

Licensed under AGPL-3.0: https://www.gnu.org/licenses/agpl-3.0.en.html
"""

import pytest
import httpx
from datetime import datetime

BASE_URL = "http://192.168.210.226:8000"

@pytest.mark.asyncio
async def test_input_screen():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/input")
    assert response.status_code == 200
    assert "Parco RTLS Input Screen" in response.text

@pytest.mark.asyncio
async def test_set_device_state():
    async with httpx.AsyncClient() as client:
        form_data = {"device_id": "DEV001", "new_state": "active"}
        response = await client.put(f"{BASE_URL}/api/set_device_state", data=form_data)
    assert response.status_code == 200
    assert response.json()["message"] == "Device state updated successfully"

@pytest.mark.asyncio
async def test_add_device():
    async with httpx.AsyncClient() as client:
        form_data = {"device_id": f"TEST_{int(datetime.now().timestamp())}", "device_type": 1, "device_name": "Test Device"}
        response = await client.post(f"{BASE_URL}/api/add_device", data=form_data)
    assert response.status_code == 200
    assert "device_id" in response.json()

@pytest.mark.asyncio
async def test_delete_device():
    # First, add a device to delete
    async with httpx.AsyncClient() as client:
        device_id = f"DELETE_{int(datetime.now().timestamp())}"
        await client.post(f"{BASE_URL}/api/add_device", data={"device_id": device_id, "device_type": 1})
        response = await client.delete(f"{BASE_URL}/api/delete_device/{device_id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Device deleted successfully"

@pytest.mark.asyncio
async def test_assign_device_to_zone():
    async with httpx.AsyncClient() as client:
        form_data = {"device_id": "DEV001", "entity_id": "ENT101", "reason_id": 1}
        response = await client.post(f"{BASE_URL}/api/assign_device_to_zone", data=form_data)
    assert response.status_code == 200
    assert "assignment_id" in response.json()

@pytest.mark.asyncio
async def test_insert_position():
    async with httpx.AsyncClient() as client:
        form_data = {"device_id": "DEV001", "x": 10.0, "y": 20.0, "z": 0.0}
        response = await client.post(f"{BASE_URL}/api/insert_position", data=form_data)
    assert response.status_code == 200
    assert response.json()["message"] == "Position inserted successfully"

@pytest.mark.asyncio
async def test_fire_trigger():
    async with httpx.AsyncClient() as client:
        form_data = {"trigger_name": "test_trigger"}
        response = await client.post(f"{BASE_URL}/api/fire_trigger", data=form_data)
    assert response.status_code == 200
    assert "trigger_id" in response.json()

@pytest.mark.asyncio
async def test_log_text_event():
    async with httpx.AsyncClient(timeout=httpx.Timeout(30.0, read=30.0)) as client:
        form_data = {"device_id": "DEV001", "event_data": "Test event from UI"}
        response = await client.post(f"{BASE_URL}/api/log_text_event", data=form_data)
    assert response.status_code == 200
    assert response.json()["message"] == "Text event logged successfully"

# Existing tests (updated where necessary)
@pytest.mark.asyncio
async def test_get_recent_device_positions():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/api/get_recent_device_positions/DEV001")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_get_map():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/api/get_map/337")
    assert response.status_code == 200
    assert response.headers["content-disposition"].startswith("attachment; filename=map_zone_337.")

@pytest.mark.asyncio
async def test_get_all_devices():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/api/get_all_devices")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_get_device_by_id():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/api/get_device_by_id/DEV001")
    assert response.status_code == 200