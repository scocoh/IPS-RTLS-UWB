// File: /home/parcoadmin/parco_fastapi/app/src/components/DashboardManager/hooks/useDataSources.js
/* Name: useDataSources.js */
/* Version: 0.1.0 */
/* Created: 250713 */
/* Modified: 250713 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin + Claude */
/* Description: React hook for data source discovery and management operations */

import { useState, useCallback } from 'react';
import dashboardManagerApi from '../services/dashboardManagerApi';

const useDataSources = () => {
  const [dataSources, setDataSources] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const refreshSources = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);

      // Discover data sources
      const discoveryResponse = await dashboardManagerApi.discoverDataSources();
      setDataSources(discoveryResponse.sources || []);

    } catch (err) {
      console.error('Error fetching data sources:', err);
      setError(err.message || 'Failed to fetch data sources');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const getSourceStatus = useCallback(async (sourceId) => {
    try {
      setError(null);
      const statusResponse = await dashboardManagerApi.getDataSourceStatus(sourceId);
      return statusResponse;
    } catch (err) {
      console.error(`Error getting status for ${sourceId}:`, err);
      setError(err.message || `Failed to get status for ${sourceId}`);
      throw err;
    }
  }, []);

  const checkHealth = useCallback(async (sourceId) => {
    try {
      setError(null);
      const healthResponse = await dashboardManagerApi.checkDataSourceHealth(sourceId);
      return healthResponse;
    } catch (err) {
      console.error(`Error checking health for ${sourceId}:`, err);
      setError(err.message || `Failed to check health for ${sourceId}`);
      throw err;
    }
  }, []);

  const startSource = useCallback(async (sourceId) => {
    try {
      setError(null);
      const startResponse = await dashboardManagerApi.startDataSource(sourceId);
      
      // Refresh sources after starting
      setTimeout(refreshSources, 1000);
      
      return startResponse;
    } catch (err) {
      console.error(`Error starting ${sourceId}:`, err);
      setError(err.message || `Failed to start ${sourceId}`);
      throw err;
    }
  }, [refreshSources]);

  const stopSource = useCallback(async (sourceId) => {
    try {
      setError(null);
      const stopResponse = await dashboardManagerApi.stopDataSource(sourceId);
      
      // Refresh sources after stopping
      setTimeout(refreshSources, 1000);
      
      return stopResponse;
    } catch (err) {
      console.error(`Error stopping ${sourceId}:`, err);
      setError(err.message || `Failed to stop ${sourceId}`);
      throw err;
    }
  }, [refreshSources]);

  const restartSource = useCallback(async (sourceId) => {
    try {
      setError(null);
      const restartResponse = await dashboardManagerApi.restartDataSource(sourceId);
      
      // Refresh sources after restarting
      setTimeout(refreshSources, 2000);
      
      return restartResponse;
    } catch (err) {
      console.error(`Error restarting ${sourceId}:`, err);
      setError(err.message || `Failed to restart ${sourceId}`);
      throw err;
    }
  }, [refreshSources]);

  return {
    // Data
    dataSources,
    isLoading,
    error,

    // Actions
    refreshSources,
    getSourceStatus,
    checkHealth,
    startSource,
    stopSource,
    restartSource
  };
};

export default useDataSources;