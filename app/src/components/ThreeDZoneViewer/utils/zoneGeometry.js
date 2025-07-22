/* Name: zoneGeometry.js */
/* Version: 0.1.2 */
/* Created: 250719 */
/* Modified: 250722 */
/* Creator: ParcoAdmin + Claude */
/* Modified By: ParcoAdmin + Claude */
/* Description: ZONE BOUNDARY FILTER - Filters API response to show only zone boundary, not trigger regions */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/ThreeDZoneViewer/utils */
/* Role: Frontend Utility */
/* Status: Active */
/* Dependent: TRUE */
/* Changelog: */
/* - 0.1.2: ZONE BOUNDARY FILTER - Added dynamic filtering to extract only zone boundary region from API response */
/* - 0.1.1: ENHANCED VERTEX PROCESSING - Added polygon validation, better debugging, order gap detection */
/* - 0.1.0: Initial zone geometry utilities */

import * as THREE from 'three';
import { parcoToThreeJs } from './mapCoordinateSystem';

// Function to fetch real zone vertices from API
export const fetchZoneVertices = async (zoneId, config) => {
  try {
    const response = await fetch(`${config.API_URL}/maps/get_zone_vertices_3d/${zoneId}`);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    const data = await response.json();
    console.log(`📊 Fetched zone ${zoneId} data:`, data);
    return data;
  } catch (error) {
    console.error(`❌ Error fetching zone ${zoneId} vertices:`, error);
    return null;
  }
};

// NEW v0.1.2: Function to extract zone boundary vertices from API response
export const extractZoneBoundaryVertices = (zoneData) => {
  if (!zoneData || !zoneData.regions || zoneData.regions.length === 0) {
    console.warn('⚠️ No regions data available in API response');
    return [];
  }

  console.log(`🔍 v0.1.2: Extracting zone boundary for: ${zoneData.zone_name} (ID: ${zoneData.zone_id})`);
  console.log(`📊 API returned ${zoneData.regions.length} regions, ${zoneData.total_vertices} total vertices`);

  // Strategy 1: Find region that matches zone name exactly (zone boundary)
  let zoneBoundaryRegion = zoneData.regions.find(region => 
    region.region_name === zoneData.zone_name
  );

  if (zoneBoundaryRegion) {
    console.log(`✅ Found zone boundary region by name match: "${zoneBoundaryRegion.region_name}" (ID: ${zoneBoundaryRegion.region_id})`);
    console.log(`📐 Zone boundary has ${zoneBoundaryRegion.vertex_count} vertices`);
    return zoneBoundaryRegion.vertices;
  }

  // Strategy 2: Find region that doesn't contain "Trigger" in the name
  zoneBoundaryRegion = zoneData.regions.find(region => 
    !region.region_name.toLowerCase().includes('trigger')
  );

  if (zoneBoundaryRegion) {
    console.log(`✅ Found zone boundary region by non-trigger filter: "${zoneBoundaryRegion.region_name}" (ID: ${zoneBoundaryRegion.region_id})`);
    console.log(`📐 Zone boundary has ${zoneBoundaryRegion.vertex_count} vertices`);
    return zoneBoundaryRegion.vertices;
  }

  // Strategy 3: Use the region with the most vertices (likely the zone boundary)
  zoneBoundaryRegion = zoneData.regions.reduce((prev, current) => 
    (prev.vertex_count > current.vertex_count) ? prev : current
  );

  if (zoneBoundaryRegion) {
    console.log(`✅ Found zone boundary region by largest vertex count: "${zoneBoundaryRegion.region_name}" (ID: ${zoneBoundaryRegion.region_id})`);
    console.log(`📐 Zone boundary has ${zoneBoundaryRegion.vertex_count} vertices`);
    return zoneBoundaryRegion.vertices;
  }

  // Fallback: Use all_vertices from API response (old behavior)
  console.warn(`⚠️ Could not identify zone boundary region, falling back to all_vertices`);
  console.warn(`⚠️ This may include trigger vertices - wireframe may show triangulation artifacts`);
  return zoneData.all_vertices || [];
};

// ENHANCED v0.1.2: Function to extract unique vertices and sort by order with zone boundary filtering
export const processZoneVertices = (zoneData) => {
  if (!zoneData) {
    console.warn('⚠️ No vertex data available');
    return [];
  }

  console.log(`🔍 v0.1.2: Processing vertices for zone: ${zoneData.zone_name} (ID: ${zoneData.zone_id})`);

  // NEW v0.1.2: Extract only zone boundary vertices from API response
  const zoneBoundaryVertices = extractZoneBoundaryVertices(zoneData);
  
  if (zoneBoundaryVertices.length === 0) {
    console.warn('⚠️ No zone boundary vertices found');
    return [];
  }

  console.log(`📊 Zone boundary vertex count: ${zoneBoundaryVertices.length}`);

  // Create a map to deduplicate vertices by vertex_id
  const uniqueVertices = new Map();
  zoneBoundaryVertices.forEach(vertex => {
    if (!uniqueVertices.has(vertex.vertex_id)) {
      uniqueVertices.set(vertex.vertex_id, vertex);
    }
  });

  console.log(`🔢 Unique vertices after deduplication: ${uniqueVertices.size}`);

  // Convert to array and sort by order field
  const sortedVertices = Array.from(uniqueVertices.values())
    .sort((a, b) => a.order - b.order);

  console.log(`📋 Zone boundary vertices sorted by order:`);
  sortedVertices.forEach((v, i) => {
    console.log(`  ${i+1}. Order ${v.order}: (${v.x.toFixed(2)}, ${v.y.toFixed(2)}, ${v.z}) - vertex_id ${v.vertex_id}`);
  });

  // ENHANCED: Check for order gaps and potential issues
  if (sortedVertices.length > 1) {
    const orderValues = sortedVertices.map(v => v.order);
    const minOrder = Math.min(...orderValues);
    const maxOrder = Math.max(...orderValues);
    const orderRange = maxOrder - minOrder;
    const expectedConsecutive = sortedVertices.length - 1;
    
    console.log(`🔍 Order Analysis:`);
    console.log(`  Min Order: ${minOrder}, Max Order: ${maxOrder}`);
    console.log(`  Order Range: ${orderRange}, Expected Range: ${expectedConsecutive}`);
    
    if (orderRange > expectedConsecutive * 2) {
      console.warn(`⚠️ Large gaps in vertex order detected - this may indicate non-consecutive ordering`);
      console.warn(`⚠️ Order values: [${orderValues.join(', ')}]`);
    }
    
    // Check for duplicate orders
    const duplicateOrders = orderValues.filter((order, index) => orderValues.indexOf(order) !== index);
    if (duplicateOrders.length > 0) {
      console.warn(`⚠️ Duplicate order values detected: [${duplicateOrders.join(', ')}]`);
    }
  }

  // ENHANCED: Validate polygon closure
  if (sortedVertices.length >= 3) {
    const firstVertex = sortedVertices[0];
    const lastVertex = sortedVertices[sortedVertices.length - 1];
    const distanceToClose = Math.sqrt(
      Math.pow(lastVertex.x - firstVertex.x, 2) + 
      Math.pow(lastVertex.y - firstVertex.y, 2)
    );
    
    console.log(`🔗 Polygon Analysis:`);
    console.log(`  First vertex: (${firstVertex.x.toFixed(2)}, ${firstVertex.y.toFixed(2)})`);
    console.log(`  Last vertex: (${lastVertex.x.toFixed(2)}, ${lastVertex.y.toFixed(2)})`);
    console.log(`  Distance to close: ${distanceToClose.toFixed(2)} units`);
    
    if (distanceToClose > 5) {
      console.warn(`⚠️ Large gap between first and last vertex - polygon may not close properly`);
    } else if (distanceToClose < 0.1) {
      console.log(`✅ Polygon properly closes - first and last vertices match`);
    }
  }

  // ENHANCED: Calculate polygon area to detect issues
  if (sortedVertices.length >= 3) {
    let area = 0;
    for (let i = 0; i < sortedVertices.length; i++) {
      const j = (i + 1) % sortedVertices.length;
      area += sortedVertices[i].x * sortedVertices[j].y;
      area -= sortedVertices[j].x * sortedVertices[i].y;
    }
    area = Math.abs(area) / 2;
    
    console.log(`📐 Polygon area: ${area.toFixed(2)} square units`);
    
    if (area < 1) {
      console.warn(`⚠️ Very small polygon area detected - vertices may be too close together`);
    }
  }

  console.log(`✅ v0.1.2: Processed ${sortedVertices.length} zone boundary vertices for zone ${zoneData.zone_name}`);
  console.log(`🚫 Filtered out trigger regions - should eliminate triangulation artifacts`);
  return sortedVertices;
};

// Function to create 3D zone geometry from vertices - FIXED FLAT PROJECTION
export const createZoneGeometry = (vertices, mapBounds, height = 30) => {
  if (vertices.length < 3) {
    console.warn('⚠️ Need at least 3 vertices to create zone geometry');
    return null;
  }

  console.log(`🏗️ Creating zone geometry with ${vertices.length} vertices, height: ${height} feet`);

  // Convert vertices to Three.js coordinates for shape creation
  const threeVertices = vertices.map(vertex => {
    const threeCoords = parcoToThreeJs(vertex.x, vertex.y, vertex.z, mapBounds);
    console.log(`📍 Vertex ${vertex.vertex_id}: Parco(${vertex.x}, ${vertex.y}, ${vertex.z}) → Three(${threeCoords.x.toFixed(1)}, ${threeCoords.y.toFixed(1)}, ${threeCoords.z.toFixed(1)})`);
    return threeCoords;
  });

  // Create a simple flat polygon on the ground plane (Y=0)
  const shape = new THREE.Shape();
  
  // Log shape creation for debugging
  console.log(`📐 Creating shape with vertices:`);
  threeVertices.forEach((v, i) => {
    console.log(`  ${i}: moveTo/lineTo(${v.x.toFixed(1)}, ${v.z.toFixed(1)})`);
  });
  
  // Start at first vertex - use Three.js X,Z coordinates for horizontal plane
  shape.moveTo(threeVertices[0].x, threeVertices[0].z);
  
  // Add lines to remaining vertices
  for (let i = 1; i < threeVertices.length; i++) {
    shape.lineTo(threeVertices[i].x, threeVertices[i].z);
  }
  
  // Close the shape - return to first vertex (this should be automatic, but let's be explicit)
  // shape.lineTo(threeVertices[0].x, threeVertices[0].z);

  // Create a simple flat geometry at ground level (Y=0)
  const geometry = new THREE.ShapeGeometry(shape);
  
  // The ShapeGeometry is created in XY plane, we want it in XZ plane
  // Rotate 90 degrees around X axis to make it horizontal
  geometry.rotateX(-Math.PI / 2);
  
  // Keep it at Y=0 (ground level) - no translation needed
  
  console.log(`✅ Created FLAT zone geometry: ${vertices.length} vertices (for alignment testing)`);
  console.log(`📊 First vertex shape coords: (${threeVertices[0].x}, ${threeVertices[0].z})`);
  console.log(`📊 Last vertex shape coords: (${threeVertices[threeVertices.length-1].x}, ${threeVertices[threeVertices.length-1].z})`);
  return geometry;
};

// Function to create zone mesh with proper material
export const createZoneMesh = (geometry, zoneData) => {
  // Create zone material - green wireframe for campus boundary
  const zoneMaterial = new THREE.MeshBasicMaterial({
    color: 0x00ff00, // Green
    wireframe: true,
    transparent: true,
    opacity: 0.9
  });

  // Create zone mesh
  const zoneMesh = new THREE.Mesh(geometry, zoneMaterial);
  
  // Position at origin since geometry already has correct coordinates
  zoneMesh.position.set(0, 0, 0);
  
  // Set user data
  zoneMesh.userData.isRealZone = true;
  zoneMesh.userData.zoneId = zoneData.zone_id;
  zoneMesh.userData.zoneName = zoneData.zone_name;

  console.log(`✅ Created zone mesh: ${zoneData.zone_name} (ID: ${zoneData.zone_id})`);
  return zoneMesh;
};

// ENHANCED: Function to create vertex markers with order labels
export const createVertexMarkers = (vertices, mapBounds, scene) => {
  const markers = [];
  
  vertices.forEach((vertex, index) => {
    const threeCoords = parcoToThreeJs(vertex.x, vertex.y, vertex.z, mapBounds);
    
    // Create sphere at vertex position - ENHANCED: Different colors for first/last vertices
    const sphereGeometry = new THREE.SphereGeometry(2, 8, 8);
    let sphereColor = 0x00ff00; // Default green
    
    if (index === 0) {
      sphereColor = 0xff0000; // Red for first vertex
    } else if (index === vertices.length - 1) {
      sphereColor = 0x0000ff; // Blue for last vertex
    }
    
    const sphereMaterial = new THREE.MeshBasicMaterial({ color: sphereColor });
    const sphere = new THREE.Mesh(sphereGeometry, sphereMaterial);
    sphere.position.set(threeCoords.x, threeCoords.y, threeCoords.z);
    sphere.userData.isRealZone = true;
    sphere.userData.vertexOrder = vertex.order;
    sphere.userData.vertexIndex = index;
    
    markers.push(sphere);
    scene.add(sphere);

    console.log(`📍 Vertex ${index + 1}: Order ${vertex.order}, Parco(${vertex.x}, ${vertex.y}, ${vertex.z}) → Three(${threeCoords.x.toFixed(1)}, ${threeCoords.y.toFixed(1)}, ${threeCoords.z.toFixed(1)}) [Color: ${sphereColor === 0xff0000 ? 'RED-FIRST' : sphereColor === 0x0000ff ? 'BLUE-LAST' : 'GREEN'}]`);
  });

  console.log(`✅ Added ${vertices.length} vertex markers (RED=first, BLUE=last, GREEN=middle)`);
  return markers;
};