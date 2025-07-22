/* Name: zoneShapeGeometry.js */
/* Version: 0.1.12 */
/* Created: 250720 */
/* Modified: 250721 */
/* Creator: ParcoAdmin + Claude */
/* Modified By: ParcoAdmin + Claude */
/* Changelog: */
/* - 0.1.12: OPTIONAL CORNER SPHERES - Added showCornerMarkers parameter to control sphere visibility */
/* - 0.1.11: OPTIONAL LABELS - Added showLabels parameter to control text label visibility */
/* - 0.1.10: WIREFRAME-ONLY SOLUTION - 100% reliable visibility using wireframe + filled outline approach */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/ThreeDZoneViewer/utils */

import * as THREE from 'three';
import { parcoToThreeJs } from './mapCoordinateSystem';

/**
 * Create extruded zone geometry - SAME AS v0.1.11 (working perfectly)
 */
export const createExtrudedZoneGeometry = (vertices, mapBounds, defaultHeight = 10) => {
  if (vertices.length < 3) {
    console.warn('⚠️ Need at least 3 vertices to create extruded zone geometry');
    return null;
  }

  console.log(`🏗️ v0.1.12: Creating geometry for configurable wireframe rendering`);

  // Same proven vertex processing
  const coordinateMap = new Map();
  const cleanVertices = [];
  
  vertices.forEach((vertex, index) => {
    const coordKey = `${vertex.x.toFixed(6)}_${vertex.y.toFixed(6)}`;
    if (!coordinateMap.has(coordKey)) {
      coordinateMap.set(coordKey, vertex);
      cleanVertices.push(vertex);
    }
  });

  let sortedVertices;
  const orderValues = cleanVertices.map(v => v.order);
  const hasLargeGaps = orderValues.length > 1 && (Math.max(...orderValues) - Math.min(...orderValues)) > (orderValues.length * 2);
  
  if (hasLargeGaps) {
    sortedVertices = cleanVertices
      .sort((a, b) => a.vertex_id - b.vertex_id)
      .map((vertex, index) => ({ ...vertex, order: index + 1 }));
  } else {
    sortedVertices = cleanVertices
      .sort((a, b) => a.order - b.order)
      .map((vertex, index) => ({ ...vertex, order: index + 1 }));
  }

  const zValues = sortedVertices.map(v => v.z);
  const validZValues = zValues.filter(z => z !== null && z !== undefined);
  const maxDatabaseZ = validZValues.length > 0 ? Math.max(...validZValues) : null;
  const effectiveHeight = maxDatabaseZ !== null ? maxDatabaseZ : (defaultHeight + mapBounds.minZ);

  const threeVertices = sortedVertices.map((vertex, index) => {
    return parcoToThreeJs(vertex.x, vertex.y, vertex.z, mapBounds);
  });

  // Winding order fix
  let signedArea = 0;
  for (let i = 0; i < threeVertices.length; i++) {
    const j = (i + 1) % threeVertices.length;
    signedArea += (threeVertices[j].x - threeVertices[i].x) * (threeVertices[j].z + threeVertices[i].z);
  }
  
  const isClockwise = signedArea > 0;
  const orderedVertices = isClockwise ? [...threeVertices].reverse() : threeVertices;

  const shape = new THREE.Shape();
  const firstVertex = orderedVertices[0];
  shape.moveTo(firstVertex.x, -firstVertex.z);
  
  for (let i = 1; i < orderedVertices.length; i++) {
    const vertex = orderedVertices[i];
    shape.lineTo(vertex.x, -vertex.z);
  }

  const extrudeSettings = {
    depth: effectiveHeight,
    bevelEnabled: false,
    steps: 1,
    curveSegments: 16
  };

  const geometry = new THREE.ExtrudeGeometry(shape, extrudeSettings);
  geometry.computeVertexNormals();
  geometry.rotateX(-Math.PI / 2);
  geometry.computeVertexNormals();

  console.log(`✅ v0.1.12: Created geometry for fully configurable wireframe rendering`);
  return geometry;
};

/**
 * v0.1.12: WIREFRAME-ONLY with OPTIONAL LABELS AND CORNER SPHERES
 * 
 * @param {THREE.ExtrudeGeometry} geometry - 3D extruded geometry
 * @param {Object} zoneData - Zone metadata
 * @param {string} color - Hex color for material
 * @param {number} opacity - Transparency level (affects line opacity)
 * @param {boolean} showLabels - Whether to show text labels (default: false)
 * @param {boolean} showCornerMarkers - Whether to show corner spheres (default: true)
 * @returns {THREE.Group} - Group with configurable wireframe layers
 */
export const createExtrudedZoneMesh = (geometry, zoneData, color = 0x00ff00, opacity = 0.6, showLabels = false, showCornerMarkers = true) => {
  if (!geometry) {
    console.error('❌ No geometry provided to createExtrudedZoneMesh');
    return null;
  }

  console.log(`🎨 v0.1.12: Creating configurable wireframe zone`);
  console.log(`   Zone: ${zoneData.zone_name} (${zoneData.zone_id})`);
  console.log(`   Labels: ${showLabels ? 'ON' : 'OFF'} | Corner Markers: ${showCornerMarkers ? 'ON' : 'OFF'}`);

  const zoneGroup = new THREE.Group();

  // LAYER 1: Base filled plane (very subtle)
  const baseGeometry = new THREE.BufferGeometry();
  const bounds = new THREE.Box3().setFromBufferAttribute(geometry.getAttribute('position'));
  const baseY = bounds.min.y;
  
  const minX = bounds.min.x, maxX = bounds.max.x;
  const minZ = bounds.min.z, maxZ = bounds.max.z;
  
  const basePositions = new Float32Array([
    minX, baseY, minZ,
    maxX, baseY, minZ,
    maxX, baseY, maxZ,
    minX, baseY, minZ,
    maxX, baseY, maxZ,
    minX, baseY, maxZ
  ]);
  
  baseGeometry.setAttribute('position', new THREE.BufferAttribute(basePositions, 3));
  
  const baseMaterial = new THREE.MeshBasicMaterial({
    color: color,
    transparent: true,
    opacity: opacity * 0.15, // Very subtle fill
    side: THREE.DoubleSide,
    depthWrite: false
  });
  
  const baseMesh = new THREE.Mesh(baseGeometry, baseMaterial);
  zoneGroup.add(baseMesh);

  // LAYER 2: Primary wireframe (always visible - the core feature)
  const wireframeGeometry = new THREE.EdgesGeometry(geometry);
  const primaryWireframeMaterial = new THREE.LineBasicMaterial({
    color: color,
    linewidth: 3,
    transparent: true,
    opacity: Math.min(1.0, opacity + 0.4),
    depthTest: false // Always render on top
  });
  
  const primaryWireframe = new THREE.LineSegments(wireframeGeometry, primaryWireframeMaterial);
  zoneGroup.add(primaryWireframe);

  // LAYER 3: Secondary wireframe (backup for depth perception)
  const secondaryWireframeMaterial = new THREE.LineBasicMaterial({
    color: new THREE.Color(color).multiplyScalar(1.2),
    linewidth: 1,
    transparent: true,
    opacity: 0.8,
    depthTest: true
  });
  
  const secondaryWireframe = new THREE.LineSegments(wireframeGeometry.clone(), secondaryWireframeMaterial);
  zoneGroup.add(secondaryWireframe);

  // LAYER 4: Corner markers (OPTIONAL - controlled by showCornerMarkers parameter)
  if (showCornerMarkers) {
    const cornerGroup = new THREE.Group();
    const sphereGeometry = new THREE.SphereGeometry(2, 12, 12);
    
    const corners = [
      new THREE.Vector3(bounds.min.x, bounds.min.y, bounds.min.z),
      new THREE.Vector3(bounds.max.x, bounds.min.y, bounds.min.z),
      new THREE.Vector3(bounds.max.x, bounds.max.y, bounds.min.z),
      new THREE.Vector3(bounds.min.x, bounds.max.y, bounds.min.z),
      new THREE.Vector3(bounds.min.x, bounds.min.y, bounds.max.z),
      new THREE.Vector3(bounds.max.x, bounds.min.y, bounds.max.z),
      new THREE.Vector3(bounds.max.x, bounds.max.y, bounds.max.z),
      new THREE.Vector3(bounds.min.x, bounds.max.y, bounds.max.z)
    ];

    corners.forEach((corner, index) => {
      const isBottom = index < 4;
      const sphereMaterial = new THREE.MeshBasicMaterial({
        color: isBottom ? 0xff4444 : 0x4444ff, // Red for bottom, blue for top
        transparent: true,
        opacity: 0.8
      });
      const sphere = new THREE.Mesh(sphereGeometry, sphereMaterial);
      sphere.position.copy(corner);
      
      // Mark sphere for easy identification
      sphere.userData.isCornerMarker = true;
      sphere.userData.cornerIndex = index;
      sphere.userData.isBottom = isBottom;
      
      cornerGroup.add(sphere);
    });

    zoneGroup.add(cornerGroup);
    console.log(`🔴🔵 Added 8 corner markers (4 red bottom, 4 blue top)`);
  } else {
    console.log(`🚫 Skipped corner markers (disabled)`);
  }

  // LAYER 5: Zone label (OPTIONAL - controlled by showLabels parameter)
  if (showLabels) {
    const labelGeometry = new THREE.PlaneGeometry(20, 5);
    const canvas = document.createElement('canvas');
    canvas.width = 256;
    canvas.height = 64;
    const context = canvas.getContext('2d');
    
    context.fillStyle = '#000000';
    context.fillRect(0, 0, canvas.width, canvas.height);
    context.fillStyle = '#ffffff';
    context.font = 'bold 16px Arial';
    context.textAlign = 'center';
    context.fillText(zoneData.zone_name, canvas.width / 2, canvas.height / 2 + 6);
    
    const labelTexture = new THREE.CanvasTexture(canvas);
    const labelMaterial = new THREE.MeshBasicMaterial({
      map: labelTexture,
      transparent: true,
      opacity: 0.8,
      depthTest: false
    });
    
    const labelMesh = new THREE.Mesh(labelGeometry, labelMaterial);
    labelMesh.position.set(
      (bounds.min.x + bounds.max.x) / 2,
      bounds.max.y + 5,
      (bounds.min.z + bounds.max.z) / 2
    );
    labelMesh.lookAt(0, bounds.max.y + 5, 100);
    
    // Mark label for easy identification
    labelMesh.userData.isZoneLabel = true;
    
    zoneGroup.add(labelMesh);
    console.log(`📋 Added text label for ${zoneData.zone_name}`);
  } else {
    console.log(`🚫 Skipped text label (disabled)`);
  }

  // Set user data
  zoneGroup.userData.isRealZone = true;
  zoneGroup.userData.isExtrudedGeometry = true;
  zoneGroup.userData.zoneId = zoneData.zone_id;
  zoneGroup.userData.zoneName = zoneData.zone_name;
  zoneGroup.userData.renderMethod = `WIREFRAME_${showLabels ? 'L' : ''}${showCornerMarkers ? 'C' : ''}`;
  zoneGroup.userData.hasLabels = showLabels;
  zoneGroup.userData.hasCornerMarkers = showCornerMarkers;

  // Calculate layer count
  let layerCount = 3; // Base + Primary wireframe + Secondary wireframe
  if (showCornerMarkers) layerCount++;
  if (showLabels) layerCount++;

  console.log(`✅ v0.1.12: Created wireframe zone with ${layerCount} layers`);
  console.log(`   Core: Base + Primary/Secondary wireframes (always)`);
  console.log(`   Optional: ${showCornerMarkers ? 'Corner markers ✅' : 'Corner markers ❌'} | ${showLabels ? 'Labels ✅' : 'Labels ❌'}`);
  
  return zoneGroup;
};

/**
 * Create flat zone polygon - v0.1.12 (same as v0.1.11)
 */
export const createFlatZonePolygon = (vertices, mapBounds, zHeight = 0) => {
  if (vertices.length < 3) {
    console.warn('⚠️ Need at least 3 vertices to create flat zone polygon');
    return null;
  }

  console.log(`🏗️ v0.1.12: Creating flat polygon for configurable wireframe rendering`);

  const threeVertices = vertices.map((vertex, index) => {
    return parcoToThreeJs(vertex.x, vertex.y, vertex.z, mapBounds);
  });

  let signedArea = 0;
  for (let i = 0; i < threeVertices.length; i++) {
    const j = (i + 1) % threeVertices.length;
    signedArea += (threeVertices[j].x - threeVertices[i].x) * (threeVertices[j].z + threeVertices[i].z);
  }
  
  const isClockwise = signedArea > 0;
  const orderedVertices = isClockwise ? [...threeVertices].reverse() : threeVertices;

  const shape = new THREE.Shape();
  const firstVertex = orderedVertices[0];
  shape.moveTo(firstVertex.x, -firstVertex.z);
  
  for (let i = 1; i < orderedVertices.length; i++) {
    const vertex = orderedVertices[i];
    shape.lineTo(vertex.x, -vertex.z);
  }

  const geometry = new THREE.ShapeGeometry(shape);
  geometry.computeVertexNormals();
  geometry.rotateX(-Math.PI / 2);
  
  if (zHeight !== 0) {
    geometry.translate(0, zHeight, 0);
  }

  return geometry;
};

/**
 * Create flat zone mesh - v0.1.12 with optional labels and corner markers
 */
export const createFlatZoneMesh = (geometry, zoneData, color = 0x00ff00, showLabels = false, showCornerMarkers = true) => {
  if (!geometry) {
    console.error('❌ No geometry provided to createFlatZoneMesh');
    return null;
  }

  console.log(`🎨 v0.1.12: Creating flat wireframe zone (labels: ${showLabels ? 'ON' : 'OFF'}, corners: ${showCornerMarkers ? 'ON' : 'OFF'})`);
  
  const zoneGroup = new THREE.Group();

  // Subtle filled base
  const baseMaterial = new THREE.MeshBasicMaterial({
    color: color,
    transparent: true,
    opacity: 0.1,
    side: THREE.DoubleSide,
    depthWrite: false
  });

  const baseMesh = new THREE.Mesh(geometry, baseMaterial);
  zoneGroup.add(baseMesh);

  // Primary wireframe outline
  const wireframeGeometry = new THREE.EdgesGeometry(geometry);
  const wireframeMaterial = new THREE.LineBasicMaterial({
    color: new THREE.Color(color).multiplyScalar(1.2),
    linewidth: 2,
    transparent: true,
    opacity: 1.0,
    depthTest: false
  });
  
  const wireframeMesh = new THREE.LineSegments(wireframeGeometry, wireframeMaterial);
  zoneGroup.add(wireframeMesh);

  // Optional corner markers for flat zones (just 4 corners)
  if (showCornerMarkers) {
    const bounds = new THREE.Box3().setFromObject(baseMesh);
    const cornerGroup = new THREE.Group();
    const sphereGeometry = new THREE.SphereGeometry(1.5, 10, 10); // Smaller for flat zones
    
    const corners = [
      new THREE.Vector3(bounds.min.x, bounds.min.y, bounds.min.z),
      new THREE.Vector3(bounds.max.x, bounds.min.y, bounds.min.z),
      new THREE.Vector3(bounds.max.x, bounds.min.y, bounds.max.z),
      new THREE.Vector3(bounds.min.x, bounds.min.y, bounds.max.z)
    ];

    corners.forEach((corner, index) => {
      const sphereMaterial = new THREE.MeshBasicMaterial({
        color: 0x44ff44, // Green for flat zone corners
        transparent: true,
        opacity: 0.8
      });
      const sphere = new THREE.Mesh(sphereGeometry, sphereMaterial);
      sphere.position.copy(corner);
      sphere.userData.isCornerMarker = true;
      cornerGroup.add(sphere);
    });

    zoneGroup.add(cornerGroup);
  }

  // Optional label for flat zones
  if (showLabels) {
    const bounds = new THREE.Box3().setFromObject(baseMesh);
    
    const labelGeometry = new THREE.PlaneGeometry(15, 4);
    const canvas = document.createElement('canvas');
    canvas.width = 200;
    canvas.height = 50;
    const context = canvas.getContext('2d');
    
    context.fillStyle = '#000000';
    context.fillRect(0, 0, canvas.width, canvas.height);
    context.fillStyle = '#ffffff';
    context.font = 'bold 12px Arial';
    context.textAlign = 'center';
    context.fillText(zoneData.zone_name, canvas.width / 2, canvas.height / 2 + 4);
    
    const labelTexture = new THREE.CanvasTexture(canvas);
    const labelMaterial = new THREE.MeshBasicMaterial({
      map: labelTexture,
      transparent: true,
      opacity: 0.8,
      depthTest: false
    });
    
    const labelMesh = new THREE.Mesh(labelGeometry, labelMaterial);
    labelMesh.position.set(
      (bounds.min.x + bounds.max.x) / 2,
      bounds.max.y + 3,
      (bounds.min.z + bounds.max.z) / 2
    );
    labelMesh.userData.isZoneLabel = true;
    
    zoneGroup.add(labelMesh);
  }

  zoneGroup.userData.isRealZone = true;
  zoneGroup.userData.isShapeGeometry = true;
  zoneGroup.userData.zoneId = zoneData.zone_id;
  zoneGroup.userData.zoneName = zoneData.zone_name;
  zoneGroup.userData.renderMethod = `WIREFRAME_FLAT_${showLabels ? 'L' : ''}${showCornerMarkers ? 'C' : ''}`;
  zoneGroup.userData.hasLabels = showLabels;
  zoneGroup.userData.hasCornerMarkers = showCornerMarkers;

  console.log(`✅ v0.1.12: Created flat wireframe zone with configurable features`);
  return zoneGroup;
};