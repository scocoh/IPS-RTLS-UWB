// Version: 250216 vertexFormatterL3.js Version 0P.6B.3C - SC's edits
//
// ParcoRTLS Middletier Services, ParcoRTLS DLL, ParcoDatabases, ParcoMessaging, and other code
// Copyright (C) 1999 - 2025 Affiliated Commercial Services Inc.
// Invented by Scott Cohen & Bertrand Dugal.
// Coded by Jesse Chunn O.B.M.'24 and Michael Farnsworth and Others
// Published at GitHub https://github.com/scocoh/IPS-RTLS-UWB
//
// Licensed under AGPL-3.0: https://www.gnu.org/licenses/agpl-3.0.en.html
function formatVerticesForL3(vertices, mapHeight, bounds) {
    if (!vertices || vertices.length === 0) {
        console.error("No vertices provided for formatting L3.");
        return [];
    }
    
    let scaleX = mapHeight / (bounds.y_max - bounds.y_min);
    let scaleY = mapHeight / (bounds.y_max - bounds.y_min);

    return vertices.map(v => ({
        x: (v.x - bounds.x_min) * scaleX,
        y: (v.y - bounds.y_min) * scaleY

    }));
}

function adjustL3CoordinatesForMap(vertices, canvas) {
    if (!vertices || vertices.length === 0 || !canvas) {
        console.error("Invalid input for adjusting L3 coordinates.");
        return [];
    }
    
    let scaleX = canvas.width / canvas.clientWidth;
    let scaleY = canvas.height / canvas.clientHeight;
    
    return vertices.map(v => ({
        x: v.x * scaleX,
        y: v.y * scaleY
    }));
}


