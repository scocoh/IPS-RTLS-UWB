// # VERSION 250320 /home/parcoadmin/parco_fastapi/app/src/components/BuildOutTool.js 0P.10B.33
// # --- CHANGED: Bumped version from 0P.10B.32 to 0P.10B.33 to fix crash when all devices are deleted (ensure devices and filteredDevices are always arrays)
// # 
// # ParcoRTLS Middletier Services, ParcoRTLS DLL, ParcoDatabases, ParcoMessaging, and other code
// # Copyright (C) 1999 - 2025 Affiliated Commercial Services Inc.
// # Invented by Scott Cohen & Bertrand Dugal.
// # Coded by Jesse Chunn O.B.M.'24 and Michael Farnsworth and Others
// # Published at GitHub https://github.com/scocoh/IPS-RTLS-UWB
// #
// # Licensed under AGPL-3.0: https://www.gnu.org/licenses/agpl-3.0.en.html

import React, { useState, useEffect, useRef } from "react";
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
    const [estimatingMode, setEstimatingMode] = useState(false);
    const [startingDeviceId, setStartingDeviceId] = useState("");
    const [currentDeviceId, setCurrentDeviceId] = useState(null);
    const addEditSectionRef = useRef(null);
    const [displayLocation, setDisplayLocation] = useState({ x: "", y: "", z: "" });
    const [locationErrors, setLocationErrors] = useState({ x: false, y: false, z: false });
    const [deploymentMode, setDeploymentMode] = useState(false);
    const [clickMarker, setClickMarker] = useState(null);
    const [activeTab, setActiveTab] = useState("addEditDevice");

    useEffect(() => {
        const fetchData = async () => {
            try {
                const devicesRes = await fetch("/api/get_all_devices");
                const devicesData = await devicesRes.json();
                console.log("Raw devices response:", JSON.stringify(devicesData, null, 2));
                // Ensure devicesData is an array; fallback to [] if not
                setDevices(Array.isArray(devicesData) ? devicesData : []);

                const typesRes = await fetch("/api/list_device_types");
                const typesData = await typesRes.json();
                setDeviceTypes(typesData);

                const zonesRes = await fetch("/api/zones_with_maps");
                const zonesData = await zonesRes.json();
                console.log("Raw zones response:", JSON.stringify(zonesData, null, 2));
                const zonesArray = Array.isArray(zonesData) ? zonesData : zonesData.zones || [];
                console.log("Processed zones array:", zonesArray.map(z => ({ i_zn: z.i_zn, x_nm_zn: z.x_nm_zn })));
                setZones(zonesArray);

                const zoneTypesRes = await fetch("/zonebuilder/get_zone_types");
                const zoneTypesData = await zoneTypesRes.json();
                setZoneTypes(zoneTypesData || []);

                const mapsRes = await fetch("/zonebuilder/get_maps");
                const mapsData = await mapsRes.json();
                setMaps(mapsData.maps || []);
            } catch (err) {
                console.error("Error fetching initial data:", err);
                setDevices([]); // Fallback to empty array on error
                setZones([]);
                setZoneTypes([]);
            }
        };
        fetchData();
    }, []);

    const filteredZones = zones.filter(z => !zoneType || z.i_typ_zn === parseInt(zoneType));
    const selectedZoneData = zones.find(z => z.i_zn === parseInt(selectedZone));
    const mapId = selectedZoneData ? selectedZoneData.i_map : null;

    const getZoneHierarchy = (zoneId, zones) => {
        const hierarchy = new Set([parseInt(zoneId)]);
        const addChildren = (parentId) => {
            zones.forEach(z => {
                if (z.i_pnt_zn === parentId) {
                    hierarchy.add(z.i_zn);
                    addChildren(z.i_zn);
                }
            });
        };
        addChildren(parseInt(zoneId));
        console.log("Zone hierarchy for", zoneId, ":", Array.from(hierarchy));
        return hierarchy;
    };

    const filteredDevices = selectedZone
        ? devices.filter(d => {
            const hierarchy = getZoneHierarchy(selectedZone, zones);
            const deviceZoneId = d.zone_id !== undefined ? parseInt(d.zone_id) : null;
            console.log("Filtering device:", d.x_id_dev, "zone_id:", d.zone_id, "parsed:", deviceZoneId, "in hierarchy:", hierarchy.has(deviceZoneId));
            return deviceZoneId !== null && hierarchy.has(deviceZoneId);
        })
        : devices;

    const handleAddDevice = async () => {
        if (!deviceId || !deviceType) {
            alert("Please provide a Device ID and select a Device Type.");
            return;
        }
        if (!selectedZone) {
            alert("Please select a Zone.");
            return;
        }
        if (locationErrors.x || locationErrors.y || locationErrors.z) {
            alert("Please correct the invalid location coordinates before adding the device.");
            return;
        }

        try {
            const res = await fetch(`/api/check_device_id/${deviceId}`);
            const result = await res.json();
            if (result.exists) {
                alert(`Device ID ${deviceId} already exists in the database. Please use a different ID.`);
                return;
            }
        } catch (err) {
            console.error("Error checking device ID:", err);
            alert("Error checking device ID. Please try again.");
            return;
        }

        const formData = new FormData();
        formData.append("device_id", deviceId);
        formData.append("device_type", deviceType);
        formData.append("device_name", deviceName || "New Device");
        if (location.x !== null) formData.append("n_moe_x", Number(location.x).toFixed(6));
        if (location.y !== null) formData.append("n_moe_y", Number(location.y).toFixed(6));
        const zValue = estimatingMode ? 10.0 : location.z;
        formData.append("n_moe_z", Number(zValue).toFixed(6));
        formData.append("zone_id", selectedZone);

        console.log("Adding device with data:", {
            device_id: deviceId,
            device_type: deviceType,
            device_name: deviceName || "New Device",
            n_moe_x: location.x !== null ? Number(location.x).toFixed(6) : null,
            n_moe_y: location.y !== null ? Number(location.y).toFixed(6) : null,
            n_moe_z: Number(zValue).toFixed(6),
            zone_id: selectedZone
        });

        try {
            const res = await fetch("/api/add_device", { method: "POST", body: formData });
            const result = await res.json();
            if (res.ok) {
                setDevices([...devices, { 
                    x_id_dev: deviceId, 
                    i_typ_dev: parseInt(deviceType), 
                    x_nm_dev: deviceName || "New Device", 
                    n_moe_x: location.x !== null ? Number(location.x).toFixed(6) : null, 
                    n_moe_y: location.y !== null ? Number(location.y).toFixed(6) : null, 
                    n_moe_z: Number(zValue).toFixed(6),
                    zone_id: parseInt(selectedZone)
                }]);
                if (estimatingMode) {
                    const nextId = parseInt(deviceId) + 1;
                    setDeviceId(nextId.toString());
                    setDeviceName(nextId.toString());
                    setCurrentDeviceId(nextId);
                    setClickMarker(null);
                } else {
                    resetForm();
                }
            } else {
                alert(`Error: ${result.detail || "Failed to add device"}`);
            }
        } catch (err) {
            console.error("Error adding device:", err);
            alert("Error: Failed to connect to server");
        }
    };

    const handleEditDevice = async () => {
        if (!selectedZone) {
            alert("Please select a Zone.");
            return;
        }
        if (locationErrors.x || locationErrors.y || locationErrors.z) {
            alert("Please correct the invalid location coordinates before updating the device.");
            return;
        }

        if (deviceId !== editingDevice.x_id_dev) {
            try {
                const res = await fetch(`/api/check_device_id/${deviceId}`);
                const result = await res.json();
                if (result.exists) {
                    alert(`Device ID ${deviceId} already exists in the database. Please use a different ID.`);
                    return;
                }
            } catch (err) {
                console.error("Error checking device ID:", err);
                alert("Error checking device ID. Please try again.");
                return;
            }
        }

        console.log("Editing device with deviceType:", deviceType, "typeof deviceType:", typeof deviceType);

        const deviceTypeValue = deviceType && deviceType !== "" ? parseInt(deviceType) : null;
        if (deviceTypeValue === null) {
            console.warn("deviceType is empty or invalid, sending null to backend");
        }

        const formData = new FormData();
        formData.append("new_device_id", deviceId);
        if (deviceTypeValue !== null) {
            formData.append("device_type", deviceTypeValue);
        }
        formData.append("device_name", deviceName);
        if (location.x !== null) formData.append("n_moe_x", Number(location.x).toFixed(6));
        if (location.y !== null) formData.append("n_moe_y", Number(location.y).toFixed(6));
        const zValue = estimatingMode ? 10.0 : location.z;
        formData.append("n_moe_z", Number(zValue).toFixed(6));
        formData.append("zone_id", selectedZone);

        try {
            const res = await fetch(`/api/edit_device/${editingDevice.x_id_dev}`, { method: "PUT", body: formData });
            const result = await res.json();
            if (res.ok) {
                setDevices(devices.map(d => d.x_id_dev === editingDevice.x_id_dev ? { 
                    ...d, 
                    x_id_dev: deviceId,
                    i_typ_dev: deviceTypeValue !== null ? deviceTypeValue : d.i_typ_dev,
                    x_nm_dev: deviceName, 
                    n_moe_x: location.x !== null ? Number(location.x).toFixed(6) : null, 
                    n_moe_y: location.y !== null ? Number(location.y).toFixed(6) : null, 
                    n_moe_z: Number(zValue).toFixed(6),
                    zone_id: parseInt(selectedZone)
                } : d));
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
        setLocation({ x: null, y: null, z: estimatingMode ? 10.0 : 0 });
        setDisplayLocation({ x: "", y: "", z: "" });
        setLocationErrors({ x: false, y: false, z: false });
        setEditingDevice(null);
        setClickMarker(null);
    };

    const handleMapClick = (coords) => {
        const newLocation = { x: coords.n_x, y: coords.n_y, z: estimatingMode ? 10.0 : 0 };
        setLocation(newLocation);
        setDisplayLocation({
            x: newLocation.x != null ? newLocation.x.toString() : "",
            y: newLocation.y != null ? newLocation.y.toString() : "",
            z: newLocation.z != null ? newLocation.z.toString() : ""
        });
        setLocationErrors({ x: false, y: false, z: false });
        setClickMarker({ x: coords.n_x, y: coords.n_y });
    };

    const handleEstimatingModeToggle = (e) => {
        const isEnabled = e.target.checked;
        setEstimatingMode(isEnabled);
        if (isEnabled) {
            setDeploymentMode(false);
            const startId = parseInt(startingDeviceId) || 0;
            setCurrentDeviceId(startId);
            setDeviceId(startId.toString());
            setDeviceName(startId.toString());
            setLocation({ ...location, z: 10.0 });
            setDisplayLocation({ ...displayLocation, z: "10.0" });
            setLocationErrors({ ...locationErrors, z: false });
        } else {
            setDeviceId("");
            setDeviceName("");
            setStartingDeviceId("");
            setCurrentDeviceId(null);
            setLocation({ ...location, z: 0 });
            setDisplayLocation({ ...displayLocation, z: "" });
            setLocationErrors({ ...locationErrors, z: false });
            setClickMarker(null);
        }
    };

    const handleDeploymentModeToggle = (e) => {
        const isEnabled = e.target.checked;
        setDeploymentMode(isEnabled);
        if (isEnabled) {
            setUseLeaflet(true);
            setEstimatingMode(false);
            setDeviceId("");
            setDeviceName("");
            setStartingDeviceId("");
            setCurrentDeviceId(null);
            setLocation({ ...location, z: 0 });
            setDisplayLocation({ ...displayLocation, z: "" });
            setLocationErrors({ ...locationErrors, z: false });
            setClickMarker(null);
        }
    };

    const handleLocationChange = (field, value) => {
        setDisplayLocation({ ...displayLocation, [field]: value });

        const regex = /^-?\d*\.?\d*$/;
        if (value === "" || regex.test(value)) {
            const parsedValue = value === "" ? null : parseFloat(value);
            setLocation({ ...location, [field]: parsedValue });
            setLocationErrors({ ...locationErrors, [field]: false });
            if (field === "x" || field === "y") {
                setClickMarker({ x: field === "x" ? parsedValue : location.x, y: field === "y" ? parsedValue : location.y });
            }
        } else {
            setLocationErrors({ ...locationErrors, [field]: true });
        }
    };

    const handleLocationBlur = (field) => {
        const value = displayLocation[field];
        if (value !== "" && !isNaN(parseFloat(value))) {
            const formattedValue = parseFloat(value).toFixed(6);
            setDisplayLocation({ ...displayLocation, [field]: formattedValue });
            setLocation({ ...location, [field]: parseFloat(formattedValue) });
            setLocationErrors({ ...locationErrors, [field]: false });
        } else if (value === "") {
            setLocation({ ...location, [field]: null });
            setLocationErrors({ ...locationErrors, [field]: false });
            if (field === "x" || field === "y") {
                setClickMarker(null);
            }
        } else {
            setLocationErrors({ ...locationErrors, [field]: true });
        }
    };

    const handleDeviceSelect = (device) => {
        setEditingDevice(device);
        setDeviceId(device.x_id_dev);
        setDeviceName(device.x_nm_dev);
        setDeviceType(String(device.i_typ_dev));
        const newLocation = { x: device.n_moe_x, y: device.n_moe_y, z: device.n_moe_z || 0 };
        setLocation(newLocation);
        setDisplayLocation({
            x: newLocation.x != null ? newLocation.x.toString() : "",
            y: newLocation.y != null ? newLocation.y.toString() : "",
            z: newLocation.z != null ? newLocation.z.toString() : ""
        });
        setLocationErrors({ x: false, y: false, z: false });
        setSelectedZone(String(device.zone_id || ""));
        setClickMarker(null);
        addEditSectionRef.current.scrollIntoView({ behavior: "smooth" });
    };

    return (
        <div style={{ padding: "20px" }}>
            <h2>Build Out Tool</h2>

            {/* Tab Navigation */}
            <div className="mb-4">
                <ul className="nav nav-tabs">
                    <li className="nav-item">
                        <button
                            className={`nav-link ${activeTab === "addEditDevice" ? "active" : ""}`}
                            onClick={() => setActiveTab("addEditDevice")}
                        >
                            Add/Edit Device
                        </button>
                    </li>
                    <li className="nav-item">
                        <button
                            className={`nav-link ${activeTab === "deviceTypes" ? "active" : ""}`}
                            onClick={() => setActiveTab("deviceTypes")}
                        >
                            Device Types
                        </button>
                    </li>
                </ul>
            </div>

            {/* Tab Content */}
            {activeTab === "addEditDevice" && (
                <div>
                    <div ref={addEditSectionRef} className="card p-4 mb-4 shadow-sm">
                        <h3 className="mb-3">Add/Edit Device</h3>

                        <div className="row g-3 align-items-end">
                            <div className="col-md-4">
                                <label className="form-label">Zone Type</label>
                                <select 
                                    className="form-select"
                                    value={zoneType} 
                                    onChange={(e) => setZoneType(e.target.value)} 
                                    disabled={estimatingMode}
                                >
                                    <option value="">Select Zone Type</option>
                                    {zoneTypes.map(zt => (
                                        <option key={zt.zone_level} value={zt.zone_level}>{zt.zone_name}</option>
                                    ))}
                                </select>
                            </div>

                            <div className="col-md-4">
                                <label className="form-label">Zone/Map</label>
                                <select 
                                    className="form-select"
                                    value={selectedZone} 
                                    onChange={(e) => setSelectedZone(e.target.value)} 
                                    disabled={estimatingMode}
                                >
                                    <option value="">Select Zone</option>
                                    {filteredZones.map(z => (
                                        <option key={z.i_zn} value={z.i_zn}>{z.x_nm_zn}</option>
                                    ))}
                                </select>
                            </div>

                            <div className="col-md-4">
                                <div className="form-check form-check-inline">
                                    <input className="form-check-input" type="checkbox" checked={useLeaflet} onChange={(e) => setUseLeaflet(e.target.checked)} id="leafletCheck" />
                                    <label className="form-check-label" htmlFor="leafletCheck">Use Leaflet</label>
                                </div>
                                <div className="form-check form-check-inline">
                                    <input className="form-check-input" type="checkbox" checked={estimatingMode} onChange={handleEstimatingModeToggle} id="estimatingCheck" />
                                    <label className="form-check-label" htmlFor="estimatingCheck">Estimating</label>
                                </div>
                                <div className="form-check form-check-inline">
                                    <input className="form-check-input" type="checkbox" checked={deploymentMode} onChange={handleDeploymentModeToggle} id="deploymentCheck" />
                                    <label className="form-check-label" htmlFor="deploymentCheck">Deploy</label>
                                </div>
                            </div>
                        </div>

                        {estimatingMode && (
                            <div className="row mt-3">
                                <div className="col-md-4">
                                    <label className="form-label">Starting Device ID</label>
                                    <input
                                        type="number"
                                        className="form-control"
                                        value={startingDeviceId}
                                        onChange={(e) => {
                                            const value = e.target.value;
                                            setStartingDeviceId(value);
                                            const startId = parseInt(value) || 0;
                                            setCurrentDeviceId(startId);
                                            setDeviceId(startId.toString());
                                            setDeviceName(startId.toString());
                                        }}
                                    />
                                </div>
                            </div>
                        )}

                        <div className="row g-3 mt-3">
                            <div className="col-md-3">
                                <label className="form-label">Device ID/Serial</label>
                                <input 
                                    className="form-control"
                                    value={deviceId} 
                                    onChange={(e) => {
                                        setDeviceId(e.target.value);
                                        if (estimatingMode) setDeviceName(e.target.value);
                                    }} 
                                    disabled={editingDevice !== null && !deploymentMode}
                                />
                            </div>

                            <div className="col-md-3">
                                <label className="form-label">Name</label>
                                <input 
                                    className="form-control"
                                    value={deviceName} 
                                    onChange={(e) => setDeviceName(e.target.value)} 
                                    disabled={estimatingMode}
                                />
                            </div>

                            <div className="col-md-3">
                                <label className="form-label">Type</label>
                                <select 
                                    className="form-select"
                                    value={deviceType} 
                                    onChange={(e) => setDeviceType(e.target.value)}
                                >
                                    <option value="">Select Type</option>
                                    {deviceTypes.map(t => (
                                        <option key={t.i_typ_dev} value={t.i_typ_dev}>{t.x_dsc_dev}</option>
                                    ))}
                                </select>
                            </div>
                        </div>

                        <div className="row g-3 mt-3">
                            <div className="col-md-2">
                                <label className="form-label">X</label>
                                <input 
                                    className={`form-control ${locationErrors.x ? 'is-invalid' : ''}`}
                                    type="text" 
                                    inputMode="decimal"
                                    pattern="^-?\\d*\\.?\\d*$"
                                    value={displayLocation.x}
                                    onChange={(e) => handleLocationChange("x", e.target.value)}
                                    onBlur={() => handleLocationBlur("x")}
                                />
                            </div>

                            <div className="col-md-2">
                                <label className="form-label">Y</label>
                                <input 
                                    className={`form-control ${locationErrors.y ? 'is-invalid' : ''}`}
                                    type="text" 
                                    inputMode="decimal"
                                    pattern="^-?\\d*\\.?\\d*$"
                                    value={displayLocation.y}
                                    onChange={(e) => handleLocationChange("y", e.target.value)}
                                    onBlur={() => handleLocationBlur("y")}
                                />
                            </div>

                            <div className="col-md-2">
                                <label className="form-label">Z</label>
                                <input 
                                    className={`form-control ${locationErrors.z ? 'is-invalid' : ''}`}
                                    type="text" 
                                    inputMode="decimal"
                                    pattern="^-?\\d*\\.?\\d*$"
                                    value={displayLocation.z}
                                    onChange={(e) => handleLocationChange("z", e.target.value)}
                                    onBlur={() => handleLocationBlur("z")}
                                    disabled={estimatingMode}
                                />
                            </div>

                            <div className="col-md-3 d-flex align-items-end">
                                <button onClick={editingDevice ? handleEditDevice : handleAddDevice} className="btn btn-primary me-2">
                                    {editingDevice ? "Update" : "Add"}
                                </button>
                                {editingDevice && (
                                    <button onClick={resetForm} className="btn btn-secondary">Cancel</button>
                                )}
                            </div>
                        </div>

                        {mapId && (
                            <div className="mt-4">
                                <MapBuildOut 
                                    zoneId={mapId} 
                                    onDrawComplete={handleMapClick} 
                                    devices={filteredDevices} 
                                    useLeaflet={useLeaflet} 
                                    onDeviceSelect={handleDeviceSelect} 
                                    deploymentMode={deploymentMode}
                                    clickMarker={clickMarker}
                                />
                            </div>
                        )}
                    </div>

                    <div>
                        <h3>Devices</h3>
                        {/* Ensure filteredDevices is an array before mapping; fallback to [] if not */}
                        {Array.isArray(filteredDevices) && filteredDevices.length > 0 ? (
                            <ul style={{ listStyle: "none", padding: 0 }}>
                                {filteredDevices.map(d => (
                                    <li key={d.x_id_dev} style={{ marginBottom: "10px" }}>
                                        {d.x_id_dev} - {d.x_nm_dev} (Type: {d.i_typ_dev}, Zone: {zones.find(z => parseInt(z.i_zn) === parseInt(d.zone_id))?.x_nm_zn || "N/A"}, 
                                        Loc: {d.n_moe_x != null ? Number(d.n_moe_x).toFixed(6) : "N/A"}, 
                                        {d.n_moe_y != null ? Number(d.n_moe_y).toFixed(6) : "N/A"}, 
                                        {d.n_moe_z != null ? Number(d.n_moe_z).toFixed(6) : "N/A"})
                                        <button 
                                            onClick={() => handleDeviceSelect(d)} 
                                            style={{ marginLeft: "10px", padding: "5px" }}
                                        >
                                            Edit
                                        </button>
                                        <button onClick={() => handleDeleteDevice(d.x_id_dev)} style={{ marginLeft: "10px", padding: "5px" }}>Delete</button>
                                    </li>
                                ))}
                            </ul>
                        ) : (
                            <p>No devices available.</p>
                        )}
                    </div>
                </div>
            )}

            {activeTab === "deviceTypes" && (
                <div className="card p-4 shadow-sm">
                    <h3>Device Types</h3>
                    <div className="mb-3">
                        <input 
                            className="form-control d-inline-block" 
                            style={{ width: "300px", marginRight: "10px" }} 
                            value={newDeviceType} 
                            onChange={(e) => setNewDeviceType(e.target.value)} 
                            placeholder="New Device Type" 
                        />
                        <button onClick={handleAddDeviceType} className="btn btn-primary">Add Type</button>
                    </div>
                    <ul style={{ listStyle: "none", padding: 0 }}>
                        {deviceTypes.map(t => (
                            <li key={t.i_typ_dev} className="mb-2">
                                {t.x_dsc_dev} (ID: {t.i_typ_dev})
                                <button 
                                    onClick={() => handleDeleteDeviceType(t.i_typ_dev)} 
                                    className="btn btn-danger btn-sm" 
                                    style={{ marginLeft: "10px" }}
                                >
                                    Delete
                                </button>
                            </li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    );
};

export default BuildOutTool;