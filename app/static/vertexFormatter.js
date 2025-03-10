// Version: 250216 vertexFormatter.js Version 0P.6B.3C - SC's edits
//
// ParcoRTLS Middletier Services, ParcoRTLS DLL, ParcoDatabases, ParcoMessaging, and other code
// Copyright (C) 1999 - 2025 Affiliated Commercial Services Inc.
// Invented by Scott Cohen & Bertrand Dugal.
// Coded by Jesse Chunn O.B.M.'24 and Michael Farnsworth and Others
// Published at GitHub https://github.com/scocoh/IPS-RTLS-UWB
//
// Licensed under AGPL-3.0: https://www.gnu.org/licenses/agpl-3.0.en.html

export function formatVertices(points) {
    // Get scaling factors from sessionStorage
    let xScale = parseFloat(sessionStorage.getItem("x_scale")) || 1;
    let yScale = parseFloat(sessionStorage.getItem("y_scale")) || 1;
    let canvas = document.getElementById("zoneCanvas");

    let exportPoints = points.map(p => {
        let x = Math.round(p.x / xScale);  // Apply scaling and round to integer
        let y = Math.round((canvas.height - p.y) / yScale); // Flip Y-axis, apply scaling, and round

        return { 
            n_x: x,
            n_y: y,
            n_z: 0,
            n_ord: index + 1
         };
    });

}
