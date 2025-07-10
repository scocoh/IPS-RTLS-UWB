/* Name: TriggerDeleteTab.js */
/* Version: 0.1.1 */
/* Created: 250625 */
/* Modified: 250709 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin + Claude */
/* Description: Delete Triggers tab component for NewTriggerDemo - Enhanced with WebSocket refresh after trigger operations */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/NewTriggerDemo/components */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

import React from "react";
import { Table, Button } from "react-bootstrap";
import { triggerApi } from "../services/triggerApi";
import { getFormattedTimestamp } from "../utils/formatters";

const TriggerDeleteTab = ({
  triggers,
  triggerDirections,
  fetchTriggers,
  setEventList,
  // Add WebSocket controls
  connectWebSocket,
  disconnectWebSocket,
  isConnected
}) => {
  // Get direction name by ID
  const getDirectionName = (id) => {
    return triggerDirections.find(d => d.i_dir === id)?.x_dir || `ID ${id}`;
  };

  // WebSocket refresh function
  const refreshWebSocketConnection = async () => {
    try {
      console.log("Refreshing WebSocket connection after trigger operation...");
      setEventList(prev => [...prev, `Refreshing WebSocket connection at ${getFormattedTimestamp()}`]);
      
      if (isConnected) {
        await disconnectWebSocket();
        // Wait a moment for clean disconnection
        await new Promise(resolve => setTimeout(resolve, 1000));
      }
      
      // Reconnect
      connectWebSocket();
      setEventList(prev => [...prev, `WebSocket reconnection initiated at ${getFormattedTimestamp()}`]);
    } catch (e) {
      console.error("Error refreshing WebSocket connection:", e);
      setEventList(prev => [...prev, `WebSocket refresh error: ${e.message} at ${getFormattedTimestamp()}`]);
    }
  };

  // Handle trigger deletion
  const handleDeleteTrigger = async (id) => {
    if (!window.confirm(`Delete trigger ID ${id}?`)) return;
    
    try {
      await triggerApi.deleteTrigger(id);
      alert(`Deleted trigger ${id}`);
      setEventList(prev => [...prev, `Trigger ID ${id} deleted on ${getFormattedTimestamp()}`]);
      
      // Refresh triggers first
      await fetchTriggers();

      // Try to reload triggers on server
      const reloadSuccess = await triggerApi.retryReloadTriggers(3, 1000);
      if (!reloadSuccess) {
        console.log("Server reload failed, refreshing WebSocket connection instead");
        setEventList(prev => [...prev, `Server reload failed, refreshing WebSocket at ${getFormattedTimestamp()}`]);
        await refreshWebSocketConnection();
      } else {
        console.log("Server reload successful, but refreshing WebSocket for good measure");
        setEventList(prev => [...prev, `Server reload successful, refreshing WebSocket at ${getFormattedTimestamp()}`]);
        await refreshWebSocketConnection();
      }
    } catch (e) {
      console.error("Delete error:", e);
      alert("Failed to delete trigger.");
    }
  };

  // Handle move portable trigger
  const handleMoveTrigger = async (triggerId) => {
    const x = prompt("Enter new X coordinate:");
    const y = prompt("Enter new Y coordinate:");
    const z = prompt("Enter new Z coordinate:");
    
    if (x && y && z && !isNaN(x) && !isNaN(y) && !isNaN(z)) {
      try {
        await triggerApi.movePortableTrigger(triggerId, Number(x), Number(y), Number(z));
        setEventList(prev => [...prev, `Moved trigger ${triggerId} to (${x}, ${y}, ${z}) on ${getFormattedTimestamp()}`]);
        console.log(`Moved trigger ${triggerId}`);
        
        // Refresh triggers first
        await fetchTriggers();
        
        // Refresh WebSocket connection after move
        await refreshWebSocketConnection();
      } catch (e) {
        console.error(`Error moving trigger ${triggerId}:`, e);
        alert(`Error moving trigger: ${e.message}`);
      }
    } else {
      alert("Invalid coordinates entered.");
    }
  };

  if (triggers.length === 0) {
    return <p>No triggers found.</p>;
  }

  return (
    <Table striped bordered hover>
      <thead>
        <tr>
          <th>ID</th>
          <th>Name</th>
          <th>Direction</th>
          <th>Zone</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        {triggers.map(t => (
          <tr key={t.i_trg}>
            <td>{t.i_trg}</td>
            <td>{t.x_nm_trg}</td>
            <td>{getDirectionName(t.i_dir)}</td>
            <td>{t.zone_name || "Unknown"}</td>
            <td>
              <Button 
                variant="danger" 
                onClick={() => handleDeleteTrigger(t.i_trg)}
              >
                Delete
              </Button>
              {t.is_portable && (
                <Button
                  variant="primary"
                  onClick={() => handleMoveTrigger(t.i_trg)}
                  style={{ marginLeft: "10px" }}
                >
                  Move
                </Button>
              )}
            </td>
          </tr>
        ))}
      </tbody>
    </Table>
  );
};

export default TriggerDeleteTab;