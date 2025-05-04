/* Name: mapLoader_pac.js */
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

// Version: 250218  mapLoader.js Version 0P.6B.4Z
// 
//  ParcoRTLS Middletier Services, ParcoRTLS DLL, ParcoDatabases, ParcoMessaging, and other code
//  Copyright (C) 1999 - 2025 Affiliated Commercial Services Inc.
//  Invented by Scott Cohen & Bertrand Dugal.
//  Coded by Jesse Chunn O.B.M.'24 and Michael Farnsworth and Others
//  Published at GitHub https://github.com/scocoh/IPS-RTLS-UWB
// 
//  Licensed under AGPL-3.0: https://www.gnu.org/licenses/agpl-3.0.en.html
//  🔥 FIXED: export { loadmap } as last line so that drawingTool.js can import
//     confirmed final line of export
//     check if zone details existing in function loadmap
//     REPLACED all code
//     Remove unnecessary validation.
//     Use the values directly from the response instead of expecting a nested bounds object.
//     Map metadata is correctly saved in window.mapScaling before calling drawPoint().
//     Draw logic only executes once scaling values are available.
//     added console log
// changed export function loadMap replaced with updated export function
// mapLoader.js - Handles map selection, metadata, display, and zoom
// mapLoader.js loadmap change
// updated image loading section at bottom and changed from this code img.src = `/get_map/${document.getElementById("mapSelect").value}`
// in step 3.1 replaced function applyZoom
// replaced the entire export function loadMap to try to get the map to display
// add globally available zoom at bottom and bump version to 4R
// replace applyZoom to try to resolve zoom issue 4S
// added import points at first line, change apply zoom (again), and modify redrawPointsAndLines to resolve zoom issue 4T// 
//  🔥 FIXED: Zooming issues - properly updates canvas width & height
//  🔥 FIXED: Ensure points persist after zoom
//  🔥 FIXED: Correct scaling of points after zoom
//  🔥 FIXED: Import `points` correctly from `drawingTool.js`
// replaced applyZoom to have better zoom details 4V, 4W, 4X
// replaced loadMap and applyZoomto have bigger canvas at load 4Y

import { points } from "./drawingTool.js";

console.log("[INFO] Loaded mapLoader.js Version 0P.6B.4Z");

let zoomLevel = 1.0; // Initial zoom level
const zoomStep = 0.2; // Zoom increment/decrement step
const minZoom = 0.5; // Minimum zoom level
const maxZoom = 3.0; // Maximum zoom level;
let originalWidth, originalHeight;

export function loadMaps() {
    console.log("[INFO] Fetching maps...");
    fetch('/get_maps')
        .then(response => response.json())
        .then(data => {
            let mapDropdown = document.getElementById("mapSelect");
            mapDropdown.innerHTML = "<option value=''>Select Map</option>";
            data.maps.forEach(map => {
                let option = document.createElement("option");
                option.value = map.map_id;
                option.textContent = map.name;
                mapDropdown.appendChild(option);
            });
            console.log("[INFO] Maps loaded successfully.");
        })
        .catch(error => console.error("[ERROR] Fetching maps failed:", error));
}

export function loadMap() {
    let selectedMap = document.getElementById("mapSelect").value;
    if (!selectedMap) {
        console.error("[ERROR] No map selected! Cannot load map image.");
        alert("🚨 Please select a map before loading.");
        return;
    }

    console.log(`[INFO] Loading map ${selectedMap}`);

    fetch(`/get_map_metadata/${selectedMap}`)
        .then(response => response.json())
        .then(metadata => {
            console.log("[INFO] Map Metadata Response:", metadata);

            if (
                metadata.min_x === undefined || metadata.min_y === undefined ||
                metadata.max_x === undefined || metadata.max_y === undefined
            ) {
                console.error("[ERROR] Map metadata missing required fields!", metadata);
                alert("🚨 Error fetching map metadata. Please check API response!");
                return;
            }

            // ✅ Store Map Scaling
            window.mapScaling = {
                min_x: metadata.min_x,
                min_y: metadata.min_y,
                max_x: metadata.max_x,
                max_y: metadata.max_y
            };

            sessionStorage.setItem("map_metadata", JSON.stringify(metadata));

            console.log(`[INFO] Stored Map Scaling - X: (${metadata.min_x}, ${metadata.max_x}), Y: (${metadata.min_y}, ${metadata.max_y})`);

            let canvas = document.getElementById("zoneCanvas");
            let ctx = canvas.getContext("2d");

            // ✅ Ensure the canvas starts at a 5x larger size
            originalWidth = (metadata.max_x - metadata.min_x) * 5;
            originalHeight = (metadata.max_y - metadata.min_y) * 5;
            zoomLevel = 1.0; // Reset zoom level

            canvas.width = originalWidth;
            canvas.height = originalHeight;

            sessionStorage.setItem("originalWidth", originalWidth);
            sessionStorage.setItem("originalHeight", originalHeight);

            let img = new Image();

            img.onload = function () {
                console.log(`[DEBUG] Successfully loaded map image: ${img.src}`);
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                ctx.imageSmoothingEnabled = false;
                ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
            };

            img.onerror = function () {
                console.error("[ERROR] Map image failed to load! URL:", img.src);
                alert("🚨 Error loading the map image. Please check the API.");
            };

            let mapURL = `/get_map/${selectedMap}?t=${new Date().getTime()}`;
            console.log(`[DEBUG] Setting img.src = ${mapURL}`);

            img.src = mapURL;
        })
        .catch(error => {
            console.error("[ERROR] Fetching map metadata:", error);
            alert("🚨 Error fetching map metadata. Please check API response!");
        });
}

export function zoomIn() {
    if (zoomLevel < maxZoom) {
        zoomLevel += zoomStep;
        applyZoom();
    }
}

export function zoomOut() {
    if (zoomLevel > minZoom) {
        zoomLevel -= zoomStep;
        applyZoom();
    }
}

function applyZoom() {
    let canvas = document.getElementById("zoneCanvas");
    let ctx = canvas.getContext("2d");

    let selectedMap = document.getElementById("mapSelect").value;
    if (!selectedMap) {
        console.error("[ERROR] No map selected! Cannot apply zoom.");
        alert("🚨 Please select a map before applying zoom.");
        return;
    }

    let maxZoom = 5.0;  // ✅ Ensure max zoom is large enough
    let minZoom = 1.0;  // ✅ Prevent shrinking smaller than original

    // ✅ Keep zoom within allowed range
    zoomLevel = Math.min(maxZoom, Math.max(minZoom, zoomLevel));

    let newWidth = Math.round(originalWidth * zoomLevel);
    let newHeight = Math.round(originalHeight * zoomLevel);

    // ✅ Update Canvas Element Size
    canvas.width = newWidth;
    canvas.height = newHeight;
    canvas.style.width = `${newWidth}px`;
    canvas.style.height = `${newHeight}px`;

    console.log(`[INFO] Zoom Level: ${zoomLevel}, Canvas Updated to: ${newWidth} x ${newHeight}`);

    let img = new Image();
    img.onload = function () {
        console.log(`[DEBUG] Successfully loaded map image: ${img.src}`);
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.imageSmoothingEnabled = false;
        ctx.drawImage(img, 0, 0, newWidth, newHeight);

        // ✅ Redraw points and lines at new zoom level
        redrawPointsAndLines(ctx);
    };

    img.onerror = function () {
        console.error("[ERROR] Map image failed to load! URL:", img.src);
        alert("🚨 Error loading the map image. Please check the API.");
    };

    let mapURL = `/get_map/${selectedMap}?t=${new Date().getTime()}`;
    console.log(`[DEBUG] Setting img.src = ${mapURL}`);
    img.src = mapURL;
}

/**
 * ✅ **Redraw markers and lines after zooming**
 */
function redrawPointsAndLines(ctx) {
    if (!window.mapScaling) {
        console.error("🚨 Error: Map scaling values are not defined!");
        return;
    }

    if (!points || points.length === 0) {
        console.log("[INFO] No points to redraw.");
        return;
    }

    console.log("[INFO] Redrawing points and lines after zoom...");
    ctx.strokeStyle = "red";
    ctx.lineWidth = 2;

    ctx.beginPath();
    points.forEach((point, index) => {
        let scaledX = point.x * zoomLevel;
        let scaledY = point.y * zoomLevel;

        if (index === 0) {
            ctx.moveTo(scaledX, scaledY);
        } else {
            ctx.lineTo(scaledX, scaledY);
        }

        ctx.fillStyle = "red";
        ctx.beginPath();
        ctx.arc(scaledX, scaledY, 3, 0, 2 * Math.PI);
        ctx.fill();
    });

    ctx.stroke();
}

window.onload = loadMaps;
window.zoomIn = zoomIn;
window.zoomOut = zoomOut;
