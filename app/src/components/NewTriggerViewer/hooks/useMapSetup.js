// hooks/useMapSetup.js  • ParcoRTLS v0.1.9 - FIXED INFINITE LOOP
// -----------------------------------------------------------------------------
// Handles Leaflet map creation, image overlay, bounds/view management, custom
// controls attachment, event listeners, and cleanup. Extracted from the
// monolithic NewTriggerViewer.js (v0.1.7).
//
// FIXED: Removed unstable dependencies from useCallback to prevent infinite loop
// -----------------------------------------------------------------------------

import { useEffect, useCallback, useRef } from "react";
import L from "leaflet";

export const useMapSetup = ({
  useLeaflet = true,
  mapRef,            // div ref for mounting
  mapInstanceRef,    // ref to expose Leaflet map
  mapData,           // { bounds, imageUrl }
  enableDrawing = false,
  drawOptions = {},  // { onDrawComplete, onVerticesUpdate }
  enableControls = true,
  controlRefs = {},  // { homeControlRef, fitDataControlRef, scaleControlRef }
  onMapInitialized = () => {},
}) => {
  // Store unstable dependencies in refs to avoid recreating callback
  const drawOptionsRef = useRef(drawOptions);
  const controlRefsRef = useRef(controlRefs);
  const onMapInitializedRef = useRef(onMapInitialized);
  
  // Update refs when dependencies change
  drawOptionsRef.current = drawOptions;
  controlRefsRef.current = controlRefs;
  onMapInitializedRef.current = onMapInitialized;

  const initMap = useCallback(() => {
    // ENHANCED VALIDATION - Check DOM element properly
    if (!useLeaflet || !mapData || !mapRef?.current || mapInstanceRef?.current) {
      console.log("Map init skipped:", { 
        useLeaflet, 
        hasMapData: !!mapData, 
        hasMapRef: !!mapRef?.current,
        hasMapInstance: !!mapInstanceRef?.current,
        mapRefTagName: mapRef?.current?.tagName 
      });
      return;
    }

    // Additional safety check for DOM element
    const mapElement = mapRef.current;
    if (!mapElement || !mapElement.tagName || mapElement.tagName.toLowerCase() !== 'div') {
      console.error("Invalid map DOM element:", mapElement);
      return;
    }

    console.log("Initializing map on element:", mapElement.tagName, mapElement);

    try {
      // === 1. Create Leaflet map & base image =================================
      mapInstanceRef.current = L.map(mapElement, {
        crs: L.CRS.Simple,
        zoomControl: true,
        minZoom: -5,
        maxZoom: 7,
        zoomAnimation: false,
        fadeAnimation: false,
        markerZoomAnimation: false,
      });

      const { bounds, url: imageUrl } = mapData; // Use 'url' from useMapData
      L.imageOverlay(imageUrl, bounds).addTo(mapInstanceRef.current);
      mapInstanceRef.current.fitBounds(bounds);
      
      console.log("Map created successfully with bounds:", bounds);

      // === 2. Optional drawing controls =======================================
      if (enableDrawing) {
        const drawnItems = new L.FeatureGroup();
        mapInstanceRef.current.addLayer(drawnItems);

        const drawControl = new L.Control.Draw({
          edit: { featureGroup: drawnItems, remove: false },
          draw: {
            polygon: {
              allowIntersection: false,
              showArea: true,
              ...drawOptionsRef.current.polygonOptions,
            },
            polyline: false,
            rectangle: false,
            circle: false,
            marker: false,
            circlemarker: false,
          },
        });
        mapInstanceRef.current.addControl(drawControl);

        mapInstanceRef.current.on(L.Draw.Event.CREATED, (e) => {
          const layer = e.layer;
          drawnItems.addLayer(layer);
          if (drawOptionsRef.current.onDrawComplete) drawOptionsRef.current.onDrawComplete(layer);
        });
        mapInstanceRef.current.on(L.Draw.Event.EDITED, () => {
          if (drawOptionsRef.current.onVerticesUpdate) drawOptionsRef.current.onVerticesUpdate(drawnItems);
        });
      }

      // === 3. Custom controls ==================================================
      if (enableControls) {
        const HomeControl = L.Control.extend({
          onAdd: function () {
            const container = L.DomUtil.create("div", "leaflet-bar leaflet-control leaflet-control-custom");
            container.style.backgroundColor = "white";
            container.style.width = "30px";
            container.style.height = "30px";
            container.style.cursor = "pointer";
            container.title = "Reset map view";
            container.innerHTML = "🏠";
            container.onclick = () => {
              if (mapInstanceRef.current) mapInstanceRef.current.fitBounds(bounds);
            };
            return container;
          },
        });
        
        if (controlRefsRef.current.homeControlRef) {
          controlRefsRef.current.homeControlRef.current = new HomeControl({ position: "topleft" });
          controlRefsRef.current.homeControlRef.current.addTo(mapInstanceRef.current);
        }

        // Other controls (FitData, Help, Scale) can be instantiated similarly
        // and attached via controlRefs.
      }

      // === 4. Map event listeners ============================================
      mapInstanceRef.current.on("zoomstart", () => {
        if (controlRefsRef.current.isZoomingRef) controlRefsRef.current.isZoomingRef.current = true;
        console.log("🔄 Zoom started - pausing marker updates");
      });
      
      mapInstanceRef.current.on("zoomend", () => {
        if (controlRefsRef.current.isZoomingRef) {
          controlRefsRef.current.isZoomingRef.current = false;
          console.log("✅ Zoom ended - resuming marker updates");
          if (controlRefsRef.current.pendingUpdateRef?.current) {
            controlRefsRef.current.pendingUpdateRef.current = false;
            if (controlRefsRef.current.executeMarkerUpdate) {
              controlRefsRef.current.executeMarkerUpdate();
              console.log("🔄 Executed pending marker update after zoom");
            }
          }
        }
      });

      mapInstanceRef.current.on('zoomend moveend', () => {
        console.log("User interacted with map, zoom/center locked");
      });

      // Notify parent once map is ready
      console.log("✅ Map initialization complete");
      onMapInitializedRef.current();
      
    } catch (error) {
      console.error("❌ Error during map initialization:", error);
    }
  }, [useLeaflet, mapData, mapRef, mapInstanceRef, enableDrawing, enableControls]); // FIXED: Removed unstable dependencies

  // Mount map once with proper timing
  useEffect(() => {
    // Small delay to ensure DOM is ready
    const timer = setTimeout(() => {
      initMap();
    }, 50);

    return () => {
      clearTimeout(timer);
      if (mapInstanceRef.current) {
        try {
          mapInstanceRef.current.remove();
          mapInstanceRef.current = null;
          console.log("🧹 Map cleaned up");
        } catch (error) {
          console.error("❌ Error during map cleanup:", error);
        }
      }
    };
  }, [initMap]);
};