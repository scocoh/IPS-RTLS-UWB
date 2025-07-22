/* Name: wireframeUtils.js */
/* Version: 0.1.1 */
/* Created: 250719 */
/* Modified: 250719 */
/* Creator: ParcoAdmin + Claude */
/* Modified By: ParcoAdmin + Claude */
/* Description: Wireframe and 3D geometry utilities for zone visualization */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/ThreeDZoneViewer/utils */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

import * as THREE from 'three';
import { regionBoundsToThreeJs, verticesToThreeJs, getBoundsCenter, getBoundsSize, parcoToThreeJs, createBoundsFromPoints } from './coordinateUtils';

/**
 * Create a wireframe bounding box from region bounds
 */
export const createWireframeBoundingBox = (region, options = {}) => {
  const {
    color = 0xff0000,
    opacity = 0.8,
    linewidth = 2,
    transparent = true
  } = options;

  // Convert region bounds to Three.js coordinates
  const bounds = regionBoundsToThreeJs(region);
  const size = {
    width: Math.abs(bounds.maxX - bounds.minX),
    height: Math.abs(bounds.maxY - bounds.minY),
    depth: Math.abs(bounds.maxZ - bounds.minZ)
  };
  
  const center = {
    x: (bounds.maxX + bounds.minX) / 2,
    y: (bounds.maxY + bounds.minY) / 2,
    z: (bounds.maxZ + bounds.minZ) / 2
  };

  // Create box geometry
  const geometry = new THREE.BoxGeometry(size.width, size.height, size.depth);
  
  // Create wireframe material
  const material = new THREE.MeshBasicMaterial({
    color,
    wireframe: true,
    transparent,
    opacity,
    side: THREE.DoubleSide
  });

  // Create mesh
  const wireframe = new THREE.Mesh(geometry, material);
  wireframe.position.set(center.x, center.y, center.z);

  return wireframe;
};

/**
 * Create wireframe from vertices
 */
export const createWireframeFromVertices = (vertices, options = {}) => {
  const {
    color = 0x00ff00,
    opacity = 0.8,
    linewidth = 2,
    closed = true
  } = options;

  if (!vertices || vertices.length < 3) {
    console.warn('Need at least 3 vertices to create wireframe');
    return null;
  }

  // Convert vertices to Three.js coordinates
  const threeJsVertices = verticesToThreeJs(vertices);
  
  // Sort by order
  threeJsVertices.sort((a, b) => (a.order || 0) - (b.order || 0));

  // Compute bounds for dynamic height
  const bounds = createBoundsFromPoints(threeJsVertices);
  const size = getBoundsSize(bounds, 'threejs');
  const height = Math.max(size.height, 10); // Min 10 if flat

  // Create points for the base (at min y)
  const minY = Math.min(...threeJsVertices.map(v => v.y));
  const basePoints = threeJsVertices.map(v => new THREE.Vector3(v.x, minY, v.z));
  
  if (closed && basePoints.length > 2) {
    basePoints.push(basePoints[0]); // Close the loop
  }

  // Create line geometry for base
  const baseGeometry = new THREE.BufferGeometry().setFromPoints(basePoints);
  const lineMaterial = new THREE.LineBasicMaterial({ 
    color, 
    linewidth,
    transparent: true,
    opacity 
  });
  
  const baseLine = new THREE.Line(baseGeometry, lineMaterial);

  // Create vertical lines and top
  const group = new THREE.Group();
  group.add(baseLine);

  // Create top line at max height
  const topPoints = basePoints.map(p => new THREE.Vector3(p.x, minY + height, p.z));
  
  const topGeometry = new THREE.BufferGeometry().setFromPoints(topPoints);
  const topLine = new THREE.Line(topGeometry, lineMaterial);
  group.add(topLine);

  // Create vertical connecting lines
  basePoints.forEach((p, i) => {
    const verticalPoints = [
      p,
      topPoints[i]
    ];
    
    const verticalGeometry = new THREE.BufferGeometry().setFromPoints(verticalPoints);
    const verticalLine = new THREE.Line(verticalGeometry, lineMaterial);
    group.add(verticalLine);
  });

  return group;
};

/**
 * Create extruded solid from vertices
 */
export const createExtrudedSolid = (vertices, options = {}) => {
  const {
    color = 0x0088ff,
    opacity = 0.5,
    height = 10,
    transparent = true,
    wireframe = false
  } = options;

  if (!vertices || vertices.length < 3) {
    console.warn('Need at least 3 vertices to create extruded solid');
    return null;
  }

  try {
    // Convert vertices to Three.js coordinates
    const threeJsVertices = verticesToThreeJs(vertices);
    
    // Sort by order
    threeJsVertices.sort((a, b) => (a.order || 0) - (b.order || 0));

    // Create 2D shape from vertices (projected to XZ plane)
    const shape = new THREE.Shape();
    
    if (threeJsVertices.length > 0) {
      const firstVertex = threeJsVertices[0];
      shape.moveTo(firstVertex.x, firstVertex.z);
      
      for (let i = 1; i < threeJsVertices.length; i++) {
        const vertex = threeJsVertices[i];
        shape.lineTo(vertex.x, vertex.z);
      }
      
      shape.closePath();
    }

    // Extrude settings
    const extrudeSettings = {
      depth: height,
      bevelEnabled: false
    };

    // Create extruded geometry
    const geometry = new THREE.ExtrudeGeometry(shape, extrudeSettings);
    
    // Create material
    const material = new THREE.MeshLambertMaterial({
      color,
      transparent,
      opacity,
      wireframe,
      side: THREE.DoubleSide
    });

    // Create mesh
    const mesh = new THREE.Mesh(geometry, material);
    
    // Position at min Y of vertices
    const minY = Math.min(...threeJsVertices.map(v => v.y));
    mesh.position.y = minY;
    
    return mesh;

  } catch (error) {
    console.error('Error creating extruded solid:', error);
    return null;
  }
};

/**
 * Create zone wireframe based on zone type
 */
export const createZoneWireframe = (zone, regionData, options = {}) => {
  const zoneTypeColors = {
    1: 0xff0000,   // Campus L1 - Red
    2: 0x00ff00,   // Building L3 - Green
    3: 0x0000ff,   // Floor L4 - Blue
    4: 0xffaa00,   // Wing L5 - Orange
    5: 0x8800ff,   // Room L6 - Purple
    10: 0xffaa00,  // Building Outside L2 - Light Orange
    20: 0x888888,  // Outdoor General - Gray
    901: 0xffff00  // Virtual Subject - Yellow
  };

  const zoneTypeHeights = {
    1: 30,   // Campus
    2: 25,   // Building L3
    3: 15,   // Floor L4
    4: 12,   // Wing L5
    5: 8,    // Room L6
    10: 20,  // Building Outside L2
    20: 5,   // Outdoor
    901: 15  // Virtual
  };

  const defaultOptions = {
    color: zoneTypeColors[zone.zone_type] || 0x666666,
    height: zoneTypeHeights[zone.zone_type] || 10,
    opacity: 0.7,
    wireframe: true
  };

  const finalOptions = { ...defaultOptions, ...options };

  // If we have region data with vertices, use them
  if (regionData && regionData.length > 0) {
    const region = regionData[0]; // Use first region
    
    // Check if region has vertices
    const vertices = regionData.filter(r => r.n_x !== undefined);
    
    if (vertices.length >= 3) {
      return createWireframeFromVertices(vertices, finalOptions);
    } else {
      // Use region bounds for bounding box
      return createWireframeBoundingBox(region, finalOptions);
    }
  }

  // Default: create a simple box based on zone type
  return createDefaultZoneBox(zone, finalOptions);
};

/**
 * Create default zone box when no region data
 */
export const createDefaultZoneBox = (zone, options = {}) => {
  const {
    color = 0x666666,
    height = 10,
    opacity = 0.7
  } = options;

  // Default sizes based on zone type
  const defaultSizes = {
    1: { width: 200, depth: 150 },  // Campus
    2: { width: 80, depth: 60 },    // Building L3
    3: { width: 60, depth: 45 },    // Floor L4
    4: { width: 40, depth: 30 },    // Wing L5
    5: { width: 20, depth: 15 },    // Room L6
    10: { width: 100, depth: 75 }, // Building Outside L2
    20: { width: 150, depth: 100 }, // Outdoor
    901: { width: 10, depth: 10 }   // Virtual
  };

  const size = defaultSizes[zone.zone_type] || { width: 30, depth: 20 };

  const geometry = new THREE.BoxGeometry(size.width, height, size.depth);
  const material = new THREE.MeshBasicMaterial({
    color,
    wireframe: true,
    transparent: true,
    opacity
  });

  const box = new THREE.Mesh(geometry, material);
  
  // Position with spacing based on zone ID
  const spacing = 120;
  const row = Math.floor((zone.zone_id - 1) / 5);
  const col = (zone.zone_id - 1) % 5;
  
  box.position.set(
    col * spacing - spacing * 2,
    height / 2,
    row * spacing - spacing * 2
  );

  return box;
};

/**
 * Create edges for wireframe effect
 */
export const createWireframeEdges = (mesh, options = {}) => {
  const {
    color = 0xffffff,
    linewidth = 1,
    opacity = 1.0
  } = options;

  if (!mesh || !mesh.geometry) {
    console.warn('Invalid mesh for wireframe edges');
    return null;
  }

  const edges = new THREE.EdgesGeometry(mesh.geometry);
  const material = new THREE.LineBasicMaterial({ 
    color, 
    linewidth,
    transparent: opacity < 1.0,
    opacity 
  });
  
  const wireframe = new THREE.LineSegments(edges, material);
  wireframe.position.copy(mesh.position);
  wireframe.rotation.copy(mesh.rotation);
  wireframe.scale.copy(mesh.scale);

  return wireframe;
};

/**
 * Create glow effect for wireframes
 */
export const createGlowEffect = (object, options = {}) => {
  const {
    color = 0x00ffff,
    intensity = 0.5,
    size = 1.1
  } = options;

  if (!object || !object.geometry) {
    console.warn('Invalid object for glow effect');
    return null;
  }

  // Clone geometry and scale it up slightly
  const glowGeometry = object.geometry.clone();
  
  const glowMaterial = new THREE.MeshBasicMaterial({
    color,
    transparent: true,
    opacity: intensity,
    side: THREE.BackSide
  });

  const glowMesh = new THREE.Mesh(glowGeometry, glowMaterial);
  glowMesh.scale.multiplyScalar(size);
  glowMesh.position.copy(object.position);
  glowMesh.rotation.copy(object.rotation);

  return glowMesh;
};

/**
 * Create animated wireframe with pulsing effect
 */
export const createAnimatedWireframe = (geometry, options = {}) => {
  const {
    color = 0x00ff00,
    pulseSpeed = 0.01,
    minOpacity = 0.3,
    maxOpacity = 1.0
  } = options;

  const material = new THREE.MeshBasicMaterial({
    color,
    wireframe: true,
    transparent: true,
    opacity: maxOpacity
  });

  const mesh = new THREE.Mesh(geometry, material);

  // Add animation function
  mesh.animate = () => {
    const time = Date.now() * pulseSpeed;
    const opacity = minOpacity + (maxOpacity - minOpacity) * (Math.sin(time) * 0.5 + 0.5);
    material.opacity = opacity;
  };

  return mesh;
};

/**
 * Calculate optimal wireframe thickness based on distance
 */
export const calculateOptimalLineWidth = (distance, baseWidth = 2) => {
  // Increase line width for distant objects
  const scaleFactor = Math.max(1, distance / 100);
  return Math.min(baseWidth * scaleFactor, 10); // Cap at 10px
};

/**
 * Create level-of-detail wireframe
 */
export const createLODWireframe = (geometry, distances = [50, 100, 200], options = {}) => {
  const lod = new THREE.LOD();

  distances.forEach((distance, index) => {
    const detail = 1 - (index / distances.length);
    
    // Simplify geometry based on detail level
    let lodGeometry = geometry;
    if (detail < 1) {
      // In a real implementation, you might use geometry simplification
      lodGeometry = geometry.clone();
    }

    const material = new THREE.MeshBasicMaterial({
      color: options.color || 0x00ff00,
      wireframe: true,
      transparent: true,
      opacity: (options.opacity || 0.7) * detail
    });

    const mesh = new THREE.Mesh(lodGeometry, material);
    lod.addLevel(mesh, distance);
  });

  return lod;
};

/**
 * Dispose of wireframe resources
 */
export const disposeWireframe = (wireframe) => {
  if (!wireframe) return;

  // Handle groups
  if (wireframe.type === 'Group') {
    wireframe.children.forEach(child => disposeWireframe(child));
    return;
  }

  // Dispose geometry
  if (wireframe.geometry) {
    wireframe.geometry.dispose();
  }

  // Dispose material
  if (wireframe.material) {
    if (Array.isArray(wireframe.material)) {
      wireframe.material.forEach(material => material.dispose());
    } else {
      wireframe.material.dispose();
    }
  }

  // Dispose texture if present
  if (wireframe.material && wireframe.material.map) {
    wireframe.material.map.dispose();
  }
};

export default {
  createWireframeBoundingBox,
  createWireframeFromVertices,
  createExtrudedSolid,
  createZoneWireframe,
  createDefaultZoneBox,
  createWireframeEdges,
  createGlowEffect,
  createAnimatedWireframe,
  calculateOptimalLineWidth,
  createLODWireframe,
  disposeWireframe
};