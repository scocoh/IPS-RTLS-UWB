/* Name: PointEditor.js */
/* Version: 0.1.0 */
/* Created: 250707 */
/* Modified: 250707 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin + Claude */
/* Description: Point editing modal component for ZoneViewer */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/ZoneViewer/components */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

import React, { useState, useEffect, useRef } from "react";
import { Modal, Button, Form } from "react-bootstrap";

const PointEditor = ({ 
  isOpen, 
  onClose, 
  vertex, 
  vertices, 
  onUpdateVertices 
}) => {
  const [xValue, setXValue] = useState("");
  const [yValue, setYValue] = useState("");
  const [relatedVertices, setRelatedVertices] = useState([]);
  const [isUpdating, setIsUpdating] = useState(false);
  
  const xInputRef = useRef(null);

  // Initialize values when vertex changes
  useEffect(() => {
    if (vertex) {
      const x = Number(vertex.x).toFixed(6);
      const y = Number(vertex.y).toFixed(6);
      setXValue(x);
      setYValue(y);
      
      // Find related vertices (same coordinates in same zone)
      const related = vertices.filter(v => 
        v.zone_id === vertex.zone_id &&
        Number(v.x).toFixed(6) === x &&
        Number(v.y).toFixed(6) === y
      );
      setRelatedVertices(related);
    }
  }, [vertex, vertices]);

  // Auto-focus X input when modal opens
  useEffect(() => {
    if (isOpen && xInputRef.current) {
      // Small delay to ensure modal is fully rendered
      setTimeout(() => {
        xInputRef.current.focus();
        xInputRef.current.select();
      }, 100);
    }
  }, [isOpen]);

  const handleUpdate = async () => {
    if (!vertex || relatedVertices.length === 0) return;
    
    setIsUpdating(true);
    try {
      // Prepare updates for all related vertices
      const updates = relatedVertices.map(v => ({
        vertex_id: v.vertex_id,
        x: parseFloat(xValue).toFixed(6),
        y: parseFloat(yValue).toFixed(6),
        z: Number(v.z).toFixed(6),
        order: v.order
      }));

      await onUpdateVertices(updates);
      onClose();
    } catch (error) {
      console.error("❌ Error updating vertices:", error);
      alert("Failed to update vertices: " + error.message);
    } finally {
      setIsUpdating(false);
    }
  };

  const handleCancel = () => {
    onClose();
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleUpdate();
    } else if (e.key === 'Escape') {
      e.preventDefault();
      handleCancel();
    }
  };

  if (!vertex) return null;

  return (
    <Modal show={isOpen} onHide={onClose} centered>
      <Modal.Header closeButton>
        <Modal.Title>Edit Point Location</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <div style={{ marginBottom: "15px" }}>
          <strong>Point Details:</strong>
          <div style={{ fontSize: "14px", color: "#666", marginTop: "5px" }}>
            Primary Vertex: {vertex.vertex_id} (Zone {vertex.zone_id})
            {relatedVertices.length > 1 && (
              <div style={{ marginTop: "5px", color: "#007bff" }}>
                Related Vertices: {relatedVertices.map(v => v.vertex_id).join(", ")}
                <br />
                <em>All {relatedVertices.length} vertices will be updated together</em>
              </div>
            )}
          </div>
        </div>

        <Form>
          <Form.Group style={{ marginBottom: "15px" }}>
            <Form.Label>X Coordinate</Form.Label>
            <Form.Control
              ref={xInputRef}
              type="text"
              value={xValue}
              onChange={(e) => setXValue(e.target.value)}
              onKeyDown={handleKeyPress}
              placeholder="0.000000"
              style={{ fontFamily: "monospace" }}
            />
          </Form.Group>

          <Form.Group style={{ marginBottom: "15px" }}>
            <Form.Label>Y Coordinate</Form.Label>
            <Form.Control
              type="text"
              value={yValue}
              onChange={(e) => setYValue(e.target.value)}
              onKeyDown={handleKeyPress}
              placeholder="0.000000"
              style={{ fontFamily: "monospace" }}
            />
          </Form.Group>
        </Form>

        <div style={{ 
          fontSize: "12px", 
          color: "#666", 
          padding: "10px", 
          backgroundColor: "#f8f9fa", 
          borderRadius: "4px" 
        }}>
          <strong>Instructions:</strong> Enter coordinates to 6 decimal places. 
          Press Enter to update, Escape to cancel.
          {relatedVertices.length > 1 && (
            <div style={{ marginTop: "5px" }}>
              <strong>Note:</strong> Since this is a start/end point, both vertices will be updated with the same coordinates.
            </div>
          )}
        </div>
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={handleCancel} disabled={isUpdating}>
          Cancel
        </Button>
        <Button variant="primary" onClick={handleUpdate} disabled={isUpdating}>
          {isUpdating ? "Updating..." : "Update"}
        </Button>
      </Modal.Footer>
    </Modal>
  );
};

export default PointEditor;