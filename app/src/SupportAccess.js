// SupportAccess.js
import React from "react";

function SupportAccess() {
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
              "http://192.168.210.231:8000/zonebuilder/internal-metadata?format=html",
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
