import React, { useState, useEffect } from "react";

const MapPreview = ({ mapId, onClose }) => {
    const [imageSrc, setImageSrc] = useState(null);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchMapImage();
    }, [mapId]);

    const fetchMapImage = async () => {
        try {
            const response = await fetch(`/maps/map_image/${mapId}`);
            if (!response.ok) throw new Error("Failed to load map image");

            const blob = await response.blob();
            const url = URL.createObjectURL(blob);
            setImageSrc(url);
        } catch (err) {
            setError(err.message);
        }
    };

    return (
        <div style={{
            position: "fixed", top: 0, left: 0, width: "100%", height: "100%",
            backgroundColor: "rgba(0,0,0,0.8)", display: "flex", justifyContent: "center", alignItems: "center"
        }}>
            <div style={{
                background: "white", padding: "20px", borderRadius: "8px", textAlign: "center"
            }}>
                <h3>Map Preview</h3>
                {error ? <p style={{ color: "red" }}>❌ {error}</p> : (
                    imageSrc ? <img src={imageSrc} alt="Map Preview" style={{ maxWidth: "500px", maxHeight: "500px" }} /> : <p>Loading...</p>
                )}
                <br />
                <button onClick={onClose} style={{ padding: "10px", marginTop: "10px", background: "red", color: "white", border: "none", cursor: "pointer" }}>Close</button>
            </div>
        </div>
    );
};

export default MapPreview;
