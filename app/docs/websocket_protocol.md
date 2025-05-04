# ParcoRTLS Manager WebSocket Protocol
Version: 0.1.2 – Finalized

## Overview
This document explains how external applications can subscribe to real-time `TriggerEvent` messages from the ParcoRTLS Manager using WebSocket.

- **Server Address**: `ws://192.168.210.226:8001/ws/{manager_name}`
  - Example: `ws://192.168.210.226:8001/ws/Manager1`
- **Protocol**: JSON messages over WebSocket.

## Steps to Subscribe

### 1. Connect to WebSocket
Use a WebSocket client to open a connection.

**Example (JavaScript):**
```javascript
const ws = new WebSocket("ws://192.168.210.226:8001/ws/Manager1");
```

---

### 2. Send BeginStream Request
After connecting, send a `BeginStream` request to subscribe to specific tags inside a zone.

**Request Example:**
```json
{
  "type": "request",
  "request": "BeginStream",
  "reqid": "myApp1",
  "params": [
    { "id": "TAG001", "data": "true" }
  ],
  "zone_id": 417
}
```

**Server Response Example:**
```json
{
  "type": "response",
  "reqid": "myApp1",
  "response": "BeginStream"
}
```

---

### 3. Receive TriggerEvent Messages
Once subscribed, you will receive `TriggerEvent` messages when tags trigger events.

**Event Example:**
```json
{
  "type": "TriggerEvent",
  "trigger_id": 123,
  "direction": "OnEnter",
  "tag_id": "TAG001",
  "timestamp": "2025-04-26T12:34:56.789Z"
}
```

---

### 4. Handle HeartBeat Messages
The server sends `HeartBeat` messages to check if the client is still connected.

**HeartBeat Received Example:**
```json
{
  "type": "HeartBeat",
  "ts": 1698771234567
}
```

**HeartBeat Reply Example:**
```json
{
  "type": "HeartBeat",
  "ts": 1698771234567
}
```

---

### 5. (Optional) Add More Tags
You can add new tags after the stream starts.

**AddTag Request Example:**
```json
{
  "type": "request",
  "request": "AddTag",
  "reqid": "addTag1",
  "params": [
    { "id": "TAG002", "data": "true" }
  ]
}
```

**Server Response Example:**
```json
{
  "type": "response",
  "reqid": "addTag1",
  "response": "AddTag"
}
```

---

### 6. (Optional) End the Stream
You can end the subscription by sending an `EndStream` request.

**EndStream Request Example:**
```json
{
  "type": "request",
  "request": "EndStream",
  "reqid": "myApp1"
}
```

**Server Response Example:**
```json
{
  "type": "response",
  "reqid": "myApp1",
  "response": "EndStream"
}
```

After this, the WebSocket connection should be closed.

---

## Notes
- Always respond to `HeartBeat` messages to keep the connection alive.
- Make sure to handle WebSocket disconnects gracefully.
- This protocol is required when connecting directly to the Manager’s WebSocket server (port 8001).
