import React, { useEffect, useRef, useState, memo } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css"; // Leaflet core CSS
import "leaflet-draw/dist/leaflet.draw.css"; // Leaflet.Draw CSS
import "leaflet-draw"; // Import Leaflet.Draw

const Map = memo(({ zoneId, onDrawComplete, triggerColor }) => {
  const mapRef = useRef(null);
  const mapInstance = useRef(null);
  const drawnItems = useRef(new L.FeatureGroup()); // Persist drawn items
  const [mapData, setMapData] = useState(null);
  const [error, setError] = useState(null);
  const isInitialized = useRef(false); // Flag to prevent multiple initializations

  // Debug mount/unmount
  useEffect(() => {
    console.log("Map component mounted with zoneId:", zoneId);
    return () => {
      console.log("Map component unmounted with zoneId:", zoneId);
    };
  }, [zoneId]);

  // Fetch map data when zoneId changes
  useEffect(() => {
    if (zoneId && !mapData) {
      const fetchMapData = async () => {
        try {
          const response = await fetch(`/maps/get_map_data/${zoneId}`);
          if (!response.ok) {
            const text = await response.text();
            throw new Error(`HTTP error! status: ${response.status}, response: ${text}`);
          }
          const data = await response.json();
          console.log("Map data fetched:", data);
          setMapData(data);
          setError(null);
        } catch (error) {
          console.error("Error fetching map data:", error);
          setError(`Error fetching map data: ${error.message}`);
        }
      };

      fetchMapData();
    }
  }, [zoneId, mapData]);

  // Initialize the Leaflet map when mapData is available
  useEffect(() => {
    if (mapData && mapRef.current && !isInitialized.current) {
      try {
        // Initialize the map with a simple CRS for non-geographic maps
        mapInstance.current = L.map(mapRef.current, {
          crs: L.CRS.Simple,
          minZoom: -5,
          maxZoom: 5,
          zoomControl: true,
          // Disable default tile layer
          attributionControl: false,
        });

        // Remove default tile layer
        mapInstance.current.eachLayer((layer) => {
          if (layer instanceof L.TileLayer) {
            mapInstance.current.removeLayer(layer);
          }
        });

        // Correct the bounds interpretation: API returns [[yMin, xMin], [yMax, xMax]]
        // Expected: [[xMin, yMin], [xMax, yMax]] = [[-80, -40], [160, 160]]
        const boundsFromApi = [
          [mapData.bounds[0][1], mapData.bounds[0][0]], // [xMin, yMin]
          [mapData.bounds[1][1], mapData.bounds[1][0]], // [xMax, yMax]
        ];
        const xMin = boundsFromApi[0][0]; // -80
        const xMax = boundsFromApi[1][0]; // 160
        const yMin = boundsFromApi[0][1]; // -40
        const yMax = boundsFromApi[1][1]; // 160
        const xRange = xMax - xMin; // 240
        const yRange = yMax - yMin; // 200

        // Test image load with timeout
        const img = new Image();
        img.crossOrigin = "anonymous";
        img.src = mapData.imageUrl;

        const imageLoadTimeout = setTimeout(() => {
          if (!img.complete) {
            setError("Map image load timed out. Please check the image URL.");
            console.error("Map image load timed out:", mapData.imageUrl);
          }
        }, 5000); // 5-second timeout

        img.onload = () => {
          clearTimeout(imageLoadTimeout);
          console.log("Map image loaded successfully:", mapData.imageUrl, "Dimensions:", img.width, "x", img.height);

          // Calculate container dimensions to match image aspect ratio
          const imageAspectRatio = img.width / img.height; // 721/601 ≈ 1.2
          const containerHeight = 500; // Fixed height
          const containerWidth = containerHeight * imageAspectRatio; // 500 * 1.2 = 600px

          // Map logical bounds (240x200 feet) to container dimensions (600x500px)
          const pixelBounds = [
            [0, 0], // Bottom-left in pixel coordinates
            [containerWidth, containerHeight], // Top-right in pixel coordinates
          ];

          // Apply the image overlay with pixel-based bounds
          L.imageOverlay(mapData.imageUrl, pixelBounds).addTo(mapInstance.current);
          mapInstance.current.fitBounds(pixelBounds);

          // Add persistent drawn items layer
          mapInstance.current.addLayer(drawnItems.current);

          const colorMap = {
            Red: "#ff0000",
            Green: "#00ff00",
            Blue: "#0000ff",
          };

          const drawControl = new L.Control.Draw({
            edit: {
              featureGroup: drawnItems.current,
            },
            draw: {
              polygon: {
                shapeOptions: {
                  color: colorMap[triggerColor] || "#ff0000", // Use selected color
                  weight: 2,
                },
              },
              rectangle: false,
              polyline: false,
              circle: false,
              marker: false,
              circlemarker: false,
            },
          });
          mapInstance.current.addControl(drawControl);

          mapInstance.current.on(L.Draw.Event.CREATED, (event) => {
            const layer = event.layer;
            drawnItems.current.addLayer(layer);
            // Transform coordinates to match X-Y order based on pixel bounds
            const coords = layer.getLatLngs()[0].map((latLng, index) => {
              // Log raw latLng for debugging
              console.log(`Raw latLng for point ${index + 1}:`, { lat: latLng.lat, lng: latLng.lng });

              // In L.CRS.Simple: lat = y, lng = x, normalized to [0, 1]
              const xPixelRange = pixelBounds[1][0] - pixelBounds[0][0]; // 600
              const yPixelRange = pixelBounds[1][1] - pixelBounds[0][1]; // 500
              const xPixel = latLng.lng * xPixelRange; // Map to [0, 600]
              const yPixel = (1 - latLng.lat) * yPixelRange; // Map to [0, 500], flip y-axis

              // Map pixel coordinates back to logical coordinates
              const x = xMin + (xPixel / containerWidth) * xRange; // Map to [-80, 160]
              const y = yMin + (yPixel / containerHeight) * yRange; // Map to [-40, 160]
              return { n_x: x, n_y: y, n_z: 0, n_ord: index + 1 }; // Match vertex format
            });
            console.log("Drawn coordinates (X, Y):", coords);
            if (onDrawComplete) {
              onDrawComplete(JSON.stringify(coords));
            }
          });

          // Set the container dimensions to match the aspect ratio
          if (mapRef.current) {
            mapRef.current.style.width = `${containerWidth}px`;
            mapRef.current.style.height = `${containerHeight}px`;
            mapRef.current.style.background = "none"; // Remove Leaflet grid background
          }

          isInitialized.current = true; // Mark as initialized
        };

        img.onerror = () => {
          clearTimeout(imageLoadTimeout);
          console.error("Failed to load map image:", mapData.imageUrl);
          setError("Failed to load map image. Please check the server response.");
        };
      } catch (error) {
        console.error("Error initializing map:", error);
        setError(`Error initializing map: ${error.message}`);
      }
    }

    // Cleanup on unmount
    return () => {
      if (mapInstance.current) {
        mapInstance.current.remove();
        mapInstance.current = null;
        isInitialized.current = false; // Reset initialization flag
      }
      if (mapData) {
        const img = new Image();
        img.src = mapData.imageUrl; // Clear any pending loads
      }
    };
  }, [mapData, onDrawComplete, triggerColor]);

  return (
    <div>
      {error && <div style={{ color: "red", marginBottom: "10px" }}>{error}</div>}
      <div ref={mapRef} style={{ height: "500px", width: "100%" }} />
    </div>
  );
});

export default Map;