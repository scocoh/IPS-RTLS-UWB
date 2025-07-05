/* Name: EntityTypes.js */
/* Version: 0.2.1 */
/* Created: 250704 */
/* Modified: 250704 */
/* Creator: ParcoAdmin */
/* Modified By: AI Assistant */
/* Description: Shared constants and types for Entity management components */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/Entities */
/* Role: Frontend Constants */
/* Status: Active */
/* Dependent: TRUE */

// /home/parcoadmin/parco_fastapi/app/src/components/Entities/EntityTypes.js
// Version: v0.2.1 - Initial creation with shared constants for Entity grid interface
// ParcoRTLS © 2025 — Scott Cohen, Jesse Chunn, etc.

/**
 * Shared constants and types for Entity management
 * Used by EntityGridDemo, EntityGridView, and other entity components
 */

// Grid Layout Constants
export const GRID_LAYOUT = {
  TAG_SIZE: 40,           // Size of round tag checkers in pixels
  TAG_MARGIN: 8,          // Margin between tags
  CART_WIDTH: 120,        // Width of entity cart/bucket
  CART_HEIGHT: 80,        // Height of entity cart/bucket
  CART_MARGIN: 16,        // Margin between carts
  GRID_PADDING: 20,       // Padding around grid container
  TAGS_PER_ROW: 8,        // Number of unassigned tags per row
  MIN_GRID_WIDTH: 800,    // Minimum width for grid container
  MIN_GRID_HEIGHT: 600,   // Minimum height for grid container
};

// Visual Design Constants
export const COLORS = {
  // Tag Colors
  TAG_UNASSIGNED: '#e3f2fd',      // Light blue for unassigned tags
  TAG_ASSIGNED: '#c8e6c9',        // Light green for assigned tags
  TAG_PARENT: '#ffecb3',          // Light yellow for parent tags
  TAG_BORDER: '#1976d2',          // Blue border for tags
  TAG_TEXT: '#1565c0',            // Blue text for tag numbers
  
  // Cart Colors
  CART_BACKGROUND: '#f5f5f5',     // Light gray cart background
  CART_BORDER: '#424242',         // Dark gray cart border
  CART_HOVER: '#e0e0e0',          // Hover state for carts
  CART_ACTIVE: '#c5e1a5',         // Active drop target color
  
  // Grid Colors
  GRID_BACKGROUND: '#fafafa',     // Light background for grid
  GRID_BORDER: '#e0e0e0',         // Grid border color
  
  // Text Colors
  TEXT_PRIMARY: '#212121',        // Primary text color
  TEXT_SECONDARY: '#757575',      // Secondary text color
  TEXT_DISABLED: '#bdbdbd',       // Disabled text color
};

// Entity Status Constants
export const ENTITY_STATUS = {
  ACTIVE: 'active',
  INACTIVE: 'inactive',
  PENDING: 'pending',
  ERROR: 'error',
};

// Assignment Status Constants
export const ASSIGNMENT_STATUS = {
  ASSIGNED: 'assigned',
  UNASSIGNED: 'unassigned',
  PENDING: 'pending',
  FAILED: 'failed',
};

// Drag and Drop Constants
export const DRAG_TYPES = {
  TAG: 'tag',
  ENTITY: 'entity',
  CART: 'cart',
};

// Default Entity Types (fallback if API fails)
export const DEFAULT_ENTITY_TYPES = [
  { i_typ_ent: 1, x_dsc_ent: 'Person', x_nm_ent: 'Person' },
  { i_typ_ent: 2, x_dsc_ent: 'Vehicle', x_nm_ent: 'Vehicle' },
  { i_typ_ent: 3, x_dsc_ent: 'Asset', x_nm_ent: 'Asset' },
  { i_typ_ent: 4, x_dsc_ent: 'Zone', x_nm_ent: 'Zone' },
];

// Default Assignment Reasons (fallback if API fails)
export const DEFAULT_ASSIGNMENT_REASONS = [
  { i_rsn: 1, x_rsn: 'Manual Assignment' },
  { i_rsn: 2, x_rsn: 'Automatic Merge' },
  { i_rsn: 3, x_rsn: 'Proximity Based' },
];

// Default Device Types (fallback if API fails)
export const DEFAULT_DEVICE_TYPES = [
  { i_typ_dev: 1, x_dsc_dev: 'Tag Type 1' },
  { i_typ_dev: 2, x_dsc_dev: 'Tag Type 2' },
  { i_typ_dev: 3, x_dsc_dev: 'Tag Type 3' },
];

// Grid Animation Constants
export const ANIMATIONS = {
  DRAG_DURATION: 200,     // Duration for drag animations in ms
  DROP_DURATION: 300,     // Duration for drop animations in ms
  HOVER_DURATION: 150,    // Duration for hover effects in ms
  FADE_DURATION: 250,     // Duration for fade transitions in ms
};

// Entity Hierarchy Constants
export const HIERARCHY = {
  MAX_DEPTH: 3,           // Maximum nesting depth for entities
  MAX_CHILDREN: 20,       // Maximum children per entity
  INDENT_SIZE: 20,        // Indentation size for hierarchy display
};

// Validation Constants
export const VALIDATION = {
  MIN_ENTITY_NAME: 3,     // Minimum entity name length
  MAX_ENTITY_NAME: 50,    // Maximum entity name length
  MIN_TAG_ID: 1,          // Minimum tag ID length
  MAX_TAG_ID: 20,         // Maximum tag ID length
};

// Component States
export const COMPONENT_STATES = {
  LOADING: 'loading',
  READY: 'ready',
  ERROR: 'error',
  EMPTY: 'empty',
};

// Grid View Modes
export const VIEW_MODES = {
  GRID: 'grid',           // Grid layout view
  LIST: 'list',           // List layout view
  HIERARCHY: 'hierarchy', // Hierarchical tree view
};

// Error Messages
export const ERROR_MESSAGES = {
  FETCH_FAILED: 'Failed to fetch data from server',
  ASSIGNMENT_FAILED: 'Failed to assign tag to entity',
  CREATION_FAILED: 'Failed to create new entity',
  VALIDATION_FAILED: 'Validation failed for input data',
  NETWORK_ERROR: 'Network connection error',
  PERMISSION_DENIED: 'Permission denied for this operation',
};

// Success Messages
export const SUCCESS_MESSAGES = {
  ASSIGNMENT_SUCCESS: 'Tag successfully assigned to entity',
  CREATION_SUCCESS: 'Entity created successfully',
  UPDATE_SUCCESS: 'Entity updated successfully',
  DELETE_SUCCESS: 'Entity deleted successfully',
};

// CSS Classes (for consistent styling)
export const CSS_CLASSES = {
  // Tag Classes
  TAG_UNASSIGNED: 'tag-unassigned',
  TAG_ASSIGNED: 'tag-assigned',
  TAG_PARENT: 'tag-parent',
  TAG_DRAGGING: 'tag-dragging',
  TAG_HOVER: 'tag-hover',
  
  // Cart Classes
  CART_EMPTY: 'cart-empty',
  CART_FILLED: 'cart-filled',
  CART_DROP_TARGET: 'cart-drop-target',
  CART_DROP_ACTIVE: 'cart-drop-active',
  
  // Grid Classes
  GRID_CONTAINER: 'grid-container',
  GRID_TAGS: 'grid-tags',
  GRID_ENTITIES: 'grid-entities',
  GRID_LOADING: 'grid-loading',
  GRID_ERROR: 'grid-error',
  
  // Layout Classes
  LAYOUT_COLUMN: 'layout-column',
  LAYOUT_ROW: 'layout-row',
  LAYOUT_CENTERED: 'layout-centered',
  LAYOUT_SPACED: 'layout-spaced',
};

// Default Configuration
export const DEFAULT_CONFIG = {
  AUTO_REFRESH: true,       // Auto refresh data
  REFRESH_INTERVAL: 30000,  // Refresh interval in ms (30 seconds)
  DRAG_ENABLED: true,       // Enable drag and drop
  ANIMATIONS_ENABLED: true, // Enable animations
  SOUND_ENABLED: false,     // Enable sound effects
  DEBUG_MODE: false,        // Enable debug logging
};

// Utility Functions
export const UTILS = {
  /**
   * Generate a unique ID for entities
   * @returns {string} Unique ID
   */
  generateEntityId: () => {
    return `entity_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  },

  /**
   * Format entity name for display
   * @param {string} name - Entity name
   * @returns {string} Formatted name
   */
  formatEntityName: (name) => {
    return name ? name.trim() : 'Unnamed Entity';
  },

  /**
   * Get entity type display name
   * @param {number} typeId - Entity type ID
   * @param {Array} entityTypes - Array of entity types
   * @returns {string} Display name
   */
  getEntityTypeName: (typeId, entityTypes = DEFAULT_ENTITY_TYPES) => {
    const type = entityTypes.find(t => t.i_typ_ent === typeId);
    return type ? type.x_dsc_ent : `Type ${typeId}`;
  },

  /**
   * Get assignment reason display name
   * @param {number} reasonId - Reason ID
   * @param {Array} reasons - Array of assignment reasons
   * @returns {string} Display name
   */
  getAssignmentReasonName: (reasonId, reasons = DEFAULT_ASSIGNMENT_REASONS) => {
    const reason = reasons.find(r => r.i_rsn === reasonId);
    return reason ? reason.x_rsn : `Reason ${reasonId}`;
  },

  /**
   * Validate entity name
   * @param {string} name - Entity name to validate
   * @returns {boolean} True if valid
   */
  isValidEntityName: (name) => {
    return name && 
           name.trim().length >= VALIDATION.MIN_ENTITY_NAME && 
           name.trim().length <= VALIDATION.MAX_ENTITY_NAME;
  },

  /**
   * Calculate grid dimensions
   * @param {number} tagCount - Number of tags
   * @returns {Object} Grid dimensions
   */
  calculateGridDimensions: (tagCount) => {
    const rows = Math.ceil(tagCount / GRID_LAYOUT.TAGS_PER_ROW);
    const cols = Math.min(tagCount, GRID_LAYOUT.TAGS_PER_ROW);
    const width = cols * (GRID_LAYOUT.TAG_SIZE + GRID_LAYOUT.TAG_MARGIN) + GRID_LAYOUT.GRID_PADDING * 2;
    const height = rows * (GRID_LAYOUT.TAG_SIZE + GRID_LAYOUT.TAG_MARGIN) + GRID_LAYOUT.GRID_PADDING * 2;
    
    return { rows, cols, width, height };
  },
};

export default {
  GRID_LAYOUT,
  COLORS,
  ENTITY_STATUS,
  ASSIGNMENT_STATUS,
  DRAG_TYPES,
  DEFAULT_ENTITY_TYPES,
  DEFAULT_ASSIGNMENT_REASONS,
  DEFAULT_DEVICE_TYPES,
  ANIMATIONS,
  HIERARCHY,
  VALIDATION,
  COMPONENT_STATES,
  VIEW_MODES,
  ERROR_MESSAGES,
  SUCCESS_MESSAGES,
  CSS_CLASSES,
  DEFAULT_CONFIG,
  UTILS,
};