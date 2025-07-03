/* Name: formatters.js */
/* Version: 0.1.0 */
/* Created: 250625 */
/* Modified: 250625 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin + Claude */
/* Description: Formatting utilities for NewTriggerDemo */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/NewTriggerDemo/utils */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

// Format timestamp in YYMMDD HHMMSS format
export const getFormattedTimestamp = () => {
  const now = new Date();
  const pad = (val) => String(val).padStart(2, "0");
  return `${String(now.getFullYear()).slice(-2)}${pad(now.getMonth() + 1)}${pad(now.getDate())} ${pad(now.getHours())}${pad(now.getMinutes())}${pad(now.getSeconds())}`;
};

// Format tag data for display
export const formatTagInfo = (tagData, selectedZone, zones, tagCount, tagRate) => {
  if (!tagData || Object.keys(tagData).length === 0) {
    return "No tag data";
  }

  return Object.values(tagData).map(data => {
    const zoneId = data.zone_id || selectedZone?.i_zn || "N/A";
    const zoneName = zones.find(z => z.i_zn === zoneId)?.x_nm_zn || "Unknown";
    
    return `Tag ${data.id} (Zone ${zoneId} - ${zoneName}): X=${data.x}, Y=${data.y}, Z=${data.z}, Sequence=${data.sequence}, Counts=${tagCount}, Tags/sec=${tagRate.toFixed(2)}`;
  }).join('\n');
};

// Format coordinates for display
export const formatCoordinate = (value, decimals = 6) => {
  return Number(value).toFixed(decimals);
};

// Format trigger event message
export const formatTriggerEvent = (data, trigger, zones, sequenceNumbers, tagsData) => {
  const zoneName = zones.find(z => z.i_zn === trigger.i_zn)?.x_nm_zn || "Unknown";
  const sequenceNumber = sequenceNumbers[data.tag_id] || (tagsData[data.tag_id]?.sequence || "N/A");
  
  if (data.assigned_tag_id && data.tag_id !== data.assigned_tag_id) {
    return `${data.tag_id} within ${data.assigned_tag_id} Trigger ${trigger.i_trg} (Zone ${trigger.i_zn} - ${zoneName}, Seq ${sequenceNumber}) at ${data.timestamp}`;
  } else {
    return `Tag ${data.tag_id} ${data.direction} trigger ${trigger.i_trg} (Zone ${trigger.i_zn} - ${zoneName}, Seq ${sequenceNumber}) at ${data.timestamp}`;
  }
};

// Format WebSocket status message
export const formatWebSocketStatus = (type, status, timestamp, details = {}) => {
  const base = `${type} WebSocket ${status} on ${timestamp}`;
  
  if (details.code || details.reason) {
    return `${base} (code: ${details.code || 'N/A'}, reason: ${details.reason || 'N/A'})`;
  }
  
  if (details.error) {
    return `${base}: ${details.error}`;
  }
  
  return base;
};

// Format zone option for display
export const formatZoneOption = (zone, indentLevel = 0) => {
  const indent = "  ".repeat(indentLevel);
  const prefix = indentLevel > 0 ? "- " : "";
  return `${indent}${prefix}${zone.i_zn} - ${zone.x_nm_zn} (Level ${zone.i_typ_zn})`;
};