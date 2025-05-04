/* Name: drawingTool.js */
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

// Version: 250227 drawingTool.js Version 0P.6B.5O
// 
//  ParcoRTLS Middletier Services, ParcoRTLS DLL, ParcoDatabases, ParcoMessaging, and other code
//  Copyright (C) 1999 - 2025 Affiliated Commercial Services Inc.
//  Invented by Scott Cohen & Bertrand Dugal.
//  Coded by Jesse Chunn O.B.M.'24 and Michael Farnsworth and Others
//  Published at GitHub https://github.com/scocoh/IPS-RTLS-UWB
// 
//  Licensed under AGPL-3.0: https://www.gnu.org/licenses/agpl-3.0.en.html
// 
//  🔥 FIXED: Ensured all necessary exports are properly declared
//  🔥 FIXED: Dynamic API endpoint selection based on `/get_zone_types`
//  🔥 FIXED: Console logging includes CLI version tracking
//  🔥 FIXED: Ensured zone level selection updates correctly
//  🔥 FIXED: Map clicks register correctly and zone outline renders
//  🔥 COMMENTED OUT: Polygon rendering for now
//  🔥 UPDATE: Save Zone button appears after finishing the drawing
//     Replaced: drawPoint
//     Replaced: saveZone and bumped version to 4H in console.log
//     Added updateZoneLevel at last line and bumped version to 4I
//     Replaced drawPoint in effort to add lines and fill. Bumped version to 5A
//     Updated to export points to help with + - zoom issue bump version to 5B
//     Updated to include refreshZoneDropdowns for real-time UI updates after saving. Bumped version to 5D.
//     Fixed duplicate export of 'updateZoneLevel' by consolidating exports. Bumped version to 5E.
//     Fixed duplicate export of 'saveZone' by consolidating exports. Bumped version to 5F.
//     Fixed duplicate export of 'finishDrawingZone' by consolidating exports. Bumped version to 5G.
//     Fixed duplicate export of 'saveZone' again by consolidating exports. Bumped version to 5H.
//     Fixed duplicate export of 'drawPoint' by consolidating exports. Bumped version to 5I.
//     Fixed duplicate export of 'startDrawingZone' by consolidating exports. Bumped version to 5J.
//     Re-exported 'updateZoneLevel' but it was undefined; redefined and re-exported correctly. Bumped version to 5L.
//     Fixed duplicate export of 'updateZoneLevel' again by consolidating exports. Bumped version to 5M.
//     Fixed duplicate entries in parentZoneSelect dropdown by deduplicating zones by zone_id. Bumped version to 5N.
//     Enhanced parentZoneSelect deduplication logic, added clearing, and improved debugging. Bumped version to 5O.

import { formatVertices } from "./vertexFormatter.js";
import { loadMap } from "./mapLoader.js";

let drawing = false;
export let points = [];
let currentZoneLevel = 1;
window.mapScaling = null;

console.log("[INFO] Loaded drawingTool.js Version 0P.6B.5O");

// ✅ Fetch and Populate Map List
document.addEventListener("DOMContentLoaded", function () {
    fetch("/get_maps")
        .then(response => response.json())
        .then(data => {
            let mapSelect = document.getElementById("mapSelect");
            data.maps.forEach(map => {
                let option = document.createElement("option");
                option.value = map.map_id;
                option.textContent = map.name;
                mapSelect.appendChild(option);
            });
        })
        .catch(error => console.error("Error fetching maps:", error));

    fetch("/get_parent_zones")
        .then(response => response.json())
        .then(data => {
            let parentZoneSelect = document.getElementById("parentZoneSelect");
            // Clear existing options completely to prevent duplicates
            parentZoneSelect.innerHTML = "";
            
            let defaultOption = document.createElement("option");
            defaultOption.value = "";
            defaultOption.textContent = "(None - Parent Zone)";
            parentZoneSelect.appendChild(defaultOption);

            // Deduplicate zones by zone_id and add debugging log
            const uniqueZones = {};
            data.zones.forEach(zone => {
                if (!uniqueZones[zone.zone_id]) {
                    uniqueZones[zone.zone_id] = true;
                    let option = document.createElement("option");
                    option.value = zone.zone_id;
                    option.textContent = zone.name;
                    parentZoneSelect.appendChild(option);
                }
            });
            console.log(`[DEBUG] Populated parentZoneSelect with ${Object.keys(uniqueZones).length} unique zones:`, Object.keys(uniqueZones));
        })
        .catch(error => console.error("Error fetching parent zones:", error));
});

// ✅ Dynamically Retrieve API Endpoint for Zone Level
async function getApiEndpoint(zoneLevel) {
    try {
        let response = await fetch("/get_zone_types");
        let zones = await response.json();
        let zone = zones.find(z => z.zone_level == zoneLevel);
        return zone ? zone.api_endpoint : null;
    } catch (error) {
        console.error("[ERROR] Fetching zone types failed:", error);
        return null;
    }
}

function startDrawingZone() {
    let canvas = document.getElementById("zoneCanvas");
    if (!canvas) {
        console.error("[ERROR] Canvas element not found!");
        return;
    }

    let ctx = canvas.getContext("2d");
    let zoneName = document.getElementById("zoneName").value;
    let mapId = document.getElementById("mapSelect").value;
    let zoneLevel = document.getElementById("zoneLevel").value;

    if (!zoneName) {
        alert("Enter a Zone Name before defining the outline.");
        return;
    }
    if (!mapId) {
        alert("Select a map before defining the outline.");
        return;
    }
    if (!zoneLevel) {
        alert("Select a zone level before defining the outline.");
        return;
    }

    console.log(`[INFO] Starting drawing for Zone Level ${zoneLevel}: ${zoneName} on Map ID ${mapId}`);

    // ✅ Let mapLoader.js handle the map loading & scaling
    loadMap();

    drawing = true;
    points = [];
    canvas.addEventListener("click", drawPoint);
    document.getElementById("finishDrawing").classList.remove("hidden");
}

function drawPoint(event) {
    let canvas = document.getElementById("zoneCanvas");
    let ctx = canvas.getContext("2d");
    
    if (!canvas) {
        console.error("🚨 Error: Canvas not found!");
        return;
    }

    const rect = canvas.getBoundingClientRect();
    const pixelX = event.clientX - rect.left;
    const pixelY = event.clientY - rect.top;

    console.log(`[INFO] Clicked at (Pixels): X=${pixelX}, Y=${pixelY}`);

    // ✅ **Ensure map scaling values exist before processing clicks**
    if (!window.mapScaling) {
        console.error("🚨 Error: Map scaling values are not defined!");
        alert("🚨 Map scaling values are missing! Please reload the page.");
        return;
    }

    const { min_x, min_y, max_x, max_y } = window.mapScaling;
    const imageWidth = canvas.width;
    const imageHeight = canvas.height;

    const feetX = min_x + ((pixelX / imageWidth) * (max_x - min_x));
    const feetY = max_y - ((pixelY / imageHeight) * (max_y - min_y));

    console.log(`[INFO] Converted to (Feet): X=${feetX.toFixed(2)}, Y=${feetY.toFixed(2)}`);
    points.push({ x: feetX, y: feetY });

    // 🖍️ Draw Point
    ctx.fillStyle = "red";
    ctx.beginPath();
    ctx.arc(pixelX, pixelY, 3, 0, 2 * Math.PI);
    ctx.fill();

    // 🖍️ Draw Line to Previous Point (if there's at least one point)
    if (points.length > 1) {
        let prevPoint = points[points.length - 2];
        let prevPixelX = ((prevPoint.x - min_x) / (max_x - min_x)) * imageWidth;
        let prevPixelY = ((max_y - prevPoint.y) / (max_y - min_y)) * imageHeight;

        ctx.strokeStyle = "blue";
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(prevPixelX, prevPixelY);
        ctx.lineTo(pixelX, pixelY);
        ctx.stroke();
    }

    // 🎨 **Fill Polygon if 3+ Points** 
    if (points.length >= 3) {
        ctx.fillStyle = "rgba(0, 0, 255, 0.3)"; // Light blue fill
        ctx.beginPath();
        points.forEach((point, index) => {
            let px = ((point.x - min_x) / (max_x - min_x)) * imageWidth;
            let py = ((max_y - point.y) / (max_y - min_y)) * imageHeight;
            if (index === 0) {
                ctx.moveTo(px, py);
            } else {
                ctx.lineTo(px, py);
            }
        });
        ctx.closePath();
        ctx.fill();
    }
}

function finishDrawingZone() {
    if (points.length < 3) {
        alert("You must define at least 3 points to create an enclosed area.");
        return;
    }
    points.push(points[0]); // Close the loop
    console.log("Final Points:", points);

    document.getElementById("saveZone").classList.remove("hidden");
}

function saveZone() {
    let zoneName = document.getElementById("zoneName").value;
    let mapId = document.getElementById("mapSelect").value;
    let zoneDropdown = document.getElementById("zoneLevel");
    let apiEndpoint = zoneDropdown.value;  // Get API from dropdown
    let parentZoneId = document.getElementById("parentZoneSelect").value || null;

    if (!zoneName || !mapId || !apiEndpoint) {
        alert("🚨 Error: Zone Name, Map ID, and a valid API Endpoint are required!");
        return;
    }

    // Retrieve the zone level for logging/debugging
    let selectedZoneLevel = zoneDropdown.options[zoneDropdown.selectedIndex].dataset.zoneLevel;

    let scaledVertices = points.map(p => ({
        n_x: p.x,
        n_y: p.y,
        n_z: 0
    }));

    let zoneData = {
        zone_name: zoneName,
        map_id: mapId,  // Ensure map_id is included in the payload
        zone_level: selectedZoneLevel,
        parent_zone_id: parentZoneId,
        vertices: scaledVertices
    };

    console.log(`[INFO] Sending Zone Data to API ${apiEndpoint}:`, zoneData);

    fetch(apiEndpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(zoneData)
    })
    .then(response => {
        if (!response.ok) throw new Error(`API Error! Status: ${response.status}`);
        return response.json();
    })
    .then(data => {
        console.log(`[INFO] Zone created successfully:`, data);
        alert(`✅ Zone "${zoneName}" created successfully!`);
        document.getElementById("saveZone").classList.add("hidden");
        
        // Refresh zone types and parent zones after saving
        refreshZoneDropdowns();
    })
    .catch(error => {
        console.error("[ERROR] API Response:", error);
        alert("❌ Error saving zone. Check console for details.");
    });
}

// New function to refresh zone level and parent zone dropdowns
function refreshZoneDropdowns() {
    // Refresh zone level dropdown
    fetch("/get_zone_types")
        .then(response => response.json())
        .then(data => {
            let zoneSelect = document.getElementById("zoneLevel");
            // Clear existing options completely to prevent duplicates
            zoneSelect.innerHTML = "<option value=''>Select Zone Type</option>";

            data.forEach(zone => {
                let option = document.createElement("option");
                option.value = zone.api_endpoint || "";  // Store API endpoint directly
                option.textContent = zone.zone_name;
                option.dataset.zoneLevel = zone.zone_level; // Store zone level separately
                zoneSelect.appendChild(option);
            });

            console.log("[INFO] Refreshed zoneLevel dropdown with API endpoints:", data);
        })
        .catch(error => console.error("[ERROR] Refreshing zone types failed:", error));

    // Refresh parent zone dropdown
    fetch("/get_parent_zones")
        .then(response => response.json())
        .then(data => {
            let parentZoneSelect = document.getElementById("parentZoneSelect");
            // Clear existing options completely to prevent duplicates
            parentZoneSelect.innerHTML = "";

            let defaultOption = document.createElement("option");
            defaultOption.value = "";
            defaultOption.textContent = "(None - Parent Zone)";
            parentZoneSelect.appendChild(defaultOption);

            // Deduplicate zones by zone_id and add debugging log
            const uniqueZones = {};
            data.zones.forEach(zone => {
                if (!uniqueZones[zone.zone_id]) {
                    uniqueZones[zone.zone_id] = true;
                    let option = document.createElement("option");
                    option.value = zone.zone_id;
                    option.textContent = zone.name;
                    parentZoneSelect.appendChild(option);
                }
            });
            console.log(`[DEBUG] Refreshed parentZoneSelect with ${Object.keys(uniqueZones).length} unique zones:`, Object.keys(uniqueZones));
        })
        .catch(error => console.error("Error refreshing parent zones:", error));
}

function updateZoneLevel(event) {
    let selectedLevel = event.target.value;
    console.log(`[INFO] Updated Zone Level to: ${selectedLevel}`);
    currentZoneLevel = selectedLevel;
}

// Export all required functions (consolidated to fix duplicate export)
export { startDrawingZone, drawPoint, finishDrawingZone, saveZone, refreshZoneDropdowns, updateZoneLevel };