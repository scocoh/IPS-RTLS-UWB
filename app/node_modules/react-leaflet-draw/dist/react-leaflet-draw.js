(function webpackUniversalModuleDefinition(root, factory) {
	if(typeof exports === 'object' && typeof module === 'object')
		module.exports = factory(require("leaflet-draw"), require("react"), require("leaflet"));
	else if(typeof define === 'function' && define.amd)
		define(["leaflet-draw", "react", "leaflet"], factory);
	else if(typeof exports === 'object')
		exports["ReactLeaflet"] = factory(require("leaflet-draw"), require("react"), require("leaflet"));
	else
		root["ReactLeaflet"] = factory(root["L"], root["React"], root["L"]);
})(self, (__WEBPACK_EXTERNAL_MODULE__654__, __WEBPACK_EXTERNAL_MODULE__329__, __WEBPACK_EXTERNAL_MODULE__708__) => {
return /******/ (() => { // webpackBootstrap
/******/ 	var __webpack_modules__ = ({

/***/ 704:
/***/ ((module) => {

"use strict";
 // do not edit .js files directly - edit src/index.jst

module.exports = function equal(a, b) {
  if (a === b) return true;

  if (a && b && typeof a == 'object' && typeof b == 'object') {
    if (a.constructor !== b.constructor) return false;
    var length, i, keys;

    if (Array.isArray(a)) {
      length = a.length;
      if (length != b.length) return false;

      for (i = length; i-- !== 0;) if (!equal(a[i], b[i])) return false;

      return true;
    }

    if (a.constructor === RegExp) return a.source === b.source && a.flags === b.flags;
    if (a.valueOf !== Object.prototype.valueOf) return a.valueOf() === b.valueOf();
    if (a.toString !== Object.prototype.toString) return a.toString() === b.toString();
    keys = Object.keys(a);
    length = keys.length;
    if (length !== Object.keys(b).length) return false;

    for (i = length; i-- !== 0;) if (!Object.prototype.hasOwnProperty.call(b, keys[i])) return false;

    for (i = length; i-- !== 0;) {
      var key = keys[i];
      if (!equal(a[key], b[key])) return false;
    }

    return true;
  } // true if both NaN, false otherwise


  return a !== a && b !== b;
};

/***/ }),

/***/ 433:
/***/ ((module, __unused_webpack_exports, __webpack_require__) => {

"use strict";
/**
 * Copyright (c) 2013-present, Facebook, Inc.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */


var ReactPropTypesSecret = __webpack_require__(642);

function emptyFunction() {}

function emptyFunctionWithReset() {}

emptyFunctionWithReset.resetWarningCache = emptyFunction;

module.exports = function () {
  function shim(props, propName, componentName, location, propFullName, secret) {
    if (secret === ReactPropTypesSecret) {
      // It is still safe when called from React.
      return;
    }

    var err = new Error('Calling PropTypes validators directly is not supported by the `prop-types` package. ' + 'Use PropTypes.checkPropTypes() to call them. ' + 'Read more at http://fb.me/use-check-prop-types');
    err.name = 'Invariant Violation';
    throw err;
  }

  ;
  shim.isRequired = shim;

  function getShim() {
    return shim;
  }

  ; // Important!
  // Keep this list in sync with production version in `./factoryWithTypeCheckers.js`.

  var ReactPropTypes = {
    array: shim,
    bigint: shim,
    bool: shim,
    func: shim,
    number: shim,
    object: shim,
    string: shim,
    symbol: shim,
    any: shim,
    arrayOf: getShim,
    element: shim,
    elementType: shim,
    instanceOf: getShim,
    node: shim,
    objectOf: getShim,
    oneOf: getShim,
    oneOfType: getShim,
    shape: getShim,
    exact: getShim,
    checkPropTypes: emptyFunctionWithReset,
    resetWarningCache: emptyFunction
  };
  ReactPropTypes.PropTypes = ReactPropTypes;
  return ReactPropTypes;
};

/***/ }),

/***/ 74:
/***/ ((module, __unused_webpack_exports, __webpack_require__) => {

/**
 * Copyright (c) 2013-present, Facebook, Inc.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
if (false) { var throwOnDirectAccess, ReactIs; } else {
  // By explicitly using `prop-types` you are opting into new production behavior.
  // http://fb.me/prop-types-in-prod
  module.exports = __webpack_require__(433)();
}

/***/ }),

/***/ 642:
/***/ ((module) => {

"use strict";
/**
 * Copyright (c) 2013-present, Facebook, Inc.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */


var ReactPropTypesSecret = 'SECRET_DO_NOT_PASS_THIS_OR_YOU_WILL_BE_FIRED';
module.exports = ReactPropTypesSecret;

/***/ }),

/***/ 708:
/***/ ((module) => {

"use strict";
module.exports = __WEBPACK_EXTERNAL_MODULE__708__;

/***/ }),

/***/ 654:
/***/ ((module) => {

"use strict";
module.exports = __WEBPACK_EXTERNAL_MODULE__654__;

/***/ }),

/***/ 329:
/***/ ((module) => {

"use strict";
module.exports = __WEBPACK_EXTERNAL_MODULE__329__;

/***/ })

/******/ 	});
/************************************************************************/
/******/ 	// The module cache
/******/ 	var __webpack_module_cache__ = {};
/******/ 	
/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {
/******/ 		// Check if module is in cache
/******/ 		var cachedModule = __webpack_module_cache__[moduleId];
/******/ 		if (cachedModule !== undefined) {
/******/ 			return cachedModule.exports;
/******/ 		}
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = __webpack_module_cache__[moduleId] = {
/******/ 			// no module.id needed
/******/ 			// no module.loaded needed
/******/ 			exports: {}
/******/ 		};
/******/ 	
/******/ 		// Execute the module function
/******/ 		__webpack_modules__[moduleId](module, module.exports, __webpack_require__);
/******/ 	
/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}
/******/ 	
/************************************************************************/
/******/ 	/* webpack/runtime/compat get default export */
/******/ 	(() => {
/******/ 		// getDefaultExport function for compatibility with non-harmony modules
/******/ 		__webpack_require__.n = (module) => {
/******/ 			var getter = module && module.__esModule ?
/******/ 				() => (module['default']) :
/******/ 				() => (module);
/******/ 			__webpack_require__.d(getter, { a: getter });
/******/ 			return getter;
/******/ 		};
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/define property getters */
/******/ 	(() => {
/******/ 		// define getter functions for harmony exports
/******/ 		__webpack_require__.d = (exports, definition) => {
/******/ 			for(var key in definition) {
/******/ 				if(__webpack_require__.o(definition, key) && !__webpack_require__.o(exports, key)) {
/******/ 					Object.defineProperty(exports, key, { enumerable: true, get: definition[key] });
/******/ 				}
/******/ 			}
/******/ 		};
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/hasOwnProperty shorthand */
/******/ 	(() => {
/******/ 		__webpack_require__.o = (obj, prop) => (Object.prototype.hasOwnProperty.call(obj, prop))
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/make namespace object */
/******/ 	(() => {
/******/ 		// define __esModule on exports
/******/ 		__webpack_require__.r = (exports) => {
/******/ 			if(typeof Symbol !== 'undefined' && Symbol.toStringTag) {
/******/ 				Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });
/******/ 			}
/******/ 			Object.defineProperty(exports, '__esModule', { value: true });
/******/ 		};
/******/ 	})();
/******/ 	
/************************************************************************/
var __webpack_exports__ = {};
// This entry need to be wrapped in an IIFE because it need to be in strict mode.
(() => {
"use strict";
// ESM COMPAT FLAG
__webpack_require__.r(__webpack_exports__);

// EXPORTS
__webpack_require__.d(__webpack_exports__, {
  "EditControl": () => (/* reexport */ src_EditControl)
});

// EXTERNAL MODULE: ./node_modules/prop-types/index.js
var prop_types = __webpack_require__(74);
// EXTERNAL MODULE: external {"amd":"leaflet-draw","commonjs":"leaflet-draw","commonjs2":"leaflet-draw","root":"L"}
var external_amd_leaflet_draw_commonjs_leaflet_draw_commonjs2_leaflet_draw_root_L_ = __webpack_require__(654);
// EXTERNAL MODULE: ./node_modules/fast-deep-equal/index.js
var fast_deep_equal = __webpack_require__(704);
var fast_deep_equal_default = /*#__PURE__*/__webpack_require__.n(fast_deep_equal);
// EXTERNAL MODULE: external {"amd":"react","commonjs":"react","commonjs2":"react","root":"React"}
var external_amd_react_commonjs_react_commonjs2_react_root_React_ = __webpack_require__(329);
var external_amd_react_commonjs_react_commonjs2_react_root_React_default = /*#__PURE__*/__webpack_require__.n(external_amd_react_commonjs_react_commonjs2_react_root_React_);
;// CONCATENATED MODULE: ./node_modules/@react-leaflet/core/lib/context.js

const CONTEXT_VERSION = 1;
function createLeafletContext(map) {
  return Object.freeze({
    __version: CONTEXT_VERSION,
    map
  });
}
function extendContext(source, extra) {
  return Object.freeze({ ...source,
    ...extra
  });
}
const LeafletContext = (0,external_amd_react_commonjs_react_commonjs2_react_root_React_.createContext)(null);
const LeafletProvider = LeafletContext.Provider;
function useLeafletContext() {
  const context = (0,external_amd_react_commonjs_react_commonjs2_react_root_React_.useContext)(LeafletContext);

  if (context == null) {
    throw new Error('No context provided: useLeafletContext() can only be used in a descendant of <MapContainer>');
  }

  return context;
}
// EXTERNAL MODULE: external {"amd":"leaflet","commonjs":"leaflet","commonjs2":"leaflet","root":"L"}
var external_amd_leaflet_commonjs_leaflet_commonjs2_leaflet_root_L_ = __webpack_require__(708);
var external_amd_leaflet_commonjs_leaflet_commonjs2_leaflet_root_L_default = /*#__PURE__*/__webpack_require__.n(external_amd_leaflet_commonjs_leaflet_commonjs2_leaflet_root_L_);
;// CONCATENATED MODULE: ./src/EditControl.js
function ownKeys(object, enumerableOnly) { var keys = Object.keys(object); if (Object.getOwnPropertySymbols) { var symbols = Object.getOwnPropertySymbols(object); enumerableOnly && (symbols = symbols.filter(function (sym) { return Object.getOwnPropertyDescriptor(object, sym).enumerable; })), keys.push.apply(keys, symbols); } return keys; }

function _objectSpread(target) { for (var i = 1; i < arguments.length; i++) { var source = null != arguments[i] ? arguments[i] : {}; i % 2 ? ownKeys(Object(source), !0).forEach(function (key) { _defineProperty(target, key, source[key]); }) : Object.getOwnPropertyDescriptors ? Object.defineProperties(target, Object.getOwnPropertyDescriptors(source)) : ownKeys(Object(source)).forEach(function (key) { Object.defineProperty(target, key, Object.getOwnPropertyDescriptor(source, key)); }); } return target; }

function _defineProperty(obj, key, value) { if (key in obj) { Object.defineProperty(obj, key, { value: value, enumerable: true, configurable: true, writable: true }); } else { obj[key] = value; } return obj; }


 // eslint-disable-line





var eventHandlers = {
  onEdited: 'draw:edited',
  onDrawStart: 'draw:drawstart',
  onDrawStop: 'draw:drawstop',
  onDrawVertex: 'draw:drawvertex',
  onEditStart: 'draw:editstart',
  onEditMove: 'draw:editmove',
  onEditResize: 'draw:editresize',
  onEditVertex: 'draw:editvertex',
  onEditStop: 'draw:editstop',
  onDeleted: 'draw:deleted',
  onDeleteStart: 'draw:deletestart',
  onDeleteStop: 'draw:deletestop'
};

function EditControl(props) {
  var context = useLeafletContext();
  var drawRef = (0,external_amd_react_commonjs_react_commonjs2_react_root_React_.useRef)();
  var propsRef = (0,external_amd_react_commonjs_react_commonjs2_react_root_React_.useRef)(props);

  var onDrawCreate = function onDrawCreate(e) {
    var onCreated = props.onCreated;
    var container = context.layerContainer || context.map;
    container.addLayer(e.layer);
    onCreated && onCreated(e);
  };

  external_amd_react_commonjs_react_commonjs2_react_root_React_default().useEffect(function () {
    var map = context.map;
    var onMounted = props.onMounted;

    for (var key in eventHandlers) {
      map.on(eventHandlers[key], function (evt) {
        var handlers = Object.keys(eventHandlers).filter(function (handler) {
          return eventHandlers[handler] === evt.type;
        });

        if (handlers.length === 1) {
          var handler = handlers[0];
          props[handler] && props[handler](evt);
        }
      });
    }

    map.on((external_amd_leaflet_commonjs_leaflet_commonjs2_leaflet_root_L_default()).Draw.Event.CREATED, onDrawCreate);
    drawRef.current = createDrawElement(props, context);
    map.addControl(drawRef.current);
    onMounted && onMounted(drawRef.current);
    return function () {
      map.off((external_amd_leaflet_commonjs_leaflet_commonjs2_leaflet_root_L_default()).Draw.Event.CREATED, onDrawCreate);

      for (var _key in eventHandlers) {
        if (props[_key]) {
          map.off(eventHandlers[_key], props[_key]);
        }
      }

      drawRef.current.remove(map);
    };
  }, [props.onCreated, props.onDeleted, props.onEdited]);
  external_amd_react_commonjs_react_commonjs2_react_root_React_default().useEffect(function () {
    if (fast_deep_equal_default()(props.draw, propsRef.current.draw) && fast_deep_equal_default()(props.edit, propsRef.current.edit) && props.position === propsRef.current.position) {
      return;
    }

    var map = context.map;
    drawRef.current.remove(map);
    drawRef.current = createDrawElement(props, context);
    drawRef.current.addTo(map);
    var onMounted = props.onMounted;
    onMounted && onMounted(drawRef.current);
    return function () {
      drawRef.current.remove(map);
    };
  }, [props.draw, props.edit, props.position, props.onCreated, props.onDeleted, props.onEdited]);
  return null;
}

function createDrawElement(props, context) {
  var layerContainer = context.layerContainer;
  var draw = props.draw,
      edit = props.edit,
      position = props.position;
  var options = {
    edit: _objectSpread(_objectSpread({}, edit), {}, {
      featureGroup: layerContainer
    })
  };

  if (draw) {
    options.draw = _objectSpread({}, draw);
  }

  if (position) {
    options.position = position;
  }

  return new external_amd_leaflet_commonjs_leaflet_commonjs2_leaflet_root_L_.Control.Draw(options);
}

EditControl.propTypes = _objectSpread(_objectSpread({}, Object.keys(eventHandlers).reduce(function (acc, val) {
  acc[val] = prop_types.PropTypes.func;
  return acc;
}, {})), {}, {
  onCreated: prop_types.PropTypes.func,
  onMounted: prop_types.PropTypes.func,
  draw: prop_types.PropTypes.shape({
    polyline: prop_types.PropTypes.oneOfType([prop_types.PropTypes.object, prop_types.PropTypes.bool]),
    polygon: prop_types.PropTypes.oneOfType([prop_types.PropTypes.object, prop_types.PropTypes.bool]),
    rectangle: prop_types.PropTypes.oneOfType([prop_types.PropTypes.object, prop_types.PropTypes.bool]),
    circle: prop_types.PropTypes.oneOfType([prop_types.PropTypes.object, prop_types.PropTypes.bool]),
    marker: prop_types.PropTypes.oneOfType([prop_types.PropTypes.object, prop_types.PropTypes.bool])
  }),
  edit: prop_types.PropTypes.shape({
    edit: prop_types.PropTypes.oneOfType([prop_types.PropTypes.object, prop_types.PropTypes.bool]),
    remove: prop_types.PropTypes.oneOfType([prop_types.PropTypes.object, prop_types.PropTypes.bool]),
    poly: prop_types.PropTypes.oneOfType([prop_types.PropTypes.object, prop_types.PropTypes.bool]),
    allowIntersection: prop_types.PropTypes.bool
  }),
  position: prop_types.PropTypes.oneOf(['topright', 'topleft', 'bottomright', 'bottomleft']),
  leaflet: prop_types.PropTypes.shape({
    map: prop_types.PropTypes.instanceOf(external_amd_leaflet_commonjs_leaflet_commonjs2_leaflet_root_L_.Map),
    layerContainer: prop_types.PropTypes.shape({
      addLayer: prop_types.PropTypes.func.isRequired,
      removeLayer: prop_types.PropTypes.func.isRequired
    })
  })
});
/* harmony default export */ const src_EditControl = (EditControl);
;// CONCATENATED MODULE: ./src/index.js

})();

/******/ 	return __webpack_exports__;
/******/ })()
;
});