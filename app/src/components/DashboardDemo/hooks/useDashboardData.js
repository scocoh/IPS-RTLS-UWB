/* Name: useDashboardData.js */
/* Version: 0.1.1 */
/* Created: 250711 */
/* Modified: 250712 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin + Claude */
/* Description: Dashboard data fetching hook for ParcoRTLS with dynamic device categories */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/DashboardDemo/hooks */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

import { useState, useEffect, useCallback } from 'react';
import { dashboardApi } from '../services/dashboardApi';

const useDashboardData = (refreshInterval = 30000, isAutoRefresh = true, customerId = 1) => {
  const [dashboardData, setDashboardData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  const fetchDashboardData = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      const data = await dashboardApi.getOverview(customerId);
      setDashboardData(data);
      setLastUpdated(new Date().toISOString());
    } catch (err) {
      console.error('Dashboard data fetch error:', err);
      setError(err.message || 'Failed to fetch dashboard data');
    } finally {
      setIsLoading(false);
    }
  }, [customerId]);

  const refreshData = useCallback(() => {
    fetchDashboardData();
  }, [fetchDashboardData]);

  // Initial data fetch
  useEffect(() => {
    fetchDashboardData();
  }, [fetchDashboardData]);

  // Auto-refresh interval
  useEffect(() => {
    if (!isAutoRefresh || refreshInterval <= 0) {
      return;
    }

    const interval = setInterval(() => {
      fetchDashboardData();
    }, refreshInterval);

    return () => clearInterval(interval);
  }, [fetchDashboardData, refreshInterval, isAutoRefresh]);

  // Update last_updated in dashboard data if we have it
  const enrichedDashboardData = dashboardData ? {
    ...dashboardData,
    last_updated: lastUpdated || dashboardData.last_updated
  } : null;

  return {
    dashboardData: enrichedDashboardData,
    isLoading,
    error,
    refreshData,
    lastUpdated
  };
};

export default useDashboardData;