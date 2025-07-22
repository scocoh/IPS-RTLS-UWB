/* Name: mapCoordinateSystem.js */
/* Version: 0.1.0 */
/* Created: 250719 */
/* Modified: 250719 */
/* Creator: ParcoAdmin + Claude */
/* Modified By: ParcoAdmin + Claude */
/* Description: Map coordinate system utilities for ParcoRTLS 3D visualization - UCS origin at bottom-left */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/ThreeDZoneViewer/utils */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

/**
 * Map Coordinate System Management
 * 
 * ParcoRTLS coordinate system: X+ = East, Y+ = North, Z+ = Up (feet)
 * Three.js coordinate system:  X+ = East, Y+ = Up,    Z+ = South (feet)
 * 
 * UCS Origin: Bottom-left corner of map plane at Three.js (0,0,0)
 * 
 * Map bounds format: { minX, minY, minZ, maxX, maxY, maxZ }
 * Standard map: min(0,0,0) to max(254,304,60) feet
 */

/**
 * Get map bounds from mapData
 * Converts various map data formats to standard bounds object
 */
export const getMapBounds = (mapData) => {
  if (!mapData) {
    console.warn('No map data provided, using default bounds');
    return { minX: 0, minY: 0, minZ: 0, maxX: 254, maxY: 304, maxZ: 60 };
  }

  // Handle mapData.bounds format: [[min_y, min_x], [max_y, max_x]]
  if (mapData.bounds && Array.isArray(mapData.bounds)) {
    const [[minY, minX], [maxY, maxX]] = mapData.bounds;
    return {
      minX: minX,
      minY: minY, 
      minZ: 0,
      maxX: maxX,
      maxY: maxY,
      maxZ: 60 // Standard map height
    };
  }

  // Handle direct bounds object
  if (mapData.minX !== undefined) {
    return {
      minX: mapData.minX || 0,
      minY: mapData.minY || 0,
      minZ: mapData.minZ || 0,
      maxX: mapData.maxX || 254,
      maxY: mapData.maxY || 304,
      maxZ: mapData.maxZ || 60
    };
  }

  // Fallback to default
  console.warn('Unknown map data format, using default bounds');
  return { minX: 0, minY: 0, minZ: 0, maxX: 254, maxY: 304, maxZ: 60 };
};

/**
 * Convert ParcoRTLS coordinates to Three.js coordinates with UCS translation
 * Origin is moved to bottom-left corner of map plane
 */
export const parcoToThreeJs = (x, y, z = 0, mapBounds) => {
  if (!mapBounds) {
    console.warn('No map bounds provided to parcoToThreeJs, using default');
    mapBounds = { minX: 0, minY: 0, minZ: 0, maxX: 254, maxY: 304, maxZ: 60 };
  }

  // Translate coordinates so map minimum becomes Three.js origin
  const translatedX = x - mapBounds.minX; // Parco X relative to map min
  const translatedY = y - mapBounds.minY; // Parco Y relative to map min  
  const translatedZ = z - mapBounds.minZ; // Parco Z relative to map min

  // Apply axis mapping: Parco X→Three Z, Parco Y→Three X, Parco Z→Three Y
  return {
    x: translatedY,  // Parco Y becomes Three X (East/West)
    y: translatedZ,  // Parco Z becomes Three Y (Up/Down)
    z: translatedX   // Parco X becomes Three Z (North/South)
  };
};

/**
 * Convert Three.js coordinates back to ParcoRTLS coordinates
 */
export const threeJsToParco = (x, y, z, mapBounds) => {
  if (!mapBounds) {
    console.warn('No map bounds provided to threeJsToParco, using default');
    mapBounds = { minX: 0, minY: 0, minZ: 0, maxX: 254, maxY: 304, maxZ: 60 };
  }

  // Reverse axis mapping: Three X→Parco Y, Three Y→Parco Z, Three Z→Parco X
  const parcoX = z + mapBounds.minX; // Three Z becomes Parco X, add offset
  const parcoY = x + mapBounds.minY; // Three X becomes Parco Y, add offset
  const parcoZ = y + mapBounds.minZ; // Three Y becomes Parco Z, add offset

  return {
    x: parcoX,
    y: parcoY,
    z: parcoZ
  };
};

/**
 * Create map plane geometry positioned with UCS at bottom-left
 */
export const createMapPlaneGeometry = (mapBounds) => {
  const width = mapBounds.maxY - mapBounds.minY;   // Parco Y range → Three X
  const height = mapBounds.maxX - mapBounds.minX;  // Parco X range → Three Z
  
  return {
    width: width,    // Three X dimension (304 feet)
    height: height,  // Three Z dimension (254 feet)
    position: {
      x: width / 2,   // Center X position (152)
      y: 0,           // Ground level
      z: height / 2   // Center Z position (127)
    }
  };
};

/**
 * Create hardcoded bounding box with UCS at origin
 * Box dimensions: 160×80×40 feet positioned at (0,0,0)
 */
export const createHardcodedBox = (mapBounds) => {
  // Box dimensions in ParcoRTLS coordinates
  const boxMinX = 0, boxMinY = 0, boxMinZ = 0;
  const boxMaxX = 160, boxMaxY = 80, boxMaxZ = 40;
  
  // Convert to Three.js coordinates
  const minThree = parcoToThreeJs(boxMinX, boxMinY, boxMinZ, mapBounds);
  const maxThree = parcoToThreeJs(boxMaxX, boxMaxY, boxMaxZ, mapBounds);
  
  const width = Math.abs(maxThree.x - minThree.x);   // Three X dimension = 80
  const height = Math.abs(maxThree.y - minThree.y);  // Three Y dimension = 40  
  const depth = Math.abs(maxThree.z - minThree.z);   // Three Z dimension = 160
  
  return {
    dimensions: { width, height, depth },
    position: {
      x: (minThree.x + maxThree.x) / 2,  // Center X = 40
      y: (minThree.y + maxThree.y) / 2,  // Center Y = 20
      z: (minThree.z + maxThree.z) / 2   // Center Z = 80
    },
    corners: {
      min: minThree,
      max: maxThree
    }
  };
};

/**
 * Get camera position for isometric view of the map and bounding box
 */
export const getCameraPosition = (mapBounds, distance = 1.2) => {
  // EXACT coordinates as specified: x=80, y=-120, z=120
  return {
    x: 80,                         // X = 80
    y: -120,                       // Y = -120 (negative!)
    z: 120                         // Z = 120 (positive!)
  };
};

/**
 * Debug logging for coordinate system
 */
export const logCoordinateSystem = (mapBounds) => {
  console.log('🗺️ Map Coordinate System Debug:');
  console.log('  Map Bounds (Parco):', mapBounds);
  console.log('  Map Dimensions:', `${mapBounds.maxX - mapBounds.minX} × ${mapBounds.maxY - mapBounds.minY} × ${mapBounds.maxZ - mapBounds.minZ} feet`);
  
  const mapPlane = createMapPlaneGeometry(mapBounds);
  console.log('  Map Plane (Three):', mapPlane);
  
  const hardcodedBox = createHardcodedBox(mapBounds);
  console.log('  Hardcoded Box (Three):', hardcodedBox);
  
  // Test coordinate conversion
  const testPoints = [
    { x: 0, y: 0, z: 0 },      // Origin
    { x: 160, y: 80, z: 40 },  // Box max
    { x: 254, y: 304, z: 60 }  // Map max
  ];
  
  console.log('  Coordinate Conversion Tests:');
  testPoints.forEach(point => {
    const three = parcoToThreeJs(point.x, point.y, point.z, mapBounds);
    const back = threeJsToParco(three.x, three.y, three.z, mapBounds);
    console.log(`    Parco(${point.x},${point.y},${point.z}) → Three(${three.x},${three.y},${three.z}) → Parco(${back.x},${back.y},${back.z})`);
  });
};

export default {
  getMapBounds,
  parcoToThreeJs,
  threeJsToParco,
  createMapPlaneGeometry,
  createHardcodedBox,
  getCameraPosition,
  logCoordinateSystem
};