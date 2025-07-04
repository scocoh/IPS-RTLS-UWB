/* Name: SupportAccess.js */
/* Version: 0.1.1 */
/* Created: 971201 */
/* Modified: 250704 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin */
/* Description: JavaScript file for ParcoRTLS frontend */
/* Location: /home/parcoadmin/parco_fastapi/app/src */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

// SupportAccess.js
import React from "react";

function SupportAccess() {
  // Dynamic hostname detection for API calls
  const API_BASE_URL = `http://${window.location.hostname || 'localhost'}:8000`;
  
  const handleClick = async (event) => {
    // Check if CTRL and SHIFT are pressed (for macOS, you might also check event.metaKey)
    if (event.ctrlKey && event.shiftKey) {
      const password = window.prompt("Enter password:");
      if (password) {
        try {
          // Send the password to the backend for validation
          const response = await fetch("/zonebuilder/validate-support-access", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ password }),
          });
          if (!response.ok) {
            throw new Error("Invalid password");
          }
          const result = await response.json();
          if (result.status === "ok") {
            // Open the internal metadata page in a new tab
            window.open(
              `${API_BASE_URL}/zonebuilder/internal-metadata?format=html`,
              "_blank"
            );
          }
        } catch (error) {
          alert("Invalid password.");
        }
      }
    }
  };

  return (
    <span
      onClick={handleClick}
      style={{
        position: "fixed",
        bottom: "10px",
        right: "10px",
        fontSize: "24px",
        cursor: "pointer",
        opacity: 0.3,
      }}
    >
      π
    </span>
  );
}

export default SupportAccess;