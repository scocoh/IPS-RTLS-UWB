/* Name: useScalingAPI.js */
/* Version: 0.1.0 */
/* Created: 250716 */
/* Modified: 250716 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin + Claude */
/* Description: React hook for scaling operations API integration */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/ScalingManager/hooks */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

import { useState, useEffect, useCallback } from 'react';
import { scalingAPI } from '../services/scalingAPI';

export const useScalingAPI = (refreshTrigger = 0) => {
    const [scalingStatus, setScalingStatus] = useState(null);
    const [scalingCandidates, setScalingCandidates] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const [lastOperation, setLastOperation] = useState(null);

    // Fetch scaling status
    const fetchScalingStatus = useCallback(async () => {
        try {
            console.log('🔍 Fetching scaling status...');
            const statusData = await scalingAPI.getScalingStatus();
            setScalingStatus(statusData);
            console.log('✅ Scaling status loaded:', statusData);
        } catch (err) {
            console.error('❌ Error fetching scaling status:', err);
            setError(err.message);
            setScalingStatus({
                port_health: { status: 'error' },
                scaling_candidates: [],
                available_scaling_ports: [],
                active_scaling_ports: [],
                scaling_status: {
                    total_scaling_candidates: 0,
                    available_slots: 0,
                    active_scaling_instances: 0
                }
            });
        }
    }, []);

    // Fetch scaling candidates
    const fetchScalingCandidates = useCallback(async () => {
        try {
            console.log('🔍 Fetching scaling candidates...');
            const candidatesData = await scalingAPI.getScalingCandidates();
            setScalingCandidates(candidatesData.scaling_candidates || []);
            console.log('✅ Scaling candidates loaded:', candidatesData.scaling_candidates?.length || 0);
        } catch (err) {
            console.error('❌ Error fetching scaling candidates:', err);
            setScalingCandidates([]);
        }
    }, []);

    // Create scaling port
    const createPort = useCallback(async (port) => {
        setIsLoading(true);
        setError(null);
        
        try {
            console.log(`🚀 Creating scaling port ${port}...`);
            const result = await scalingAPI.createScalingPort(port);
            
            setLastOperation({
                type: 'create',
                port,
                success: true,
                message: result.message,
                timestamp: new Date()
            });
            
            console.log('✅ Port created successfully:', result);
            
            // Refresh data after successful creation
            await Promise.all([
                fetchScalingStatus(),
                fetchScalingCandidates()
            ]);
            
            return { success: true, data: result };
        } catch (err) {
            console.error(`❌ Error creating port ${port}:`, err);
            
            setLastOperation({
                type: 'create',
                port,
                success: false,
                message: err.message,
                timestamp: new Date()
            });
            
            setError(`Failed to create port ${port}: ${err.message}`);
            return { success: false, error: err.message };
        } finally {
            setIsLoading(false);
        }
    }, [fetchScalingStatus, fetchScalingCandidates]);

    // Remove scaling port
    const removePort = useCallback(async (port) => {
        setIsLoading(true);
        setError(null);
        
        try {
            console.log(`🗑️ Removing scaling port ${port}...`);
            const result = await scalingAPI.removeScalingPort(port);
            
            setLastOperation({
                type: 'remove',
                port,
                success: true,
                message: result.message,
                timestamp: new Date()
            });
            
            console.log('✅ Port removed successfully:', result);
            
            // Refresh data after successful removal
            await Promise.all([
                fetchScalingStatus(),
                fetchScalingCandidates()
            ]);
            
            return { success: true, data: result };
        } catch (err) {
            console.error(`❌ Error removing port ${port}:`, err);
            
            setLastOperation({
                type: 'remove',
                port,
                success: false,
                message: err.message,
                timestamp: new Date()
            });
            
            setError(`Failed to remove port ${port}: ${err.message}`);
            return { success: false, error: err.message };
        } finally {
            setIsLoading(false);
        }
    }, [fetchScalingStatus, fetchScalingCandidates]);

    // Get next available port
    const getNextPort = useCallback(async (basePort) => {
        try {
            console.log(`🔍 Getting next available port for base ${basePort}...`);
            const result = await scalingAPI.getNextScalingPort(basePort);
            console.log('✅ Next port result:', result);
            return result;
        } catch (err) {
            console.error(`❌ Error getting next port for ${basePort}:`, err);
            throw err;
        }
    }, []);

    // Batch create multiple ports
    const createMultiplePorts = useCallback(async (basePort, count) => {
        const results = [];
        setIsLoading(true);
        
        try {
            for (let i = 0; i < count; i++) {
                const nextPortResult = await getNextPort(basePort);
                const nextPort = nextPortResult.next_available_port;
                
                const createResult = await createPort(nextPort);
                results.push({
                    port: nextPort,
                    ...createResult
                });
                
                // Small delay between creations
                await new Promise(resolve => setTimeout(resolve, 500));
            }
            
            return {
                success: true,
                results,
                created: results.filter(r => r.success).length,
                failed: results.filter(r => !r.success).length
            };
        } catch (err) {
            console.error('❌ Error in batch port creation:', err);
            return {
                success: false,
                error: err.message,
                results
            };
        } finally {
            setIsLoading(false);
        }
    }, [getNextPort, createPort]);

    // Effect to fetch data on mount and refresh trigger
    useEffect(() => {
        console.log('🔄 Scaling API hook triggered, refreshTrigger:', refreshTrigger);
        
        const fetchData = async () => {
            setIsLoading(true);
            await Promise.all([
                fetchScalingStatus(),
                fetchScalingCandidates()
            ]);
            setIsLoading(false);
        };

        fetchData();
    }, [refreshTrigger, fetchScalingStatus, fetchScalingCandidates]);

    // Helper functions
    const getAvailablePortsCount = useCallback(() => {
        return scalingStatus?.available_scaling_ports?.length || 0;
    }, [scalingStatus]);

    const getActivePortsCount = useCallback(() => {
        return scalingStatus?.active_scaling_ports?.length || 0;
    }, [scalingStatus]);

    const getCandidatesCount = useCallback(() => {
        return scalingCandidates.length;
    }, [scalingCandidates]);

    const getScalingCapacity = useCallback(() => {
        const available = getAvailablePortsCount();
        const active = getActivePortsCount();
        const total = available + active;
        
        return {
            available,
            active,
            total,
            utilizationPercentage: total > 0 ? Math.round((active / total) * 100) : 0
        };
    }, [getAvailablePortsCount, getActivePortsCount]);

    const isPortInUse = useCallback((port) => {
        return scalingStatus?.active_scaling_ports?.includes(port) || false;
    }, [scalingStatus]);

    const canCreatePort = useCallback(() => {
        return getAvailablePortsCount() > 0 && !isLoading;
    }, [getAvailablePortsCount, isLoading]);

    return {
        // Data
        scalingStatus,
        scalingCandidates,
        lastOperation,
        
        // State
        isLoading,
        error,
        
        // Actions
        createPort,
        removePort,
        getNextPort,
        createMultiplePorts,
        
        // Helpers
        getAvailablePortsCount,
        getActivePortsCount,
        getCandidatesCount,
        getScalingCapacity,
        isPortInUse,
        canCreatePort
    };
};