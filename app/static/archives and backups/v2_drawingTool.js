import { formatVertices } from "./vertexFormatter.js";

let drawing = false;
let points = [];
window.points = []; // Ensure global accessibility

function startDrawingBuildingL2() {
    let canvas = document.getElementById("zoneCanvas");
    let ctx = canvas.getContext("2d");
    let buildingL2Name = document.getElementById("buildingL2Name").value;
    let buttonContainer = document.getElementById("saveBuildingL2Container");

    if (!buildingL2Name) {
        alert("Enter a Building Outside L2 Name before defining the outline.");
        return;
    }

    console.log(`Starting drawing for Building Outside L2: ${buildingL2Name}`);

    // Reset drawing state
    drawing = true;
    points = [];

    // Load map image
    let img = new Image();
    img.src = `/get_map/${document.getElementById("mapSelect").value}`;

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    img.onload = function () {
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
    };

    alert("Click on the map to define the building outline.");

    function drawPoint(event) {
        if (!drawing) return;
        let rect = canvas.getBoundingClientRect();
        let rawX = event.clientX - rect.left;
        let rawY = event.clientY - rect.top;

        points.push({ x: rawX, y: rawY });

        ctx.fillStyle = "red";
        ctx.fillRect(rawX - 2, rawY - 2, 4, 4);

        if (points.length > 1) {
            ctx.beginPath();
            ctx.moveTo(points[points.length - 2].x, points[points.length - 2].y);
            ctx.lineTo(rawX, rawY);
            ctx.stroke();
        }

        if (points.length >= 3) {
            ctx.beginPath();
            ctx.moveTo(points[0].x, points[0].y);
            for (let i = 1; i < points.length; i++) {
                ctx.lineTo(points[i].x, points[i].y);
            }
            ctx.closePath();
            ctx.fillStyle = "rgba(0, 0, 255, 0.3)";
            ctx.fill();

            if (!document.getElementById("finishDrawing")) {
                let finishButton = document.createElement("button");
                finishButton.id = "finishDrawing";
                finishButton.innerText = "Finish Drawing";
                finishButton.onclick = finishDrawing;
                buttonContainer.appendChild(finishButton);
            }
        }
    }

    function finishDrawing() {
        drawing = false;
    
        if (points.length < 3) {
            alert("At least three points are required to define the zone.");
            return;
        }
    
        // Ensure last point connects to the first point
        points.push({ x: points[0].x, y: points[0].y });
    
        ctx.beginPath();
        ctx.moveTo(points[0].x, points[0].y);
        for (let i = 1; i < points.length; i++) {
            ctx.lineTo(points[i].x, points[i].y);
        }
        ctx.closePath();
        ctx.strokeStyle = "blue";
        ctx.lineWidth = 2;
        ctx.stroke();
    
        alert("Building outline defined. Click 'Save Building Outside L2' to proceed.");

        let buttonContainer = document.getElementById("saveBuildingL2Container");

         // ✅ Ensure Save Building L2 button appears after finishing drawing
        if (!document.getElementById("saveBuildingL2")) {
            let saveButton = document.createElement("button");
            saveButton.id = "saveBuildingL2";
            saveButton.innerText = "Save Building Outside L2";
            saveButton.onclick = saveBuildingL2;
            buttonContainer.appendChild(saveButton);
        }
    }
    

    function saveBuildingL2() {
        let zoneId = sessionStorage.getItem("current_zone_id");
        let buildingL2Name = document.getElementById("buildingL2Name").value;
    
        if (!zoneId || !buildingL2Name || points.length < 3) {
            alert("Building Name and at least 3 boundary points are required.");
            return;
        }
    
        console.log(`Saving Building Outside L2: ${buildingL2Name} for Campus ID ${zoneId}`);
    
        // ✅ Format vertices before sending
        let formattedVertices = formatVertices(points);
    
        // ✅ Ensure last point connects to first for closed shape
        if (formattedVertices.length >= 3) {
            formattedVertices.push({ x: formattedVertices[0].x, y: formattedVertices[0].y });
        }
    
        let payload = {
            campus_id: zoneId,
            parent_zone_id: zoneId, // Ensure parent relationship is correct
            zone_name: buildingL2Name,
            vertices: formattedVertices
        };
    
        console.log("Sending payload:", payload);
    
        fetch('/create_building_outside_l2', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                alert(`Building Outside L2 "${buildingL2Name}" created successfully!`);
                
                // ✅ Store L2 vertices for L3 usage
                sessionStorage.setItem("lastL2Vertices", JSON.stringify(formattedVertices));

                // ✅ Open a new window for Define Building L3
                let mapId = document.getElementById("mapSelect").value;
                let newWindow = window.open(`/zonebuilder_ui_l3?map_id=${mapId}`, '_blank');

                if (!newWindow) {
                alert("Popup blocked! Please allow popups for this site.");
                }
                
                // ✅ Ensure L3 form is visible
                document.getElementById("buildingL3Details").classList.remove("hidden");
    
                // ✅ Enable Define Interior Outline button
                let startL3Button = document.getElementById("startL3Button");
                if (startL3Button) {
                    startL3Button.disabled = false;
}
            } else {
                alert(`Error: ${data.error}`);
            }
        })
        .catch(error => console.error("Error:", error));
    }
    


    canvas.removeEventListener("click", drawPoint);
    canvas.addEventListener("click", drawPoint);
}

// Register functions globally for HTML button access
window.startDrawingBuildingL2 = startDrawingBuildingL2;
window.finishDrawing = finishDrawing;
window.saveBuildingL2 = saveBuildingL2;
window.showBuildingL3Form = showBuildingL3Form;
window.drawL2BorderOnly = drawL2BorderOnly;
window.startDrawingBuildingL3 = startDrawingBuildingL3;
window.finishDrawingL3 = finishDrawingL3;
window.saveBuildingL3 = saveBuildingL3;

