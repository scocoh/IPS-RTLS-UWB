/* Name: useThreeScene.js */
/* Version: 0.1.0 */
/* Created: 250719 */
/* Modified: 250719 */
/* Creator: ParcoAdmin + Claude */
/* Modified By: ParcoAdmin + Claude */
/* Description: Three.js scene setup and management hook */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/ThreeDZoneViewer/hooks */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

import { useRef, useEffect, useState } from 'react';
import * as THREE from 'three';

const useThreeScene = ({ 
  width = 800, 
  height = 500, 
  enableControls = true,
  onZoneClick = null 
}) => {
  const mountRef = useRef(null);
  const sceneRef = useRef(null);
  const rendererRef = useRef(null);
  const cameraRef = useRef(null);
  const frameIdRef = useRef(null);
  const raycasterRef = useRef(null);
  const mouseRef = useRef(new THREE.Vector2());
  
  const [isInitialized, setIsInitialized] = useState(false);
  const [selectedObject, setSelectedObject] = useState(null);

  // Initialize Three.js scene
  useEffect(() => {
    if (!mountRef.current || isInitialized) return;

    console.log('🎮 Initializing Three.js scene');

    // Scene setup
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0xf5f5f5);
    scene.fog = new THREE.Fog(0xf5f5f5, 100, 1000);

    // Camera setup
    const camera = new THREE.PerspectiveCamera(
      60, 
      width / height, 
      0.1, 
      2000
    );
    camera.position.set(200, 150, 200);
    camera.lookAt(0, 0, 0);

    // Renderer setup
    const renderer = new THREE.WebGLRenderer({ 
      antialias: true,
      alpha: true
    });
    renderer.setSize(width, height);
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    renderer.outputColorSpace = THREE.SRGBColorSpace;

    // Add to DOM
    mountRef.current.appendChild(renderer.domElement);

    // Lighting setup
    const ambientLight = new THREE.AmbientLight(0x404040, 0.6);
    scene.add(ambientLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(100, 100, 50);
    directionalLight.castShadow = true;
    directionalLight.shadow.mapSize.width = 2048;
    directionalLight.shadow.mapSize.height = 2048;
    directionalLight.shadow.camera.near = 0.5;
    directionalLight.shadow.camera.far = 500;
    directionalLight.shadow.camera.left = -200;
    directionalLight.shadow.camera.right = 200;
    directionalLight.shadow.camera.top = 200;
    directionalLight.shadow.camera.bottom = -200;
    scene.add(directionalLight);

    // Add hemisphere light for better overall lighting
    const hemiLight = new THREE.HemisphereLight(0xffffff, 0x444444, 0.4);
    hemiLight.position.set(0, 200, 0);
    scene.add(hemiLight);

    // Add grid helper
    const gridHelper = new THREE.GridHelper(500, 25, 0x888888, 0xcccccc);
    gridHelper.position.y = -0.1; // Slightly below ground to avoid z-fighting
    scene.add(gridHelper);

    // Add axis helper
    const axesHelper = new THREE.AxesHelper(50);
    scene.add(axesHelper);

    // Raycaster for object picking
    const raycaster = new THREE.Raycaster();

    // Mouse controls
    let isMouseDown = false;
    let mouseX = 0;
    let mouseY = 0;

    const handleMouseDown = (event) => {
      isMouseDown = true;
      mouseX = event.clientX;
      mouseY = event.clientY;
    };

    const handleMouseUp = (event) => {
      if (!isMouseDown) return;
      
      const deltaX = Math.abs(event.clientX - mouseX);
      const deltaY = Math.abs(event.clientY - mouseY);
      
      // If mouse didn't move much, treat as click
      if (deltaX < 5 && deltaY < 5 && onZoneClick) {
        handleMouseClick(event);
      }
      
      isMouseDown = false;
    };

    const handleMouseMove = (event) => {
      if (!isMouseDown || !enableControls) return;

      const deltaX = event.clientX - mouseX;
      const deltaY = event.clientY - mouseY;

      // Rotate camera around target
      const spherical = new THREE.Spherical();
      spherical.setFromVector3(camera.position);
      spherical.theta -= deltaX * 0.01;
      spherical.phi += deltaY * 0.01;
      spherical.phi = Math.max(0.1, Math.min(Math.PI - 0.1, spherical.phi));

      camera.position.setFromSpherical(spherical);
      camera.lookAt(0, 0, 0);

      mouseX = event.clientX;
      mouseY = event.clientY;
    };

    const handleMouseClick = (event) => {
      if (!onZoneClick) return;

      // Calculate mouse position in normalized device coordinates
      const rect = renderer.domElement.getBoundingClientRect();
      mouseRef.current.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
      mouseRef.current.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

      // Cast ray from camera through mouse position
      raycaster.setFromCamera(mouseRef.current, camera);
      
      // Find intersections with clickable objects
      const clickableObjects = [];
      scene.traverse((object) => {
        if (object.userData.clickable && object.visible) {
          clickableObjects.push(object);
        }
      });

      const intersects = raycaster.intersectObjects(clickableObjects);
      
      if (intersects.length > 0) {
        const clickedObject = intersects[0].object;
        console.log('🖱️ Clicked zone:', clickedObject.userData);
        setSelectedObject(clickedObject);
        onZoneClick(clickedObject.userData);
      } else {
        setSelectedObject(null);
        onZoneClick(null);
      }
    };

    const handleWheel = (event) => {
      if (!enableControls) return;
      
      event.preventDefault();
      const scale = event.deltaY > 0 ? 1.1 : 0.9;
      
      camera.position.multiplyScalar(scale);
      
      // Clamp camera distance
      const distance = camera.position.length();
      if (distance < 50) {
        camera.position.normalize().multiplyScalar(50);
      } else if (distance > 1000) {
        camera.position.normalize().multiplyScalar(1000);
      }
    };

    // Add event listeners
    renderer.domElement.addEventListener('mousedown', handleMouseDown);
    document.addEventListener('mouseup', handleMouseUp);
    document.addEventListener('mousemove', handleMouseMove);
    renderer.domElement.addEventListener('wheel', handleWheel);

    // Animation loop
    const animate = () => {
      frameIdRef.current = requestAnimationFrame(animate);
      
      // Update selected object highlight
      if (selectedObject && selectedObject.material) {
        selectedObject.material.opacity = 0.8 + Math.sin(Date.now() * 0.005) * 0.2;
      }
      
      renderer.render(scene, camera);
    };
    animate();

    // Store refs
    sceneRef.current = scene;
    rendererRef.current = renderer;
    cameraRef.current = camera;
    raycasterRef.current = raycaster;

    setIsInitialized(true);
    console.log('✅ Three.js scene initialized');

    // Cleanup function
    return () => {
      if (frameIdRef.current) {
        cancelAnimationFrame(frameIdRef.current);
      }
      
      renderer.domElement.removeEventListener('mousedown', handleMouseDown);
      document.removeEventListener('mouseup', handleMouseUp);
      document.removeEventListener('mousemove', handleMouseMove);
      renderer.domElement.removeEventListener('wheel', handleWheel);

      if (mountRef.current && renderer.domElement) {
        mountRef.current.removeChild(renderer.domElement);
      }
      
      renderer.dispose();
      console.log('🧹 Three.js scene cleaned up');
    };
  }, [width, height, enableControls, onZoneClick, isInitialized]);

  // Helper functions
  const addToScene = (object) => {
    if (sceneRef.current) {
      sceneRef.current.add(object);
    }
  };

  const removeFromScene = (object) => {
    if (sceneRef.current) {
      sceneRef.current.remove(object);
    }
  };

  const clearScene = (filterFn = null) => {
    if (!sceneRef.current) return;
    
    const objectsToRemove = [];
    sceneRef.current.traverse((object) => {
      if (filterFn ? filterFn(object) : object.userData.clearable) {
        objectsToRemove.push(object);
      }
    });
    
    objectsToRemove.forEach(obj => sceneRef.current.remove(obj));
  };

  const resetCameraView = () => {
    if (cameraRef.current) {
      cameraRef.current.position.set(200, 150, 200);
      cameraRef.current.lookAt(0, 0, 0);
    }
  };

  const fitCameraToObject = (object, offset = 1.5) => {
    if (!cameraRef.current || !object) return;
    
    const box = new THREE.Box3().setFromObject(object);
    const center = box.getCenter(new THREE.Vector3());
    const size = box.getSize(new THREE.Vector3());
    
    const maxDim = Math.max(size.x, size.y, size.z);
    const distance = maxDim * offset;
    
    cameraRef.current.position.copy(center).add(new THREE.Vector3(distance, distance, distance));
    cameraRef.current.lookAt(center);
  };

  return {
    mountRef,
    sceneRef,
    rendererRef,
    cameraRef,
    isInitialized,
    selectedObject,
    
    // Helper methods
    addToScene,
    removeFromScene,
    clearScene,
    resetCameraView,
    fitCameraToObject
  };
};

export default useThreeScene;