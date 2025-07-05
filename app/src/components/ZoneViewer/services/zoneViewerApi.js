/* Name: zoneViewerApi.js */
/* Version: 0.1.0 */
/* Created: 250704 */
/* Modified: 250704 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin + Claude */
/* Description: API service for zone viewer operations */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/ZoneViewer/services */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

// Base URL - uses dynamic hostname detection like the original
const API_BASE_URL = `http://${window.location.hostname || 'localhost'}:8000`;

export const zoneViewerApi = {
  // Fetch zone types from zonebuilder
  fetchZoneTypes: async () => {
    const response = await fetch(`${API_BASE_URL}/zonebuilder/get_zone_types`);
    if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
    const data = await response.json();
    return data;
  },

  // Fetch all zones with maps (for dropdown selection)
  fetchZonesWithMaps: async () => {
    const response = await fetch(`${API_BASE_URL}/api/zones_with_maps`);
    if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
    const data = await response.json();
    return Array.isArray(data) ? data : data.zones || [];
  },

  // Fetch hierarchical zones for a campus
  fetchZonesForCampus: async (campusId) => {
    const response = await fetch(`${API_BASE_URL}/zoneviewer/get_all_zones_for_campus/${campusId}`);
    if (!response.ok) throw new Error(`Zones fetch failed: ${response.status}`);
    const data = await response.json();
    return data.zones || [];
  },

  // Delete zone recursively
  deleteZoneRecursive: async (zoneId) => {
    const response = await fetch(`${API_BASE_URL}/zoneviewer/delete_zone_recursive/${zoneId}`, {
      method: "DELETE",
    });
    if (!response.ok) throw new Error(`Failed to delete zone: ${response.status}`);
    const result = await response.json();
    console.log("✅ Zone deleted:", result);
    return result;
  },

  // Fetch campus zones (if needed for backward compatibility)
  fetchCampusZones: async () => {
    const response = await fetch(`${API_BASE_URL}/zoneviewer/get_campus_zones`);
    if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
    const data = await response.json();
    return data.campuses || [];
  }
};