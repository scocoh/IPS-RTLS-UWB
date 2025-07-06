/* Name: TetseConversionTab.js */
/* Version: 0.2.0 */
/* Created: 250625 */
/* Modified: 250705 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin + Claude */
/* Description: Enhanced TETSE to Triggers conversion tab with delete functionality */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/NewTriggerDemo/components */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

import React, { useState } from "react";
import { Table, Button, FormCheck, ButtonGroup } from "react-bootstrap";
import { tetseApi } from "../services/tetseApi";
import { triggerApi } from "../services/triggerApi";

const TetseConversionTab = ({
  eventList,
  setEventList,
  fetchTriggers
}) => {
  const [tetseRules, setTetseRules] = useState([]);
  const [loadingTetseRules, setLoadingTetseRules] = useState(false);
  const [tetseRulesError, setTetseRulesError] = useState(null);
  const [conversionStatus, setConversionStatus] = useState({});
  const [deleteStatus, setDeleteStatus] = useState({});
  const [selectedRules, setSelectedRules] = useState(new Set());
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  // Fetch TETSE rules
  const fetchTetseRules = async () => {
    setLoadingTetseRules(true);
    setTetseRulesError(null);
    
    try {
      console.log("Fetching TETSE rules from tlk_rules table via API...");
      const tetseRulesData = await tetseApi.fetchTetseRules();
      console.log(`Fetched ${tetseRulesData.length} TETSE rules:`, tetseRulesData);
      
      setTetseRules(tetseRulesData);
      setEventList([...eventList, `Loaded ${tetseRulesData.length} TETSE rules from database`]);
    } catch (error) {
      console.error("Error fetching TETSE rules:", error);
      setTetseRulesError(`Failed to load TETSE rules: ${error.message}`);
    } finally {
      setLoadingTetseRules(false);
    }
  };

  // Handle rule conversion
  const handleConvertRule = async (ruleId) => {
    setConversionStatus({
      ...conversionStatus,
      [ruleId]: { status: 'converting', message: 'Converting rule to portable trigger...' }
    });
    
    try {
      console.log(`Converting TETSE rule ${ruleId} to portable trigger...`);
      
      // Find the rule data
      const rule = tetseRules.find(r => r.id === ruleId);
      if (!rule) {
        throw new Error('Rule not found');
      }
      
      // Extract parameters based on rule type
      let triggerParams;
      let apiCall;

      if (rule.rule_type === 'proximity_condition') {
        triggerParams = {
          name: `converted_proximity_${rule.subject_id}_${Date.now()}`,
          direction: 1, // WhileIn
          ignore: false,
          zone_id: rule.conditions.zone_transition?.from === 'inside' ? null : parseInt(rule.conditions.zone || 425),
          is_portable: true,
          assigned_tag_id: rule.subject_id,
          radius_ft: rule.conditions.proximity_distance || 6.0,
          z_min: 0,
          z_max: 10,
          vertices: []
        };
        apiCall = triggerApi.createPortableTrigger(triggerParams);
        
      } else if (rule.rule_type === 'zone_transition') {
        triggerParams = {
          name: `converted_transition_${rule.subject_id}_${Date.now()}`,
          direction: 4, // OnEnter 
          ignore: false,
          zone_id: parseInt(rule.conditions.to_zone || rule.conditions.zone || 425),
          is_portable: null,
          assigned_tag_id: null,
          radius_ft: null,
          z_min: 0,
          z_max: 10,
          vertices: []
        };
        apiCall = triggerApi.createTrigger(triggerParams);
        
      } else if (rule.rule_type === 'zone_entry_monitoring') {
        const zoneId = parseInt(rule.zone_id || rule.zone || 425);
        
        // Use FormData for zone-based endpoint
        const formData = new FormData();
        formData.append('name', `converted_zone_entry_${rule.subject_id}_${Date.now()}`);
        formData.append('direction', 4); // OnEnter
        formData.append('zone_id', zoneId);
        formData.append('ignore', false);
        
        apiCall = triggerApi.createTriggerFromZone(formData);
        
      } else {
        throw new Error(`Rule type '${rule.rule_type}' not supported for conversion`);
      }

      console.log('Converting with params:', triggerParams || 'FormData');
      const result = await apiCall;
      console.log('Trigger created:', result);

      // Update status with success
      setConversionStatus({
        ...conversionStatus,
        [ruleId]: { 
          status: 'success', 
          message: `Converted to trigger ID ${result.trigger_id}` 
        }
      });
      
      // Add to event list
      setEventList([...eventList, `TETSE rule ${ruleId} converted to portable trigger ID ${result.trigger_id}`]);
      
      // Refresh triggers list to show the new trigger
      await fetchTriggers();

    } catch (error) {
      console.error(`Error converting rule ${ruleId}:`, error);
      
      setConversionStatus({
        ...conversionStatus,
        [ruleId]: { 
          status: 'error', 
          message: `Failed to convert: ${error.message}` 
        }
      });
    }
  };

  // Handle single rule deletion
  const handleDeleteRule = async (ruleId) => {
    if (!window.confirm(`Are you sure you want to delete TETSE rule ${ruleId}? This cannot be undone.`)) {
      return;
    }

    setDeleteStatus({
      ...deleteStatus,
      [ruleId]: { status: 'deleting', message: 'Deleting rule...' }
    });

    try {
      console.log(`Deleting TETSE rule ${ruleId}...`);
      await tetseApi.deleteTetseRule(ruleId);
      
      // Remove from local state
      setTetseRules(prev => prev.filter(rule => rule.id !== ruleId));
      
      // Update status
      setDeleteStatus({
        ...deleteStatus,
        [ruleId]: { status: 'success', message: 'Deleted successfully' }
      });
      
      // Add to event list
      setEventList([...eventList, `TETSE rule ${ruleId} deleted from database`]);
      
      // Clean up status after a delay
      setTimeout(() => {
        setDeleteStatus(prev => {
          const updated = { ...prev };
          delete updated[ruleId];
          return updated;
        });
      }, 3000);

    } catch (error) {
      console.error(`Error deleting rule ${ruleId}:`, error);
      
      setDeleteStatus({
        ...deleteStatus,
        [ruleId]: { 
          status: 'error', 
          message: `Failed to delete: ${error.message}` 
        }
      });
    }
  };

  // Handle bulk rule deletion
  const handleDeleteSelectedRules = async () => {
    if (selectedRules.size === 0) {
      alert("Please select rules to delete.");
      return;
    }

    if (!window.confirm(`Are you sure you want to delete ${selectedRules.size} selected TETSE rules? This cannot be undone.`)) {
      return;
    }

    const ruleIds = Array.from(selectedRules);
    console.log(`Deleting ${ruleIds.length} TETSE rules:`, ruleIds);

    try {
      // Delete all selected rules
      const deletePromises = ruleIds.map(async (ruleId) => {
        setDeleteStatus(prev => ({
          ...prev,
          [ruleId]: { status: 'deleting', message: 'Deleting...' }
        }));
        
        try {
          await tetseApi.deleteTetseRule(ruleId);
          return { ruleId, success: true };
        } catch (error) {
          console.error(`Failed to delete rule ${ruleId}:`, error);
          return { ruleId, success: false, error: error.message };
        }
      });

      const results = await Promise.all(deletePromises);
      
      // Process results
      const successful = results.filter(r => r.success);
      const failed = results.filter(r => !r.success);
      
      // Update local state - remove successful deletions
      if (successful.length > 0) {
        const successfulIds = successful.map(r => r.ruleId);
        setTetseRules(prev => prev.filter(rule => !successfulIds.includes(rule.id)));
        setSelectedRules(new Set());
      }
      
      // Update status
      results.forEach(({ ruleId, success, error }) => {
        setDeleteStatus(prev => ({
          ...prev,
          [ruleId]: {
            status: success ? 'success' : 'error',
            message: success ? 'Deleted' : `Failed: ${error}`
          }
        }));
      });
      
      // Add to event list
      if (successful.length > 0) {
        setEventList(prev => [...prev, `Bulk deleted ${successful.length} TETSE rules from database`]);
      }
      if (failed.length > 0) {
        setEventList(prev => [...prev, `Failed to delete ${failed.length} TETSE rules`]);
      }
      
      // Clean up status after delay
      setTimeout(() => {
        setDeleteStatus({});
      }, 5000);

    } catch (error) {
      console.error("Error in bulk delete:", error);
      alert(`Bulk delete failed: ${error.message}`);
    }
  };

  // Handle select all / deselect all
  const handleSelectAll = () => {
    if (selectedRules.size === tetseRules.length) {
      setSelectedRules(new Set());
    } else {
      setSelectedRules(new Set(tetseRules.map(rule => rule.id)));
    }
  };

  // Handle individual rule selection
  const handleRuleSelection = (ruleId, checked) => {
    const newSelected = new Set(selectedRules);
    if (checked) {
      newSelected.add(ruleId);
    } else {
      newSelected.delete(ruleId);
    }
    setSelectedRules(newSelected);
  };

  return (
    <div>
      <h3>Convert TETSE Rules to Portable Triggers</h3>
      <p>Convert proximity and transition rules from TETSE (tlk_rules table) into working portable triggers (triggers table).</p>
      
      {/* Control Buttons */}
      <div style={{ marginBottom: "15px", display: "flex", gap: "10px", alignItems: "center" }}>
        <Button 
          variant="primary" 
          onClick={fetchTetseRules}
          disabled={loadingTetseRules}
        >
          {loadingTetseRules ? 'Loading TETSE Rules...' : 'Load TETSE Rules'}
        </Button>

        {tetseRules.length > 0 && (
          <>
            <Button
              variant="secondary"
              onClick={handleSelectAll}
              size="sm"
            >
              {selectedRules.size === tetseRules.length ? 'Deselect All' : 'Select All'}
            </Button>

            <Button
              variant="danger"
              onClick={handleDeleteSelectedRules}
              disabled={selectedRules.size === 0}
              size="sm"
            >
              Delete Selected ({selectedRules.size})
            </Button>
          </>
        )}
      </div>

      {tetseRulesError && (
        <div className="alert alert-danger" role="alert">
          {tetseRulesError}
        </div>
      )}

      {tetseRules.length === 0 && !loadingTetseRules ? (
        <p>No TETSE rules loaded. Click "Load TETSE Rules" to fetch available rules from the tlk_rules table.</p>
      ) : (
        <Table striped bordered hover>
          <thead>
            <tr>
              <th style={{ width: "50px" }}>
                <FormCheck 
                  type="checkbox"
                  checked={selectedRules.size === tetseRules.length && tetseRules.length > 0}
                  onChange={handleSelectAll}
                  title="Select/Deselect All"
                />
              </th>
              <th>Rule ID</th>
              <th>Name</th>
              <th>Type</th>
              <th>Subject ID</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {tetseRules.map(rule => (
              <tr key={rule.id}>
                <td>
                  <FormCheck 
                    type="checkbox"
                    checked={selectedRules.has(rule.id)}
                    onChange={(e) => handleRuleSelection(rule.id, e.target.checked)}
                  />
                </td>
                <td>{rule.id}</td>
                <td>{rule.name}</td>
                <td>
                  <span className={`badge bg-${
                    rule.rule_type === 'proximity_condition' ? 'info' :
                    rule.rule_type === 'zone_transition' ? 'warning' :
                    rule.rule_type === 'layered_trigger' ? 'primary' : 'secondary'
                  }`}>
                    {rule.rule_type || 'zone_stay'}
                  </span>
                </td>
                <td>{rule.subject_id || 'N/A'}</td>
                <td>
                  {/* Conversion Status */}
                  {conversionStatus[rule.id] && (
                    <span className={`badge bg-${
                      conversionStatus[rule.id].status === 'success' ? 'success' : 
                      conversionStatus[rule.id].status === 'error' ? 'danger' : 'warning'
                    }`} style={{ marginRight: "5px" }}>
                      Convert: {conversionStatus[rule.id].message}
                    </span>
                  )}
                  
                  {/* Delete Status */}
                  {deleteStatus[rule.id] ? (
                    <span className={`badge bg-${
                      deleteStatus[rule.id].status === 'success' ? 'success' : 
                      deleteStatus[rule.id].status === 'error' ? 'danger' : 'warning'
                    }`}>
                      Delete: {deleteStatus[rule.id].message}
                    </span>
                  ) : (
                    !conversionStatus[rule.id] && (
                      <span className="badge bg-secondary">Ready</span>
                    )
                  )}
                </td>
                <td>
                  <ButtonGroup size="sm">
                    <Button
                      variant="success"
                      onClick={() => handleConvertRule(rule.id)}
                      disabled={conversionStatus[rule.id]?.status === 'converting' || deleteStatus[rule.id]?.status === 'deleting'}
                      title="Convert to Trigger"
                    >
                      {conversionStatus[rule.id]?.status === 'converting' ? 'Converting...' : '🔄 Convert'}
                    </Button>
                    
                    <Button
                      variant="danger"
                      onClick={() => handleDeleteRule(rule.id)}
                      disabled={deleteStatus[rule.id]?.status === 'deleting' || conversionStatus[rule.id]?.status === 'converting'}
                      title="Delete Rule"
                    >
                      {deleteStatus[rule.id]?.status === 'deleting' ? 'Deleting...' : '🗑️ Delete'}
                    </Button>
                  </ButtonGroup>
                </td>
              </tr>
            ))}
          </tbody>
        </Table>
      )}

      {/* Help Section */}
      <div style={{ 
        marginTop: "20px", 
        padding: "15px", 
        backgroundColor: "#e7f3ff", 
        borderRadius: "5px",
        border: "1px solid #b3d9ff"
      }}>
        <h6 style={{ color: "#0066cc" }}>💡 TETSE Rule Management</h6>
        <ul style={{ fontSize: "13px", color: "#333", marginBottom: 0 }}>
          <li><strong>Load TETSE Rules:</strong> Fetch all rules from the tlk_rules database table</li>
          <li><strong>Convert:</strong> Transform TETSE rules into working triggers in the triggers table</li>
          <li><strong>Delete:</strong> Permanently remove TETSE rules from the database (cannot be undone)</li>
          <li><strong>Bulk Operations:</strong> Select multiple rules for bulk deletion</li>
          <li><strong>Status Tracking:</strong> Monitor conversion and deletion progress in real-time</li>
        </ul>
      </div>
    </div>
  );
};

export default TetseConversionTab;