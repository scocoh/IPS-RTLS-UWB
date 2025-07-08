/* Name: TriggerTemplates.js */
/* Version: 0.1.0 */
/* Created: 250707 */
/* Modified: 250707 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin + Claude */
/* Description: Trigger template presets module */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/NewTriggerDemo/modules */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

import React from "react";
import { Button, Card, Row, Col } from "react-bootstrap";

const TriggerTemplates = ({ onApplyTemplate, showTemplates = true }) => {
  const templatePresets = [
    { 
      name: "Entry Detection", 
      direction: "OnEnter", 
      color: "#00ff00", 
      description: "Detects when tags enter the area",
      icon: "🚪"
    },
    { 
      name: "Exit Detection", 
      direction: "OnExit", 
      color: "#ff6600", 
      description: "Detects when tags leave the area",
      icon: "🚶"
    },
    { 
      name: "Continuous Monitoring", 
      direction: "WhileIn", 
      color: "#0066ff", 
      description: "Monitors tags while in the area",
      icon: "👁️"
    },
    { 
      name: "Boundary Crossing", 
      direction: "OnCross", 
      color: "#ff00ff", 
      description: "Detects any boundary crossing",
      icon: "🔄"
    }
  ];

  if (!showTemplates) return null;

  return (
    <Card className="mb-3">
      <Card.Header>🎯 Quick Templates</Card.Header>
      <Card.Body>
        <Row>
          {templatePresets.map((template, index) => (
            <Col md={6} lg={3} key={index} className="mb-2">
              <Button
                variant="outline-primary"
                size="sm"
                className="w-100"
                onClick={() => onApplyTemplate(template)}
                style={{ 
                  borderColor: template.color,
                  color: template.color,
                  textAlign: 'left',
                  height: '70px',
                  position: 'relative'
                }}
              >
                <div style={{ 
                  position: 'absolute', 
                  top: '5px', 
                  right: '8px', 
                  fontSize: '16px' 
                }}>
                  {template.icon}
                </div>
                <div style={{ fontSize: '12px', fontWeight: 'bold', marginBottom: '4px' }}>
                  {template.name}
                </div>
                <div style={{ fontSize: '10px', opacity: 0.8, lineHeight: '1.2' }}>
                  {template.description}
                </div>
              </Button>
            </Col>
          ))}
        </Row>
      </Card.Body>
    </Card>
  );
};

export default TriggerTemplates;