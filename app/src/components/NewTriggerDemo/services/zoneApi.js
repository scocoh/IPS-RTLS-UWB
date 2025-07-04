/* Name: zoneApi.js */
/* Version: 0.1.2 */
/* Created: 250625 */
/* Modified: 250704 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin + Claude */
/* Description: API service for zone operations */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/NewTriggerDemo/services */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */
/* Changelog: */
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
  const response = await fetch(`${API_BASE_URL}/zoneviewer/get_vertices_for_campus/${zoneId}`);
  if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
  const data = await response.json();
  
  const vertices = data.vertices.map(vertex => ({
    i_vtx: vertex.vertex_id,
    zone_id: vertex.zone_id,
    n_x: Number(vertex.x).toFixed(6),
    n_y: Number(vertex.y).toFixed(6),
    n_z: Number(vertex.z).toFixed(6),
    n_ord: vertex.order,
  }));
  
  const zValues = vertices.map(v => Number(v.n_z));
  const minZ = Math.min(...zValues);
  const maxZ = Math.max(...zValues);
  
  return {
    vertices,
    minZ,
    maxZ
  };
};

export const zoneApi = {
  // Export the helper functions as methods
  fetchZones,
  fetchZoneVertices,
  
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
      const { vertices, minZ, maxZ } = await fetchZoneVertices(selectedZone.i_zn);
      selectedZone.vertices = vertices;
      selectedZone.minZ = minZ;
      selectedZone.maxZ = maxZ;
    }

    return {
      zones: mappedZones,
      hierarchy,
      selectedZone
    };
  }
};