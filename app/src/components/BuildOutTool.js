// # VERSION 250316 /home/parcoadmin/parco_fastapi/app/src/components/BuildOutTool.js 0P.10B.01
// #  
// # ParcoRTLS Middletier Services, ParcoRTLS DLL, ParcoDatabases, ParcoMessaging, and other code
// # Copyright (C) 1999 - 2025 Affiliated Commercial Services Inc.
// # Invented by Scott Cohen & Bertrand Dugal.
// # Coded by Jesse Chunn O.B.M.'24 and Michael Farnsworth and Others
// # Published at GitHub https://github.com/scocoh/IPS-RTLS-UWB
// #
// # Licensed under AGPL-3.0: https://www.gnu.org/licenses/agpl-3.0.en.html

import React, { useState, useEffect } from "react";
import MapBuildOut from "./MapBuildOut";

const BuildOutTool = () => {
    const [devices, setDevices] = useState([]);
    const [deviceTypes, setDeviceTypes] = useState([]);
    const [zones, setZones] = useState([]);
    const [zoneTypes, setZoneTypes] = useState([]);
    const [maps, setMaps] = useState([]);
    const [deviceId, setDeviceId] = useState("");
    const [deviceName, setDeviceName] = useState("");
    const [deviceType, setDeviceType] = useState("");
    const [zoneType, setZoneType] = useState("");
    const [selectedZone, setSelectedZone] = useState("");
    const [location, setLocation] = useState({ x: null, y: null, z: 0 });
    const [useLeaflet, setUseLeaflet] = useState(false);
    const [editingDevice, setEditingDevice] = useState(null);
    const [newDeviceType, setNewDeviceType] = useState("");

    useEffect(() => {
        const fetchData = async () => {
            try {
                const devicesRes = await fetch("/api/get_all_devices");
                const devicesData = await devicesRes.json();
                setDevices(devicesData);

                const typesRes = await fetch("/api/list_device_types");
                const typesData = await typesRes.json();
                setDeviceTypes(typesData);

                const zonesRes = await fetch("/api/zones_with_maps"); // New endpoint
                const zonesData = await zonesRes.json();
                console.log("Raw zones response:", zonesData);
                const zonesArray = Array.isArray(zonesData) ? zonesData : zonesData.zones || [];
                setZones(zonesArray);

                const zoneTypesRes = await fetch("/zonebuilder/get_zone_types");
                const zoneTypesData = await zoneTypesRes.json();
                setZoneTypes(zoneTypesData || []);

                const mapsRes = await fetch("/zonebuilder/get_maps");
                const mapsData = await mapsRes.json();
                setMaps(mapsData.maps || []);
            } catch (err) {
                console.error("Error fetching initial data:", err);
                setZones([]);
                setZoneTypes([]);
            }
        };
        fetchData();
    }, []);

    const filteredZones = zones.filter(z => !zoneType || z.i_typ_zn === parseInt(zoneType));
    const selectedZoneData = zones.find(z => z.i_zn === parseInt(selectedZone));
    const mapId = selectedZoneData ? selectedZoneData.i_map : null;

    const handleAddDevice = async () => {
        if (!deviceId || !deviceType) {
            alert("Please provide a Device ID and select a Device Type.");
            return;
        }
    
        const formData = new FormData();
        formData.append("device_id", deviceId);
        formData.append("device_type", deviceType);
        formData.append("device_name", deviceName || "New Device");
        if (location.x !== null) formData.append("n_moe_x", location.x);
        if (location.y !== null) formData.append("n_moe_y", location.y);
        formData.append("n_moe_z", location.z);
    
        try {
            const res = await fetch("/api/add_device", { method: "POST", body: formData });
            const result = await res.json();
            if (res.ok) {
                setDevices([...devices, { 
                    x_id_dev: deviceId, 
                    i_typ_dev: parseInt(deviceType), 
                    x_nm_dev: deviceName || "New Device", 
                    n_moe_x: location.x, 
                    n_moe_y: location.y, 
                    n_moe_z: location.z 
                }]);
                resetForm();
            } else {
                alert(`Error: ${result.detail || "Failed to add device"}`);
            }
        } catch (err) {
            console.error("Error adding device:", err);
            alert("Error: Failed to connect to server");
        }
    };

    const handleEditDevice = async () => {
        const formData = new FormData();
        formData.append("device_name", deviceName);
        if (location.x !== null) formData.append("n_moe_x", location.x);
        if (location.y !== null) formData.append("n_moe_y", location.y);
        formData.append("n_moe_z", location.z);

        try {
            const res = await fetch(`/api/edit_device/${editingDevice.x_id_dev}`, { method: "PUT", body: formData });
            const result = await res.json();
            if (res.ok) {
                setDevices(devices.map(d => d.x_id_dev === editingDevice.x_id_dev ? { ...d, x_nm_dev: deviceName, n_moe_x: location.x, n_moe_y: location.y, n_moe_z: location.z } : d));
                resetForm();
            } else {
                alert(`Error: ${result.detail}`);
            }
        } catch (err) {
            console.error("Error editing device:", err);
        }
    };

    const handleDeleteDevice = async (deviceId) => {
        try {
            const res = await fetch(`/api/delete_device/${deviceId}`, { method: "DELETE" });
            const result = await res.json();
            if (res.ok) {
                setDevices(devices.filter(d => d.x_id_dev !== deviceId));
            } else {
                alert(`Error: ${result.detail}`);
            }
        } catch (err) {
            console.error("Error deleting device:", err);
        }
    };

    const handleAddDeviceType = async () => {
        try {
            const res = await fetch("/api/add_device_type", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ description: newDeviceType })
            });
            const result = await res.json();
            if (res.ok) {
                setDeviceTypes([...deviceTypes, { i_typ_dev: result.type_id, x_dsc_dev: newDeviceType }]);
                setNewDeviceType("");
            } else {
                alert(`Error: ${result.detail}`);
            }
        } catch (err) {
            console.error("Error adding device type:", err);
        }
    };

    const handleDeleteDeviceType = async (typeId) => {
        try {
            const res = await fetch(`/api/delete_device_type/${typeId}`, { method: "DELETE" });
            const result = await res.json();
            if (res.ok) {
                setDeviceTypes(deviceTypes.filter(t => t.i_typ_dev !== typeId));
            } else {
                alert(`Error: ${result.detail}`);
            }
        } catch (err) {
            console.error("Error deleting device type:", err);
        }
    };

    const resetForm = () => {
        setDeviceId("");
        setDeviceName("");
        setDeviceType("");
        setZoneType("");
        setSelectedZone("");
        setLocation({ x: null, y: null, z: 0 });
        setEditingDevice(null);
    };

    const handleMapClick = (coords) => {
        setLocation({ x: coords.n_x, y: coords.n_y, z: 0 });
    };

    return (
        <div style={{ padding: "20px" }}>
            <h2>Build Out Tool</h2>

            {/* Add Device Section */}
            <div style={{ marginBottom: "20px" }}>
                <h3>Add/Edit Device</h3>
                <label>Zone Type: </label>
                <select value={zoneType} onChange={(e) => setZoneType(e.target.value)} style={{ marginRight: "10px" }}>
                    <option value="">Select Zone Type</option>
                    {zoneTypes.map(zt => (
                        <option key={zt.zone_level} value={zt.zone_level}>{zt.zone_name}</option>
                    ))}
                </select>
                <label>Zone/Map: </label>
                <select value={selectedZone} onChange={(e) => setSelectedZone(e.target.value)} style={{ marginRight: "10px" }}>
                    <option value="">Select Zone</option>
                    {filteredZones.map(z => (
                        <option key={z.i_zn} value={z.i_zn}>{z.x_nm_zn}</option>
                    ))}
                </select>
                <label>Use Leaflet: </label>
                <input type="checkbox" checked={useLeaflet} onChange={(e) => setUseLeaflet(e.target.checked)} />
                <br />
                <label>Device ID/Serial: </label>
                <input value={deviceId} onChange={(e) => setDeviceId(e.target.value)} disabled={editingDevice !== null} style={{ marginRight: "10px" }} />
                <label>Name: </label>
                <input value={deviceName} onChange={(e) => setDeviceName(e.target.value)} style={{ marginRight: "10px" }} />
                <label>Type: </label>
                <select value={deviceType} onChange={(e) => setDeviceType(e.target.value)} style={{ marginRight: "10px" }}>
                    <option value="">Select Type</option>
                    {deviceTypes.map(t => (
                        <option key={t.i_typ_dev} value={t.i_typ_dev}>{t.x_dsc_dev}</option>
                    ))}
                </select>
                <label>X: </label>
                <input type="number" value={location.x || ""} onChange={(e) => setLocation({ ...location, x: parseFloat(e.target.value) || null })} style={{ width: "60px", marginRight: "10px" }} />
                <label>Y: </label>
                <input type="number" value={location.y || ""} onChange={(e) => setLocation({ ...location, y: parseFloat(e.target.value) || null })} style={{ width: "60px", marginRight: "10px" }} />
                <label>Z: </label>
                <input type="number" value={location.z} onChange={(e) => setLocation({ ...location, z: parseFloat(e.target.value) || 0 })} style={{ width: "60px", marginRight: "10px" }} />
                <button onClick={editingDevice ? handleEditDevice : handleAddDevice} style={{ padding: "5px 10px" }}>
                    {editingDevice ? "Update" : "Add"}
                </button>
                {editingDevice && (
                    <button onClick={resetForm} style={{ padding: "5px 10px", marginLeft: "10px" }}>Cancel</button>
                )}
                {mapId && (
                    <MapBuildOut zoneId={mapId} onDrawComplete={handleMapClick} devices={devices} useLeaflet={useLeaflet} />
                )}
            </div>

            {/* Device Types Section */}
            <div style={{ marginBottom: "20px" }}>
                <h3>Device Types</h3>
                <input value={newDeviceType} onChange={(e) => setNewDeviceType(e.target.value)} placeholder="New Device Type" style={{ marginRight: "10px" }} />
                <button onClick={handleAddDeviceType} style={{ padding: "5px 10px" }}>Add Type</button>
                <ul style={{ listStyle: "none", padding: 0 }}>
                    {deviceTypes.map(t => (
                        <li key={t.i_typ_dev}>
                            {t.x_dsc_dev} (ID: {t.i_typ_dev})
                            <button onClick={() => handleDeleteDeviceType(t.i_typ_dev)} style={{ marginLeft: "10px", padding: "5px" }}>Delete</button>
                        </li>
                    ))}
                </ul>
            </div>

            {/* Devices List */}
            <div>
                <h3>Devices</h3>
                <ul style={{ listStyle: "none", padding: 0 }}>
                    {devices.map(d => (
                        <li key={d.x_id_dev} style={{ marginBottom: "10px" }}>
                            {d.x_id_dev} - {d.x_nm_dev} (Type: {d.i_typ_dev}, Loc: {d.n_moe_x || "N/A"}, {d.n_moe_y || "N/A"}, {d.n_moe_z || "N/A"})
                            <button onClick={() => { setEditingDevice(d); setDeviceId(d.x_id_dev); setDeviceName(d.x_nm_dev); setDeviceType(d.i_typ_dev); setLocation({ x: d.n_moe_x, y: d.n_moe_y, z: d.n_moe_z || 0 }); }} style={{ marginLeft: "10px", padding: "5px" }}>Edit</button>
                            <button onClick={() => handleDeleteDevice(d.x_id_dev)} style={{ marginLeft: "10px", padding: "5px" }}>Delete</button>
                        </li>
                    ))}
                </ul>
            </div>
        </div>
    );
};

export default BuildOutTool;