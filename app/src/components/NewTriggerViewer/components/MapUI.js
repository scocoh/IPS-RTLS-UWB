/* Name: MapUI.js */
/* Version: 0.1.0 */
/* Created: 971201 */
/* Modified: 250502 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin */
/* Description: ParcoRTLS frontend script */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/NewTriggerViewer/components */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

// components/MapUI.js  • ParcoRTLS v0.1.8
// -----------------------------------------------------------------------------
// Legend & TagControls overlay components. Separated for clarity so NewTrigger
// Viewer stays lean. These components are **presentational only**.
// -----------------------------------------------------------------------------
import React from "react";

export const Legend = ({ isConnected, mapMode }) => (
  <div style={{ position: "absolute", top: 10, right: 10, background: "rgba(255,255,255,0.9)", padding: 10, borderRadius: 5, border: "1px solid #ccc", fontSize: 12, zIndex: 1000, minWidth: 150 }}>
    <h4 style={{ margin: 0, marginBottom: 8, fontSize: 14 }}>Legend</h4>
    <Row color="red" label="Active Tag" />
    <Row color="gray" label="Stale Tag" style={{ opacity: 0.7 }} />
    <Row color="red" label="Disconnected" style={{ opacity: 0.5 }} />
    <Row color="blue" label="Zone Trigger" shape="rect" />
    <Row color="purple" label="Portable Trigger" shape="circle-outline" />
    <div style={{ display: "flex", alignItems: "center", marginTop: 8 }}>
      <span style={{ color: isConnected ? "green" : "red" }}>●</span>
      <span style={{ marginLeft: 4 }}>{isConnected ? "Connected" : "Disconnected"}</span>
      {mapMode !== "view" && <span style={{ marginLeft: 8, fontSize: 10, color: "#666" }}>Mode: {mapMode}</span>}
    </div>
  </div>
);

const Row = ({ color, label, shape = "circle", style = {} }) => {
  const base = {
    width: 10,
    height: shape === "rect" ? 2 : 10,
    background: color,
    borderRadius: shape === "circle" ? "50%" : 0,
    border: shape === "circle-outline" ? `2px solid ${color}` : undefined,
    marginRight: 8,
    ...style,
  };
  return (
    <div style={{ display: "flex", alignItems: "center", marginBottom: 4 }}>
      <div style={base} /> {label}
    </div>
  );
};

export const TagControls = ({ activeTags = [], hiddenTags, onToggleTag, onToggleAll, showHotkeyHint = true }) => (
  <div style={{ position: "absolute", bottom: 50, right: 10, background: "rgba(255,255,255,0.9)", padding: 10, borderRadius: 5, border: "1px solid #ccc", fontSize: 12, zIndex: 1000, maxHeight: 200, overflowY: "auto", minWidth: 120 }}>
    <h4 style={{ margin: 0, marginBottom: 8, fontSize: 14 }}>Tag Visibility</h4>
    {activeTags.length ? activeTags.map((t) => (
      <div key={t} style={{ display: "flex", alignItems: "center", marginBottom: 4 }}>
        <input type="checkbox" id={`tag-${t}`} checked={!hiddenTags.has(t)} onChange={() => onToggleTag(t)} style={{ marginRight: 6 }} />
        <label htmlFor={`tag-${t}`}>{t}</label>
      </div>
    )) : <div style={{ color: "#666", fontStyle: "italic" }}>No active tags</div>}
    {showHotkeyHint && activeTags.length > 0 && (
      <div style={{ marginTop: 8, fontSize: 10, color: "#999", borderTop: "1px solid #ddd", paddingTop: 4 }}>
        💡 Press V to toggle all tags, ? for shortcuts
      </div>
    )}
  </div>
);
