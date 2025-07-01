/* Name: bomc_useMapData.js */
/* Version: 0.1.1 */
/* Created: 250701 */
/* Modified: 250701 */
/* Creator: Claude AI */
/* Modified By: Claude AI */
/* Description: Simple map selection using maps API */
/* Location: /home/parcoadmin/parco_fastapi/app/src/hooks */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

import { useState, useEffect } from 'react';

export const useMapData = () => {
    const [maps, setMaps] = useState([]);
    const [selectedMapId, setSelectedMapId] = useState("");

    useEffect(() => {
        const fetchMaps = async () => {
            try {
                const mapsRes = await fetch("http://192.168.210.226:8000/maps/get_maps");
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