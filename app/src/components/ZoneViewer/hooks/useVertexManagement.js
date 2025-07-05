/* Name: useVertexManagement.js */
/* Version: 0.1.0 */
/* Created: 250704 */
/* Modified: 250704 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin + Claude */
/* Description: Custom hook for vertex management operations */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/ZoneViewer/hooks */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

import { useCallback } from "react";
import { vertexApi } from "../services/vertexApi";

export const useVertexManagement = ({
  vertices,
  setVertices,
  editedVertices,
  setEditedVertices,
  deletedVertices,
  setDeletedVertices,
  selectedVertices,
  setSelectedVertices,
  targetVertex,
  setTargetVertex,
  checkedZones,
  selectedZone,
  allZones,
  findCampusForZone
}) => {

  // Handle vertex field changes during typing
  const handleVertexChange = useCallback((vertexId, field, value) => {
    // Store the raw input value as a string during typing
    setEditedVertices((prev) => ({
      ...prev,
      [vertexId]: { ...prev[vertexId], [field]: value },
    }));
  }, [setEditedVertices]);

  // Format the value to 6 decimal places on blur
  const handleVertexBlur = useCallback((vertexId, field, value) => {
    const numValue = parseFloat(value) || 0;
    setEditedVertices((prev) => ({
      ...prev,
      [vertexId]: { ...prev[vertexId], [field]: numValue.toFixed(6) },
    }));
  }, [setEditedVertices]);

  // Stage a vertex for deletion (remove from display, add to deletion queue)
  const stageDeleteVertex = useCallback((vertexId) => {
    setDeletedVertices((prev) => [...prev, vertexId]);
    setVertices((prev) => prev.filter((v) => v.vertex_id !== vertexId));
    setEditedVertices((prev) => {
      const newEdits = { ...prev };
      delete newEdits[vertexId];
      return newEdits;
    });
  }, [setDeletedVertices, setVertices, setEditedVertices]);

  // Add a new vertex
  const addVertex = useCallback(async (zoneId, position, refVertexId) => {
    try {
      const zoneVertices = vertices.filter(v => v.zone_id === zoneId).sort((a, b) => a.order - b.order);
      const refVertex = vertices.find(v => v.vertex_id === refVertexId);
      const order = position === "before" 
        ? (refVertex ? refVertex.order - 0.5 : 0) 
        : (refVertex ? refVertex.order + 0.5 : zoneVertices.length + 1);

      const payload = { 
        zone_id: zoneId, 
        x: Number(0.0).toFixed(6), 
        y: Number(0.0).toFixed(6), 
        z: Number(0.0).toFixed(6), 
        order 
      };

      const newVertex = await vertexApi.addVertex(payload);

      const updatedVertices = [...vertices, newVertex].map(v => {
        if (v.zone_id !== zoneId) return v;
        const currentOrder = v.vertex_id === newVertex.vertex_id ? order : v.order;
        return { ...v, order: currentOrder };
      }).sort((a, b) => a.order - b.order).map((v, idx) => ({ ...v, order: idx + 1 }));

      setVertices(updatedVertices);
      console.log("✅ Added vertex:", newVertex);
    } catch (error) {
      console.error("❌ Error adding vertex:", error);
      alert("Failed to add vertex: " + error.message);
    }
  }, [vertices, setVertices]);

  // Save all vertex changes
  const saveVertices = useCallback(async () => {
    try {
      // Delete vertices first
      if (deletedVertices.length > 0) {
        await vertexApi.deleteVertices(deletedVertices);
      }

      // Prepare updates for edited vertices
      const updates = Object.entries(editedVertices)
        .filter(([vertexId]) => vertices.some(v => v && v.vertex_id === parseInt(vertexId)))
        .map(([vertexId, changes]) => {
          const vertex = vertices.find((v) => v && v.vertex_id === parseInt(vertexId));
          if (!vertex) return null;
          return { 
            vertex_id: vertex.vertex_id, 
            x: Number(changes.x ?? vertex.x).toFixed(6), 
            y: Number(changes.y ?? vertex.y).toFixed(6), 
            z: Number(changes.z ?? vertex.z).toFixed(6),
            order: vertex.order
          };
        })
        .filter(update => update !== null);

      // Include unchanged vertices
      const allUpdates = [...updates, ...vertices.filter(v => !editedVertices[v.vertex_id] && !deletedVertices.includes(v.vertex_id)).map(v => ({
        vertex_id: v.vertex_id,
        x: Number(v.x).toFixed(6),
        y: Number(v.y).toFixed(6),
        z: Number(v.z).toFixed(6),
        order: v.order
      }))];

      if (allUpdates.length > 0) {
        await vertexApi.updateVertices(allUpdates);
      }

      // Refresh vertices from server
      const campusZone = findCampusForZone(selectedZone, allZones);
      const refreshedVertices = await vertexApi.fetchVerticesForCampus(campusZone);
      setVertices(refreshedVertices);
      setEditedVertices({});
      setDeletedVertices([]);
      setSelectedVertices(new Set());
      setTargetVertex(null);
      alert("Changes saved successfully!");
    } catch (error) {
      console.error("❌ Error saving changes:", error);
      alert("Failed to save changes: " + error.message);
    }
  }, [deletedVertices, editedVertices, vertices, selectedZone, allZones, findCampusForZone, setVertices, setEditedVertices, setDeletedVertices, setSelectedVertices, setTargetVertex]);

  // Export vertices to JSON
  const exportVertices = useCallback(() => {
    if (!selectedZone) {
      alert("Please select a zone first.");
      return;
    }
    const verticesToExport = vertices.filter(v => checkedZones.includes(v.zone_id));
    if (verticesToExport.length === 0) {
      alert("No vertices to export for the selected zones.");
      return;
    }
    const json = JSON.stringify(verticesToExport, null, 2);
    const blob = new Blob([json], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `vertices_zone_${selectedZone}.json`;
    link.click();
    URL.revokeObjectURL(url);
  }, [selectedZone, vertices, checkedZones]);

  // Import vertices from JSON
  const importVertices = useCallback(async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    try {
      const text = await file.text();
      const importedVertices = JSON.parse(text);
      if (!Array.isArray(importedVertices)) {
        throw new Error("Imported file must contain an array of vertices.");
      }

      const validVertices = importedVertices.filter(v => {
        return (
          typeof v.vertex_id === "number" &&
          typeof v.x === "number" &&
          typeof v.y === "number" &&
          (v.z === null || typeof v.z === "number") &&
          typeof v.order === "number" &&
          typeof v.zone_id === "number" &&
          checkedZones.includes(v.zone_id)
        );
      });

      if (validVertices.length === 0) {
        throw new Error("No valid vertices found in the imported file for the selected zones.");
      }

      const existingVertexIds = new Set(vertices.map(v => v.vertex_id));
      const newVertices = validVertices.filter(v => !existingVertexIds.has(v.vertex_id));
      const updatedVertices = vertices.map(v => {
        const imported = validVertices.find(iv => iv.vertex_id === v.vertex_id);
        return imported ? { ...v, ...imported } : v;
      });

      setVertices([...updatedVertices, ...newVertices].sort((a, b) => a.order - b.order));
      setSelectedVertices(new Set());
      setTargetVertex(null);
      alert(`Imported ${newVertices.length} new vertices and updated ${validVertices.length - newVertices.length} existing vertices.`);
    } catch (error) {
      console.error("❌ Error importing vertices:", error);
      alert("Failed to import vertices: " + error.message);
    }
  }, [vertices, checkedZones, setVertices, setSelectedVertices, setTargetVertex]);

  // Export vertices to SVG
  const exportToSVG = useCallback(() => {
    if (!selectedZone) {
      alert("Please select a zone first.");
      return;
    }
    const verticesToExport = vertices.filter(v => checkedZones.includes(v.zone_id));
    if (verticesToExport.length === 0) {
      alert("No vertices to export for the selected zones.");
      return;
    }

    const width = 1000;
    const height = 800;
    const min_x = Math.min(...verticesToExport.map(v => v.x));
    const min_y = Math.min(...verticesToExport.map(v => v.y));
    const max_x = Math.max(...verticesToExport.map(v => v.x));
    const max_y = Math.max(...verticesToExport.map(v => v.y));

    const scale_x = (max_x - min_x) ? width / (max_x - min_x) : 1;
    const scale_y = (max_y - min_y) ? height / (max_y - min_y) : 1;

    const normalizedVertices = verticesToExport.map(v => ({
      ...v,
      x: (v.x - min_x) * scale_x,
      y: height - (v.y - min_y) * scale_y
    }));

    const regions = {};
    normalizedVertices.forEach(v => {
      if (!regions[v.zone_id]) {
        regions[v.zone_id] = [];
      }
      regions[v.zone_id].push({ x: v.x, y: v.y, vertex_id: v.vertex_id });
    });

    let svgContent = `<svg width="${width}" height="${height}" xmlns="http://www.w3.org/2000/svg">\n`;
    for (const [zone_id, points] of Object.entries(regions)) {
      const zoneVertices = vertices.filter(v => v.zone_id === parseInt(zone_id)).sort((a, b) => a.order - b.order);
      const orderedPoints = zoneVertices.map(v => {
        const normalized = normalizedVertices.find(nv => nv.vertex_id === v.vertex_id);
        return { x: normalized.x, y: normalized.y, vertex_id: v.vertex_id };
      });

      const pointsStr = orderedPoints.map(p => `${p.x},${p.y}`).join(" ");
      svgContent += `<polygon points="${pointsStr}" fill="rgba(173, 216, 230, 0.6)" stroke="black" stroke-width="2"/>\n`;

      const centroid_x = orderedPoints.reduce((sum, p) => sum + p.x, 0) / orderedPoints.length;
      const centroid_y = orderedPoints.reduce((sum, p) => sum + p.y, 0) / orderedPoints.length;
      svgContent += `<text x="${centroid_x}" y="${centroid_y}" font-size="14" fill="black">Zone ${zone_id}</text>\n`;

      orderedPoints.forEach(p => {
        svgContent += `<text x="${p.x + 5}" y="${p.y - 5}" font-size="12" fill="black">${p.vertex_id}</text>\n`;
      });
    }
    svgContent += `</svg>`;

    const blob = new Blob([svgContent], { type: "image/svg+xml" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `map_zone_${selectedZone}.svg`;
    link.click();
    URL.revokeObjectURL(url);
  }, [selectedZone, vertices, checkedZones]);

  // Apply coordinates from target vertex to selected vertices
  const applyCoordinates = useCallback(async () => {
    if (!targetVertex || selectedVertices.size === 0) {
      alert("Please select a target vertex and at least one vertex to update.");
      return;
    }

    try {
      const updates = Array.from(selectedVertices).map(vertexId => {
        const vertex = vertices.find(v => v.vertex_id === vertexId);
        return {
          vertex_id: vertexId,
          x: Number(targetVertex.x).toFixed(6),
          y: Number(targetVertex.y).toFixed(6),
          z: Number(targetVertex.z).toFixed(6),
          order: vertex.order
        };
      });

      await vertexApi.updateVertices(updates);

      const campusZone = findCampusForZone(selectedZone, allZones);
      const refreshedVertices = await vertexApi.fetchVerticesForCampus(campusZone);
      setVertices(refreshedVertices);

      setSelectedVertices(new Set());
      setTargetVertex(null);
      alert("Coordinates applied successfully!");
    } catch (error) {
      console.error("❌ Error applying coordinates:", error);
      alert("Failed to apply coordinates: " + error.message);
    }
  }, [targetVertex, selectedVertices, vertices, selectedZone, allZones, findCampusForZone, setVertices, setSelectedVertices, setTargetVertex]);

  return {
    handleVertexChange,
    handleVertexBlur,
    stageDeleteVertex,
    addVertex,
    saveVertices,
    exportVertices,
    importVertices,
    exportToSVG,
    applyCoordinates
  };
};