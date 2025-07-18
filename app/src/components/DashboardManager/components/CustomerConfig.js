// File: /home/parcoadmin/parco_fastapi/app/src/components/DashboardManager/components/CustomerConfig.js
/* Name: CustomerConfig.js */
/* Version: 0.1.0 */
/* Created: 250713 */
/* Modified: 250713 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin + Claude */
/* Description: Customer configuration management component */

import React, { useState } from 'react';

const CustomerConfig = ({ customers, onRefresh }) => {
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingCustomer, setEditingCustomer] = useState(null);
  const [newCustomer, setNewCustomer] = useState({
    customer_name: '',
    dashboard_title: '',
    device_categories: []
  });

  const handleAddCustomer = () => {
    // TODO: Implement add customer logic
    console.log('Adding customer:', newCustomer);
    setShowAddForm(false);
    setNewCustomer({ customer_name: '', dashboard_title: '', device_categories: [] });
    onRefresh();
  };

  const handleEditCustomer = (customerId) => {
    setEditingCustomer(customerId);
  };

  const handleSaveEdit = (customerId) => {
    // TODO: Implement save customer logic
    console.log('Saving customer:', customerId);
    setEditingCustomer(null);
    onRefresh();
  };

  const handleDeleteCustomer = (customerId) => {
    if (window.confirm('Are you sure you want to delete this customer?')) {
      // TODO: Implement delete customer logic
      console.log('Deleting customer:', customerId);
      onRefresh();
    }
  };

  if (!customers || Object.keys(customers).length === 0) {
    return (
      <div className="customer-config-container">
        <div className="alert alert-info">
          <h5>No customers configured</h5>
          <p>Dashboard Manager is using default customer configuration.</p>
          <button 
            className="btn btn-primary"
            onClick={() => setShowAddForm(true)}
          >
            Add First Customer
          </button>
        </div>

        {showAddForm && (
          <div className="card mt-3">
            <div className="card-header">
              <h5>Add New Customer</h5>
            </div>
            <div className="card-body">
              <div className="form-group">
                <label>Customer Name:</label>
                <input
                  type="text"
                  className="form-control"
                  value={newCustomer.customer_name}
                  onChange={(e) => setNewCustomer({...newCustomer, customer_name: e.target.value})}
                  placeholder="Enter customer name"
                />
              </div>
              <div className="form-group">
                <label>Dashboard Title:</label>
                <input
                  type="text"
                  className="form-control"
                  value={newCustomer.dashboard_title}
                  onChange={(e) => setNewCustomer({...newCustomer, dashboard_title: e.target.value})}
                  placeholder="Enter dashboard title"
                />
              </div>
              <div className="form-actions">
                <button className="btn btn-success" onClick={handleAddCustomer}>
                  Add Customer
                </button>
                <button 
                  className="btn btn-secondary ml-2" 
                  onClick={() => setShowAddForm(false)}
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="customer-config-container">
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h5>Customer Configuration</h5>
        <button 
          className="btn btn-primary"
          onClick={() => setShowAddForm(true)}
        >
          Add Customer
        </button>
      </div>

      <div className="row">
        {Object.entries(customers).map(([customerId, customerData]) => (
          <div key={customerId} className="col-md-6 col-lg-4 mb-3">
            <div className="card">
              <div className="card-header d-flex justify-content-between align-items-center">
                <h6 className="mb-0">Customer {customerId}</h6>
                <div className="btn-group btn-group-sm">
                  <button 
                    className="btn btn-outline-primary"
                    onClick={() => handleEditCustomer(customerId)}
                  >
                    Edit
                  </button>
                  <button 
                    className="btn btn-outline-danger"
                    onClick={() => handleDeleteCustomer(customerId)}
                  >
                    Delete
                  </button>
                </div>
              </div>
              <div className="card-body">
                <table className="table table-sm table-borderless">
                  <tbody>
                    <tr>
                      <td><strong>Name:</strong></td>
                      <td>{customerData.name || 'Unknown'}</td>
                    </tr>
                    <tr>
                      <td><strong>Status:</strong></td>
                      <td>
                        <span className={`badge badge-${customerData.active ? 'success' : 'secondary'}`}>
                          {customerData.active ? 'Active' : 'Inactive'}
                        </span>
                      </td>
                    </tr>
                    <tr>
                      <td><strong>Messages:</strong></td>
                      <td>{customerData.router_stats?.total_processed || 0}</td>
                    </tr>
                    <tr>
                      <td><strong>Routed:</strong></td>
                      <td>{customerData.router_stats?.total_routed || 0}</td>
                    </tr>
                    <tr>
                      <td><strong>Rate:</strong></td>
                      <td>{customerData.router_stats?.route_rate?.toFixed(2) || 0}%</td>
                    </tr>
                  </tbody>
                </table>

                {customerData.router_stats?.category_counts && (
                  <div className="mt-2">
                    <small className="text-muted">Categories:</small>
                    <div className="category-badges">
                      {Object.entries(customerData.router_stats.category_counts).map(([category, count]) => (
                        <span key={category} className="badge badge-light mr-1 mb-1">
                          {category}: {count}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {showAddForm && (
        <div className="card mt-3">
          <div className="card-header">
            <h5>Add New Customer</h5>
          </div>
          <div className="card-body">
            <div className="form-group">
              <label>Customer Name:</label>
              <input
                type="text"
                className="form-control"
                value={newCustomer.customer_name}
                onChange={(e) => setNewCustomer({...newCustomer, customer_name: e.target.value})}
                placeholder="Enter customer name"
              />
            </div>
            <div className="form-group">
              <label>Dashboard Title:</label>
              <input
                type="text"
                className="form-control"
                value={newCustomer.dashboard_title}
                onChange={(e) => setNewCustomer({...newCustomer, dashboard_title: e.target.value})}
                placeholder="Enter dashboard title"
              />
            </div>
            <div className="form-group">
              <label>Device Categories (comma-separated):</label>
              <input
                type="text"
                className="form-control"
                placeholder="vehicles, assets, staff, equipment"
                onChange={(e) => {
                  const categories = e.target.value.split(',').map(cat => cat.trim()).filter(cat => cat);
                  setNewCustomer({...newCustomer, device_categories: categories});
                }}
              />
              <small className="form-text text-muted">
                Enter device categories separated by commas (e.g., vehicles, assets, staff)
              </small>
            </div>
            <div className="form-actions">
              <button className="btn btn-success" onClick={handleAddCustomer}>
                Add Customer
              </button>
              <button 
                className="btn btn-secondary ml-2" 
                onClick={() => setShowAddForm(false)}
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CustomerConfig;