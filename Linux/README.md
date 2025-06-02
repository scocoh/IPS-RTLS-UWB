# IPS-RTLS-UWB ParcoRTLS Linux Fast API

Parco RTLS API for integrating various hardware positioning systems into a unified format. Features tag-agnostic, scalable data streams (Full, Subscription, and Polling) and comprehensive services for real-time and historical location tracking. Includes tools for database management, map creation, and hardware setup.

This repository contains the Parco Real-Time Location System (RTLS) API and related services. Parco RTLS is designed to integrate with various hardware positioning systems, providing a common format for data regardless of the hardware used. This allows for seamless upgrades or changes to hardware without impacting the end-user applications built with the Parco SDK.

For a full history on this code visit [https://asproj.com/github-rtls](https://asproj.com/github-rtls)

---

## 🔐 License & Attribution

This repository is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0), as defined in the Windows branch and explicitly extended here to cover this Linux FastAPI version.

> **You are free to use, modify, and redistribute this code under the AGPL-3.0 license.**
> All files using core Parco intellectual property should be marked with the following attribution header:

```python
#
# ParcoRTLS Middletier Services, ParcoRTLS DLL, ParcoDatabases, ParcoMessaging, and other code
# Copyright (C) 1999 - 2025 Affiliated Commercial Services Inc.
# Invented by Scott Cohen & Bertrand Dugal.
# Coded by Jesse Chunn O.B.M.'24 and Michael Farnsworth and Others
# Published at GitHub https://github.com/scocoh/IPS-RTLS-UWB
#
# Licensed under AGPL-3.0: https://www.gnu.org/licenses/agpl-3.0.en.html
```

---

# Key Features:

Tag Agnostic and Scalable: Supports active RFID systems, ensuring tag data is immediately available without prior system knowledge.

# Three Main Data Access Methods:

Full Stream: Provides a comprehensive stream of all tags with the latest coordinates.

Subscription Stream: Offers a filtered stream with only requested tags.

Standard Data Polling: Allows querying the history databases for tag positions.

Extensive Database Support: Includes databases for device position history, device management, entity assignments, and more.

Comprehensive SDK: The Parco RTLS SDK includes tools for rapid application development, including data access methods, pre-coded data access, and integration with CAD-based maps and zones.

# Services and Tools:

Parco Middle Tier Services: Windows-based services for managing connections and data processing.

Web Services: XML web services for scalable and secure data access.

Location Engine: Calculates tag positions based on TOA (time of arrival) messages.

Zone Builder and Buildout Tools: For creating maps and precisely locating hardware.

**New Services in This Version:**

* **Heartbeat Engine:** Monitors tag health and activity status.
* **WebSocket Multiplexing:** Handles live control and data forwarding on multiple channels.
* **TETSE™ Engine:** Temporal-Entity-Trigger-State Engine for programmable zone/event awareness.

# Supported Systems and Compatibility:

Compatible with most systems through the FastAPI.
Works with various hardware systems and offers tag data in multiple formats (Fullstream, Subscription, and Proximity data).
Includes a variety of APIs and tools for different programming environments.
Optional support for payload or sensor data.

# NO CLOUD REQUIRED

Designed to run on Linux.  Could be ideal for HomeAssistant. (TETSE presently uses the OpenAI API which is cloud.  Roll your own to excise the cloud.)

# ParcoRTLS Linux Deployment

**VERSION 0P.1B.01**

## Quickstart

1. **Install**:

   ```bash
   curl -O https://github.com/scocoh/IPS-RTLS-UWB/tree/3651eeed37248791fdca68606d436201ba2984dc/Linux/scripts/setup.sh
   chmod +x setup.sh
   sudo ./setup.sh
   ```

   Follow prompts to restore parco\_fastapi/Linux/db/PostgresQL\_ALLDBs\_backup.sql or a custom backup.

2. **Access**:
   Backend: http\://<server-ip>:8000
   Frontend: http\://<server-ip>:3000

3. **Update**:

   ```bash
   sudo /home/parcoadmin/parco_fastapi/app/update.sh
   ```

4. **Shutdown**:

   ```bash
   sudo /home/parcoadmin/parco_fastapi/app/shutdown.sh
   ```

See ParcoRTLS\_Manual.md at the repo root for detailed instructions.

---

© 1999–2025 Affiliated Commercial Services Inc.
ParcoRTLS™ and TETSE™ are trademarks of Affiliated Commercial Services Inc.
Updated 250531 v 0.1.83
