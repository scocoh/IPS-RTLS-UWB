/* Name: RuleBuilder.js */
/* Version: 0.2.6.6 */
/* Created: 250609 */
/* Modified: 250620 */
/* Creator: ParcoAdmin */
/* Modified By: ClaudeAI */
/* Description: React component for TETSE rule construction and code generation, using API-based parsing with subject_id */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/RuleBuilder.js */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */
/* Update: Fixed version typo from 0.2.6.56 to 0.2.6.6 */
/* Update: Fixed parseRuleText regex and handleSubmit to correctly merge parsed and form data, bumped from 0.2.6.4 */
/* Update: Fixed parseRuleText with simpler zone parsing logic to correctly identify "outside"/"backyard" */

import React, { useState, useEffect, useCallback } from 'react';

const useDebounce = (value, delay) => {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);
    return () => clearTimeout(handler);
  }, [value, delay]);

  return debouncedValue;
};

const EventStream = ({ subjectId }) => {
  const [events, setEvents] = useState([]);
  const [wsError, setWsError] = useState(null);
  const debouncedSubjectId = useDebounce(subjectId, 1000);

  const connectWebSocket = useCallback((id) => {
    if (!id || id.length < 3 || !/^[A-Za-z0-9]+$/.test(id)) {
      setWsError('Invalid Subject ID: Use only alphanumeric characters');
      return;
    }
    const ws = new WebSocket(`ws://192.168.210.226:9000/ws/tetse_event/${id}`);
    
    ws.onopen = () => {
      console.log(`Connected to WebSocket for ${id}`);
      setWsError(null);
    };
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type !== 'ping' && data.type !== 'HeartBeat') {
          setEvents((prev) => [...prev, data].slice(-5));
        }
      } catch (e) {
        console.error('Invalid WebSocket message:', e);
        setWsError('Invalid event data');
      }
    };
    ws.onerror = (e) => {
      console.error('WebSocket error:', e);
      setWsError('Failed to connect to event stream');
    };
    ws.onclose = () => {
      console.log('WebSocket closed');
      setWsError('Event stream disconnected');
    };
    
    return () => ws.close();
  }, []);

  useEffect(() => {
    if (debouncedSubjectId) {
      const cleanup = connectWebSocket(debouncedSubjectId);
      return cleanup;
    }
  }, [debouncedSubjectId, connectWebSocket]);

  return (
    <div className="mt-3">
      <h3 className="h5">Real-Time Events for {subjectId}</h3>
      {wsError && (
        <div className="alert alert-warning" role="alert">
          {wsError}
        </div>
      )}
      <ul className="list-group mt-2">
        {events.map((event, idx) => (
          <li key={idx} className="list-group-item">
            <pre>{JSON.stringify(event, null, 2)}</pre>
          </li>
        ))}
      </ul>
    </div>
  );
};

const RuleForm = () => {
  const [ruleText, setRuleText] = useState('');
  const [subjectId, setSubjectId] = useState('');
  const [campusZone, setCampusZone] = useState('');
  const [zone, setZone] = useState('');
  const [duration, setDuration] = useState('');
  const [action, setAction] = useState('alert');
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [allZones, setAllZones] = useState([]);
  const [campusZones, setCampusZones] = useState([]);
  const [childZones, setChildZones] = useState([]);
  const [fetchError, setFetchError] = useState(null);
  const [isFetchingZones, setIsFetchingZones] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [modalPrompt, setModalPrompt] = useState('');
  const [modalInput, setModalInput] = useState('');
  const [modalCallback, setModalCallback] = useState(null);

  useEffect(() => {
    fetch('http://192.168.210.226:8000/api/zones_for_ai')
      .then((res) => {
        if (!res.ok) {
          throw new Error(`HTTP error! Status: ${res.status}`);
        }
        return res.json();
      })
      .then((data) => {
        console.log('Zones fetch response:', data);
        if (Array.isArray(data.zones)) {
          setAllZones(data.zones);
          const campuses = data.zones.filter(z => z.type === 1);
          setCampusZones(campuses);
        } else {
          console.error('Zones data is not an array:', data);
          setAllZones([]);
          setCampusZones([]);
          setFetchError('Invalid zone data received');
        }
      })
      .catch((err) => {
        console.error('Error fetching zones:', err);
        setAllZones([]);
        setCampusZones([]);
        setFetchError(err.message);
      })
      .finally(() => {
        setIsFetchingZones(false);
      });
  }, []);

  useEffect(() => {
    if (campusZone) {
      const selectedCampus = campusZones.find(z => z.name === campusZone);
      if (selectedCampus) {
        const descendants = getDescendantZones(selectedCampus.id, allZones);
        setChildZones(descendants);
        setZone('');
      } else {
        setChildZones([]);
      }
    } else {
      setChildZones([]);
    }
  }, [campusZone, allZones]);

  const getDescendantZones = (zoneId, zones) => {
    const descendants = [];
    const children = zones.filter(z => z.parent === zoneId);
    children.forEach(child => {
      descendants.push(child);
      descendants.push(...getDescendantZones(child.id, zones));
    });
    return descendants;
  };

const parseRuleText = (text) => {
  const result = { subject_id: '', zone: '', duration_sec: 0, action: '' };
  
  // Parse subject_id
  const subjectMatch = text.match(/(?:if\s+)(tag\s+)?([A-Za-z0-9]+)\s+stays/i);
  if (subjectMatch) {
    result.subject_id = subjectMatch[2];
    console.log(`Parsed subject_id: ${result.subject_id}`);
  }
  
  // Parse zone - much simpler approach
  if (text.toLowerCase().includes('stays outside')) {
    result.zone = 'outside';
    console.log(`Parsed zone: ${result.zone}`);
  } else if (text.toLowerCase().includes('stays in backyard')) {
    result.zone = 'backyard';
    console.log(`Parsed zone: ${result.zone}`);
  } else {
    // Try to match "stays in [zone_name]"
    const zoneInMatch = text.match(/stays\s+in\s+([A-Za-z0-9\-_\s]+?)(?:\s+for|\s+then|\s*$)/i);
    if (zoneInMatch) {
      result.zone = zoneInMatch[1].trim();
      console.log(`Parsed zone: ${result.zone}`);
    }
  }
  
  // Parse duration
  const durationMatch = text.match(/(?:for\s+|more\s+than\s+)(\d+)\s+minute(s)?/i);
  if (durationMatch) {
    result.duration_sec = parseInt(durationMatch[1]) * 60;
    console.log(`Parsed duration_sec: ${result.duration_sec}`);
  }
  
  // Parse action
  const actionMatch = text.match(/(?:then\s+)?(alert|create an alert box|log|trigger mqtt|notify)\s*(?:me)?/i);
  if (actionMatch) {
    const action = actionMatch[1].toLowerCase();
    result.action = action.includes('alert') || action.includes('notify') ? 'alert' : action.includes('log') ? 'log' : 'mqtt';
    console.log(`Parsed action: ${result.action}`);
  } else if (text.toLowerCase().includes('alert me')) {
    result.action = 'alert';
    console.log(`Parsed action: ${result.action}`);
  }

  return result;
};

  const promptForMissing = async (missingField, ruleData) => {
    return new Promise((resolve) => {
      let promptText = '';
      let defaultInput = '';
      switch (missingField) {
        case 'subject_id':
          promptText = 'What is the Subject ID (device) for this rule?';
          defaultInput = ruleData.subject_id || '';
          break;
        case 'zone':
          promptText = 'Which zone should this rule apply to?';
          defaultInput = ruleData.zone || '';
          break;
        case 'duration_sec':
          promptText = 'How long (in seconds) before the event fires?';
          defaultInput = ruleData.duration_sec > 0 ? ruleData.duration_sec.toString() : '60';
          break;
        case 'action':
          promptText = 'What action should this rule trigger? (alert, mqtt, log)';
          defaultInput = ruleData.action || 'alert';
          break;
      }
      setModalPrompt(promptText);
      setModalInput(defaultInput);
      setModalCallback(() => (input) => {
        const updatedData = { ...ruleData };
        updatedData[missingField] = missingField === 'duration_sec' ? parseInt(input) || 60 : input;
        setShowModal(false);
        resolve(updatedData);
      });
      setShowModal(true);
    });
  };

  const validateRule = async (ruleData) => {
    let validatedData = { ...ruleData };
    const requiredFields = ['subject_id', 'zone', 'duration_sec', 'action'];

    console.log('Validating rule data:', validatedData);

    for (const field of requiredFields) {
      if (
        !validatedData[field] ||
        (field === 'subject_id' && validatedData[field].trim() === '') ||
        (field === 'zone' && validatedData[field].trim() === '') ||
        (field === 'duration_sec' && (isNaN(validatedData[field]) || validatedData[field] <= 0)) ||
        (field === 'action' && !['alert', 'mqtt', 'log'].includes(validatedData[field]))
      ) {
        console.log(`Prompting for missing/invalid field: ${field}`);
        validatedData = await promptForMissing(field, validatedData);
      }
    }

    return validatedData;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResponse(null); // Clear previous response
    try {
      // Log current form state
      console.log('Current form state:', {
        subjectId,
        campusZone,
        zone,
        duration,
        action,
        ruleText
      });

      // Map campusZone name to ID
      const campusId = campusZones.find(c => c.name === campusZone)?.id || '';
      if (!campusId) {
        throw new Error('Please select a valid campus zone');
      }

      // Initialize rule data
      let ruleData = {
        rule_text: ruleText,
        campus_id: campusId.toString(),
        subject_id: subjectId.trim(),
        zone: zone.trim(),
        duration_sec: parseInt(duration) || 0,
        action: action,
        verbose: true
      };

      console.log('Initial rule data:', ruleData);

      // Parse rule text if provided
      if (ruleText) {
        const parsedData = parseRuleText(ruleText);
        console.log('Parsed rule text:', parsedData);

        // Merge parsed data, prioritizing form inputs
        ruleData = {
          ...ruleData,
          subject_id: ruleData.subject_id || parsedData.subject_id || '',
          zone: ruleData.zone || parsedData.zone || '',
          duration_sec: ruleData.duration_sec || parsedData.duration_sec || 300,
          action: ruleData.action || parsedData.action || 'alert'
        };

        // Update form state to reflect parsed or form values
        setSubjectId(ruleData.subject_id);
        setZone(ruleData.zone);
        setDuration(ruleData.duration_sec.toString());
        setAction(ruleData.action);
      }

      // Validate rule data
      ruleData = await validateRule(ruleData);
      console.log('Validated rule data:', ruleData);

      // Submit rule
      const res = await fetch('http://192.168.210.226:8000/api/openai/create_rule_live', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(ruleData)
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || `HTTP error! Status: ${res.status}`);
      }

      const data = await res.json();
      console.log('API response:', data);
      setResponse(data);

    } catch (err) {
      console.error('Submit error:', err);
      setResponse({ error: `Failed to create rule: ${err.message}` });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mt-3">
      <h2 className="h4 mb-3">Create TETSE Rule</h2>
      {fetchError && (
        <div className="alert alert-danger" role="alert">
          {fetchError}
        </div>
      )}
      {showModal && (
        <div className="modal" style={{ display: 'block', backgroundColor: 'rgba(0,0,0,0.5)' }}>
          <div className="modal-dialog">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">Missing Information</h5>
                <button type="button" className="btn-close" onClick={() => setShowModal(false)}></button>
              </div>
              <div className="modal-body">
                <p>{modalPrompt}</p>
                <input
                  type="text"
                  className="form-control"
                  value={modalInput}
                  onChange={(e) => {
                    console.log(`Modal input changed: ${e.target.value}`);
                    setModalInput(e.target.value);
                  }}
                />
              </div>
              <div className="modal-footer">
                <button
                  type="button"
                  className="btn btn-primary"
                  onClick={() => {
                    console.log(`Modal submit: ${modalInput}`);
                    modalCallback(modalInput);
                  }}
                >
                  Submit
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
      <form onSubmit={handleSubmit}>
        <div className="mb-3">
          <label className="form-label">Natural Language Rule</label>
          <textarea
            value={ruleText}
            onChange={(e) => {
              console.log(`Rule text changed: ${e.target.value}`);
              setRuleText(e.target.value);
            }}
            placeholder="E.g., If TAG001 stays in 6005BOL2-Child for 5 minutes then alert"
            className="form-control"
            rows="4"
          />
        </div>
        <div className="row mb-3">
          <div className="col-md-6">
            <label className="form-label">Subject ID (Device)</label>
            <input
              type="text"
              value={subjectId}
              onChange={(e) => {
                const value = e.target.value.trim().replace(/[^A-Za-z0-9]/g, '');
                console.log(`Subject ID changed: ${value}`);
                setSubjectId(value);
              }}
              placeholder="E.g., TAG001"
              className="form-control"
            />
          </div>
          <div className="col-md-6">
            <label className="form-label">Campus Zone</label>
            {isFetchingZones ? (
              <div className="spinner-border text-primary" role="status">
                <span className="visually-hidden">Loading zones...</span>
              </div>
            ) : (
              <select
                value={campusZone}
                onChange={(e) => {
                  console.log(`Campus Zone changed: ${e.target.value}`);
                  setCampusZone(e.target.value);
                }}
                className="form-select"
              >
                <option value="">Select Campus Zone</option>
                {Array.isArray(campusZones) && campusZones.length > 0 ? (
                  campusZones.map((z) => (
                    <option key={z.id} value={z.name}>{z.name}</option>
                  ))
                ) : (
                  <option value="" disabled>No campus zones available</option>
                )}
              </select>
            )}
          </div>
        </div>
        <div className="row mb-3">
          <div className="col-md-6">
            <label className="form-label">Zone</label>
            {isFetchingZones ? (
              <div className="spinner-border text-primary" role="status">
                <span className="visually-hidden">Loading zones...</span>
              </div>
            ) : (
              <select
                value={zone}
                onChange={(e) => {
                  console.log(`Zone changed: ${e.target.value}`);
                  setZone(e.target.value);
                }}
                className="form-select"
                disabled={!campusZone}
              >
                <option value="">Select Zone</option>
                {Array.isArray(childZones) && childZones.length > 0 ? (
                  childZones.map((z) => (
                    <option key={z.id} value={z.name}>{z.name}</option>
                  ))
                ) : (
                  <option value="" disabled>No zones available</option>
                )}
              </select>
            )}
          </div>
          <div className="col-md-6">
            <label className="form-label">Duration (seconds)</label>
            <input
              type="number"
              value={duration}
              onChange={(e) => {
                console.log(`Duration changed: ${e.target.value}`);
                setDuration(e.target.value);
              }}
              placeholder="E.g., 300"
              className="form-control"
            />
          </div>
        </div>
        <div className="row mb-3">
          <div className="col-md-6">
            <label className="form-label">Action</label>
            <select
              value={action}
              onChange={(e) => {
                console.log(`Action changed: ${e.target.value}`);
                setAction(e.target.value);
              }}
              className="form-select"
            >
              <option value="alert">Alert</option>
              <option value="mqtt">MQTT Deterrent</option>
              <option value="log">Log to TETSE</option>
            </select>
          </div>
        </div>
        <button
          type="submit"
          disabled={loading}
          className="btn btn-primary w-100"
        >
          {loading ? 'Creating...' : 'Create Rule'}
        </button>
      </form>
      {response && (
        <div className="card mt-3">
          <div className="card-body">
            <h3 className="h5">Response</h3>
            <pre>{JSON.stringify(response, null, 2)}</pre>
          </div>
        </div>
      )}
      {subjectId && <EventStream subjectId={subjectId} />}
    </div>
  );
};

const CodeGenerator = () => {
  const [eventText, setEventText] = useState('');
  const [generatedCode, setGeneratedCode] = useState('');
  const [loading, setLoading] = useState(false);

  const handleGenerate = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      if (!eventText) {
        throw new Error('Please provide an event description');
      }
      const res = await fetch('http://192.168.210.226:8000/api/openai/generate_code', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ event_description: eventText }),
      });
      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || `HTTP error! Status: ${res.status}`);
      }
      const data = await res.json();
      setGeneratedCode(data.code);
    } catch (err) {
      console.error('Generate code error:', err);
      setGeneratedCode(`Error generating code: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mt-3">
      <h2 className="h4 mb-3">Generate FastAPI Code for RTLS Events</h2>
      <form onSubmit={handleGenerate}>
        <div className="mb-3">
          <label className="form-label">Event Description</label>
          <textarea
            value={eventText}
            onChange={(e) => setEventText(e.target.value)}
            placeholder="E.g., Send a webhook if a tag stays in Building A for 10 minutes"
            className="form-control"
            rows="4"
          />
        </div>
        <button
          type="submit"
          disabled={loading}
          className="btn btn-primary w-100"
        >
          {loading ? 'Generating...' : 'Generate Code'}
        </button>
      </form>
      {generatedCode && (
        <div className="card mt-3">
          <div className="card-body">
            <h3 className="h5">Generated Code</h3>
            <pre>{generatedCode}</pre>
          </div>
        </div>
      )}
    </div>
  );
};

const RuleBuilder = () => {
  const [activeTab, setActiveTab] = useState('rules');

  return (
    <div className="container mt-3">
      <h1 className="h3 text-center mb-3">ParcoRTLS Rule Builder</h1>
      <ul className="nav nav-tabs mb-3">
        <li className="nav-item">
          <button
            className={`nav-link ${activeTab === 'rules' ? 'active' : ''}`}
            onClick={() => setActiveTab('rules')}
          >
            Create Rules
          </button>
        </li>
        <li className="nav-item">
          <button
            className={`nav-link ${activeTab === 'code' ? 'active' : ''}`}
            onClick={() => setActiveTab('code')}
          >
            Generate Code
          </button>
        </li>
      </ul>
      {activeTab === 'rules' ? <RuleForm /> : <CodeGenerator />}
    </div>
  );
};

export default RuleBuilder;