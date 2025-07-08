/* Name: TriggerSuccessAlert.js */
/* Version: 0.1.0 */
/* Created: 250707 */
/* Modified: 250707 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin + Claude */
/* Description: Success notification component for trigger creation */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/NewTriggerDemo/modules */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

import React from "react";
import { Alert, Badge } from "react-bootstrap";

const TriggerSuccessAlert = ({ triggerData, onDismiss }) => {
  if (!triggerData) return null;

  return (
    <Alert variant="success" dismissible onClose={onDismiss}>
      <Alert.Heading>✅ Trigger Created Successfully!</Alert.Heading>
      
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px', marginBottom: '10px' }}>
        <Badge variant="primary" style={{ fontSize: '12px' }}>
          ID: {triggerData.id}
        </Badge>
        <Badge variant="info" style={{ fontSize: '12px' }}>
          {triggerData.direction}
        </Badge>
        <Badge variant="secondary" style={{ fontSize: '12px' }}>
          {triggerData.area} sq ft
        </Badge>
        <Badge variant="light" style={{ fontSize: '12px' }}>
          {triggerData.timestamp}
        </Badge>
      </div>
      
      <div style={{ fontSize: '14px' }}>
        <p style={{ margin: '5px 0' }}>
          <strong>Name:</strong> {triggerData.name}
        </p>
        <p style={{ margin: '5px 0' }}>
          <strong>Zone:</strong> {triggerData.zone}
        </p>
        {triggerData.description && (
          <p style={{ margin: '5px 0' }}>
            <strong>Description:</strong> {triggerData.description}
          </p>
        )}
      </div>
    </Alert>
  );
};

export default TriggerSuccessAlert;