/* Name: Scene3D.js */
/* Version: 0.1.31 */
/* Created: 250719 */
/* Modified: 250722 */
/* Creator: ParcoAdmin + Claude */
/* Modified By: ParcoAdmin + Claude */
/* Description: REAL-TIME TAGS INTEGRATION - Added 3D tag rendering with real-time position updates */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/ThreeDZoneViewer/components */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */
/* Changelog: */
/* - 0.1.31: REAL-TIME TAGS INTEGRATION - Added tag rendering, real-time updates, tag trails, configurable appearance */
/* - 0.1.30: DUPLICATE TEXT FIX - Added global instance tracking, only primary instance shows overlays */
/* - 0.1.29: DYNAMIC CAMPUS SUPPORT - Removed hardcoded 422/Map 39 references, added selectedCampusId prop, dynamic campus info */

import React, { useRef, useEffect, useState } from 'react';
import * as THREE from 'three';
import { config } from '../../../config';
import { 
  getMapBounds, 
  createMapPlaneGeometry, 
  getCameraPosition,
  logCoordinateSystem,
  parcoToThreeJs
} from '../utils/mapCoordinateSystem';

import {
  fetchZoneVertices,
  processZoneVertices,
  createVertexMarkers
} from '../utils/zoneGeometry';

import {
  createFlatZonePolygon,
  createFlatZoneMesh,
  createExtrudedZoneGeometry,
  createExtrudedZoneMesh
} from '../utils/zoneShapeGeometry';

import {
  createTextSprite,
  centerCameraOnZones,
  clearSceneObjects,
  setupSceneLighting,
  setupSceneHelpers
} from '../utils/sceneUtilities';

// NEW v0.1.31: Import tag rendering utilities
import {
  createTag3D,
  updateTagPosition,
  createTagTrail,
  updateTagAppearance,
  clearAllTags,
  getAllTagsInScene,
  isPositionWithinBounds,
  DEFAULT_TAG_CONFIG
} from '../utils/tagRenderingUtils';

const OrbitControls = (() => {
  try {
    const { OrbitControls } = require('three/examples/jsm/controls/OrbitControls');
    return OrbitControls;
  } catch (error) {
    console.warn('⚠️ OrbitControls not available, falling back to manual controls');
    return null;
  }
})();

const Scene3D = ({ 
  // Existing props (unchanged)
  mapData = null,
  zoneData = null,
  zoneSettings = {},
  selectedCampusId = null,
  selectedCampusName = "",
  showCampusZone = true,
  mapOpacity = 0.3,
  height = 500,
  width = 900,
  showDebugOverlays = true,
  showControlsHint = true,
  showZoneLabels = false,
  showCornerMarkers = false,
  
  // NEW v0.1.31: Real-time tag props
  displayTags = {},           // Tags to display in 3D scene
  tagHistory = {},            // Tag movement history for trails
  tagConfig = DEFAULT_TAG_CONFIG, // Tag appearance configuration
  showTags = true,            // Master toggle for tag visibility
  onTagClick = null           // Callback when tag is clicked
}) => {
  const mountRef = useRef(null);
  const sceneRef = useRef(null);
  const rendererRef = useRef(null);
  const cameraRef = useRef(null);
  const controlsRef = useRef(null);
  const frameIdRef = useRef(null);
  const [isInitialized, setIsInitialized] = useState(false);
  const [realZoneDataList, setRealZoneDataList] = useState([]);
  
  // NEW v0.1.31: Tag rendering state
  const [currentTagObjects, setCurrentTagObjects] = useState({}); // tagId -> Three.js group
  const [currentTrailObjects, setCurrentTrailObjects] = useState({}); // tagId -> Three.js line
  
  // Instance tracking (existing v0.1.30)
  const instanceId = useRef(`scene3d_${Math.random().toString(36).substr(2, 9)}`);

  // Global instance tracking to prevent duplicates (existing v0.1.30)
  useEffect(() => {
    if (!window.scene3dInstances) window.scene3dInstances = new Set();
    window.scene3dInstances.add(instanceId.current);
    
    console.log(`📊 [${instanceId.current}] Instance registered. Total active: ${window.scene3dInstances.size}`);
    
    return () => {
      if (window.scene3dInstances) {
        window.scene3dInstances.delete(instanceId.current);
        console.log(`📊 [${instanceId.current}] Instance removed. Total active: ${window.scene3dInstances.size}`);
      }
    };
  }, []);

  // Check if this is the primary instance (existing v0.1.30)
  const isPrimaryInstance = isInitialized && (
    !window.scene3dInstances || 
    window.scene3dInstances.size === 1 ||
    (mountRef.current && mountRef.current.querySelector('canvas'))
  );

  const zonesToShow = Object.keys(zoneSettings)
    .filter(zoneId => zoneSettings[zoneId].visible)
    .map(zoneId => parseInt(zoneId));

  console.log(`🎮 Scene3D v0.1.31 [${instanceId.current}] - Real-Time Tags:`, {
    selectedCampusId,
    selectedCampusName,
    isPrimaryInstance,
    showDebugOverlays,
    showControlsHint,
    totalInstances: window.scene3dInstances?.size || 0,
    // NEW: Tag debugging
    displayTags: Object.keys(displayTags).length,
    showTags,
    tagConfigShowLabels: tagConfig.showLabels,
    tagConfigShowTrails: tagConfig.showTrails
  });

  // Fetch zones when conditions are met (existing functionality)
  useEffect(() => {
    if (showCampusZone && selectedCampusId && realZoneDataList.length === 0) {
      console.log(`🎯 [${instanceId.current}] Loading zones for campus ${selectedCampusId}`);
      
      const fetchAllZones = async () => {
        const allZoneIds = Object.keys(zoneSettings).map(id => parseInt(id));
        
        if (allZoneIds.length === 0) {
          console.log(`⚠️ [${instanceId.current}] No zones in zoneSettings to fetch`);
          return;
        }
        
        const zoneDataPromises = allZoneIds.map(zoneId => 
          fetchZoneVertices(zoneId, config)
        );
        
        try {
          const zoneDataResults = await Promise.all(zoneDataPromises);
          const validZoneData = zoneDataResults.filter(data => data !== null);
          setRealZoneDataList(validZoneData);
          
          console.log(`✅ [${instanceId.current}] Loaded ${validZoneData.length} zones`);
        } catch (error) {
          console.error(`❌ [${instanceId.current}] Error fetching zones:`, error);
        }
      };
      
      fetchAllZones();
    } else if (!showCampusZone || !selectedCampusId) {
      setRealZoneDataList([]);
    }
  }, [showCampusZone, selectedCampusId]);

  // Initialize Three.js scene with double-render prevention (existing functionality)
  useEffect(() => {
    if (!mountRef.current || isInitialized) return;

    if (mountRef.current.hasChildNodes()) {
      console.log(`⚠️ [${instanceId.current}] Mount already has children, skipping initialization`);
      return;
    }

    console.log(`🎮 [${instanceId.current}] Initializing Three.js scene`);

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0xf0f0f0);

    const camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000);
    camera.position.set(60, 60, 60);
    camera.lookAt(0, 0, 0);

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(width, height);
    renderer.shadowMap.enabled = false;

    // NEW v0.1.31: Add mouse event handling for tag clicks
    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2();

    const handleClick = (event) => {
      if (!onTagClick) return;

      // Calculate mouse position in normalized device coordinates
      const rect = renderer.domElement.getBoundingClientRect();
      mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
      mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

      // Raycast from camera through mouse position
      raycaster.setFromCamera(mouse, camera);
      const intersects = raycaster.intersectObjects(scene.children, true);

      // Find clicked tag
      for (let intersect of intersects) {
        let object = intersect.object;
        while (object && !object.userData.isTag) {
          object = object.parent;
        }
        if (object && object.userData.isTag) {
          console.log(`🖱️ Clicked tag: ${object.userData.tagId}`);
          onTagClick(object.userData.tagId, object.userData.tagData);
          break;
        }
      }
    };

    renderer.domElement.addEventListener('click', handleClick);

    mountRef.current.appendChild(renderer.domElement);

    setupSceneLighting(scene);
    setupSceneHelpers(scene);

    let controls = null;
    if (OrbitControls) {
      controls = new OrbitControls(camera, renderer.domElement);
      controls.enableDamping = true;
      controls.dampingFactor = 0.05;
      controls.screenSpacePanning = false;
      controls.minDistance = 15;
      controls.maxDistance = 600;
      controls.maxPolarAngle = Math.PI / 2;
      controls.target.set(0, 0, 0);
      controls.update();
    }

    const animate = () => {
      frameIdRef.current = requestAnimationFrame(animate);
      if (controls && controls.update) {
        controls.update();
      }
      renderer.render(scene, camera);
    };
    animate();

    sceneRef.current = scene;
    rendererRef.current = renderer;
    cameraRef.current = camera;
    controlsRef.current = controls;

    setIsInitialized(true);
    console.log(`✅ [${instanceId.current}] Three.js scene initialized with tag support`);

    return () => {
      console.log(`🧹 [${instanceId.current}] Starting cleanup`);
      
      if (frameIdRef.current) {
        cancelAnimationFrame(frameIdRef.current);
      }
      
      if (controlsRef.current && controlsRef.current.dispose) {
        controlsRef.current.dispose();
      }
      
      // NEW v0.1.31: Clean up event listeners
      if (renderer?.domElement) {
        renderer.domElement.removeEventListener('click', handleClick);
      }
      
      if (renderer?.domElement && mountRef.current?.contains(renderer.domElement)) {
        mountRef.current.removeChild(renderer.domElement);
      }
      
      if (renderer) {
        renderer.dispose();
      }
    };
  }, [width, height, onTagClick]);

  // Add map plane (existing functionality)
  useEffect(() => {
    if (!isInitialized || !sceneRef.current || !mapData) return;

    console.log(`🗺️ [${instanceId.current}] Adding map plane`);
    
    clearSceneObjects(sceneRef.current, 'isMapPlane');

    const mapBounds = getMapBounds(mapData);
    const mapPlaneGeom = createMapPlaneGeometry(mapBounds);
    const mapGeometry = new THREE.PlaneGeometry(mapPlaneGeom.width, mapPlaneGeom.height);

    const mapMaterial = new THREE.MeshStandardMaterial({ 
      color: 0x4a90e2,
      side: THREE.DoubleSide,
      transparent: true,
      opacity: mapOpacity,
      roughness: 1.0,
      metalness: 0.0
    });

    const mapPlane = new THREE.Mesh(mapGeometry, mapMaterial);
    mapPlane.rotation.x = -Math.PI / 2;
    mapPlane.position.set(
      mapPlaneGeom.position.x,
      mapPlaneGeom.position.y,
      mapPlaneGeom.position.z
    );
    mapPlane.receiveShadow = false;
    mapPlane.userData.isMapPlane = true;

    sceneRef.current.add(mapPlane);

    if (cameraRef.current) {
      const cameraPos = getCameraPosition(mapBounds);
      cameraRef.current.position.set(cameraPos.x * 1.2, cameraPos.y * 1.1, cameraPos.z * 1.2);
      cameraRef.current.lookAt(
        mapPlaneGeom.position.x,
        0,
        mapPlaneGeom.position.z
      );
      
      if (controlsRef.current && controlsRef.current.target) {
        controlsRef.current.target.set(
          mapPlaneGeom.position.x,
          0,
          mapPlaneGeom.position.z
        );
        controlsRef.current.update();
      }
    }
  }, [isInitialized, mapData, mapOpacity]);

  // Add zones (existing functionality)
  const zoneSettingsKey = JSON.stringify(zoneSettings);
  
  useEffect(() => {
    if (!isInitialized || !sceneRef.current || !mapData || !showCampusZone || !selectedCampusId) return;

    console.log(`🏢 [${instanceId.current}] Rendering zones for campus ${selectedCampusId}`);
    clearSceneObjects(sceneRef.current, 'isRealZone');

    if (realZoneDataList.length === 0) {
      return;
    }

    const mapBounds = getMapBounds(mapData);
    
    realZoneDataList.forEach((zoneData) => {
      const zoneId = zoneData.zone_id;
      const settings = zoneSettings[zoneId];
      
      if (!settings || !settings.visible) {
        return;
      }
      
      const uniqueVertices = processZoneVertices(zoneData);
      if (uniqueVertices.length < 3) {
        return;
      }

      const zoneColor = new THREE.Color(settings.color).getHex();
      const extrudedGeometry = createExtrudedZoneGeometry(uniqueVertices, mapBounds);
      
      if (!extrudedGeometry) {
        return;
      }

      const extrudedZoneMesh = createExtrudedZoneMesh(
        extrudedGeometry, 
        zoneData, 
        zoneColor, 
        settings.opacity,
        showZoneLabels,
        showCornerMarkers
      );
      
      if (extrudedZoneMesh) {
        sceneRef.current.add(extrudedZoneMesh);
      }

      createVertexMarkers(uniqueVertices, mapBounds, sceneRef.current);
    });

    if (realZoneDataList.filter(z => zoneSettings[z.zone_id]?.visible).length > 0) {
      centerCameraOnZones(sceneRef.current, cameraRef.current, controlsRef.current);
    }

  }, [isInitialized, mapData, realZoneDataList, showCampusZone, zoneSettingsKey, showZoneLabels, showCornerMarkers, selectedCampusId]);

  // NEW v0.1.31: Render and update real-time tags
  const displayTagsKey = JSON.stringify(displayTags);
  const tagConfigKey = JSON.stringify(tagConfig);
  
  useEffect(() => {
    if (!isInitialized || !sceneRef.current || !mapData || !showTags) {
      // Clear all tags if conditions not met
      if (isInitialized && sceneRef.current) {
        console.log(`🧹 [${instanceId.current}] Clearing tags - conditions not met`);
        clearAllTags(sceneRef.current);
        setCurrentTagObjects({});
        setCurrentTrailObjects({});
      }
      return;
    }

    console.log(`🏷️ [${instanceId.current}] Updating tags for campus ${selectedCampusId}:`, {
      displayTags: Object.keys(displayTags).length,
      showTags,
      tagConfig: tagConfig
    });

    const mapBounds = getMapBounds(mapData);
    const scene = sceneRef.current;

    // Remove tags that are no longer selected
    Object.keys(currentTagObjects).forEach(tagId => {
      if (!displayTags[tagId]) {
        console.log(`➖ [${instanceId.current}] Removing tag ${tagId}`);
        const tagObject = currentTagObjects[tagId];
        if (tagObject) {
          scene.remove(tagObject);
          // Dispose of geometries and materials
          tagObject.traverse((child) => {
            if (child.geometry) child.geometry.dispose();
            if (child.material) {
              if (child.material.map) child.material.map.dispose();
              child.material.dispose();
            }
          });
        }
        
        // Remove trail if exists
        const trailObject = currentTrailObjects[tagId];
        if (trailObject) {
          scene.remove(trailObject);
          if (trailObject.geometry) trailObject.geometry.dispose();
          if (trailObject.material) trailObject.material.dispose();
        }
      }
    });

    // Update current objects state
    const newTagObjects = {};
    const newTrailObjects = {};

    // Add or update tags that are selected
    Object.entries(displayTags).forEach(([tagId, tagData]) => {
      // Check if position is within map bounds
      if (!isPositionWithinBounds(tagData.x, tagData.y, mapBounds)) {
        console.warn(`⚠️ [${instanceId.current}] Tag ${tagId} position out of bounds: (${tagData.x}, ${tagData.y})`);
        return;
      }

      const existingTag = currentTagObjects[tagId];
      
      if (existingTag) {
        // Update existing tag position
        console.log(`🔄 [${instanceId.current}] Updating tag ${tagId} position`);
        updateTagPosition(existingTag, tagData, mapBounds, tagConfig);
        newTagObjects[tagId] = existingTag;
      } else {
        // Create new tag
        console.log(`➕ [${instanceId.current}] Creating new tag ${tagId}`);
        const tagObject = createTag3D(tagData, mapBounds, tagConfig);
        if (tagObject) {
          scene.add(tagObject);
          newTagObjects[tagId] = tagObject;
        }
      }

      // Handle tag trails if enabled
      if (tagConfig.showTrails && tagHistory[tagId] && tagHistory[tagId].length > 1) {
        // Remove existing trail
        const existingTrail = currentTrailObjects[tagId];
        if (existingTrail) {
          scene.remove(existingTrail);
          if (existingTrail.geometry) existingTrail.geometry.dispose();
          if (existingTrail.material) existingTrail.material.dispose();
        }

        // Create new trail
        const trailObject = createTagTrail(tagHistory[tagId], mapBounds, tagConfig);
        if (trailObject) {
          scene.add(trailObject);
          newTrailObjects[tagId] = trailObject;
        }
      }
    });

    // Update state
    setCurrentTagObjects(newTagObjects);
    setCurrentTrailObjects(newTrailObjects);

    console.log(`✅ [${instanceId.current}] Tag update complete: ${Object.keys(newTagObjects).length} tags, ${Object.keys(newTrailObjects).length} trails`);

  }, [isInitialized, mapData, showTags, displayTagsKey, tagConfigKey, tagHistory, selectedCampusId]);

  // NEW v0.1.31: Update tag appearance when config changes
  useEffect(() => {
    if (!isInitialized || !sceneRef.current) return;

    console.log(`🎨 [${instanceId.current}] Updating tag appearance:`, tagConfig);

    Object.entries(currentTagObjects).forEach(([tagId, tagObject]) => {
      updateTagAppearance(tagObject, {
        color: new THREE.Color(tagConfig.activeColor).getHex(),
        opacity: tagConfig.opacity || 0.8,
        scale: tagConfig.sphereRadius / DEFAULT_TAG_CONFIG.sphereRadius
      });
    });

  }, [isInitialized, tagConfig.activeColor, tagConfig.sphereRadius, currentTagObjects]);

  return (
    <div style={{ position: 'relative' }}>
      <div 
        ref={mountRef} 
        style={{ 
          width: `${width}px`, 
          height: `${height}px`, 
          border: '2px solid #ccc',
          borderRadius: '4px'
        }} 
      />
      
      {/* Updated debug overlays - only PRIMARY instance shows overlays */}
      {showDebugOverlays && isPrimaryInstance && (
        <div style={{ 
          position: 'absolute', 
          top: '10px', 
          right: '10px', 
          background: 'rgba(0,0,0,0.8)', 
          color: 'white', 
          padding: '10px', 
          borderRadius: '6px',
          fontSize: '12px',
          fontFamily: 'monospace',
          maxWidth: '300px'
        }}>
          <div>Three.js Scene: {isInitialized ? '✅' : '⏳'}</div>
          <div>Selected Campus: {selectedCampusId ? `${selectedCampusName} (${selectedCampusId})` : '❌ None'}</div>
          <div>Instance: [{instanceId.current}]</div>
          <div>Primary: {isPrimaryInstance ? '✅' : '❌'}</div>
          <div>Map Data: {mapData ? '✅' : '❌'}</div>
          <div>Real Zones: {realZoneDataList.length > 0 ? `✅ ${realZoneDataList.length} zones` : '⏳'}</div>
          <div>Visible Zones: {zonesToShow.length}</div>
          <div>Campus Zone: {showCampusZone ? '👁️' : '🙈'}</div>
          <div>Zone Labels: {showZoneLabels ? '📋 ON' : '🚫 OFF'}</div>
          <div>Corner Markers: {showCornerMarkers ? '🔴🔵 ON' : '🚫 OFF'}</div>
          {/* NEW v0.1.31: Tag debugging info */}
          <div>Real-Time Tags: {showTags ? `🏷️ ${Object.keys(displayTags).length} shown` : '🚫 OFF'}</div>
          <div>Tag Labels: {tagConfig.showLabels ? '📋 ON' : '🚫 OFF'}</div>
          <div>Tag Trails: {tagConfig.showTrails ? '🛤️ ON' : '🚫 OFF'}</div>
          <div>🆕 v0.1.31: Real-time tags</div>
        </div>
      )}

      {showControlsHint && isPrimaryInstance && (
        <div style={{
          position: 'absolute',
          bottom: '10px',
          right: '10px',
          background: 'rgba(0,0,0,0.8)',
          color: 'white',
          padding: '10px',
          borderRadius: '6px',
          fontSize: '12px',
          maxWidth: '350px'
        }}>
          🖱️ Drag to rotate • 🖲️ Scroll to zoom
          {/* NEW v0.1.31: Tag interaction hints */}
          {showTags && Object.keys(displayTags).length > 0 && (
            <div>🏷️ Click tags for details</div>
          )}
          <div>🏫 Campus: {selectedCampusId ? `${selectedCampusName} (${selectedCampusId})` : 'None'}</div>
          <div>🆕 v0.1.31: Real-time tag support</div>
          <div>🔧 Instance: [{instanceId.current}]</div>
        </div>
      )}
    </div>
  );
};

export default Scene3D;