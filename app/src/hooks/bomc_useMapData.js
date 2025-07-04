/* Name: bomc_useMapData.js */
/* Version: 0.1.2 */
/* Created: 250701 */
/* Modified: 250704 */
/* Creator: Claude AI */
/* Modified By: Claude AI */
/* Description: Simple map selection using maps API */
/* Location: /home/parcoadmin/parco_fastapi/app/src/hooks */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

import { useState, useEffect } from 'react';

export const useMapData = () => {
    // Dynamic hostname detection for API calls
    const API_BASE_URL = `http://${window.location.hostname || 'localhost'}:8000`;
    
    const [maps, setMaps] = useState([]);
    const [selectedMapId, setSelectedMapId] = useState("");

    useEffect(() => {
        const fetchMaps = async () => {
            try {
                const mapsRes = await fetch(`${API_BASE_URL}/maps/get_maps`);
                const mapsData = await mapsRes.json();
                setMaps(Array.isArray(mapsData) ? mapsData : []);
            } catch (err) {
                console.error("Error fetching maps:", err);
                setMaps([]);
            }
        };
        fetchMaps();
    }, []);

    return {
        maps,
        selectedMapId,
        setSelectedMapId,
        mapId: selectedMapId ? parseInt(selectedMapId) : null
    };
};