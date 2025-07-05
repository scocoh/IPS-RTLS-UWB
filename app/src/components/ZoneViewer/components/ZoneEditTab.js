/* Name: ZoneEditTab.js */
/* Version: 0.1.0 */
/* Created: 250704 */
/* Modified: 250704 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin + Claude */
/* Description: Vertex editing tab component for ZoneViewer */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/ZoneViewer/components */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

import React from "react";

const ZoneEditTab = ({
  vertices,
  checkedZones,
  editedVertices,
  selectedVertices,
  targetVertex,
  onVertexChange,
  onVertexBlur,
  onVertexSelect,
  onTargetVertexSelect,
  onAddVertex,
  onStageDeleteVertex,
  onSaveVertices,
  onApplyCoordinates,
  onExportVertices,
  onImportVertices,
  onExportToSVG,
  selectedZone
}) => {

  if (!selectedZone) {
    return (
      <div style={{ padding: "20px", textAlign: "center", color: "#666" }}>
        <h4>No Zone Selected</h4>
        <p>Please select a zone from the Zone Selection tab to edit vertices.</p>
      </div>
    );
  }

  const filteredVertices = vertices.filter((v) => checkedZones.includes(v.zone_id));

  if (filteredVertices.length === 0) {
    return (
      <div style={{ padding: "20px", textAlign: "center", color: "#666" }}>
        <h4>No Vertices Available</h4>
        <p>No vertices found for the selected zones. Make sure zones are checked in the Zone Selection tab.</p>
      </div>
    );
  }

  return (
    <div>
      {/* Action Buttons */}
      <div style={{ marginBottom: "20px", padding: "15px", backgroundColor: "#f8f9fa", borderRadius: "5px" }}>
        <h4>Vertex Operations</h4>
        <div style={{ display: "flex", gap: "10px", flexWrap: "wrap", alignItems: "center" }}>
          <button 
            onClick={onExportVertices} 
            style={{ padding: "8px 16px", backgroundColor: "#007bff", color: "white", border: "none", borderRadius: "4px", cursor: "pointer" }}
          >
            Export JSON
          </button>
          <button 
            onClick={onExportToSVG} 
            style={{ padding: "8px 16px", backgroundColor: "#28a745", color: "white", border: "none", borderRadius: "4px", cursor: "pointer" }}
          >
            Export SVG
          </button>
          <input
            type="file"
            accept=".json"
            onChange={onImportVertices}
            style={{ padding: "8px" }}
          />
          <button 
            onClick={onSaveVertices} 
            style={{ padding: "8px 16px", backgroundColor: "#ffc107", color: "black", border: "none", borderRadius: "4px", cursor: "pointer" }}
          >
            Save All Changes
          </button>
          <button 
            onClick={onApplyCoordinates} 
            style={{ padding: "8px 16px", backgroundColor: "#6f42c1", color: "white", border: "none", borderRadius: "4px", cursor: "pointer" }}
            disabled={!targetVertex || selectedVertices.size === 0}
          >
            Apply Coordinates ({selectedVertices.size} selected)
          </button>
        </div>
      </div>

      {/* Statistics */}
      <div style={{ marginBottom: "15px", padding: "10px", backgroundColor: "#e9ecef", borderRadius: "5px", fontSize: "14px" }}>
        <strong>Vertices:</strong> {filteredVertices.length} total | 
        <strong> Selected:</strong> {selectedVertices.size} | 
        <strong> Target:</strong> {targetVertex ? `Vertex ${targetVertex.vertex_id}` : "None"} |
        <strong> Edited:</strong> {Object.keys(editedVertices).length}
      </div>

      {/* Vertex Table */}
      <div style={{ overflowX: "auto" }}>
        <table style={{ width: "100%", borderCollapse: "collapse", border: "1px solid black", fontSize: "14px" }}>
          <thead>
            <tr style={{ backgroundColor: "#f8f9fa" }}>
              <th style={{ border: "1px solid black", padding: "8px" }}>Select</th>
              <th style={{ border: "1px solid black", padding: "8px" }}>Vertex #</th>
              <th style={{ border: "1px solid black", padding: "8px" }}>Zone ID</th>
              <th style={{ border: "1px solid black", padding: "8px" }}>X</th>
              <th style={{ border: "1px solid black", padding: "8px" }}>Y</th>
              <th style={{ border: "1px solid black", padding: "8px" }}>Z</th>
              <th style={{ border: "1px solid black", padding: "8px" }}>Order</th>
              <th style={{ border: "1px solid black", padding: "8px" }}>Use as Target</th>
              <th style={{ border: "1px solid black", padding: "8px" }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredVertices
              .sort((a, b) => {
                // Sort by zone_id first, then by order
                if (a.zone_id !== b.zone_id) return a.zone_id - b.zone_id;
                return a.order - b.order;
              })
              .map((v) => (
                <tr key={v.vertex_id} style={{ 
                  backgroundColor: selectedVertices.has(v.vertex_id) ? "#e3f2fd" : 
                                   targetVertex && targetVertex.vertex_id === v.vertex_id ? "#fff3cd" : "white"
                }}>
                  <td style={{ border: "1px solid black", padding: "8px", textAlign: "center" }}>
                    <input
                      type="checkbox"
                      checked={selectedVertices.has(v.vertex_id)}
                      onChange={() => onVertexSelect(v.vertex_id)}
                    />
                  </td>
                  <td style={{ border: "1px solid black", padding: "8px", textAlign: "center" }}>
                    <strong>{v.vertex_id}</strong>
                  </td>
                  <td style={{ border: "1px solid black", padding: "8px", textAlign: "center" }}>
                    {v.zone_id}
                  </td>
                  <td style={{ border: "1px solid black", padding: "8px" }}>
                    <input
                      type="text"
                      value={editedVertices[v.vertex_id]?.x ?? Number(v.x).toFixed(6)}
                      onChange={(e) => onVertexChange(v.vertex_id, "x", e.target.value)}
                      onBlur={(e) => onVertexBlur(v.vertex_id, "x", e.target.value)}
                      style={{ 
                        width: "100px", 
                        padding: "4px",
                        backgroundColor: editedVertices[v.vertex_id]?.x !== undefined ? "#fff2cc" : "white"
                      }}
                    />
                  </td>
                  <td style={{ border: "1px solid black", padding: "8px" }}>
                    <input
                      type="text"
                      value={editedVertices[v.vertex_id]?.y ?? Number(v.y).toFixed(6)}
                      onChange={(e) => onVertexChange(v.vertex_id, "y", e.target.value)}
                      onBlur={(e) => onVertexBlur(v.vertex_id, "y", e.target.value)}
                      style={{ 
                        width: "100px", 
                        padding: "4px",
                        backgroundColor: editedVertices[v.vertex_id]?.y !== undefined ? "#fff2cc" : "white"
                      }}
                    />
                  </td>
                  <td style={{ border: "1px solid black", padding: "8px" }}>
                    <input
                      type="text"
                      value={editedVertices[v.vertex_id]?.z ?? Number(v.z).toFixed(6)}
                      onChange={(e) => onVertexChange(v.vertex_id, "z", e.target.value)}
                      onBlur={(e) => onVertexBlur(v.vertex_id, "z", e.target.value)}
                      style={{ 
                        width: "100px", 
                        padding: "4px",
                        backgroundColor: editedVertices[v.vertex_id]?.z !== undefined ? "#fff2cc" : "white"
                      }}
                    />
                  </td>
                  <td style={{ border: "1px solid black", padding: "8px", textAlign: "center" }}>
                    {v.order}
                  </td>
                  <td style={{ border: "1px solid black", padding: "8px", textAlign: "center" }}>
                    <input
                      type="checkbox"
                      checked={targetVertex && targetVertex.vertex_id === v.vertex_id}
                      onChange={() => onTargetVertexSelect(v)}
                    />
                  </td>
                  <td style={{ border: "1px solid black", padding: "8px" }}>
                    <div style={{ display: "flex", gap: "4px", flexWrap: "wrap" }}>
                      <button 
                        onClick={() => onAddVertex(v.zone_id, "before", v.vertex_id)}
                        style={{ padding: "4px 8px", fontSize: "12px", backgroundColor: "#28a745", color: "white", border: "none", borderRadius: "3px", cursor: "pointer" }}
                      >
                        + Before
                      </button>
                      <button 
                        onClick={() => onAddVertex(v.zone_id, "after", v.vertex_id)}
                        style={{ padding: "4px 8px", fontSize: "12px", backgroundColor: "#007bff", color: "white", border: "none", borderRadius: "3px", cursor: "pointer" }}
                      >
                        + After
                      </button>
                      <button 
                        onClick={() => onStageDeleteVertex(v.vertex_id)}
                        style={{ padding: "4px 8px", fontSize: "12px", backgroundColor: "#dc3545", color: "white", border: "none", borderRadius: "3px", cursor: "pointer" }}
                      >
                        Delete
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
          </tbody>
        </table>
      </div>

      {/* Help Text */}
      <div style={{ marginTop: "15px", padding: "10px", backgroundColor: "#f8f9fa", borderRadius: "5px", fontSize: "12px", color: "#666" }}>
        <strong>Instructions:</strong> 
        • Select vertices to apply coordinates in bulk 
        • Set one vertex as target to copy its coordinates to selected vertices 
        • Edited values are highlighted in yellow 
        • Use + Before/After to add vertices adjacent to existing ones 
        • Remember to Save All Changes when finished
      </div>
    </div>
  );
};

export default ZoneEditTab;