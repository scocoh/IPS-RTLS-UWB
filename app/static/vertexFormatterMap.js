// ✅ Function to format vertices for map display (Fixes Y-axis flip)
// Version: 250216 vertexFormatter.js Version 0P.6B.3C - SC's edits
// /home/parcoadmin/parco_fastapi/app/static/vertexFormatterMap.js
// ParcoRTLS Middletier Services, ParcoRTLS DLL, ParcoDatabases, ParcoMessaging, and other code
// Copyright (C) 1999 - 2025 Affiliated Commercial Services Inc.
// Invented by Scott Cohen & Bertrand Dugal.
// Coded by Jesse Chunn O.B.M.'24 and Michael Farnsworth and Others
// Published at GitHub https://github.com/scocoh/IPS-RTLS-UWB
//
// Licensed under AGPL-3.0: https://www.gnu.org/licenses/agpl-3.0.en.html
function formatVerticesForMapDisplay(points, canvasHeight) {
    return points.map(p => ({
        x: p.x, 
        y: canvasHeight - p.y  // ✅ Flip Y-axis for correct display
    }));
}

// ✅ Expose function globally
window.formatVerticesForMapDisplay = formatVerticesForMapDisplay;
