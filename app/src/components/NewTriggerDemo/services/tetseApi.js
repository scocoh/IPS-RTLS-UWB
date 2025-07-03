/* Name: tetseApi.js */
/* Version: 0.1.0 */
/* Created: 250625 */
/* Modified: 250625 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin + Claude */
/* Description: API service for TETSE rule operations */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/NewTriggerDemo/services */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

// Base URL - will be replaced with config later
const API_BASE_URL = "http://192.168.210.226:8000";

export const tetseApi = {
  // Fetch TETSE rules from tlk_rules table
  fetchTetseRules: async () => {
    const response = await fetch(`${API_BASE_URL}/api/openai/get_tetse_rules`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return response.json();
  }
};