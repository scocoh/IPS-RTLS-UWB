# Name: rtls_message_router.py
# Version: 0.1.1
# Created: 971201
# Modified: 250716
# Creator: ParcoAdmin
# Modified By: ParcoAdmin + Claude
# Description: Protocol-agnostic RTLS message routing and filtering system - FIXED DATABASE QUERY
# Location: /home/parcoadmin/parco_fastapi/app/manager
# Role: Backend
# Status: Active
# Dependent: False

"""
Protocol-Agnostic RTLS Message Router

This module provides generic message routing for any RTLS protocol (AllTraq GeoTraqr, 
Ubisense, Zebra, etc.) with configurable filtering based on message categories.

Core RTLS Message Types (from your requirements):
- TAG_ID: Tag identification
- DATETIME: Date/time stamp  
- PROX: Proximity data
- RANGE: Range/distance data
- LOC_2D: 2D location (X, Y)
- LOC_3D: 3D location (X, Y, Z)
- MOTION: Motion detection
- BUTTON: Button press events
- SENSOR_PAYLOAD: Sensor data package (everything non-RTLS/RFID)

Key Features:
- Builds on existing GISData model
- Protocol-agnostic message categorization
- Configurable sensor payload parsing
- Customer-specific routing rules
- Performance optimized for high-frequency location data

Version 0.1.1 Changes:
- Fixed database query to use inbound_message_routing table instead of non-existent v_customer_routing_config view
- Updated load_routing_configuration method to work with actual database schema
"""

import asyncio
import logging
from typing import Dict, List, Set, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import json
from datetime import datetime, timedelta
import asyncpg
from db_config_helper import config_helper

# Import existing models
from .models import GISData, Tag

logger = logging.getLogger(__name__)

class MessageCategory(Enum):
    """RTLS message categories (protocol-agnostic)"""
    TAG_ID = "TAG_ID"
    DATETIME = "DATETIME"
    PROX = "PROX"
    RANGE = "RANGE"
    LOC_2D = "LOC_2D"
    LOC_3D = "LOC_3D"
    MOTION = "MOTION"
    BUTTON = "BUTTON"
    SENSOR_PAYLOAD = "SENSOR_PAYLOAD"
    HEARTBEAT = "HEARTBEAT"
    BATTERY = "BATTERY"
    SIGNAL_STRENGTH = "SIGNAL_STRENGTH"
    ERROR = "ERROR"
    DIAGNOSTIC = "DIAGNOSTIC"
    CONFIG = "CONFIG"
    DEBUG = "DEBUG"

class RouteAction(Enum):
    """Message routing actions"""
    DASHBOARD = "dashboard"
    LOGGING = "logging"
    REALTIME = "realtime"
    SENSOR_PAYLOAD = "sensor_payload"
    BLOCKED = "blocked"

@dataclass
class RTLSMessage:
    """Generic RTLS message structure built on existing GISData model."""
    # Core RTLS fields (extend existing GISData)
    gis_data: GISData
    
    # Additional RTLS fields
    proximity_data: Optional[Dict[str, Any]] = None
    range_data: Optional[Dict[str, Any]] = None
    motion_detected: Optional[bool] = None
    button_pressed: Optional[Dict[str, Any]] = None
    
    # Sensor payload package (everything non-RTLS/RFID)
    sensor_payload: Optional[Dict[str, Any]] = None
    sensor_payload_raw: str = ""
    
    # Message metadata
    message_categories: Set[MessageCategory] = field(default_factory=set)
    original_protocol: str = "generic"
    processed_timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class RoutingRule:
    """Customer routing configuration"""
    customer_id: int
    category: MessageCategory
    dashboard_visible: bool
    logging_enabled: bool
    realtime_enabled: bool
    sensor_payload_enabled: bool
    priority: int
    filter_config: Optional[Dict[str, Any]] = None

@dataclass
class RoutedMessage:
    """Message with routing information applied"""
    rtls_message: RTLSMessage
    customer_id: int
    actions: Set[RouteAction]
    priority: int
    route_timestamp: datetime

class SensorPayloadParser:
    """Parse sensor payload data from various formats"""
    
    def __init__(self):
        self.parsers: Dict[str, Dict[str, Any]] = {}
        
    async def load_parsers(self) -> None:
        """Load sensor payload parsers from database"""
        try:
            conn_str = config_helper.get_connection_string("ParcoRTLSMaint")
            conn = await asyncpg.connect(conn_str)
            
            try:
                # Updated query to check if table exists first
                table_exists = await conn.fetchval("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'v_active_payload_parsers'
                    )
                """)
                
                if table_exists:
                    query = "SELECT x_nm_parser, x_payload_format, x_parse_rules FROM v_active_payload_parsers"
                    rows = await conn.fetch(query)
                    
                    self.parsers = {}
                    for row in rows:
                        self.parsers[row['x_nm_parser']] = {
                            'format': row['x_payload_format'],
                            'rules': row['x_parse_rules']
                        }
                        
                    logger.info(f"Loaded {len(self.parsers)} sensor payload parsers")
                else:
                    logger.warning("v_active_payload_parsers table not found, using default parsers")
                    self._load_default_parsers()
                
            finally:
                await conn.close()
                
        except Exception as e:
            logger.error(f"Failed to load sensor payload parsers: {e}")
            self._load_default_parsers()

    def _load_default_parsers(self):
        """Load default sensor payload parsers"""
        self.parsers = {
            "json_extractor": {
                "format": "JSON",
                "rules": {"extract_all": True, "flatten": False}
            },
            "hex_to_binary": {
                "format": "HEX",
                "rules": {"sensors": [], "buttons": []}
            }
        }

    def parse_payload(self, raw_payload: str, parser_name: Optional[str] = None) -> Dict[str, Any]:
        """Parse sensor payload using specified or auto-detected parser."""
        if not raw_payload:
            return {}
            
        try:
            # Auto-detect parser if not specified
            if parser_name is None:
                parser_name = self._detect_parser(raw_payload)
            
            if parser_name not in self.parsers:
                logger.warning(f"Parser '{parser_name}' not found, using raw payload")
                return {"raw": raw_payload}
            
            parser_config = self.parsers[parser_name]
            payload_format = parser_config['format']
            parse_rules = parser_config['rules']
            
            # Parse based on format
            if payload_format == 'JSON':
                return self._parse_json_payload(raw_payload, parse_rules)
            elif payload_format == 'HEX':
                return self._parse_hex_payload(raw_payload, parse_rules)
            elif payload_format == 'BASE64':
                return self._parse_base64_payload(raw_payload, parse_rules)
            else:
                logger.warning(f"Unknown payload format: {payload_format}")
                return {"raw": raw_payload}
                
        except Exception as e:
            logger.error(f"Failed to parse sensor payload: {e}")
            return {"raw": raw_payload, "parse_error": str(e)}

    def _detect_parser(self, raw_payload: str) -> str:
        """Auto-detect appropriate parser based on payload format"""
        try:
            # Try JSON first
            json.loads(raw_payload)
            return "json_extractor"
        except json.JSONDecodeError:
            pass
        
        # Check if HEX
        if all(c in '0123456789ABCDEFabcdef' for c in raw_payload.replace(' ', '')):
            return "hex_to_binary"
        
        # Default fallback
        return "json_extractor"

    def _parse_json_payload(self, payload: str, rules: Dict[str, Any]) -> Dict[str, Any]:
        """Parse JSON sensor payload"""
        try:
            data = json.loads(payload)
            if rules.get('extract_all', False):
                return self._flatten_dict(data) if rules.get('flatten', False) else data
            return data
        except json.JSONDecodeError:
            return {"raw": payload}

    def _parse_hex_payload(self, payload: str, rules: Dict[str, Any]) -> Dict[str, Any]:
        """Parse HEX sensor payload"""
        try:
            # Remove spaces and convert to bytes
            hex_clean = payload.replace(' ', '')
            payload_bytes = bytes.fromhex(hex_clean)
            
            parsed_data = {}
            
            # Parse sensors if defined
            if 'sensors' in rules:
                for sensor in rules['sensors']:
                    name = sensor['name']
                    offset = sensor['offset']
                    length = sensor['length']
                    scale = sensor.get('scale', 1.0)
                    unit = sensor.get('unit', '')
                    
                    # Extract bytes and convert to integer
                    sensor_bytes = payload_bytes[offset:offset+length]
                    value = int.from_bytes(sensor_bytes, byteorder='big')
                    scaled_value = value * scale
                    
                    parsed_data[name] = {
                        'value': scaled_value,
                        'unit': unit,
                        'raw_value': value
                    }
            
            # Parse buttons if defined
            if 'buttons' in rules:
                for button in rules['buttons']:
                    name = button['name']
                    bit_position = button['bit_position']
                    
                    # Extract bit value
                    byte_index = bit_position // 8
                    bit_index = bit_position % 8
                    
                    if byte_index < len(payload_bytes):
                        byte_value = payload_bytes[byte_index]
                        bit_value = (byte_value >> bit_index) & 1
                        parsed_data[name] = bool(bit_value)
            
            return parsed_data
            
        except Exception as e:
            return {"raw": payload, "hex_parse_error": str(e)}

    def _parse_base64_payload(self, payload: str, rules: Dict[str, Any]) -> Dict[str, Any]:
        """Parse BASE64 sensor payload"""
        try:
            import base64
            decoded_bytes = base64.b64decode(payload)
            # Convert to hex and parse using hex rules
            hex_payload = decoded_bytes.hex().upper()
            return self._parse_hex_payload(hex_payload, rules)
        except Exception as e:
            return {"raw": payload, "base64_parse_error": str(e)}

    def _flatten_dict(self, d: Dict[str, Any], parent_key: str = '', sep: str = '_') -> Dict[str, Any]:
        """Flatten nested dictionary"""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)

class RTLSMessageRouter:
    """Protocol-agnostic RTLS message router."""
    
    def __init__(self, customer_id: int = 1):
        """Initialize message router for specific customer."""
        self.customer_id = customer_id
        self.routing_rules: Dict[MessageCategory, RoutingRule] = {}
        self.payload_parser = SensorPayloadParser()
        self.message_counts: Dict[MessageCategory, int] = {}
        self.last_config_reload = datetime.min
        self.config_cache_duration = timedelta(minutes=5)
        
        # Performance tracking
        self.processed_count = 0
        self.routed_count = 0
        self.last_stats_time = datetime.now()
        
        logger.info(f"Initialized RTLS message router for customer {customer_id}")

    async def load_routing_configuration(self) -> None:
        """Load routing configuration from database - FIXED to use inbound_message_routing table"""
        try:
            # Check if we need to reload config
            if (datetime.now() - self.last_config_reload) < self.config_cache_duration:
                return
            
            conn_str = config_helper.get_connection_string("ParcoRTLSMaint")
            conn = await asyncpg.connect(conn_str)
            
            try:
                # Updated query to use the actual inbound_message_routing table
                query = """
                SELECT message_category, route_to_dashboard, route_to_logging, 
                       route_to_realtime, include_sensor_payload, priority
                FROM inbound_message_routing 
                WHERE customer_id = $1 AND is_enabled = true
                ORDER BY priority, message_category
                """
                
                rows = await conn.fetch(query, self.customer_id)
                
                self.routing_rules = {}
                for row in rows:
                    try:
                        category = MessageCategory(row['message_category'])
                        routing_rule = RoutingRule(
                            customer_id=self.customer_id,
                            category=category,
                            dashboard_visible=row['route_to_dashboard'],
                            logging_enabled=row['route_to_logging'],
                            realtime_enabled=row['route_to_realtime'],
                            sensor_payload_enabled=row['include_sensor_payload'],
                            priority=row['priority']
                        )
                        self.routing_rules[category] = routing_rule
                    except ValueError:
                        logger.warning(f"Unknown message category: {row['message_category']}")
                
                # Load sensor payload parsers
                await self.payload_parser.load_parsers()
                
                self.last_config_reload = datetime.now()
                logger.info(f"Loaded {len(self.routing_rules)} routing rules for customer {self.customer_id}")
                
            finally:
                await conn.close()
                
        except Exception as e:
            logger.error(f"Failed to load routing configuration: {e}")
            await self._load_default_routing()

    async def _load_default_routing(self) -> None:
        """Load default essential routing as fallback"""
        essential_categories = [
            MessageCategory.TAG_ID,
            MessageCategory.DATETIME,
            MessageCategory.LOC_2D,
            MessageCategory.LOC_3D,
            MessageCategory.HEARTBEAT
        ]
        
        self.routing_rules = {}
        for category in essential_categories:
            self.routing_rules[category] = RoutingRule(
                customer_id=self.customer_id,
                category=category,
                dashboard_visible=True,
                logging_enabled=True,
                realtime_enabled=True,
                sensor_payload_enabled=False,
                priority=1 if category in [MessageCategory.LOC_2D, MessageCategory.LOC_3D] else 2
            )
        
        logger.warning(f"Loaded {len(self.routing_rules)} default routing rules as fallback")

    async def process_gis_message(self, gis_data: GISData, 
                                 sensor_payload_raw: str = "") -> Optional[RoutedMessage]:
        """Process GISData message into generic RTLS message with routing."""
        self.processed_count += 1
        
        # Ensure routing configuration is loaded
        await self.load_routing_configuration()
        
        # Create RTLS message from GISData
        rtls_message = await self._create_rtls_message(gis_data, sensor_payload_raw)
        
        # Categorize message
        self._categorize_message(rtls_message)
        
        # Apply routing rules
        routed_message = await self._apply_routing_rules(rtls_message)
        
        if routed_message:
            self.routed_count += 1
            
            # Update message counts
            for category in rtls_message.message_categories:
                self.message_counts[category] = self.message_counts.get(category, 0) + 1
        
        return routed_message

    async def _create_rtls_message(self, gis_data: GISData, 
                                  sensor_payload_raw: str = "") -> RTLSMessage:
        """Create RTLS message from GISData"""
        rtls_message = RTLSMessage(gis_data=gis_data)
        
        # Extract sensor payload if present
        if sensor_payload_raw:
            rtls_message.sensor_payload_raw = sensor_payload_raw
            rtls_message.sensor_payload = self.payload_parser.parse_payload(sensor_payload_raw)
        elif gis_data.data:
            # Use existing data field as sensor payload
            rtls_message.sensor_payload_raw = gis_data.data
            rtls_message.sensor_payload = self.payload_parser.parse_payload(gis_data.data)
        
        # Extract additional RTLS data from payload if available
        if rtls_message.sensor_payload:
            self._extract_rtls_fields(rtls_message)
        
        return rtls_message

    def _extract_rtls_fields(self, rtls_message: RTLSMessage) -> None:
        """Extract RTLS-specific fields from sensor payload"""
        payload = rtls_message.sensor_payload
        if not payload:
            return
        
        # Extract proximity data
        prox_fields = ['proximity', 'prox', 'distance', 'range']
        for field in prox_fields:
            if field in payload:
                rtls_message.proximity_data = {field: payload[field]}
                break
        
        # Extract range data
        range_fields = ['range', 'distance', 'rssi']
        for field in range_fields:
            if field in payload:
                rtls_message.range_data = {field: payload[field]}
                break
        
        # Extract motion detection
        motion_fields = ['motion', 'moving', 'accelerometer', 'motion_detected']
        for field in motion_fields:
            if field in payload:
                rtls_message.motion_detected = bool(payload[field])
                break
        
        # Extract button press data
        button_fields = [k for k in payload.keys() if 'button' in k.lower()]
        if button_fields:
            rtls_message.button_pressed = {field: payload[field] for field in button_fields}

    def _categorize_message(self, rtls_message: RTLSMessage) -> None:
        """Auto-categorize RTLS message based on content"""
        categories = set()
        
        # Always has tag ID and datetime
        categories.add(MessageCategory.TAG_ID)
        categories.add(MessageCategory.DATETIME)
        
        # Location categories
        if rtls_message.gis_data.z != 0:
            categories.add(MessageCategory.LOC_3D)
        else:
            categories.add(MessageCategory.LOC_2D)
        
        # Proximity/Range
        if rtls_message.proximity_data:
            categories.add(MessageCategory.PROX)
        if rtls_message.range_data:
            categories.add(MessageCategory.RANGE)
        
        # Motion
        if rtls_message.motion_detected is not None:
            categories.add(MessageCategory.MOTION)
        
        # Button
        if rtls_message.button_pressed:
            categories.add(MessageCategory.BUTTON)
        
        # Sensor payload
        if rtls_message.sensor_payload:
            categories.add(MessageCategory.SENSOR_PAYLOAD)
        
        # System categories
        if rtls_message.gis_data.bat >= 0:
            categories.add(MessageCategory.BATTERY)
        if rtls_message.gis_data.type and 'heartbeat' in rtls_message.gis_data.type.lower():
            categories.add(MessageCategory.HEARTBEAT)
        
        rtls_message.message_categories = categories

    async def _apply_routing_rules(self, rtls_message: RTLSMessage) -> Optional[RoutedMessage]:
        """Apply customer routing rules to message"""
        actions = set()
        highest_priority = 10
        
        # Check each message category against routing rules
        for category in rtls_message.message_categories:
            rule = self.routing_rules.get(category)
            if not rule:
                continue
            
            # Collect actions based on rule
            if rule.dashboard_visible:
                actions.add(RouteAction.DASHBOARD)
            if rule.logging_enabled:
                actions.add(RouteAction.LOGGING)
            if rule.realtime_enabled:
                actions.add(RouteAction.REALTIME)
            if rule.sensor_payload_enabled and rtls_message.sensor_payload:
                actions.add(RouteAction.SENSOR_PAYLOAD)
            
            # Track highest priority
            if rule.priority < highest_priority:
                highest_priority = rule.priority
        
        # Block message if no actions
        if not actions:
            return None
        
        return RoutedMessage(
            rtls_message=rtls_message,
            customer_id=self.customer_id,
            actions=actions,
            priority=highest_priority,
            route_timestamp=datetime.now()
        )

    def get_dashboard_messages(self, messages: List[RoutedMessage]) -> List[RoutedMessage]:
        """Get messages routed for dashboard display"""
        return [msg for msg in messages if RouteAction.DASHBOARD in msg.actions]

    def get_realtime_messages(self, messages: List[RoutedMessage]) -> List[RoutedMessage]:
        """Get messages routed for real-time streaming"""
        return [msg for msg in messages if RouteAction.REALTIME in msg.actions]

    def get_logging_messages(self, messages: List[RoutedMessage]) -> List[RoutedMessage]:
        """Get messages routed for database logging"""
        return [msg for msg in messages if RouteAction.LOGGING in msg.actions]

    def get_sensor_payload_messages(self, messages: List[RoutedMessage]) -> List[RoutedMessage]:
        """Get messages with sensor payload routing enabled"""
        return [msg for msg in messages if RouteAction.SENSOR_PAYLOAD in msg.actions]

    def get_routing_statistics(self) -> Dict[str, Any]:
        """Get routing statistics"""
        now = datetime.now()
        duration = (now - self.last_stats_time).total_seconds()
        
        stats = {
            "customer_id": self.customer_id,
            "total_processed": self.processed_count,
            "total_routed": self.routed_count,
            "route_rate": self.routed_count / max(self.processed_count, 1),
            "messages_per_second": self.processed_count / max(duration, 1),
            "category_counts": {cat.value: count for cat, count in self.message_counts.items()},
            "configured_rules": len(self.routing_rules),
            "last_config_reload": self.last_config_reload.isoformat(),
            "stats_duration_seconds": duration
        }
        
        return stats