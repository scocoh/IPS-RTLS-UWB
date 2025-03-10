// ✅ Function to format vertices for map display (Fixes Y-axis flip)
function formatVerticesForMapDisplay(points, canvasHeight) {
    return points.map(p => ({
        x: p.x, 
        y: canvasHeight - p.y  // ✅ Flip Y-axis for correct display
    }));
}

// ✅ Expose function globally
window.formatVerticesForMapDisplay = formatVerticesForMapDisplay;
