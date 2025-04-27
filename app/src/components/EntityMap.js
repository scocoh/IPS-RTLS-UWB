// /home/parcoadmin/parco_fastapi/app/src/components/EntityMap.js
// Version: v0.1.1 - Fixed map initialization by ensuring ref is set, added logging
// Version: v0.1.0 - Initial implementation for Entity Merge Demo map
// ParcoRTLS © 2025 — Scott Cohen, Jesse Chunn, etc.
import React, { useEffect, useRef, useState } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import "./EntityMap.css";

const EntityMap = ({ devices, entities, entityAssignments, entityHierarchy, onMerge, onAssign }) => {
  const mapRef = useRef(null);
  const mapInstance = useRef(null);
  const deviceMarkersRef = useRef({});
  const entityMarkersRef = useRef({});
  const [isMapReady, setIsMapReady] = useState(false);

  // Log when the ref is set
  useEffect(() => {
    console.log("EntityMap: mapRef.current set to:", mapRef.current);
    if (mapRef.current) {
      setIsMapReady(true);
    }
  }, []);

  // Initialize the Leaflet map
  useEffect(() => {
    if (!isMapReady || mapInstance.current) {
      console.log("EntityMap: Skipping initialization - isMapReady:", isMapReady, "mapInstance.current:", !!mapInstance.current);
      return;
    }

    console.log("EntityMap: Initializing map...");
    try {
      mapInstance.current = L.map(mapRef.current, {
        crs: L.CRS.Simple,
        zoomControl: true,
        minZoom: -5,
        maxZoom: 7,
        attributionControl: false,
      });

      // Set default bounds
      const defaultBounds = [[0, 0], [1000, 1000]];
      mapInstance.current.fitBounds(defaultBounds);
      console.log("EntityMap bounds set to:", defaultBounds);

      // Add a simple background
      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: "© OpenStreetMap contributors",
        maxZoom: 7,
        minZoom: -5,
        tileSize: 256,
        zoomOffset: 0,
      }).addTo(mapInstance.current);

      // Add a static marker to test Leaflet functionality
      const staticMarker = L.marker([500, 500], {
        icon: L.divIcon({
          className: "static-marker",
          html: `<div style="background-color: purple; width: 15px; height: 15px; border-radius: 50%;"></div>`,
          iconSize: [15, 15],
          iconAnchor: [7.5, 7.5],
        }),
      }).addTo(mapInstance.current);
      staticMarker.bindTooltip("Static Test Marker", { permanent: true, direction: "top" });
      console.log("Static marker added at [500, 500]");

      console.log("EntityMap initialized successfully");
    } catch (error) {
      console.error("EntityMap: Failed to initialize map:", error);
    }

    return () => {
      if (mapInstance.current) {
        mapInstance.current.off();
        mapInstance.current.remove();
        console.log("EntityMap cleaned up");
        mapInstance.current = null;
        deviceMarkersRef.current = {};
        entityMarkersRef.current = {};
      }
    };
  }, [isMapReady]);

  // Add markers for devices (tags)
  useEffect(() => {
    if (!mapInstance.current || devices.length === 0) {
      console.log("Skipping device markers: mapInstance.current:", !!mapInstance.current, "devices.length:", devices.length);
      return;
    }

    console.log("Adding device markers...");
    devices.forEach(device => {
      let latLng;
      if (device.n_moe_x === null || device.n_moe_y === null || isNaN(device.n_moe_x) || isNaN(device.n_moe_y)) {
        console.log(`Device ${device.x_id_dev} has missing or invalid coordinates (n_moe_x: ${device.n_moe_x}, n_moe_y: ${device.n_moe_y}), using default position`);
        latLng = [500, 500];
      } else {
        latLng = [device.n_moe_y, device.n_moe_x];
      }

      let marker = deviceMarkersRef.current[device.x_id_dev];
      if (!marker) {
        try {
          marker = L.marker(latLng, {
            draggable: true,
            icon: L.divIcon({
              className: "device-marker",
              html: `<div style="background-color: red; width: 10px; height: 10px; border-radius: 50%;"></div>`,
              iconSize: [10, 10],
              iconAnchor: [5, 5],
            }),
            zIndexOffset: 1000,
          }).addTo(mapInstance.current);

          marker.bindTooltip(`Tag ${device.x_id_dev}`, { permanent: false, direction: "top" });
          deviceMarkersRef.current[device.x_id_dev] = marker;
          console.log(`Tag marker created for ${device.x_id_dev} at:`, latLng);

          marker.on("dragend", async () => {
            const draggedDeviceId = device.x_id_dev;
            const draggedPosition = marker.getLatLng();

            for (const [otherDeviceId, otherMarker] of Object.entries(deviceMarkersRef.current)) {
              if (draggedDeviceId === otherDeviceId) continue;
              const otherPosition = otherMarker.getLatLng();
              const distance = mapInstance.current.distance(draggedPosition, otherPosition);
              console.log(`Distance between ${draggedDeviceId} and ${otherDeviceId}: ${distance} pixels`);

              if (distance < 30) {
                const parentChoice = window.prompt(
                  `Merge tags ${draggedDeviceId} and ${otherDeviceId} into a new entity?\n` +
                  `Enter '1' to make ${draggedDeviceId} the parent, '2' for ${otherDeviceId}, or 'cancel' to abort:`
                );
                if (parentChoice === "1" || parentChoice === "2") {
                  const parentDeviceId = parentChoice === "1" ? draggedDeviceId : otherDeviceId;
                  const childDeviceId = parentChoice === "1" ? otherDeviceId : draggedDeviceId;
                  if (onMerge) onMerge(parentDeviceId, childDeviceId);
                }
                break;
              }
            }

            for (const [entityId, entityMarker] of Object.entries(entityMarkersRef.current)) {
              const entityPosition = entityMarker.getLatLng();
              const distance = mapInstance.current.distance(draggedPosition, entityPosition);
              console.log(`Distance between ${draggedDeviceId} and entity ${entityId}: ${distance} pixels`);

              if (distance < 30) {
                const hierarchy = entityHierarchy[entityId] || {};
                const devicesInEntity = Object.keys(hierarchy);
                const options = [
                  `1: Add as child of parent entity ${entityId}`,
                  ...devicesInEntity.map((devId, idx) => `${idx + 2}: Add as grandchild under ${devId}`),
                ];
                const choice = window.prompt(
                  `Add tag ${draggedDeviceId} to entity ${entityId}?\n` +
                  options.join("\n") + "\nEnter number or 'cancel' to abort:"
                );
                if (choice && choice !== "cancel" && !isNaN(choice)) {
                  const optionIndex = parseInt(choice);
                  if (optionIndex === 1) {
                    if (onAssign) onAssign(draggedDeviceId, entityId, null);
                  } else if (optionIndex >= 2 && optionIndex <= devicesInEntity.length + 1) {
                    const childDeviceId = devicesInEntity[optionIndex - 2];
                    const childEntityId = hierarchy[childDeviceId].x_id_ent;
                    if (onAssign) onAssign(draggedDeviceId, childEntityId, entityId);
                  }
                }
                break;
              }
            }
          });
        } catch (error) {
          console.error(`Failed to create marker for device ${device.x_id_dev}:`, error);
        }
      } else {
        marker.setLatLng(latLng);
        console.log(`Tag marker updated for ${device.x_id_dev} to:`, latLng);
      }
    });
  }, [devices, onMerge, onAssign, entityHierarchy]);

  // Add markers for entities
  useEffect(() => {
    if (!mapInstance.current || entities.length === 0) {
      console.log("Skipping entity markers: mapInstance.current:", !!mapInstance.current, "entities.length:", entities.length);
      return;
    }

    console.log("Adding entity markers...");
    entities.forEach(entity => {
      let latLng;
      const assignments = entityAssignments[entity.x_id_ent] || [];
      if (assignments.length > 0) {
        const parentDevice = assignments.find(a => !a.x_id_pnt);
        const device = devices.find(d => d.x_id_dev === parentDevice?.x_id_dev);
        if (!device || device.n_moe_x === null || device.n_moe_y === null || isNaN(device.n_moe_x) || isNaN(device.n_moe_y)) {
          console.log(`No valid coordinates for entity ${entity.x_id_ent} parent device ${parentDevice?.x_id_dev}, using default position`);
          latLng = [500, 500];
        } else {
          latLng = [device.n_moe_y, device.n_moe_x];
        }
      } else {
        console.log(`No assignments for entity ${entity.x_id_ent}, using default position`);
        latLng = [500, 500];
      }

      let marker = entityMarkersRef.current[entity.x_id_ent];
      if (!marker) {
        try {
          marker = L.marker(latLng, {
            draggable: false,
            icon: L.divIcon({
              className: "entity-marker",
              html: `<div style="background-color: blue; width: 10px; height: 10px;"></div>`,
              iconSize: [10, 10],
              iconAnchor: [5, 5],
            }),
            zIndexOffset: 2000,
          }).addTo(mapInstance.current);

          const hierarchy = entityHierarchy[entity.x_id_ent] || {};
          const devicesInEntity = Object.keys(hierarchy);
          const tooltipContent = `Entity ${entity.x_id_ent}<br>Contains: ${devicesInEntity.join(", ") || "None"}`;
          marker.bindTooltip(tooltipContent, { permanent: false, direction: "top" });
          entityMarkersRef.current[entity.x_id_ent] = marker;
          console.log(`Entity marker created for ${entity.x_id_ent} at:`, latLng);
        } catch (error) {
          console.error(`Failed to create marker for entity ${entity.x_id_ent}:`, error);
        }
      } else {
        marker.setLatLng(latLng);
        console.log(`Entity marker updated for ${entity.x_id_ent} to:`, latLng);
      }
    });
  }, [entities, entityAssignments, devices, entityHierarchy]);

  return (
    <div>
      <div ref={mapRef} style={{ height: "600px", width: "100%", border: "2px solid black" }} />
    </div>
  );
};

export default EntityMap;