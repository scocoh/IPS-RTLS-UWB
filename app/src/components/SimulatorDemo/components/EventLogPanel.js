/* Name: EventLogPanel.js */
/* Version: 0.2.0 */
/* Created: 250707 */
/* Modified: 250708 */
/* Creator: ParcoAdmin */
/* Modified By: ChatGPT */
/* Description: Scrollable Event log panel component with auto-scroll toggle and export */
/* Role: Frontend */
/* Status: Active */

import React, { useEffect, useRef, useState } from 'react';
import '../styles/SimulatorDemo.css';

const EventLogPanel = ({ eventLog, onClear }) => {
  const logEndRef = useRef(null);
  const [autoScroll, setAutoScroll] = useState(true);

  useEffect(() => {
    if (autoScroll && logEndRef.current) {
      logEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [eventLog, autoScroll]);

  const formatLogEntry = (entry) => {
    const match = entry.match(/^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d+Z): (.+)$/);
    if (match) {
      const [, timestamp, message] = match;
      const time = new Date(timestamp).toLocaleTimeString();
      return { time, message };
    }
    return { time: '', message: entry };
  };

  const getLogEntryClass = (msg) => {
    if (/error|fail/i.test(msg)) return 'log-entry error';
    if (/success|connected/i.test(msg)) return 'log-entry success';
    if (/starting|stopping/i.test(msg)) return 'log-entry info';
    if (/GISData|sent/i.test(msg)) return 'log-entry data';
    return 'log-entry';
  };

  const exportLog = () => {
    const blob = new Blob([eventLog.join('\n')], { type: 'text/plain' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `sim-log-${new Date().toISOString()}.txt`;
    a.click();
    URL.revokeObjectURL(a.href);
  };

  return (
    <div className="event-log-panel">
      <div className="log-header">
        <h3>Event Log</h3>
        <div className="log-controls">
          <span className="log-count">{eventLog.length} entries</span>
          <label>
            <input
              type="checkbox"
              checked={autoScroll}
              onChange={() => setAutoScroll(!autoScroll)}
            />
            Auto-scroll
          </label>
          <button onClick={exportLog} disabled={eventLog.length === 0}>Export</button>
          <button onClick={onClear}>Clear</button>
        </div>
      </div>

      <div className="log-scroll-container">
        <div className="log-content">
          {eventLog.length === 0 ? (
            <div className="log-empty">No events logged yet.</div>
          ) : (
            eventLog.map((entry, idx) => {
              const { time, message } = formatLogEntry(entry);
              return (
                <div key={idx} className={getLogEntryClass(message)}>
                  {time && <span className="log-time">{time}</span>}
                  <span className="log-message">{message}</span>
                </div>
              );
            })
          )}
          <div ref={logEndRef} />
        </div>
      </div>
    </div>
  );
};

export default EventLogPanel;
