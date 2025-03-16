// Version: 250227 campusMapLoader.js Version 0P.6B.48t 🚀
// // #  
// # ParcoRTLS Middletier Services, ParcoRTLS DLL, ParcoDatabases, ParcoMessaging, and other code
// # Copyright (C) 1999 - 2025 Affiliated Commercial Services Inc.
// # Invented by Scott Cohen & Bertrand Dugal.
// # Coded by Jesse Chunn O.B.M.'24 and Michael Farnsworth and Others
// # Published at GitHub https://github.com/scocoh/IPS-RTLS-UWB
// #
// # Licensed under AGPL-3.0: https://www.gnu.org/licenses/agpl-3.0.en.html

console.log("[INFO] Loaded campusMapLoader.js Version 0P.6B.48t 🚀");

// Declare mapImage and vertexData globally
let mapImage;
let vertexData; // Store vertex data globally
let mapMetadata; // Store map metadata globally for scaling

window.drawVertices = drawVertices; // Expose drawVertices globally for checkbox toggle

// Define renderZones globally to fix scoping issue
function renderZones(zones, depth = 0) {
    const zoneList = document.getElementById("zoneList");
    if (!zoneList) {
        console.error(`[ERROR] #zoneList not found (Version 0P.6B.48t).`);
        return;
    }

    (zones.zones || zones).forEach(zone => {
        if (zone.zone_id && zone.zone_name) {  // Ensure zone data exists
            const div = document.createElement("div");
            div.style.marginLeft = `${depth * 20}px`;
            const checkbox = document.createElement("input");
            checkbox.type = "checkbox";
            checkbox.checked = true;
            checkbox.dataset.zoneId = zone.zone_id;
            checkbox.addEventListener("change", () => {
                console.log(`[INFO] Checkbox toggled for zone ${zone.zone_name} (Version 0P.6B.48t):`, checkbox.checked);
                drawVertices();
            });
            div.appendChild(checkbox);
            const label = document.createElement("span");
            label.textContent = ` ${zone.zone_name}`;
            div.appendChild(label);
            zoneList.appendChild(div);
            if (zone.children && Array.isArray(zone.children)) {
                renderZones(zone.children, depth + 1);
            }
        } else {
            console.warn(`[WARN] Invalid zone data skipped:`, zone);
        }
    });
}

// Define drawVertices globally
function drawVertices() {
    const canvas = document.getElementById("zoneCanvas");
    if (!canvas) {
        console.error(`[ERROR] Canvas not found (Version 0P.6B.48t).`);
        return;
    }
    const ctx = canvas.getContext("2d");
    if (!ctx) {
        console.error(`[ERROR] Canvas context not available (Version 0P.6B.48t).`);
        return;
    }

    if (!mapImage || !mapMetadata || !vertexData) {
        console.warn(`[WARN] Missing required data - mapImage: ${!!mapImage}, mapMetadata: ${!!mapMetadata}, vertexData: ${!!vertexData}`);
        return;
    }

    const showVerticesCheckbox = document.getElementById("showVertices");
    if (!showVerticesCheckbox) {
        console.error(`[ERROR] Show Vertices checkbox not found (Version 0P.6B.48t).`);
        return;
    }

    const canvasWidth = canvas.width;
    const canvasHeight = canvas.height;
    const mapWidth = mapMetadata.max_x - mapMetadata.min_x;
    const mapHeight = mapMetadata.max_y - mapMetadata.min_y;
    const scaleX = canvasWidth / mapWidth;
    const scaleY = canvasHeight / mapHeight;
    const scale = Math.min(scaleX, scaleY);

    ctx.clearRect(0, 0, canvasWidth, canvasHeight);
    ctx.drawImage(mapImage, 0, 0, mapWidth * scale, mapHeight * scale);

    if (showVerticesCheckbox.checked) {
        console.log(`[INFO] Rendering vertices (Version 0P.6B.48t)`);
        const checkedZones = Array.from(document.querySelectorAll('#zoneList input[type="checkbox"]:checked'))
            .map(cb => parseInt(cb.dataset.zoneId))
            .filter(id => !isNaN(id));
        console.log(`[DEBUG] Checked zones (Version 0P.6B.48t):`, checkedZones);

        if (checkedZones.length === 0) {
            console.warn(`[WARN] No zones checked; skipping vertex rendering (Version 0P.6B.48t).`);
            return;
        }

        checkedZones.forEach(zoneId => {
            const verticesForZone = vertexData.vertices
                .filter(v => parseInt(v.zone_id) === zoneId)
                .sort((a, b) => a.order - b.order);
            console.log(`[DEBUG] Vertices for zone ${zoneId}:`, verticesForZone);

            verticesForZone.forEach((v, index) => {
                const scaledX = (v.x - mapMetadata.min_x) * scale;
                const scaledY = canvasHeight - ((v.y - mapMetadata.min_y) * scale);
                console.log(`[DEBUG] Drawing vertex at (${scaledX}, ${scaledY}) for zone ${zoneId}`);

                ctx.beginPath();
                ctx.arc(scaledX, scaledY, 5, 0, 2 * Math.PI);
                ctx.fillStyle = "red";
                ctx.fill();

                // Draw vertex number next to the point
                ctx.font = "12px Arial";
                ctx.fillStyle = "black";
                ctx.fillText(index + 1, scaledX + 8, scaledY - 2); // Offset label slightly
            });

            for (let i = 0; i < verticesForZone.length; i++) {
                const v = verticesForZone[i];
                const nextVertex = verticesForZone[(i + 1) % verticesForZone.length];
                const scaledX = (v.x - mapMetadata.min_x) * scale;
                const scaledY = canvasHeight - ((v.y - mapMetadata.min_y) * scale);
                const nextScaledX = (nextVertex.x - mapMetadata.min_x) * scale;
                const nextScaledY = canvasHeight - ((nextVertex.y - mapMetadata.min_y) * scale);

                ctx.beginPath();
                ctx.moveTo(scaledX, scaledY);
                ctx.lineTo(nextScaledX, nextScaledY);
                ctx.strokeStyle = "red";
                ctx.lineWidth = 2;
                ctx.stroke();
            }
        });
    } else {
        console.log(`[INFO] Vertices hidden (Show Vertices unchecked)`);
    }
}

function loadCampuses() {
    console.info('Fetching Campuses (Version 0P.6B.48t)...');
    fetch('/get_campus_zones')
        .then(response => {
            if (!response.ok) throw new Error(`HTTP Error! Status: ${response.status}`);
            return response.json();
        })
        .then(data => {
            console.debug('Campus data (Version 0P.6B.48t):', data);
            const campusDropdown = document.getElementById("campusSelect");
            campusDropdown.innerHTML = "<option value=''>Select Campus</option>";

            // Handle the response as a list of campuses (direct array or hierarchical structure)
            let campuses = Array.isArray(data) ? data : (data.campuses || []);
            if (!Array.isArray(campuses)) {
                console.error('Unexpected campus data format (Version 0P.6B.48t):', data);
                throw new Error('Invalid campus data format');
            }

            if (campuses.length === 0) {
                console.warn(`[WARN] No campuses found in response (Version 0P.6B.48t)`);
            }

            campuses.forEach(campus => {
                // Only process Campus L1 zones (zone_type = 1) for the dropdown, with fallback for missing fields
                const zoneType = campus.zone_type || (campus.zone_type === 0 ? 0 : null); // Default to null if undefined
                const mapId = campus.map_id || null;
                const campusId = campus.zone_id || null; // Use zone_id as campus_id since the response uses zone_id

                if (zoneType === 1 && mapId && campusId) {  
                    console.debug(`[DEBUG] Adding campus to dropdown: ${campus.name || 'Unnamed'} (map_id: ${mapId}, campus_id: ${campusId})`);
                    const option = document.createElement("option");
                    option.value = mapId;
                    option.textContent = campus.name || `Campus ID ${campusId}`; // Fallback name if missing
                    option.dataset.campusId = String(campusId);  // Ensure campus_id is set as a string, then parsed as int
                    campusDropdown.appendChild(option);
                } else {
                    console.debug(`[DEBUG] Skipping non-CL1 zone or null/invalid data: ${campus.name || 'Unnamed'} (zone_type: ${zoneType}, map_id: ${mapId}, campus_id: ${campusId})`);
                }
            });
            console.info('Campuses loaded successfully (Version 0P.6B.48t).');
        })
        .catch(error => {
            console.error('[ERROR] Fetching campuses failed (Version 0P.6B.48t):', error);
            alert("🚨 Error fetching campus list.");
        });
}

function processCampus(campus) {
    console.debug('Processing campus:', campus);
    if (!campus.map_id) {
        console.debug(`Skipping campus due to null map_id: ${campus.name || 'Unnamed'} (Version 0P.6B.48t)`);
        return; // Skip if map_id is null
    }

    // Recursively process all children for hierarchy in zone list (CL1, BOL2, BL3), but only add CL1 to dropdown
    const zoneType = campus.zone_type || null;
    const campusId = campus.zone_id || null; // Use zone_id as campus_id since the response uses zone_id

    if (zoneType === 1 && campusId) {  // Only add Campus L1 to dropdown, ensure campus_id exists
        const campusDropdown = document.getElementById("campusSelect");
        const option = document.createElement("option");
        option.value = campus.map_id;
        option.textContent = campus.name || `Campus ID ${campusId}`;
        option.dataset.campusId = String(campusId); // Ensure campus_id is set as a string, then parsed as int
        campusDropdown.appendChild(option);
    }

    // Recursively process all children for hierarchy in zone list
    if (campus.children && Array.isArray(campus.children)) {
        campus.children.forEach(child => processCampus(child));
    }
    console.info(`Campus loaded successfully: ${campus.name || 'Unnamed'} (map_id: ${campus.map_id}, Version 0P.6B.48t)`);
}

function loadCampusMap() {
    const selectedCampus = document.getElementById("campusSelect").value;
    const campusIdElement = document.getElementById("campusSelect").selectedOptions[0];
    const campusIdStr = campusIdElement ? campusIdElement.dataset.campusId : null;
    const campusId = campusIdStr ? parseInt(campusIdStr, 10) : null; // Use null if invalid, not NaN
    if (!selectedCampus || !campusId || isNaN(campusId)) {
        console.error(`[ERROR] Invalid campus selection: selectedCampus=${selectedCampus}, campusId=${campusId} (Version 0P.6B.48t)`);
        alert("🚨 Please select a valid campus.");
        return;
    }

    console.log(`[INFO] Loading map for Campus map_id ${selectedCampus} (campus_id: ${campusId}, Version 0P.6B.48t)...`);
    const canvas = document.getElementById("zoneCanvas");
    const ctx = canvas.getContext("2d");
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Add "Select Zones & Vertices" and "Show Vertices" checkbox immediately
    const zoneList = document.getElementById("zoneList");
    if (!zoneList) {
        console.error(`[ERROR] #zoneList not found (Version 0P.6B.48t).`);
        return;
    }
    zoneList.innerHTML = ""; // Clear zone list first
    if (!document.getElementById("showVertices")) {
        const vertexToggle = document.createElement("div");
        vertexToggle.innerHTML = `<input type="checkbox" id="showVertices" checked> Show Vertices`;
        zoneList.prepend(vertexToggle);
        document.getElementById("showVertices").addEventListener("change", () => {
            console.log(`[INFO] Show Vertices toggled: ${document.getElementById("showVertices").checked} (Version 0P.6B.48t)`);
            drawVertices();
        });
    }

    // Fetch and display the map from zonebuilder_api.py on port 5002
    fetch(`http://192.168.210.231:5002/get_map/${selectedCampus}`)  
        .then(response => {
            console.log(`[DEBUG] Map fetch response for /get_map/${selectedCampus} (Version 0P.6B.48t):`, response);
            if (!response.ok) throw new Error(`Map fetch failed: ${response.status}`);
            return response.blob();
        })
        .then(blob => {
            console.log(`[DEBUG] Map blob received (Version 0P.6B.48t):`, blob);
            mapImage = new Image();
            mapImage.crossOrigin = "Anonymous";
            mapImage.onload = () => {
                fetch(`http://192.168.210.231:5002/get_map_metadata/${selectedCampus}`)  
                    .then(metaResponse => {
                        console.log(`[DEBUG] Map metadata fetch response for /get_map_metadata/${selectedCampus} (Version 0P.6B.48t):`, metaResponse);
                        if (!metaResponse.ok) throw new Error(`Metadata fetch failed: ${metaResponse.status}`);
                        return metaResponse.json();
                    })
                    .then(metadata => {
                        console.log(`[DEBUG] Map metadata (Version 0P.6B.48t):`, metadata);
                        mapMetadata = metadata;
                        if (metadata.min_x && metadata.max_x && metadata.min_y && metadata.max_y) {
                            const mapWidth = metadata.max_x - metadata.min_x;
                            const mapHeight = metadata.max_y - metadata.min_y;
                            const canvasWidth = canvas.width;
                            const canvasHeight = canvas.height;
                            const scaleX = canvasWidth / mapWidth;
                            const scaleY = canvasHeight / mapHeight;
                            const scale = Math.min(scaleX, scaleY);
                            ctx.clearRect(0, 0, canvasWidth, canvasHeight);
                            ctx.drawImage(mapImage, 0, 0, mapWidth * scale, mapHeight * scale);
                        } else {
                            ctx.drawImage(mapImage, 0, 0, canvas.width, canvas.height);
                        }
                        if (vertexData) drawVertices(); // Only call if vertices are loaded
                    })
                    .catch(metaError => console.error(`[ERROR] Fetching map metadata failed (Version 0P.6B.48t):`, metaError));
                console.log(`[DEBUG] Map drawn on canvas (Version 0P.6B.48t).`);
            };
            mapImage.src = URL.createObjectURL(blob);
        })
        .catch(error => console.error(`[ERROR] Loading map failed (Version 0P.6B.48t):`, error));

    // Fetch and display all zones recursively with event listeners from zonebuilder_api.py on port 5002
    fetch(`http://192.168.210.231:5002/get_all_zones_for_campus/${campusId}`)  
        .then(response => {
            console.log(`[DEBUG] Zones fetch response for /get_all_zones_for_campus/${campusId} (Version 0P.6B.48t):`, response);
            if (!response.ok) {
                console.error(`[ERROR] Zones fetch failed: ${response.status} - ${response.statusText}`);
                throw new Error(`Zones fetch failed: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log(`[DEBUG] Zones data (Version 0P.6B.48t):`, data);
            renderZones(data); // Use global renderZones function
            console.log(`[INFO] Zones loaded successfully (Version 0P.6B.48t).`);
            if (mapImage && mapMetadata && vertexData) drawVertices(); // Render if all data is ready
        })
        .catch(error => {
            console.error(`[ERROR] Loading zones failed (Version 0P.6B.48t):`, error);
            if (error.message.includes('404')) {
                console.warn(`[WARN] Zones not found for campus ${campusId}, defaulting to empty list`);
                renderZones([]); // Use global renderZones for empty list
            }
        });

    // Fetch and display vertices from zonebuilder_api.py on port 5002
    fetch(`http://192.168.210.231:5002/get_vertices_for_campus/${campusId}`)  
        .then(response => {
            console.log(`[DEBUG] Vertices fetch response for /get_vertices_for_campus/${campusId} (Version 0P.6B.48t):`, response);
            if (!response.ok) {
                console.error(`[ERROR] Vertices fetch failed: ${response.status} - ${response.statusText}`);
                throw new Error(`Vertices fetch failed: ${response.status}`);
            }
            return response.json();
        })
        .then(responseData => {
            console.log(`[DEBUG] Vertices data (Version 0P.6B.48t):`, responseData);
            vertexData = responseData;
            if (mapImage && mapMetadata) drawVertices(); // Render once vertices are loaded
        })
        .catch(error => {
            console.error(`[ERROR] Loading vertices failed (Version 0P.6B.48t):`, error);
            if (error.message.includes('404')) {
                console.warn(`[WARN] Vertices not found for campus ${campusId}, defaulting to empty data`);
                vertexData = { vertices: [] }; // Default to empty vertices to avoid breaking UI
                if (mapImage && mapMetadata) drawVertices(); // Render empty vertices
            }
        });
}

// NEW FUNCTION: Load vertices for selected zones and populate the edit table
function loadVerticesForSelectedZones() {
    const checkedZones = Array.from(document.querySelectorAll('#zoneList input[type="checkbox"]:checked'))
        .map(cb => parseInt(cb.dataset.zoneId))
        .filter(id => !isNaN(id));

    if (checkedZones.length === 0) {
        console.warn(`[WARN] No zones selected for vertex loading (Version 0P.6B.48t).`);
        alert("Please select at least one zone to load vertices.");
        return;
    }

    console.log(`[INFO] Loading vertices for zones:`, checkedZones);
    const vertexTableBody = document.querySelector("#vertexTable tbody");
    vertexTableBody.innerHTML = ""; // Clear existing rows

    checkedZones.forEach((zoneId, zoneIndex) => {
        const verticesForZone = vertexData.vertices
            .filter(v => parseInt(v.zone_id) === zoneId)
            .sort((a, b) => a.order - b.order);

        verticesForZone.forEach((vertex, index) => {
            const row = document.createElement("tr");
            const vertexNum = zoneIndex * 100 + (index + 1); // Unique vertex number across zones (e.g., 101, 102 for zone 1)
            row.innerHTML = `
                <td>${vertexNum}</td>
                <td><input type="number" value="${vertex.x}" data-field="x" data-vertex-id="${vertex.vertex_id}"></td>
                <td><input type="number" value="${vertex.y}" data-field="y" data-vertex-id="${vertex.vertex_id}"></td>
                <td><input type="number" value="${vertex.z || 0}" data-field="z" data-vertex-id="${vertex.vertex_id}"></td>
                <td><button disabled>Save</button></td> <!-- Individual save buttons disabled for now -->
            `;
            vertexTableBody.appendChild(row);
        });
    });

    drawVertices(); // Refresh the map with current vertex data
}

// NEW FUNCTION: Save all edited vertices to the backend
function saveAllVertices() {
    const rows = document.querySelectorAll("#vertexTable tbody tr");
    const updatedVertices = Array.from(rows).map(row => {
        const vertexId = row.querySelector('input[data-field="x"]').dataset.vertexId;
        return {
            vertex_id: parseInt(vertexId),
            x: parseFloat(row.querySelector('input[data-field="x"]').value),
            y: parseFloat(row.querySelector('input[data-field="y"]').value),
            z: parseFloat(row.querySelector('input[data-field="z"]').value)
        };
    });

    console.log(`[INFO] Saving updated vertices:`, updatedVertices);

    fetch('http://192.168.210.231:5002/update_vertices', {  
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ vertices: updatedVertices })
    })
        .then(response => {
            if (!response.ok) throw new Error(`Failed to save vertices: ${response.status}`);
            return response.json();
        })
        .then(data => {
            console.log(`[INFO] Vertices saved successfully:`, data);
            // Update local vertexData with the new values
            updatedVertices.forEach(updated => {
                const vertex = vertexData.vertices.find(v => v.vertex_id === updated.vertex_id);
                if (vertex) {
                    vertex.x = updated.x;
                    vertex.y = updated.y;
                    vertex.z = updated.z;
                }
            });
            drawVertices(); // Refresh the map with updated vertices
            alert("Vertices updated successfully!");
        })
        .catch(error => {
            console.error(`[ERROR] Failed to save vertices:`, error);
            alert("Error saving vertices. Check console for details.");
        });
}

// Export all required functions for ES module usage
export { loadCampusMap, loadCampuses, loadVerticesForSelectedZones, saveAllVertices, renderZones }; // Export renderZones globally