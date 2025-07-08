/* Name: mapUtils.js */
/* Version: 0.1.0 */
/* Created: 971201 */
/* Modified: 250502 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin */
/* Description: ParcoRTLS frontend script */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/NewTriggerViewer/utils */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

// utils/mapUtils.js  • ParcoRTLS v0.1.8
// -----------------------------------------------------------------------------
// Canvas drawing helpers and coordinate converters used by NewTriggerViewer.
// -----------------------------------------------------------------------------
import L from "leaflet";

export const drawZones = ({ ctx, zones, mapData, scale = 1 }) => {
  if (!ctx || !zones?.length || !mapData) return;
  ctx.save();
  ctx.lineWidth = 2 * scale;
  ctx.strokeStyle = "blue";
  zones.forEach((zn) => {
    if (!zn.vertices?.length) return;
    ctx.beginPath();
    zn.vertices.forEach((v, idx) => {
      const { x, y } = worldToCanvas(v, mapData);
      if (idx === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    });
    ctx.closePath();
    ctx.stroke();
  });
  ctx.restore();
};

export const drawTriggers = ({ ctx, triggers, mapData, scale = 1 }) => {
  if (!ctx || !triggers?.length || !mapData) return;
  ctx.save();
  triggers.forEach((trg) => {
    if (trg.isPortable && trg.center) {
      const { x, y } = worldToCanvas(trg.center, mapData);
      ctx.strokeStyle = "purple";
      ctx.lineWidth = 2 * scale;
      ctx.beginPath();
      ctx.arc(x, y, trg.radius_ft * scale, 0, 2 * Math.PI);
      ctx.stroke();
    } else if (trg.latLngs) {
      ctx.strokeStyle = "blue";
      ctx.lineWidth = 2 * scale;
      ctx.beginPath();
      trg.latLngs.forEach((p, idx) => {
        const { x, y } = worldToCanvas(p, mapData);
        if (idx === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      });
      ctx.closePath();
      ctx.stroke();
    }
  });
  ctx.restore();
};

export const worldToCanvas = ({ x, y }, mapData) => {
  const { bounds } = mapData;
  const [ [y0, x0], [y1, x1] ] = bounds; // bounds are [[y0,x0],[y1,x1]]
  const width  = Math.abs(x1 - x0);
  const height = Math.abs(y1 - y0);
  return {
    x: ((x - x0) / width)  * mapData.canvasWidth,
    y: ((y - y0) / height) * mapData.canvasHeight,
  };
};
