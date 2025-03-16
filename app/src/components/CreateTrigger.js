// # VERSION 250316 /home/parcoadmin/parco_fastapi/app/src/components/CreateTrigger.js 0P.10B.01
// #  
// # ParcoRTLS Middletier Services, ParcoRTLS DLL, ParcoDatabases, ParcoMessaging, and other code
// # Copyright (C) 1999 - 2025 Affiliated Commercial Services Inc.
// # Invented by Scott Cohen & Bertrand Dugal.
// # Coded by Jesse Chunn O.B.M.'24 and Michael Farnsworth and Others
// # Published at GitHub https://github.com/scocoh/IPS-RTLS-UWB
// #
// # Licensed under AGPL-3.0: https://www.gnu.org/licenses/agpl-3.0.en.html

import React, { useState, useEffect } from "react";

const CreateTrigger = ({ onTriggerCreated }) => {
  const [triggerName, setTriggerName] = useState("");
  const [selectedZone, setSelectedZone] = useState("");
  const [zones, setZones] = useState([]);

  useEffect(() => {
    fetch("/maps/get_campus_zones") // Adjust to fetch zones for a selected map
      .then((response) => response.json())
      .then((data) => setZones(data.zones || []))
      .catch((error) => console.error("Error fetching zones:", error));
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const triggerData = { name: triggerName, zone_id: selectedZone };
    const response = await fetch("/api/add_trigger", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(triggerData),
    });
    if (response.ok) {
      const result = await response.json();
      if (onTriggerCreated) onTriggerCreated(result.trigger_id);
      alert(`Trigger created with ID: ${result.trigger_id}`);
    } else {
      alert("Error creating trigger");
    }
  };

  return (
    <div>
      <h1>Create Trigger</h1>
      <form onSubmit={handleSubmit}>
        <div>
          <label>Name:</label>
          <input type="text" value={triggerName} onChange={(e) => setTriggerName(e.target.value)} />
        </div>
        <div>
          <label>Zone:</label>
          <select value={selectedZone} onChange={(e) => setSelectedZone(e.target.value)}>
            <option value="">Select Zone</option>
            {zones.map((zone) => (
              <option key={zone.zone_id} value={zone.zone_id}>
                {zone.zone_name}
              </option>
            ))}
          </select>
        </div>
        <button type="submit">Create Trigger</button>
      </form>
    </div>
  );
};

export default CreateTrigger;