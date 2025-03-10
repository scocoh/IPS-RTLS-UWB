let drawingL3 = false;
let pointsL3 = [];

function startDrawingBuildingL3() {
    let canvas = document.getElementById("zoneCanvasL3");
    if (!canvas) {
        alert("Error: L3 Canvas not found! Make sure it exists in the HTML.");
        return;
    }

    let ctx = canvas.getContext("2d");
    if (!ctx) {
        alert("Error: Unable to get context from L3 Canvas.");
        return;
    }

    let buildingL3Name = document.getElementById("buildingL3Name")?.value;
    if (!buildingL3Name) {
        alert("Enter a Building L3 Name before defining the interior outline.");
        return;
    }

    console.log(`✅ Starting drawing for Building L3: ${buildingL3Name}`);

    // ✅ Check if L2 canvas exists before hiding it
    let l2Canvas = document.getElementById("zoneCanvasL2");
    if (l2Canvas) {
        l2Canvas.style.display = "none";
    } else {
        console.warn("⚠️ Warning: L2 Canvas not found. Skipping hide.");
    }

    canvas.style.display = "block";  // ✅ Ensure L3 is visible

    let storedL2Vertices = sessionStorage.getItem("lastL2Vertices");
    if (!storedL2Vertices) {
        alert("L2 vertices not found! Cannot proceed.");
        return;
    }

    let parsedL2Vertices;
    try {
        parsedL2Vertices = JSON.parse(storedL2Vertices);
        if (!Array.isArray(parsedL2Vertices) || parsedL2Vertices.length === 0) {
            throw new Error("Invalid or empty L2 vertices.");
        }
    } catch (error) {
        console.error("❌ Error parsing L2 vertices:", error);
        alert("Error loading L2 vertices. Cannot proceed.");
        return;
    }

    // ✅ Ensure map selection exists before fetching map
    let mapSelect = document.getElementById("mapSelect");
    let mapId = mapSelect ? mapSelect.value : "5"; // Default to map 5 if missing

    let img = new Image();
    img.src = `/get_map/${mapId}`;

    img.onload = function () {
        console.log(`✅ Map Loaded: ${img.src}`);
        canvas.width = img.width;
        canvas.height = img.height;
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // ✅ Draw map background
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);

        // ✅ Draw L2 Outline (Red Border, No Fill)
        let formattedL2Vertices = formatVerticesForMapDisplay(parsedL2Vertices, canvas.height);

        ctx.beginPath();
        ctx.moveTo(formattedL2Vertices[0].x, formattedL2Vertices[0].y);
        for (let i = 1; i < formattedL2Vertices.length; i++) {
            ctx.lineTo(formattedL2Vertices[i].x, formattedL2Vertices[i].y);
        }
        ctx.closePath();

        // ✅ Ensure L2 appears as an outline ONLY
        ctx.strokeStyle = "red";
        ctx.lineWidth = 2;
        ctx.stroke();
        ctx.fillStyle = "rgba(0,0,0,0)";  // Transparent fill
        ctx.fill();
    };

    img.onerror = function () {
        console.error("❌ Error loading map image:", img.src);
        alert("Failed to load map. Check map ID and server response.");
    };

    // ✅ Enable L3 Drawing Mode
    drawingL3 = true;
    pointsL3 = [];

    alert("Click on the map to define the L3 building outline.");

    // ✅ Hide "Finish L3 Drawing" until 3 clicks
    document.getElementById("finishL3Button")?.classList.add("hidden");
    document.getElementById("saveL3Button")?.classList.add("hidden");

    // ✅ Bind Click Event to Capture Vertices
    canvas.removeEventListener("click", drawPointL3);
    canvas.addEventListener("click", drawPointL3);
}




function drawPointL3(event) {
    if (!drawingL3) return;

    let canvas = document.getElementById("zoneCanvasL3");
    let rect = canvas.getBoundingClientRect();

    let rawX = event.clientX - rect.left;
    let rawY = event.clientY - rect.top;

    // **Prevent duplicate points**
    if (pointsL3.length > 0) {
        let lastPoint = pointsL3[pointsL3.length - 1];
        if (Math.abs(lastPoint.x - rawX) < 3 && Math.abs(lastPoint.y - rawY) < 3) {
            console.warn("⚠️ Duplicate point detected. Ignoring.");
            return;
        }
    }

    pointsL3.push({ x: rawX, y: rawY });

    let ctx = canvas.getContext("2d");
    ctx.fillStyle = "red";
    ctx.fillRect(rawX - 2, rawY - 2, 4, 4);

    if (pointsL3.length >= 3) {
        document.getElementById("finishL3Button").classList.remove("hidden");
    }
}


function finishDrawingL3() {
    if (pointsL3.length < 3) {
        alert("You must define at least 3 points to create an enclosed area.");
        return;
    }

    let ctx = document.getElementById("zoneCanvasL3").getContext("2d");
    ctx.beginPath();
    ctx.moveTo(pointsL3[0].x, pointsL3[0].y);
    for (let i = 1; i < pointsL3.length; i++) {
        ctx.lineTo(pointsL3[i].x, pointsL3[i].y);
    }

    // **Automatically close the polygon**
    ctx.lineTo(pointsL3[0].x, pointsL3[0].y);
    ctx.closePath();
    ctx.strokeStyle = "blue";
    ctx.lineWidth = 2;
    ctx.stroke();
    ctx.fillStyle = "rgba(0, 0, 255, 0.3)";
    ctx.fill();

    sessionStorage.setItem("lastL3Vertices", JSON.stringify(pointsL3));
    document.getElementById("saveL3Button").classList.remove("hidden");
    drawingL3 = false;
}

function saveBuildingL3() {
    let buildingL3Name = document.getElementById("buildingL3Name").value;
    if (!buildingL3Name) {
        alert("Enter a Building L3 Name before saving.");
        return;
    }

    let payload = {
        parent_zone_id: sessionStorage.getItem("lastL2ZoneID"),
        zone_name: buildingL3Name,
        vertices: pointsL3
    };

    console.log("📌 Sending Save Request:", JSON.stringify(payload));  // ✅ Log request

    fetch("/create_building_l3", {   // ✅ Ensure this is correct
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    })
    .then(response => response.json())
    .then(data => {
        console.log("✅ L3 Saved Response:", data);
        alert("Building L3 saved successfully!");

        sessionStorage.setItem("lastL3ZoneID", data.zone_id);
        window.location.href = "/define_floor_l4";
    })
    .catch(error => console.error("🚨 Error saving L3:", error));
}



// **Register Functions Globally**
window.startDrawingBuildingL3 = startDrawingBuildingL3;
window.drawPointL3 = drawPointL3;
window.finishDrawingL3 = finishDrawingL3;
window.saveBuildingL3 = saveBuildingL3;
