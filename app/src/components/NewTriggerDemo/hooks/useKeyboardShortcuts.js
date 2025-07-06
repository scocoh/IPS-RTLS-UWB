/* Name: useKeyboardShortcuts.js */
/* Version: 0.1.0 */
/* Created: 250706 */
/* Modified: 250706 */
/* Creator: ParcoAdmin + Claude */
/* Modified By: ParcoAdmin + Claude */
/* Description: Custom hook for keyboard shortcuts in NewTriggerDemo */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/NewTriggerDemo/hooks */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

import { useEffect, useCallback, useRef } from 'react';

/**
 * Custom hook for managing keyboard shortcuts in the NewTriggerDemo
 * Provides common map navigation and control shortcuts
 */
export const useKeyboardShortcuts = ({
  isEnabled = true,
  onHomeView = null,
  onFitToData = null,
  onToggleLegend = null,
  onToggleControls = null,
  onToggleTriggers = null,
  onToggleTagVisibility = null,
  onCycleMapMode = null,
  onClearEvents = null,
  mapInstance = null
}) => {
  const shortcutsEnabledRef = useRef(isEnabled);
  const activeModifiersRef = useRef({ ctrl: false, shift: false, alt: false });

  // Update enabled state
  useEffect(() => {
    shortcutsEnabledRef.current = isEnabled;
  }, [isEnabled]);

  // Key combination handler
  const handleKeyDown = useCallback((event) => {
    if (!shortcutsEnabledRef.current) return;

    // Don't trigger shortcuts when typing in input fields
    const activeElement = document.activeElement;
    if (activeElement && (
      activeElement.tagName === 'INPUT' ||
      activeElement.tagName === 'TEXTAREA' ||
      activeElement.contentEditable === 'true'
    )) {
      return;
    }

    // Update modifier states
    activeModifiersRef.current = {
      ctrl: event.ctrlKey || event.metaKey, // Support both Ctrl and Cmd
      shift: event.shiftKey,
      alt: event.altKey
    };

    const { ctrl, shift, alt } = activeModifiersRef.current;
    const key = event.key.toLowerCase();

    // Prevent default for handled shortcuts
    let handled = false;

    // Basic navigation shortcuts
    switch (key) {
      case 'h':
        if (!ctrl && !shift && !alt) {
          onHomeView?.();
          handled = true;
        }
        break;

      case 'f':
        if (!ctrl && !shift && !alt) {
          onFitToData?.();
          handled = true;
        }
        break;

      case 'r':
        if (ctrl && !shift && !alt) {
          // Ctrl+R: Reset view (same as home)
          onHomeView?.();
          handled = true;
        }
        break;

      case 'l':
        if (!ctrl && !shift && !alt) {
          onToggleLegend?.();
          handled = true;
        }
        break;

      case 'c':
        if (!ctrl && !shift && !alt) {
          onToggleControls?.();
          handled = true;
        }
        break;

      case 't':
        if (!ctrl && !shift && !alt) {
          onToggleTriggers?.();
          handled = true;
        }
        break;

      case 'v':
        if (!ctrl && !shift && !alt) {
          onToggleTagVisibility?.();
          handled = true;
        }
        break;

      case 'm':
        if (!ctrl && !shift && !alt) {
          onCycleMapMode?.();
          handled = true;
        }
        break;

      case 'delete':
      case 'backspace':
        if (ctrl && !shift && !alt) {
          onClearEvents?.();
          handled = true;
        }
        break;

      // Zoom shortcuts (if map instance is available)
      case '+':
      case '=':
        if (mapInstance && !ctrl && !shift && !alt) {
          mapInstance.zoomIn();
          handled = true;
        }
        break;

      case '-':
        if (mapInstance && !ctrl && !shift && !alt) {
          mapInstance.zoomOut();
          handled = true;
        }
        break;

      case '0':
        if (mapInstance && !ctrl && !shift && !alt) {
          // Reset zoom to fit bounds
          onHomeView?.();
          handled = true;
        }
        break;

      // Arrow keys for map panning (if map instance is available)
      case 'arrowup':
        if (mapInstance && !ctrl && !shift && !alt) {
          mapInstance.panBy([0, -50]);
          handled = true;
        }
        break;

      case 'arrowdown':
        if (mapInstance && !ctrl && !shift && !alt) {
          mapInstance.panBy([0, 50]);
          handled = true;
        }
        break;

      case 'arrowleft':
        if (mapInstance && !ctrl && !shift && !alt) {
          mapInstance.panBy([-50, 0]);
          handled = true;
        }
        break;

      case 'arrowright':
        if (mapInstance && !ctrl && !shift && !alt) {
          mapInstance.panBy([50, 0]);
          handled = true;
        }
        break;

      // Help shortcut
      case '?':
      case '/':
        if (!ctrl && !shift && !alt) {
          showShortcutsHelp();
          handled = true;
        }
        break;
    }

    if (handled) {
      event.preventDefault();
      event.stopPropagation();
    }
  }, [
    onHomeView,
    onFitToData,
    onToggleLegend,
    onToggleControls,
    onToggleTriggers,
    onToggleTagVisibility,
    onCycleMapMode,
    onClearEvents,
    mapInstance
  ]);

  // Key up handler to reset modifier states
  const handleKeyUp = useCallback((event) => {
    activeModifiersRef.current = {
      ctrl: event.ctrlKey || event.metaKey,
      shift: event.shiftKey,
      alt: event.altKey
    };
  }, []);

  // Show shortcuts help modal/toast
  const showShortcutsHelp = useCallback(() => {
    const helpText = `
🎮 Keyboard Shortcuts:

Navigation:
• H - Home/Reset view
• F - Fit to data
• R - Reset view (Ctrl+R)
• + - Zoom in
• - - Zoom out
• 0 - Reset zoom
• Arrow keys - Pan map

Controls:
• L - Toggle legend
• C - Toggle controls
• T - Toggle triggers
• V - Toggle tag visibility
• M - Cycle map mode

Actions:
• Ctrl+Delete - Clear events
• ? or / - Show this help

Note: Shortcuts are disabled when typing in input fields.
    `;

    // Create a simple modal or use browser alert
    if (window.confirm) {
      alert(helpText);
    } else {
      console.log(helpText);
    }
  }, []);

  // Set up event listeners
  useEffect(() => {
    if (!isEnabled) return;

    document.addEventListener('keydown', handleKeyDown);
    document.addEventListener('keyup', handleKeyUp);

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.removeEventListener('keyup', handleKeyUp);
    };
  }, [handleKeyDown, handleKeyUp, isEnabled]);

  // Return useful shortcuts info for display
  const shortcutsInfo = {
    navigation: [
      { key: 'H', description: 'Home/Reset view' },
      { key: 'F', description: 'Fit to data' },
      { key: '+/-', description: 'Zoom in/out' },
      { key: 'Arrows', description: 'Pan map' }
    ],
    controls: [
      { key: 'L', description: 'Toggle legend' },
      { key: 'C', description: 'Toggle controls' },
      { key: 'T', description: 'Toggle triggers' },
      { key: 'V', description: 'Toggle tag visibility' }
    ],
    actions: [
      { key: 'M', description: 'Cycle map mode' },
      { key: 'Ctrl+Del', description: 'Clear events' },
      { key: '?', description: 'Show help' }
    ]
  };

  return {
    shortcutsInfo,
    showShortcutsHelp,
    isEnabled: shortcutsEnabledRef.current
  };
};

export default useKeyboardShortcuts;