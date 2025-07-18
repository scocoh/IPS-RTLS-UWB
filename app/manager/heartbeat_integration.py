# Name: heartbeat_integration.py
# Version: 0.1.0
# Created: 250716
# Modified: 250716
# Creator: ParcoAdmin
# Modified By: AI Assistant
# Description: Integration layer between FastAPI routes and manager heartbeat system
# Location: /home/parcoadmin/parco_fastapi/app/manager
# Role: Backend Integration
# Status: Active
# Dependent: TRUE

"""
Integration layer between FastAPI routes and manager heartbeat system.
This module provides the bridge between the REST API endpoints and the
heartbeat monitoring system running in the manager.
"""

import asyncio
import logging
from typing import Dict, Optional, Any
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class HeartbeatIntegration:
    """
    Integration class to bridge FastAPI routes with manager heartbeat system.
    """
    
    def __init__(self):
        self.manager_instances = {}  # Will store manager instances
        self.heartbeat_handlers = {}  # Will store heartbeat handlers
        
    def register_manager(self, manager_name: str, manager_instance):
        """
        Register a manager instance for heartbeat integration.
        
        Args:
            manager_name: Name of the manager
            manager_instance: Manager instance with heartbeat handler
        """
        self.manager_instances[manager_name] = manager_instance
        if hasattr(manager_instance, 'heartbeat'):
            self.heartbeat_handlers[manager_name] = manager_instance.heartbeat
            logger.info(f"Registered manager {manager_name} with heartbeat handler")
        else:
            logger.warning(f"Manager {manager_name} does not have heartbeat handler")
    
    def get_primary_manager(self):
        """
        Get the primary manager instance (usually RealTimeManager).
        
        Returns:
            Manager instance or None if not found
        """
        # Try to get RealTimeManager first
        for manager_name, manager_instance in self.manager_instances.items():
            if 'RealTime' in manager_name:
                return manager_instance
        
        # Fallback to any manager with heartbeat handler
        for manager_name, manager_instance in self.manager_instances.items():
            if hasattr(manager_instance, 'heartbeat'):
                return manager_instance
        
        return None
    
    def get_heartbeat_handler(self, manager_name: Optional[str] = None):
        """
        Get heartbeat handler for a specific manager or the primary one.
        
        Args:
            manager_name: Optional specific manager name
            
        Returns:
            Heartbeat handler instance or None
        """
        if manager_name and manager_name in self.heartbeat_handlers:
            return self.heartbeat_handlers[manager_name]
        
        # Get primary manager's heartbeat handler
        primary_manager = self.get_primary_manager()
        if primary_manager and hasattr(primary_manager, 'heartbeat'):
            return primary_manager.heartbeat
        
        return None
    
    async def get_port_health_status(self) -> Dict[str, Any]:
        """
        Get current port health status from heartbeat monitoring.
        
        Returns:
            Dictionary with port health status
        """
        heartbeat_handler = self.get_heartbeat_handler()
        if not heartbeat_handler:
            raise HTTPException(status_code=503, detail="No heartbeat handler available")
        
        try:
            stats = heartbeat_handler.get_heartbeat_stats()
            return {
                "status": "success",
                "heartbeat_stats": stats,
                "port_health": stats.get('port_health_monitoring', {}),
                "manager_count": len(self.manager_instances)
            }
        except Exception as e:
            logger.error(f"Error getting port health status: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error getting port health: {str(e)}")
    
    async def refresh_port_monitoring(self) -> Dict[str, Any]:
        """
        Refresh port monitoring from database.
        
        Returns:
            Dictionary with refresh status
        """
        heartbeat_handler = self.get_heartbeat_handler()
        if not heartbeat_handler:
            raise HTTPException(status_code=503, detail="No heartbeat handler available")
        
        try:
            primary_manager = self.get_primary_manager()
            if not primary_manager:
                raise HTTPException(status_code=503, detail="No primary manager available")
            
            success = await heartbeat_handler.refresh_port_monitoring(primary_manager)
            
            if success:
                return {
                    "status": "success",
                    "message": "Port monitoring refreshed successfully",
                    "monitored_ports": len(heartbeat_handler.port_health_monitor)
                }
            else:
                return {
                    "status": "error",
                    "message": "Failed to refresh port monitoring",
                    "error": heartbeat_handler.last_database_error
                }
        except Exception as e:
            logger.error(f"Error refreshing port monitoring: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error refreshing port monitoring: {str(e)}")
    
    async def get_unhealthy_ports(self) -> Dict[str, Any]:
        """
        Get list of unhealthy ports.
        
        Returns:
            Dictionary with unhealthy ports
        """
        heartbeat_handler = self.get_heartbeat_handler()
        if not heartbeat_handler:
            raise HTTPException(status_code=503, detail="No heartbeat handler available")
        
        try:
            unhealthy_ports = heartbeat_handler.get_unhealthy_ports()
            return {
                "status": "success",
                "unhealthy_ports": unhealthy_ports,
                "count": len(unhealthy_ports)
            }
        except Exception as e:
            logger.error(f"Error getting unhealthy ports: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error getting unhealthy ports: {str(e)}")
    
    async def get_scaling_candidates(self) -> Dict[str, Any]:
        """
        Get ports that are candidates for scaling.
        
        Returns:
            Dictionary with scaling candidates
        """
        heartbeat_handler = self.get_heartbeat_handler()
        if not heartbeat_handler:
            raise HTTPException(status_code=503, detail="No heartbeat handler available")
        
        try:
            scaling_candidates = heartbeat_handler.get_scaling_candidates()
            return {
                "status": "success",
                "scaling_candidates": scaling_candidates,
                "count": len(scaling_candidates)
            }
        except Exception as e:
            logger.error(f"Error getting scaling candidates: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error getting scaling candidates: {str(e)}")
    
    async def get_next_scaling_port(self, base_port: int) -> Dict[str, Any]:
        """
        Get next available port for scaling.
        
        Args:
            base_port: Base port to scale from
            
        Returns:
            Dictionary with next available port
        """
        heartbeat_handler = self.get_heartbeat_handler()
        if not heartbeat_handler:
            raise HTTPException(status_code=503, detail="No heartbeat handler available")
        
        try:
            next_port = heartbeat_handler.get_next_scaling_port(base_port)
            
            if next_port:
                return {
                    "status": "success",
                    "base_port": base_port,
                    "next_port": next_port,
                    "scaling_range": f"{heartbeat_handler.SCALING_PORT_RANGE_START}-{heartbeat_handler.SCALING_PORT_RANGE_END}"
                }
            else:
                return {
                    "status": "error",
                    "message": f"No available ports for scaling base port {base_port}"
                }
        except Exception as e:
            logger.error(f"Error getting next scaling port: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error getting next scaling port: {str(e)}")

# Global integration instance
heartbeat_integration = HeartbeatIntegration()

# Helper functions for FastAPI routes
async def get_integrated_port_health():
    """Helper function for FastAPI port health endpoint."""
    return await heartbeat_integration.get_port_health_status()

async def refresh_integrated_port_monitoring():
    """Helper function for FastAPI port monitoring refresh endpoint."""
    return await heartbeat_integration.refresh_port_monitoring()

async def get_integrated_unhealthy_ports():
    """Helper function for FastAPI unhealthy ports endpoint."""
    return await heartbeat_integration.get_unhealthy_ports()

async def get_integrated_scaling_candidates():
    """Helper function for FastAPI scaling candidates endpoint."""
    return await heartbeat_integration.get_scaling_candidates()

async def get_integrated_next_scaling_port(base_port: int):
    """Helper function for FastAPI next scaling port endpoint."""
    return await heartbeat_integration.get_next_scaling_port(base_port)