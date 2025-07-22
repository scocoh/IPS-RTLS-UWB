/* Name: Scene3D.js */
/* Version: 0.1.30 */
/* Created: 250719 */
/* Modified: 250722 */
/* Creator: ParcoAdmin + Claude */
/* Modified By: ParcoAdmin + Claude */
/* Description: DUPLICATE TEXT FIX - Global instance tracking to prevent duplicate overlays */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/ThreeDZoneViewer/components */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */
/* Changelog: */
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
  showCornerMarkers = false
}) => {
  const mountRef = useRef(null);
  const sceneRef = useRef(null);
  const rendererRef = useRef(null);
  const cameraRef = useRef(null);
  const controlsRef = useRef(null);
  const frameIdRef = useRef(null);
  const [isInitialized, setIsInitialized] = useState(false);
  const [realZoneDataList, setRealZoneDataList] = useState([]);
  
  // NEW v0.1.30: Unique instance ID and global tracking
  const instanceId = useRef(`scene3d_${Math.random().toString(36).substr(2, 9)}`);

  // NEW v0.1.30: Global instance tracking to prevent duplicates
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

  // NEW v0.1.30: Check if this is the primary instance (only one that shows overlays)
  const isPrimaryInstance = isInitialized && (
    !window.scene3dInstances || 
    window.scene3dInstances.size === 1 ||
    (mountRef.current && mountRef.current.querySelector('canvas'))
  );

  const zonesToShow = Object.keys(zoneSettings)
    .filter(zoneId => zoneSettings[zoneId].visible)
    .map(zoneId => parseInt(zoneId));

  console.log(`🎮 Scene3D v0.1.30 [${instanceId.current}] - Duplicate Fix:`, {
    selectedCampusId,
    selectedCampusName,
    isPrimaryInstance,
    showDebugOverlays,
    showControlsHint,
    totalInstances: window.scene3dInstances?.size || 0
  });

  // Fetch zones when conditions are met
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

  // Initialize Three.js scene with double-render prevention
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
    console.log(`✅ [${instanceId.current}] Three.js scene initialized`);

    return () => {
      console.log(`🧹 [${instanceId.current}] Starting cleanup`);
      
      if (frameIdRef.current) {
        cancelAnimationFrame(frameIdRef.current);
      }
      
      if (controlsRef.current && controlsRef.current.dispose) {
        controlsRef.current.dispose();
      }
      
      if (renderer?.domElement && mountRef.current?.contains(renderer.domElement)) {
        mountRef.current.removeChild(renderer.domElement);
      }
      
      if (renderer) {
        renderer.dispose();
      }
    };
  }, [width, height]);

  // Add map plane
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

  // Add zones
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
      
      {/* NEW v0.1.30: Only PRIMARY instance shows overlays - eliminates duplicates */}
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
          <div>🆕 v0.1.30: Duplicate fix</div>
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
          <div>🏫 Campus: {selectedCampusId ? `${selectedCampusName} (${selectedCampusId})` : 'None'}</div>
          <div>🆕 v0.1.30: Duplicate text fix</div>
          <div>🔧 Instance: [{instanceId.current}]</div>
        </div>
      )}
    </div>
  );
};

export default Scene3D;