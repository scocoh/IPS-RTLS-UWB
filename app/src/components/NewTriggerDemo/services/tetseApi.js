/* Name: tetseApi.js */
/* Version: 0.2.0 */
/* Created: 250625 */
/* Modified: 250705 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin + Claude */
/* Description: Enhanced API service for TETSE rule operations with delete functionality */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/NewTriggerDemo/services */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */
/* Changelog: */
/* - 0.2.0 (250705): Added deleteTetseRule and deleteTetseRules methods for rule deletion */
/* - 0.1.1 (250704): Replaced hardcoded IP with dynamic hostname detection */

// Base URL - dynamic hostname detection
const API_BASE_URL = `http://${window.location.hostname || 'localhost'}:8000`;

export const tetseApi = {
  // Fetch TETSE rules from tlk_rules table
  fetchTetseRules: async () => {
    const response = await fetch(`${API_BASE_URL}/api/openai/get_tetse_rules`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return response.json();
  },

  // Delete a single TETSE rule by ID
  deleteTetseRule: async (ruleId) => {
    const response = await fetch(`${API_BASE_URL}/api/openai/delete_tetse_rule/${ruleId}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }
    
    return response.json();
  },

  // Delete multiple TETSE rules by IDs
  deleteTetseRules: async (ruleIds) => {
    const response = await fetch(`${API_BASE_URL}/api/openai/delete_tetse_rules`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ rule_ids: ruleIds })
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }
    
    return response.json();
  }
};