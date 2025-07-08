/* Name: useMapData.js */
/* Version: 0.1.0 */
/* Created: 971201 */
/* Modified: 250502 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin */
/* Description: ParcoRTLS frontend script */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/NewTriggerViewer/hooks */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

// components/NewTriggerViewer/hooks/useMapData.js
// Version: 0.2.9 • 2025‑07‑06
// -----------------------------------------------------------------------------
//   ✓ Compatible with Zone‑Builder & Zone‑Viewer «/get_map_data» responses
//     which return  { imageUrl, bounds }  (no explicit width / height).
//   ✓ Computes width / height from bounds so callers relying on them still work.
//   ✓ Robust URL fix‑up (prepend host if backend returned a relative path).
// -----------------------------------------------------------------------------

import { useEffect, useState } from "react";

export const useMapData = ({
  mapId,
  serverHost = window.location.hostname, // 192.168.210.226
  zoneBuilder = true,                    // flip if you call zoneviewer service instead
  onError = () => {},
}) => {
  const [mapData, setMapData]  = useState(null);   // { url, bounds, width, height }
  const [isConnected, setConn] = useState(false);

  useEffect(() => {
    if (!mapId) return;

    const abort = new AbortController();
    const base   = zoneBuilder ? "zonebuilder" : "zoneviewer";
    const metaURL = `http://${serverHost}:8000/${base}/get_map_data/${mapId}`;

    (async () => {
      try {
        const res = await fetch(metaURL, { signal: abort.signal });
        if (!res.ok) throw new Error(`HTTP ${res.status} on ${metaURL}`);

        /* FastAPI returns → {
             imageUrl: "/zonebuilder/get_map/29" | "http://host:8000/…",
             bounds  : [[minY,minX],[maxY,maxX]]
           }
        */
        const json = await res.json();
        if (!json.bounds || json.bounds.length !== 2) {
          throw new Error("Response missing valid bounds array");
        }

        // Fix relative imageUrl → full URL
        let url = json.imageUrl;
        if (!url.startsWith("http")) {
          url = `http://${serverHost}:8000${url.startsWith("/") ? "" : "/"}${url}`;
        }

        const [[minY, minX], [maxY, maxX]] = json.bounds;
        const width  = Math.abs(maxX - minX);
        const height = Math.abs(maxY - minY);

        setMapData({ url, bounds: json.bounds, width, height });
        setConn(true);
      } catch (err) {
        console.error("Map metadata fetch error:", err);
        onError(err);
        setConn(false);
      }
    })();

    return () => abort.abort();
  }, [mapId, serverHost, zoneBuilder, onError]);

  return { mapData, isConnected };
};
