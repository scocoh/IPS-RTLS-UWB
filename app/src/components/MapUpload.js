/* Name: MapUpload.js */
/* Version: 0.1.0 */
/* Created: 971201 */
/* Modified: 250502 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin */
/* Description: JavaScript file for ParcoRTLS frontend */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

// # VERSION 250316 /home/parcoadmin/parco_fastapi/app/src/components/MapUpload.js 0P.10B.01
// #  
// # ParcoRTLS Middletier Services, ParcoRTLS DLL, ParcoDatabases, ParcoMessaging, and other code
// # Copyright (C) 1999 - 2025 Affiliated Commercial Services Inc.
// # Invented by Scott Cohen & Bertrand Dugal.
// # Coded by Jesse Chunn O.B.M.'24 and Michael Farnsworth and Others
// # Published at GitHub https://github.com/scocoh/IPS-RTLS-UWB
// #
// # Licensed under AGPL-3.0: https://www.gnu.org/licenses/agpl-3.0.en.html

import React, { useState } from "react";

const MapUpload = () => {
    const [mapName, setMapName] = useState("");
    const [latOrigin, setLatOrigin] = useState("");
    const [lonOrigin, setLonOrigin] = useState("");
    const [minX, setMinX] = useState("");
    const [minY, setMinY] = useState("");
    const [minZ, setMinZ] = useState("");
    const [maxX, setMaxX] = useState("");
    const [maxY, setMaxY] = useState("");
    const [maxZ, setMaxZ] = useState("");
    const [file, setFile] = useState(null);
    const [uploadMessage, setUploadMessage] = useState("");

    const handleFileChange = (event) => {
        setFile(event.target.files[0]);
    };

    const handleSubmit = async (event) => {
        event.preventDefault();
        if (!file) {
            alert("Please select a file to upload.");
            return;
        }

        const formData = new FormData();
        formData.append("name", mapName);
        formData.append("lat_origin", latOrigin);
        formData.append("lon_origin", lonOrigin);
        formData.append("min_x", minX);
        formData.append("min_y", minY);
        formData.append("min_z", minZ);
        formData.append("max_x", maxX);
        formData.append("max_y", maxY);
        formData.append("max_z", maxZ);
        formData.append("file", file);

        try {
            const response = await fetch("/maps/upload_map", {
                method: "POST",
                body: formData,
            });

            const result = await response.json();
            if (response.ok) {
                setUploadMessage(`✅ Success! Map uploaded with ID: ${result.map_id}`);
            } else {
                setUploadMessage(`❌ Upload failed: ${result.detail}`);
            }
        } catch (error) {
            setUploadMessage("❌ Error uploading map.");
            console.error("Upload error:", error);
        }
    };

    return (
        <div style={{ maxWidth: "500px", margin: "auto", padding: "20px", border: "1px solid #ddd", borderRadius: "8px" }}>
            <h2 style={{ textAlign: "center" }}>Upload Map</h2>
            <form onSubmit={handleSubmit} encType="multipart/form-data">
                <div style={{ marginBottom: "10px" }}>
                    <label>Map Name: </label>
                    <input type="text" value={mapName} onChange={(e) => setMapName(e.target.value)} required />
                </div>

                {/* Lat/Lon on the same line */}
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "10px" }}>
                    <div>
                        <label>Latitude Origin: </label>
                        <input type="number" value={latOrigin} onChange={(e) => setLatOrigin(e.target.value)} />
                    </div>
                    <div>
                        <label>Longitude Origin: </label>
                        <input type="number" value={lonOrigin} onChange={(e) => setLonOrigin(e.target.value)} />
                    </div>
                </div>

                {/* Min X, Y, Z on the same line */}
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "10px" }}>
                    <div>
                        <label>Min X: </label>
                        <input type="number" value={minX} onChange={(e) => setMinX(e.target.value)} />
                    </div>
                    <div>
                        <label>Min Y: </label>
                        <input type="number" value={minY} onChange={(e) => setMinY(e.target.value)} />
                    </div>
                    <div>
                        <label>Min Z: </label>
                        <input type="number" value={minZ} onChange={(e) => setMinZ(e.target.value)} />
                    </div>
                </div>

                {/* Max X, Y, Z on the same line */}
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "10px" }}>
                    <div>
                        <label>Max X: </label>
                        <input type="number" value={maxX} onChange={(e) => setMaxX(e.target.value)} />
                    </div>
                    <div>
                        <label>Max Y: </label>
                        <input type="number" value={maxY} onChange={(e) => setMaxY(e.target.value)} />
                    </div>
                    <div>
                        <label>Max Z: </label>
                        <input type="number" value={maxZ} onChange={(e) => setMaxZ(e.target.value)} />
                    </div>
                </div>

                {/* File Upload */}
                <div style={{ marginBottom: "10px" }}>
                    <label>Select Map File (PNG, JPG, GIF): </label>
                    <input type="file" accept=".png,.jpg,.jpeg,.gif" onChange={handleFileChange} required />
                </div>

                {/* Submit Button */}
                <button type="submit" style={{ padding: "10px", width: "100%", fontSize: "16px" }}>Upload Map</button>
            </form>

            {uploadMessage && <p style={{ marginTop: "10px", fontWeight: "bold", textAlign: "center" }}>{uploadMessage}</p>}
        </div>
    );
};

export default MapUpload;
