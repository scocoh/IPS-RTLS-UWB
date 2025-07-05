/* Name: ZV_index.js */
/* Version: 0.1.7 */
/* Created: 250704 */
/* Modified: 250704 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin + Claude */
/* Description: Main component for ZoneViewer - orchestrates all subcomponents */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/ZoneViewer/ZV_index.js */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

import React, { useState, useEffect, useCallback, useMemo } from "react";
import { Tabs, Tab } from "react-bootstrap";

// Import styles
import "./styles/ZoneViewer.css";

// Import components
import ZoneSelectionTab from "./components/ZoneSelectionTab";
import ZoneEditTab from "./components/ZoneEditTab";
import ZoneMapTab from "./components/ZoneMapTab";

// Import hooks
import { useZoneHierarchy } from "./hooks/useZoneHierarchy";
import { useVertexManagement } from "./hooks/useVertexManagement";

// Import services
import { zoneViewerApi } from "./services/zoneViewerApi";
import { vertexApi } from "./services/vertexApi";

const ZoneViewer = () => {
  // Zone state
  const [allZones, setAllZones] = useState([]);
  const [zones, setZones] = useState([]);
  const [zoneTypes, setZoneTypes] = useState([]);
  const [zoneType, setZoneType] = useState("");
  const [selectedZone, setSelectedZone] = useState("");
  const [checkedZones, setCheckedZones] = useState([]);
  
  // Map state - NEW: Separate map selection
  const [selectedMapId, setSelectedMapId] = useState("");
  
  // NEW: Advanced zone styling state
  const [zoneStyle, setZoneStyle] = useState({
    fillOpacity: 30,        // Zone fill transparency (0-100%)
    lineOpacity: 70,        // Line and vertex transparency (0-100%)
    lineColor: '#ff0000',   // Zone border color
    vertexColor: '#ff0000'  // Vertex marker color
  });
  
  // Vertex state
  const [vertices, setVertices] = useState([]);
  const [editedVertices, setEditedVertices] = useState({});
  const [deletedVertices, setDeletedVertices] = useState([]);
  const [selectedVertices, setSelectedVertices] = useState(new Set());
  const [targetVertex, setTargetVertex] = useState(null);
  
  // UI state
  const [activeTab, setActiveTab] = useState("zoneSelection");
  const [useLeaflet, setUseLeaflet] = useState(false);
  const [fetchError, setFetchError] = useState(null);
  const [loading, setLoading] = useState(true);

  // Zone hierarchy hook
  const {
    getZoneHierarchy,
    findCampusForZone,
    filteredZones,
    selectedZoneData
  } = useZoneHierarchy({
    allZones,
    zoneType,
    selectedZone
  });

  // ELEGANT SOLUTION: Extract available maps from hierarchical zones data
  const availableMaps = useMemo(() => {
    if (!zones || zones.length === 0) return [];

    const extractMapsFromHierarchy = (zoneNode, maps = []) => {
      // Add current zone's map if it exists
      if (zoneNode.map_id) {
        const existingMap = maps.find(m => m.mapId === zoneNode.map_id);
        if (!existingMap) {
          maps.push({
            mapId: zoneNode.map_id,
            zoneId: zoneNode.zone_id,
            zoneName: zoneNode.zone_name,
            zoneType: zoneNode.zone_type
          });
        }
      }

      // Recursively process children
      if (zoneNode.children && zoneNode.children.length > 0) {
        zoneNode.children.forEach(child => extractMapsFromHierarchy(child, maps));
      }

      return maps;
    };

    // Extract maps from all root zones
    const allMaps = [];
    zones.forEach(rootZone => extractMapsFromHierarchy(rootZone, allMaps));

    // Sort by zone type (Campus first, then Building, Floor, etc.)
    const sortedMaps = allMaps.sort((a, b) => a.zoneType - b.zoneType);
    
    console.log("🗺️ Available maps extracted from hierarchy:", sortedMaps);
    return sortedMaps;
  }, [zones]);

  // Memoize the campus finding function to prevent infinite loops
  const memoizedFindCampusForZone = useCallback((zoneId, zones) => {
    return findCampusForZone(zoneId, zones);
  }, [findCampusForZone]);

  // Memoize the hierarchy function to prevent infinite loops
  const memoizedGetZoneHierarchy = useCallback((zoneId, zones) => {
    return getZoneHierarchy(zoneId, zones);
  }, [getZoneHierarchy]);

  // Vertex management hook
  const {
    handleVertexChange,
    handleVertexBlur,
    stageDeleteVertex,
    addVertex,
    saveVertices,
    exportVertices,
    importVertices,
    exportToSVG,
    applyCoordinates
  } = useVertexManagement({
    vertices,
    setVertices,
    editedVertices,
    setEditedVertices,
    deletedVertices,
    setDeletedVertices,
    selectedVertices,
    setSelectedVertices,
    targetVertex,
    setTargetVertex,
    checkedZones,
    selectedZone,
    allZones,
    findCampusForZone: memoizedFindCampusForZone
  });

  // Load initial data
  useEffect(() => {
    const fetchInitialData = async () => {
      try {
        setLoading(true);
        
        // Fetch zone types
        const zoneTypesData = await zoneViewerApi.fetchZoneTypes();
        setZoneTypes(zoneTypesData || []);

        // Fetch all zones with maps
        const zonesData = await zoneViewerApi.fetchZonesWithMaps();
        setAllZones(zonesData);

        setFetchError(null);
      } catch (error) {
        console.error("❌ Error fetching initial data:", error);
        setFetchError(error.message);
      } finally {
        setLoading(false);
      }
    };
    
    fetchInitialData();
  }, []);

  // Load zones and vertices when zone selection changes
  useEffect(() => {
    if (selectedZone && allZones.length > 0) {
      const fetchZonesAndVertices = async () => {
        try {
          const selectedZoneData = allZones.find(z => z.i_zn === parseInt(selectedZone));
          if (!selectedZoneData) return;

          // Get zone hierarchy for the selected zone
          const zoneHierarchy = memoizedGetZoneHierarchy(selectedZone, allZones);
          const hierarchyArray = Array.from(zoneHierarchy);

          // Fetch zones and vertices
          const campusZone = memoizedFindCampusForZone(selectedZone, allZones);
          
          const [hierarchicalZones, verticesData] = await Promise.all([
            zoneViewerApi.fetchZonesForCampus(campusZone),
            vertexApi.fetchVerticesForCampus(campusZone)
          ]);

          // ELEGANT: Use the hierarchical zones directly (they contain map_id)
          setZones(hierarchicalZones);
          setCheckedZones(hierarchyArray);
          setVertices(verticesData);
          setEditedVertices({});
          setDeletedVertices([]);
          setSelectedVertices(new Set());
          setTargetVertex(null);
        } catch (error) {
          console.error("❌ Error fetching zones/vertices:", error);
          setFetchError(error.message);
        }
      };
      
      fetchZonesAndVertices();
    }
  }, [selectedZone, allZones, memoizedGetZoneHierarchy, memoizedFindCampusForZone]);

  // Auto-select first available map when zone changes
  useEffect(() => {
    if (availableMaps.length > 0 && !selectedMapId) {
      // Default to the first map (usually the most specific one)
      setSelectedMapId(availableMaps[0].mapId.toString());
    } else if (availableMaps.length === 0) {
      setSelectedMapId("");
    }
  }, [availableMaps, selectedMapId]);

  // Zone selection handlers
  const handleZoneTypeChange = useCallback((newZoneType) => {
    setZoneType(newZoneType);
    setSelectedZone(""); // Reset zone selection when type changes
    setSelectedMapId(""); // Reset map selection when type changes
  }, []);

  const handleZoneChange = useCallback((newZone) => {
    setSelectedZone(newZone);
    setSelectedMapId(""); // Reset map selection when zone changes
  }, []);

  // Map selection handler
  const handleMapChange = useCallback((newMapId) => {
    setSelectedMapId(newMapId);
    console.log("🗺️ User selected map:", newMapId);
  }, []);

  // Zone style handler
  const handleZoneStyleChange = useCallback((newStyle) => {
    setZoneStyle(newStyle);
    console.log("🎨 Zone style updated:", newStyle);
  }, []);

  const handleZoneToggle = useCallback((zoneId) => {
    setCheckedZones((prev) =>
      prev.includes(zoneId) ? prev.filter((id) => id !== zoneId) : [...prev, zoneId]
    );
  }, []);

  const handleCheckAll = useCallback((check) => {
    if (check) {
      const hierarchy = memoizedGetZoneHierarchy(selectedZone, allZones);
      setCheckedZones(Array.from(hierarchy));
    } else {
      setCheckedZones([]);
    }
  }, [selectedZone, allZones, memoizedGetZoneHierarchy]);

  const handleDeleteZone = useCallback(async (zoneId) => {
    if (!window.confirm(`Are you sure? This will delete zone ${zoneId} and all its progeny.`)) {
      return;
    }

    try {
      await zoneViewerApi.deleteZoneRecursive(zoneId);

      // Refresh all data
      const zonesData = await zoneViewerApi.fetchZonesWithMaps();
      setAllZones(zonesData);

      if (selectedZone) {
        const campusZone = memoizedFindCampusForZone(selectedZone, zonesData);
        const verticesData = await vertexApi.fetchVerticesForCampus(campusZone);
        setVertices(verticesData);
      }

      setSelectedVertices(new Set());
      setTargetVertex(null);
      alert("Zone deleted successfully!");
    } catch (error) {
      console.error("❌ Error deleting zone:", error);
      alert("Failed to delete zone: " + error.message);
    }
  }, [selectedZone, memoizedFindCampusForZone]);

  if (loading) {
    return <div>Loading Zone Viewer...</div>;
  }

  return (
    <div style={{ padding: "20px" }}>
      <h2>Zone Viewer & Editor (Modular)</h2>
      {fetchError && <div style={{ color: "red" }}>{fetchError}</div>}

      <Tabs
        activeKey={activeTab}
        onSelect={(tab) => setActiveTab(tab)}
        className="mb-3"
      >
        <Tab eventKey="zoneSelection" title="Zone Selection">
          <ZoneSelectionTab
            zoneTypes={zoneTypes}
            zoneType={zoneType}
            onZoneTypeChange={handleZoneTypeChange}
            filteredZones={filteredZones}
            selectedZone={selectedZone}
            onZoneChange={handleZoneChange}
            availableMaps={availableMaps}
            selectedMapId={selectedMapId}
            onMapChange={handleMapChange}
            zones={zones}
            checkedZones={checkedZones}
            onZoneToggle={handleZoneToggle}
            onCheckAll={handleCheckAll}
            onDeleteZone={handleDeleteZone}
          />
        </Tab>

        <Tab eventKey="zoneMap" title="Zone Map">
          <ZoneMapTab
            mapId={selectedMapId ? parseInt(selectedMapId) : null}
            zones={zones}
            checkedZones={checkedZones}
            vertices={vertices}
            useLeaflet={useLeaflet}
            setUseLeaflet={setUseLeaflet}
            selectedZone={selectedZone}
            selectedZoneData={selectedZoneData}
            selectedMapId={selectedMapId}
            availableMaps={availableMaps}
            zoneStyle={zoneStyle}
            setZoneStyle={handleZoneStyleChange}
          />
        </Tab>

        <Tab eventKey="editVertices" title="Edit Vertices">
          <ZoneEditTab
            vertices={vertices}
            checkedZones={checkedZones}
            editedVertices={editedVertices}
            selectedVertices={selectedVertices}
            targetVertex={targetVertex}
            onVertexChange={handleVertexChange}
            onVertexBlur={handleVertexBlur}
            onVertexSelect={(vertexId) => {
              const newSelectedVertices = new Set(selectedVertices);
              if (newSelectedVertices.has(vertexId)) {
                newSelectedVertices.delete(vertexId);
              } else {
                newSelectedVertices.add(vertexId);
              }
              setSelectedVertices(newSelectedVertices);
            }}
            onTargetVertexSelect={setTargetVertex}
            onAddVertex={addVertex}
            onStageDeleteVertex={stageDeleteVertex}
            onSaveVertices={saveVertices}
            onApplyCoordinates={applyCoordinates}
            onExportVertices={exportVertices}
            onImportVertices={importVertices}
            onExportToSVG={exportToSVG}
            selectedZone={selectedZone}
          />
        </Tab>
      </Tabs>
    </div>
  );
};

export default ZoneViewer;