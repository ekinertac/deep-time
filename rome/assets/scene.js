/*
 * scene.js: the WebGL city. Optional, decorative in the sense that it carries no
 * text, and load-bearing in the sense that it is the argument in a picture.
 *
 * What it draws, all of it inside the same 13.7 km² the Aurelian Walls enclose:
 *   - a field of instanced blocks whose COUNT tracks the cited population, at a
 *     fixed exchange rate of roughly 300 people per block, so the city visibly
 *     empties from imperial density to a huddle of a few dozen blocks in the 14th
 *     century and then overflows the wall in the 20th;
 *   - where those blocks sit: scattered across the whole walled area in late
 *     antiquity, contracting into the Tiber bend from the 11th century, which is
 *     the abitato/disabitato pattern (Dey 2021 revising Krautheimer);
 *   - the wall itself, which does not exist before 271 and rises when the 3rd
 *     century arrives;
 *   - eight monuments that never disappear, because they did not.
 *
 * It reads window.RomeState.t (a continuous century coordinate, 0..19) published
 * by page.js and interpolates every block between the two neighbouring centuries.
 * Nothing else in the page depends on this file. If WebGL is missing, the module
 * throws on context creation, the canvas keeps opacity 0, and the page is unharmed.
 *
 * Read alongside: page.js (publishes RomeState), data.js (pop / cluster / spill).
 */

import * as THREE from './vendor/three.module.min.js';

const canvas = document.getElementById('city');
const state = window.RomeState || { t: 0, reduced: false };
const REDUCED = state.reduced;

/* ---------- the plan ----------
 * A diagram of the Aurelian circuit and the Tiber, not a survey. Units are
 * roughly kilometres: the real circuit is about 19 km long and encloses 13.7 km².
 */
const WALL = [
  [-0.30, 2.55], [0.62, 2.34], [1.32, 1.90], [1.83, 1.18], [2.10, 0.40],
  [2.02, -0.52], [1.60, -1.32], [0.92, -1.92], [0.00, -2.28], [-0.92, -2.26],
  [-1.62, -1.88], [-2.10, -1.20], [-2.30, -0.38], [-2.20, 0.52], [-1.88, 1.30],
  [-1.40, 2.02], [-0.92, 2.46]
];
const TIBER = [
  [-0.55, 2.70], [-0.42, 1.95], [-0.78, 1.30], [-1.28, 0.92], [-1.44, 0.30],
  [-1.16, -0.22], [-1.06, -0.88], [-1.30, -1.55], [-1.42, -2.45]
];
/* The bend, which is where the medieval city actually lived. */
const ABITATO = [-1.02, 0.72];

const MONUMENTS = [
  { p: [0.42, -0.28], r: 0.095, h: 0.17, round: true },   // Colosseum
  { p: [-0.62, 0.35], r: 0.055, h: 0.12, round: true },   // Pantheon
  { p: [-1.16, 1.28], r: 0.055, h: 0.15, round: true },   // Mausoleum of Hadrian
  { p: [0.04, -0.44], r: 0.085, h: 0.07, round: false },  // the Forum
  { p: [-1.70, 1.40], r: 0.085, h: 0.19, round: false },  // St Peter's
  { p: [0.70, 0.84], r: 0.075, h: 0.10, round: false },   // Baths of Diocletian
  { p: [1.26, -1.00], r: 0.07, h: 0.09, round: false },   // Baths of Caracalla
  { p: [-0.30, -1.06], r: 0.13, h: 0.045, round: false }  // Circus Maximus
];

const PER_BLOCK = 320;      // people per block, held constant across all centuries
const MAX_BLOCKS = 9000;

/* ---------- geometry helpers ---------- */
function inPoly(x, y, poly) {
  let hit = false;
  for (let i = 0, j = poly.length - 1; i < poly.length; j = i++) {
    const [xi, yi] = poly[i], [xj, yj] = poly[j];
    if ((yi > y) !== (yj > y) && x < ((xj - xi) * (y - yi)) / (yj - yi) + xi) hit = !hit;
  }
  return hit;
}
function distToPath(x, y, path) {
  let best = Infinity;
  for (let i = 0; i < path.length - 1; i++) {
    const [ax, ay] = path[i], [bx, by] = path[i + 1];
    const dx = bx - ax, dy = by - ay;
    const t = Math.max(0, Math.min(1, ((x - ax) * dx + (y - ay) * dy) / (dx * dx + dy * dy)));
    const px = ax + t * dx, py = ay + t * dy;
    best = Math.min(best, Math.hypot(x - px, y - py));
  }
  return best;
}

/* Deterministic noise so the city is the same on every load. */
let seed = 20240605;
function rnd() { seed = (seed * 1664525 + 1013904223) % 4294967296; return seed / 4294967296; }

/* ---------- block field ----------
 * Every block gets a position, and two orderings: sA by distance from the Tiber
 * bend (the medieval contraction) and sB uniform (the late-antique scatter). Each
 * century blends them by its `cluster` value, and the visibility of every block in
 * every century is baked once at load, so the frame loop only interpolates.
 */
const blocks = [];
for (let guard = 0; guard < 400000 && blocks.length < MAX_BLOCKS; guard++) {
  const x = (rnd() - 0.5) * 9.4, y = (rnd() - 0.5) * 9.4;
  const inside = inPoly(x, y, WALL);
  if (distToPath(x, y, TIBER) < 0.12) continue;               // don't build in the river
  if (!inside && Math.hypot(x, y) > 4.6) continue;            // outer ring only so far
  blocks.push({
    x, y, inside,
    h: 0.045 + rnd() * rnd() * 0.16,
    w: 0.05 + rnd() * 0.055,
    rot: rnd() * Math.PI,
    tint: rnd(),
    dCentre: Math.hypot(x - ABITATO[0], y - ABITATO[1]) + rnd() * 0.55,
    dOut: Math.hypot(x, y) + rnd() * 0.8,
    u: rnd()
  });
}
const inner = blocks.filter(b => b.inside);
const outer = blocks.filter(b => !b.inside);

/* rank 0..1 in each ordering */
function rankBy(list, key, prop) {
  const s = list.slice().sort((a, b) => a[key] - b[key]);
  s.forEach((b, i) => { b[prop] = i / (s.length - 1 || 1); });
}
rankBy(inner, 'dCentre', 'sA');
rankBy(inner, 'u', 'sB');
rankBy(outer, 'dOut', 'sO');

/* Bake visibility per century. */
blocks.forEach(b => { b.vis = new Float32Array(20); });
CENTURIES.forEach((c, ci) => {
  const total = Math.min(MAX_BLOCKS, Math.round(Math.sqrt(c.pop[0] * c.pop[1]) / PER_BLOCK));
  const nOut = Math.round(total * (c.spill || 0));
  const nIn = Math.min(inner.length, total - nOut);
  const k = c.cluster;
  const scored = inner.map(b => ({ b, s: b.sA * k + b.sB * (1 - k) })).sort((p, q) => p.s - q.s);
  for (let i = 0; i < nIn; i++) scored[i].b.vis[ci] = 1;
  const outSorted = outer.slice().sort((p, q) => p.sO - q.sO);
  for (let i = 0; i < Math.min(outer.length, nOut); i++) outSorted[i].vis[ci] = 1;
});

/* ---------- three.js ---------- */
let renderer;
try {
  renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true, powerPreference: 'high-performance' });
} catch (e) {
  console.warn('rome: no WebGL, running without the city.', e);
  throw e;
}
renderer.setPixelRatio(Math.min(devicePixelRatio, 1.85));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;

const scene = new THREE.Scene();
/* Fog colour is picked to match the page's soil gradient, so the far edge of the
   ground dissolves into the background instead of drawing a horizon line. */
scene.fog = new THREE.Fog(0x120d09, 5.5, 15.0);

const camera = new THREE.PerspectiveCamera(34, 1, 0.5, 60);

/* Light: one low warm sun raking across the plan, one cold fill from the sky, the
   look of a site model photographed late in the day. */
const sun = new THREE.DirectionalLight(0xffd2a0, 3.1);
sun.position.set(-5.6, 2.5, 3.0);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
const sc = sun.shadow.camera;
sc.left = -5.2; sc.right = 5.2; sc.top = 5.2; sc.bottom = -5.2; sc.near = 0.5; sc.far = 20;
sun.shadow.bias = -0.0012;
scene.add(sun);
scene.add(new THREE.HemisphereLight(0x7c93a6, 0x1a1109, 1.15));

/* ground */
const groundTex = (() => {
  const c = document.createElement('canvas'); c.width = c.height = 512;
  const g = c.getContext('2d');
  const grad = g.createRadialGradient(256, 256, 40, 256, 256, 256);
  grad.addColorStop(0, '#2a1f14'); grad.addColorStop(0.55, '#1b140d'); grad.addColorStop(1, '#0b0806');
  g.fillStyle = grad; g.fillRect(0, 0, 512, 512);
  for (let i = 0; i < 26000; i++) {
    g.fillStyle = 'rgba(' + (180 + Math.random() * 60 | 0) + ',150,110,' + (Math.random() * 0.05) + ')';
    g.fillRect(Math.random() * 512, Math.random() * 512, 1.6, 1.6);
  }
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
})();
const ground = new THREE.Mesh(
  new THREE.CircleGeometry(26, 96),
  new THREE.MeshStandardMaterial({ map: groundTex, roughness: 1, metalness: 0 })
);
ground.rotation.x = -Math.PI / 2;
ground.receiveShadow = true;
scene.add(ground);

/* river */
(function river() {
  const pts = TIBER.map(p => new THREE.Vector2(p[0], p[1]));
  const curve = new THREE.SplineCurve(pts);
  const s = curve.getPoints(90);
  const shape = new THREE.Shape();
  const W = 0.085;
  const side = (i, sign) => {
    const a = s[Math.max(0, i - 1)], b = s[Math.min(s.length - 1, i + 1)];
    const dx = b.x - a.x, dy = b.y - a.y, l = Math.hypot(dx, dy) || 1;
    return new THREE.Vector2(s[i].x + sign * (-dy / l) * W, s[i].y + sign * (dx / l) * W);
  };
  const left = s.map((_, i) => side(i, 1)), right = s.map((_, i) => side(i, -1)).reverse();
  shape.setFromPoints(left.concat(right));
  const geo = new THREE.ShapeGeometry(shape);
  const mesh = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({
    color: 0x1d3330, roughness: 0.24, metalness: 0.35, emissive: 0x0a1614
  }));
  mesh.rotation.x = -Math.PI / 2;
  mesh.position.y = 0.012;
  scene.add(mesh);
})();

/* blocks */
const blockGeo = new THREE.BoxGeometry(1, 1, 1);
blockGeo.translate(0, 0.5, 0);
/* No vertexColors here: the per-instance tint rides on instanceColor, which three
   compiles in separately. Turning vertexColors on without a geometry colour
   attribute renders every block black. */
const blockMat = new THREE.MeshStandardMaterial({ roughness: 0.84, metalness: 0.02 });
const blockMesh = new THREE.InstancedMesh(blockGeo, blockMat, blocks.length);
blockMesh.castShadow = true;
blockMesh.receiveShadow = true;
blockMesh.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
scene.add(blockMesh);

const cA = new THREE.Color(0x8a6f52), cB = new THREE.Color(0xc0a07c);
const tmp = new THREE.Color();
blocks.forEach((b, i) => {
  tmp.copy(cA).lerp(cB, b.tint).multiplyScalar(0.8 + b.u * 0.35);
  blockMesh.setColorAt(i, tmp);
});
blockMesh.instanceColor.needsUpdate = true;

/* monuments: always standing, whatever the population does */
const monMat = new THREE.MeshStandardMaterial({ color: 0xbfb094, roughness: 0.82 });
MONUMENTS.forEach(m => {
  const g = m.round
    ? new THREE.CylinderGeometry(m.r, m.r * 1.05, m.h, 24)
    : new THREE.BoxGeometry(m.r * 2, m.h, m.r * 1.5);
  const mesh = new THREE.Mesh(g, monMat);
  mesh.position.set(m.p[0], m.h / 2, m.p[1]);
  mesh.castShadow = true; mesh.receiveShadow = true;
  scene.add(mesh);
});

/* wall: one instanced box per segment, raised when the 3rd century arrives */
const wallGeo = new THREE.BoxGeometry(1, 1, 1);
wallGeo.translate(0, 0.5, 0);
/* Resampled along a closed spline: the real circuit curves, and a 17-gon reads as
   a stockade rather than a wall. */
const WALL_SMOOTH = (function () {
  const curve = new THREE.CatmullRomCurve3(
    WALL.map(p => new THREE.Vector3(p[0], 0, p[1])), true, 'catmullrom', 0.4
  );
  return curve.getPoints(96).map(v => [v.x, v.z]);
})();
const wallSegs = [];
for (let i = 0; i < WALL_SMOOTH.length; i++) {
  const a = WALL_SMOOTH[i], b = WALL_SMOOTH[(i + 1) % WALL_SMOOTH.length];
  const dx = b[0] - a[0], dy = b[1] - a[1];
  wallSegs.push({ x: (a[0] + b[0]) / 2, z: (a[1] + b[1]) / 2, len: Math.hypot(dx, dy), rot: -Math.atan2(dy, dx) });
}
const wallMesh = new THREE.InstancedMesh(
  wallGeo,
  new THREE.MeshStandardMaterial({ color: 0x8a7159, roughness: 0.9 }),
  wallSegs.length
);
wallMesh.castShadow = true; wallMesh.receiveShadow = true;
wallMesh.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
scene.add(wallMesh);

/* ---------- frame loop ---------- */
const M = new THREE.Matrix4(), Q = new THREE.Quaternion();
const POS = new THREE.Vector3(), SCL = new THREE.Vector3(), EUL = new THREE.Euler();
const ZERO = new THREE.Vector3(0, 0, 0), ONE = new THREE.Vector3(0.0001, 0.0001, 0.0001);

let shown = new Float32Array(blocks.length);   // eased per-block presence
let wallUp = 0, smoothT = 0, started = performance.now();
let mx = 0, my = 0, tmx = 0, tmy = 0;

addEventListener('pointermove', e => {
  tmx = (e.clientX / innerWidth - 0.5);
  tmy = (e.clientY / innerHeight - 0.5);
}, { passive: true });

/* The reading column sits left on the gate and right through the descent, so the
   model slides to the opposite side. RomeState.hero is 1 on the gate, 0 below it. */
let offsetNow = -0.14;
function applyOffset() {
  const w = innerWidth, h = innerHeight;
  if (w > 900) camera.setViewOffset(w * 1.3, h, w * offsetNow, 0, w, h);
  else camera.clearViewOffset();
  camera.updateProjectionMatrix();
}

function resize() {
  const w = innerWidth, h = innerHeight;
  renderer.setSize(w, h, false);
  camera.aspect = w / h;
  /* Push the model left of centre on wide screens, where the reading column sits
     on the right. Below 900px the column is full width and the model is centred. */
  applyOffset();
}
addEventListener('resize', resize);
resize();

function frame(now) {
  requestAnimationFrame(frame);

  const target = Math.max(0, Math.min(19, state.t || 0));
  smoothT += (target - smoothT) * (REDUCED ? 1 : 0.075);
  const i0 = Math.min(18, Math.floor(smoothT)), f = smoothT - i0;

  /* intro: the field settles in over the first second and a half */
  const intro = REDUCED ? 1 : Math.min(1, (now - started) / 1600);
  const ease = intro * intro * (3 - 2 * intro);

  /* blocks */
  for (let i = 0; i < blocks.length; i++) {
    const b = blocks[i];
    const want = b.vis[i0] * (1 - f) + b.vis[i0 + 1] * f;
    shown[i] += (want - shown[i]) * (REDUCED ? 1 : 0.12);
    const s = shown[i] * ease;
    if (s < 0.004) {
      M.compose(POS.set(b.x, 0, b.y), Q.identity(), ONE);
    } else {
      EUL.set(0, b.rot, 0);
      M.compose(POS.set(b.x, 0, b.y), Q.setFromEuler(EUL), SCL.set(b.w, b.h * s, b.w));
    }
    blockMesh.setMatrixAt(i, M);
  }
  blockMesh.instanceMatrix.needsUpdate = true;

  /* wall: nothing before 271, then it stays for the rest of the page */
  const wantWall = smoothT >= 2 ? Math.min(1, (smoothT - 1.75) / 0.6) : 0;
  wallUp += (wantWall - wallUp) * (REDUCED ? 1 : 0.08);
  for (let i = 0; i < wallSegs.length; i++) {
    const w = wallSegs[i];
    EUL.set(0, w.rot, 0);
    const hh = 0.135 * wallUp * ease;
    M.compose(
      POS.set(w.x, 0, w.z),
      Q.setFromEuler(EUL),
      hh < 0.002 ? ONE : SCL.set(w.len + 0.035, hh, 0.035)
    );
    wallMesh.setMatrixAt(i, M);
  }
  wallMesh.instanceMatrix.needsUpdate = true;

  /* camera: a slow swing across the twenty centuries plus a little parallax */
  mx += (tmx - mx) * 0.05; my += (tmy - my) * 0.05;
  const hero = state.hero || 0;
  const wantOffset = -0.14 + 0.4 * (1 - hero);
  if (Math.abs(wantOffset - offsetNow) > 0.002) {
    offsetNow += (wantOffset - offsetNow) * 0.09;
    applyOffset();
  }

  const p = smoothT / 19;
  const ang = -0.70 + p * 1.05 + (REDUCED ? 0 : mx * 0.20);
  const dist = 7.4 + p * 1.6;
  const hgt = 2.0 + p * 2.6 + (REDUCED ? 0 : -my * 0.5);
  camera.position.set(Math.sin(ang) * dist, hgt * (0.6 + 0.4 * ease), Math.cos(ang) * dist);
  camera.lookAt(0, 0.25, -0.1);

  renderer.render(scene, camera);
}

requestAnimationFrame(frame);
canvas.classList.add('on');
