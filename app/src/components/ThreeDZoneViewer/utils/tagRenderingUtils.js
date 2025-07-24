/* Name: tagRenderingUtils.js */
/* Version: 0.1.2 */
/* Created: 250722 */
/* Modified: 250722 */
/* Creator: ParcoAdmin + Claude */
/* Modified By: ParcoAdmin + Claude */
/* Description: ACTUAL HEIGHT FIX - Use real z-coordinate from ParcoRTLS instead of fixed offset */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/ThreeDZoneViewer/utils */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */
/* Changelog: */
/* - 0.1.2: ACTUAL HEIGHT FIX - Use real z-coordinate from ParcoRTLS data, added useActualHeight flag */
/* - 0.1.1: VECTOR3 BUG FIX - Fixed .clone() error by converting positions to THREE.Vector3 objects */
/* - 0.1.0: Initial version - 3D tag objects, coordinate conversion, configurable appearance */

import * as THREE from 'three';
import { parcoToThreeJs } from './mapCoordinateSystem';

/**
 * Default tag appearance configuration
 */
export const DEFAULT_TAG_CONFIG = {
  // Tag sphere settings
  sphereRadius: 3,
  sphereSegments: 12,
  
  // Tag colors
  activeColor: 0x00ff00,      // Green for active tags
  inactiveColor: 0x888888,    // Gray for inactive tags
  selectedColor: 0xff4444,    // Red for selected tags
  
  // Label settings
  showLabels: true,
  labelSize: 8,
  labelOffset: 6,
  labelBackground: '#000000',
  labelText: '#ffffff',
  
  // Trail settings
  showTrails: false,
  trailLength: 10,
  trailColor: 0x4444ff,
  trailOpacity: 0.6,
  
  // Animation settings
  animateUpdates: true,
  animationDuration: 500,
  
  // Height settings - CHANGED v0.1.2
  useActualHeight: true,      // NEW: Use real z-coordinate from ParcoRTLS
  heightOffset: 5,            // Only used when useActualHeight is false
  minHeightAboveGround: 2     // NEW: Minimum height above ground level (safety margin)
};

/**
 * Create a 3D tag sphere object
 * 
 * @param {Object} tagData - Tag position and metadata
 * @param {Object} mapBounds - Map coordinate bounds
 * @param {Object} config - Tag appearance configuration
 * @returns {THREE.Group} - Tag group containing sphere and optional label
 */
export const createTag3D = (tagData, mapBounds, config = DEFAULT_TAG_CONFIG) => {
  console.log(`🏷️ Creating 3D tag for ${tagData.id}:`, {
    position: { x: tagData.x, y: tagData.y, z: tagData.z },
    useActualHeight: config.useActualHeight,
    mapBounds: { 
      minX: mapBounds.minX, 
      maxX: mapBounds.maxX, 
      minY: mapBounds.minY, 
      maxY: mapBounds.maxY 
    }
  });

  // Convert Parco coordinates to Three.js coordinates
  const threePosition = parcoToThreeJs(tagData.x, tagData.y, tagData.z || 0, mapBounds);
  
  // CHANGED v0.1.2: Apply height based on configuration
  if (config.useActualHeight) {
    // Use actual z-coordinate from ParcoRTLS data
    const actualHeight = tagData.z || 0;
    threePosition.y = actualHeight + config.minHeightAboveGround;
    console.log(`📏 Tag ${tagData.id} using actual height: ParcoZ=${actualHeight}, ThreeY=${threePosition.y}`);
  } else {
    // Use fixed height offset (legacy behavior)
    threePosition.y += config.heightOffset;
    console.log(`📏 Tag ${tagData.id} using fixed offset: ThreeY=${threePosition.y}`);
  }
  
  // Ensure it's a proper THREE.Vector3 object
  const position = new THREE.Vector3(threePosition.x, threePosition.y, threePosition.z);
  
  console.log(`📍 Tag ${tagData.id} converted position:`, {
    parco: { x: tagData.x, y: tagData.y, z: tagData.z },
    three: { x: position.x.toFixed(2), y: position.y.toFixed(2), z: position.z.toFixed(2) },
    heightMode: config.useActualHeight ? 'actual' : 'fixed'
  });

  // Create tag group
  const tagGroup = new THREE.Group();
  tagGroup.userData.isTag = true;
  tagGroup.userData.tagId = tagData.id;
  tagGroup.userData.tagData = tagData;
  tagGroup.userData.renderType = 'tag3D';

  // Create tag sphere
  const sphereGeometry = new THREE.SphereGeometry(
    config.sphereRadius, 
    config.sphereSegments, 
    config.sphereSegments
  );
  
  const sphereMaterial = new THREE.MeshBasicMaterial({
    color: config.activeColor,
    transparent: true,
    opacity: 0.8
  });
  
  const tagSphere = new THREE.Mesh(sphereGeometry, sphereMaterial);
  tagSphere.position.copy(position);
  tagSphere.userData.isTagSphere = true;
  tagSphere.userData.tagId = tagData.id;
  
  tagGroup.add(tagSphere);

  // Create label if enabled
  if (config.showLabels) {
    const labelMesh = createTagLabel(tagData.id, position, config);
    if (labelMesh) {
      tagGroup.add(labelMesh);
    }
  }

  // Position the entire group
  tagGroup.position.set(0, 0, 0); // Individual components have their positions set

  console.log(`✅ Created 3D tag ${tagData.id} at Three.js position (${position.x.toFixed(2)}, ${position.y.toFixed(2)}, ${position.z.toFixed(2)})`);
  
  return tagGroup;
};

/**
 * Create a text label for a tag
 * 
 * @param {string} tagId - Tag identifier 
 * @param {THREE.Vector3} position - 3D position for label
 * @param {Object} config - Label configuration
 * @returns {THREE.Mesh} - Label mesh
 */
export const createTagLabel = (tagId, position, config = DEFAULT_TAG_CONFIG) => {
  try {
    // Create canvas for text rendering
    const canvas = document.createElement('canvas');
    canvas.width = 128;
    canvas.height = 32;
    const context = canvas.getContext('2d');
    
    // Clear canvas
    context.fillStyle = config.labelBackground;
    context.fillRect(0, 0, canvas.width, canvas.height);
    
    // Draw text
    context.fillStyle = config.labelText;
    context.font = `bold ${config.labelSize}px Arial`;
    context.textAlign = 'center';
    context.textBaseline = 'middle';
    context.fillText(tagId, canvas.width / 2, canvas.height / 2);
    
    // Create texture from canvas
    const texture = new THREE.CanvasTexture(canvas);
    texture.needsUpdate = true;
    
    // Create label geometry and material
    const labelGeometry = new THREE.PlaneGeometry(12, 3);
    const labelMaterial = new THREE.MeshBasicMaterial({
      map: texture,
      transparent: true,
      opacity: 0.9,
      depthTest: false // Always render on top
    });
    
    // Create label mesh
    const labelMesh = new THREE.Mesh(labelGeometry, labelMaterial);
    labelMesh.position.set(
      position.x,
      position.y + config.labelOffset,
      position.z
    );
    
    // Make label face camera (billboard effect)
    labelMesh.lookAt(0, position.y + config.labelOffset, 100);
    
    // Set user data
    labelMesh.userData.isTagLabel = true;
    labelMesh.userData.tagId = tagId;
    
    console.log(`🏷️ Created label for tag ${tagId}`);
    return labelMesh;
    
  } catch (error) {
    console.error(`❌ Error creating label for tag ${tagId}:`, error);
    return null;
  }
};

/**
 * Update tag position with optional animation
 * 
 * @param {THREE.Group} tagGroup - Tag group object
 * @param {Object} newTagData - Updated tag data
 * @param {Object} mapBounds - Map coordinate bounds
 * @param {Object} config - Animation configuration
 */
export const updateTagPosition = (tagGroup, newTagData, mapBounds, config = DEFAULT_TAG_CONFIG) => {
  if (!tagGroup || !tagGroup.userData.isTag) {
    console.warn(`⚠️ Invalid tag group for update`);
    return;
  }

  // Convert new position
  const newThreePosition = parcoToThreeJs(newTagData.x, newTagData.y, newTagData.z || 0, mapBounds);
  
  // CHANGED v0.1.2: Apply height based on configuration
  if (config.useActualHeight) {
    // Use actual z-coordinate from ParcoRTLS data
    const actualHeight = newTagData.z || 0;
    newThreePosition.y = actualHeight + config.minHeightAboveGround;
    console.log(`📏 Tag ${newTagData.id} updating to actual height: ParcoZ=${actualHeight}, ThreeY=${newThreePosition.y}`);
  } else {
    // Use fixed height offset (legacy behavior)
    newThreePosition.y += config.heightOffset;
    console.log(`📏 Tag ${newTagData.id} updating to fixed offset: ThreeY=${newThreePosition.y}`);
  }

  // Ensure it's a proper THREE.Vector3 object
  const newPosition = new THREE.Vector3(newThreePosition.x, newThreePosition.y, newThreePosition.z);

  console.log(`🔄 Updating tag ${newTagData.id} position:`, {
    old: tagGroup.userData.tagData ? 
      `(${tagGroup.userData.tagData.x}, ${tagGroup.userData.tagData.y}, ${tagGroup.userData.tagData.z})` : 'N/A',
    new: `(${newTagData.x}, ${newTagData.y}, ${newTagData.z})`,
    threeJs: `(${newPosition.x.toFixed(2)}, ${newPosition.y.toFixed(2)}, ${newPosition.z.toFixed(2)})`,
    heightMode: config.useActualHeight ? 'actual' : 'fixed'
  });

  // Update tag data
  tagGroup.userData.tagData = newTagData;

  // Find sphere and label in the group
  const tagSphere = tagGroup.children.find(child => child.userData.isTagSphere);
  const tagLabel = tagGroup.children.find(child => child.userData.isTagLabel);

  if (config.animateUpdates) {
    // Animate position change
    animateTagPosition(tagSphere, newPosition, config.animationDuration);
    if (tagLabel) {
      const labelPosition = newPosition.clone();
      labelPosition.y += config.labelOffset;
      animateTagPosition(tagLabel, labelPosition, config.animationDuration);
    }
  } else {
    // Instant position update
    if (tagSphere) {
      tagSphere.position.copy(newPosition);
    }
    if (tagLabel) {
      tagLabel.position.set(
        newPosition.x,
        newPosition.y + config.labelOffset,
        newPosition.z
      );
    }
  }

  console.log(`✅ Updated tag ${newTagData.id} to position (${newPosition.x.toFixed(2)}, ${newPosition.y.toFixed(2)}, ${newPosition.z.toFixed(2)})`);
};

/**
 * Animate tag position change
 * 
 * @param {THREE.Object3D} object - Object to animate
 * @param {THREE.Vector3} targetPosition - Target position
 * @param {number} duration - Animation duration in ms
 */
const animateTagPosition = (object, targetPosition, duration = 500) => {
  if (!object) return;

  const startPosition = object.position.clone();
  const startTime = Date.now();

  const animate = () => {
    const elapsed = Date.now() - startTime;
    const progress = Math.min(elapsed / duration, 1);

    // Smooth easing function
    const easeProgress = 1 - Math.pow(1 - progress, 3);

    // Interpolate position
    object.position.lerpVectors(startPosition, targetPosition, easeProgress);

    if (progress < 1) {
      requestAnimationFrame(animate);
    }
  };

  animate();
};

/**
 * Create tag trail/history visualization
 * 
 * @param {Array} tagHistory - Array of historical positions
 * @param {Object} mapBounds - Map coordinate bounds  
 * @param {Object} config - Trail configuration
 * @returns {THREE.Line} - Trail line object
 */
export const createTagTrail = (tagHistory, mapBounds, config = DEFAULT_TAG_CONFIG) => {
  if (!tagHistory || tagHistory.length < 2) {
    return null;
  }

  console.log(`🛤️ Creating trail with ${tagHistory.length} points`);

  // Convert history positions to Three.js coordinates
  const points = tagHistory.map(historyPoint => {
    const threePos = parcoToThreeJs(historyPoint.x, historyPoint.y, historyPoint.z || 0, mapBounds);
    
    // CHANGED v0.1.2: Apply height based on configuration for trails too
    if (config.useActualHeight) {
      const actualHeight = historyPoint.z || 0;
      threePos.y = actualHeight + config.minHeightAboveGround;
    } else {
      threePos.y += config.heightOffset;
    }
    
    // Ensure it's a proper THREE.Vector3 object
    return new THREE.Vector3(threePos.x, threePos.y, threePos.z);
  });

  // Create line geometry
  const geometry = new THREE.BufferGeometry().setFromPoints(points);
  
  // Create line material with opacity gradient
  const material = new THREE.LineBasicMaterial({
    color: config.trailColor,
    transparent: true,
    opacity: config.trailOpacity,
    linewidth: 2
  });

  // Create line object
  const trailLine = new THREE.Line(geometry, material);
  trailLine.userData.isTagTrail = true;
  trailLine.userData.trailLength = tagHistory.length;

  console.log(`✅ Created trail with ${points.length} points using ${config.useActualHeight ? 'actual' : 'fixed'} height`);
  return trailLine;
};

/**
 * Update tag appearance (color, size, etc.)
 * 
 * @param {THREE.Group} tagGroup - Tag group object
 * @param {Object} appearance - Appearance settings
 */
export const updateTagAppearance = (tagGroup, appearance) => {
  if (!tagGroup || !tagGroup.userData.isTag) {
    console.warn(`⚠️ Invalid tag group for appearance update`);
    return;
  }

  const tagSphere = tagGroup.children.find(child => child.userData.isTagSphere);
  if (!tagSphere) return;

  // Update color
  if (appearance.color !== undefined) {
    tagSphere.material.color.setHex(appearance.color);
  }

  // Update opacity
  if (appearance.opacity !== undefined) {
    tagSphere.material.opacity = appearance.opacity;
  }

  // Update scale
  if (appearance.scale !== undefined) {
    tagSphere.scale.setScalar(appearance.scale);
  }

  console.log(`🎨 Updated tag ${tagGroup.userData.tagId} appearance:`, appearance);
};

/**
 * Remove all tag objects from scene
 * 
 * @param {THREE.Scene} scene - Three.js scene
 */
export const clearAllTags = (scene) => {
  const tagsToRemove = [];
  
  scene.traverse((object) => {
    if (object.userData.isTag || object.userData.isTagTrail) {
      tagsToRemove.push(object);
    }
  });

  tagsToRemove.forEach(tag => {
    scene.remove(tag);
    // Dispose of geometries and materials
    if (tag.geometry) tag.geometry.dispose();
    if (tag.material) {
      if (tag.material.map) tag.material.map.dispose();
      tag.material.dispose();
    }
  });

  console.log(`🧹 Cleared ${tagsToRemove.length} tag objects from scene`);
};

/**
 * Get all tag objects in scene
 * 
 * @param {THREE.Scene} scene - Three.js scene
 * @returns {Array} - Array of tag objects
 */
export const getAllTagsInScene = (scene) => {
  const tags = [];
  
  scene.traverse((object) => {
    if (object.userData.isTag) {
      tags.push(object);
    }
  });

  return tags;
};

/**
 * Check if position is within map bounds
 * 
 * @param {number} x - X coordinate
 * @param {number} y - Y coordinate  
 * @param {Object} mapBounds - Map bounds
 * @returns {boolean} - True if within bounds
 */
export const isPositionWithinBounds = (x, y, mapBounds) => {
  return x >= mapBounds.minX && 
         x <= mapBounds.maxX && 
         y >= mapBounds.minY && 
         y <= mapBounds.maxY;
};

console.log(`🏷️ tagRenderingUtils v0.1.2 loaded - 3D tag rendering with actual height support ready for deployment`);

export default {
  DEFAULT_TAG_CONFIG,
  createTag3D,
  createTagLabel,
  updateTagPosition,
  createTagTrail,
  updateTagAppearance,
  clearAllTags,
  getAllTagsInScene,
  isPositionWithinBounds
};