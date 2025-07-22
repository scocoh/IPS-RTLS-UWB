/* Name: sceneUtilities.js */
/* Version: 0.1.2 */
/* Created: 250719 */
/* Modified: 250721 */
/* Creator: ParcoAdmin + Claude */
/* Modified By: ParcoAdmin + Claude */
/* Description: Three.js scene utilities and helpers with shadowless uniform lighting */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/ThreeDZoneViewer/utils */
/* Role: Frontend Utility */
/* Status: Active */
/* Dependent: TRUE */

import * as THREE from 'three';

// Function to create text sprite with larger font
export const createTextSprite = (message, x, y, z) => {
  const canvas = document.createElement('canvas');
  const context = canvas.getContext('2d');
  context.font = '16px Arial'; // Increased from 12px to 16px
  const metrics = context.measureText(message);
  const textWidth = metrics.width;
  canvas.width = textWidth + 8; // Increased padding
  canvas.height = 24; // Increased height for larger font

  context.fillStyle = 'rgba(0, 0, 0, 0.8)';
  context.fillRect(0, 0, canvas.width, canvas.height);
  context.fillStyle = 'white';
  context.textAlign = 'center';
  context.font = '16px Arial'; // Re-apply font after canvas resize
  context.fillText(message, canvas.width / 2, 18); // Adjusted Y position

  const texture = new THREE.Texture(canvas);
  texture.needsUpdate = true;
  const spriteMaterial = new THREE.SpriteMaterial({ map: texture });
  const sprite = new THREE.Sprite(spriteMaterial);
  sprite.position.set(x, y + 3, z); // Increased offset to avoid obscuring sphere
  sprite.scale.set(15, 8, 1); // Increased scale for larger visibility
  return sprite;
};

// Function to center camera on added zones
export const centerCameraOnZones = (scene, camera, controls) => {
  const box = new THREE.Box3();
  scene.traverse((object) => {
    if (object.userData.isRealZone) {
      box.expandByObject(object);
    }
  });

  if (!box.isEmpty()) {
    const center = box.getCenter(new THREE.Vector3());
    const size = box.getSize(new THREE.Vector3());
    const maxDim = Math.max(size.x, size.y, size.z);
    const fov = camera.fov * (Math.PI / 180);
    let cameraZ = Math.abs(maxDim / 2 / Math.tan(fov / 2)) * 1.5;

    camera.position.set(center.x, center.y + cameraZ, center.z + cameraZ);
    camera.lookAt(center);

    if (controls && controls.target) {
      controls.target.copy(center);
      controls.update();
    }

    console.log(`📷 Camera centered on zones at ${center.x},${center.y},${center.z}, distance: ${cameraZ}`);
  }
};

// Function to clear objects by type
export const clearSceneObjects = (scene, userDataKey) => {
  const objectsToRemove = [];
  scene.traverse((object) => {
    if (object.userData[userDataKey]) {
      objectsToRemove.push(object);
    }
  });
  objectsToRemove.forEach(obj => scene.remove(obj));
  console.log(`🧹 Cleared ${objectsToRemove.length} objects with userData.${userDataKey}`);
};

// Function to setup enhanced scene lighting - NO SHADOWS, UNIFORM ILLUMINATION
export const setupSceneLighting = (scene) => {
  // Strong ambient light for uniform base illumination from all directions
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.8);
  scene.add(ambientLight);

  // Multiple directional lights from different angles - NO SHADOWS
  // Front-top light
  const frontLight = new THREE.DirectionalLight(0xffffff, 0.6);
  frontLight.position.set(100, 100, 100);
  frontLight.castShadow = false; // Disabled for uniform lighting
  scene.add(frontLight);

  // Back-top light
  const backLight = new THREE.DirectionalLight(0xffffff, 0.6);
  backLight.position.set(-100, 100, -100);
  backLight.castShadow = false; // Disabled for uniform lighting
  scene.add(backLight);

  // Side lights for complete coverage
  const leftLight = new THREE.DirectionalLight(0xffffff, 0.4);
  leftLight.position.set(-100, 50, 0);
  leftLight.castShadow = false; // Disabled for uniform lighting
  scene.add(leftLight);

  const rightLight = new THREE.DirectionalLight(0xffffff, 0.4);
  rightLight.position.set(100, 50, 0);
  rightLight.castShadow = false; // Disabled for uniform lighting
  scene.add(rightLight);

  // Enhanced hemisphere light for natural sky/ground gradient
  const hemiLight = new THREE.HemisphereLight(0xffffff, 0xcccccc, 0.6);
  hemiLight.position.set(0, 200, 0);
  scene.add(hemiLight);

  console.log('💡 Enhanced shadowless lighting setup complete - uniform illumination from all angles');
};

// Function to setup scene helpers (grid, axes)
export const setupSceneHelpers = (scene) => {
  // Add grid helper
  const gridHelper = new THREE.GridHelper(100, 20, 0x888888, 0xcccccc);
  scene.add(gridHelper);

  // Add axis helper
  const axesHelper = new THREE.AxesHelper(20);
  scene.add(axesHelper);

  console.log('📐 Scene helpers setup complete');
};