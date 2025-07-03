/* Name: TetseConversionTab.js */
/* Version: 0.1.0 */
/* Created: 250625 */
/* Modified: 250625 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin + Claude */
/* Description: TETSE to Triggers conversion tab component for NewTriggerDemo */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/NewTriggerDemo/components */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

import React, { useState } from "react";
import { Table, Button, FormCheck } from "react-bootstrap";
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

  return (
    <div>
      <h3>Convert TETSE Rules to Portable Triggers</h3>
      <p>Convert proximity and transition rules from TETSE (tlk_rules table) into working portable triggers (triggers table).</p>
      
      <Button 
        variant="primary" 
        onClick={fetchTetseRules}
        disabled={loadingTetseRules}
        className="mb-3"
      >
        {loadingTetseRules ? 'Loading TETSE Rules...' : 'Load TETSE Rules'}
      </Button>

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
              <th>Select</th>
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
                    id={`rule-${rule.id}`}
                    defaultChecked={false}
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
                  {conversionStatus[rule.id] ? (
                    <span className={`badge bg-${
                      conversionStatus[rule.id].status === 'success' ? 'success' : 
                      conversionStatus[rule.id].status === 'error' ? 'danger' : 'warning'
                    }`}>
                      {conversionStatus[rule.id].message}
                    </span>
                  ) : (
                    <span className="badge bg-secondary">Ready</span>
                  )}
                </td>
                <td>
                  <Button
                    variant="success"
                    size="sm"
                    onClick={() => handleConvertRule(rule.id)}
                    disabled={conversionStatus[rule.id]?.status === 'converting'}
                  >
                    {conversionStatus[rule.id]?.status === 'converting' ? 'Converting...' : 'Convert to Trigger'}
                  </Button>
                </td>
              </tr>
            ))}
          </tbody>
        </Table>
      )}
    </div>
  );
};

export default TetseConversionTab;