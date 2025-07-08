/* Name: MapControls.js */
/* Version: 0.1.0 */
/* Created: 971201 */
/* Modified: 250502 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin */
/* Description: ParcoRTLS frontend script */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/NewTriggerViewer/components */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

// components/MapControls.js  • ParcoRTLS v0.2.0 - FIXED DUPLICATE CONTROLS
// -----------------------------------------------------------------------------
// Reusable Leaflet custom controls extracted from NewTriggerViewer.js.
// Home (🏠), Fit-to-Data (📏), Help (?) and built‑in ScaleControl wrapper.
// FIXED: Enhanced cleanup to prevent duplicate controls
// -----------------------------------------------------------------------------
import { useEffect, useRef } from "react";
import L from "leaflet";

export const MapControls = ({
  mapInstance,
  onHomeClick = () => {},
  onFitDataClick = () => {},
  onHelpClick = () => {},
  showScale = true,
}) => {
  // Store control references for reliable cleanup
  const controlsRef = useRef({
    home: null,
    fit: null,
    help: null,
    scale: null
  });

  useEffect(() => {
    // COMPREHENSIVE VALIDATION - Check map is fully ready including control corners
    if (!mapInstance || 
        !mapInstance._container || 
        !mapInstance._loaded || 
        !mapInstance._controlCorners ||
        !mapInstance._controlCorners.topleft) {
      console.log("MapControls: Map not ready yet", {
        hasInstance: !!mapInstance,
        hasContainer: !!mapInstance?._container,
        isLoaded: !!mapInstance?._loaded,
        hasControlCorners: !!mapInstance?._controlCorners,
        hasTopLeft: !!mapInstance?._controlCorners?.topleft
      });
      return;
    }

    // Clear any existing controls first
    const clearExistingControls = () => {
      Object.values(controlsRef.current).forEach(control => {
        if (control && mapInstance) {
          try {
            mapInstance.removeControl(control);
          } catch (e) {
            // Ignore errors if control already removed
          }
        }
      });
      controlsRef.current = { home: null, fit: null, help: null, scale: null };
    };

    clearExistingControls();
    console.log("MapControls: Adding controls to ready map");

    try {
      // Home Control
      const HomeControl = L.Control.extend({
        onAdd: function () {
          const container = L.DomUtil.create("div", "leaflet-bar leaflet-control leaflet-control-custom");
          container.style.backgroundColor = "white";
          container.style.width = "30px";
          container.style.height = "30px";
          container.style.cursor = "pointer";
          container.style.fontSize = "16px";
          container.style.textAlign = "center";
          container.style.lineHeight = "30px";
          container.title = "Reset map view";
          container.innerHTML = "🏠";
          container.onclick = onHomeClick;
          return container;
        },
      });
      controlsRef.current.home = new HomeControl({ position: "topleft" });
      controlsRef.current.home.addTo(mapInstance);

      // Fit-to-Data Control
      const FitDataControl = L.Control.extend({
        onAdd: function () {
          const container = L.DomUtil.create("div", "leaflet-bar leaflet-control leaflet-control-custom");
          container.style.backgroundColor = "white";
          container.style.width = "30px";
          container.style.height = "30px";
          container.style.cursor = "pointer";
          container.style.fontSize = "16px";
          container.style.textAlign = "center";
          container.style.lineHeight = "30px";
          container.title = "Fit map to show all data";
          container.innerHTML = "📏";
          container.onclick = onFitDataClick;
          return container;
        },
      });
      controlsRef.current.fit = new FitDataControl({ position: "topleft" });
      controlsRef.current.fit.addTo(mapInstance);

      // Help Control
      const HelpControl = L.Control.extend({
        onAdd: function () {
          const container = L.DomUtil.create("div", "leaflet-bar leaflet-control leaflet-control-custom");
          container.style.backgroundColor = "white";
          container.style.width = "30px";
          container.style.height = "30px";
          container.style.cursor = "pointer";
          container.style.fontSize = "16px";
          container.style.textAlign = "center";
          container.style.lineHeight = "30px";
          container.style.fontWeight = "bold";
          container.title = "Show keyboard shortcuts";
          container.innerHTML = "?";
          container.onclick = onHelpClick;
          return container;
        },
      });
      controlsRef.current.help = new HelpControl({ position: "topleft" });
      controlsRef.current.help.addTo(mapInstance);

      // Scale Control
      if (showScale) {
        controlsRef.current.scale = L.control.scale({ 
          metric: true, 
          imperial: false,
          position: "bottomleft" 
        });
        controlsRef.current.scale.addTo(mapInstance);
      }

      console.log("✅ All map controls added successfully");

    } catch (error) {
      console.error("❌ Error adding map controls:", error);
    }

    // Enhanced cleanup function
    return () => {
      console.log("🧹 MapControls cleanup starting");
      try {
        Object.entries(controlsRef.current).forEach(([name, control]) => {
          if (control && mapInstance) {
            try {
              mapInstance.removeControl(control);
              console.log(`🧹 Removed ${name} control`);
            } catch (error) {
              console.warn(`⚠️ Could not remove ${name} control:`, error.message);
            }
          }
        });
        controlsRef.current = { home: null, fit: null, help: null, scale: null };
        console.log("🧹 Map controls cleanup complete");
      } catch (error) {
        console.error("❌ Error during controls cleanup:", error);
      }
    };
  }, [mapInstance, onHomeClick, onFitDataClick, onHelpClick, showScale]);

  return null; // controls attach directly to Leaflet map
};