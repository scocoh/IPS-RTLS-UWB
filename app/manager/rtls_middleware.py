# Name: rtls_middleware.py
# Version: 0.1.0
# Created: 971201
# Modified: 250502
# Creator: ParcoAdmin
# Modified By: ParcoAdmin
# Description: ParcoRTLS backend script
# Location: /home/parcoadmin/parco_fastapi/app/manager
# Role: Backend
# Status: Active
# Dependent: TRUE

# /home/parcoadmin/parco_fastapi/app/manager/rtls_middleware.py
# Version: 0.1.1
# Created: 250712
# Modified: 250712
# Creator: ParcoAdmin + Claude
# Modified By: ParcoAdmin + Claude
# Description: RTLS message filtering middleware - integrates with existing WebSocket infrastructure - FIXED TYPE ERRORS
# Location: /home/parcoadmin/parco_fastapi/app/manager
# Role: Backend
# Status: Active
# Dependent: True

"""
RTLS Message Filtering Middleware

This middleware integrates with your existing WebSocket infrastructure to provide
configurable message filtering without major architectural changes.

Integration points:
- Works with existing GISData model
- Plugs into current WebSocket message flow
- Minimal changes to existing code
- Protocol-agnostic design

Usage in existing WebSocket servers:
```python
from .rtls_middleware import RTLSFilterMiddleware

# Initialize middleware
filter_middleware = RTLSFilterMiddleware(customer_id=1)

# In your message processing loop:
async def process_message(gis_data: GISData):
    # Apply filtering
    routed_message = await filter_middleware.filter_message(gis_data)
    
    if routed_message and filter_middleware.should_send_to_dashboard(routed_message):
        # Send to dashboard clients
        await send_to_dashboard_clients(routed_message)
    
    if routed_message and filter_middleware.should_log_message(routed_message):
        # Log to database
        await log_to_database(routed_message)
```
"""

import asyncio
import logging
from typing import Dict, List, Set, Optional, Any, Callable
from datetime import datetime
import json

# Import our router
from .rtls_message_router import RTLSMessageRouter, RoutedMessage, RouteAction, MessageCategory
from .models import GISData

logger = logging.getLogger(__name__)

class RTLSFilterMiddleware:
    """Lightweight middleware for RTLS message filtering."""
    
    def __init__(self, customer_id: int = 1):
        """Initialize filter middleware."""
        self.customer_id = customer_id
        self.router = RTLSMessageRouter(customer_id)
        self.message_hooks: Dict[RouteAction, List[Callable]] = {
            RouteAction.DASHBOARD: [],
            RouteAction.LOGGING: [],
            RouteAction.REALTIME: [],
            RouteAction.SENSOR_PAYLOAD: []
        }
        
        logger.info(f"Initialized RTLS filter middleware for customer {customer_id}")

    async def filter_message(self, gis_data: GISData, 
                           sensor_payload: str = "") -> Optional[RoutedMessage]:
        """Filter a GISData message using customer configuration."""
        return await self.router.process_gis_message(gis_data, sensor_payload)

    def should_send_to_dashboard(self, routed_message: RoutedMessage) -> bool:
        """Check if message should be sent to dashboard clients"""
        return RouteAction.DASHBOARD in routed_message.actions

    def should_log_message(self, routed_message: RoutedMessage) -> bool:
        """Check if message should be logged to database"""
        return RouteAction.LOGGING in routed_message.actions

    def should_send_realtime(self, routed_message: RoutedMessage) -> bool:
        """Check if message should be sent via real-time WebSocket"""
        return RouteAction.REALTIME in routed_message.actions

    def should_include_sensor_payload(self, routed_message: RoutedMessage) -> bool:
        """Check if sensor payload should be included"""
        return RouteAction.SENSOR_PAYLOAD in routed_message.actions

    def get_essential_categories(self) -> Set[MessageCategory]:
        """Get essential message categories for this customer"""
        return {
            MessageCategory.TAG_ID,
            MessageCategory.DATETIME,
            MessageCategory.LOC_2D,
            MessageCategory.LOC_3D,
            MessageCategory.HEARTBEAT
        }

    def is_high_frequency_category(self, category: MessageCategory) -> bool:
        """Check if message category is high frequency (for throttling)"""
        high_freq_categories = {
            MessageCategory.LOC_2D,
            MessageCategory.LOC_3D,
            MessageCategory.HEARTBEAT
        }
        return category in high_freq_categories

    def register_message_hook(self, action: RouteAction, hook_func: Callable):
        """Register a hook function to be called when messages with specific actions are processed."""
        self.message_hooks[action].append(hook_func)
        logger.info(f"Registered hook for action: {action.value}")

    async def process_with_hooks(self, routed_message: RoutedMessage):
        """Process message through registered hooks"""
        for action in routed_message.actions:
            for hook in self.message_hooks.get(action, []):
                try:
                    if asyncio.iscoroutinefunction(hook):
                        await hook(routed_message)
                    else:
                        hook(routed_message)
                except Exception as e:
                    logger.error(f"Error in message hook for {action.value}: {e}")

    def get_filter_summary(self) -> Dict[str, Any]:
        """Get summary of current filter configuration"""
        return {
            "customer_id": self.customer_id,
            "configured_rules": len(self.router.routing_rules),
            "essential_categories": [cat.value for cat in self.get_essential_categories()],
            "statistics": self.router.get_routing_statistics()
        }

    async def reload_configuration(self):
        """Force reload of filter configuration"""
        self.router.last_config_reload = datetime.min
        await self.router.load_routing_configuration()
        logger.info(f"Reloaded filter configuration for customer {self.customer_id}")

# Helper functions for easy integration

async def create_dashboard_filter(customer_id: int = 1) -> RTLSFilterMiddleware:
    """Create a middleware instance configured for dashboard essential messages"""
    middleware = RTLSFilterMiddleware(customer_id)
    await middleware.router.load_routing_configuration()
    return middleware

def extract_sensor_payload_from_gis_data(gis_data: GISData) -> str:
    """Extract sensor payload from GISData."""
    # Check data field first
    if gis_data.data and gis_data.data.strip():
        return gis_data.data
    
    # Could also check other fields or combine multiple fields
    # Example: if sensor data is in a specific format
    
    return ""  # Return empty string instead of None

def is_essential_message(routed_message: RoutedMessage) -> bool:
    """Check if message contains essential categories"""
    essential_categories = {
        MessageCategory.TAG_ID,
        MessageCategory.DATETIME,
        MessageCategory.LOC_2D,
        MessageCategory.LOC_3D,
        MessageCategory.HEARTBEAT
    }
    
    return bool(routed_message.rtls_message.message_categories & essential_categories)

def format_message_for_client(routed_message: RoutedMessage, include_sensor_payload: bool = False) -> Dict[str, Any]:
    """Format routed message for WebSocket client transmission."""
    gis_data = routed_message.rtls_message.gis_data
    
    # Start with core GISData
    message_data = {
        "type": "FilteredRTLS",
        "id": gis_data.id,
        "ts": gis_data.ts.isoformat(),
        "x": gis_data.x,
        "y": gis_data.y,
        "z": gis_data.z,
        "bat": gis_data.bat,
        "cnf": gis_data.cnf,
        "gwid": gis_data.gwid,
        "zone_id": gis_data.zone_id,
        "sequence": gis_data.sequence,
        
        # Routing metadata
        "customer_id": routed_message.customer_id,
        "priority": routed_message.priority,
        "actions": [action.value for action in routed_message.actions],
        "categories": [cat.value for cat in routed_message.rtls_message.message_categories],
        "route_timestamp": routed_message.route_timestamp.isoformat()
    }
    
    # Add RTLS-specific fields if present
    rtls_msg = routed_message.rtls_message
    
    if rtls_msg.proximity_data:
        message_data["proximity"] = rtls_msg.proximity_data
    
    if rtls_msg.range_data:
        message_data["range"] = rtls_msg.range_data
    
    if rtls_msg.motion_detected is not None:
        message_data["motion"] = rtls_msg.motion_detected
    
    if rtls_msg.button_pressed:
        message_data["button"] = rtls_msg.button_pressed
    
    # Include sensor payload if requested and available
    if include_sensor_payload and rtls_msg.sensor_payload:
        message_data["sensor_payload"] = rtls_msg.sensor_payload
        if rtls_msg.sensor_payload_raw:
            message_data["sensor_payload_raw"] = rtls_msg.sensor_payload_raw
    
    return message_data

# Example integration with existing WebSocket server
class WebSocketFilterExample:
    """Example showing how to integrate with existing WebSocket servers."""
    
    def __init__(self):
        self.filter_middleware: Optional[RTLSFilterMiddleware] = None
    
    async def initialize_filtering(self, customer_id: int = 1):
        """Initialize filtering middleware"""
        self.filter_middleware = await create_dashboard_filter(customer_id)
        logger.info("RTLS filtering initialized")
    
    async def process_gis_message(self, gis_data: GISData):
        """Process GISData message with filtering."""
        if not self.filter_middleware:
            # Fallback to original processing if filtering not initialized
            return await self.original_process_gis_message(gis_data)
        
        # Extract sensor payload if present
        sensor_payload = extract_sensor_payload_from_gis_data(gis_data)
        
        # Apply filtering
        routed_message = await self.filter_middleware.filter_message(gis_data, sensor_payload)
        
        if not routed_message:
            # Message was filtered out
            logger.debug(f"Message filtered out for tag {gis_data.id}")
            return
        
        # Process based on routing actions
        if self.filter_middleware.should_send_to_dashboard(routed_message):
            await self.send_to_dashboard_clients(routed_message)
        
        if self.filter_middleware.should_log_message(routed_message):
            await self.log_to_database(routed_message)
        
        if self.filter_middleware.should_send_realtime(routed_message):
            await self.send_to_realtime_clients(routed_message)
        
        # Process hooks
        await self.filter_middleware.process_with_hooks(routed_message)
    
    async def send_to_dashboard_clients(self, routed_message: RoutedMessage):
        """Send filtered message to dashboard clients"""
        # Format message for transmission
        include_payload = bool(self.filter_middleware and self.filter_middleware.should_include_sensor_payload(routed_message))
        message_data = format_message_for_client(routed_message, include_payload)
        
        # Send to WebSocket clients (your existing code)
        # await self.broadcast_to_dashboard_clients(json.dumps(message_data))
        
        logger.debug(f"Sent dashboard message for tag {routed_message.rtls_message.gis_data.id}")
    
    async def log_to_database(self, routed_message: RoutedMessage):
        """Log filtered message to database"""
        # Your existing database logging code
        # await self.insert_gis_data(routed_message.rtls_message.gis_data)
        
        logger.debug(f"Logged message for tag {routed_message.rtls_message.gis_data.id}")
    
    async def send_to_realtime_clients(self, routed_message: RoutedMessage):
        """Send filtered message to real-time clients"""
        # Your existing real-time WebSocket code
        
        logger.debug(f"Sent real-time message for tag {routed_message.rtls_message.gis_data.id}")
    
    async def original_process_gis_message(self, gis_data: GISData):
        """Fallback to original processing"""
        # Your existing message processing code
        pass