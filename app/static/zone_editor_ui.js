/**
 * Version: 250220 zone_editor_ui.js Version 0P.6B.3S
 * 
 * ParcoRTLS Middletier Services, ParcoRTLS DLL, ParcoDatabases, ParcoMessaging, and other code
 * Copyright (C) 1999 - 2025 Affiliated Commercial Services Inc.
 * Invented by Scott Cohen & Bertrand Dugal.
 * Coded by Jesse Chunn O.B.M.'24 and Michael Farnsworth and Others
 * Published at GitHub https://github.com/scocoh/IPS-RTLS-UWB
 * 
 * Licensed under AGPL-3.0: https://www.gnu.org/licenses/agpl-3.0.en.html
 */

document.addEventListener("DOMContentLoaded", () => {
    const parentSelect = document.getElementById("parentSelect");
    const childContainer = document.getElementById("childZones");
    const mapImage = document.getElementById("mapImage");
    let zoneLayers = {}; // Store rendered zones

    // ✅ Fetch Parent Zones
    fetch('/api/get_parents')
        .then(response => response.json())
        .then(data => {
            data.parents.forEach(parent => {
                let option = document.createElement("option");
                option.value = parent.i_zn;
                option.textContent = parent.x_nm_zn;
                parentSelect.appendChild(option);
            });

            // Load the first parent zone automatically
            if (data.parents.length > 0) {
                parentSelect.value = data.parents[0].i_zn;
                loadParentZone(data.parents[0].i_zn);
            }
        });

    parentSelect.addEventListener("change", () => {
        loadParentZone(parentSelect.value);
    });

    // ✅ Load Parent Zone and its Map
    function loadParentZone(parentId) {
        // Load map image from database
        mapImage.src = `/api/get_map/${parentId}`;

        // Load child zones dynamically
        fetch(`/api/get_children/${parentId}`)
            .then(response => response.json())
            .then(data => {
                childContainer.innerHTML = "";  // Clear old child zone checkboxes

                data.children.forEach(child => {
                    let checkbox = document.createElement("input");
                    checkbox.type = "checkbox";
                    checkbox.value = child.i_zn;
                    checkbox.addEventListener("change", () => toggleChildZone(child.i_zn, checkbox.checked));

                    let label = document.createElement("label");
                    label.textContent = child.x_nm_zn;
                    childContainer.appendChild(checkbox);
                    childContainer.appendChild(label);
                    childContainer.appendChild(document.createElement("br"));
                });
            });
    }

    // ✅ Toggle Child Zone Visibility
    function toggleChildZone(zoneId, show) {
        fetch(`/api/get_zone_vertices/${zoneId}`)
            .then(response => response.json())
            .then(data => {
                let canvas = document.getElementById("zoneCanvas");
                let ctx = canvas.getContext("2d");

                if (show) {
                    ctx.strokeStyle = "red";
                    ctx.lineWidth = 2;
                    ctx.beginPath();
                    data.vertices.forEach((vertex, index) => {
                        let x = vertex.n_x, y = vertex.n_y;
                        if (index === 0) {
                            ctx.moveTo(x, y);
                        } else {
                            ctx.lineTo(x, y);
                        }
                    });
                    ctx.closePath();
                    ctx.stroke();

                    zoneLayers[zoneId] = data.vertices;
                } else {
                    ctx.clearRect(0, 0, canvas.width, canvas.height);
                    delete zoneLayers[zoneId];
                }
            });
    }
});
