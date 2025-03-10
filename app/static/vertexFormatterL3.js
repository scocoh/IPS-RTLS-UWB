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


