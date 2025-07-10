/* Name: index.js */
/* Version: 0.1.4 */
/* Created: 971201 */
/* Modified: 250704 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin */
/* Description: JavaScript file for ParcoRTLS frontend */
/* Location: /home/parcoadmin/parco_fastapi/app/src */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

//
// # VERSION 250704 /home/parcoadmin/parco_fastapi/app/src/index.js 0.1.4
// # CHANGED: Added ZoneViewerModular import and button for testing modular version alongside original
// # CHANGED: Bumped version from 0.1.3 to 0.1.4
// # Previous: Added BuildOutMapCal import and button for map calibration testing, bumped from 0.1.2
// # Previous: Added RuleBuilder view for TETSE rule construction and code generation, bumped from 0.1.1
// # Previous: Added Portable Trigger Add button and view, bumped from 0.1.0
// # Previous: Added EntityMergeDemo button and view, bumped to 0.0.2
// # Index for the New Trigger Demo
// #
// # Copyright (C) 1999 - 2025 Affiliated Commercial Services Inc.
// # ParcoRTLS Middletier Services, ParcoRTLS DLL, ParcoDatabases, ParcoMessaging, and other code
// # Invented by Scott Cohen & Bertrand Dugal.
// # Coded by Jesse Chunn O.B.M.'24 and Michael Farnsworth and Others
// # Published at GitHub https://github.com/scocoh/IPS-RTLS-UWB
//
// # Licensed under AGPL-3.0: https://www.gnu.org/licenses/agpl-3.0.en.html
import 'bootstrap/dist/css/bootstrap.min.css';
import React, { useState } from "react";
import { createRoot } from "react-dom/client";
import TriggerDemo from "./TriggerDemo";
import MapUpload from "./components/MapUpload";
import MapList from "./components/MapList";
import SupportAccess from "./SupportAccess";
import TriggerUX2025 from "./components/TriggerUX2025";
import ZoneBuilder from "./components/ZoneBuilder";
import ZoneViewer from "./components/ZoneViewer";
import ZoneViewerModular from "./components/ZoneViewer/ZV_index";
import BuildOutTool from "./components/BuildOutTool";
import BuildOutMapCal from "./components/BuildOutMapCal";
import NewTriggerDemo from "./components/NewTriggerDemo/NTD_index";
import EntityMergeDemo from "./components/EntityMergeDemo";
import PortableTriggerAdd from "./components/PortableTriggerAdd";
import RuleBuilder from "./components/RuleBuilder";
import SimulatorDemo from "./components/SimulatorDemo/sim_index";

const App = () => {
  const [view, setView] = useState("triggers");

  return (
    <div style={{ textAlign: "center", padding: "20px" }}>
      <h1>ParcoRTLS Management 0.1.4</h1>

      <div style={{ marginBottom: "20px" }}>
        <button onClick={() => setView("triggers")} style={{ marginRight: "10px", padding: "10px", fontSize: "16px" }}>Trigger Management</button>
        <button onClick={() => setView("zones")} style={{ marginRight: "10px", padding: "10px", fontSize: "16px" }}>Zone Management</button>
        <button onClick={() => setView("maps")} style={{ marginRight: "10px", padding: "10px", fontSize: "16px" }}>Map Upload</button>
        <button onClick={() => setView("mapList")} style={{ marginRight: "10px", padding: "10px", fontSize: "16px" }}>View Maps</button>
        <button onClick={() => setView("zoneviewer")} style={{ marginRight: "10px", padding: "10px", fontSize: "16px" }}>Zone Viewer & Editor</button>
        <button onClick={() => setView("zoneviewermodular")} style={{ marginRight: "10px", padding: "10px", fontSize: "16px", backgroundColor: "#007bff", color: "white" }}>Zone Viewer (Modular)</button>
        <button onClick={() => setView("buildout")} style={{ marginRight: "10px", padding: "10px", fontSize: "16px" }}>Build Out Tool</button>
        <button onClick={() => setView("buildoutcal")} style={{ marginRight: "10px", padding: "10px", fontSize: "16px" }}>Map Calibration</button>
        <button onClick={() => setView("newTriggerDemo")} style={{ marginRight: "10px", padding: "10px", fontSize: "16px" }}>Alpha New Trigger Demo</button>
        <button onClick={() => setView("simulatorDemo")} style={{ marginRight: "10px", padding: "10px", fontSize: "16px" }}>Simulator Demo</button>
        <button onClick={() => setView("entityMergeDemo")} style={{ marginRight: "10px", padding: "10px", fontSize: "16px" }}>Entity Merge Demo</button>
        <button onClick={() => setView("portableTriggerAdd")} style={{ marginRight: "10px", padding: "10px", fontSize: "16px" }}>Portable Trigger Add</button>
        <button onClick={() => setView("ruleBuilder")} style={{ padding: "10px", fontSize: "16px" }}>Rule Builder</button>
      </div>

      <hr />

      {view === "trigger2025" && <TriggerUX2025 />}
      {view === "triggers" && <TriggerDemo />}
      {view === "zones" && <ZoneBuilder />}
      {view === "maps" && <MapUpload />}
      {view === "mapList" && <MapList />}
      {view === "zoneviewer" && <ZoneViewer />}
      {view === "zoneviewermodular" && <ZoneViewerModular />}
      {view === "buildout" && <BuildOutTool />}
      {view === "buildoutcal" && <BuildOutMapCal />}
      {view === "newTriggerDemo" && <NewTriggerDemo />}
      {view === "simulatorDemo" && <SimulatorDemo />}
      {view === "entityMergeDemo" && <EntityMergeDemo />}
      {view === "portableTriggerAdd" && <PortableTriggerAdd />}
      {view === "ruleBuilder" && <RuleBuilder />}
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