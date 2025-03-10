let drawingL3 = false;
let pointsL3 = [];

function showBuildingL3Form() {
    let l3Details = document.getElementById("buildingL3Details");
    let defineInteriorButton = document.getElementById("startL3Button");

    if (l3Details) {
        l3Details.classList.remove("hidden");
    }
    if (defineInteriorButton) {
        defineInteriorButton.classList.remove("hidden");
    }
}

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

    let buildingL3Name = document.getElementById("buildingL3Name").value;
    if (!buildingL3Name) {
        alert("Enter a Building L3 Name before defining the interior outline.");
        return;
    }

    console.log(`Starting drawing for Building L3: ${buildingL3Name}`);

    let storedL2Vertices = JSON.parse(sessionStorage.getItem("lastL2Vertices"));
    if (!storedL2Vertices || storedL2Vertices.length === 0) {
        alert("L2 vertices not found! Cannot proceed.");
        return;
    }

    // ✅ Load background map and dynamically adjust canvas size
    let img = new Image();
    img.src = `/get_map/${document.getElementById("mapSelect").value}`;

    img.onload = function () {
        // ✅ Dynamically set canvas size to match the map
        canvas.width = img.width;
        canvas.height = img.height;
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // ✅ Draw map background
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);

        // ✅ Fix Y-axis and draw L2 Outline (Red Border, No Fill)
        let formattedL2Vertices = formatVerticesForMapDisplay(storedL2Vertices, canvas.height);

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

    // ✅ Enable L3 Drawing Mode 
    drawingL3 = true;
    pointsL3 = [];

    alert("Click on the map to define the L3 building outline.");

    // ✅ Hide "Finish L3 Drawing" until 3 clicks
    document.getElementById("finishL3Button").classList.add("hidden");
    document.getElementById("saveL3Button").classList.add("hidden");

    // ✅ Bind Click Event to Capture Vertices
    canvas.removeEventListener("click", drawPointL3);
    canvas.addEventListener("click", drawPointL3);
}



function drawPointL3(event) { 
    if (!drawingL3) return;  // ✅ Ensure we are in drawing mode

    let canvas = document.getElementById("zoneCanvasL3");
    let rect = canvas.getBoundingClientRect();
    let rawX = event.clientX - rect.left;
    let rawY = event.clientY - rect.top;

    pointsL3.push({ x: rawX, y: rawY });

    let ctx = canvas.getContext("2d");
    ctx.fillStyle = "red";
    ctx.fillRect(rawX - 2, rawY - 2, 4, 4);

    if (pointsL3.length > 1) {
        ctx.beginPath();
        ctx.moveTo(pointsL3[pointsL3.length - 2].x, pointsL3[pointsL3.length - 2].y);
        ctx.lineTo(rawX, rawY);
        ctx.stroke();
    }

    // ✅ Only show "Finish L3 Drawing" after 3 clicks
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
    ctx.closePath();
    ctx.strokeStyle = "blue";
    ctx.lineWidth = 2;
    ctx.stroke();
    ctx.fillStyle = "rgba(0, 0, 255, 0.3)";
    ctx.fill();

    // ✅ Store the drawn L3 shape for saving later
    sessionStorage.setItem("lastL3Vertices", JSON.stringify(pointsL3));

    // ✅ Show Save Button
    document.getElementById("saveL3Button").classList.remove("hidden");

    // ✅ Disable drawing mode
    drawingL3 = false;
}

// ✅ Register the function globally
window.showBuildingL3Form = showBuildingL3Form;
window.startDrawingBuildingL3 = startDrawingBuildingL3;
window.drawPointL3 = drawPointL3;
window.finishDrawingL3 = finishDrawingL3;