// File: /home/parcoadmin/parco_fastapi/app/src/components/DashboardManager/components/ClientConnections.js
/* Name: ClientConnections.js */
/* Version: 0.1.0 */
/* Created: 250713 */
/* Modified: 250713 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin + Claude */
/* Description: Client connections monitoring and management component */

import React, { useState } from 'react';

const ClientConnections = ({ connections, onRefresh }) => {
  const [filterType, setFilterType] = useState('all');
  const [sortBy, setSortBy] = useState('connect_time');
  const [sortOrder, setSortOrder] = useState('desc');

  const handleDisconnectClient = (clientId) => {
    if (window.confirm('Are you sure you want to disconnect this client?')) {
      // TODO: Implement disconnect client logic
      console.log('Disconnecting client:', clientId);
      onRefresh();
    }
  };

  const handleDisconnectAllClients = () => {
    if (window.confirm('Are you sure you want to disconnect ALL clients?')) {
      // TODO: Implement disconnect all clients logic
      console.log('Disconnecting all clients');
      onRefresh();
    }
  };

  const formatDuration = (connectTime) => {
    if (!connectTime) return 'Unknown';
    const now = new Date();
    const connect = new Date(connectTime);
    const durationMs = now - connect;
    const minutes = Math.floor(durationMs / (1000 * 60));
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);

    if (days > 0) return `${days}d ${hours % 24}h`;
    if (hours > 0) return `${hours}h ${minutes % 60}m`;
    return `${minutes}m`;
  };

  const getConnectionStatus = (lastActivity) => {
    if (!lastActivity) return { status: 'unknown', color: 'secondary' };
    const now = new Date();
    const activity = new Date(lastActivity);
    const inactiveMs = now - activity;
    const inactiveMinutes = inactiveMs / (1000 * 60);

    if (inactiveMinutes < 1) return { status: 'active', color: 'success' };
    if (inactiveMinutes < 5) return { status: 'idle', color: 'warning' };
    return { status: 'inactive', color: 'danger' };
  };

  // Mock data if no connections provided
  const mockConnections = [
    {
      client_id: 'dashboard_001',
      client_type: 'Dashboard',
      customer_id: 1,
      ip_address: '192.168.210.100',
      connect_time: new Date(Date.now() - 30 * 60 * 1000),
      last_activity: new Date(Date.now() - 30 * 1000),
      messages_sent: 1250,
      messages_received: 45,
      user_agent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    },
    {
      client_id: 'sdk_002',
      client_type: 'SDK',
      customer_id: null,
      ip_address: '192.168.210.101',
      connect_time: new Date(Date.now() - 120 * 60 * 1000),
      last_activity: new Date(Date.now() - 5 * 1000),
      messages_sent: 8900,
      messages_received: 234,
      user_agent: 'ParcoRTLS-SDK/1.0'
    }
  ];

  const clientData = connections && connections.length > 0 ? connections : mockConnections;

  const filteredClients = clientData.filter(client => {
    if (filterType === 'all') return true;
    if (filterType === 'dashboard') return client.client_type === 'Dashboard';
    if (filterType === 'sdk') return client.client_type === 'SDK';
    if (filterType === 'websocket') return client.client_type === 'WebSocket';
    return true;
  });

  const sortedClients = [...filteredClients].sort((a, b) => {
    let valueA = a[sortBy];
    let valueB = b[sortBy];

    if (sortBy === 'connect_time' || sortBy === 'last_activity') {
      valueA = new Date(valueA);
      valueB = new Date(valueB);
    }

    if (sortOrder === 'asc') {
      return valueA > valueB ? 1 : -1;
    } else {
      return valueA < valueB ? 1 : -1;
    }
  });

  const totalConnections = clientData.length;
  const dashboardConnections = clientData.filter(c => c.client_type === 'Dashboard').length;
  const sdkConnections = clientData.filter(c => c.client_type === 'SDK').length;
  const activeConnections = clientData.filter(c => 
    getConnectionStatus(c.last_activity).status === 'active'
  ).length;

  return (
    <div className="client-connections-container">
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h5>Client Connections</h5>
        <div className="connection-actions">
          <button className="btn btn-danger btn-sm" onClick={handleDisconnectAllClients}>
            Disconnect All
          </button>
          <button className="btn btn-info btn-sm ml-2" onClick={onRefresh}>
            Refresh
          </button>
        </div>
      </div>

      {/* Connection Statistics */}
      <div className="row mb-3">
        <div className="col-md-3">
          <div className="stat-card">
            <div className="stat-value">{totalConnections}</div>
            <div className="stat-label">Total Connections</div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="stat-card">
            <div className="stat-value">{activeConnections}</div>
            <div className="stat-label">Active Connections</div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="stat-card">
            <div className="stat-value">{dashboardConnections}</div>
            <div className="stat-label">Dashboard Clients</div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="stat-card">
            <div className="stat-value">{sdkConnections}</div>
            <div className="stat-label">SDK Clients</div>
          </div>
        </div>
      </div>

      {/* Filters and Sorting */}
      <div className="row mb-3">
        <div className="col-md-6">
          <div className="form-group">
            <label>Filter by Type:</label>
            <select
              className="form-control"
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
            >
              <option value="all">All Clients</option>
              <option value="dashboard">Dashboard Clients</option>
              <option value="sdk">SDK Clients</option>
              <option value="websocket">WebSocket Clients</option>
            </select>
          </div>
        </div>
        <div className="col-md-3">
          <div className="form-group">
            <label>Sort by:</label>
            <select
              className="form-control"
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
            >
              <option value="connect_time">Connect Time</option>
              <option value="last_activity">Last Activity</option>
              <option value="client_id">Client ID</option>
              <option value="client_type">Client Type</option>
              <option value="messages_sent">Messages Sent</option>
            </select>
          </div>
        </div>
        <div className="col-md-3">
          <div className="form-group">
            <label>Order:</label>
            <select
              className="form-control"
              value={sortOrder}
              onChange={(e) => setSortOrder(e.target.value)}
            >
              <option value="desc">Descending</option>
              <option value="asc">Ascending</option>
            </select>
          </div>
        </div>
      </div>

      {/* Client Connections Table */}
      <div className="card">
        <div className="card-body">
          {sortedClients.length > 0 ? (
            <div className="table-responsive">
              <table className="table table-striped">
                <thead>
                  <tr>
                    <th>Client ID</th>
                    <th>Type</th>
                    <th>Status</th>
                    <th>IP Address</th>
                    <th>Customer</th>
                    <th>Connected</th>
                    <th>Last Activity</th>
                    <th>Messages</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {sortedClients.map((client) => {
                    const connectionStatus = getConnectionStatus(client.last_activity);
                    return (
                      <tr key={client.client_id}>
                        <td>
                          <code className="client-id">{client.client_id}</code>
                        </td>
                        <td>
                          <span className={`badge badge-${client.client_type === 'Dashboard' ? 'primary' : 'info'}`}>
                            {client.client_type}
                          </span>
                        </td>
                        <td>
                          <span className={`badge badge-${connectionStatus.color}`}>
                            {connectionStatus.status.toUpperCase()}
                          </span>
                        </td>
                        <td>{client.ip_address}</td>
                        <td>
                          {client.customer_id ? `Customer ${client.customer_id}` : 'N/A'}
                        </td>
                        <td>
                          {formatDuration(client.connect_time)}
                        </td>
                        <td>
                          {new Date(client.last_activity).toLocaleTimeString()}
                        </td>
                        <td>
                          <small>
                            ↑ {client.messages_sent || 0}<br/>
                            ↓ {client.messages_received || 0}
                          </small>
                        </td>
                        <td>
                          <button
                            className="btn btn-danger btn-sm"
                            onClick={() => handleDisconnectClient(client.client_id)}
                          >
                            Disconnect
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center py-4">
              <div className="text-muted">
                <i className="fas fa-users fa-3x mb-3"></i>
                <h5>No Clients Connected</h5>
                <p>No clients are currently connected to the Dashboard Manager.</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Connection Details Modal (placeholder) */}
      <div className="mt-3">
        <small className="text-muted">
          Click on any client to view detailed connection information and message history.
        </small>
      </div>
    </div>
  );
};

export default ClientConnections;