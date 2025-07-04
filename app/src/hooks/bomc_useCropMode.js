/* Name: bomc_useCropMode.js */
/* Version: 0.1.2 */
/* Created: 250701 */
/* Modified: 250704 */
/* Creator: Claude AI */
/* Modified By: Claude AI */
/* Description: Pure map cropping with coordinate correction */
/* Location: /home/parcoadmin/parco_fastapi/app/src/hooks */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

import { useState } from 'react';

export const useCropMode = () => {
    // Dynamic hostname detection for API calls
    const API_BASE_URL = `http://${window.location.hostname || 'localhost'}:8000`;
    
    const [cropMode, setCropMode] = useState(false);
    const [cropBounds, setCropBounds] = useState({ min_x: null, min_y: null, max_x: null, max_y: null });
    const [cropName, setCropName] = useState('');
    const [cropClicks, setCropClicks] = useState(0);
    const [cropPreview, setCropPreview] = useState(null);
    
    // Coordinate correction state
    const [showCorrection, setShowCorrection] = useState(false);
    const [usePreviewCoords, setUsePreviewCoords] = useState(false);
    const [correctedBounds, setCorrectedBounds] = useState({
        min_x: 0, min_y: 0, min_z: 0,
        max_x: 100, max_y: 100, max_z: 10
    });

    const enableCropMode = (mapId) => {
        if (!mapId) {
            alert("Please select a map first");
            return false;
        }
        
        setCropMode(true);
        setCropBounds({ min_x: null, min_y: null, max_x: null, max_y: null });
        setCropName('');
        setCropClicks(0);
        setCropPreview(null);
        setShowCorrection(false);
        document.body.classList.add('crop-mode-cursor');
        alert("Click two corners to define crop area");
        return true;
    };

    const disableCropMode = () => {
        setCropMode(false);
        setCropBounds({ min_x: null, min_y: null, max_x: null, max_y: null });
        setCropName('');
        setCropClicks(0);
        setCropPreview(null);
        setShowCorrection(false);
        document.body.classList.remove('crop-mode-cursor');
    };

    const handleMapClick = (coords) => {
        if (cropClicks === 0) {
            setCropBounds(prev => ({ ...prev, min_x: coords.n_x, min_y: coords.n_y }));
            setCropClicks(1);
            alert(`Corner 1 set. Click opposite corner.`);
        } else if (cropClicks === 1) {
            setCropBounds(prev => ({ ...prev, max_x: coords.n_x, max_y: coords.n_y }));
            setCropClicks(2);
            
            const minX = Math.min(cropBounds.min_x, coords.n_x);
            const minY = Math.min(cropBounds.min_y, coords.n_y);
            const maxX = Math.max(cropBounds.min_x, coords.n_x);
            const maxY = Math.max(cropBounds.min_y, coords.n_y);
            const width = maxX - minX;
            const height = maxY - minY;
            
            setCropPreview({ minX, minY, maxX, maxY, width, height });
            
            // Pre-fill corrected bounds with actual clicked coordinates
            setCorrectedBounds({
                min_x: minX,
                min_y: minY,
                min_z: 0,
                max_x: maxX,
                max_y: maxY,
                max_z: 10
            });
            
            setShowCorrection(true);
        }
    };

    const createCrop = async (mapId) => {
        if (!cropBounds.min_x || !cropBounds.max_x || !cropName.trim()) {
            alert('Please complete crop area and enter name');
            return false;
        }
        
        // Use preview coordinates if checkbox is checked
        const finalBounds = usePreviewCoords ? {
            min_x: Math.min(cropBounds.min_x, cropBounds.max_x),
            min_y: Math.min(cropBounds.min_y, cropBounds.max_y),
            min_z: 0,
            max_x: Math.max(cropBounds.min_x, cropBounds.max_x),
            max_y: Math.max(cropBounds.min_y, cropBounds.max_y),
            max_z: 10
        } : correctedBounds;
        
        try {
            const response = await fetch(`${API_BASE_URL}/maps/create_coordinate_crop`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    source_map_id: mapId,
                    crop_name: cropName,
                    min_x: Math.min(cropBounds.min_x, cropBounds.max_x),
                    min_y: Math.min(cropBounds.min_y, cropBounds.max_y),
                    max_x: Math.max(cropBounds.min_x, cropBounds.max_x),
                    max_y: Math.max(cropBounds.min_y, cropBounds.max_y),
                    preserve_source_coordinates: usePreviewCoords
                })
            });
            
            const result = await response.json();
            
            if (response.ok) {
                // Only update coordinates if NOT using preview coordinates
                // Preview coordinates are already correct from the source map
                if (!usePreviewCoords) {
                    const success = await updateMapCoordinates(result.new_map_id, finalBounds);
                    if (success) {
                        alert(`Success! New Map ID: ${result.new_map_id} with corrected coordinates`);
                        disableCropMode();
                        return true;
                    } else {
                        alert(`Crop created (ID: ${result.new_map_id}) but coordinate update failed`);
                        return false;
                    }
                } else {
                    alert(`Success! New Map ID: ${result.new_map_id} with preview coordinates`);
                    disableCropMode();
                    return true;
                }
            } else {
                alert(`Error: ${result.detail}`);
                return false;
            }
        } catch (error) {
            alert('Failed to create crop');
            return false;
        }
    };

    const updateMapCoordinates = async (mapId, bounds = correctedBounds) => {
        try {
            // Use the new simple endpoint with query parameters
            const params = new URLSearchParams({
                min_x: bounds.min_x,
                min_y: bounds.min_y,
                min_z: bounds.min_z,
                max_x: bounds.max_x,
                max_y: bounds.max_y,
                max_z: bounds.max_z,
                lat_origin: 0,
                lon_origin: 0
            });
            
            const response = await fetch(`/maps/update_all_metadata/${mapId}?${params}`, {
                method: 'PUT'
            });
            
            if (response.ok) {
                console.log('Map coordinates updated successfully');
                return true;
            } else {
                const result = await response.json();
                console.error('Update failed:', result);
                return false;
            }
        } catch (error) {
            console.error('Failed to update coordinates:', error);
            return false;
        }
    };

    return {
        cropMode,
        cropBounds,
        cropName,
        cropClicks,
        cropPreview,
        showCorrection,
        usePreviewCoords,
        correctedBounds,
        setCropName,
        setCorrectedBounds,
        setUsePreviewCoords,
        enableCropMode,
        disableCropMode,
        handleMapClick,
        createCrop
    };
};