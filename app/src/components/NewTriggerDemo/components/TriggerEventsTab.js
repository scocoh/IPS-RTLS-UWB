/* Name: TriggerEventsTab.js */
/* Version: 0.1.0 */
/* Created: 250625 */
/* Modified: 250625 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin + Claude */
/* Description: System Events tab component for NewTriggerDemo */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/NewTriggerDemo/components */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

import React from "react";

const TriggerEventsTab = ({ eventList }) => {
  if (eventList.length === 0) {
    return <p>No system events recorded.</p>;
  }

  return (
    <ul>
      {eventList.map((event, index) => (
        <li key={index}>{event}</li>
      ))}
    </ul>
  );
};

export default TriggerEventsTab;