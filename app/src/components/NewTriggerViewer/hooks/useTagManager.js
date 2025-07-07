// hooks/useTagManager.js  • ParcoRTLS v0.1.8
// -----------------------------------------------------------------------------
// Tag‑marker lifecycle management extracted from NewTriggerViewer (v0.1.7).
// Handles creation, updating, greying & removal of markers with extended
// time‑outs (10 s‑>gray, 5 min‑>remove), portable–trigger scaling, responsive
// auto‑zoom on first tag, visibility filtering, and WebSocket disconnect state.
// -----------------------------------------------------------------------------
// Public API (100 % backward‑compatible):
//   const {
//     tagMarkersRef,          // readonly • map of tagId → Leaflet marker
//     executeMarkerUpdate,    // imperative update fn (rarely needed)
//   } = useTagManager({ ...params });
//
// The hook self‑schedules updates whenever its reactive deps change, so the
// parent component normally does **not** call executeMarkerUpdate manually.
// -----------------------------------------------------------------------------

import { useRef, useEffect, useCallback } from "react";
import L from "leaflet";

export const useTagManager = ({
  // === Map & mode flags =====================================================
  useLeaflet = true,          // whether we are running in Leaflet mode
  mapInstanceRef,            // ref.current MUST hold a live Leaflet map
  mapData,                   // { bounds: [[y0,x0],[y1,x1]], imageUrl: ... }
  mapInitialized = false,    // set true once mapInstanceRef.current is ready
  // === Application data =====================================================
  zones = [],                // [{ i_zn, ... }]  – zone list (first = selected)
  tagsData = {},             // live tag positions keyed by tagId
  triggers = [],             // full triggers array (portable & zone)
  hiddenTags = new Set(),    // Set<tagId> that user has hidden
  isConnected = true,        // websocket connectivity flag
  // === Zoom‑coordination refs (supplied by useMapSetup) =====================
  isZoomingRef,              // ref<boolean> – true while user is zooming
  pendingUpdateRef,          // ref<boolean> – flag a postponed update
}) => {
  // -------------------------------------------------------------------------
  // Refs that must persist across re‑renders – identical semantics to the
  // originals inside NewTriggerViewer.
  // -------------------------------------------------------------------------
  const tagMarkersRef      = useRef({});   // tagId → L.Marker
  const tagLastSeenRef     = useRef({});   // tagId → timestamp (ms)
  const tagTimeoutRef      = useRef({});   // tagId → timeoutHandle
  const tagLastPositionRef = useRef({});   // tagId → "x,y" string
  const firstTagAppearance = useRef(true); // used for initial auto‑zoom
  const updateTimeoutRef   = useRef(null); // debounce for high‑freq data

  // -------------------------------------------------------------------------
  // Helper: create / update / gray / remove a single marker (extracted inline
  // from the original executeMarkerUpdate for clarity).
  // -------------------------------------------------------------------------
  const upsertMarker = useCallback((tagId, tagData, markerSize, tooltip) => {
    const { x, y } = tagData;
    const latLng = [y, x];

    let marker = tagMarkersRef.current[tagId];
    if (!marker) {
      marker = L.marker(latLng, {
        icon: L.divIcon({
          className: "tag-marker",
          html: `<div style="background-color: red; width: ${markerSize}px; height: ${markerSize}px; border-radius: 50%;"></div>`,
          iconSize: [markerSize, markerSize],
          iconAnchor: [markerSize / 2, markerSize / 2],
        }),
        zIndexOffset: 1000,
      }).addTo(mapInstanceRef.current);
      marker.bindTooltip(tooltip, { permanent: false, direction: "top" });
      tagMarkersRef.current[tagId] = marker;
    } else {
      // Position change?
      const positionKey = `${x},${y}`;
      if (tagLastPositionRef.current[tagId] !== positionKey) {
        marker.setLatLng(latLng);
        tagLastPositionRef.current[tagId] = positionKey;
      }
      // Tooltip refresh
      marker.setTooltipContent(tooltip);
      // Size change?
      const currentSize = marker.options.icon.options.iconSize[0];
      if (currentSize !== markerSize) {
        marker.setIcon(L.divIcon({
          className: "tag-marker",
          html: `<div style="background-color: red; width: ${markerSize}px; height: ${markerSize}px; border-radius: 50%;"></div>`,
          iconSize: [markerSize, markerSize],
          iconAnchor: [markerSize / 2, markerSize / 2],
        }));
      }
    }
  }, [mapInstanceRef]);

  // -------------------------------------------------------------------------
  // Core algorithm – identical to original executeMarkerUpdate but extracted
  // into a stable callback so it can be used both internally & imperatively.
  // -------------------------------------------------------------------------
  const executeMarkerUpdate = useCallback(() => {
    if (!useLeaflet || !mapInstanceRef.current || !mapData || !mapInitialized) {
      return;
    }

    const selectedZoneId = zones[0]?.i_zn ?? "N/A";
    const now = Date.now();

    // === 1. Process incoming tag data ======================================
    Object.entries(tagsData).forEach(([tagId, tagData]) => {
      // Zone filter – identical to old behaviour
      const tagZoneId = tagData.zone_id ?? selectedZoneId;
      if (tagZoneId !== selectedZoneId) return;
      if (hiddenTags.has(tagId)) return; // user‑hidden

      // Last‑seen bookkeeping
      tagLastSeenRef.current[tagId] = now;
      if (tagTimeoutRef.current[tagId]) {
        clearTimeout(tagTimeoutRef.current[tagId]);
        delete tagTimeoutRef.current[tagId];
      }

      // Ignore out‑of‑bounds positions to match map bounds
      const { x, y } = tagData;
      const latLng = [y, x];
      if (!L.latLngBounds(mapData.bounds).contains(latLng)) return;

      // Portable‑trigger scaling
      const associatedTrigger = triggers?.find(
        (t) => t.is_portable && t.assigned_tag_id === tagId
      );
      const markerSize = associatedTrigger && associatedTrigger.radius_ft
        ? Math.round(10 * (associatedTrigger.radius_ft / 3))
        : 10;

      // Render / update marker
      const tooltip = `Tag ${tagId}<br/>Zone: ${tagZoneId}<br/>Pos: (${x.toFixed(
        2
      )}, ${y.toFixed(2)})`;
      upsertMarker(tagId, tagData, markerSize, tooltip);

      // Auto‑zoom on very first tag appearance
      if (
        firstTagAppearance.current &&
        Object.keys(tagMarkersRef.current).length === 1
      ) {
        mapInstanceRef.current.setView(latLng, 7, { animate: false });
        firstTagAppearance.current = false;
      }
    });

    // === 2. Grey‑out or remove stale markers ===============================
    Object.keys(tagMarkersRef.current).forEach((tagId) => {
      const lastSeen = tagLastSeenRef.current[tagId];
      const timeSince = now - (lastSeen ?? 0);

      // Tag disappeared from live feed
      if (!tagsData[tagId]) {
        if (timeSince > 300_000) {
          // remove after 5 min
          const m = tagMarkersRef.current[tagId];
          if (m && mapInstanceRef.current.hasLayer(m)) {
            mapInstanceRef.current.removeLayer(m);
          }
          delete tagMarkersRef.current[tagId];
          delete tagLastSeenRef.current[tagId];
          delete tagLastPositionRef.current[tagId];
          if (tagTimeoutRef.current[tagId]) {
            clearTimeout(tagTimeoutRef.current[tagId]);
            delete tagTimeoutRef.current[tagId];
          }
        } else if (timeSince > 10_000) {
          // grey after 10 s
          const m = tagMarkersRef.current[tagId];
          if (m) {
            const sz = 10;
            m.setIcon(
              L.divIcon({
                className: "tag-marker-stale",
                html: `<div style=\"background-color: gray; width: ${sz}px; height: ${sz}px; border-radius: 50%; opacity: 0.7;\"></div>`,
                iconSize: [sz, sz],
                iconAnchor: [sz / 2, sz / 2],
              })
            );
            if (!tagTimeoutRef.current[tagId]) {
              tagTimeoutRef.current[tagId] = setTimeout(() => {
                const marker = tagMarkersRef.current[tagId];
                if (marker && mapInstanceRef.current.hasLayer(marker)) {
                  mapInstanceRef.current.removeLayer(marker);
                }
                delete tagMarkersRef.current[tagId];
                delete tagLastSeenRef.current[tagId];
                delete tagLastPositionRef.current[tagId];
                delete tagTimeoutRef.current[tagId];
              }, 300_000 - timeSince);
            }
          }
        }
      }
    });

    // === 3. Disconnection shading (all markers red w/ 0.5 opacity) =========
    if (!isConnected) {
      Object.values(tagMarkersRef.current).forEach((marker) => {
        const sz = 10;
        marker.setIcon(
          L.divIcon({
            className: "tag-marker-disconnected",
            html: `<div style=\"background-color: red; width: ${sz}px; height: ${sz}px; border-radius: 50%; opacity: 0.5;\"></div>`,
            iconSize: [sz, sz],
            iconAnchor: [sz / 2, sz / 2],
          })
        );
      });
    }
  }, [
    useLeaflet,
    mapInstanceRef,
    mapData,
    mapInitialized,
    zones,
    tagsData,
    triggers,
    hiddenTags,
    isConnected,
    upsertMarker,
  ]);

  // -------------------------------------------------------------------------
  // Debounced update effect (≈ original tag‑marker useEffect) ---------------
  // -------------------------------------------------------------------------
  useEffect(() => {
    if (!useLeaflet || !mapInstanceRef.current || !mapData || !mapInitialized) {
      return;
    }

    if (updateTimeoutRef.current) clearTimeout(updateTimeoutRef.current);

    updateTimeoutRef.current = setTimeout(() => {
      // Defer update during zoom animations
      if (isZoomingRef?.current) {
        pendingUpdateRef.current = true;
        return;
      }
      executeMarkerUpdate();
    }, 100);

    return () => {
      if (updateTimeoutRef.current) clearTimeout(updateTimeoutRef.current);
    };
  }, [
    useLeaflet,
    mapInstanceRef,
    mapData,
    mapInitialized,
    tagsData,
    hiddenTags,
    isConnected,
    triggers,
    executeMarkerUpdate,
    isZoomingRef,
    pendingUpdateRef,
  ]);

  // -------------------------------------------------------------------------
  // Global cleanup on unmount (clear all pending timeouts) -------------------
  // -------------------------------------------------------------------------
  useEffect(() => () => {
    Object.values(tagTimeoutRef.current).forEach(clearTimeout);
    tagTimeoutRef.current = {};
    tagLastSeenRef.current = {};
    tagLastPositionRef.current = {};
  }, []);

  // Expose (readonly) refs + imperative fn
  return {
    tagMarkersRef,
    executeMarkerUpdate, // exposed mainly for test harnesses
  };
};
