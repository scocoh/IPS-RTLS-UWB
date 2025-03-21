// # VERSION 250320 /home/parcoadmin/parco_fastapi/app/src/components/BuildOutTool.js 0P.10B.31
// # --- CHANGED: Bumped version from 0P.10B.30 to 0P.10B.31 to fix device ID update persistence by using new_device_id parameter
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

    useEffect(() => {
        const fetchData = async () => {
            try {
                const devicesRes = await fetch("/api/get_all_devices");
                const devicesData = await devicesRes.json();
                console.log("Raw devices response:", JSON.stringify(devicesData, null, 2));
                setDevices(devicesData);

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
        formData.append("new_device_id", deviceId); // --- CHANGED: Use new_device_id parameter to match the endpoint
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

            <div ref={addEditSectionRef} style={{ marginBottom: "20px" }}>
                <h3>Add/Edit Device</h3>
                <label>Zone Type: </label>
                <select 
                    value={zoneType} 
                    onChange={(e) => setZoneType(e.target.value)} 
                    style={{ marginRight: "10px" }} 
                    disabled={estimatingMode}
                >
                    <option value="">Select Zone Type</option>
                    {zoneTypes.map(zt => (
                        <option key={zt.zone_level} value={zt.zone_level}>{zt.zone_name}</option>
                    ))}
                </select>
                <label>Zone/Map: </label>
                <select 
                    value={selectedZone} 
                    onChange={(e) => setSelectedZone(e.target.value)} 
                    style={{ marginRight: "10px" }} 
                    disabled={estimatingMode}
                >
                    <option value="">Select Zone</option>
                    {filteredZones.map(z => (
                        <option key={z.i_zn} value={z.i_zn}>{z.x_nm_zn}</option>
                    ))}
                </select>
                <label>Use Leaflet: </label>
                <input 
                    type="checkbox" 
                    checked={useLeaflet} 
                    onChange={(e) => setUseLeaflet(e.target.checked)} 
                />
                <label style={{ marginLeft: "20px" }}>Estimating Mode: </label>
                <input 
                    type="checkbox" 
                    checked={estimatingMode} 
                    onChange={handleEstimatingModeToggle} 
                />
                <label style={{ marginLeft: "20px" }}>Deployment Mode: </label>
                <input 
                    type="checkbox" 
                    checked={deploymentMode} 
                    onChange={handleDeploymentModeToggle} 
                />
                {estimatingMode && (
                    <>
                        <label style={{ marginLeft: "20px" }}>Starting Device ID: </label>
                        <input
                            type="number"
                            value={startingDeviceId}
                            onChange={(e) => {
                                const value = e.target.value;
                                setStartingDeviceId(value);
                                const startId = parseInt(value) || 0;
                                setCurrentDeviceId(startId);
                                setDeviceId(startId.toString());
                                setDeviceName(startId.toString());
                            }}
                            style={{ width: "100px", marginRight: "10px" }}
                        />
                    </>
                )}
                <br />
                <label>Device ID/Serial: </label>
                <input 
                    value={deviceId} 
                    onChange={(e) => {
                        setDeviceId(e.target.value);
                        if (estimatingMode) {
                            setDeviceName(e.target.value);
                        }
                    }} 
                    disabled={editingDevice !== null && !deploymentMode}
                    style={{ marginRight: "10px", width: "150px" }} 
                />
                <label>Name: </label>
                <input 
                    value={deviceName} 
                    onChange={(e) => setDeviceName(e.target.value)} 
                    disabled={estimatingMode}
                    style={{ marginRight: "10px", width: "150px" }} 
                />
                <label>Type: </label>
                <select 
                    value={deviceType} 
                    onChange={(e) => {
                        console.log("Selected device type:", e.target.value);
                        setDeviceType(e.target.value);
                    }} 
                    style={{ marginRight: "10px" }}
                >
                    <option value="">Select Type</option>
                    {deviceTypes.map(t => (
                        <option key={t.i_typ_dev} value={t.i_typ_dev}>{t.x_dsc_dev}</option>
                    ))}
                </select>
                <label>X: </label>
                <input 
                    type="text" 
                    inputMode="decimal"
                    pattern="^-?\d*\.?\d*$"
                    value={displayLocation.x}
                    onChange={(e) => handleLocationChange("x", e.target.value)}
                    onBlur={() => handleLocationBlur("x")}
                    style={{ 
                        width: "100px", 
                        marginRight: "10px", 
                        border: locationErrors.x ? "2px solid red" : "1px solid #ccc" 
                    }} 
                />
                <label>Y: </label>
                <input 
                    type="text" 
                    inputMode="decimal"
                    pattern="^-?\d*\.?\d*$"
                    value={displayLocation.y}
                    onChange={(e) => handleLocationChange("y", e.target.value)}
                    onBlur={() => handleLocationBlur("y")}
                    style={{ 
                        width: "100px", 
                        marginRight: "10px", 
                        border: locationErrors.y ? "2px solid red" : "1px solid #ccc" 
                    }} 
                />
                <label>Z: </label>
                <input 
                    type="text" 
                    inputMode="decimal"
                    pattern="^-?\d*\.?\d*$"
                    value={displayLocation.z}
                    onChange={(e) => handleLocationChange("z", e.target.value)}
                    onBlur={() => handleLocationBlur("z")}
                    disabled={estimatingMode}
                    style={{ 
                        width: "100px", 
                        marginRight: "10px", 
                        border: locationErrors.z ? "2px solid red" : "1px solid #ccc" 
                    }} 
                />
                <button onClick={editingDevice ? handleEditDevice : handleAddDevice} style={{ padding: "5px 10px" }}>
                    {editingDevice ? "Update" : "Add"}
                </button>
                {editingDevice && (
                    <button onClick={resetForm} style={{ padding: "5px 10px", marginLeft: "10px" }}>Cancel</button>
                )}
                {mapId && (
                    <MapBuildOut 
                        zoneId={mapId} 
                        onDrawComplete={handleMapClick} 
                        devices={filteredDevices} 
                        useLeaflet={useLeaflet} 
                        onDeviceSelect={handleDeviceSelect} 
                        deploymentMode={deploymentMode}
                        clickMarker={clickMarker}
                    />
                )}
            </div>

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

            <div>
                <h3>Devices</h3>
                <ul style={{ listStyle: "none", padding: 0 }}>
                    {filteredDevices.map(d => (
                        <li key={d.x_id_dev} style={{ marginBottom: "10px" }}>
                            {d.x_id_dev} - {d.x_nm_dev} (Type: {d.i_typ_dev}, Zone: {zones.find(z => parseInt(z.i_zn) === parseInt(d.zone_id))?.x_nm_zn || "N/A"}, 
                            Loc: {d.n_moe_x != null ? Number(d.n_moe_x).toFixed(6) : "N/A"}, 
                            {d.n_moe_y != null ? Number(d.n_moe_y).toFixed(6) : "N/A"}, 
                            {d.n_moe_z != null ? Number(d.n_moe_z).toFixed(6) : "N/A"})
                            <button 
                                onClick={() => { 
                                    setEditingDevice(d); 
                                    setDeviceId(d.x_id_dev); 
                                    setDeviceName(d.x_nm_dev); 
                                    setDeviceType(String(d.i_typ_dev)); 
                                    const newLocation = { x: d.n_moe_x, y: d.n_moe_y, z: d.n_moe_z || 0 };
                                    setLocation(newLocation);
                                    setDisplayLocation({
                                        x: newLocation.x != null ? newLocation.x.toString() : "",
                                        y: newLocation.y != null ? newLocation.y.toString() : "",
                                        z: newLocation.z != null ? newLocation.z.toString() : ""
                                    });
                                    setLocationErrors({ x: false, y: false, z: false });
                                    setSelectedZone(String(d.zone_id || "")); 
                                    addEditSectionRef.current.scrollIntoView({ behavior: "smooth" });
                                }} 
                                style={{ marginLeft: "10px", padding: "5px" }}
                            >
                                Edit
                            </button>
                            <button onClick={() => handleDeleteDevice(d.x_id_dev)} style={{ marginLeft: "10px", padding: "5px" }}>Delete</button>
                        </li>
                    ))}
                </ul>
            </div>
        </div>
    );
};

export default BuildOutTool;