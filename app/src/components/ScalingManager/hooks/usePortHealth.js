/* Name: usePortHealth.js */
/* Version: 0.1.0 */
/* Created: 250716 */
/* Modified: 250716 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin + Claude */
/* Description: React hook for port health monitoring integration with manager heartbeat system */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/ScalingManager/hooks */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

import { useState, useEffect, useCallback } from 'react';
import { portHealthAPI } from '../services/portHealthAPI';

export const usePortHealth = (refreshTrigger = 0) => {
    const [portHealth, setPortHealth] = useState(null);
    const [unhealthyPorts, setUnhealthyPorts] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const [lastUpdate, setLastUpdate] = useState(null);

    // Fetch port health status
    const fetchPortHealth = useCallback(async () => {
        setIsLoading(true);
        setError(null);
        
        try {
            console.log('🔍 Fetching port health status...');
            const healthData = await portHealthAPI.getPortHealth();
            
            if (healthData.integration_needed) {
                console.warn('⚠️ Heartbeat integration not available, using fallback mode');
                setPortHealth({
                    status: 'fallback_mode',
                    message: 'Heartbeat integration not available',
                    fallback_mode: true,
                    ports: []
                });
            } else {
                setPortHealth(healthData);
                console.log('✅ Port health data loaded:', healthData);
            }
            
            setLastUpdate(new Date());
        } catch (err) {
            console.error('❌ Error fetching port health:', err);
            setError(err.message);
            // Set fallback data
            setPortHealth({
                status: 'error',
                message: 'Failed to fetch port health',
                fallback_mode: true,
                ports: []
            });
        } finally {
            setIsLoading(false);
        }
    }, []);

    // Fetch unhealthy ports
    const fetchUnhealthyPorts = useCallback(async () => {
        try {
            console.log('🔍 Fetching unhealthy ports...');
            const unhealthyData = await portHealthAPI.getUnhealthyPorts();
            
            if (unhealthyData.integration_needed) {
                console.warn('⚠️ Heartbeat integration not available for unhealthy ports');
                setUnhealthyPorts([]);
            } else {
                setUnhealthyPorts(unhealthyData.unhealthy_ports || []);
                console.log('📋 Unhealthy ports:', unhealthyData.unhealthy_ports?.length || 0);
            }
        } catch (err) {
            console.error('❌ Error fetching unhealthy ports:', err);
            setUnhealthyPorts([]);
        }
    }, []);

    // Manual refresh function
    const refreshPortHealth = useCallback(async () => {
        console.log('🔄 Manual port health refresh triggered');
        
        try {
            const refreshResult = await portHealthAPI.refreshPortHealth();
            console.log('🔄 Refresh result:', refreshResult);
            
            // Fetch updated data after refresh
            await Promise.all([
                fetchPortHealth(),
                fetchUnhealthyPorts()
            ]);
        } catch (err) {
            console.error('❌ Error during manual refresh:', err);
            // Still try to fetch current data
            await Promise.all([
                fetchPortHealth(),
                fetchUnhealthyPorts()
            ]);
        }
    }, [fetchPortHealth, fetchUnhealthyPorts]);

    // Effect to fetch data on mount and refresh trigger
    useEffect(() => {
        console.log('🔄 Port health hook triggered, refreshTrigger:', refreshTrigger);
        
        const fetchData = async () => {
            await Promise.all([
                fetchPortHealth(),
                fetchUnhealthyPorts()
            ]);
        };

        fetchData();
    }, [refreshTrigger, fetchPortHealth, fetchUnhealthyPorts]);

    // Auto-refresh every 30 seconds
    useEffect(() => {
        const interval = setInterval(() => {
            console.log('⏰ Auto-refresh port health (30s interval)');
            fetchPortHealth();
            fetchUnhealthyPorts();
        }, 30000);

        return () => clearInterval(interval);
    }, [fetchPortHealth, fetchUnhealthyPorts]);

    // Helper functions for port health analysis
    const getHealthSummary = useCallback(() => {
        if (!portHealth || portHealth.fallback_mode) {
            return {
                total: 0,
                healthy: 0,
                unhealthy: 0,
                unknown: 0,
                healthPercentage: 0
            };
        }

        const ports = portHealth.ports || [];
        const total = ports.length;
        const unhealthy = unhealthyPorts.length;
        const healthy = total - unhealthy;
        
        return {
            total,
            healthy,
            unhealthy,
            unknown: 0,
            healthPercentage: total > 0 ? Math.round((healthy / total) * 100) : 0
        };
    }, [portHealth, unhealthyPorts]);

    const getPortsByStatus = useCallback(() => {
        if (!portHealth || portHealth.fallback_mode) {
            return {
                healthy: [],
                unhealthy: [],
                unknown: []
            };
        }

        const ports = portHealth.ports || [];
        const unhealthyPortNumbers = unhealthyPorts.map(p => p.port);
        
        return {
            healthy: ports.filter(p => !unhealthyPortNumbers.includes(p.port)),
            unhealthy: unhealthyPorts,
            unknown: []
        };
    }, [portHealth, unhealthyPorts]);

    const isPortHealthy = useCallback((port) => {
        const unhealthyPortNumbers = unhealthyPorts.map(p => p.port);
        return !unhealthyPortNumbers.includes(port);
    }, [unhealthyPorts]);

    return {
        // Data
        portHealth,
        unhealthyPorts,
        
        // State
        isLoading,
        error,
        lastUpdate,
        
        // Actions
        refreshPortHealth,
        
        // Helpers
        getHealthSummary,
        getPortsByStatus,
        isPortHealthy,
        
        // Status
        isIntegrationAvailable: portHealth && !portHealth.fallback_mode,
        isFallbackMode: portHealth && portHealth.fallback_mode
    };
};