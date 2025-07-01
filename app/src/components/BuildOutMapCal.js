/* Name: BuildOutMapCal.js */
/* Version: 0.1.56 */
/* Created: 971201 */
/* Modified: 250701 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin, TC and Nexus, Claude AI */
/* Description: Pure map cropping tool - using maps API */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

import React, { useState } from "react";
import MapBuildOut from "./MapBuildOut";
import { useMapData } from "../hooks/bomc_useMapData";
import { useCropMode } from "../hooks/bomc_useCropMode";

const BuildOutMapCal = () => {
    const [useLeaflet, setUseLeaflet] = useState(false);
    
    const mapData = useMapData();
    const cropMode = useCropMode();

    const handleMapClick = (coords) => {
        if (cropMode.cropMode) {
            cropMode.handleMapClick(coords);
        }
    };

    const handleCropToggle = (e) => {
        if (e.target.checked) {
            if (!cropMode.enableCropMode(mapData.mapId)) {
                e.target.checked = false;
            }
        } else {
            cropMode.disableCropMode();
        }
    };

    const handleCreateCrop = async () => {
        const success = await cropMode.createCrop(mapData.mapId);
        if (success) {
            window.location.reload();
        }
    };

    return (
        <div style={{ padding: "20px" }}>
            <style>
                {`
                .crop-mode-cursor {
                    cursor: crosshair !important;
                }
                .crop-mode-cursor * {
                    cursor: crosshair !important;
                }
                `}
            </style>

            <h2>Map Crop Tool</h2>

            <div className="card p-4 mb-4">
                <h3>Map Selection</h3>
                
                <div className="row g-3 align-items-end">
                    <div className="col-md-4">
                        <label className="form-label">Select Map</label>
                        <select 
                            className="form-select"
                            value={mapData.selectedMapId} 
                            onChange={(e) => mapData.setSelectedMapId(e.target.value)}
                        >
                            <option value="">Choose Map</option>
                            {mapData.maps.map(map => (
                                <option key={map.i_map} value={map.i_map}>
                                    {map.x_nm_map} (ID: {map.i_map})
                                </option>
                            ))}
                        </select>
                    </div>

                    <div className="col-md-4">
                        <div className="form-check">
                            <input 
                                className="form-check-input" 
                                type="checkbox" 
                                checked={useLeaflet} 
                                onChange={(e) => setUseLeaflet(e.target.checked)} 
                                id="leafletCheck"
                            />
                            <label className="form-check-label" htmlFor="leafletCheck">Use Leaflet</label>
                        </div>
                    </div>

                    <div className="col-md-4">
                        <div className="form-check">
                            <input 
                                className="form-check-input" 
                                type="checkbox" 
                                checked={cropMode.cropMode} 
                                onChange={handleCropToggle} 
                                id="cropCheck"
                            />
                            <label className="form-check-label" htmlFor="cropCheck">
                                <strong>Crop Mode</strong>
                                {cropMode.cropMode && cropMode.cropClicks === 0 && " (Click corner 1)"}
                                {cropMode.cropMode && cropMode.cropClicks === 1 && " (Click corner 2)"}
                                {cropMode.cropMode && cropMode.cropClicks === 2 && " (Ready)"}
                            </label>
                        </div>
                    </div>
                </div>

                {/* CROP UI */}
                {cropMode.cropMode && (
                    <div className="card mt-3" style={{ border: '2px solid #28a745' }}>
                        <div className="card-header bg-success text-white">
                            <h5 className="mb-0">Crop Mode</h5>
                        </div>
                        <div className="card-body">
                            <div className="row">
                                <div className="col-md-6">
                                    <label className="form-label">Crop Name</label>
                                    <input
                                        type="text"
                                        className="form-control"
                                        placeholder="Enter crop name"
                                        value={cropMode.cropName}
                                        onChange={(e) => cropMode.setCropName(e.target.value)}
                                    />
                                </div>
                                <div className="col-md-6">
                                    <label className="form-label">Status</label>
                                    <div className="form-control-plaintext">
                                        {cropMode.cropClicks === 0 && "Click first corner"}
                                        {cropMode.cropClicks === 1 && "Click opposite corner"}
                                        {cropMode.cropClicks === 2 && "Ready to crop"}
                                    </div>
                                </div>
                            </div>
                            
                            {cropMode.cropPreview && (
                                <div className="alert alert-info mt-3">
                                    <strong>Preview:</strong><br/>
                                    Area: ({cropMode.cropPreview.minX.toFixed(1)}, {cropMode.cropPreview.minY.toFixed(1)}) to 
                                    ({cropMode.cropPreview.maxX.toFixed(1)}, {cropMode.cropPreview.maxY.toFixed(1)})<br/>
                                    Size: {cropMode.cropPreview.width.toFixed(1)} × {cropMode.cropPreview.height.toFixed(1)} feet
                                </div>
                            )}

                            {/* COORDINATE CORRECTION */}
                            {cropMode.showCorrection && (
                                <div className="card mt-3" style={{ border: '2px solid #ffc107' }}>
                                    <div className="card-header bg-warning text-dark">
                                        <h6 className="mb-0">Coordinate Options</h6>
                                    </div>
                                    <div className="card-body">
                                        <div className="form-check mb-3">
                                            <input
                                                className="form-check-input"
                                                type="checkbox"
                                                checked={cropMode.usePreviewCoords}
                                                onChange={(e) => cropMode.setUsePreviewCoords(e.target.checked)}
                                                id="usePreviewCheck"
                                            />
                                            <label className="form-check-label" htmlFor="usePreviewCheck">
                                                <strong>Use Preview Coordinates</strong> (for correctly scaled source maps)
                                            </label>
                                        </div>
                                        
                                        {!cropMode.usePreviewCoords && (
                                            <div className="row g-2">
                                                <div className="col-md-2">
                                                    <label className="form-label">Min X</label>
                                                    <input
                                                        type="number"
                                                        step="0.1"
                                                        className="form-control form-control-sm"
                                                        value={cropMode.correctedBounds.min_x}
                                                        onChange={(e) => cropMode.setCorrectedBounds(prev => ({...prev, min_x: parseFloat(e.target.value) || 0}))}
                                                    />
                                                </div>
                                                <div className="col-md-2">
                                                    <label className="form-label">Min Y</label>
                                                    <input
                                                        type="number"
                                                        step="0.1"
                                                        className="form-control form-control-sm"
                                                        value={cropMode.correctedBounds.min_y}
                                                        onChange={(e) => cropMode.setCorrectedBounds(prev => ({...prev, min_y: parseFloat(e.target.value) || 0}))}
                                                    />
                                                </div>
                                                <div className="col-md-2">
                                                    <label className="form-label">Min Z</label>
                                                    <input
                                                        type="number"
                                                        step="0.1"
                                                        className="form-control form-control-sm"
                                                        value={cropMode.correctedBounds.min_z}
                                                        onChange={(e) => cropMode.setCorrectedBounds(prev => ({...prev, min_z: parseFloat(e.target.value) || 0}))}
                                                    />
                                                </div>
                                                <div className="col-md-2">
                                                    <label className="form-label">Max X</label>
                                                    <input
                                                        type="number"
                                                        step="0.1"
                                                        className="form-control form-control-sm"
                                                        value={cropMode.correctedBounds.max_x}
                                                        onChange={(e) => cropMode.setCorrectedBounds(prev => ({...prev, max_x: parseFloat(e.target.value) || 0}))}
                                                    />
                                                </div>
                                                <div className="col-md-2">
                                                    <label className="form-label">Max Y</label>
                                                    <input
                                                        type="number"
                                                        step="0.1"
                                                        className="form-control form-control-sm"
                                                        value={cropMode.correctedBounds.max_y}
                                                        onChange={(e) => cropMode.setCorrectedBounds(prev => ({...prev, max_y: parseFloat(e.target.value) || 0}))}
                                                    />
                                                </div>
                                                <div className="col-md-2">
                                                    <label className="form-label">Max Z</label>
                                                    <input
                                                        type="number"
                                                        step="0.1"
                                                        className="form-control form-control-sm"
                                                        value={cropMode.correctedBounds.max_z}
                                                        onChange={(e) => cropMode.setCorrectedBounds(prev => ({...prev, max_z: parseFloat(e.target.value) || 0}))}
                                                    />
                                                </div>
                                            </div>
                                        )}
                                        
                                        <div className="mt-2">
                                            <small className="text-muted">
                                                {cropMode.usePreviewCoords 
                                                    ? "Will use preview coordinates from correctly scaled source map."
                                                    : "Manual coordinate entry for incorrectly scaled source maps."
                                                }
                                                <br />Lat/Lon will be set to 0.
                                            </small>
                                        </div>
                                    </div>
                                </div>
                            )}
                            
                            <div className="mt-3">
                                <button
                                    onClick={handleCreateCrop}
                                    disabled={cropMode.cropClicks < 2 || !cropMode.cropName.trim()}
                                    className="btn btn-success me-2"
                                >
                                    Create Crop
                                </button>
                                <button
                                    onClick={cropMode.disableCropMode}
                                    className="btn btn-secondary"
                                >
                                    Cancel
                                </button>
                            </div>
                        </div>
                    </div>
                )}

                {/* MAP */}
                {mapData.mapId && (
                    <div className={`mt-4 ${cropMode.cropMode ? 'crop-mode-cursor' : ''}`}>
                        <MapBuildOut 
                            zoneId={mapData.mapId} 
                            selectedZoneId={mapData.selectedMapId}
                            showZoneBoundary={false}
                            onDrawComplete={handleMapClick} 
                            devices={[]} 
                            useLeaflet={useLeaflet} 
                            onDeviceSelect={() => {}} 
                            deploymentMode={false}
                            clickMarker={null}
                            cropMode={cropMode.cropMode}
                            cropBounds={cropMode.cropBounds}
                            cropClicks={cropMode.cropClicks}
                        />
                    </div>
                )}
            </div>
        </div>
    );
};

export default BuildOutMapCal;