/* Name: colorUtils.js */
/* Version: 0.1.0 */
/* Created: 250719 */
/* Modified: 250719 */
/* Creator: ParcoAdmin + Claude */
/* Modified By: ParcoAdmin + Claude */
/* Description: Color utilities for 3D zone visualization */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/ThreeDZoneViewer/utils */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

/**
 * Zone type color mappings based on ParcoRTLS hierarchy
 */
export const ZONE_TYPE_COLORS = {
  // Primary zone types
  1: '#ff0000',   // Campus L1 - Red (highest level)
  2: '#00aa00',   // Building L3 - Green
  3: '#0066ff',   // Floor L4 - Blue
  4: '#ff6600',   // Wing L5 - Orange
  5: '#9900ff',   // Room L6 - Purple (lowest level)
  
  // Special zone types
  10: '#ff8800',  // Building Outside L2 - Light Orange
  20: '#888888',  // Outdoor General - Gray
  901: '#ffdd00', // Virtual Subject Zone - Yellow
  
  // Additional types (for extensibility)
  6: '#ff3399',   // ODataProximity - Pink
  7: '#33ff99',   // PDataProximity - Cyan
  9: '#9933ff'    // Demo Zone Type - Light Purple
};

/**
 * Alternative color schemes
 */
export const COLOR_SCHEMES = {
  default: ZONE_TYPE_COLORS,
  
  // Bright scheme
  bright: {
    1: '#ff0033',
    2: '#00ff33', 
    3: '#3300ff',
    4: '#ff9900',
    5: '#cc00ff',
    10: '#ff6633',
    20: '#666666',
    901: '#ffff00'
  },
  
  // Pastel scheme
  pastel: {
    1: '#ffb3ba',
    2: '#baffc9',
    3: '#bae1ff',
    4: '#ffffba',
    5: '#ffdfba',
    10: '#e0b3ff',
    20: '#d4d4d4',
    901: '#fff2b3'
  },
  
  // Monochrome scheme
  monochrome: {
    1: '#2c2c2c',
    2: '#404040',
    3: '#555555',
    4: '#6a6a6a',
    5: '#7f7f7f',
    10: '#949494',
    20: '#a9a9a9',
    901: '#bebebe'
  },
  
  // High contrast scheme
  highContrast: {
    1: '#000000',
    2: '#ffffff',
    3: '#ff0000',
    4: '#00ff00',
    5: '#0000ff',
    10: '#ffff00',
    20: '#ff00ff',
    901: '#00ffff'
  }
};

/**
 * Get color for zone type
 */
export const getZoneTypeColor = (zoneType, scheme = 'default') => {
  const colors = COLOR_SCHEMES[scheme] || COLOR_SCHEMES.default;
  return colors[zoneType] || '#666666';
};

/**
 * Get color as Three.js hex number
 */
export const getZoneTypeColorHex = (zoneType, scheme = 'default') => {
  const colorStr = getZoneTypeColor(zoneType, scheme);
  return parseInt(colorStr.replace('#', '0x'));
};

/**
 * Convert hex color to RGB
 */
export const hexToRgb = (hex) => {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return result ? {
    r: parseInt(result[1], 16),
    g: parseInt(result[2], 16),
    b: parseInt(result[3], 16)
  } : null;
};

/**
 * Convert RGB to hex
 */
export const rgbToHex = (r, g, b) => {
  return "#" + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1);
};

/**
 * Convert hex color to HSL
 */
export const hexToHsl = (hex) => {
  const rgb = hexToRgb(hex);
  if (!rgb) return null;
  
  const r = rgb.r / 255;
  const g = rgb.g / 255;
  const b = rgb.b / 255;
  
  const max = Math.max(r, g, b);
  const min = Math.min(r, g, b);
  let h, s, l = (max + min) / 2;
  
  if (max === min) {
    h = s = 0; // achromatic
  } else {
    const d = max - min;
    s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
    switch (max) {
      case r: h = (g - b) / d + (g < b ? 6 : 0); break;
      case g: h = (b - r) / d + 2; break;
      case b: h = (r - g) / d + 4; break;
    }
    h /= 6;
  }
  
  return {
    h: Math.round(h * 360),
    s: Math.round(s * 100),
    l: Math.round(l * 100)
  };
};

/**
 * Lighten a color by percentage
 */
export const lightenColor = (hex, percent) => {
  const hsl = hexToHsl(hex);
  if (!hsl) return hex;
  
  hsl.l = Math.min(100, hsl.l + percent);
  return hslToHex(hsl.h, hsl.s, hsl.l);
};

/**
 * Darken a color by percentage
 */
export const darkenColor = (hex, percent) => {
  const hsl = hexToHsl(hex);
  if (!hsl) return hex;
  
  hsl.l = Math.max(0, hsl.l - percent);
  return hslToHex(hsl.h, hsl.s, hsl.l);
};

/**
 * Convert HSL to hex
 */
export const hslToHex = (h, s, l) => {
  h /= 360;
  s /= 100;
  l /= 100;
  
  const hue2rgb = (p, q, t) => {
    if (t < 0) t += 1;
    if (t > 1) t -= 1;
    if (t < 1/6) return p + (q - p) * 6 * t;
    if (t < 1/2) return q;
    if (t < 2/3) return p + (q - p) * (2/3 - t) * 6;
    return p;
  };
  
  let r, g, b;
  
  if (s === 0) {
    r = g = b = l; // achromatic
  } else {
    const q = l < 0.5 ? l * (1 + s) : l + s - l * s;
    const p = 2 * l - q;
    r = hue2rgb(p, q, h + 1/3);
    g = hue2rgb(p, q, h);
    b = hue2rgb(p, q, h - 1/3);
  }
  
  return rgbToHex(
    Math.round(r * 255),
    Math.round(g * 255),
    Math.round(b * 255)
  );
};

/**
 * Generate zone type gradient
 */
export const getZoneTypeGradient = (zoneType, steps = 5) => {
  const baseColor = getZoneTypeColor(zoneType);
  const gradient = [];
  
  for (let i = 0; i < steps; i++) {
    const percent = (i / (steps - 1)) * 40 - 20; // -20% to +20%
    const color = percent < 0 
      ? darkenColor(baseColor, Math.abs(percent))
      : lightenColor(baseColor, percent);
    gradient.push(color);
  }
  
  return gradient;
};

/**
 * Get contrasting text color for background
 */
export const getContrastColor = (backgroundColor) => {
  const rgb = hexToRgb(backgroundColor);
  if (!rgb) return '#000000';
  
  // Calculate luminance
  const luminance = (0.299 * rgb.r + 0.587 * rgb.g + 0.114 * rgb.b) / 255;
  
  return luminance > 0.5 ? '#000000' : '#ffffff';
};

/**
 * Generate color palette for multiple zones
 */
export const generateZonePalette = (zoneTypes, scheme = 'default') => {
  const palette = {};
  
  zoneTypes.forEach(zoneType => {
    palette[zoneType] = {
      primary: getZoneTypeColor(zoneType, scheme),
      hex: getZoneTypeColorHex(zoneType, scheme),
      light: lightenColor(getZoneTypeColor(zoneType, scheme), 20),
      dark: darkenColor(getZoneTypeColor(zoneType, scheme), 20),
      contrast: getContrastColor(getZoneTypeColor(zoneType, scheme))
    };
  });
  
  return palette;
};

/**
 * Zone type labels
 */
export const ZONE_TYPE_LABELS = {
  1: 'Campus L1',
  2: 'Building L3',
  3: 'Floor L4',
  4: 'Wing L5',
  5: 'Room L6',
  6: 'ODataProximity',
  7: 'PDataProximity',
  9: 'Demo Zone Type',
  10: 'Building Outside L2',
  20: 'Outdoor General',
  901: 'Virtual Subject Zone'
};

/**
 * Get zone type label
 */
export const getZoneTypeLabel = (zoneType) => {
  return ZONE_TYPE_LABELS[zoneType] || `Zone Type ${zoneType}`;
};

/**
 * Zone type icons/emojis
 */
export const ZONE_TYPE_ICONS = {
  1: '🏫',   // Campus
  2: '🏢',   // Building
  3: '🏬',   // Floor
  4: '🏠',   // Wing
  5: '🚪',   // Room
  6: '📡',   // ODataProximity
  7: '📊',   // PDataProximity
  9: '🧪',   // Demo Zone
  10: '🏗️',  // Building Outside
  20: '🌳',  // Outdoor
  901: '👤'  // Virtual Subject
};

/**
 * Get zone type icon
 */
export const getZoneTypeIcon = (zoneType) => {
  return ZONE_TYPE_ICONS[zoneType] || '📍';
};

/**
 * Color accessibility utilities
 */
export const colorAccessibility = {
  /**
   * Check if color contrast meets WCAG AA standards
   */
  meetsContrastStandard: (foreground, background, standard = 'AA') => {
    const ratio = colorAccessibility.getContrastRatio(foreground, background);
    const threshold = standard === 'AAA' ? 7 : 4.5;
    return ratio >= threshold;
  },
  
  /**
   * Calculate contrast ratio between two colors
   */
  getContrastRatio: (color1, color2) => {
    const lum1 = colorAccessibility.getLuminance(color1);
    const lum2 = colorAccessibility.getLuminance(color2);
    const lightest = Math.max(lum1, lum2);
    const darkest = Math.min(lum1, lum2);
    return (lightest + 0.05) / (darkest + 0.05);
  },
  
  /**
   * Calculate relative luminance
   */
  getLuminance: (hex) => {
    const rgb = hexToRgb(hex);
    if (!rgb) return 0;
    
    const rsRGB = rgb.r / 255;
    const gsRGB = rgb.g / 255;
    const bsRGB = rgb.b / 255;
    
    const r = rsRGB <= 0.03928 ? rsRGB / 12.92 : Math.pow((rsRGB + 0.055) / 1.055, 2.4);
    const g = gsRGB <= 0.03928 ? gsRGB / 12.92 : Math.pow((gsRGB + 0.055) / 1.055, 2.4);
    const b = bsRGB <= 0.03928 ? bsRGB / 12.92 : Math.pow((bsRGB + 0.055) / 1.055, 2.4);
    
    return 0.2126 * r + 0.7152 * g + 0.0722 * b;
  }
};

export default {
  ZONE_TYPE_COLORS,
  COLOR_SCHEMES,
  getZoneTypeColor,
  getZoneTypeColorHex,
  getZoneTypeLabel,
  getZoneTypeIcon,
  hexToRgb,
  rgbToHex,
  hexToHsl,
  hslToHex,
  lightenColor,
  darkenColor,
  getContrastColor,
  generateZonePalette,
  colorAccessibility
};