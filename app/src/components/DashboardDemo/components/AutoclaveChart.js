/* Name: AutoclaveChart.js */
/* Version: 0.1.0 */
/* Created: 250711 */
/* Modified: 250711 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin + Claude */
/* Description: Autoclave chart component for dashboard */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/DashboardDemo/components */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

import React from 'react';

const AutoclaveChart = ({ autoclaveData = [], isLoading = false }) => {
  // Helper function to get month name
  const getMonthName = (dateString) => {
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', { month: 'short' });
    } catch (error) {
      return 'Unknown';
    }
  };

  // Calculate max value for chart scaling
  const maxValue = autoclaveData.length > 0 
    ? Math.max(...autoclaveData.map(item => item.cycle_count))
    : 200;

  // Chart bar height calculation
  const getBarHeight = (value) => {
    if (maxValue === 0) return 0;
    return Math.max((value / maxValue) * 100, 2); // Minimum 2% height for visibility
  };

  // Current date for highlighting current month
  const currentMonth = new Date().getMonth();

  // Summary calculations
  const thisYear = autoclaveData.reduce((sum, item) => sum + item.cycle_count, 0);
  const thisMonth = autoclaveData.find(item => {
    const itemDate = new Date(item.cycle_date);
    return itemDate.getMonth() === currentMonth;
  })?.cycle_count || 0;

  const today = 0; // Would need daily data for this

  if (isLoading) {
    return (
      <div className="chart-container">
        <div className="chart-header">
          <h2 className="chart-title">Autoclave Cycle Counts</h2>
        </div>
        <div className="chart-placeholder">
          <div className="loading-spinner"></div>
          <p>Loading autoclave data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="chart-container">
      <div className="chart-header">
        <h2 className="chart-title">Autoclave Cycle Counts</h2>
        <div className="chart-subtitle">
          <a href="#view-cycles" className="chart-link">
            View autoclave cycles by date
          </a>
        </div>
      </div>

      {autoclaveData.length > 0 ? (
        <>
          {/* Bar Chart */}
          <div className="autoclave-chart">
            <div className="chart-y-axis">
              <div className="y-axis-label">{maxValue}</div>
              <div className="y-axis-label">{Math.floor(maxValue * 0.75)}</div>
              <div className="y-axis-label">{Math.floor(maxValue * 0.5)}</div>
              <div className="y-axis-label">{Math.floor(maxValue * 0.25)}</div>
              <div className="y-axis-label">0</div>
            </div>
            
            <div className="chart-bars">
              {autoclaveData.map((item, index) => {
                const itemDate = new Date(item.cycle_date);
                const isCurrentMonth = itemDate.getMonth() === currentMonth;
                
                return (
                  <div key={index} className="chart-bar-container">
                    <div 
                      className={`chart-bar ${isCurrentMonth ? 'current-month' : ''}`}
                      style={{ height: `${getBarHeight(item.cycle_count)}%` }}
                      title={`${getMonthName(item.cycle_date)}: ${item.cycle_count} cycles`}
                    >
                      <div className="bar-value">{item.cycle_count}</div>
                    </div>
                    <div className="chart-x-label">
                      {getMonthName(item.cycle_date)}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Summary Stats */}
          <div className="autoclave-summary">
            <div className="summary-item">
              <div className="summary-value">{today}</div>
              <div className="summary-label">Today (-100%)</div>
            </div>
            <div className="summary-item">
              <div className="summary-value">{thisMonth}</div>
              <div className="summary-label">This Month (-77%)</div>
            </div>
            <div className="summary-item">
              <div className="summary-value">{thisYear}</div>
              <div className="summary-label">This Year (223%)</div>
            </div>
          </div>
        </>
      ) : (
        <div className="chart-placeholder">
          <p>No autoclave data available</p>
          <small>Autoclave cycle data will appear here when available.</small>
        </div>
      )}
    </div>
  );
};

export default AutoclaveChart;