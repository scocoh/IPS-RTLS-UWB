// File: /home/parcoadmin/parco_fastapi/app/src/components/DashboardManager/hooks/useDashboardManagerData.js
/* Name: useDashboardManagerData.js */
/* Version: 0.1.0 */
/* Created: 250713 */
/* Modified: 250713 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin + Claude */
/* Description: React hook for Dashboard Manager data and operations */

import { useState, useCallback } from 'react';
import dashboardManagerApi from '../services/dashboardManagerApi';

const useDashboardManagerData = () => {
  const [managerStatus, setManagerStatus] = useState(null);
  const [customerStats, setCustomerStats] = useState({});
  const [messageStats, setMessageStats] = useState({});
  const [clientConnections, setClientConnections] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const refreshData = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);

      // Fetch manager status
      const statusResponse = await dashboardManagerApi.getManagerStatus();
      setManagerStatus(statusResponse);

      // Fetch customer statistics
      const customerResponse = await dashboardManagerApi.getCustomerStats();
      setCustomerStats(customerResponse);

      // Fetch message statistics
      const messageResponse = await dashboardManagerApi.getMessageStats();
      setMessageStats(messageResponse);

      // Fetch client connections
      const clientsResponse = await dashboardManagerApi.getClientConnections();
      setClientConnections(clientsResponse);

    } catch (err) {
      console.error('Error fetching dashboard manager data:', err);
      setError(err.message || 'Failed to fetch data');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const startManager = useCallback(async () => {
    try {
      setError(null);
      await dashboardManagerApi.startManager();
      // Refresh data after starting
      setTimeout(refreshData, 1000);
    } catch (err) {
      console.error('Error starting manager:', err);
      setError(err.message || 'Failed to start manager');
    }
  }, [refreshData]);

  const stopManager = useCallback(async () => {
    try {
      setError(null);
      await dashboardManagerApi.stopManager();
      // Refresh data after stopping
      setTimeout(refreshData, 1000);
    } catch (err) {
      console.error('Error stopping manager:', err);
      setError(err.message || 'Failed to stop manager');
    }
  }, [refreshData]);

  const restartManager = useCallback(async () => {
    try {
      setError(null);
      await dashboardManagerApi.restartManager();
      // Refresh data after restarting
      setTimeout(refreshData, 2000);
    } catch (err) {
      console.error('Error restarting manager:', err);
      setError(err.message || 'Failed to restart manager');
    }
  }, [refreshData]);

  const updateCustomerConfig = useCallback(async (customerId, config) => {
    try {
      setError(null);
      await dashboardManagerApi.updateCustomerConfig(customerId, config);
      // Refresh data after updating
      setTimeout(refreshData, 500);
    } catch (err) {
      console.error('Error updating customer config:', err);
      setError(err.message || 'Failed to update customer config');
    }
  }, [refreshData]);

  const addCustomer = useCallback(async (customerData) => {
    try {
      setError(null);
      await dashboardManagerApi.addCustomer(customerData);
      // Refresh data after adding
      setTimeout(refreshData, 500);
    } catch (err) {
      console.error('Error adding customer:', err);
      setError(err.message || 'Failed to add customer');
    }
  }, [refreshData]);

  const removeCustomer = useCallback(async (customerId) => {
    try {
      setError(null);
      await dashboardManagerApi.removeCustomer(customerId);
      // Refresh data after removing
      setTimeout(refreshData, 500);
    } catch (err) {
      console.error('Error removing customer:', err);
      setError(err.message || 'Failed to remove customer');
    }
  }, [refreshData]);

  return {
    // Data
    managerStatus,
    customerStats,
    messageStats,
    clientConnections,
    isLoading,
    error,

    // Actions
    refreshData,
    startManager,
    stopManager,
    restartManager,
    updateCustomerConfig,
    addCustomer,
    removeCustomer
  };
};

export default useDashboardManagerData;