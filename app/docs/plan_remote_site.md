# Plan: Remote Site Connection for ParcoRTLS Manager/FastAPI

**Document Version**: 0.1.0  
**Date**: May 05, 2025  
**Author**: ParcoAdmin (assisted by Grok, xAI)

## 1. Introduction
This document outlines the plan for enabling an off-premise (remote) site to connect to the on-premise ParcoRTLS system via the Manager’s WebSocket interface. The remote site operates a local instance of the FastAPI application, potentially alongside HomeAssistant, TriggerDemo/Entity Apps, and custom applications, to access real-time data from the on-premise ParcoRTLS system. This plan includes system architecture, firewall configuration, connection details, data integration, and future enhancements.

## 2. System Architecture Overview

### On-Premise (ParcoRTLS System)
- **Server**: Located at `192.168.210.226` (Ubuntu machine, `parcortlsserver`).
- **Manager**: Runs `manager/websocket.py` (version 0.1.0) on port 8001, exposing the WebSocket endpoint `ws://192.168.210.226:8001/ws/Manager1`.
  - Connects to the database (`ParcoRTLSMaint`) using the connection string `postgresql://parcoadmin:parcoMCSE04106!@192.168.210.226:5432/ParcoRTLSMaint`.
  - Validates `manager_name` against the `tlkresources` table and loads triggers via `manager.load_triggers(zone_id)`.
  - Handles WebSocket connections, processes `BeginStream` requests, and sends `TriggerEvent` messages to subscribed clients.
- **FastAPI**: Runs `app.py` (version 0P.10B.08) on port 8000, providing REST endpoints (e.g., `/api/list_triggers`) and a WebSocket endpoint (`/api/ws/events/{zone_id}`).
  - Port 8000 is blocked by the firewall for external access.
- **Database**: PostgreSQL (`ParcoRTLSMaint`) on `192.168.210.226:5432`, storing triggers, zones, tags, and resources (e.g., `tlkresources` with `Manager1`).
- **Firewall**: Allows inbound/outbound traffic on port 8001 (Manager’s WebSocket) but blocks port 8000 (FastAPI).

### Off-Premise (Remote Site)
- **Server**: A remote machine (e.g., cloud server, home server, or local device) running:
  - **FastAPI**: A local copy of `app.py`, running on `http://localhost:8000` (port configurable). No direct access to the on-premise database or FastAPI server.
  - **HomeAssistant**: Smart home platform, capable of polling REST endpoints or subscribing to WebSocket events.
  - **TriggerDemo/Entity Apps**: Apps like `NewTriggerDemo.js` (version v0.10.87) for visualizing trigger events, connecting to the local FastAPI.
  - **Custom Apps**: Applications built by the remote user, interacting with the local FastAPI to access ParcoRTLS data.
- **Network**: Can reach `192.168.210.226:8001` over the internet, but not `192.168.210.226:8000` due to firewall restrictions.

## 3. Use Case Description
- **Objective**: Allow a remote site to access real-time `TriggerEvent` data (e.g., tag movements, trigger activations) from the on-premise ParcoRTLS system without direct access to the internal FastAPI server (port 8000).
- **Connection Method**: The remote FastAPI connects to the Manager’s WebSocket endpoint (`ws://192.168.210.226:8001/ws/Manager1`) to subscribe to `TriggerEvent` messages.
- **Data Flow**:
  - The remote FastAPI subscribes to events for specific tags and zones (e.g., tags `SIM1` and `SIM2` in zone 417).
  - The Manager sends real-time `TriggerEvent` messages to the remote FastAPI, which processes and exposes the data to local clients (e.g., HomeAssistant, TriggerDemo apps, or custom apps) via REST or WebSocket endpoints.
- **Scenarios**:
  - **HomeAssistant Integration**: HomeAssistant polls the remote FastAPI to trigger automations (e.g., turn on lights when a tag enters a zone).
  - **TriggerDemo/Entity Apps**: `NewTriggerDemo.js` connects to the local FastAPI to display live events.
  - **Custom Applications**: Apps access events for analytics, alerts, or integration with other systems.

## 4. Firewall Configuration
The firewall must allow communication on port 8001 (already accessible, as confirmed by prior usage).

- **Inbound Traffic**:
  - **Port**: 8001 (TCP)
  - **Source**: Any (remote site IPs may vary).
  - **Destination**: `192.168.210.226:8001`
  - **Purpose**: Allows the remote FastAPI to initiate a WebSocket connection.
- **Outbound Traffic**:
  - **Port**: 8001 (TCP)
  - **Source**: `192.168.210.226:8001`
  - **Destination**: Any
  - **Purpose**: Allows the Manager to send WebSocket messages to the remote FastAPI.
- **Firewall Rule Example** (using `ufw` on Ubuntu):
  ```
  ufw allow in on eth0 to 192.168.210.226 port 8001 proto tcp
  ufw allow out on eth0 from 192.168.210.226 port 8001 proto tcp
  ```

## 5. Remote FastAPI Connection to Manager’s WebSocket
The remote FastAPI connects to the Manager’s WebSocket to receive real-time `TriggerEvent` messages.

- **Connection Initiation**:
  - The remote FastAPI uses a WebSocket client to connect to `ws://192.168.210.226:8001/ws/Manager1`.
  - The connection URL is configured (e.g., `MANAGER_WS_URL=ws://192.168.210.226:8001/ws/Manager1`).
  - The client sends an HTTP `GET` request with WebSocket upgrade headers:
    ```
    GET /ws/Manager1 HTTP/1.1
    Host: 192.168.210.226:8001
    Upgrade: websocket
    Connection: Upgrade
    Sec-WebSocket-Key: <random-key>
    Sec-WebSocket-Version: 13
    ```
  - The Manager responds with a `101 Switching Protocols` status:
    ```
    HTTP/1.1 101 Switching Protocols
    Upgrade: websocket
    Connection: Upgrade
    Sec-WebSocket-Accept: <computed-accept-key>
    ```

- **Manager Validation**:
  - The Manager validates `manager_name` (`Manager1`) by querying the `tlkresources` table:
    ```
    SELECT COUNT(*) FROM tlkresources WHERE X_NM_RES = 'Manager1'
    ```
  - Uses embedded credentials: `postgresql://parcoadmin:parcoMCSE04106!@192.168.210.226:5432/ParcoRTLSMaint`.
  - `Manager1` exists in `tlkresources` (`x_nm_res="Manager1", x_ip="192.168.210.226", i_prt=8001`), so validation passes.
  - If validation fails, the Manager closes the connection with a `1008` status code (`Manager not found`).

- **Subscription Request**:
  - The remote FastAPI sends a `BeginStream` request for tags `SIM1` and `SIM2` in zone 417:
    ```
    {
      "type": "request",
      "request": "BeginStream",
      "reqid": "remote_api_1",
      "params": [
        {"id": "SIM1", "data": "true"},
        {"id": "SIM2", "data": "true"}
      ],
      "zone_id": 417
    }
    ```
  - The Manager processes the request:
    - Creates an `SDKClient` instance (`client_id`: `<remote-ip>:<remote-port>`).
    - Sets `zone_id` (`sdk_client.zone_id = 417`, `manager.zone_id = 417`).
    - Reloads triggers if `zone_id` changes (`manager.load_triggers(417)`).
    - Adds tags to the `SDKClient` (`sdk_client.add_tag("SIM1")`, `sdk_client.add_tag("SIM2")`).
    - Sends a response:
      ```
      {"type": "response", "reqid": "remote_api_1", "response": "BeginStream"}
      ```

- **HeartBeat Handling**:
  - The Manager sends `HeartBeat` messages every ~30 seconds:
    ```
    {"type": "HeartBeat", "ts": 1698771234567}
    ```
  - The remote FastAPI responds:
    ```
    {"type": "HeartBeat", "ts": 1698771234567}
    ```
  - Failure to respond may result in connection closure (`CLOSE 1000 (OK)`).

- **Receiving TriggerEvent Messages**:
  - The Manager sends `TriggerEvent` messages when events occur:
    ```
    {
      "type": "TriggerEvent",
      "trigger_id": 123,
      "direction": "OnEnter",
      "tag_id": "SIM1",
      "timestamp": "2025-05-05T12:34:56.789Z"
    }
    ```
  - The remote FastAPI processes these messages (e.g., logs, stores, forwards).

- **Connection Closure**:
  - The remote FastAPI sends an `EndStream` request to close:
    ```
    {"type": "request", "request": "EndStream", "reqid": "remote_api_1"}
    ```
  - The Manager responds:
    ```
    {"type": "response", "reqid": "remote_api_1", "response": "EndStream"}
    ```
  - The connection closes gracefully (`CLOSE 1000 (OK)`).

## 6. Remote FastAPI Processing and Data Integration
The remote FastAPI processes `TriggerEvent` messages and exposes them to local clients.

- **Event Processing**:
  - Parses JSON payloads, extracting `trigger_id`, `tag_id`, `direction`, `timestamp`.
  - Transforms data (e.g., maps `trigger_id: 123` to “Entry Gate” if static data is available).
  - Stores data in a local structure (e.g., in-memory list, SQLite database, Redis cache).

- **Exposing Data**:
  - **REST Endpoint**: Exposes `/recent_events` to return events:
    ```
    [
      {
        "trigger_id": 123,
        "trigger_name": "Entry Gate",
        "tag_id": "SIM1",
        "tag_name": "Employee Badge 1",
        "direction": "OnEnter",
        "timestamp": "2025-05-05T12:34:56.789Z"
      },
      ...
    ]
    ```
  - **WebSocket Endpoint**: Exposes `/ws/events` to broadcast events to local clients.

- **HomeAssistant Integration**:
  - Polls `/recent_events` every 10 seconds to trigger automations (e.g., turn on lights for `"direction": "OnEnter"`).
  - Alternatively, subscribes to `/ws/events` for real-time updates.

- **TriggerDemo/Entity Apps**:
  - `NewTriggerDemo.js` connects to `ws://localhost:8000/ws/events` to display live events.
  - `EntityMap.js` uses `/recent_events` to map entities to locations.

- **Custom Apps**:
  - Access events via REST or WebSocket for alerts, analytics, or integration with other systems.

## 7. Data Context and Limitations
- **Missing Static Data**: `TriggerEvent` messages lack context (e.g., trigger names, zone details).
- **Mitigation**:
  - Preload static data (e.g., export trigger definitions as JSON).
  - Infer context from messages (e.g., use `zone_id` from `BeginStream`).
  - Sync static data manually via a secure channel.

## 8. Security Considerations
- **Current State**: The WebSocket endpoint is open to any client.
- **Risk**: Unauthorized access to sensitive data (e.g., tag movements).
- **Future Mitigation**: Add an `api_key` parameter (to be implemented later).

## 9. Connection Stability and Error Handling
- **Initial Connection**:
  - Retry with exponential backoff if connection fails (e.g., 5s, 10s, 20s, max 60s).
- **HeartBeat Compliance**:
  - Respond to `HeartBeat` messages within 10 seconds to avoid closure.
- **Disconnection Handling**:
  - Reconnect on closure, resend `BeginStream` request.
- **Event Volume**:
  - Filter or aggregate events to manage high volumes.

## 10. Testing and Validation
- **Basic Connection**: Subscribe to tags `SIM1` and `SIM2` in zone 417, verify events.
- **HeartBeat Handling**: Ensure connection stays open for 1 hour.
- **Disconnection**: Simulate Manager downtime, confirm reconnection.
- **HomeAssistant**: Poll `/recent_events`, verify automations.
- **TriggerDemo**: Connect to `/ws/events`, verify UI updates.
- **Custom Apps**: Fetch events, confirm data accuracy.

## 11. Future Enhancements
- **Authentication**: Add `api_key` parameter to secure WebSocket access.
- **Static Data Sync**: Export static data for remote use.
- **Monitoring**: Log external connections, detect issues.
- **Event Filtering**: Allow clients to filter events by tags or triggers.