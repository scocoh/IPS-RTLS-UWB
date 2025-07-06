/* Name: TriggerDataTab.js */
/* Version: 0.1.0 */
/* Created: 250705 */
/* Modified: 250705 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin + Claude */
/* Description: Data subscription tab for NewTriggerDemo - handles WebSocket connections and tag data */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/NewTriggerDemo/components */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

import React from "react";
import { Form, Button, InputGroup, FormControl } from "react-bootstrap";
import { formatTagInfo } from "../utils/formatters";

const TriggerDataTab = ({
  zones,
  zoneHierarchy,
  selectedZone,
  tagIdsInput,
  setTagIdsInput,
  isConnected,
  tagsData,
  sequenceNumbers,
  tagCount,
  tagRate,
  connectWebSocket,
  disconnectWebSocket,
  handleZoneChange
}) => {
  // Render zone options
  const renderZoneOptions = (zoneList, indentLevel = 0) => {
    return zoneList.map(zone => (
      <React.Fragment key={zone.i_zn}>
        <option value={zone.i_zn}>
          {`${"  ".repeat(indentLevel)}${indentLevel > 0 ? "- " : ""}${zone.i_zn} - ${zone.x_nm_zn} (Level ${zone.i_typ_zn})`}
        </option>
        {zone.children && zone.children.length > 0 && renderZoneOptions(zone.children, indentLevel + 1)}
      </React.Fragment>
    ));
  };

  const infoLines = formatTagInfo(tagsData, selectedZone, zones, tagCount, tagRate);

  return (
    <div>
      <h3>Tag Data Subscription</h3>
      <p>Connect to WebSocket to receive live tag position data and trigger events.</p>

      {/* Connection Status */}
      <div style={{ 
        marginBottom: "15px", 
        padding: "10px", 
        backgroundColor: "#f8f9fa", 
        borderRadius: "5px",
        border: "1px solid #dee2e6"
      }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <h6 style={{ margin: 0 }}>🔗 Connection Status</h6>
          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <span style={{ 
              fontSize: "12px", 
              color: isConnected ? "#28a745" : "#dc3545",
              fontWeight: "500"
            }}>
              <span style={{ 
                display: "inline-block", 
                width: "8px", 
                height: "8px", 
                borderRadius: "50%", 
                backgroundColor: isConnected ? "#28a745" : "#dc3545",
                marginRight: "5px"
              }}></span>
              {isConnected ? "Connected" : "Disconnected"}
            </span>
            <span style={{ fontSize: "12px", color: "#6c757d" }}>
              Rate: {tagRate.toFixed(2)} tags/sec
            </span>
          </div>
        </div>
      </div>

      {/* Tag Subscription */}
      <Form.Group style={{ marginBottom: "15px" }}>
        <Form.Label>Tag IDs to Subscribe (comma-separated, e.g., SIM1,SIM2)</Form.Label>
        <InputGroup>
          <FormControl
            type="text"
            value={tagIdsInput}
            onChange={(e) => setTagIdsInput(e.target.value)}
            placeholder="Enter Tag IDs (e.g., SIM1,SIM2)"
            disabled={isConnected}
          />
          <Button
            variant={isConnected ? "danger" : "primary"}
            onClick={() => {
              if (isConnected) {
                disconnectWebSocket();
              } else {
                connectWebSocket();
              }
            }}
            disabled={!tagIdsInput}
          >
            {isConnected ? "Disconnect" : "Connect"}
          </Button>
        </InputGroup>
      </Form.Group>

      {/* Zone Selection */}
      <Form.Group style={{ marginBottom: "15px" }}>
        <Form.Label>Select Zone</Form.Label>
        <Form.Control 
          as="select" 
          value={selectedZone?.i_zn || ""} 
          onChange={e => handleZoneChange(e.target.value)}
        >
          <option value="">-- Choose Zone --</option>
          {renderZoneOptions(zoneHierarchy)}
        </Form.Control>
      </Form.Group>

      {/* Live Tag Data Display */}
      {Object.values(tagsData).length > 0 && (
        <div style={{ 
          marginTop: "15px", 
          padding: "10px", 
          backgroundColor: "#ffffff", 
          borderRadius: "5px",
          border: "1px solid #dee2e6"
        }}>
          <h6>📍 Live Tag Data</h6>
          <div style={{ 
            fontFamily: "monospace", 
            fontSize: "12px", 
            whiteSpace: "pre-wrap",
            backgroundColor: "#f8f9fa",
            padding: "8px",
            borderRadius: "3px"
          }}>
            {infoLines}
          </div>
        </div>
      )}

      {/* Connection Help */}
      <div style={{ 
        marginTop: "15px", 
        padding: "10px", 
        backgroundColor: "#e7f3ff", 
        borderRadius: "5px",
        border: "1px solid #b3d9ff"
      }}>
        <h6 style={{ color: "#0066cc" }}>💡 Connection Help</h6>
        <ul style={{ fontSize: "13px", color: "#333", marginBottom: 0 }}>
          <li>Enter tag IDs (e.g., SIM1,SIM2) and click Connect</li>
          <li>Select a zone to filter data for that zone</li>
          <li>Live position data will appear once connected</li>
          <li>Connection status shows real-time data rate</li>
        </ul>
      </div>
    </div>
  );
};

export default TriggerDataTab;