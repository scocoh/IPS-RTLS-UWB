//
// # VERSION 250316 /home/parcoadmin/parco_fastapi/app/src/index.js 0P.10B.01
// #
// # ParcoRTLS Middletier Services, ParcoRTLS DLL, ParcoDatabases, ParcoMessaging, and other code
// # Invented by Scott Cohen & Bertrand Dugal.
// # Coded by Jesse Chunn O.B.M.'24 and Michael Farnsworth and Others
// # Published at GitHub https://github.com/scocoh/IPS-RTLS-UWB
// #
// # Licensed under AGPL-3.0: https://www.gnu.org/licenses/agpl-3.0.en.html
import React, { useState } from "react";
import { createRoot } from "react-dom/client";
import TriggerDemo from "./TriggerDemo";
import MapUpload from "./components/MapUpload";
import MapList from "./components/MapList";  // ✅ Import MapList.js
import SupportAccess from "./SupportAccess"; // Import the new module
import ZoneBuilder from "./components/ZoneBuilder";
import ZoneViewer from "./components/ZoneViewer";  // Updated import
import BuildOutTool from "./components/BuildOutTool"; // New import


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
        <button onClick={() => setView("mapList")} style={{ marginRight: "10px", padding: "10px", fontSize: "16px" }}>View Maps</button>
        <button onClick={() => setView("zoneviewer")} style={{ marginRight: "10px", padding: "10px", fontSize: "16px" }}>Zone Viewer & Editor</button>
        <button onClick={() => setView("buildout")} style={{ padding: "10px", fontSize: "16px" }}>Build Out Tool</button>
      </div>

      <hr />

      {/* Conditionally Render Components */}
      {view === "triggers" && <TriggerDemo />}
      {view === "zones" && <ZoneBuilder />}
      {view === "maps" && <MapUpload />}
      {view === "mapList" && <MapList />}
      {view === "zoneviewer" && <ZoneViewer />}
      {view === "buildout" && <BuildOutTool />}
    </div>
  );
};

const container = document.getElementById("root");
const root = createRoot(container);
root.render(
  <>
    <App />
    <SupportAccess />
  </>
);
