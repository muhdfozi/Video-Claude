// "Lori Towing" — deterministic 3D scene. window.renderAt(t) draws frame at t seconds.
import * as THREE from 'three';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';

const qs = new URLSearchParams(location.search);
const W = Number(qs.get('w') || 1080), H = Number(qs.get('h') || 1920);
const S = W / 1080;
const TL = await (await fetch('/build/timeline.json')).json();
const EV = TL.events;
const BEAT = EV.beat;

// ---------------------------------------------------------------- helpers
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const lerp = (a, b, t) => a + (b - a) * t;
const k = (t, a, b) => clamp((t - a) / (b - a));
const sm = (x) => x * x * (3 - 2 * x);
const eOut = (x) => 1 - Math.pow(1 - x, 3);
const eIn = (x) => x * x * x;
const eIO = (x) => (x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2);
const eBack = (x) => { const c = 1.9; return 1 + (c + 1) * Math.pow(x - 1, 3) + c * Math.pow(x - 1, 2); };
const hash = (n) => { const s = Math.sin(n * 127.1 + 311.7) * 43758.5453; return s - Math.floor(s); };
const V = (x, y, z) => new THREE.Vector3(x, y, z);
const speaking = (t) => TL.words.some((w) => t >= w.t0 && t < w.t1 - 0.04) ? 1 : 0;
const blinkOn = (t, phase = 0) => ((t / BEAT + phase) % 1 + 1) % 1 < 0.5;

// ---------------------------------------------------------------- renderer
const glCanvas = document.getElementById('gl');
const renderer = new THREE.WebGLRenderer({ canvas: glCanvas, antialias: true, preserveDrawingBuffer: true });
renderer.setPixelRatio(1);
renderer.setSize(W, H);
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.05;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;

const scene = new THREE.Scene();
const pmrem = new THREE.PMREMGenerator(renderer);
scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
scene.environmentIntensity = 0.35;

// Sky gradient as screen-space background.
{
  const c = document.createElement('canvas'); c.width = 4; c.height = 512;
  const g = c.getContext('2d'), gr = g.createLinearGradient(0, 0, 0, 512);
  gr.addColorStop(0, '#3f8fdc'); gr.addColorStop(0.55, '#8cc4ef'); gr.addColorStop(1, '#e6f1f4');
  g.fillStyle = gr; g.fillRect(0, 0, 4, 512);
  const tex = new THREE.CanvasTexture(c); tex.colorSpace = THREE.SRGBColorSpace;
  scene.background = tex;
}
scene.fog = new THREE.Fog(0xd9e9ef, 70, 320);

const camera = new THREE.PerspectiveCamera(40, W / H, 0.1, 1200);

const hemi = new THREE.HemisphereLight(0xcfe8ff, 0x6f8f4a, 1.0);
scene.add(hemi);
const sun = new THREE.DirectionalLight(0xfff1dc, 2.7);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
sun.shadow.bias = -0.0004;
sun.shadow.normalBias = 0.02;
scene.add(sun, sun.target);
const SUN_DIR = V(-0.55, 1, 0.65).normalize();

// ---------------------------------------------------------------- materials
const mat = (color, o = {}) => new THREE.MeshStandardMaterial({ color, roughness: 0.7, metalness: 0, ...o });
const M = {
  grass: mat(0x86b25c, { roughness: 1 }),
  grass2: mat(0x79a653, { roughness: 1 }),
  asphalt: mat(0x45484e, { roughness: 0.95 }),
  shoulder: mat(0x55585e, { roughness: 0.95 }),
  white: mat(0xf2f2ee, { roughness: 0.6 }),
  yellowLine: mat(0xf2c230, { roughness: 0.6 }),
  steel: mat(0xb9c0c6, { roughness: 0.35, metalness: 0.8 }),
  darkSteel: mat(0x2c2f34, { roughness: 0.5, metalness: 0.6 }),
  black: mat(0x16171a, { roughness: 0.8 }),
  tire: mat(0x1b1c1f, { roughness: 0.9 }),
  rim: mat(0xd3d7db, { roughness: 0.3, metalness: 0.9 }),
  truck: mat(0xf4b400, { roughness: 0.45 }),
  truckDark: mat(0x2a2b2f, { roughness: 0.6 }),
  bed: mat(0x8d949b, { roughness: 0.45, metalness: 0.6 }),
  glass: mat(0x1d2c3a, { roughness: 0.1, metalness: 0.3, transparent: true, opacity: 0.62 }),
  car: mat(0x2f7fb8, { roughness: 0.35, metalness: 0.15 }),
  carDark: mat(0x1f2328, { roughness: 0.6 }),
  head: mat(0xfff7d6, { emissive: 0xfff2c0, emissiveIntensity: 0.6 }),
  tail: mat(0xb3121b, { emissive: 0x550000, emissiveIntensity: 0.4 }),
  trunk: mat(0x6e5a44, { roughness: 1 }),
  frond: mat(0x3f7f35, { roughness: 0.9, side: THREE.DoubleSide }),
  skin: mat(0xc78a64, { roughness: 0.75 }),
  skinKid: mat(0xe0b08e, { roughness: 0.75 }),
  hair: mat(0x16110f, { roughness: 0.9 }),
  beard: mat(0x2a1d17, { roughness: 1, transparent: true, opacity: 0.42, depthWrite: false }),
  jeans: mat(0x3d5577, { roughness: 0.9 }),
  shoe: mat(0x2b2b2b, { roughness: 0.8 }),
  hijab: mat(0xd8cfc4, { roughness: 0.95 }),
  cloud: mat(0xffffff, { roughness: 1, emissive: 0xffffff, emissiveIntensity: 0.25 }),
};
const amberOn = mat(0xffa000, { emissive: 0xff8a00, emissiveIntensity: 3.2 });
const amberOff = mat(0x8a5a12, { emissive: 0x000000, roughness: 0.4 });
const redOn = mat(0xff2a1a, { emissive: 0xff1a0a, emissiveIntensity: 3 });

function stripeTexture() {
  const c = document.createElement('canvas'); c.width = 64; c.height = 256;
  const g = c.getContext('2d');
  for (let i = 0; i < 8; i++) { g.fillStyle = i % 2 ? '#f3f3f1' : '#1c2742'; g.fillRect(0, i * 32, 64, 32); }
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace;
  t.wrapS = t.wrapT = THREE.RepeatWrapping; return t;
}
M.polo = mat(0xffffff, { map: stripeTexture(), roughness: 0.85 });
M.poloNavy = mat(0x1c2742, { roughness: 0.85 });

function doorTexture(n) {
  const c = document.createElement('canvas'); c.width = 256; c.height = 256;
  const g = c.getContext('2d');
  g.fillStyle = '#f4b400'; g.fillRect(0, 0, 256, 256);
  g.fillStyle = '#16171a'; g.fillRect(0, 196, 256, 60);
  g.font = '900 150px "Inter Display", Inter, sans-serif'; g.textAlign = 'center'; g.textBaseline = 'middle';
  g.fillText(String(n), 128, 96);
  g.fillStyle = '#f4b400'; g.font = '800 34px "Inter Display", Inter, sans-serif';
  g.fillText('TOWING 24J', 128, 228);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t;
}

const add = (parent, geo, material, x = 0, y = 0, z = 0, cast = true) => {
  const m = new THREE.Mesh(geo, material);
  m.position.set(x, y, z); m.castShadow = cast; m.receiveShadow = true;
  parent.add(m); return m;
};
const rbox = (w, h, d, r = 0.08) => new RoundedBoxGeometry(w, h, d, 3, Math.min(r, w / 2, h / 2, d / 2));

// ---------------------------------------------------------------- world
const world = new THREE.Group(); scene.add(world);
const ROAD = { z0: -2.3, z1: 9.8 };
{
  const g = new THREE.PlaneGeometry(1400, 1400); g.rotateX(-Math.PI / 2);
  add(world, g, M.grass, 0, -0.02, 0, false);
  const road = new THREE.PlaneGeometry(1400, ROAD.z1 - ROAD.z0); road.rotateX(-Math.PI / 2);
  add(world, road, M.asphalt, 0, 0, (ROAD.z0 + ROAD.z1) / 2, false);
  const shoulder = new THREE.PlaneGeometry(1400, 3.9); shoulder.rotateX(-Math.PI / 2);
  add(world, shoulder, M.shoulder, 0, 0.003, -0.05, false);
  const line = (z, w, m) => { const lg = new THREE.PlaneGeometry(1400, w); lg.rotateX(-Math.PI / 2); add(world, lg, m, 0, 0.006, z, false); };
  line(-1.95, 0.16, M.yellowLine); line(1.95, 0.14, M.white); line(9.4, 0.14, M.white);
  const dash = new THREE.PlaneGeometry(3, 0.13); dash.rotateX(-Math.PI / 2);
  const dashes = new THREE.InstancedMesh(dash, M.white, 160);
  const m4 = new THREE.Matrix4();
  for (let i = 0; i < 160; i++) { m4.makeTranslation(-400 + i * 9, 0.006, 5.65); dashes.setMatrixAt(i, m4); }
  dashes.receiveShadow = true; world.add(dashes);

  // Guardrail on the verge.
  const post = new THREE.BoxGeometry(0.12, 0.75, 0.12);
  const posts = new THREE.InstancedMesh(post, M.steel, 220);
  for (let i = 0; i < 220; i++) { m4.makeTranslation(-300 + i * 4, 0.375, -3.0); posts.setMatrixAt(i, m4); }
  posts.castShadow = true; posts.receiveShadow = true; world.add(posts);
  add(world, new THREE.BoxGeometry(880, 0.3, 0.06), M.steel, 140, 0.62, -2.92);

  // Oil palm estate (instanced trunks + fronds).
  const trunkG = new THREE.CylinderGeometry(0.28, 0.4, 1, 7); trunkG.translate(0, 0.5, 0);
  const frondG = new THREE.ConeGeometry(0.55, 4.2, 4, 1); frondG.translate(0, 2.1, 0); frondG.scale(1, 1, 0.18);
  const palms = [];
  for (let gx = -40; gx < 70; gx++) for (let gz = 0; gz < 12; gz++) {
    const x = gx * 6.5 + (gz % 2) * 3.2 + (hash(gx * 13 + gz) - 0.5) * 1.6;
    const z = -9 - gz * 6.5 + (hash(gx * 7 + gz * 3) - 0.5) * 1.5;
    palms.push([x, z, 4.5 + hash(gx + gz * 31) * 3.5]);
  }
  for (let gx = -40; gx < 70; gx++) for (let gz = 0; gz < 8; gz++) {
    const x = gx * 7 + (gz % 2) * 3.5 + (hash(gx * 5 + gz) - 0.5) * 2;
    const z = 38 + gz * 7 + (hash(gx * 3 + gz * 7) - 0.5) * 2;
    palms.push([x, z, 4 + hash(gx * 2 + gz * 17) * 4]);
  }
  const trunks = new THREE.InstancedMesh(trunkG, M.trunk, palms.length);
  const NF = 11;
  const fronds = new THREE.InstancedMesh(frondG, M.frond, palms.length * NF);
  const q = new THREE.Quaternion(), e = new THREE.Euler(), sc = V(1, 1, 1), col = new THREE.Color();
  palms.forEach(([x, z, h], i) => {
    m4.compose(V(x, 0, z), q.identity(), V(1, h, 1)); trunks.setMatrixAt(i, m4);
    for (let f = 0; f < NF; f++) {
      const a = (f / NF) * Math.PI * 2 + hash(i) * 6;
      const tilt = 0.9 + hash(i * 11 + f) * 0.6 + (f % 2) * 0.35;
      e.set(0, a, 0, 'YXZ'); e.x = 0; e.z = 0;
      q.setFromEuler(new THREE.Euler(tilt, a, 0, 'YXZ'));
      sc.set(1, 0.8 + hash(i + f * 3) * 0.45, 1);
      m4.compose(V(x, h, z), q, sc); fronds.setMatrixAt(i * NF + f, m4);
      col.setHSL(0.28 + hash(i * 3 + f) * 0.05, 0.45, 0.28 + hash(i + f) * 0.1); fronds.setColorAt(i * NF + f, col);
    }
  });
  trunks.castShadow = fronds.castShadow = true; trunks.receiveShadow = fronds.receiveShadow = true;
  world.add(trunks, fronds);

  // Clouds.
  const cg = new THREE.SphereGeometry(1, 12, 8);
  for (let i = 0; i < 26; i++) {
    const cx = -250 + i * 28 + hash(i) * 20, cz = -180 - hash(i * 3) * 120, cy = 55 + hash(i * 7) * 35;
    for (let j = 0; j < 5; j++) {
      const s = 7 + hash(i * 5 + j) * 7;
      const m = add(world, cg, M.cloud, cx + (j - 2) * 7, cy + hash(i + j) * 4, cz + hash(j) * 5, false);
      m.scale.set(s * 1.4, s * 0.7, s); m.receiveShadow = false;
    }
  }
}

// ---------------------------------------------------------------- vehicles
function wheel(parent, r, w, x, y, z) {
  const g = new THREE.Group(); g.position.set(x, y, z); parent.add(g);
  const tg = new THREE.CylinderGeometry(r, r, w, 20); tg.rotateX(Math.PI / 2);
  add(g, tg, M.tire);
  const rg = new THREE.CylinderGeometry(r * 0.58, r * 0.58, w * 1.02, 10); rg.rotateX(Math.PI / 2);
  add(g, rg, M.rim);
  const hub = new THREE.BoxGeometry(r * 0.9, r * 0.14, w * 1.04);
  add(g, hub, M.darkSteel);
  return g;
}

function makeCar() {
  const root = new THREE.Group();
  const body = new THREE.Group(); root.add(body);
  add(body, rbox(3.9, 0.72, 1.72, 0.22), M.car, 0, 0.7, 0);
  add(body, rbox(2.4, 0.62, 1.6, 0.2), M.glass, -0.25, 1.32, 0);
  add(body, rbox(2.1, 0.08, 1.5, 0.04), M.car, -0.35, 1.64, 0);          // roof
  add(body, rbox(0.12, 0.6, 0.12, 0.04), M.car, -1.42, 1.32, 0.76);       // pillars
  add(body, rbox(0.12, 0.6, 0.12, 0.04), M.car, -1.42, 1.32, -0.76);
  add(body, rbox(3.95, 0.2, 1.76, 0.08), M.carDark, 0, 0.38, 0);         // skirt
  const bonnet = new THREE.Group(); bonnet.position.set(0.85, 1.05, 0); body.add(bonnet);
  add(bonnet, rbox(1.15, 0.07, 1.62, 0.03), M.car, 0.55, 0, 0);
  const lights = [];
  for (const z of [-0.6, 0.6]) {
    add(body, rbox(0.06, 0.16, 0.36, 0.03), M.head, 1.95, 0.85, z);
    add(body, rbox(0.06, 0.18, 0.3, 0.03), M.tail, -1.95, 0.88, z);
    lights.push(add(body, rbox(0.08, 0.09, 0.14, 0.02), amberOff, 1.94, 0.72, z * 1.25));
    lights.push(add(body, rbox(0.08, 0.09, 0.14, 0.02), amberOff, -1.94, 0.72, z * 1.25));
  }
  const wheels = [];
  for (const x of [-1.25, 1.25]) for (const z of [-0.78, 0.78]) wheels.push(wheel(body, 0.33, 0.24, x, 0.33, z));
  // Family waiting inside (passenger seat + child at the back).
  const wife = new THREE.Group(); wife.position.set(0.05, 1.05, -0.38); body.add(wife);
  add(wife, new THREE.SphereGeometry(0.17, 16, 12), M.hijab, 0, 0.2, 0);
  add(wife, new THREE.ConeGeometry(0.24, 0.3, 16), M.hijab, 0, 0.0, 0);
  add(wife, new THREE.SphereGeometry(0.11, 14, 10), M.skinKid, 0.08, 0.19, 0);
  const kid = new THREE.Group(); kid.position.set(-0.85, 1.0, -0.3); body.add(kid);
  add(kid, new THREE.SphereGeometry(0.12, 14, 10), M.skinKid, 0, 0.16, 0);
  add(kid, new THREE.SphereGeometry(0.125, 14, 10, 0, Math.PI * 2, 0, 1.3), M.hair, -0.01, 0.17, 0);
  add(kid, new THREE.CylinderGeometry(0.1, 0.13, 0.22, 12), M.white, 0, -0.03, 0);
  return { root, body, bonnet, lights, wheels };
}

const SCALES = [1.0, 1.12, 1.26, 1.42, 1.72];
const TRUCK_L = 8.7;
function makeTruck(n, s) {
  const root = new THREE.Group();
  const body = new THREE.Group(); root.add(body); body.scale.setScalar(s);
  // chassis
  add(body, new THREE.BoxGeometry(8.6, 0.32, 1.1), M.truckDark, 4.3, 0.78, 0);
  // cab
  add(body, rbox(2.5, 1.65, 2.4, 0.18), M.truck, 7.35, 1.85, 0);
  add(body, rbox(1.2, 0.9, 2.4, 0.12), M.truck, 8.05, 1.1, 0);           // nose
  add(body, rbox(0.06, 0.8, 2.1, 0.04), M.glass, 8.6, 2.15, 0);            // windscreen
  for (const z of [-1.21, 1.21]) add(body, rbox(1.2, 0.7, 0.04, 0.02), M.glass, 7.45, 2.2, z);
  add(body, rbox(0.2, 0.35, 2.5, 0.06), M.darkSteel, 8.7, 0.75, 0);       // bumper
  add(body, rbox(0.06, 0.45, 1.3, 0.03), M.darkSteel, 8.66, 1.15, 0);     // grille
  for (const z of [-0.95, 0.95]) add(body, rbox(0.06, 0.2, 0.3, 0.03), M.head, 8.67, 1.25, z);
  const dt = mat(0xffffff, { map: doorTexture(n), roughness: 0.5 });
  for (const z of [-1.215, 1.215]) {
    const p = add(body, new THREE.PlaneGeometry(0.95, 0.95), dt, 6.7, 1.45, z, false);
    if (z < 0) p.rotation.y = Math.PI;
  }
  // roof light bar
  add(body, new THREE.BoxGeometry(0.35, 0.12, 1.8), M.black, 7.2, 2.76, 0);
  const beacons = [];
  for (const z of [-0.6, -0.2, 0.2, 0.6]) beacons.push(add(body, rbox(0.3, 0.18, 0.32, 0.06), amberOff, 7.2, 2.9, z));
  // bed (pivots near the cab so the rear can tilt down)
  const bed = new THREE.Group(); bed.position.set(6.0, 1.12, 0); body.add(bed);
  add(bed, new THREE.BoxGeometry(6.0, 0.22, 2.45), M.bed, -3.0, 0, 0);
  for (const z of [-1.2, 1.2]) add(bed, new THREE.BoxGeometry(6.0, 0.16, 0.08), M.truck, -3.0, 0.16, z);
  add(bed, new THREE.BoxGeometry(0.25, 1.0, 2.3), M.truckDark, -0.05, 0.6, 0);  // headboard
  // tail lights + hazards
  const hazards = [];
  for (const z of [-1.05, 1.05]) {
    add(body, rbox(0.08, 0.16, 0.3, 0.03), M.tail, 0.0, 0.78, z);
    hazards.push(add(body, rbox(0.1, 0.12, 0.16, 0.03), amberOff, 0.0, 0.58, z));
    hazards.push(add(body, rbox(0.1, 0.12, 0.16, 0.03), amberOff, 8.78, 0.98, z * 1.05));
  }
  // rear wheel-lift + front tow eye
  add(body, new THREE.BoxGeometry(0.9, 0.16, 0.9), M.darkSteel, -0.35, 0.42, 0);
  add(body, new THREE.BoxGeometry(0.2, 0.14, 1.6), M.darkSteel, -0.75, 0.42, 0);
  const wheels = [];
  for (const x of [1.4, 2.65, 7.55]) for (const z of [-1.0, 1.0]) wheels.push(wheel(body, 0.52, 0.42, x, 0.52, z));
  for (const x of [2.0]) for (const z of [-1.0, 1.0]) add(body, new THREE.BoxGeometry(2.4, 0.08, 0.5), M.truckDark, x, 1.08, z);
  return { root, body, bed, beacons, hazards, wheels, s, n };
}

const car = makeCar(); scene.add(car.root);
const trucks = SCALES.map((s, i) => { const t = makeTruck(i + 1, s); scene.add(t.root); return t; });

// Tow bars between trucks.
const barG = new THREE.CylinderGeometry(0.07, 0.07, 1, 8); barG.translate(0, 0.5, 0); barG.rotateZ(-Math.PI / 2);
const bars = trucks.map(() => { const m = new THREE.Mesh(barG, M.darkSteel); m.castShadow = true; scene.add(m); return m; });

// Background traffic.
const traffic = [0xd8d8d8, 0xb3261e, 0x222831, 0xf0f0f0].map((c) => {
  const v = makeCar(); v.body.children[0].material = mat(c, { roughness: 0.35 });
  v.body.children.filter((m) => m.material === M.car).forEach((m) => (m.material = v.body.children[0].material));
  scene.add(v.root); return v;
});

// ---------------------------------------------------------------- person
function capsule(r, len) { return new THREE.CapsuleGeometry(r, len, 6, 12); }
function makePerson() {
  const root = new THREE.Group();
  const hips = new THREE.Group(); hips.position.y = 0.93; root.add(hips);
  const legs = [];
  for (const x of [-0.1, 0.1]) {
    const leg = new THREE.Group(); leg.position.set(x, 0, 0); hips.add(leg);
    add(leg, capsule(0.085, 0.7), M.jeans, 0, -0.43, 0);
    add(leg, rbox(0.15, 0.1, 0.3, 0.04), M.shoe, 0, -0.88, 0.05);
    legs.push(leg);
  }
  add(hips, rbox(0.36, 0.16, 0.22, 0.07), M.jeans, 0, 0.0, 0);
  const torso = new THREE.Group(); hips.add(torso);
  const tm = add(torso, capsule(0.175, 0.3), M.polo, 0, 0.3, 0); tm.scale.set(1.08, 1, 0.78);
  add(torso, new THREE.TorusGeometry(0.075, 0.025, 6, 16), M.poloNavy, 0, 0.55, 0.0).rotation.x = Math.PI / 2;
  add(torso, new THREE.CylinderGeometry(0.06, 0.065, 0.12, 10), M.skin, 0, 0.6, 0);
  const head = new THREE.Group(); head.position.y = 0.66; torso.add(head);
  const hs = add(head, new THREE.SphereGeometry(0.15, 24, 18), M.skin, 0, 0.11, 0); hs.scale.set(0.95, 1.08, 1);
  const hair = add(head, new THREE.SphereGeometry(0.157, 20, 14, 0, Math.PI * 2, 0, 1.25), M.hair, 0, 0.13, -0.012);
  hair.scale.set(0.98, 1.08, 1.02); hair.rotation.x = -0.25;
  const beard = add(head, new THREE.SphereGeometry(0.153, 32, 16, -1.9, 3.8, 1.95, 0.85), M.beard, 0, 0.112, 0.004, false);
  beard.scale.set(0.96, 1.08, 1.0);
  for (const x of [-0.148, 0.148]) add(head, new THREE.SphereGeometry(0.032, 8, 6), M.skin, x, 0.11, -0.01);
  const eyes = [], brows = [], lenses = [];
  for (const x of [-0.055, 0.055]) {
    eyes.push(add(head, new THREE.SphereGeometry(0.016, 8, 6), M.black, x, 0.135, 0.138, false));
    const b = add(head, new THREE.BoxGeometry(0.06, 0.012, 0.012), M.hair, x, 0.192, 0.14, false); brows.push(b);
    const l = add(head, new THREE.TorusGeometry(0.039, 0.0075, 6, 24), M.black, x, 0.135, 0.149, false); lenses.push(l);
    add(head, new THREE.BoxGeometry(0.008, 0.008, 0.14), M.black, x * 2.5, 0.14, 0.08, false);
  }
  add(head, new THREE.BoxGeometry(0.03, 0.01, 0.01), M.black, 0, 0.14, 0.158, false);
  const mouth = add(head, rbox(0.055, 0.014, 0.012, 0.005), mat(0x4a1c1a), 0, 0.058, 0.142, false);
  add(head, new THREE.SphereGeometry(0.022, 8, 6), M.skin, 0, 0.1, 0.152, false);   // nose
  const sweat = add(head, new THREE.SphereGeometry(0.018, 8, 6), mat(0x8fd3ff, { roughness: 0.1, transparent: true, opacity: 0.9 }), 0.12, 0.2, 0.09, false);
  sweat.scale.set(0.8, 1.3, 0.8);
  const arms = [];
  for (const side of [-1, 1]) {           // -1 = right arm (character's right is -x)
    const sh = new THREE.Group(); sh.position.set(side * 0.215, 0.47, 0); torso.add(sh);
    add(sh, capsule(0.07, 0.16), M.polo, 0, -0.12, 0);
    const el = new THREE.Group(); el.position.set(0, -0.27, 0); sh.add(el);
    add(el, capsule(0.052, 0.2), M.skin, 0, -0.12, 0);
    const hand = add(el, new THREE.SphereGeometry(0.058, 12, 10), M.skin, 0, -0.27, 0.0);
    arms.push({ sh, el, hand });
  }
  const phone = add(arms[0].el, rbox(0.035, 0.15, 0.075, 0.012), M.black, -0.03, -0.3, 0.02, false);
  return { root, hips, torso, head, legs, arms, brows, mouth, sweat, phone, eyes };
}
const me = makePerson(); scene.add(me.root);
const ME_POS = V(-3.6, 0, 1.05);

// Two-bone IK: place elbow so the hand (0.27 below the elbow) lands on `target`.
const ARM = 0.27, Y_DOWN = V(0, -1, 0), _q = new THREE.Quaternion();
function armIK(arm, target, pole) {
  const S0 = arm.sh.position, d = target.clone().sub(S0);
  const len = Math.min(d.length(), ARM * 2 - 1e-3); d.normalize();
  const perp = pole.clone().sub(d.clone().multiplyScalar(pole.dot(d))).normalize();
  const hgt = Math.sqrt(ARM * ARM - (len / 2) ** 2);
  const E = S0.clone().addScaledVector(d, len / 2).addScaledVector(perp, hgt);
  const dSE = E.clone().sub(S0).normalize();
  arm.sh.quaternion.setFromUnitVectors(Y_DOWN, dSE);
  const T = S0.clone().addScaledVector(d, len);
  const dEH = T.sub(E).normalize().applyQuaternion(_q.copy(arm.sh.quaternion).invert());
  arm.el.quaternion.setFromUnitVectors(Y_DOWN, dEH);
}

// pose: phone (0..1), palm (facepalm 0..1), mood (-1 calm .. 1 furious), talk (mouth)
function posePerson(t, { phone = 0, palm = 0, mood = 0, talk = 0, face = 0, look = 0, sweat = 0 }) {
  const P = me;
  P.root.position.copy(ME_POS);
  P.root.rotation.y = face;
  const breathe = Math.sin(t * 2.2) * 0.012;
  P.torso.rotation.x = breathe + palm * 0.18;
  P.torso.position.y = breathe * 0.3;
  P.head.rotation.set(palm * 0.32 - Math.abs(mood) * 0.04, look + Math.sin(t * 1.3) * 0.04, phone * 0.12);
  // arms via 2-bone IK in torso space: hand targets blend idle -> ear / forehead
  const [R, L] = P.arms;
  const sw = Math.sin(t * 2.2) * 0.01;
  armIK(R, lerpV(V(-0.25, -0.05 + sw, 0.06), V(-0.165, 0.76, 0.02), eIO(phone)), lerpV(V(-0.3, 0, -1), V(-0.8, -0.45, 0.35), phone));
  armIK(L, lerpV(V(0.25, -0.05 - sw, 0.06), V(0.0, 0.84, 0.19), eIO(palm)), lerpV(V(0.3, 0, -1), V(0.8, -0.5, 0.45), palm));
  P.phone.visible = palm < 0.5;
  // face
  const ang = mood * 0.35;
  P.brows[0].rotation.z = -ang; P.brows[1].rotation.z = ang;
  P.brows[0].position.y = P.brows[1].position.y = 0.192 - Math.max(0, mood) * 0.01;
  const open = talk > 0 ? 0.6 + 0.4 * Math.abs(Math.sin(t * 22)) : 0;
  P.mouth.scale.set(1 - open * 0.2, 1 + open * 1.1 * talk, 1);
  P.mouth.position.y = 0.055 - open * 0.006 * talk;
  P.sweat.visible = sweat > 0;
  P.sweat.position.y = 0.2 - ((t * 0.35) % 0.12);
}

// ---------------------------------------------------------------- smoke
const smokeTex = (() => {
  const c = document.createElement('canvas'); c.width = c.height = 128;
  const g = c.getContext('2d'), gr = g.createRadialGradient(64, 64, 4, 64, 64, 62);
  gr.addColorStop(0, 'rgba(255,255,255,1)'); gr.addColorStop(0.55, 'rgba(255,255,255,0.55)'); gr.addColorStop(1, 'rgba(255,255,255,0)');
  g.fillStyle = gr; g.fillRect(0, 0, 128, 128);
  return new THREE.CanvasTexture(c);
})();
const smokePool = [];
let smokeUsed = 0;
function puff(pos, size, color, alpha) {
  let sp = smokePool[smokeUsed];
  if (!sp) {
    sp = new THREE.Sprite(new THREE.SpriteMaterial({ map: smokeTex, transparent: true, depthWrite: false, fog: true }));
    scene.add(sp); smokePool.push(sp);
  }
  smokeUsed++;
  sp.visible = true; sp.position.copy(pos); sp.scale.setScalar(size);
  sp.material.color.set(color); sp.material.opacity = alpha;
}
// continuous plume from `origin` since `start`
function plume(t, start, origin, s = 1, dark = 0, seed = 0) {
  if (t < start) return;
  const N = 14, life = 2.4, iv = life / N;
  for (let j = 0; j < N; j++) {
    const age = ((t - start - j * iv) % life + life) % life;
    if (t - start < j * iv) continue;
    const a = age / life, h = hash(j + seed * 17);
    const p = origin.clone().add(V((h - 0.5) * 0.4 * s - a * 1.2 * s, a * 3.2 * s, (hash(j * 3 + seed) - 0.5) * 0.6 * s));
    const c = new THREE.Color().setScalar(lerp(0.85, 0.35, dark) - a * 0.1);
    puff(p, (0.5 + a * 1.9) * s, c, (1 - a) * Math.min(1, a * 6) * 0.75);
  }
}
function burst(t, tb, origin, s = 1, seed = 0) {
  const dt = t - tb; if (dt < 0 || dt > 1.8) return;
  for (let j = 0; j < 18; j++) {
    const a = j / 18 * Math.PI * 2 + hash(j + seed), up = 0.4 + hash(j * 7 + seed) * 1.2;
    const sp = eOut(clamp(dt / 1.2)) * (1.4 + hash(j * 3) * 1.4) * s;
    const p = origin.clone().add(V(Math.cos(a) * sp, up * sp + dt * 0.8 * s, Math.sin(a) * sp * 0.7));
    const c = new THREE.Color().setScalar(0.28 + hash(j) * 0.25);
    puff(p, (0.7 + dt * 1.6) * s, c, (1 - dt / 1.8) * 0.9);
  }
}

// ---------------------------------------------------------------- story state
const ARR = EV.arrive, HITCH = EV.hitch, DRIVE = EV.drive, BREAK = EV.break, LOAD = EV.load;
const shiftOf = (i, t) => DRIVE.reduce((acc, [a, b, m], kx) => acc + (kx >= i ? m * eIO(k(t, a, b)) : 0), 0);
const base = [];
{
  const gap = 1.8;
  base[0] = 2.9;
  for (let i = 1; i < 5; i++) base[i] = base[i - 1] + DRIVE[i - 1][2] + TRUCK_L * SCALES[i - 1] + gap * SCALES[i];
}
function truckRear(i, t) {
  const arr = ARR[i];
  const inX = 46 * Math.pow(1 - eOut(k(t, arr[0], arr[1])), 1.4);
  return base[i] + inX + shiftOf(i, t);
}
const truckFront = (i, t) => truckRear(i, t) + TRUCK_L * SCALES[i];
const truckVisible = (i, t) => t >= ARR[i][0] - 0.01;
const broken = (i, t) => t >= BREAK[i];
const BED_TOP = 1.23;

function updateWorld(t) {
  smokeUsed = 0;
  const hz = blinkOn(t);
  // trucks
  trucks.forEach((tr, i) => {
    const vis = truckVisible(i, t);
    tr.root.visible = vis; bars[i].visible = false;
    if (!vis) return;
    const x = truckRear(i, t), s = tr.s;
    tr.root.position.set(x, 0, 0);
    const db = t - BREAK[i];
    const jolt = db > 0 && db < 1.2 ? Math.exp(-db * 4.5) * Math.sin(db * 34) : 0;
    tr.body.position.y = jolt * 0.05 * s;
    tr.body.rotation.x = jolt * 0.02;
    tr.body.rotation.z = db > 0 ? -0.012 * Math.min(1, db * 3) : 0;   // sags after breakdown
    tr.wheels.forEach((w) => (w.rotation.z = -x / 0.52 / s));
    tr.beacons.forEach((b, j) => (b.material = !broken(i, t) && blinkOn(t, j % 2 ? 0.5 : 0) ? amberOn : amberOff));
    tr.hazards.forEach((h) => (h.material = broken(i, t) && hz ? amberOn : amberOff));
    // bed tilt for truck 1 loading
    let tilt = 0;
    if (i === 0) tilt = 0.19 * sm(k(t, LOAD[0] - 0.35, LOAD[0])) * (1 - sm(k(t, LOAD[1] - 0.05, LOAD[1] + 0.3)));
    tr.bed.rotation.z = tilt;
    // tow bar to the truck behind
    if (i > 0 && HITCH[i] && t >= HITCH[i]) {
      const a = V(x - 0.75 * s, 0.45 * s, 0), b = V(truckFront(i - 1, t) + 0.05, 0.75 * SCALES[i - 1], 0);
      const grow = eOut(k(t, HITCH[i], HITCH[i] + 0.22));
      const bar = bars[i]; bar.visible = true;
      const d = b.clone().sub(a);
      bar.position.copy(a);
      bar.quaternion.setFromUnitVectors(V(1, 0, 0), d.clone().normalize());
      bar.scale.set(d.length() * grow, 1, 1);
    }
    // smoke from the bonnet once broken
    const s1 = s;
    if (broken(i, t)) {
      const origin = V(x + 8.1 * s1, 2.4 * s1, 0);
      burst(t, BREAK[i], origin, s1 * 1.1, i * 9);
      plume(t, BREAK[i] + 0.15, origin, s1 * 0.95, 0.35 + i * 0.1, i * 5);
    }
  });
  // car: broken from the start, winched onto truck 1
  const tr0 = trucks[0];
  const rear0 = truckRear(0, t);
  const u = eIO(k(t, LOAD[0], LOAD[1]));
  const onX = rear0 + 3.3;
  const carX = lerp(0, onX, u);
  const tilt = tr0.bed.rotation.z;
  const xb = carX - rear0;                     // car centre in bed coords (0 = bed rear)
  const surf = BED_TOP - Math.max(0, 6.0 - xb) * Math.sin(tilt);
  const onBed = sm(k(xb, -1.6, 0.9));
  car.root.position.set(carX, Math.max(0, surf) * (u > 0 ? onBed : 0), 0);
  car.root.rotation.z = tilt * onBed;
  car.wheels.forEach((w) => (w.rotation.z = -carX / 0.33));
  car.bonnet.rotation.z = -0.32;
  car.lights.forEach((l) => (l.material = hz ? amberOn : amberOff));
  plume(t, -3, car.root.position.clone().add(V(1.6, 1.3 + car.root.position.y * 0, 0)), 0.55, 0.0, 99);

  // traffic (only some shots ask for it)
  traffic.forEach((v, j) => {
    const lane = j % 2 ? 7.5 : 3.8, sp = j % 2 ? 22 : 27;
    v.root.position.set(((t * sp + j * 97) % 420) - 180, 0, lane);
    v.wheels.forEach((w) => (w.rotation.z = -(t * sp) / 0.33));
    v.lights.forEach((l) => (l.material = amberOff));
    v.root.visible = SHOT_STATE.traffic;
  });
  for (let i = smokeUsed; i < smokePool.length; i++) smokePool[i].visible = false;
}

// ---------------------------------------------------------------- camera
const SHOT_STATE = { traffic: false };
function setCam(pos, look, fov = 40, roll = 0) {
  camera.position.copy(pos); camera.fov = fov; camera.up.set(0, 1, 0);
  camera.lookAt(look);
  if (roll) camera.rotateZ(roll);
  camera.updateProjectionMatrix();
  // keep shadows sharp around what we're looking at
  const c = look.clone();
  sun.target.position.copy(c);
  sun.position.copy(c).addScaledVector(SUN_DIR, 60);
  const r = Math.min(60, Math.max(14, pos.distanceTo(look) * 0.9));
  Object.assign(sun.shadow.camera, { left: -r, right: r, top: r, bottom: -r, near: 1, far: 160 });
  sun.shadow.camera.updateProjectionMatrix();
}
const shake = (t, tb, amp) => {
  const d = t - tb; if (d < 0 || d > 1) return V(0, 0, 0);
  const a = amp * Math.exp(-d * 6);
  return V(Math.sin(d * 71) * a, Math.sin(d * 53 + 1) * a, Math.sin(d * 63 + 2) * a * 0.5);
};
const lerpV = (a, b, t) => a.clone().lerp(b, t);

// Character framing helpers: the camera sits in front of him (towards -x / road side).
const ME_HEAD = () => ME_POS.clone().add(V(0, 1.71, 0));
const faceToward = (from, to) => Math.atan2(to.x - from.x, to.z - from.z);

// Close-up on "me": camera at `dist` from the head, `az` radians off his facing
// direction, `dy` above/below eye line. He faces FACE so the tow chain (+x) sits behind him.
const FACE = -1.15;
// `headY` = where the head sits in frame (fraction from the top), clear of the call card.
function meCam(t, p, { dist, az = -0.42, dy = -0.05, fov = 32, roll = 0, push = 0.12, headY = 0.42 }) {
  const h = ME_HEAD(), d = dist * (1 - push * eIO(p)), a = FACE + az;
  const pos = h.clone().add(V(Math.sin(a) * d, dy, Math.cos(a) * d));
  const half = d * Math.tan((fov * Math.PI) / 360);
  setCam(pos, h.clone().add(V(0, -(0.5 - headY) * 2 * half, 0)), fov, roll);
}

// Each shot: (t, lt, p, dur) -> sets camera + per-shot state; returns ui flags.
const SHOTS = {
  establish(t, lt, p) {
    SHOT_STATE.traffic = true;
    posePerson(t, { mood: -0.2, face: faceToward(ME_POS, V(0, 0, 0)), look: 0 });
    const e = eIO(p);
    setCam(lerpV(V(-21, 13, 19), V(-9.8, 2.9, 8.8), e), lerpV(V(0.5, 0.4, -1), V(-0.8, 1.1, 0), e), 38);
  },
  call1(t, lt, p) {
    posePerson(t, { phone: eOut(k(lt, 0.0, 0.35)), mood: 0, talk: speaking(t), face: FACE });
    meCam(t, p, { dist: 3.3, az: -0.45, dy: 0.0, fov: 34, headY: 0.4 });
  },
  load(t, lt, p) {
    SHOT_STATE.traffic = false;
    posePerson(t, { phone: 0, face: 1.4, mood: 0.1 });
    setCam(lerpV(V(-1, 3.6, 17.5), V(1.5, 3.2, 15.5), eIO(p)), lerpV(V(4, 1.2, 0), V(5, 1.3, 0), eIO(p)), 42);
  },
  break1(t, lt, p) {
    posePerson(t, { face: 1.5, mood: 0.2 });
    const x = truckRear(0, t);
    const sh = shake(t, BREAK[0], 0.18);
    setCam(V(x + 1.0, 2.2, 12.5).add(sh), V(x + 4.6, 1.8, 0), 44);
  },
  call2(t, lt, p) {
    posePerson(t, { phone: eOut(k(lt, 0.1, 0.45)), mood: 0.35, talk: speaking(t), face: FACE });
    meCam(t, p, { dist: 2.6, az: 0.35, dy: 0.1, fov: 32, roll: 0.04, headY: 0.41 });
  },
  hitch2(t, lt, p) {
    const gx = truckFront(0, t) + 1.0;
    setCam(lerpV(V(gx - 3.5, 1.1, 8.5), V(gx - 2.5, 1.3, 7.2), eIO(p)), V(gx + 1.5, 1.4, 0), 46);
    posePerson(t, { face: 1.5 });
  },
  break2(t, lt, p) {
    const fx = truckFront(1, t);
    const sh = shake(t, BREAK[1], 0.25);
    setCam(lerpV(V(fx + 9, 4.2, 15), V(fx + 7, 3.6, 13), eIO(p)).add(sh), V(fx - 5, 1.6, 0), 42);
    posePerson(t, { face: 1.5 });
  },
  call3(t, lt, p) {
    posePerson(t, { phone: 1, mood: 0.6, talk: speaking(t), face: FACE, sweat: 1 });
    meCam(t, p, { dist: 2.0, az: -0.5, dy: 0.0, fov: 32, roll: -0.07, headY: 0.42 });
  },
  hitch3(t, lt, p) {
    const gx = truckFront(1, t) + 1.2;
    setCam(lerpV(V(gx - 6, 15, 12), V(gx - 3, 12, 10), eIO(p)), V(gx + 2, 0.5, 0), 44);
    posePerson(t, { face: 1.5 });
  },
  break3(t, lt, p) {
    const fx = truckFront(2, t);
    const sh = shake(t, BREAK[2], 0.25);
    setCam(lerpV(V(fx + 8, 1.0, 6.5), V(fx + 6.5, 1.3, 6.0), eIO(p)).add(sh), V(fx - 1, 2.6, 0), 46);
    posePerson(t, { face: 1.5 });
  },
  call4(t, lt, p) {
    posePerson(t, { phone: 1, mood: 0.85, talk: speaking(t), face: FACE, sweat: 1 });
    meCam(t, p, { dist: 2.3, az: 0.3, dy: -0.7, fov: 36, roll: 0.09, headY: 0.4 });
  },
  hitch4(t, lt, p) {
    const fx = truckFront(2, t);
    setCam(lerpV(V(fx - 7, 3.2, 7.5), V(fx - 5, 3.0, 7.2), eIO(p)), V(fx + 7, 2.2, 0), 44);
    posePerson(t, { face: 1.5 });
  },
  break4(t, lt, p) {
    const fx = truckFront(3, t);
    const sh = shake(t, BREAK[3], 0.35);
    setCam(lerpV(V(fx + 3, 2.6, 13), V(fx + 2, 2.4, 12), eIO(p)).add(sh), V(fx - 4, 2.4, 0), 44);
    posePerson(t, { face: 1.5 });
  },
  call5(t, lt, p) {
    posePerson(t, { phone: 1, mood: 1, talk: speaking(t), face: FACE, sweat: 1 });
    meCam(t, p, { dist: 1.5, az: -0.2, dy: -0.05, fov: 32, roll: -0.11, push: 0.16, headY: 0.44 });
  },
  hitch5(t, lt, p) {
    const fx = truckFront(3, t);
    setCam(lerpV(V(fx - 0.5, 0.8, 9.5), V(fx + 0.5, 0.9, 8.5), eIO(p)), V(fx + 8, 3.0, 0), 48);
    posePerson(t, { face: 1.5 });
  },
  reveal(t, lt, p) {
    SHOT_STATE.traffic = true;
    // drone rises behind the car and looks down the whole dead convoy
    const r0 = car.root.position.x, f4 = truckFront(4, t), e = eIO(p);
    const mid = (r0 + f4) / 2;
    setCam(lerpV(V(r0 - 9, 4.5, 11), V(r0 - 20, 22, 24), e), lerpV(V(r0 + 14, 1.5, -1), V(mid + 6, 0, -3), e), 44);
    posePerson(t, { face: 1.5, mood: 0.6 });
  },
  still(t, lt, p) {
    SHOT_STATE.traffic = false;
    const cx = car.root.position.x;
    setCam(lerpV(V(cx - 4.2, 3.0, 10.5), V(cx - 3.0, 2.8, 8.6), eIO(p)), V(cx + 0.6, 1.9, 0), 40);
    posePerson(t, { face: 1.5, mood: 0.6 });
  },
  facepalm(t, lt, p) {
    posePerson(t, { palm: eOut(k(lt, 0.05, 0.45)), mood: -0.6, face: FACE + 0.25 });
    const h = ME_HEAD(), e = eIO(p);
    // over-the-shoulder-ish: him on the left third, the dead chain trailing off to the right
    setCam(lerpV(h.clone().add(V(-3.6, 0.15, 3.9)), h.clone().add(V(-3.0, 0.1, 3.3)), e), h.clone().add(V(1.6, -0.35, -0.9)), 36);
  },
};

// ---------------------------------------------------------------- 2D overlay
const ui = document.getElementById('ui');
ui.width = W; ui.height = H;
const g = ui.getContext('2d');
const FONT = '"Inter Display", Inter, sans-serif';

// caption chunks: up to 4 words, break on punctuation or pauses
const chunks = [];
{
  let cur = [];
  TL.words.forEach((w, i) => {
    const prev = TL.words[i - 1];
    if (cur.length && (cur.length >= 4 || /[.,?!]$/.test(prev.w) || w.t0 - prev.t1 > 0.45)) { chunks.push(cur); cur = []; }
    cur.push(w);
  });
  if (cur.length) chunks.push(cur);
  chunks.forEach((c, i) => { c.start = c[0].t0 - 0.02; c.end = i + 1 < chunks.length ? Math.min(chunks[i + 1][0].t0 - 0.02, c[c.length - 1].t1 + 0.9) : c[c.length - 1].t1 + 1.2; });
}
function rr(x, y, w, h, r) { g.beginPath(); g.roundRect(x, y, w, h, r); }

function drawCaption(t) {
  const c = chunks.find((ch) => t >= ch.start && t < ch.end);
  if (!c) return;
  const size = 64 * S;
  g.font = `800 ${size}px ${FONT}`;
  const padX = 16 * S, gap = 16 * S;
  const items = c.map((w) => ({ ...w, text: w.w.replace(/[.,?!]+$/, '').toLowerCase(), width: g.measureText(w.w.replace(/[.,?!]+$/, '').toLowerCase()).width + (w.style ? padX * 2 : 0) }));
  // wrap to lines
  const maxW = 920 * S, lines = [[]]; let lw = 0;
  for (const it of items) {
    if (lw && lw + gap + it.width > maxW) { lines.push([]); lw = 0; }
    lines[lines.length - 1].push(it); lw += (lw ? gap : 0) + it.width;
  }
  const lh = size * 1.32;
  let y = H * 0.635 - ((lines.length - 1) * lh) / 2;
  for (const line of lines) {
    const total = line.reduce((a, it) => a + it.width, 0) + gap * (line.length - 1);
    let x = (W - total) / 2;
    for (const it of line) {
      const a = k(t, it.t0 - 0.03, it.t0 + 0.05);
      if (a > 0) {
        const sc = 0.72 + 0.28 * eBack(k(t, it.t0 - 0.03, it.t0 + 0.13));
        g.save();
        g.translate(x + it.width / 2, y);
        g.scale(sc, sc);
        g.globalAlpha = a;
        g.textAlign = 'center'; g.textBaseline = 'middle';
        if (it.style) {
          g.fillStyle = it.style === 'red' ? '#ff4545' : '#ffd23f';
          g.shadowColor = 'rgba(0,0,0,0.35)'; g.shadowBlur = 14 * S; g.shadowOffsetY = 4 * S;
          rr(-it.width / 2, -size * 0.62, it.width, size * 1.2, 18 * S); g.fill();
          g.shadowColor = 'transparent';
          g.fillStyle = it.style === 'red' ? '#ffffff' : '#17171b';
          g.fillText(it.text, 0, size * 0.02);
        } else {
          g.shadowColor = 'rgba(0,0,0,0.65)'; g.shadowBlur = 16 * S; g.shadowOffsetY = 3 * S;
          g.lineWidth = 7 * S; g.strokeStyle = 'rgba(15,15,20,0.55)'; g.lineJoin = 'round';
          g.strokeText(it.text, 0, size * 0.02);
          g.shadowColor = 'transparent';
          g.fillStyle = '#ffffff'; g.fillText(it.text, 0, size * 0.02);
        }
        g.restore();
      }
      x += it.width + gap;
    }
    y += lh;
  }
}

function truckIcon(x, y, s, color = '#f4b400') {
  g.save(); g.translate(x, y); g.scale(s, s);
  g.fillStyle = color;
  rr(-34, -10, 44, 16, 3); g.fill();              // bed
  rr(10, -22, 22, 28, 5); g.fill();               // cab
  g.fillStyle = '#1b2a38'; rr(20, -18, 9, 10, 2); g.fill();
  g.fillStyle = '#111'; for (const wx of [-22, -8, 22]) { g.beginPath(); g.arc(wx, 8, 7, 0, Math.PI * 2); g.fill(); }
  g.fillStyle = '#ff9d00'; rr(14, -27, 14, 5, 2); g.fill();
  g.restore();
}

const CALL_NAMES = ['Towing 24 Jam', 'Towing Express', 'Towing Laju Gila', 'Towing Mega', 'Towing GIGA'];
const CALL_SHOTS = ['call1', 'call2', 'call3', 'call4', 'call5'];
function drawCallCard(t, shot) {
  const n = CALL_SHOTS.indexOf(shot.id);
  if (n < 0) return;
  const lt = t - shot.start, rem = shot.end - t;
  const a = eOut(k(lt, 0, 0.22)) * k(rem, 0, 0.12);
  const y = 300 * S - (1 - eOut(k(lt, 0, 0.25))) * 60 * S;
  const w = 780 * S, h = 156 * S, x = (W - w) / 2;
  g.save(); g.globalAlpha = a;
  g.shadowColor = 'rgba(0,0,0,0.35)'; g.shadowBlur = 30 * S; g.shadowOffsetY = 10 * S;
  g.fillStyle = 'rgba(24,25,30,0.9)'; rr(x, y, w, h, 44 * S); g.fill();
  g.shadowColor = 'transparent';
  // avatar
  g.fillStyle = '#2e3038'; g.beginPath(); g.arc(x + 84 * S, y + h / 2, 52 * S, 0, Math.PI * 2); g.fill();
  truckIcon(x + 82 * S, y + h / 2 + 6 * S, 1.25 * S);
  g.textAlign = 'left'; g.textBaseline = 'alphabetic';
  g.fillStyle = '#ffffff'; g.font = `800 ${42 * S}px ${FONT}`;
  g.fillText(CALL_NAMES[n], x + 160 * S, y + 68 * S);
  const dots = '.'.repeat(1 + (Math.floor(t * 4) % 3));
  g.fillStyle = '#a7abb6'; g.font = `600 ${30 * S}px ${FONT}`;
  g.fillText(`memanggil${dots}   lori #${n + 1}`, x + 160 * S, y + 112 * S);
  // pulsing green call button
  const cx = x + w - 84 * S, cy = y + h / 2, pulse = (t / BEAT) % 1;
  g.fillStyle = `rgba(52,199,89,${0.35 * (1 - pulse)})`;
  g.beginPath(); g.arc(cx, cy, (44 + pulse * 26) * S, 0, Math.PI * 2); g.fill();
  g.fillStyle = '#34c759'; g.beginPath(); g.arc(cx, cy, 44 * S, 0, Math.PI * 2); g.fill();
  // handset glyph
  g.save(); g.translate(cx, cy); g.rotate(-0.75); g.fillStyle = '#fff';
  rr(-20 * S, -7 * S, 40 * S, 14 * S, 7 * S); g.fill();
  rr(-24 * S, -7 * S, 12 * S, 22 * S, 5 * S); g.fill(); rr(12 * S, -7 * S, 12 * S, 22 * S, 5 * S); g.fill();
  g.restore();
  g.restore();
}

function drawTally(t) {
  const calls = EV.calls;
  const n = calls.filter((c) => t >= c).length;
  if (!n) return;
  const tn = calls[n - 1];
  const pop = 1 + 0.25 * (1 - eOut(k(t, tn, tn + 0.3)));
  const a = eOut(k(t, calls[0], calls[0] + 0.25));
  const x = 44 * S, y = 150 * S, w = 400 * S, h = 116 * S;
  g.save(); g.globalAlpha = a;
  g.fillStyle = 'rgba(20,21,26,0.82)'; rr(x, y, w, h, 26 * S); g.fill();
  truckIcon(x + 70 * S, y + h / 2 + 6 * S, 1.3 * S);
  g.fillStyle = '#c9ccd4'; g.font = `700 ${27 * S}px ${FONT}`; g.textAlign = 'left'; g.textBaseline = 'alphabetic';
  g.fillText('LORI TOWING', x + 132 * S, y + 46 * S);
  g.save(); g.translate(x + 132 * S, y + 96 * S); g.scale(pop, pop);
  g.fillStyle = '#ffd23f'; g.font = `900 ${50 * S}px ${FONT}`; g.fillText(`× ${n}`, 0, 0);
  g.restore();
  const broke = EV.break.filter((b) => t >= b).length;
  if (broke) {
    g.fillStyle = '#ff5a4f'; g.font = `800 ${28 * S}px ${FONT}`;
    g.fillText(`${broke} rosak`, x + 250 * S, y + 92 * S);
  }
  // final gag row
  const tg = EV.gag;
  if (t >= tg) {
    const b = eOut(k(t, tg, tg + 0.3));
    const y2 = y + h + 14 * S;
    g.globalAlpha = a * b;
    g.fillStyle = 'rgba(20,21,26,0.82)'; rr(x, y2, w + 40 * S, 90 * S, 24 * S); g.fill();
    g.fillStyle = '#c9ccd4'; g.font = `700 ${27 * S}px ${FONT}`; g.fillText('BENGKEL', x + 28 * S, y2 + 56 * S);
    g.fillStyle = '#ff5a4f'; g.font = `900 ${42 * S}px ${FONT}`; g.fillText('masih 42 km', x + 172 * S, y2 + 60 * S);
  }
  g.restore();
}

function drawFlash(t) {
  for (const b of EV.break) {
    const d = t - b;
    if (d >= 0 && d < 0.12) { g.fillStyle = `rgba(255,255,255,${0.35 * (1 - d / 0.12)})`; g.fillRect(0, 0, W, H); }
  }
}

// ---------------------------------------------------------------- frame
function shotAt(t) { return TL.shots.find((s) => t >= s.start && t < s.end) || TL.shots[TL.shots.length - 1]; }
window.renderAt = (t) => {
  const shot = shotAt(t);
  const lt = t - shot.start, dur = shot.end - shot.start;
  SHOT_STATE.traffic = false;
  SHOTS[shot.id](t, lt, clamp(lt / dur), dur);
  updateWorld(t);
  // small zoom punch on every cut
  camera.fov *= 1 - 0.045 * (1 - eOut(k(lt, 0, 0.3)));
  camera.updateProjectionMatrix();
  renderer.render(scene, camera);
  g.clearRect(0, 0, W, H);
  drawFlash(t);
  drawTally(t);
  drawCallCard(t, shot);
  drawCaption(t);
};

await document.fonts.load(`800 64px "Inter Display"`);
await document.fonts.load(`900 64px "Inter Display"`);
window.renderAt(0);
window.sceneReady = true;
