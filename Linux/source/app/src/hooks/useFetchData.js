// # VERSION 250316 /home/parcoadmin/parco_fastapi/app/src/hooks/useFetchData.js 0P.10B.01
// #  
// # ParcoRTLS Middletier Services, ParcoRTLS DLL, ParcoDatabases, ParcoMessaging, and other code
// # Copyright (C) 1999 - 2025 Affiliated Commercial Services Inc.
// # Invented by Scott Cohen & Bertrand Dugal.
// # Coded by Jesse Chunn O.B.M.'24 and Michael Farnsworth and Others
// # Published at GitHub https://github.com/scocoh/IPS-RTLS-UWB
// #
// # Licensed under AGPL-3.0: https://www.gnu.org/licenses/agpl-3.0.en.html

import { useState, useEffect } from "react";

const useFetchData = (endpoints) => {
  const [data, setData] = useState({});
  const [loading, setLoading] = useState({});
  const [error, setError] = useState(null);

  const fetchData = async () => {
    setLoading(true);
    try {
      const results = {};
      for (const key in endpoints) {
        let url = endpoints[key];
        
        // Special handling for map data - get correct map_id if querying by zone
        if (key === "mapData") {
          const zoneId = url.split("/").pop(); // Extract zoneId from URL
          const zoneResponse = await fetch(`/maps/get_map_data/${zoneId}`);
          if (!zoneResponse.ok) {
            throw new Error(`HTTP error! status: ${zoneResponse.status}`);
          }
          const zoneData = await zoneResponse.json();
          if (!zoneData.map_id) {
            throw new Error(`No map associated with zone ${zoneId}`);
          }
          url = `/api/get_map/${zoneData.map_id}`; // Now fetch the actual map
        }

        const response = await fetch(url);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const jsonData = await response.json();
        results[key] = Array.isArray(jsonData) ? jsonData : []; // Ensure it's always an array
      }
      setData(results);
      setError(null);
    } catch (err) {
      console.error("Error fetching data:", err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  return { data, loading, error, fetchData };
};

export default useFetchData;
