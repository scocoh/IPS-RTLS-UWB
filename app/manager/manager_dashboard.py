# Name: manager_dashboard.py
# Version: 0.1.1
# Created: 250712
# Modified: 250712
# Creator: ParcoAdmin
# Modified By: ParcoAdmin + Claude
# Description: Dedicated Dashboard Manager for ParcoRTLS - Customer-facing dashboard data broker - Fixed import and database issues
# Location: /home/parcoadmin/parco_fastapi/app/manager
# Role: Backend
# Status: Active
# Dependent: TRUE

"""
Dashboard Manager for ParcoRTLS

Dedicated manager that acts as a data broker specifically for dashboard clients.
Follows established ParcoRTLS manager patterns with customer-specific filtering.

Key Features:
- Customer-specific data filtering via rtls_message_router
- Independent scaling from RealTime manager
- Feeds websocket_dashboard.py on port 8008
- Registers as RESOURCE_TYPE = 8008 in tlkresources
- Modular design following existing manager architecture

Data Flow:
Hardware → DashboardManager → websocket_dashboard.py:8008 → Customer frontends
"""

import asyncio
import logging
import json
from datetime import datetime
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass

# Centralized configuration
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import get_server_host

# Configure logging FIRST - before any conditional imports that use logger
import logging
logger = logging.getLogger(__name__)

# Core manager imports
from .manager import Manager
from .models import GISData, Tag
from .enums import eRunState

# Centralized configuration
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import get_server_host

# Configure logging FIRST - before any conditional imports that use logger
import logging
logger = logging.getLogger(__name__)

# Core manager imports
from .manager import Manager
from .models import GISData, Tag
from .enums import eRunState

# Message routing - conditional import for graceful fallback
try:
    from .rtls_message_router import RTLSMessageRouter, RoutedMessage, RouteAction
    HAS_MESSAGE_ROUTER = True
except ImportError:
    logger.warning("rtls_message_router not available - using basic message processing")
    HAS_MESSAGE_ROUTER = False
    RTLSMessageRouter = None
    RoutedMessage = None
    RouteAction = None

# WebSocket dashboard integration - conditional import
try:
    from . import websocket_dashboard
    HAS_DASHBOARD_WEBSOCKET = True
except ImportError:
    logger.warning("websocket_dashboard not available - dashboard broadcasting disabled")
    HAS_DASHBOARD_WEBSOCKET = False
    websocket_dashboard = None

# Centralized configuration
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import get_server_host

# Configure logging
logger = logging.getLogger(__name__)

# Dashboard Manager Configuration
DASHBOARD_RESOURCE_TYPE = 8008
DASHBOARD_PORT = 8008
DASHBOARD_STREAM_TYPE = "Dashboard"

@dataclass
class DashboardCustomer:
    """Customer configuration for dashboard filtering"""
    customer_id: int
    customer_name: str
    is_active: bool = True
    message_router: Optional[Any] = None  # RTLSMessageRouter when available
    
class DashboardManager(Manager):
    """
    Dedicated Dashboard Manager for customer-facing dashboard data.
    
    Extends the base Manager class with dashboard-specific functionality:
    - Customer filtering and routing
    - Dashboard message formatting
    - Integration with websocket_dashboard.py
    """
    
    def __init__(self, name: str, zone_id: int = 1):
        """
        Initialize Dashboard Manager.
        
        Args:
            name: Manager instance name (should be registered in tlkresources)
            zone_id: Default zone ID for dashboard operations
        """
        super().__init__(name, zone_id)
        
        # Dashboard-specific attributes
        self.dashboard_customers: Dict[int, DashboardCustomer] = {}
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.processing_task: Optional[asyncio.Task] = None
        
        # Performance tracking
        self.messages_processed = 0
        self.messages_routed = 0
        self.customers_active = 0
        
        logger.info(f"Dashboard Manager '{name}' initialized for zone {zone_id}")

    async def start(self) -> bool:
        """
        Start the Dashboard Manager and all its components.
        
        Returns:
            bool: True if started successfully
        """
        logger.info(f"Starting Dashboard Manager: {self.name}")
        
        # Start base manager
        if not await super().start():
            logger.error("Failed to start base manager")
            return False
        
        # Load dashboard customers
        await self.load_dashboard_customers()
        
        # Start message processing
        self.processing_task = asyncio.create_task(self._process_message_queue())
        
        logger.info(f"Dashboard Manager '{self.name}' started successfully")
        return True

    async def shutdown(self) -> bool:
        """
        Shutdown the Dashboard Manager gracefully.
        
        Returns:
            bool: True if shutdown completed successfully
        """
        logger.info(f"Shutting down Dashboard Manager: {self.name}")
        
        # Stop message processing
        if self.processing_task:
            self.processing_task.cancel()
            try:
                await self.processing_task
            except asyncio.CancelledError:
                pass
        
        # Shutdown base manager
        return await super().shutdown()

    async def load_dashboard_customers(self) -> bool:
        """
        Load dashboard customer configurations from database.
        
        Returns:
            bool: True if customers loaded successfully
        """
        try:
            # Use database handler from base manager
            if not self.database.is_database_ready():
                logger.warning("Database not ready, using default customer")
                await self._load_default_customer()
                return False
            
            # Query dashboard customer configurations
            # This would use the existing database tables from websocket_dashboard.py
            conn_string = self.database.get_connection_strings()[0]
            
            import asyncpg
            async with asyncpg.create_pool(conn_string) as pool:
                async with pool.acquire() as conn:
                    # Check if dashboard tables exist
                    table_exists = await conn.fetchval("""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables 
                            WHERE table_name = 'dashboard_customer_config'
                        )
                    """)
                    
                    if not table_exists:
                        logger.warning("Dashboard tables not found, using default customer")
                        await self._load_default_customer()
                        return False
                    
                    # Load customer configurations
                    customers = await conn.fetch("""
                        SELECT customer_id, customer_name, created_at
                        FROM dashboard_customer_config
                        WHERE created_at IS NOT NULL
                        ORDER BY customer_id
                    """)
                    
                    self.dashboard_customers.clear()
                    for customer_row in customers:
                        customer_id = customer_row['customer_id']
                        customer = DashboardCustomer(
                            customer_id=customer_id,
                            customer_name=customer_row['customer_name']
                        )
                        
        # Initialize message router for this customer
                        if HAS_MESSAGE_ROUTER and RTLSMessageRouter:
                            customer.message_router = RTLSMessageRouter(customer_id)
                            await customer.message_router.load_routing_configuration()
                        else:
                            logger.warning(f"Message routing not available for customer {customer_id}")
                            customer.message_router = None
                        
                        self.dashboard_customers[customer_id] = customer
                        logger.info(f"Loaded dashboard customer: {customer_id} - {customer.customer_name}")
            
            self.customers_active = len(self.dashboard_customers)
            logger.info(f"Loaded {self.customers_active} dashboard customers")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load dashboard customers: {str(e)}")
            await self._load_default_customer()
            return False

    async def _load_default_customer(self):
        """Load default customer configuration as fallback"""
        default_customer = DashboardCustomer(
            customer_id=1,
            customer_name="Default Customer"
        )
        
        if HAS_MESSAGE_ROUTER and RTLSMessageRouter:
            default_customer.message_router = RTLSMessageRouter(1)
            await default_customer.message_router.load_routing_configuration()
        else:
            logger.warning("Message routing not available for default customer")
            default_customer.message_router = None
        
        self.dashboard_customers[1] = default_customer
        self.customers_active = 1
        logger.info("Loaded default dashboard customer")

    async def parser_data_arrived(self, sm: dict) -> bool:
        """
        Override base manager data processing for dashboard-specific handling.
        
        Args:
            sm: Raw message dictionary
            
        Returns:
            bool: True if processed successfully
        """
        # Process message using base manager logic first
        success = await super().parser_data_arrived(sm)
        if not success:
            return False
        
        # Add to dashboard processing queue
        await self.message_queue.put(sm)
        self.messages_processed += 1
        
        return True

    async def _process_message_queue(self):
        """
        Process messages from the queue for dashboard clients.
        """
        logger.info("Started dashboard message processing loop")
        
        while self.run_state == eRunState.Started:
            try:
                # Get message from queue with timeout
                sm = await asyncio.wait_for(self.message_queue.get(), timeout=1.0)
                
                # Process message for each customer
                await self._process_dashboard_message(sm)
                
            except asyncio.TimeoutError:
                # Normal timeout - continue loop
                continue
            except Exception as e:
                logger.error(f"Error processing dashboard message: {str(e)}")
                await asyncio.sleep(1)

    async def _process_dashboard_message(self, sm: dict):
        """
        Process a single message for all dashboard customers.
        
        Args:
            sm: Raw message dictionary
        """
        try:
            # Create GISData from raw message
            msg = await self.data.process_gis_data(sm, sm.get('zone_id', self.zone_id))
            
            if HAS_MESSAGE_ROUTER and RouteAction:
                # Process message for each active customer with message routing
                routed_messages = []
                for customer_id, customer in self.dashboard_customers.items():
                    if not customer.is_active or not customer.message_router:
                        continue
                    
                    # Apply customer-specific routing
                    routed_message = await customer.message_router.process_gis_message(
                        msg, 
                        sm.get('sensor_payload', '')
                    )
                    
                    if routed_message and RouteAction.DASHBOARD in routed_message.actions:
                        routed_messages.append(routed_message)
                
                # Broadcast to dashboard WebSocket if we have routed messages
                if routed_messages:
                    await self._broadcast_to_dashboard(routed_messages)
                    self.messages_routed += len(routed_messages)
            else:
                # Fallback: basic message processing without routing
                await self._broadcast_basic_message(msg)
                self.messages_routed += 1
                
        except Exception as e:
            logger.error(f"Failed to process dashboard message: {str(e)}")

    async def _broadcast_basic_message(self, msg: GISData):
        """
        Fallback method to broadcast basic message without routing.
        
        Args:
            msg: GISData message to broadcast
        """
        try:
            # Create basic dashboard message for all customers
            basic_data = {
                'type': 'rtls_data',
                'timestamp': datetime.now().isoformat(),
                'data': [{
                    'tag_id': msg.id,
                    'x': msg.x,
                    'y': msg.y,
                    'z': msg.z,
                    'timestamp': msg.ts.isoformat(),
                    'zone_id': msg.zone_id,
                    'confidence': msg.cnf,
                    'battery': msg.bat,
                    'gateway_id': msg.gwid
                }]
            }
            
            # Broadcast to all customers
            if HAS_DASHBOARD_WEBSOCKET and websocket_dashboard:
                target_customers = set(self.dashboard_customers.keys())
                await websocket_dashboard.broadcast_dashboard_message(basic_data, target_customers)
            else:
                logger.debug("Dashboard WebSocket not available - message not broadcast")
                
        except Exception as e:
            logger.error(f"Failed to broadcast basic message: {str(e)}")

    async def _broadcast_to_dashboard(self, routed_messages: List[Any]):
        """
        Broadcast routed messages to dashboard WebSocket clients.
        
        Args:
            routed_messages: List of messages routed for dashboard display
        """
        try:
            if not HAS_DASHBOARD_WEBSOCKET or not websocket_dashboard:
                logger.debug("Dashboard WebSocket not available - skipping broadcast")
                return
                
            # Group messages by customer
            customer_messages: Dict[int, List[Any]] = {}
            for routed_msg in routed_messages:
                customer_id = routed_msg.customer_id
                if customer_id not in customer_messages:
                    customer_messages[customer_id] = []
                customer_messages[customer_id].append(routed_msg)
            
            # Send to each customer's dashboard clients
            for customer_id, messages in customer_messages.items():
                dashboard_data = {
                    'type': 'rtls_data',
                    'customer_id': customer_id,
                    'message_count': len(messages),
                    'timestamp': datetime.now().isoformat(),
                    'data': [self._format_dashboard_message(msg) for msg in messages]
                }
                
                # Use the broadcast function from websocket_dashboard.py
                target_customers = {customer_id}
                await websocket_dashboard.broadcast_dashboard_message(dashboard_data, target_customers)
                
        except Exception as e:
            logger.error(f"Failed to broadcast to dashboard: {str(e)}")

    def _format_dashboard_message(self, routed_message: Any) -> Dict[str, Any]:
        """
        Format a routed message for dashboard display.
        
        Args:
            routed_message: Routed message to format
            
        Returns:
            Dict: Formatted message for dashboard
        """
        gis_data = routed_message.rtls_message.gis_data
        
        formatted = {
            'tag_id': gis_data.id,
            'x': gis_data.x,
            'y': gis_data.y,
            'z': gis_data.z,
            'timestamp': gis_data.ts.isoformat(),
            'zone_id': gis_data.zone_id,
            'confidence': gis_data.cnf,
            'battery': gis_data.bat,
            'gateway_id': gis_data.gwid,
            'actions': [action.value for action in routed_message.actions],
            'priority': routed_message.priority,
            'route_timestamp': routed_message.route_timestamp.isoformat()
        }
        
        # Add sensor payload if present
        if routed_message.rtls_message.sensor_payload:
            formatted['sensor_data'] = routed_message.rtls_message.sensor_payload
        
        return formatted

    def get_dashboard_stats(self) -> Dict[str, Any]:
        """
        Get dashboard manager statistics.
        
        Returns:
            Dict: Dashboard statistics
        """
        base_stats = self.get_manager_stats()
        
        dashboard_stats = {
            'dashboard_manager': {
                'customers_configured': len(self.dashboard_customers),
                'customers_active': self.customers_active,
                'messages_processed': self.messages_processed,
                'messages_routed': self.messages_routed,
                'queue_size': self.message_queue.qsize(),
                'routing_rate': (self.messages_routed / max(self.messages_processed, 1)) * 100
            },
            'customer_stats': {
                customer_id: {
                    'name': customer.customer_name,
                    'active': customer.is_active,
                    'router_stats': customer.message_router.get_routing_statistics() 
                    if customer.message_router else None
                }
                for customer_id, customer in self.dashboard_customers.items()
            }
        }
        
        # Merge with base manager stats
        base_stats.update(dashboard_stats)
        return base_stats

    def is_healthy(self) -> bool:
        """
        Check if the dashboard manager is healthy.
        
        Returns:
            bool: True if healthy
        """
        base_healthy = super().is_healthy()
        dashboard_healthy = (
            len(self.dashboard_customers) > 0 and
            self.processing_task is not None and
            not self.processing_task.done()
        )
        
        return base_healthy and dashboard_healthy