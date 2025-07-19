/* Name: zoneApi.js */
/* Version: 0.1.5 */
/* Created: 250625 */
/* Modified: 250718 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin + Claude */
/* Description: API service for zone operations - Added getZoneBoundaries method for boundary visualization */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/NewTriggerDemo/services */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */
/* Changelog: */
/* - 0.1.5 (250718): Added getZoneBoundaries method for zone boundary visualization */
/* - 0.1.4 (250718): Updated to use new /api/get_zone_boundaries endpoint for authoritative Z boundaries */
/* - 0.1.3 (250718): Fixed fetchZoneVertices to use correct /api/get_zone_vertices endpoint */
/* - 0.1.2 (250704): Replaced hardcoded IP with dynamic hostname detection */

// Base URL - dynamic hostname detection
const API_BASE_URL = `http://${window.location.hostname || 'localhost'}:8000`;

// Helper functions defined outside the object
const fetchZones = async () => {
  const response = await fetch(`${API_BASE_URL}/zonebuilder/get_parent_zones_for_trigger_demo`);
  console.log("Raw response status:", response.status);
  console.log("Raw response headers:", [...response.headers.entries()]);
  
  const text = await response.text();
  console.log("Raw response text:", text);
  
  if (!response.ok) throw new Error(`Failed to fetch zones: ${response.status}`);
  
  let data;
  try {
    data = JSON.parse(text);
  } catch (e) {
    throw new Error(`Failed to parse response as JSON: ${e.message}`);
  }
  console.log("Parsed response data:", data);

  let zonesArray;
  if (Array.isArray(data)) {
    zonesArray = data;
  } else if (data && Array.isArray(data.zones)) {
    zonesArray = data.zones;
  } else {
    throw new Error("Invalid zones response from server: Expected an array or object with zones array.");
  }

  return zonesArray;
};

const fetchZoneVertices = async (zoneId) => {
  console.log(`🔍 Fetching vertices and boundaries for zone ${zoneId}`);
  
  // Fetch vertices for display/drawing purposes
  const verticesResponse = await fetch(`${API_BASE_URL}/api/get_zone_vertices/${zoneId}`);
  console.log(`📡 Zone vertices API response status: ${verticesResponse.status}`);
  
  if (!verticesResponse.ok) throw new Error(`HTTP error fetching vertices! Status: ${verticesResponse.status}`);
  const verticesData = await verticesResponse.json();
  console.log(`📊 Zone vertices response data:`, verticesData);
  
  // Process vertices for display/drawing
  const vertices = verticesData.vertices.map((vertex, index) => ({
    i_vtx: vertex.i_vtx || index + 1,
    zone_id: zoneId,
    n_x: Number(vertex.n_x || vertex.x).toFixed(6),
    n_y: Number(vertex.n_y || vertex.y).toFixed(6),
    n_z: Number(vertex.n_z || vertex.z || 0).toFixed(6),
    n_ord: vertex.n_ord || index + 1,
  }));
  
  console.log(`📍 Processed vertices for zone ${zoneId}:`, vertices);
  
  // FIXED: Use new zone boundaries API for authoritative Z Min/Max
  console.log(`🎯 Fetching authoritative boundaries from regions table for zone ${zoneId}`);
  const boundariesResponse = await fetch(`${API_BASE_URL}/api/get_zone_boundaries/${zoneId}`);
  console.log(`📡 Zone boundaries API response status: ${boundariesResponse.status}`);
  
  let minZ = 0;
  let maxZ = 0;
  
  if (boundariesResponse.ok) {
    const boundariesData = await boundariesResponse.json();
    console.log(`📊 Zone boundaries response data:`, boundariesData);
    
    minZ = Number(boundariesData.min_z || 0);
    maxZ = Number(boundariesData.max_z || 0);
    console.log(`✅ Using authoritative boundaries for zone ${zoneId}: min_z=${minZ}, max_z=${maxZ}`);
  } else {
    console.warn(`⚠️ Failed to fetch boundaries for zone ${zoneId}, falling back to vertex calculation`);
    const zValues = vertices.map(v => Number(v.n_z));
    minZ = zValues.length > 0 ? Math.min(...zValues) : 0;
    maxZ = zValues.length > 0 ? Math.max(...zValues) : 0;
    console.log(`📊 Calculated from vertices: min_z=${minZ}, max_z=${maxZ}`);
  }
  
  console.log(`⬆️ Final zone ${zoneId} Z boundaries: min=${minZ}, max=${maxZ}`);
  
  return {
    vertices,
    minZ,
    maxZ
  };
};

// NEW: Helper function to fetch zone boundaries for visualization
const getZoneBoundaries = async (zoneId) => {
  console.log(`📐 Fetching zone boundaries for visualization: zone ${zoneId}`);
  
  const response = await fetch(`${API_BASE_URL}/api/get_zone_boundaries/${zoneId}`);
  console.log(`📡 Zone boundaries API response status: ${response.status}`);
  
  if (!response.ok) {
    throw new Error(`HTTP error fetching zone boundaries! Status: ${response.status}`);
  }
  
  const boundariesData = await response.json();
  console.log(`📊 Zone ${zoneId} boundary data:`, boundariesData);
  
  // Ensure all values are properly typed
  const boundaries = {
    zone_id: parseInt(boundariesData.zone_id),
    min_x: Number(boundariesData.min_x),
    max_x: Number(boundariesData.max_x),
    min_y: Number(boundariesData.min_y),
    max_y: Number(boundariesData.max_y),
    min_z: Number(boundariesData.min_z),
    max_z: Number(boundariesData.max_z)
  };
  
  console.log(`✅ Processed zone ${zoneId} boundaries:`, boundaries);
  return boundaries;
};

export const zoneApi = {
  // Export the helper functions as methods
  fetchZones,
  fetchZoneVertices,
  
  // NEW: Export zone boundaries method for visualization
  getZoneBoundaries,
  
  // Check which zones contain a point
  getZonesByPoint: async (x, y, z) => {
    const res = await fetch(`${API_BASE_URL}/api/zones_by_point?x=${x}&y=${y}&z=${z}`);
    if (!res.ok) throw new Error(`Failed to check zone: ${res.status}`);
    return res.json();
  },

  // Fetch zones with hierarchy (combined operation)
  fetchZonesWithHierarchy: async () => {
    // Now we can use the helper function directly
    const zonesArray = await fetchZones();
    
    const mappedZones = zonesArray.map(zone => ({
      i_zn: parseInt(zone.zone_id),
      x_nm_zn: zone.name,
      i_typ_zn: zone.level,
      i_map: zone.i_map || null,
      parent_zone_id: zone.parent_zone_id ? parseInt(zone.parent_zone_id) : null
    }));

    // Build hierarchy
    const hierarchy = [];
    const zoneMap = new Map(mappedZones.map(zone => [zone.i_zn, { ...zone, children: [] }]));
    
    zoneMap.forEach(zone => {
      if (zone.parent_zone_id && zoneMap.has(zone.parent_zone_id)) {
        zoneMap.get(zone.parent_zone_id).children.push(zone);
      } else {
        hierarchy.push(zone);
      }
    });

    // Sort hierarchy
    hierarchy.sort((a, b) => a.x_nm_zn.localeCompare(b.x_nm_zn));
    
    const customOrder = [1, 10, 2];
    const sortChildren = (children) => {
      children.sort((a, b) => {
        const aIndex = customOrder.indexOf(a.i_typ_zn);
        const bIndex = customOrder.indexOf(b.i_typ_zn);
        if (aIndex !== -1 && bIndex !== -1) return aIndex - bIndex;
        if (aIndex !== -1) return -1;
        if (bIndex !== -1) return 1;
        if (a.i_typ_zn !== b.i_typ_zn) return a.i_typ_zn - b.i_typ_zn;
        return a.x_nm_zn.localeCompare(b.x_nm_zn);
      });
      children.forEach(child => sortChildren(child.children));
    };

    hierarchy.forEach(parent => sortChildren(parent.children));
    console.log("Zone hierarchy:", JSON.stringify(hierarchy, null, 2));

    // Select initial zone (campus zone or first zone)
    const campusZone = hierarchy.find(z => z.i_typ_zn === 1);
    const selectedZone = campusZone || (hierarchy.length > 0 ? hierarchy[0] : null);
    
    if (selectedZone) {
      console.log("Selected initial zone:", selectedZone);
      try {
        const { vertices, minZ, maxZ } = await fetchZoneVertices(selectedZone.i_zn);
        selectedZone.vertices = vertices;
        selectedZone.minZ = minZ;
        selectedZone.maxZ = maxZ;
      } catch (e) {
        console.error(`Failed to fetch vertices for initial zone ${selectedZone.i_zn}:`, e);
        selectedZone.vertices = [];
        selectedZone.minZ = 0;
        selectedZone.maxZ = 0;
      }
    }

    return {
      zones: mappedZones,
      hierarchy,
      selectedZone
    };
  }
};