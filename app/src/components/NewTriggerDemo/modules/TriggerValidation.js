/* Name: TriggerValidation.js */
/* Version: 0.1.0 */
/* Created: 250707 */
/* Modified: 250707 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin + Claude */
/* Description: Trigger form validation utilities */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/NewTriggerDemo/modules */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

import React from "react";
import { Alert } from "react-bootstrap";

// Validation rules
export const validateTriggerForm = (formData) => {
  const { triggerName, selectedZone, triggerDirection, coordinates, polygonArea } = formData;
  const errors = [];
  
  if (!triggerName?.trim()) errors.push("Trigger name is required");
  if (triggerName && triggerName.length > 50) errors.push("Trigger name must be less than 50 characters");
  if (!selectedZone) errors.push("Zone selection is required");
  if (!triggerDirection) errors.push("Direction selection is required");
  if (!coordinates || coordinates.length < 3) errors.push("At least 3 polygon points are required");
  if (polygonArea < 1) errors.push("Polygon area too small (minimum 1 sq ft)");
  if (polygonArea > 10000) errors.push("Polygon area too large (maximum 10,000 sq ft)");
  
  return errors;
};

// Calculate polygon area in square feet
export const calculatePolygonArea = (coordinates) => {
  if (!coordinates || coordinates.length < 3) return 0;
  
  let area = 0;
  for (let i = 0; i < coordinates.length; i++) {
    const j = (i + 1) % coordinates.length;
    area += parseFloat(coordinates[i].n_x) * parseFloat(coordinates[j].n_y);
    area -= parseFloat(coordinates[j].n_x) * parseFloat(coordinates[i].n_y);
  }
  return Math.abs(area) / 2;
};

// Auto-generate trigger name
export const generateTriggerName = (selectedZone, triggerDirection) => {
  if (!selectedZone || !triggerDirection) return "";
  
  const zoneName = selectedZone.x_nm_zn.replace(/\s+/g, '_');
  const direction = triggerDirection.replace(/\s+/g, '_');
  const timestamp = new Date().toISOString().slice(11, 19).replace(/:/g, '');
  return `${zoneName}_${direction}_${timestamp}`;
};

// Validation Error Display Component
export const ValidationErrorDisplay = ({ errors }) => {
  if (!errors || errors.length === 0) return null;

  return (
    <Alert variant="danger">
      <Alert.Heading>⚠️ Please fix the following issues:</Alert.Heading>
      <ul style={{ margin: 0 }}>
        {errors.map((error, index) => (
          <li key={index}>{error}</li>
        ))}
      </ul>
    </Alert>
  );
};

// Drawing Instructions Component
export const DrawingInstructions = ({ showMapForDrawing, coordinatesLength }) => {
  if (!showMapForDrawing) return null;

  let instruction = "";
  let variant = "info";

  if (coordinatesLength === 0) {
    instruction = "Click on the map to start drawing your trigger polygon";
    variant = "info";
  } else if (coordinatesLength < 3) {
    instruction = `${coordinatesLength} point(s) placed. Need at least 3 points for a polygon.`;
    variant = "warning";
  } else {
    instruction = `${coordinatesLength} points placed. Click 'Save Trigger' when ready.`;
    variant = "success";
  }

  return (
    <div style={{ 
      padding: "8px 12px", 
      backgroundColor: variant === "success" ? "#d4edda" : 
                      variant === "warning" ? "#fff3cd" : "#cce7ff",
      borderRadius: "3px",
      marginBottom: "10px",
      border: `1px solid ${variant === "success" ? "#c3e6cb" : 
                            variant === "warning" ? "#ffeaa7" : "#b3d9ff"}`,
      fontSize: "13px"
    }}>
      <strong>Drawing Mode:</strong> {instruction}
    </div>
  );
};