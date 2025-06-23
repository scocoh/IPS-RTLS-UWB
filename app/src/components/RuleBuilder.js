/* Name: RuleBuilder.js */
/* Version: 0.2.7.0 */
/* Created: 250609 */
/* Modified: 250623 */
/* Creator: ParcoAdmin */
/* Modified By: ClaudeAI */
/* Description: React component for TETSE rule construction and code generation, using backend API parsing only */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/RuleBuilder.js */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */
/* Update: Removed frontend parsing, rely entirely on backend API for rule interpretation */

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

// Frontend parsing removed - backend API handles all rule interpretation

  const promptForMissing = async (missingField, ruleData) => {
    return new Promise((resolve) => {
      let promptText = '';
      let defaultInput = '';
      switch (missingField) {
        case 'campus_id':
          promptText = 'Please select a campus zone from the dropdown above';
          defaultInput = '';
          break;
        default:
          promptText = `Missing ${missingField}. Please check your rule text or fill the form fields.`;
          defaultInput = '';
          break;
      }
      setModalPrompt(promptText);
      setModalInput(defaultInput);
      setModalCallback(() => (input) => {
        const updatedData = { ...ruleData };
        if (missingField === 'campus_id') {
          // For campus_id, we need them to select from dropdown
          setShowModal(false);
          resolve(null); // Return null to indicate they need to use the form
        } else {
          updatedData[missingField] = input;
          setShowModal(false);
          resolve(updatedData);
        }
      });
      setShowModal(true);
    });
  };

  const validateRule = async (ruleData) => {
    // Only validate required fields that frontend needs
    if (!ruleData.rule_text || ruleData.rule_text.trim() === '') {
      throw new Error('Please enter a rule in natural language');
    }
    
    if (!ruleData.campus_id || ruleData.campus_id === '') {
      const updatedData = await promptForMissing('campus_id', ruleData);
      if (!updatedData) {
        throw new Error('Campus zone is required. Please select one from the dropdown.');
      }
      return updatedData;
    }

    return ruleData;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResponse(null);
    
    try {
      console.log('Current form state:', {
        ruleText,
        campusZone,
        subjectId,
        zone,
        duration,
        action
      });

      // Map campusZone name to ID
      const campusId = campusZones.find(c => c.name === campusZone)?.id || '';
      if (!campusId) {
        throw new Error('Please select a valid campus zone');
      }

      // Build rule data - only send what we have, let backend parse everything
      let ruleData = {
        rule_text: ruleText,
        campus_id: campusId.toString(),
        verbose: true
      };

      // Only include form fields if they have values (optional hints to backend)
      if (subjectId.trim()) {
        ruleData.subject_id = subjectId.trim();
      }
      if (zone.trim()) {
        ruleData.zone = zone.trim();
      }
      if (duration) {
        ruleData.duration_sec = parseInt(duration) || undefined;
      }
      if (action && action !== 'alert') {
        ruleData.action = action;
      }

      console.log('Sending to API:', ruleData);

      // Validate minimal requirements
      await validateRule(ruleData);

      // Submit to backend API - let it do all the parsing
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

      // Update form fields with any parsed values from response if available
      if (data.rule && data.rule.subject_id && !subjectId) {
        setSubjectId(data.rule.subject_id);
      }

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
            placeholder="E.g., if tag 23001 goes from inside to outside with tag 23003 send an alert"
            className="form-control"
            rows="4"
          />
        </div>
        <div className="row mb-3">
          <div className="col-md-6">
            <label className="form-label">Subject ID (Device) <small className="text-muted">(Optional - can be parsed from rule text)</small></label>
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
            <label className="form-label">Zone <small className="text-muted">(Optional - can be parsed from rule text)</small></label>
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
            <label className="form-label">Duration (seconds) <small className="text-muted">(Optional - can be parsed from rule text)</small></label>
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
            <label className="form-label">Action <small className="text-muted">(Optional - can be parsed from rule text)</small></label>
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