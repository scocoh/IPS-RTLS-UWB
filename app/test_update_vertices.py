# Name: test_update_vertices.py
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

# /home/parcoadmin/parco_fastapi/app/test_update_vertices.py
import requests
import json

# Define the URL for the endpoint
url = "http://192.168.210.226:8000/zoneviewer/update_vertices"

# Payload with vertices to update (same as before)
payload = [
    {
        "vertex_id": 1807,
        "x": -77.5,
        "y": 158.0,
        "z": 0.0
    },
    {
        "vertex_id": 1808,
        "x": 158.5,
        "y": 157.5,
        "z": 0.0
    }
]

# Headers for JSON content
headers = {"Content-Type": "application/json"}

try:
    # Send the POST request
    response = requests.post(url, data=json.dumps(payload), headers=headers)

    # Print the status code and response
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")

    # If successful, fetch updated vertices to confirm
    if response.status_code == 200:
        verify_url = "http://192.168.210.226:8000/zoneviewer/get_vertices_for_campus/360"
        verify_response = requests.get(verify_url)
        print(f"Verification Status Code: {verify_response.status_code}")
        print(f"Updated Vertices: {verify_response.text}")

except requests.exceptions.RequestException as e:
    print(f"Error: {e}")