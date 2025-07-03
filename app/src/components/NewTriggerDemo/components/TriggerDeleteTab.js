/* Name: TriggerDeleteTab.js */
/* Version: 0.1.0 */
/* Created: 250625 */
/* Modified: 250625 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin + Claude */
/* Description: Delete Triggers tab component for NewTriggerDemo */
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
  setEventList
}) => {
  // Get direction name by ID
  const getDirectionName = (id) => {
    return triggerDirections.find(d => d.i_dir === id)?.x_dir || `ID ${id}`;
  };

  // Handle trigger deletion
  const handleDeleteTrigger = async (id) => {
    if (!window.confirm(`Delete trigger ID ${id}?`)) return;
    
    try {
      await triggerApi.deleteTrigger(id);
      alert(`Deleted trigger ${id}`);
      setEventList(prev => [...prev, `Trigger ID ${id} deleted on ${getFormattedTimestamp()}`]);
      await fetchTriggers();

      const reloadSuccess = await triggerApi.retryReloadTriggers(3, 1000);
      if (!reloadSuccess) {
        alert("Trigger deleted, but failed to reload triggers on the server. Please restart the WebSocket server or try again.");
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
        await fetchTriggers();
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