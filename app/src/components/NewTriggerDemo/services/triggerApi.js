/* Name: triggerApi.js */
/* Version: 0.1.1 */
/* Created: 250625 */
/* Modified: 250704 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin + Claude */
/* Description: API service for trigger operations */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/NewTriggerDemo/services */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */
/* Changelog: */
/* - 0.1.1 (250704): Replaced hardcoded IP with dynamic hostname detection */

// Base URL - dynamic hostname detection
const API_BASE_URL = `http://${window.location.hostname || 'localhost'}:8000`;

export const triggerApi = {
  // Fetch all triggers
  fetchTriggers: async () => {
    const res = await fetch(`${API_BASE_URL}/api/list_newtriggers`);
    console.log("Fetch triggers response status:", res.status);
    if (!res.ok) throw new Error(`Failed to fetch triggers: ${res.status}`);
    return res.json();
  },

  // Fetch trigger directions
  fetchTriggerDirections: async () => {
    const res = await fetch(`${API_BASE_URL}/api/list_trigger_directions`);
    if (!res.ok) throw new Error(`Failed to fetch trigger directions: ${res.status}`);
    return res.json();
  },

  // Get trigger details
  getTriggerDetails: async (triggerId) => {
    const res = await fetch(`${API_BASE_URL}/api/get_trigger_details/${triggerId}`);
    if (!res.ok) throw new Error(`Failed to fetch trigger details: ${res.status}`);
    return res.json();
  },

  // Create new trigger
  createTrigger: async (payload) => {
    const res = await fetch(`${API_BASE_URL}/api/add_trigger`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error(`Failed to create trigger: ${res.status}`);
    return res.json();
  },

  // Create trigger from zone
  createTriggerFromZone: async (formData) => {
    const res = await fetch(`${API_BASE_URL}/api/add_trigger_from_zone`, {
      method: "POST",
      body: formData
    });
    if (!res.ok) {
      const errorData = await res.json().catch(() => ({}));
      throw new Error(errorData.detail || `Failed to create trigger from zone: ${res.status}`);
    }
    return res.json();
  },

  // Create portable trigger
  createPortableTrigger: async (payload) => {
    const res = await fetch(`${API_BASE_URL}/api/add_portable_trigger`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    if (!res.ok) {
      const errorData = await res.json().catch(() => ({}));
      throw new Error(errorData.detail || `Failed to create portable trigger: ${res.status}`);
    }
    return res.json();
  },

  // Delete trigger
  deleteTrigger: async (triggerId) => {
    const res = await fetch(`${API_BASE_URL}/api/delete_trigger/${triggerId}`, {
      method: "DELETE"
    });
    if (!res.ok) throw new Error(`Failed to delete trigger: ${res.status}`);
    return res.json();
  },

  // Move portable trigger
  movePortableTrigger: async (triggerId, x, y, z) => {
    const res = await fetch(
      `${API_BASE_URL}/api/move_trigger/${triggerId}?new_x=${x}&new_y=${y}&new_z=${z}`,
      { method: "PUT" }
    );
    if (!res.ok) throw new Error(`Failed to move trigger: ${res.status}`);
    return res.json();
  },

  // Reload triggers (notify server)
  reloadTriggers: async () => {
    const res = await fetch(`${API_BASE_URL}/api/reload_triggers`, {
      method: "POST",
      headers: { "Content-Type": "application/json" }
    });
    if (!res.ok) throw new Error(`Failed to reload triggers: ${res.status}`);
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

  // Check if point is contained in trigger
  checkTriggerContainment: async (triggerId, x, y, z) => {
    const res = await fetch(
      `${API_BASE_URL}/api/trigger_contains_point/${triggerId}?x=${x}&y=${y}&z=${z}`
    );
    if (!res.ok) throw new Error(`Failed to check containment: ${res.status}`);
    return res.json();
  }
};