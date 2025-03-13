///home/parcoadmin/parco_fastapi/app/src/index.js
import React, { useState } from "react";
import { createRoot } from "react-dom/client";
import TriggerDemo from "./TriggerDemo";
import MapUpload from "./components/MapUpload";
import MapList from "./components/MapList";  // ✅ Import MapList.js
import ZoneBuilder from "./components/ZoneBuilder";

const App = () => {
    const [view, setView] = useState("triggers");

    return (
        <div style={{ textAlign: "center", padding: "20px" }}>
            <h1>ParcoRTLS Management</h1>

            {/* Toggle Buttons */}
            <div style={{ marginBottom: "20px" }}>
                <button onClick={() => setView("triggers")} style={{ marginRight: "10px", padding: "10px", fontSize: "16px" }}>Trigger Management</button>
                <button onClick={() => setView("zones")} style={{ marginRight: "10px", padding: "10px", fontSize: "16px" }}>Zone Management</button> 
                <button onClick={() => setView("maps")} style={{ marginRight: "10px", padding: "10px", fontSize: "16px" }}>Map Upload</button>
                <button onClick={() => setView("mapList")} style={{ padding: "10px", fontSize: "16px" }}>View Maps</button>
            </div>

            <hr />

            {/* Conditionally Render Components */}
            {view === "triggers" && <TriggerDemo />}
            {view === "zones" && <ZoneBuilder />}
            {view === "maps" && <MapUpload />}
            {view === "mapList" && <MapList />}
        </div>
    );
};

const container = document.getElementById("root");
const root = createRoot(container);
root.render(<App />);
