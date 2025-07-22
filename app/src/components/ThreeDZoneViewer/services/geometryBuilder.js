/* Name: geometryBuilder.js */
/* Version: 0.1.3 */
/* Created: 250719 */
/* Modified: 250721 */
/* Creator: ParcoAdmin + Claude */
/* Modified By: ParcoAdmin + Claude */
/* Description: Service for building 3D geometries from ParcoRTLS zone data with all-angle visibility enhancements */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/ThreeDZoneViewer/services */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

import * as THREE from 'three';
import { parcoToThreeJs, createBoundsFromPoints } from '../utils/coordinateUtils';

class GeometryBuilder {
  constructor() {
    this.materialCache = new Map();
    this.geometryCache = new Map();
  }

  /**
   * Create a cached material for zone types - ENHANCED FOR ALL-ANGLE VISIBILITY
   */
  getMaterial(zoneType, options = {}) {
    const {
      color = this.getZoneTypeColor(zoneType),
      wireframe = true,
      transparent = true,
      opacity = 0.7,
      linewidth = 2
    } = options;

    const cacheKey = `${zoneType}_${color}_${wireframe}_${opacity}`;
    
    if (this.materialCache.has(cacheKey)) {
      return this.materialCache.get(cacheKey);
    }

    const material = wireframe 
      ? new THREE.MeshBasicMaterial({
          color,
          wireframe: true,
          transparent,
          opacity,
          side: THREE.DoubleSide, // CRITICAL: Visible from both sides
          depthWrite: false
        })
      : new THREE.MeshStandardMaterial({
          color,
          transparent,
          opacity,
          roughness: 0.5,
          metalness: 0.1,
          side: THREE.DoubleSide, // CRITICAL: Visible from both sides
          flatShading: false, // ENHANCED: Smooth shading for better visibility
          emissive: new THREE.Color(color).multiplyScalar(0.1) // ENHANCED: Slight self-illumination
        });

    this.materialCache.set(cacheKey, material);
    return material;
  }

  /**
   * Get color for zone type
   */
  getZoneTypeColor(zoneType) {
    const colors = {
      1: 0xff0000,   // Campus L1 - Red
      2: 0x00ff00,   // Building L3 - Green
      3: 0x0000ff,   // Floor L4 - Blue
      4: 0xff00ff,   // Wing L5 - Magenta
      5: 0x8800ff,   // Room L6 - Purple
      10: 0xff8800,  // Building Outside L2 - Orange
      20: 0x888888,  // Outdoor General - Gray
      901: 0xffff00  // Virtual Subject - Yellow
    };
    return colors[zoneType] || 0x666666;
  }

  /**
   * Create a wireframe bounding box from region data
   */
  createZoneBoundingBox(zone, regionData = []) {
    if (!regionData || regionData.length === 0) {
      // Fallback: create default box
      return this.createDefaultZoneBox(zone);
    }

    // Get bounds from region data
    const region = regionData[0]; // Use first region
    const minX = region.n_min_x || 0;
    const minY = region.n_min_y || 0;
    const minZ = region.n_min_z || 0;
    const maxX = region.n_max_x || 10;
    const maxY = region.n_max_y || 10;
    const maxZ = region.n_max_z || 10;

    const mappedMin = parcoToThreeJs(minX, minY, minZ);
    const mappedMax = parcoToThreeJs(maxX, maxY, maxZ);

    const width = Math.abs(mappedMax.x - mappedMin.x);
    const height = Math.abs(mappedMax.y - mappedMin.y) || 10; // Use Y for height
    const depth = Math.abs(mappedMax.z - mappedMin.z);

    console.log(`📦 Creating bounding box for ${zone.zone_name}: ${width}x${height}x${depth}`);

    // Create geometry
    const geometry = new THREE.BoxGeometry(width, height, depth);
    const material = this.getMaterial(zone.zone_type, { wireframe: true });
    
    const box = new THREE.Mesh(geometry, material);
    
    // Position at center of bounds
    box.position.set(
      (mappedMax.x + mappedMin.x) / 2,
      (mappedMax.y + mappedMin.y) / 2,
      (mappedMax.z + mappedMin.z) / 2
    );

    // Add metadata
    box.userData = {
      isZone: true,
      clickable: true,
      zoneId: zone.zone_id,
      zoneName: zone.zone_name,
      zoneType: zone.zone_type,
      zone: zone,
      regionData: regionData
    };

    return box;
  }

  /**
   * Create default zone box when no region data available
   */
  createDefaultZoneBox(zone) {
    // Default sizes based on zone type
    const defaultSizes = {
      1: { w: 200, h: 30, d: 150 },  // Campus - Large
      2: { w: 80, h: 25, d: 60 },    // Building L3
      3: { w: 60, h: 15, d: 45 },    // Floor L4
      4: { w: 40, h: 12, d: 30 },    // Wing L5
      5: { w: 20, h: 8, d: 15 },     // Room L6 - Small
      10: { w: 100, h: 20, d: 75 },  // Building Outside L2
      20: { w: 150, h: 5, d: 100 },  // Outdoor - Flat
      901: { w: 10, h: 15, d: 10 }   // Virtual - Small
    };

    const size = defaultSizes[zone.zone_type] || { w: 30, h: 15, d: 20 };
    
    const geometry = new THREE.BoxGeometry(size.w, size.h, size.d);
    const material = this.getMaterial(zone.zone_type, { wireframe: true });
    
    const box = new THREE.Mesh(geometry, material);
    
    // Position with some spacing based on zone ID
    const spacing = 120;
    const row = Math.floor((zone.zone_id - 1) / 5);
    const col = (zone.zone_id - 1) % 5;
    
    box.position.set(
      col * spacing - spacing * 2,
      size.h / 2,
      row * spacing - spacing * 2
    );

    // Add metadata
    box.userData = {
      isZone: true,
      clickable: true,
      zoneId: zone.zone_id,
      zoneName: zone.zone_name,
      zoneType: zone.zone_type,
      zone: zone,
      isDefaultBox: true
    };

    console.log(`📦 Created default box for ${zone.zone_name} at position:`, box.position);
    
    return box;
  }

  /**
   * Create zone geometry from vertices (for complex shapes)
   */
  createZoneFromVertices(zone, vertices = []) {
    if (!vertices || vertices.length < 3) {
      return this.createDefaultZoneBox(zone);
    }

    try {
      // Sort vertices by order
      const sortedVertices = vertices.sort((a, b) => a.n_ord - b.n_ord);
      
      // Map to Three.js coordinates
      const mappedVertices = sortedVertices.map(v => parcoToThreeJs(v.n_x, v.n_y, v.n_z || 0));

      // Create bounds from mapped vertices
      const bounds = createBoundsFromPoints(mappedVertices);

      // Create 2D shape from vertices (XZ plane)
      const shape = new THREE.Shape();
      
      if (mappedVertices.length > 0) {
        const firstVertex = mappedVertices[0];
        shape.moveTo(firstVertex.x, firstVertex.z);
        
        for (let i = 1; i < mappedVertices.length; i++) {
          const vertex = mappedVertices[i];
          shape.lineTo(vertex.x, vertex.z);
        }
        
        shape.closePath();
      }

      // Extrude the shape to create 3D geometry
      const extrudeSettings = {
        depth: this.getZoneHeight(zone.zone_type),
        bevelEnabled: false
      };
      
      const geometry = new THREE.ExtrudeGeometry(shape, extrudeSettings);
      const material = this.getMaterial(zone.zone_type, { 
        wireframe: false, 
        opacity: 0.5 
      });
      
      const mesh = new THREE.Mesh(geometry, material);
      
      // Position at average Y of vertices
      const avgY = mappedVertices.reduce((sum, v) => sum + v.y, 0) / mappedVertices.length;
      mesh.position.y = avgY;
      
      // Add wireframe edges
      const edges = new THREE.EdgesGeometry(geometry);
      const edgeMaterial = new THREE.LineBasicMaterial({ 
        color: this.getZoneTypeColor(zone.zone_type) 
      });
      const wireframe = new THREE.LineSegments(edges, edgeMaterial);
      
      // Create group with both mesh and wireframe
      const group = new THREE.Group();
      group.add(mesh);
      group.add(wireframe);
      
      // Add metadata
      group.userData = {
        isZone: true,
        clickable: true,
        zoneId: zone.zone_id,
        zoneName: zone.zone_name,
        zoneType: zone.zone_type,
        zone: zone,
        vertices: vertices,
        hasCustomShape: true
      };

      console.log(`🔺 Created zone from ${vertices.length} vertices for ${zone.zone_name}`);
      
      return group;
      
    } catch (error) {
      console.error(`❌ Error creating zone from vertices for ${zone.zone_name}:`, error);
      return this.createDefaultZoneBox(zone);
    }
  }

  /**
   * Get height for zone type
   */
  getZoneHeight(zoneType) {
    const heights = {
      1: 30,   // Campus
      2: 25,   // Building L3
      3: 15,   // Floor L4
      4: 12,   // Wing L5
      5: 8,    // Room L6
      10: 20,  // Building Outside L2
      20: 5,   // Outdoor
      901: 15  // Virtual
    };
    return heights[zoneType] || 10;
  }

  /**
   * Create a map plane from map data - ENHANCED FOR ALL-ANGLE VISIBILITY
   */
  createMapPlane(mapData) {
    if (!mapData || !mapData.bounds) {
      console.warn('⚠️ No map data provided for plane creation');
      return null;
    }

    // Parse bounds: [[min_y, min_x], [max_y, max_x]]
    const minX = mapData.bounds[0][1];
    const minY = mapData.bounds[0][0];
    const maxX = mapData.bounds[1][1];
    const maxY = mapData.bounds[1][0];
    
    const width = maxX - minX;
    const height = maxY - minY;
    
    console.log(`🗺️ Creating map plane: ${width} x ${height}`);

    const geometry = new THREE.PlaneGeometry(width, height);
    const material = new THREE.MeshStandardMaterial({
      color: 0x4a90e2,
      side: THREE.DoubleSide, // CRITICAL: Visible from both sides
      transparent: true,
      opacity: 0.3,
      roughness: 1.0,
      metalness: 0.0,
      emissive: new THREE.Color(0x4a90e2).multiplyScalar(0.05) // ENHANCED: Slight self-illumination
    });

    const plane = new THREE.Mesh(geometry, material);
    plane.rotation.x = -Math.PI / 2; // Rotate to horizontal
    plane.position.set(
      (maxX + minX) / 2,
      -1, // Slightly below ground
      (maxY + minY) / 2
    );
    plane.receiveShadow = false; // No shadows

    // Add metadata
    plane.userData = {
      isMapPlane: true,
      clickable: false,
      mapData: mapData
    };

    return plane;
  }

  /**
   * Create zone label
   */
  createZoneLabel(zone, position) {
    // Create text geometry (simplified - in real app might use TextGeometry)
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');
    
    canvas.width = 256;
    canvas.height = 64;
    
    context.fillStyle = '#ffffff';
    context.fillRect(0, 0, canvas.width, canvas.height);
    
    context.fillStyle = '#000000';
    context.font = '16px Arial';
    context.textAlign = 'center';
    context.fillText(zone.zone_name, canvas.width / 2, canvas.height / 2);
    
    const texture = new THREE.CanvasTexture(canvas);
    const material = new THREE.MeshBasicMaterial({ 
      map: texture, 
      transparent: true 
    });
    
    const geometry = new THREE.PlaneGeometry(20, 5);
    const label = new THREE.Mesh(geometry, material);
    
    label.position.copy(position);
    label.position.y += 10; // Above the zone
    
    // Make label always face camera
    label.lookAt(0, position.y + 10, 100);
    
    label.userData = {
      isLabel: true,
      clickable: false,
      zoneId: zone.zone_id
    };
    
    return label;
  }

  /**
   * Clear cached materials and geometries
   */
  clearCache() {
    this.materialCache.clear();
    this.geometryCache.clear();
    console.log('🧹 Geometry builder cache cleared');
  }

  /**
   * Dispose of materials and geometries
   */
  dispose() {
    for (const material of this.materialCache.values()) {
      material.dispose();
    }
    
    for (const geometry of this.geometryCache.values()) {
      geometry.dispose();
    }
    
    this.clearCache();
  }
}

// Export singleton instance
export default new GeometryBuilder();