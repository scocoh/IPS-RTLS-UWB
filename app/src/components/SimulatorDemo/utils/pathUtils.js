/* Name: pathUtils.js */
/* Version: 0.1.0 */
/* Created: 971201 */
/* Modified: 250502 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin */
/* Description: ParcoRTLS frontend script */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/SimulatorDemo/utils */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

// pathUtils.js
// Version: 0.4.0
// Description: Uses speed (ft/s) to interpolate path over real-world time

export function interpolatePath(positions, elapsed, speedFps = 5.0) {
  if (!positions || positions.length < 2 || speedFps <= 0) {
    return {
      x: positions?.[0]?.x || 0,
      y: positions?.[0]?.y || 0,
      z: positions?.[0]?.z || 0,
      debug: {
        segmentIndex: 0,
        t: 0,
        elapsed,
        dx: 0,
        dy: 0,
        distance: 0,
        from: { x: 0, y: 0, z: 0 },
        to: { x: 0, y: 0, z: 0 }
      }
    };
  }

  const distances = [];
  let totalDistance = 0;

  for (let i = 0; i < positions.length - 1; i++) {
    const dx = positions[i+1].x - positions[i].x;
    const dy = positions[i+1].y - positions[i].y;
    const dist = Math.sqrt(dx*dx + dy*dy);
    distances.push(dist);
    totalDistance += dist;
  }

  const totalTime = totalDistance / speedFps;
  let timeRemaining = elapsed % totalTime;

  let segmentIndex = 0;
  while (segmentIndex < distances.length) {
    const segTime = distances[segmentIndex] / speedFps;
    if (timeRemaining < segTime) break;
    timeRemaining -= segTime;
    segmentIndex++;
  }

  const start = positions[segmentIndex] || positions[positions.length - 2];
  const end = positions[segmentIndex + 1] || positions[positions.length - 1];
  const segDist = distances[segmentIndex] || 1;
  const t = segDist > 0 ? (timeRemaining * speedFps / segDist) : 0;

  const x = start.x + (end.x - start.x) * t;
  const y = start.y + (end.y - start.y) * t;
  const z = start.z + (end.z - start.z) * t;

  const debug = {
    segmentIndex,
    t: +t.toFixed(3),
    elapsed: +elapsed.toFixed(1),
    from: start,
    to: end,
    segDist: +segDist.toFixed(2),
    totalDistance: +totalDistance.toFixed(2),
    totalTime: +totalTime.toFixed(2),
    speedFps
  };

  console.log("🟦 interpolatePath() w/ speed", debug);

  return { x, y, z, debug };
}
