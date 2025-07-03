# Name: manager_clients.py
# Version: 0.1.0
# Created: 250703
# Modified: 250703
# Creator: ParcoAdmin
# Modified By: AI Assistant
# Description: Client manager handler module for ParcoRTLS Manager - Extracted from manager.py v0.1.22
# Location: /home/parcoadmin/parco_fastapi/app/manager
# Role: Backend
# Status: Active
# Dependent: TRUE

"""
Client Manager Handler Module for ParcoRTLS Manager

This module handles all client management operations for the Manager class including:
- WebSocket client management (add, remove, tracking)
- SDK client management and lifecycle
- Event broadcasting to clients
- Client-specific message routing
- Average data distribution to subscribed clients

Extracted from manager.py v0.1.22 for better modularity and maintainability.
"""

import logging
from typing import Dict, List
from fastapi import WebSocket
from manager.sdk_client import SDKClient

logger = logging.getLogger(__name__)

class ManagerClients:
    """
    Handles all client management operations for the Manager class.
    
    This class encapsulates WebSocket client management, SDK client tracking,
    event broadcasting, and message routing operations that were previously 
    part of the main Manager class.
    """
    
    def __init__(self, manager_name: str):
        """
        Initialize the client manager.
        
        Args:
            manager_name: Name of the manager instance for logging
        """
        self.manager_name = manager_name
        
        # Client tracking
        self.sdk_clients: Dict[str, SDKClient] = {}
        self.clients: Dict[str, List[WebSocket]] = {}  # Instance-level clients for TETSE WebSocket
        self.kill_list: List[SDKClient] = []
        
        logger.debug(f"Initialized ManagerClients for manager: {manager_name}")

    # WebSocket Client Management
    async def add_websocket_client(self, reqid: str, websocket: WebSocket) -> bool:
        """
        Add a WebSocket client to tracking.
        
        Args:
            reqid: Request ID for client identification
            websocket: WebSocket connection
            
        Returns:
            bool: True if added successfully
        """
        try:
            logger.debug(f"Adding WebSocket client for reqid {reqid}")
            if reqid not in self.clients:
                self.clients[reqid] = []
            self.clients[reqid].append(websocket)
            logger.debug(f"After adding client, total clients: {sum(len(clients) for clients in self.clients.values())}")
            return True
        except Exception as e:
            logger.error(f"Failed to add WebSocket client {reqid}: {str(e)}")
            return False

    async def remove_websocket_client(self, reqid: str, websocket: WebSocket) -> bool:
        """
        Remove a WebSocket client from tracking.
        
        Args:
            reqid: Request ID for client identification
            websocket: WebSocket connection
            
        Returns:
            bool: True if removed successfully
        """
        try:
            logger.debug(f"Removing WebSocket client for reqid {reqid}")
            if reqid in self.clients:
                if websocket in self.clients[reqid]:
                    self.clients[reqid].remove(websocket)
                if not self.clients[reqid]:
                    del self.clients[reqid]
            logger.debug(f"After removing client, total clients: {sum(len(clients) for clients in self.clients.values())}")
            return True
        except Exception as e:
            logger.error(f"Failed to remove WebSocket client {reqid}: {str(e)}")
            return False

    # SDK Client Management
    def add_sdk_client(self, client_id: str, sdk_client: SDKClient) -> bool:
        """
        Add an SDK client to tracking.
        
        Args:
            client_id: Client identifier
            sdk_client: SDK client object
            
        Returns:
            bool: True if added successfully
        """
        try:
            self.sdk_clients[client_id] = sdk_client
            logger.debug(f"Added SDK client {client_id}, total SDK clients: {len(self.sdk_clients)}")
            return True
        except Exception as e:
            logger.error(f"Failed to add SDK client {client_id}: {str(e)}")
            return False

    def remove_sdk_client(self, client_id: str) -> bool:
        """
        Remove an SDK client from tracking.
        
        Args:
            client_id: Client identifier
            
        Returns:
            bool: True if removed successfully
        """
        try:
            if client_id in self.sdk_clients:
                del self.sdk_clients[client_id]
                logger.debug(f"Removed SDK client {client_id}, total SDK clients: {len(self.sdk_clients)}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to remove SDK client {client_id}: {str(e)}")
            return False

    def get_sdk_client(self, client_id: str) -> SDKClient | None:
        """
        Get an SDK client by ID.
        
        Args:
            client_id: Client identifier
            
        Returns:
            SDKClient: SDK client object or None if not found
        """
        return self.sdk_clients.get(client_id)

    # Event Broadcasting
    async def broadcast_trigger_event(self, event_message: dict, msg_id: str) -> int:
        """
        Broadcast trigger event to relevant SDK and WebSocket clients.
        
        Args:
            event_message: Trigger event message to broadcast
            msg_id: Message/tag ID for filtering
            
        Returns:
            int: Number of clients message was sent to
        """
        sent_count = 0
        
        try:
            # Send to SDK clients
            for client_id, client in self.sdk_clients.items():
                try:
                    if not client.is_closing and client.contains_tag(msg_id):
                        await client.websocket.send_json(event_message)
                        logger.info(f"Sent TriggerEvent to SDK client {client_id}: {event_message}")
                        sent_count += 1
                    else:
                        logger.debug(f"Skipping SDK client {client_id}: closing={client.is_closing}, contains_tag={client.contains_tag(msg_id)}")
                except Exception as e:
                    logger.error(f"Failed to send TriggerEvent to SDK client {client_id}: {str(e)}")

            # Send to WebSocket clients
            for reqid, clients in self.clients.items():
                for client in clients:
                    try:
                        await client.send_json(event_message)
                        logger.debug(f"Sent TriggerEvent to WebSocket client {reqid}: {event_message}")
                        sent_count += 1
                    except Exception as e:
                        logger.error(f"Failed to send TriggerEvent to WebSocket client {reqid}: {str(e)}")
                        
        except Exception as e:
            logger.error(f"Failed to broadcast trigger event: {str(e)}")
            
        return sent_count

    async def broadcast_averaged_data(self, tag_id: str, ave_data: dict) -> int:
        """
        Broadcast averaged data to subscribed WebSocket clients.
        
        Args:
            tag_id: Tag ID for topic filtering
            ave_data: Averaged data to broadcast
            
        Returns:
            int: Number of clients message was sent to
        """
        sent_count = 0
        
        try:
            topic = f"ws_ave_{tag_id}"
            logger.debug(f"Broadcasting averaged data for tag ID:{tag_id} on topic {topic}")
            
            for reqid, clients in list(self.clients.items()):
                if reqid.startswith(topic):
                    for client in clients:
                        try:
                            await client.send_json(ave_data)
                            logger.debug(f"Sent AveragedData to WebSocket client {reqid}: {ave_data}")
                            sent_count += 1
                        except Exception as e:
                            logger.error(f"Failed to send AveragedData to WebSocket client {reqid}: {str(e)}")
                            clients.remove(client)
                            if not clients:
                                del self.clients[reqid]
                                
        except Exception as e:
            logger.error(f"Failed to broadcast averaged data: {str(e)}")
            
        return sent_count

    async def broadcast_event(self, entity_id: str, data: dict) -> int:
        """
        Broadcast event to clients subscribed to a specific entity.
        
        Args:
            entity_id: Entity ID for topic filtering
            data: Event data to broadcast
            
        Returns:
            int: Number of clients message was sent to
        """
        sent_count = 0
        
        try:
            topic = f"ws_event_{entity_id}"
            logger.debug(f"Broadcasting event for {entity_id}: {data}")
            
            if topic not in self.clients:
                logger.debug(f"No active subscribers for topic {topic}")
                return 0
                
            for client in self.clients[topic]:
                try:
                    await client.send_json(data)
                    logger.debug(f"Sent event to client on topic {topic}")
                    sent_count += 1
                except Exception as e:
                    logger.error(f"Failed to send event to client on topic {topic}: {str(e)}")
                    
        except Exception as e:
            logger.error(f"Failed to broadcast event: {str(e)}")
            
        return sent_count

    # Client Cleanup and Maintenance
    async def cleanup_disconnected_clients(self) -> int:
        """
        Clean up disconnected WebSocket clients.
        
        Returns:
            int: Number of clients cleaned up
        """
        cleaned_count = 0
        
        try:
            for reqid, clients in list(self.clients.items()):
                active_clients = []
                for client in clients:
                    try:
                        # Test if client is still connected by checking state
                        if hasattr(client, 'client_state') and client.client_state.value == 3:  # DISCONNECTED
                            logger.debug(f"Removing disconnected WebSocket client from {reqid}")
                            cleaned_count += 1
                        else:
                            active_clients.append(client)
                    except Exception:
                        # If we can't determine state, assume disconnected
                        logger.debug(f"Removing unresponsive WebSocket client from {reqid}")
                        cleaned_count += 1
                        
                if active_clients:
                    self.clients[reqid] = active_clients
                else:
                    del self.clients[reqid]
                    
        except Exception as e:
            logger.error(f"Failed to cleanup disconnected clients: {str(e)}")
            
        return cleaned_count

    def mark_sdk_client_for_removal(self, client: SDKClient):
        """
        Mark an SDK client for removal during next cleanup cycle.
        
        Args:
            client: SDK client to mark for removal
        """
        if client not in self.kill_list:
            self.kill_list.append(client)
            logger.debug(f"Marked SDK client {client.client_id} for removal")

    async def process_kill_list(self) -> int:
        """
        Process the SDK client kill list and remove marked clients.
        
        Returns:
            int: Number of clients removed
        """
        removed_count = 0
        
        try:
            for client in self.kill_list:
                try:
                    if client.client_id in self.sdk_clients:
                        # Close the client connection
                        if not client.is_closing:
                            await client.close()
                        # Remove from tracking
                        del self.sdk_clients[client.client_id]
                        removed_count += 1
                        logger.debug(f"Removed SDK client {client.client_id} from kill list")
                except Exception as e:
                    logger.error(f"Failed to remove SDK client {client.client_id}: {str(e)}")
                    
            self.kill_list.clear()
            
        except Exception as e:
            logger.error(f"Failed to process kill list: {str(e)}")
            
        return removed_count

    # Static Methods for Backward Compatibility
    @staticmethod
    async def add_client_static(clients_dict: Dict[str, List[WebSocket]], reqid: str, websocket: WebSocket):
        """
        Static method to add WebSocket client (for backward compatibility).
        
        Args:
            clients_dict: Clients dictionary to update
            reqid: Request ID for client identification
            websocket: WebSocket connection
        """
        logger.debug(f"Adding WebSocket client for reqid {reqid} (static)")
        if reqid not in clients_dict:
            clients_dict[reqid] = []
        clients_dict[reqid].append(websocket)

    @staticmethod
    async def remove_client_static(clients_dict: Dict[str, List[WebSocket]], reqid: str, websocket: WebSocket):
        """
        Static method to remove WebSocket client (for backward compatibility).
        
        Args:
            clients_dict: Clients dictionary to update
            reqid: Request ID for client identification
            websocket: WebSocket connection
        """
        logger.debug(f"Removing WebSocket client for reqid {reqid} (static)")
        if reqid in clients_dict:
            if websocket in clients_dict[reqid]:
                clients_dict[reqid].remove(websocket)
            if not clients_dict[reqid]:
                del clients_dict[reqid]

    @staticmethod
    async def broadcast_event_static(clients_dict: Dict[str, List[WebSocket]], entity_id: str, data: dict) -> int:
        """
        Static method to broadcast event (for backward compatibility).
        
        Args:
            clients_dict: Clients dictionary
            entity_id: Entity ID for topic filtering
            data: Event data to broadcast
            
        Returns:
            int: Number of clients message was sent to
        """
        sent_count = 0
        topic = f"ws_event_{entity_id}"
        logger.debug(f"Broadcasting event for {entity_id}: {data} (static)")
        
        if topic not in clients_dict:
            logger.debug(f"No active subscribers for topic {topic}")
            return 0
            
        for client in clients_dict[topic]:
            try:
                await client.send_json(data)
                logger.debug(f"Sent event to client on topic {topic}")
                sent_count += 1
            except Exception as e:
                logger.error(f"Failed to send event to client on topic {topic}: {str(e)}")
                
        return sent_count

    # Client Statistics and Information
    def get_client_stats(self) -> dict:
        """
        Get client statistics.
        
        Returns:
            dict: Statistics about connected clients
        """
        websocket_count = sum(len(clients) for clients in self.clients.values())
        
        return {
            'total_websocket_clients': websocket_count,
            'total_sdk_clients': len(self.sdk_clients),
            'websocket_topics': len(self.clients),
            'clients_marked_for_removal': len(self.kill_list),
            'topic_breakdown': {reqid: len(clients) for reqid, clients in self.clients.items()}
        }

    def get_sdk_client_info(self) -> dict:
        """
        Get detailed SDK client information.
        
        Returns:
            dict: Information about SDK clients
        """
        client_info = {}
        
        for client_id, client in self.sdk_clients.items():
            try:
                client_info[client_id] = {
                    'is_closing': getattr(client, 'is_closing', False),
                    'failed_heartbeat': getattr(client, 'failed_heartbeat', False),
                    'heartbeat': getattr(client, 'heartbeat', 0),
                    'zone_id': getattr(client, 'zone_id', None),
                    'tag_count': len(getattr(client, 'tags', [])) if hasattr(client, 'tags') else 0
                }
            except Exception as e:
                client_info[client_id] = {'error': str(e)}
                
        return client_info

    def get_websocket_topics(self) -> List[str]:
        """
        Get list of active WebSocket topics.
        
        Returns:
            List[str]: Active topic names
        """
        return list(self.clients.keys())

    def get_clients_for_topic(self, topic: str) -> List[WebSocket]:
        """
        Get WebSocket clients for a specific topic.
        
        Args:
            topic: Topic name
            
        Returns:
            List[WebSocket]: Clients subscribed to the topic
        """
        return self.clients.get(topic, [])

    # Client Health and Validation
    def validate_client_integrity(self) -> bool:
        """
        Validate the integrity of client tracking.
        
        Returns:
            bool: True if all clients are valid, False otherwise
        """
        try:
            # Check SDK clients
            for client_id, client in self.sdk_clients.items():
                if not hasattr(client, 'client_id'):
                    logger.error(f"SDK client missing client_id: {client_id}")
                    return False
                if not hasattr(client, 'websocket'):
                    logger.error(f"SDK client {client_id} missing websocket")
                    return False
                    
            # Check WebSocket clients
            for reqid, clients in self.clients.items():
                if not isinstance(clients, list):
                    logger.error(f"WebSocket clients for {reqid} is not a list")
                    return False
                for client in clients:
                    if not hasattr(client, 'send_json'):
                        logger.error(f"WebSocket client in {reqid} missing send_json method")
                        return False
                        
            logger.debug("Client integrity validation passed")
            return True
            
        except Exception as e:
            logger.error(f"Client integrity validation failed: {str(e)}")
            return False

    async def shutdown_all_clients(self) -> bool:
        """
        Shutdown all clients gracefully.
        
        Returns:
            bool: True if shutdown completed successfully
        """
        try:
            logger.info("Shutting down all clients...")
            
            # Close all SDK clients
            for client_id, client in list(self.sdk_clients.items()):
                try:
                    if not client.is_closing:
                        await client.close()
                    logger.debug(f"Closed SDK client {client_id}")
                except Exception as e:
                    logger.error(f"Failed to close SDK client {client_id}: {str(e)}")
                    
            self.sdk_clients.clear()
            
            # Close all WebSocket clients
            for reqid, clients in list(self.clients.items()):
                for client in clients:
                    try:
                        if hasattr(client, 'close'):
                            await client.close()
                        logger.debug(f"Closed WebSocket client in {reqid}")
                    except Exception as e:
                        logger.error(f"Failed to close WebSocket client in {reqid}: {str(e)}")
                        
            self.clients.clear()
            self.kill_list.clear()
            
            logger.info("All clients shutdown complete")
            return True
            
        except Exception as e:
            logger.error(f"Failed to shutdown all clients: {str(e)}")
            return False

    # Utility Methods
    def has_clients(self) -> bool:
        """
        Check if there are any active clients.
        
        Returns:
            bool: True if there are active clients
        """
        return len(self.sdk_clients) > 0 or len(self.clients) > 0

    def get_total_client_count(self) -> int:
        """
        Get total number of active clients.
        
        Returns:
            int: Total client count
        """
        websocket_count = sum(len(clients) for clients in self.clients.values())
        return len(self.sdk_clients) + websocket_count

    def clear_topic(self, topic: str) -> int:
        """
        Clear all clients from a specific topic.
        
        Args:
            topic: Topic to clear
            
        Returns:
            int: Number of clients removed
        """
        if topic in self.clients:
            count = len(self.clients[topic])
            del self.clients[topic]
            logger.debug(f"Cleared {count} clients from topic {topic}")
            return count
        return 0

    def subscribe_client_to_topic(self, topic: str, websocket: WebSocket) -> bool:
        """
        Subscribe a WebSocket client to a specific topic.
        
        Args:
            topic: Topic name
            websocket: WebSocket client
            
        Returns:
            bool: True if subscription successful
        """
        try:
            if topic not in self.clients:
                self.clients[topic] = []
            if websocket not in self.clients[topic]:
                self.clients[topic].append(websocket)
                logger.debug(f"Subscribed client to topic {topic}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to subscribe client to topic {topic}: {str(e)}")
            return False

    def unsubscribe_client_from_topic(self, topic: str, websocket: WebSocket) -> bool:
        """
        Unsubscribe a WebSocket client from a specific topic.
        
        Args:
            topic: Topic name
            websocket: WebSocket client
            
        Returns:
            bool: True if unsubscription successful
        """
        try:
            if topic in self.clients and websocket in self.clients[topic]:
                self.clients[topic].remove(websocket)
                if not self.clients[topic]:
                    del self.clients[topic]
                logger.debug(f"Unsubscribed client from topic {topic}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to unsubscribe client from topic {topic}: {str(e)}")
            return False