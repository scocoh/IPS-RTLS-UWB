import React, { useState } from "react";

const TriggerUX2025 = () => {
  const [triggerName, setTriggerName] = useState("");
  const [zone, setZone] = useState("");
  const [direction, setDirection] = useState("");
  const [width, setWidth] = useState("8");
  const [color, setColor] = useState("#ff0000");
  const [useLeaflet, setUseLeaflet] = useState(false);

  const handleCreateTrigger = () => {
    console.log("Creating trigger:", {
      triggerName,
      zone,
      direction,
      width,
      color,
      useLeaflet,
    });
    alert("Trigger created (console.log for now)");
  };

  return (
    <div style={{ padding: "20px", fontFamily: "Arial, sans-serif" }}>
      <h1 style={{ fontSize: "24px", fontWeight: "bold", marginBottom: "20px" }}>
        Trigger Management (UX 2025 - Lite)
      </h1>

      <div style={{
        display: "flex",
        gap: "40px",
        flexWrap: "wrap"
      }}>
        {/* Create Trigger Form */}
        <div style={{
          flex: "1",
          minWidth: "300px",
          border: "1px solid #ccc",
          borderRadius: "8px",
          padding: "20px"
        }}>
          <h2 style={{ fontSize: "18px", marginBottom: "10px" }}>Create Trigger</h2>

          <div style={{ marginBottom: "10px" }}>
            <label>Trigger Name:</label><br />
            <input
              type="text"
              value={triggerName}
              onChange={(e) => setTriggerName(e.target.value)}
              style={{ width: "100%" }}
            />
          </div>

          <div style={{ marginBottom: "10px" }}>
            <label>Parent Zone:</label><br />
            <select value={zone} onChange={(e) => setZone(e.target.value)} style={{ width: "100%" }}>
              <option value="">Select Zone</option>
              <option value="zone1">Zone 1</option>
              <option value="zone2">Zone 2</option>
            </select>
          </div>

          <div style={{ marginBottom: "10px" }}>
            <label>Direction:</label><br />
            <select value={direction} onChange={(e) => setDirection(e.target.value)} style={{ width: "100%" }}>
              <option value="">Select Direction</option>
              <option value="0">North</option>
              <option value="1">South</option>
              <option value="2">East</option>
              <option value="3">West</option>
              <option value="8">Bidirectional</option>
            </select>
          </div>

          <div style={{ marginBottom: "10px" }}>
            <label>Width:</label><br />
            <input
              type="number"
              value={width}
              onChange={(e) => setWidth(e.target.value)}
              style={{ width: "100%" }}
            />
          </div>

          <div style={{ marginBottom: "10px" }}>
            <label>Color:</label><br />
            <input
              type="color"
              value={color}
              onChange={(e) => setColor(e.target.value)}
              style={{ width: "100%" }}
            />
          </div>

          <div style={{ marginBottom: "10px" }}>
            <label>
              <input
                type="checkbox"
                checked={useLeaflet}
                onChange={(e) => setUseLeaflet(e.target.checked)}
              />
              {" "}Render with Leaflet
            </label>
          </div>

          <button
            onClick={handleCreateTrigger}
            style={{
              backgroundColor: "#007bff",
              color: "#fff",
              padding: "10px 16px",
              border: "none",
              borderRadius: "4px",
              cursor: "pointer"
            }}
          >
            Create Trigger
          </button>
        </div>

        {/* Vertices Table */}
        <div style={{
          flex: "1",
          minWidth: "300px",
          border: "1px solid #ccc",
          borderRadius: "8px",
          padding: "20px"
        }}>
          <h2 style={{ fontSize: "18px", marginBottom: "10px" }}>Edit Trigger Vertices</h2>

          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr>
                <th>#</th>
                <th>X</th>
                <th>Y</th>
                <th>Z</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>1</td>
                <td>123</td>
                <td>456</td>
                <td>789</td>
                <td>
                  <button>Edit</button>
                </td>
              </tr>
            </tbody>
          </table>

          <div style={{ marginTop: "10px" }}>
            <button style={{ marginRight: "10px" }}>Load Vertices</button>
            <button>Save Changes</button>
          </div>
        </div>
      </div>

      {/* Optional Map Placeholder */}
      {useLeaflet && (
        <div style={{ marginTop: "40px", border: "1px solid #ccc", padding: "20px", borderRadius: "8px" }}>
          <h3 style={{ fontSize: "16px" }}>Map Preview</h3>
          <div id="leafletMap" style={{ width: "100%", height: "300px", backgroundColor: "#eee", marginTop: "10px" }}>
            {/* TODO: Leaflet map goes here */}
          </div>
        </div>
      )}
    </div>
  );
};

export default TriggerUX2025;
