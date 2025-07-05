/* Name: EntityGridView.js */
/* Version: 0.2.1 */
/* Created: 250704 */
/* Modified: 250704 */
/* Creator: ParcoAdmin */
/* Modified By: AI Assistant */
/* Description: Visual grid layout component for Entity management - displays tags and carts */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/Entities */
/* Role: Frontend UI Component */
/* Status: Active */
/* Dependent: TRUE */

// /home/parcoadmin/parco_fastapi/app/src/components/Entities/EntityGridView.js
// Version: v0.2.1 - Initial creation with grid layout for tags and entity carts
// ParcoRTLS © 2025 — Scott Cohen, Jesse Chunn, etc.

import React, { useState, useRef, useCallback, useMemo } from 'react';
import { 
  GRID_LAYOUT, 
  COLORS, 
  DRAG_TYPES, 
  CSS_CLASSES, 
  ANIMATIONS,
  UTILS 
} from './EntityTypes';

/**
 * TagChecker Component - Round tag with number
 */
const TagChecker = ({ tag, isAssigned, isDragging, onDragStart, onDragEnd }) => {
  const tagStyle = {
    width: `${GRID_LAYOUT.TAG_SIZE}px`,
    height: `${GRID_LAYOUT.TAG_SIZE}px`,
    borderRadius: '50%',
    backgroundColor: isAssigned ? COLORS.TAG_ASSIGNED : COLORS.TAG_UNASSIGNED,
    border: `2px solid ${COLORS.TAG_BORDER}`,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    margin: `${GRID_LAYOUT.TAG_MARGIN}px`,
    cursor: isDragging ? 'grabbing' : 'grab',
    fontSize: '12px',
    fontWeight: 'bold',
    color: COLORS.TAG_TEXT,
    userSelect: 'none',
    transition: `all ${ANIMATIONS.HOVER_DURATION}ms ease`,
    opacity: isDragging ? 0.7 : 1,
    transform: isDragging ? 'scale(1.1)' : 'scale(1)',
    zIndex: isDragging ? 1000 : 1,
  };

  return (
    <div
      style={tagStyle}
      draggable
      onDragStart={(e) => onDragStart(e, tag)}
      onDragEnd={onDragEnd}
      className={`${CSS_CLASSES.TAG_UNASSIGNED} ${isDragging ? CSS_CLASSES.TAG_DRAGGING : ''}`}
      title={`Tag: ${tag.x_id_dev}`}
    >
      {tag.x_id_dev}
    </div>
  );
};

/**
 * EntityCart Component - Visual cart/bucket for entities
 */
const EntityCart = ({ entity, devices, onDrop, onDragOver, onDragLeave, isDropTarget }) => {
  const cartStyle = {
    width: `${GRID_LAYOUT.CART_WIDTH}px`,
    height: `${GRID_LAYOUT.CART_HEIGHT}px`,
    backgroundColor: isDropTarget ? COLORS.CART_ACTIVE : COLORS.CART_BACKGROUND,
    border: `2px solid ${COLORS.CART_BORDER}`,
    borderRadius: '8px',
    margin: `${GRID_LAYOUT.CART_MARGIN}px`,
    padding: '8px',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    cursor: 'pointer',
    transition: `all ${ANIMATIONS.HOVER_DURATION}ms ease`,
    position: 'relative',
    boxShadow: isDropTarget ? '0 4px 8px rgba(0,0,0,0.2)' : '0 2px 4px rgba(0,0,0,0.1)',
  };

  const headerStyle = {
    fontSize: '14px',
    fontWeight: 'bold',
    color: COLORS.TEXT_PRIMARY,
    textAlign: 'center',
    marginBottom: '4px',
    overflow: 'hidden',
    textOverflow: 'ellipsis',
    whiteSpace: 'nowrap',
    width: '100%',
  };

  const deviceCountStyle = {
    fontSize: '12px',
    color: COLORS.TEXT_SECONDARY,
    textAlign: 'center',
  };

  const deviceListStyle = {
    fontSize: '10px',
    color: COLORS.TEXT_SECONDARY,
    textAlign: 'center',
    marginTop: '4px',
    overflow: 'hidden',
    height: '20px',
  };

  return (
    <div
      style={cartStyle}
      onDrop={onDrop}
      onDragOver={onDragOver}
      onDragLeave={onDragLeave}
      className={`${CSS_CLASSES.CART_EMPTY} ${isDropTarget ? CSS_CLASSES.CART_DROP_ACTIVE : ''}`}
      title={`Entity: ${entity.x_nm_ent || entity.x_id_ent}`}
    >
      <div style={headerStyle}>
        {UTILS.formatEntityName(entity.x_nm_ent || entity.x_id_ent)}
      </div>
      <div style={deviceCountStyle}>
        {devices.length} device{devices.length !== 1 ? 's' : ''}
      </div>
      <div style={deviceListStyle}>
        {devices.slice(0, 3).map(d => d.x_id_dev).join(', ')}
        {devices.length > 3 && '...'}
      </div>
    </div>
  );
};

/**
 * UnassignedTagsGrid Component - Grid layout for unassigned tags
 */
const UnassignedTagsGrid = ({ tags, onDragStart, onDragEnd, draggingTag }) => {
  const gridDimensions = UTILS.calculateGridDimensions(tags.length);
  
  const gridStyle = {
    display: 'flex',
    flexWrap: 'wrap',
    maxWidth: `${gridDimensions.width}px`,
    padding: `${GRID_LAYOUT.GRID_PADDING}px`,
    backgroundColor: COLORS.GRID_BACKGROUND,
    border: `1px solid ${COLORS.GRID_BORDER}`,
    borderRadius: '8px',
    margin: '10px',
  };

  const headerStyle = {
    width: '100%',
    fontSize: '16px',
    fontWeight: 'bold',
    color: COLORS.TEXT_PRIMARY,
    marginBottom: '10px',
    textAlign: 'center',
  };

  return (
    <div style={gridStyle} className={CSS_CLASSES.GRID_TAGS}>
      <div style={headerStyle}>Unassigned Tags ({tags.length})</div>
      {tags.map(tag => (
        <TagChecker
          key={tag.x_id_dev}
          tag={tag}
          isAssigned={false}
          isDragging={draggingTag === tag.x_id_dev}
          onDragStart={onDragStart}
          onDragEnd={onDragEnd}
        />
      ))}
      {tags.length === 0 && (
        <div style={{ 
          width: '100%', 
          textAlign: 'center', 
          color: COLORS.TEXT_SECONDARY,
          fontSize: '14px',
          padding: '20px'
        }}>
          No unassigned tags
        </div>
      )}
    </div>
  );
};

/**
 * EntityCartsGrid Component - Grid layout for entity carts
 */
const EntityCartsGrid = ({ entities, entityAssignments, onDrop, onDragOver, onDragLeave, dropTarget }) => {
  const gridStyle = {
    display: 'flex',
    flexWrap: 'wrap',
    padding: `${GRID_LAYOUT.GRID_PADDING}px`,
    backgroundColor: COLORS.GRID_BACKGROUND,
    border: `1px solid ${COLORS.GRID_BORDER}`,
    borderRadius: '8px',
    margin: '10px',
    minHeight: '200px',
  };

  const headerStyle = {
    width: '100%',
    fontSize: '16px',
    fontWeight: 'bold',
    color: COLORS.TEXT_PRIMARY,
    marginBottom: '10px',
    textAlign: 'center',
  };

  return (
    <div style={gridStyle} className={CSS_CLASSES.GRID_ENTITIES}>
      <div style={headerStyle}>Entity Carts ({entities.length})</div>
      {entities.map(entity => (
        <EntityCart
          key={entity.x_id_ent}
          entity={entity}
          devices={entityAssignments[entity.x_id_ent] || []}
          onDrop={(e) => onDrop(e, entity)}
          onDragOver={(e) => onDragOver(e, entity)}
          onDragLeave={(e) => onDragLeave(e, entity)}
          isDropTarget={dropTarget === entity.x_id_ent}
        />
      ))}
      {entities.length === 0 && (
        <div style={{ 
          width: '100%', 
          textAlign: 'center', 
          color: COLORS.TEXT_SECONDARY,
          fontSize: '14px',
          padding: '20px'
        }}>
          No entities created yet
        </div>
      )}
    </div>
  );
};

/**
 * CreateEntityButton Component - Button to create new entity
 */
const CreateEntityButton = ({ onClick, entityTypes, selectedEntityType, onEntityTypeChange }) => {
  const buttonStyle = {
    backgroundColor: COLORS.CART_BACKGROUND,
    border: `2px dashed ${COLORS.CART_BORDER}`,
    borderRadius: '8px',
    width: `${GRID_LAYOUT.CART_WIDTH}px`,
    height: `${GRID_LAYOUT.CART_HEIGHT}px`,
    margin: `${GRID_LAYOUT.CART_MARGIN}px`,
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    cursor: 'pointer',
    transition: `all ${ANIMATIONS.HOVER_DURATION}ms ease`,
    fontSize: '12px',
    color: COLORS.TEXT_SECONDARY,
  };

  const hoverStyle = {
    ...buttonStyle,
    backgroundColor: COLORS.CART_HOVER,
    borderColor: COLORS.TAG_BORDER,
  };

  const [isHovered, setIsHovered] = useState(false);

  return (
    <div
      style={isHovered ? hoverStyle : buttonStyle}
      onClick={onClick}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      title="Create New Entity"
    >
      <div style={{ fontSize: '24px', marginBottom: '4px' }}>+</div>
      <div>Create Entity</div>
    </div>
  );
};

/**
 * EntityGridView Component - Main grid view component
 */
const EntityGridView = ({ 
  devices, 
  entities, 
  entityAssignments, 
  entityTypes,
  selectedEntityType,
  onEntityTypeChange,
  onTagDrop,
  onCreateEntity,
  loading 
}) => {
  const [draggingTag, setDraggingTag] = useState(null);
  const [dropTarget, setDropTarget] = useState(null);
  const dragDataRef = useRef(null);

  // Handle drag start
  const handleDragStart = useCallback((e, tag) => {
    setDraggingTag(tag.x_id_dev);
    dragDataRef.current = tag;
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/plain', tag.x_id_dev);
  }, []);

  // Handle drag end
  const handleDragEnd = useCallback(() => {
    setDraggingTag(null);
    setDropTarget(null);
    dragDataRef.current = null;
  }, []);

  // Handle drag over entity
  const handleDragOver = useCallback((e, entity) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
    setDropTarget(entity.x_id_ent);
  }, []);

  // Handle drag leave entity
  const handleDragLeave = useCallback((e, entity) => {
    // Only clear drop target if leaving the entity area
    if (!e.currentTarget.contains(e.relatedTarget)) {
      setDropTarget(null);
    }
  }, []);

  // Handle drop on entity
  const handleDrop = useCallback((e, entity) => {
    e.preventDefault();
    const tag = dragDataRef.current;
    if (tag && onTagDrop) {
      onTagDrop(tag, entity);
    }
    setDraggingTag(null);
    setDropTarget(null);
    dragDataRef.current = null;
  }, [onTagDrop]);

  // Filter unassigned devices
  const unassignedDevices = useMemo(() => {
    const assignedDeviceIds = new Set();
    Object.values(entityAssignments).forEach(assignments => {
      assignments.forEach(assignment => {
        assignedDeviceIds.add(assignment.x_id_dev);
      });
    });
    return devices.filter(device => !assignedDeviceIds.has(device.x_id_dev));
  }, [devices, entityAssignments]);

  const containerStyle = {
    display: 'flex',
    flexDirection: 'column',
    padding: '20px',
    backgroundColor: COLORS.GRID_BACKGROUND,
    minHeight: `${GRID_LAYOUT.MIN_GRID_HEIGHT}px`,
    minWidth: `${GRID_LAYOUT.MIN_GRID_WIDTH}px`,
  };

  const headerStyle = {
    fontSize: '24px',
    fontWeight: 'bold',
    color: COLORS.TEXT_PRIMARY,
    textAlign: 'center',
    marginBottom: '20px',
  };

  const statsStyle = {
    display: 'flex',
    justifyContent: 'center',
    gap: '20px',
    marginBottom: '20px',
    fontSize: '14px',
    color: COLORS.TEXT_SECONDARY,
  };

  if (loading) {
    return (
      <div style={containerStyle} className={CSS_CLASSES.GRID_LOADING}>
        <div style={headerStyle}>Loading Entity Grid...</div>
        <div style={{ textAlign: 'center', color: COLORS.TEXT_SECONDARY }}>
          Please wait while we load your entities and devices.
        </div>
      </div>
    );
  }

  return (
    <div style={containerStyle} className={CSS_CLASSES.GRID_CONTAINER}>
      <div style={headerStyle}>Entity Grid Interface</div>
      
      <div style={statsStyle}>
        <span>Total Devices: {devices.length}</span>
        <span>Unassigned: {unassignedDevices.length}</span>
        <span>Entities: {entities.length}</span>
      </div>

      <div style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'center' }}>
        <UnassignedTagsGrid
          tags={unassignedDevices}
          onDragStart={handleDragStart}
          onDragEnd={handleDragEnd}
          draggingTag={draggingTag}
        />
        
        <div style={{ display: 'flex', flexDirection: 'column' }}>
          <EntityCartsGrid
            entities={entities}
            entityAssignments={entityAssignments}
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            dropTarget={dropTarget}
          />
          
          <div style={{ 
            display: 'flex', 
            flexWrap: 'wrap', 
            padding: `${GRID_LAYOUT.GRID_PADDING}px`,
            justifyContent: 'center'
          }}>
            <CreateEntityButton
              onClick={onCreateEntity}
              entityTypes={entityTypes}
              selectedEntityType={selectedEntityType}
              onEntityTypeChange={onEntityTypeChange}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default EntityGridView;