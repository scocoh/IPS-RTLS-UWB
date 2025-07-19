/* Name: triggerApi.js */
/* Version: 0.1.2 */
/* Created: 250625 */
/* Modified: 250718 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin + Claude */
/* Description: API service for trigger operations with enhanced error handling */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/NewTriggerDemo/services */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */
/* Changelog: */
/* - 0.1.2 (250718): Enhanced error handling for boundary violations with detailed user messages */
/* - 0.1.1 (250704): Replaced hardcoded IP with dynamic hostname detection */

// Base URL - dynamic hostname detection
const API_BASE_URL = `http://${window.location.hostname || 'localhost'}:8000`;

/**
 * Helper function to extract detailed error information from API responses
 * @param {Response} response - The fetch response object
 * @returns {Promise<Error>} - Formatted error with detailed message
 */
const createDetailedError = async (response) => {
  try {
    const errorData = await response.json();
    
    // Check if this is a boundary violation error
    if (response.status === 400 && errorData.detail) {
      const detail = errorData.detail;
      
      // If the error mentions coordinates exceeding boundaries
      if (detail.includes("coordinates") && detail.includes("boundaries")) {
        return new Error(`⚠️ Trigger Placement Error\n\n${detail}\n\nℹ️ Please redraw your trigger within the highlighted zone area.`);
      }
      
      // If the error mentions trigger name already exists
      if (detail.includes("already exists")) {
        return new Error(`⚠️ Duplicate Name Error\n\n${detail}\n\nℹ️ Please choose a different trigger name.`);
      }
      
      // Other 400 errors with detail
      return new Error(`⚠️ Request Error\n\n${detail}`);
    }
    
    // Server errors (500)
    if (response.status >= 500) {
      const serverDetail = errorData.detail || "Internal server error occurred";
      return new Error(`🔧 Server Error\n\n${serverDetail}\n\nℹ️ Please try again or contact support if the problem persists.`);
    }
    
    // Generic error with detail
    if (errorData.detail) {
      return new Error(errorData.detail);
    }
    
    // Fallback to status-based error
    return new Error(`Request failed with status ${response.status}`);
    
  } catch (parseError) {
    // If we can't parse the response, use the status code
    console.warn("Could not parse error response:", parseError);
    
    switch (response.status) {
      case 400:
        return new Error(`⚠️ Invalid Request\n\nThe request contains invalid data. Please check your input and try again.`);
      case 404:
        return new Error(`❌ Not Found\n\nThe requested resource could not be found.`);
      case 500:
        return new Error(`🔧 Server Error\n\nAn internal server error occurred. Please try again later.`);
      default:
        return new Error(`❌ Request Failed\n\nRequest failed with status ${response.status}. Please try again.`);
    }
  }
};

export const triggerApi = {
  // Fetch all triggers
  fetchTriggers: async () => {
    const res = await fetch(`${API_BASE_URL}/api/list_newtriggers`);
    console.log("Fetch triggers response status:", res.status);
    if (!res.ok) {
      const error = await createDetailedError(res);
      throw error;
    }
    return res.json();
  },

  // Fetch trigger directions
  fetchTriggerDirections: async () => {
    const res = await fetch(`${API_BASE_URL}/api/list_trigger_directions`);
    if (!res.ok) {
      const error = await createDetailedError(res);
      throw error;
    }
    return res.json();
  },

  // Get trigger details
  getTriggerDetails: async (triggerId) => {
    const res = await fetch(`${API_BASE_URL}/api/get_trigger_details/${triggerId}`);
    if (!res.ok) {
      const error = await createDetailedError(res);
      throw error;
    }
    return res.json();
  },

  // Create new trigger with enhanced error handling
  createTrigger: async (payload) => {
    const res = await fetch(`${API_BASE_URL}/api/add_trigger`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    
    if (!res.ok) {
      const error = await createDetailedError(res);
      throw error;
    }
    
    const result = await res.json();
    
    // Log successful creation with any corrections applied
    if (result.corrections_applied && result.corrections_applied.length > 0) {
      console.log("Trigger created with auto-corrections:", result.corrections_applied);
    }
    
    return result;
  },

  // Create trigger from zone with enhanced error handling
  createTriggerFromZone: async (formData) => {
    const res = await fetch(`${API_BASE_URL}/api/add_trigger_from_zone`, {
      method: "POST",
      body: formData
    });
    
    if (!res.ok) {
      const error = await createDetailedError(res);
      throw error;
    }
    
    return res.json();
  },

  // Create portable trigger with enhanced error handling
  createPortableTrigger: async (payload) => {
    const res = await fetch(`${API_BASE_URL}/api/add_portable_trigger`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    
    if (!res.ok) {
      const error = await createDetailedError(res);
      throw error;
    }
    
    return res.json();
  },

  // Delete trigger with enhanced error handling
  deleteTrigger: async (triggerId) => {
    const res = await fetch(`${API_BASE_URL}/api/delete_trigger/${triggerId}`, {
      method: "DELETE"
    });
    
    if (!res.ok) {
      const error = await createDetailedError(res);
      throw error;
    }
    
    return res.json();
  },

  // Move portable trigger with enhanced error handling
  movePortableTrigger: async (triggerId, x, y, z) => {
    const res = await fetch(
      `${API_BASE_URL}/api/move_trigger/${triggerId}?new_x=${x}&new_y=${y}&new_z=${z}`,
      { method: "PUT" }
    );
    
    if (!res.ok) {
      const error = await createDetailedError(res);
      throw error;
    }
    
    return res.json();
  },

  // Reload triggers (notify server) with enhanced error handling
  reloadTriggers: async () => {
    const res = await fetch(`${API_BASE_URL}/api/reload_triggers`, {
      method: "POST",
      headers: { "Content-Type": "application/json" }
    });
    
    if (!res.ok) {
      const error = await createDetailedError(res);
      throw error;
    }
    
    return res.json();
  },

  // Retry reload triggers with exponential backoff
  retryReloadTriggers: async (retries = 3, delay = 1000) => {
    for (let attempt = 1; attempt <= retries; attempt++) {
      try {
        await triggerApi.reloadTriggers();
        console.log("Successfully sent reload triggers request");
        return true;
      } catch (e) {
        console.error(`Attempt ${attempt} failed: ${e.message}`);
        if (attempt === retries) {
          console.error("All retry attempts failed.");
          return false;
        }
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }
    return false;
  },

  // Check if point is contained in trigger with enhanced error handling
  checkTriggerContainment: async (triggerId, x, y, z) => {
    const res = await fetch(
      `${API_BASE_URL}/api/trigger_contains_point/${triggerId}?x=${x}&y=${y}&z=${z}`
    );
    
    if (!res.ok) {
      const error = await createDetailedError(res);
      throw error;
    }
    
    return res.json();
  },

  // Get zone boundaries for validation (new helper method)
  getZoneBoundaries: async (zoneId) => {
    const res = await fetch(`${API_BASE_URL}/api/get_zone_boundaries/${zoneId}`);
    
    if (!res.ok) {
      const error = await createDetailedError(res);
      throw error;
    }
    
    return res.json();
  }
};