/* Name: coordinateUtils.js */
/* Version: 0.1.1 */
/* Created: 250719 */
/* Modified: 250719 */
/* Creator: ParcoAdmin + Claude */
/* Modified By: ParcoAdmin + Claude */
/* Description: Coordinate transformation utilities for ParcoRTLS 3D visualization - Updated for new UCS */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/ThreeDZoneViewer/utils */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

/**
 * Coordinate system definitions:
 * 
 * ParcoRTLS: X+ = East, Y+ = North, Z+ = Up (feet)
 * Three.js:  X+ = East, Y+ = Up,    Z+ = South (meters or feet)
 * Leaflet:   X+ = East, Y+ = North (lat/lng degrees)
 * 
 * Map bounds format: [[min_lat, min_lng], [max_lat, max_lng]]
 * Region bounds: {n_min_x, n_min_y, n_min_z, n_max_x, n_max_y, n_max_z}
 */

/**
 * Convert ParcoRTLS coordinates to Three.js coordinates
 * DEPRECATED: Use mapCoordinateSystem.parcoToThreeJs for new code
 * This function maintains backward compatibility
 */
export const parcoToThreeJs = (x, y, z = 0, mapBounds = null) => {
  if (mapBounds) {
    // Use new coordinate system with UCS translation
    const translatedX = x - mapBounds.minX;
    const translatedY = y - mapBounds.minY;  
    const translatedZ = z - mapBounds.minZ;
    
    return {
      x: translatedY,  // Parco Y → Three X
      y: translatedZ,  // Parco Z → Three Y
      z: translatedX   // Parco X → Three Z
    };
  }
  
  // Legacy behavior for backward compatibility
  return {
    x: x,        // X stays the same (East)
    y: z,        // Z becomes Y (Up)
    z: -y        // Y becomes -Z (North becomes South in Three.js)
  };
};

/**
 * Convert Three.js coordinates to ParcoRTLS coordinates
 */
export const threeJsToParco = (x, y, z) => {
  return {
    x: x,        // X stays the same (East)
    y: -z,       // -Z becomes Y (South becomes North)
    z: y         // Y becomes Z (Up)
  };
};

/**
 * Convert map bounds to Three.js coordinate system
 */
export const mapBoundsToThreeJs = (bounds) => {
  if (!bounds || !Array.isArray(bounds) || bounds.length !== 2) {
    console.warn('Invalid map bounds format:', bounds);
    return { minX: 0, minY: 0, minZ: 0, maxX: 100, maxY: 10, maxZ: 100 };
  }

  // Bounds format: [[min_lat, min_lng], [max_lat, max_lng]]
  // In ParcoRTLS: min_lat = min_y, min_lng = min_x
  const minX = bounds[0][1];  // min_lng
  const minY = bounds[0][0];  // min_lat  
  const maxX = bounds[1][1];  // max_lng
  const maxY = bounds[1][0];  // max_lat

  // Convert to Three.js coordinate system
  return {
    minX: minX,
    minY: 0,        // Ground level
    minZ: -maxY,    // North becomes negative Z
    maxX: maxX,
    maxY: 10,       // Default height
    maxZ: -minY     // South becomes positive Z
  };
};

/**
 * Convert region bounds to Three.js coordinate system
 */
export const regionBoundsToThreeJs = (region) => {
  if (!region) {
    return { minX: 0, minY: 0, minZ: 0, maxX: 10, maxY: 10, maxZ: 10 };
  }

  const minX = region.n_min_x || 0;
  const minY = region.n_min_y || 0;
  const minZ = region.n_min_z || 0;
  const maxX = region.n_max_x || 10;
  const maxY = region.n_max_y || 10;
  const maxZ = region.n_max_z || 10;

  return {
    minX: minX,
    minY: minZ,     // Z becomes Y (height)
    minZ: -maxY,    // Y becomes -Z (North to South)
    maxX: maxX,
    maxY: maxZ,     // Z becomes Y (height)
    maxZ: -minY     // Y becomes -Z (North to South)
  };
};

/**
 * Convert vertices array to Three.js coordinates
 */
export const verticesToThreeJs = (vertices) => {
  if (!Array.isArray(vertices)) return [];
  
  return vertices.map(vertex => ({
    ...vertex,
    ...parcoToThreeJs(vertex.n_x || 0, vertex.n_y || 0, vertex.n_z || 0),
    originalX: vertex.n_x,
    originalY: vertex.n_y,
    originalZ: vertex.n_z,
    order: vertex.n_ord || 0
  }));
};

/**
 * Calculate center point of bounds
 */
export const getBoundsCenter = (bounds, coordinateSystem = 'parco') => {
  if (coordinateSystem === 'threejs') {
    return {
      x: (bounds.minX + bounds.maxX) / 2,
      y: (bounds.minY + bounds.maxY) / 2,
      z: (bounds.minZ + bounds.maxZ) / 2
    };
  }
  
  // ParcoRTLS bounds
  return {
    x: (bounds.n_min_x + bounds.n_max_x) / 2,
    y: (bounds.n_min_y + bounds.n_max_y) / 2,
    z: (bounds.n_min_z + bounds.n_max_z) / 2
  };
};

/**
 * Calculate bounds size
 */
export const getBoundsSize = (bounds, coordinateSystem = 'parco') => {
  if (coordinateSystem === 'threejs') {
    return {
      width: Math.abs(bounds.maxX - bounds.minX),
      height: Math.abs(bounds.maxY - bounds.minY),
      depth: Math.abs(bounds.maxZ - bounds.minZ)
    };
  }
  
  // ParcoRTLS bounds
  return {
    width: Math.abs(bounds.n_max_x - bounds.n_min_x),
    height: Math.abs(bounds.n_max_z - bounds.n_min_z), // Z is height
    depth: Math.abs(bounds.n_max_y - bounds.n_min_y)   // Y is depth
  };
};

/**
 * Normalize coordinates to 0-1 range within bounds
 */
export const normalizeCoordinates = (x, y, z, bounds) => {
  const size = getBoundsSize(bounds);
  const center = getBoundsCenter(bounds);
  
  return {
    x: size.width > 0 ? (x - bounds.n_min_x) / size.width : 0,
    y: size.depth > 0 ? (y - bounds.n_min_y) / size.depth : 0,
    z: size.height > 0 ? (z - bounds.n_min_z) / size.height : 0
  };
};

/**
 * Denormalize coordinates from 0-1 range to actual bounds
 */
export const denormalizeCoordinates = (x, y, z, bounds) => {
  const size = getBoundsSize(bounds);
  
  return {
    x: bounds.n_min_x + (x * size.width),
    y: bounds.n_min_y + (y * size.depth),
    z: bounds.n_min_z + (z * size.height)
  };
};

/**
 * Scale coordinates between different coordinate systems
 */
export const scaleCoordinates = (coords, fromBounds, toBounds) => {
  // Normalize to 0-1 range in source bounds
  const normalized = normalizeCoordinates(coords.x, coords.y, coords.z, fromBounds);
  
  // Denormalize to target bounds
  return denormalizeCoordinates(normalized.x, normalized.y, normalized.z, toBounds);
};

/**
 * Calculate distance between two points
 */
export const calculateDistance = (point1, point2) => {
  const dx = point2.x - point1.x;
  const dy = point2.y - point1.y;
  const dz = (point2.z || 0) - (point1.z || 0);
  
  return Math.sqrt(dx * dx + dy * dy + dz * dz);
};

/**
 * Calculate 2D distance (ignoring Z axis)
 */
export const calculateDistance2D = (point1, point2) => {
  const dx = point2.x - point1.x;
  const dy = point2.y - point1.y;
  
  return Math.sqrt(dx * dx + dy * dy);
};

/**
 * Check if point is within bounds
 */
export const isPointInBounds = (point, bounds) => {
  return point.x >= bounds.n_min_x &&
         point.x <= bounds.n_max_x &&
         point.y >= bounds.n_min_y &&
         point.y <= bounds.n_max_y &&
         (point.z || 0) >= (bounds.n_min_z || -Infinity) &&
         (point.z || 0) <= (bounds.n_max_z || Infinity);
};

/**
 * Create bounding box from points
 */
export const createBoundsFromPoints = (points) => {
  if (!points || points.length === 0) {
    return {
      n_min_x: 0, n_min_y: 0, n_min_z: 0,
      n_max_x: 0, n_max_y: 0, n_max_z: 0
    };
  }
  
  let minX = Infinity, minY = Infinity, minZ = Infinity;
  let maxX = -Infinity, maxY = -Infinity, maxZ = -Infinity;
  
  points.forEach(point => {
    minX = Math.min(minX, point.x || point.n_x || 0);
    minY = Math.min(minY, point.y || point.n_y || 0);
    minZ = Math.min(minZ, point.z || point.n_z || 0);
    maxX = Math.max(maxX, point.x || point.n_x || 0);
    maxY = Math.max(maxY, point.y || point.n_y || 0);
    maxZ = Math.max(maxZ, point.z || point.n_z || 0);
  });
  
  return {
    n_min_x: minX, n_min_y: minY, n_min_z: minZ,
    n_max_x: maxX, n_max_y: maxY, n_max_z: maxZ
  };
};

/**
 * Expand bounds by a margin
 */
export const expandBounds = (bounds, margin) => {
  const marginX = typeof margin === 'object' ? margin.x : margin;
  const marginY = typeof margin === 'object' ? margin.y : margin;
  const marginZ = typeof margin === 'object' ? margin.z : margin;
  
  return {
    n_min_x: bounds.n_min_x - marginX,
    n_min_y: bounds.n_min_y - marginY,
    n_min_z: bounds.n_min_z - marginZ,
    n_max_x: bounds.n_max_x + marginX,
    n_max_y: bounds.n_max_y + marginY,
    n_max_z: bounds.n_max_z + marginZ
  };
};

/**
 * Merge multiple bounds into one encompassing bounds
 */
export const mergeBounds = (boundsArray) => {
  if (!boundsArray || boundsArray.length === 0) {
    return {
      n_min_x: 0, n_min_y: 0, n_min_z: 0,
      n_max_x: 0, n_max_y: 0, n_max_z: 0
    };
  }
  
  let minX = Infinity, minY = Infinity, minZ = Infinity;
  let maxX = -Infinity, maxY = -Infinity, maxZ = -Infinity;
  
  boundsArray.forEach(bounds => {
    minX = Math.min(minX, bounds.n_min_x || 0);
    minY = Math.min(minY, bounds.n_min_y || 0);
    minZ = Math.min(minZ, bounds.n_min_z || 0);
    maxX = Math.max(maxX, bounds.n_max_x || 0);
    maxY = Math.max(maxY, bounds.n_max_y || 0);
    maxZ = Math.max(maxZ, bounds.n_max_z || 0);
  });
  
  return {
    n_min_x: minX, n_min_y: minY, n_min_z: minZ,
    n_max_x: maxX, n_max_y: maxY, n_max_z: maxZ
  };
};

/**
 * Convert degrees to radians
 */
export const degreesToRadians = (degrees) => {
  return degrees * (Math.PI / 180);
};

/**
 * Convert radians to degrees
 */
export const radiansToDegrees = (radians) => {
  return radians * (180 / Math.PI);
};

/**
 * Rotate point around origin
 */
export const rotatePoint = (point, angle, origin = { x: 0, y: 0 }) => {
  const cos = Math.cos(angle);
  const sin = Math.sin(angle);
  
  const dx = point.x - origin.x;
  const dy = point.y - origin.y;
  
  return {
    x: origin.x + (dx * cos - dy * sin),
    y: origin.y + (dx * sin + dy * cos),
    z: point.z || 0
  };
};

/**
 * Interpolate between two points
 */
export const interpolatePoints = (point1, point2, t) => {
  return {
    x: point1.x + (point2.x - point1.x) * t,
    y: point1.y + (point2.y - point1.y) * t,
    z: (point1.z || 0) + ((point2.z || 0) - (point1.z || 0)) * t
  };
};

/**
 * Validate coordinate data
 */
export const validateCoordinates = (coords) => {
  if (!coords || typeof coords !== 'object') {
    return { valid: false, error: 'Coordinates must be an object' };
  }
  
  if (typeof coords.x !== 'number' || isNaN(coords.x)) {
    return { valid: false, error: 'X coordinate must be a valid number' };
  }
  
  if (typeof coords.y !== 'number' || isNaN(coords.y)) {
    return { valid: false, error: 'Y coordinate must be a valid number' };
  }
  
  if (coords.z !== undefined && (typeof coords.z !== 'number' || isNaN(coords.z))) {
    return { valid: false, error: 'Z coordinate must be a valid number or undefined' };
  }
  
  return { valid: true };
};

/**
 * Validate bounds data
 */
export const validateBounds = (bounds) => {
  if (!bounds || typeof bounds !== 'object') {
    return { valid: false, error: 'Bounds must be an object' };
  }
  
  const required = ['n_min_x', 'n_min_y', 'n_max_x', 'n_max_y'];
  
  for (const prop of required) {
    if (typeof bounds[prop] !== 'number' || isNaN(bounds[prop])) {
      return { valid: false, error: `Bounds property ${prop} must be a valid number` };
    }
  }
  
  if (bounds.n_min_x >= bounds.n_max_x) {
    return { valid: false, error: 'n_min_x must be less than n_max_x' };
  }
  
  if (bounds.n_min_y >= bounds.n_max_y) {
    return { valid: false, error: 'n_min_y must be less than n_max_y' };
  }
  
  return { valid: true };
};

export default {
  parcoToThreeJs,
  threeJsToParco,
  mapBoundsToThreeJs,
  regionBoundsToThreeJs,
  verticesToThreeJs,
  getBoundsCenter,
  getBoundsSize,
  normalizeCoordinates,
  denormalizeCoordinates,
  scaleCoordinates,
  calculateDistance,
  calculateDistance2D,
  isPointInBounds,
  createBoundsFromPoints,
  expandBounds,
  mergeBounds,
  degreesToRadians,
  radiansToDegrees,
  rotatePoint,
  interpolatePoints,
  validateCoordinates,
  validateBounds
};