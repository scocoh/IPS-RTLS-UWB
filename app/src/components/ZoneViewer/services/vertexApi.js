/* Name: vertexApi.js */
/* Version: 0.1.0 */
/* Created: 250704 */
/* Modified: 250704 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin + Claude */
/* Description: API service for vertex operations */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/ZoneViewer/services */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

// Base URL - uses dynamic hostname detection like the original
const API_BASE_URL = `http://${window.location.hostname || 'localhost'}:8000`;

export const vertexApi = {
  // Fetch vertices for a campus
  fetchVerticesForCampus: async (campusId) => {
    const response = await fetch(`${API_BASE_URL}/zoneviewer/get_vertices_for_campus/${campusId}`);
    if (!response.ok) throw new Error(`Vertices fetch failed: ${response.status}`);
    const data = await response.json();
    return data.vertices || [];
  },

  // Add a new vertex
  addVertex: async (payload) => {
    console.log("Sending payload to add_vertex:", payload);
    const response = await fetch(`${API_BASE_URL}/zoneviewer/add_vertex`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!response.ok) throw new Error(`Failed to add vertex: ${response.status}`);
    const newVertex = await response.json();
    console.log("✅ Added vertex:", newVertex);
    return newVertex;
  },

  // Update multiple vertices
  updateVertices: async (updates) => {
    if (updates.length === 0) return { message: "No updates to process" };
    
    const response = await fetch(`${API_BASE_URL}/zoneviewer/update_vertices`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(updates),
    });
    if (!response.ok) throw new Error(`Failed to save edits: ${response.status}`);
    const result = await response.json();
    console.log("✅ Vertices saved:", result);
    return result;
  },

  // Delete a vertex
  deleteVertex: async (vertexId) => {
    const response = await fetch(`${API_BASE_URL}/zoneviewer/delete_vertex/${vertexId}`, {
      method: "DELETE",
    });
    if (!response.ok) throw new Error(`Failed to delete vertex ${vertexId}: ${response.status}`);
    return { success: true };
  },

  // Batch delete vertices
  deleteVertices: async (vertexIds) => {
    const results = [];
    for (const vertexId of vertexIds) {
      try {
        await vertexApi.deleteVertex(vertexId);
        results.push({ vertexId, success: true });
      } catch (error) {
        results.push({ vertexId, success: false, error: error.message });
      }
    }
    return results;
  }
};
