# IPS-RTLS-UWB
Parco RTLS SDK for integrating various hardware positioning systems into a unified format. Features tag-agnostic, scalable data streams (Full, Subscription, and Polling) and comprehensive services for real-time and historical location tracking. Includes tools for database management, map creation, and hardware setup.

This repository contains the Parco Real-Time Location System (RTLS) software development kit (SDK) and related services. Parco RTLS is designed to integrate with various hardware positioning systems, providing a common format for data regardless of the hardware used. This allows for seamless upgrades or changes to hardware without impacting the end-user applications built with the Parco SDK.

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

# Supported Systems and Compatibility:
Compatible with SQL Server 2000, 2003, and 2003 x64.
Works with various hardware systems and offers tag data in multiple formats (Fullstream, Subscription, and Proximity data).
Includes a variety of SDKs and tools for different programming environments, including .Net and Java.
Optional support for payload or sensor data.

# NO CLOUD REQUIRED
Designed to run on a pentium class laptop circa 2002 as part of a mass casualty scalability system.  Could be ideal for HomeAssistant.
