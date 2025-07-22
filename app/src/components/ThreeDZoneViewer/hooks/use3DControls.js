/* Name: use3DControls.js */
/* Version: 0.1.0 */
/* Created: 250719 */
/* Modified: 250719 */
/* Creator: ParcoAdmin + Claude */
/* Modified By: ParcoAdmin + Claude */
/* Description: Hook for managing 3D camera controls and view states */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/ThreeDZoneViewer/hooks */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

import { useState, useCallback } from 'react';
import * as THREE from 'three';

const use3DControls = ({ 
  cameraRef, 
  sceneRef,
  mapData = null 
}) => {
  const [currentView, setCurrentView] = useState('isometric');
  const [isAnimating, setIsAnimating] = useState(false);

  // Smooth camera animation
  const animateCamera = useCallback((targetPosition, targetLookAt, duration = 1000) => {
    if (!cameraRef.current || isAnimating) return;

    setIsAnimating(true);
    const camera = cameraRef.current;
    
    const startPosition = camera.position.clone();
    const startRotation = camera.rotation.clone();
    
    // Calculate target rotation by looking at target
    const tempCamera = camera.clone();
    tempCamera.position.copy(targetPosition);
    tempCamera.lookAt(targetLookAt);
    const targetRotation = tempCamera.rotation.clone();

    const startTime = Date.now();

    const animate = () => {
      const elapsed = Date.now() - startTime;
      const progress = Math.min(elapsed / duration, 1);
      
      // Easing function (ease out cubic)
      const eased = 1 - Math.pow(1 - progress, 3);

      // Interpolate position
      camera.position.lerpVectors(startPosition, targetPosition, eased);
      
      // Interpolate rotation
      camera.rotation.x = startRotation.x + (targetRotation.x - startRotation.x) * eased;
      camera.rotation.y = startRotation.y + (targetRotation.y - startRotation.y) * eased;
      camera.rotation.z = startRotation.z + (targetRotation.z - startRotation.z) * eased;

      if (progress < 1) {
        requestAnimationFrame(animate);
      } else {
        // Ensure exact final position
        camera.position.copy(targetPosition);
        camera.lookAt(targetLookAt);
        setIsAnimating(false);
        console.log('📷 Camera animation completed');
      }
    };

    requestAnimationFrame(animate);
  }, [cameraRef, isAnimating]);

  // Calculate scene bounds for auto-fitting
  const getSceneBounds = useCallback(() => {
    if (!sceneRef.current) return null;

    const box = new THREE.Box3();
    const objects = [];
    
    sceneRef.current.traverse((object) => {
      if (object.userData.isZone || object.userData.isMapPlane) {
        objects.push(object);
      }
    });

    if (objects.length === 0) {
      // Fallback to map data if available
      if (mapData?.bounds) {
        const minX = mapData.bounds[0][1];
        const minY = mapData.bounds[0][0]; 
        const maxX = mapData.bounds[1][1];
        const maxY = mapData.bounds[1][0];
        
        box.min.set(minX, -10, minY);
        box.max.set(maxX, 50, maxY);
      } else {
        // Default bounds
        box.min.set(-100, -10, -100);
        box.max.set(100, 50, 100);
      }
    } else {
      objects.forEach(obj => box.expandByObject(obj));
    }

    return box;
  }, [sceneRef, mapData]);

  // View preset functions
  const resetView = useCallback(() => {
    if (!cameraRef.current) return;
    
    const bounds = getSceneBounds();
    if (!bounds) return;

    const center = bounds.getCenter(new THREE.Vector3());
    const size = bounds.getSize(new THREE.Vector3());
    const maxDim = Math.max(size.x, size.y, size.z);
    
    const distance = maxDim * 1.5;
    const targetPosition = new THREE.Vector3(
      center.x + distance * 0.7,
      center.y + distance * 0.7,
      center.z + distance * 0.7
    );

    animateCamera(targetPosition, center);
    setCurrentView('isometric');
  }, [cameraRef, getSceneBounds, animateCamera]);

  const topView = useCallback(() => {
    if (!cameraRef.current) return;
    
    const bounds = getSceneBounds();
    if (!bounds) return;

    const center = bounds.getCenter(new THREE.Vector3());
    const size = bounds.getSize(new THREE.Vector3());
    const distance = Math.max(size.x, size.z) * 1.2;
    
    const targetPosition = new THREE.Vector3(center.x, center.y + distance, center.z);
    
    animateCamera(targetPosition, center);
    setCurrentView('top');
  }, [cameraRef, getSceneBounds, animateCamera]);

  const frontView = useCallback(() => {
    if (!cameraRef.current) return;
    
    const bounds = getSceneBounds();
    if (!bounds) return;

    const center = bounds.getCenter(new THREE.Vector3());
    const size = bounds.getSize(new THREE.Vector3());
    const distance = Math.max(size.x, size.y) * 1.5;
    
    const targetPosition = new THREE.Vector3(center.x, center.y, center.z + distance);
    
    animateCamera(targetPosition, center);
    setCurrentView('front');
  }, [cameraRef, getSceneBounds, animateCamera]);

  const sideView = useCallback(() => {
    if (!cameraRef.current) return;
    
    const bounds = getSceneBounds();
    if (!bounds) return;

    const center = bounds.getCenter(new THREE.Vector3());
    const size = bounds.getSize(new THREE.Vector3());
    const distance = Math.max(size.y, size.z) * 1.5;
    
    const targetPosition = new THREE.Vector3(center.x + distance, center.y, center.z);
    
    animateCamera(targetPosition, center);
    setCurrentView('side');
  }, [cameraRef, getSceneBounds, animateCamera]);

  const isometricView = useCallback(() => {
    if (!cameraRef.current) return;
    
    const bounds = getSceneBounds();
    if (!bounds) return;

    const center = bounds.getCenter(new THREE.Vector3());
    const size = bounds.getSize(new THREE.Vector3());
    const maxDim = Math.max(size.x, size.y, size.z);
    const distance = maxDim * 1.2;
    
    // Classic isometric angles (30°, 45°)
    const targetPosition = new THREE.Vector3(
      center.x + distance * 0.866, // cos(30°) ≈ 0.866
      center.y + distance * 0.5,   // sin(30°) = 0.5
      center.z + distance * 0.866
    );
    
    animateCamera(targetPosition, center);
    setCurrentView('isometric');
  }, [cameraRef, getSceneBounds, animateCamera]);

  const fitToZones = useCallback(() => {
    if (!cameraRef.current) return;
    
    const bounds = getSceneBounds();
    if (!bounds) return;

    const center = bounds.getCenter(new THREE.Vector3());
    const size = bounds.getSize(new THREE.Vector3());
    
    // Calculate optimal distance based on camera FOV
    const camera = cameraRef.current;
    const fov = camera.fov * (Math.PI / 180); // Convert to radians
    const maxDim = Math.max(size.x, size.z);
    const distance = (maxDim / 2) / Math.tan(fov / 2) * 1.5; // 1.5 for padding
    
    const targetPosition = new THREE.Vector3(
      center.x + distance * 0.7,
      center.y + distance * 0.7,
      center.z + distance * 0.7
    );

    animateCamera(targetPosition, center);
    setCurrentView('fitted');
    console.log(`📏 Fitted camera to zones, distance: ${distance.toFixed(1)}`);
  }, [cameraRef, getSceneBounds, animateCamera]);

  const zoomIn = useCallback(() => {
    if (!cameraRef.current) return;
    
    const camera = cameraRef.current;
    const direction = new THREE.Vector3();
    camera.getWorldDirection(direction);
    
    const zoomDistance = camera.position.length() * 0.1;
    camera.position.add(direction.multiplyScalar(zoomDistance));
    
    console.log('🔍+ Zoomed in');
  }, [cameraRef]);

  const zoomOut = useCallback(() => {
    if (!cameraRef.current) return;
    
    const camera = cameraRef.current;
    const direction = new THREE.Vector3();
    camera.getWorldDirection(direction);
    
    const zoomDistance = camera.position.length() * 0.1;
    camera.position.add(direction.multiplyScalar(-zoomDistance));
    
    console.log('🔍- Zoomed out');
  }, [cameraRef]);

  // Keyboard shortcuts
  const handleKeyPress = useCallback((event) => {
    if (isAnimating) return;

    switch (event.key.toLowerCase()) {
      case '1':
        topView();
        break;
      case '2':
        frontView();
        break;
      case '3':
        sideView();
        break;
      case '4':
        isometricView();
        break;
      case 'r':
        resetView();
        break;
      case 'f':
        fitToZones();
        break;
      case '+':
      case '=':
        zoomIn();
        break;
      case '-':
        zoomOut();
        break;
      default:
        break;
    }
  }, [isAnimating, topView, frontView, sideView, isometricView, resetView, fitToZones, zoomIn, zoomOut]);

  return {
    currentView,
    isAnimating,
    
    // View controls
    resetView,
    topView,
    frontView,
    sideView,
    isometricView,
    fitToZones,
    zoomIn,
    zoomOut,
    
    // Utilities
    handleKeyPress,
    getSceneBounds,
    animateCamera
  };
};

export default use3DControls;