/* Name: zoneManager.js */
/* Version: 0.1.0 */
/* Created: 971201 */
/* Modified: 250502 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin */
/* Description: JavaScript file for ParcoRTLS frontend */
/* Location: /home/parcoadmin/parco_fastapi/app/static */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

// zoneManager.js - Manages Campus (L1) and Building (L2) zone creation
// zoneManager.js - Manages Campus (L1) and Building (L2) zone creation
// # VERSION 250316 /home/parcoadmin/parco_fastapi/app/static/zoneManager.js 0P.10B.01
// #  
// # ParcoRTLS Middletier Services, ParcoRTLS DLL, ParcoDatabases, ParcoMessaging, and other code
// # Copyright (C) 1999 - 2025 Affiliated Commercial Services Inc.
// # Invented by Scott Cohen & Bertrand Dugal.
// # Coded by Jesse Chunn O.B.M.'24 and Michael Farnsworth and Others
// # Published at GitHub https://github.com/scocoh/IPS-RTLS-UWB
// #
// # Licensed under AGPL-3.0: https://www.gnu.org/licenses/agpl-3.0.en.html


let mapMetadata = null; // Store map bounds for scaling

function startNewSession() {
    console.log("Starting a new session...");
    document.getElementById("mapSelection").classList.remove("hidden");
    document.getElementById("zoneDetails").classList.add("hidden");
    document.getElementById("zoneCanvas").classList.add("hidden");
    document.getElementById("nextStepContainer").classList.add("hidden");
    document.getElementById("buildingL2Details").classList.add("hidden");
    sessionStorage.clear(); // Clear previous session data
}

function saveCampus() {
    let zoneName = document.getElementById("zoneName").value;
    let selectedMap = document.getElementById("mapSelect").value;
    if (!zoneName || !selectedMap) {
        alert("Map ID and Zone Name are required");
        return;
    }

    console.log(`Saving Campus L1: ${zoneName} for map ID ${selectedMap}`);

    fetch('/create_campus_l1', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ map_id: selectedMap, zone_name: zoneName })
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            alert(`Campus L1 "${zoneName}" created successfully!`);
            document.getElementById("nextStepContainer").classList.remove("hidden");
            sessionStorage.setItem("current_zone_id", data.zone_id);
        } else {
            alert(`Error: ${data.error}`);
        }
    })
    .catch(error => console.error("Error:", error));
}

function showBuildingL2Form() {
    console.log("Building Outside L2 form is now visible.");
    document.getElementById("buildingL2Details").classList.remove("hidden");
}
