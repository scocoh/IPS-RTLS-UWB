/* Name: TriggerMapTab.js */
/* Version: 0.1.4 */
/* Created: 250625 */
/* Modified: 250706 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin + Claude */
/* Description: Enhanced Map & Trigger tab component with full NewTriggerViewer integration */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/NewTriggerDemo/components */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

import React, { useState, useEffect, useMemo } from "react";
import { Container, Row, Col, Form, Button, Card, Alert, Badge } from "react-bootstrap";
import NewTriggerViewer from "../../NewTriggerViewer";

const TriggerMapTab = ({
  zones,
  selectedZone,
  triggers,
  tagsData,
  isConnected,
  triggerEvents,
  showTriggerEvents,
  setShowTriggerEvents,
  portableTriggerContainment,
  // NEW: Enhanced props from NTD_index
  mapSettings = {},
  highlightedTrigger = null,
  enhancedTriggerPolygons = [],
  enableResponsive = true,
  enableControls = true,
  height = "600px",
  width = "100%"
}) => {
  // Local state for map-specific controls
  const [showExistingTriggers, setShowExistingTriggers] = useState(true);
  const [selectedTriggerTypes, setSelectedTriggerTypes] = useState(new Set(['portable', 'zone']));
  const [mapMode, setMapMode] = useState('view'); // 'view', 'analyze', 'debug'
  const [showMapStats, setShowMapStats] = useState(false);
  
  // Map configuration
  const mapId = selectedZone?.map_id || zones[0]?.map_id;
  const checkedZones = selectedZone ? [selectedZone.i_zn] : [];

  // Enhanced trigger polygons with filtering and highlighting
  const processedTriggerPolygons = useMemo(() => {
    if (!enhancedTriggerPolygons || enhancedTriggerPolygons.length === 0) return [];
    
    return enhancedTriggerPolygons
      .filter(trigger => {
        // Filter by selected types
        const triggerType = trigger.isPortable ? 'portable' : 'zone';
        if (!selectedTriggerTypes.has(triggerType)) return false;
        
        // Filter by zone if applicable
        if (selectedZone && trigger.zone_id && trigger.zone_id !== selectedZone.i_zn) return false;
        
        return true;
      })
      .map(trigger => ({
        ...trigger,
        // Enhanced styling based on state
        color: trigger.isHighlighted ? '#ff6b35' : 
               trigger.isContained ? '#e74c3c' : 
               trigger.isPortable ? '#9b59b6' : '#3498db',
        fillOpacity: trigger.isHighlighted ? 0.8 : 
                     trigger.isContained ? 0.6 : 0.4,
        weight: trigger.isHighlighted ? 4 : 2,
        // Add pulsing effect for highlighted triggers
        className: trigger.isHighlighted ? 'highlighted-trigger' : ''
      }));
  }, [enhancedTriggerPolygons, selectedTriggerTypes, selectedZone, highlightedTrigger]);

  // Calculate map statistics
  const mapStats = useMemo(() => {
    const activeTags = Object.keys(tagsData).length;
    const visibleTriggers = processedTriggerPolygons.length;
    const portableTriggers = processedTriggerPolygons.filter(t => t.isPortable).length;
    const zoneTriggers = processedTriggerPolygons.filter(t => !t.isPortable).length;
    const containedTriggers = processedTriggerPolygons.filter(t => t.isContained).length;
    
    return {
      activeTags,
      visibleTriggers,
      portableTriggers,
      zoneTriggers,
      containedTriggers,
      connectionStatus: isConnected ? 'Connected' : 'Disconnected'
    };
  }, [tagsData, processedTriggerPolygons, isConnected]);

  // Handle trigger type filter changes
  const handleTriggerTypeChange = (type, checked) => {
    const newTypes = new Set(selectedTriggerTypes);
    if (checked) {
      newTypes.add(type);
    } else {
      newTypes.delete(type);
    }
    setSelectedTriggerTypes(newTypes);
  };

  // Handle map mode changes
  const handleMapModeChange = (mode) => {
    setMapMode(mode);
    // Could trigger different behaviors based on mode
    console.log(`Map mode changed to: ${mode}`);
  };

  // Recent trigger events for quick reference
  const recentTriggerEvents = useMemo(() => {
    return triggerEvents.slice(-5).reverse(); // Last 5 events, newest first
  }, [triggerEvents]);

  return (
    <Container fluid className="trigger-map-tab">
      <Row>
        {/* Left sidebar - Controls */}
        <Col md={3}>
          <Card className="mb-3">
            <Card.Header>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span>Map Controls</span>
                <Badge variant={isConnected ? 'success' : 'danger'}>
                  {isConnected ? '●' : '○'} {mapStats.connectionStatus}
                </Badge>
              </div>
            </Card.Header>
            <Card.Body>
              {/* Map Mode Selection */}
              <Form.Group className="mb-3">
                <Form.Label>Map Mode</Form.Label>
                <Form.Select 
                  value={mapMode} 
                  onChange={(e) => handleMapModeChange(e.target.value)}
                  size="sm"
                >
                  <option value="view">View Mode</option>
                  <option value="analyze">Analyze Mode</option>
                  <option value="debug">Debug Mode</option>
                </Form.Select>
              </Form.Group>

              {/* Trigger Visibility Controls */}
              <Form.Group className="mb-3">
                <Form.Label>Show Triggers</Form.Label>
                <div>
                  <Form.Check
                    type="switch"
                    id="show-triggers"
                    label="Show All Triggers"
                    checked={showExistingTriggers}
                    onChange={(e) => setShowExistingTriggers(e.target.checked)}
                  />
                </div>
              </Form.Group>

              {/* Trigger Type Filters */}
              {showExistingTriggers && (
                <Form.Group className="mb-3">
                  <Form.Label>Trigger Types</Form.Label>
                  <div>
                    <Form.Check
                      type="checkbox"
                      id="portable-triggers"
                      label={`Portable (${mapStats.portableTriggers})`}
                      checked={selectedTriggerTypes.has('portable')}
                      onChange={(e) => handleTriggerTypeChange('portable', e.target.checked)}
                    />
                    <Form.Check
                      type="checkbox"
                      id="zone-triggers"
                      label={`Zone-based (${mapStats.zoneTriggers})`}
                      checked={selectedTriggerTypes.has('zone')}
                      onChange={(e) => handleTriggerTypeChange('zone', e.target.checked)}
                    />
                  </div>
                </Form.Group>
              )}

              {/* Trigger Events Control */}
              <Form.Group className="mb-3">
                <Form.Check
                  type="switch"
                  id="show-trigger-events"
                  label="Show Trigger Events"
                  checked={showTriggerEvents}
                  onChange={(e) => setShowTriggerEvents(e.target.checked)}
                />
              </Form.Group>

              {/* Map Statistics Toggle */}
              <Form.Group className="mb-3">
                <Form.Check
                  type="switch"
                  id="show-map-stats"
                  label="Show Statistics"
                  checked={showMapStats}
                  onChange={(e) => setShowMapStats(e.target.checked)}
                />
              </Form.Group>
            </Card.Body>
          </Card>

          {/* Map Statistics */}
          {showMapStats && (
            <Card className="mb-3">
              <Card.Header>Map Statistics</Card.Header>
              <Card.Body>
                <div style={{ fontSize: '14px' }}>
                  <div className="mb-2">
                    <strong>Active Tags:</strong> <Badge variant="primary">{mapStats.activeTags}</Badge>
                  </div>
                  <div className="mb-2">
                    <strong>Visible Triggers:</strong> <Badge variant="info">{mapStats.visibleTriggers}</Badge>
                  </div>
                  <div className="mb-2">
                    <strong>Contained:</strong> <Badge variant="warning">{mapStats.containedTriggers}</Badge>
                  </div>
                  <div className="mb-2">
                    <strong>Zone:</strong> {selectedZone?.x_nm_zn || 'None selected'}
                  </div>
                  {mapMode === 'debug' && (
                    <div style={{ marginTop: '10px', fontSize: '12px', color: '#666' }}>
                      <div>Map ID: {mapId}</div>
                      <div>Checked Zones: {checkedZones.join(', ')}</div>
                      <div>Highlighted: {highlightedTrigger || 'None'}</div>
                    </div>
                  )}
                </div>
              </Card.Body>
            </Card>
          )}

          {/* Recent Trigger Events */}
          {showTriggerEvents && recentTriggerEvents.length > 0 && (
            <Card className="mb-3">
              <Card.Header>Recent Events</Card.Header>
              <Card.Body style={{ maxHeight: '200px', overflowY: 'auto' }}>
                {recentTriggerEvents.map((event, index) => (
                  <div 
                    key={index} 
                    style={{ 
                      fontSize: '12px', 
                      marginBottom: '8px',
                      padding: '4px 8px',
                      backgroundColor: event.trigger_id === highlightedTrigger ? '#fff3cd' : '#f8f9fa',
                      border: '1px solid #dee2e6',
                      borderRadius: '3px'
                    }}
                  >
                    <div>
                      <strong>T{event.trigger_id}</strong> - {event.event_type}
                    </div>
                    <div style={{ color: '#666' }}>
                      Tag: {event.tag_id} at {new Date(event.timestamp).toLocaleTimeString()}
                    </div>
                  </div>
                ))}
              </Card.Body>
            </Card>
          )}
        </Col>

        {/* Main map area */}
        <Col md={9}>
          {!selectedZone && (
            <Alert variant="warning" className="mb-3">
              Please select a zone to view the map and triggers.
            </Alert>
          )}
          
          {selectedZone && (
            <div>
              {/* Map header with zone info */}
              <div style={{ 
                display: 'flex', 
                justifyContent: 'space-between', 
                alignItems: 'center', 
                marginBottom: '15px',
                padding: '10px',
                backgroundColor: '#f8f9fa',
                border: '1px solid #dee2e6',
                borderRadius: '4px'
              }}>
                <div>
                  <h5 style={{ margin: 0 }}>
                    Zone {selectedZone.i_zn} - {selectedZone.x_nm_zn}
                  </h5>
                  <small style={{ color: '#666' }}>
                    Map ID: {mapId} | Mode: {mapMode.charAt(0).toUpperCase() + mapMode.slice(1)}
                  </small>
                </div>
                <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
                  {highlightedTrigger && (
                    <Badge variant="warning" style={{ animation: 'pulse 1s infinite' }}>
                      Trigger {highlightedTrigger} highlighted
                    </Badge>
                  )}
                  <Badge variant={isConnected ? 'success' : 'danger'}>
                    {mapStats.activeTags} tags active
                  </Badge>
                </div>
              </div>

              {/* Enhanced NewTriggerViewer with all new features */}
              <NewTriggerViewer
                key={`map-${selectedZone.i_zn}-${mapMode}`} // Force re-render on zone/mode change
                mapId={mapId}
                zones={[selectedZone]}
                checkedZones={checkedZones}
                useLeaflet={true}
                enableDrawing={false}
                showExistingTriggers={showExistingTriggers}
                existingTriggerPolygons={processedTriggerPolygons}
                tagsData={tagsData}
                triggers={triggers}
                // NEW: Enhanced responsive and control props
                enableResponsive={enableResponsive}
                enableControls={enableControls}
                height={height}
                width={width}
                // NEW: Map settings integration
                {...mapSettings}
              />

              {/* Debug information (only in debug mode) */}
              {mapMode === 'debug' && (
                <div style={{
                  marginTop: '15px',
                  padding: '10px',
                  backgroundColor: '#f1f3f4',
                  border: '1px solid #dadce0',
                  borderRadius: '4px',
                  fontSize: '12px',
                  fontFamily: 'monospace'
                }}>
                  <strong>Debug Info:</strong><br/>
                  Tags Data: {JSON.stringify(Object.keys(tagsData))}<br/>
                  Processed Triggers: {processedTriggerPolygons.length}<br/>
                  Map Settings: {JSON.stringify(mapSettings)}<br/>
                  Highlighted Trigger: {highlightedTrigger || 'None'}<br/>
                  Selected Types: {Array.from(selectedTriggerTypes).join(', ')}
                </div>
              )}
            </div>
          )}
        </Col>
      </Row>

      {/* CSS for highlight animation */}
      <style jsx>{`
        @keyframes pulse {
          0% { opacity: 1; }
          50% { opacity: 0.5; }
          100% { opacity: 1; }
        }
        
        .highlighted-trigger {
          animation: pulse 2s ease-in-out infinite;
        }
      `}</style>
    </Container>
  );
};

export default TriggerMapTab;