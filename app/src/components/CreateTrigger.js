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