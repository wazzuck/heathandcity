/**
 * ============================================================================
 * FILE: js/gpu-scene.js
 * ============================================================================
 *
 * PURPOSE:
 * Implements the interactive Three-Dimensional (3D) visual centrepiece for
 * the Hampstead & North West (NW) London consulting website. Detects Web
 * Graphics Processing Unit (WebGPU) hardware support, pairs it with a custom
 * Three.js Web Graphics Library (WebGL) shader and geometry pipeline, and
 * provides a self-contained Two-Dimensional (2D) Canvas 3D projection fallback
 * plus a static reduced-motion fallback.
 *
 * WHAT THIS FILE IS NOT FOR:
 * - Does not use SharedArrayBuffer, Cross-Origin Opener Policy (COOP), or
 *   Cross-Origin Embedder Policy (COEP) headers.
 * - Does not perform multi-threaded WebAssembly (WASM) CPU compute.
 * - Does not mutate business copy outside the canvas and telemetry readout.
 *
 * INVARIANTS:
 * 1. Always degrades gracefully across four tiers:
 *    Tier 1: WebGPU Device + Three.js Custom Shader Pipeline.
 *    Tier 2: Three.js WebGL2 Custom Shader Pipeline.
 *    Tier 3: Built-in Zero-Dependency 3D Perspective Canvas Engine.
 *    Tier 4: Static Architectural Fallback (when reduced motion is active).
 * 2. Maintains smooth frame pacing via requestAnimationFrame and pauses
 *    automatically when the browser tab is hidden.
 * 3. Responds immediately to scene switches ("lattice", "vault", "telemetry"),
 *    the Entropy-to-Order ratio slider ([0.0, 1.0]), pointer movement, and
 *    shockwave pulse triggers.
 * ============================================================================
 */

import { SCENE_MODES } from "./config.js";

/**
 * Step 1: Define numerical constants and magic numbers.
 * Every constant states its meaning, units, value, and consumer.
 */

// Total number of GPU-animated data particles in the Three.js shader cloud.
// Value: 7200 particles. Consumed by: buildParticleBuffers().
const PARTICLE_COUNT_GPU = 7200;

// Total number of projected 3D particles in the zero-dependency Canvas engine.
// Value: 950 particles. Consumed by: initCanvas3DFallback().
const PARTICLE_COUNT_CANVAS = 950;

// Number of floating 3D architectural document polyhedra in the Three.js scene.
// Value: 28 meshes. Consumed by: buildArchitecturalMeshes().
const DOCUMENT_NODE_COUNT = 28;

// Camera perspective vertical field of view in degrees.
// Value: 50 degrees. Consumed by: initThreePipeline().
const CAMERA_FOV_DEGREES = 50;

// Camera default distance along the positive Z axis in world units.
// Value: 18.5 world units. Consumed by: initThreePipeline().
const CAMERA_DISTANCE_Z = 18.5;

// Maximum device pixel ratio to cap fill-rate cost on 4K/Retina displays.
// Value: 2.0x pixel density. Consumed by: handleResize().
const MAX_PIXEL_RATIO = 2.0;

// Interpolation speed factor for smooth transitions between scene topologies.
// Value: 3.2 per second (dimensionless damping rate). Consumed by: animate().
const TOPOLOGY_LERP_RATE = 3.2;

// Duration in seconds of an interactive neural/reconciliation shockwave pulse.
// Value: 1.8 seconds. Consumed by: triggerPulse() and animate().
const PULSE_DURATION_SECONDS = 1.8;

// CDN Uniform Resource Locator (URL) for the Three.js ES module (v0.170.0).
// Consumed by: loadThreeModule().
const THREE_CDN_URL =
  "https://cdn.jsdelivr.net/npm/three@0.170.0/build/three.module.js";

/**
 * Step 2: Define the WebGPU Shading Language (WGSL) verification shader.
 * Compiled on the client's GPUDevice when navigator.gpu is available to confirm
 * hardware shader compilation capability without requiring COOP/COEP headers.
 */
const WEBGPU_PROBE_WGSL = /* wgsl */ `
  struct VertexOut {
    @builtin(position) position : vec4<f32>,
    @location(0) colour : vec4<f32>,
  };

  @vertex
  fn vs_main(@builtin(vertex_index) idx : u32) -> VertexOut {
    var pos = array<vec2<f32>, 3>(
      vec2<f32>(0.0, 0.5),
      vec2<f32>(-0.5, -0.5),
      vec2<f32>(0.5, -0.5)
    );
    var out : VertexOut;
    out.position = vec4<f32>(pos[idx], 0.0, 1.0);
    out.colour = vec4<f32>(0.83, 0.68, 0.41, 1.0);
    return out;
  }

  @fragment
  fn fs_main(in : VertexOut) -> @location(0) vec4<f32> {
    return in.colour;
  }
`;

/**
 * Step 3: Define the GLSL Vertex Shader for the Three.js particle system.
 * Blends between chaotic entropy positions and three ordered target topologies
 * ("lattice", "vault", and "telemetry") directly on the GPU.
 */
const PARTICLE_VERTEX_SHADER = /* glsl */ `
  attribute vec3 aChaosPos;
  attribute vec3 aLatticePos;
  attribute vec3 aVaultPos;
  attribute vec3 aTelemetryPos;
  attribute float aPhase;
  attribute float aScale;
  attribute float aColorMix;

  uniform float uTime;
  uniform float uOrder;
  uniform float uModeWeights[3];
  uniform vec2 uPointer;
  uniform float uPulse;
  uniform float uPixelRatio;

  varying float vColorMix;
  varying float vAlpha;
  varying float vPulseHighlight;

  void main() {
    // 1. Compute the ordered target coordinate by blending the three scene
    //    topologies according to uModeWeights[0..2].
    vec3 orderedTarget =
      aLatticePos * uModeWeights[0] +
      aVaultPos * uModeWeights[1] +
      aTelemetryPos * uModeWeights[2];

    // 2. Add subtle breathing harmonic motion to the ordered state.
    float wave = sin(uTime * 1.35 + aPhase * 6.2831) * 0.14;
    orderedTarget.y += wave;

    // 3. Compute the swirling chaotic inbox/document storm coordinate.
    float swirlAngle = uTime * (0.45 + aColorMix * 0.35) + aPhase * 6.2831;
    vec3 chaosSwirl = aChaosPos;
    chaosSwirl.x += cos(swirlAngle) * 0.85;
    chaosSwirl.y += sin(swirlAngle * 1.3) * 0.85;
    chaosSwirl.z += sin(swirlAngle * 0.7) * 0.65;

    // 4. Interpolate between Chaos (0.0) and Order (1.0) using smoothstep.
    float smoothOrder = smoothstep(0.0, 1.0, clamp(uOrder, 0.0, 1.0));
    vec3 pos = mix(chaosSwirl, orderedTarget, smoothOrder);

    // 5. Apply radial shockwave pulse when the user triggers reconciliation.
    float distFromCentre = length(pos.xy);
    float pulseRing = abs(distFromCentre - uPulse * 11.0);
    float pulseEffect = smoothstep(1.8, 0.0, pulseRing) *
                        (1.0 - smoothstep(0.75, 1.0, uPulse)) *
                        step(0.001, uPulse);
    pos += normalize(pos + vec3(0.001)) * pulseEffect * 0.75;

    // 6. Apply gentle pointer field attraction in Normalized Device Space.
    vec2 pointerWorld = uPointer * vec2(7.0, 4.5);
    float pointerDist = length(pos.xy - pointerWorld);
    float pointerInfluence = smoothstep(3.8, 0.0, pointerDist);
    pos.z += pointerInfluence * 0.95;

    vec4 mvPosition = modelViewMatrix * vec4(pos, 1.0);
    gl_Position = projectionMatrix * mvPosition;

    // 7. Compute perspective-attenuated point size.
    float baseSize = (2.6 + aScale * 3.8 + pulseEffect * 3.2 +
                      pointerInfluence * 2.2) * uPixelRatio;
    gl_PointSize = clamp(baseSize * (16.0 / -mvPosition.z), 1.5, 22.0);

    vColorMix = aColorMix;
    vPulseHighlight = max(pulseEffect, pointerInfluence * 0.7);
    vAlpha = mix(0.48, 0.92, smoothOrder) + vPulseHighlight * 0.25;
  }
`;

/**
 * Step 4: Define the GLSL Fragment Shader for the Three.js particle system.
 * Renders soft circular luminous nodes with a high-contrast core and metallic
 * brass/emerald/sapphire halo.
 */
const PARTICLE_FRAGMENT_SHADER = /* glsl */ `
  uniform vec3 uPrimaryColor;
  uniform vec3 uSecondaryColor;

  varying float vColorMix;
  varying float vAlpha;
  varying float vPulseHighlight;

  void main() {
    // 1. Measure radial distance from the centre of the point sprite.
    vec2 uv = gl_PointCoord.xy - vec2(0.5);
    float dist = length(uv);
    if (dist > 0.5) {
      discard;
    }

    // 2. Create a crisp inner core with a soft atmospheric glow halo.
    float core = smoothstep(0.5, 0.06, dist);
    float hotCentre = smoothstep(0.22, 0.0, dist);

    // 3. Blend between the scene's primary and secondary metallic colours.
    vec3 baseColour = mix(uPrimaryColor, uSecondaryColor, vColorMix);
    vec3 highlightColour = vec3(1.0, 0.97, 0.88);
    vec3 finalColour = mix(
      baseColour,
      highlightColour,
      hotCentre * 0.55 + vPulseHighlight * 0.45
    );

    gl_FragColor = vec4(finalColour, core * clamp(vAlpha, 0.0, 1.0));
  }
`;

/**
 * Step 5: Define deterministic pseudo-random generator for reproducible 3D
 * coordinates across sessions and rendering backends.
 *
 * @param {number} seed - Initial integer seed (> 0).
 * @returns {function(): number} Generator returning floats in [0.0, 1.0).
 */
function createSeededRandom(seed) {
  let state = seed >>> 0;
  return function nextFloat() {
    // 1. Advance state with xorshift32 bit mixing.
    state ^= state << 13;
    state ^= state >>> 17;
    state ^= state << 5;
    // 2. Normalise unsigned 32-bit integer into [0.0, 1.0).
    return (state >>> 0) / 4294967296;
  };
}

/**
 * Step 6: Compute the mathematical coordinates for a single particle across
 * all four topological states (Chaos, Lattice, Vault, Telemetry).
 *
 * @param {number} index - Zero-based particle index.
 * @param {number} total - Total number of particles in the cloud.
 * @param {function(): number} rand - Seeded random number generator.
 * @returns {{
 *   chaos: [number, number, number],
 *   lattice: [number, number, number],
 *   vault: [number, number, number],
 *   telemetry: [number, number, number],
 *   phase: number,
 *   scale: number,
 *   colorMix: number
 * }} Coordinate set in world space units (roughly [-9, +9]).
 */
function computeParticleTopologies(index, total, rand) {
  // 1. Generate Chaos coordinate (turbulent outer cloud representing raw
  //    unsorted emails, scanned PDFs, and unindexed attachments).
  const radiusChaos = 3.2 + rand() * 6.8;
  const thetaChaos = rand() * Math.PI * 2.0;
  const phiChaos = Math.acos(2.0 * rand() - 1.0);
  const chaosX = radiusChaos * Math.sin(phiChaos) * Math.cos(thetaChaos) * 1.35;
  const chaosY = radiusChaos * Math.sin(phiChaos) * Math.sin(thetaChaos) * 0.95;
  const chaosZ = radiusChaos * Math.cos(phiChaos) * 0.85;

  // 2. Generate Mode 1 ("lattice") coordinate: a structured 3D architectural
  //    ledger grid with a central circular normalisation aperture.
  const cols = 30;
  const rows = 18;
  const layers = Math.max(1, Math.floor(total / (cols * rows)));
  const col = index % cols;
  const row = Math.floor(index / cols) % rows;
  const layer = Math.floor(index / (cols * rows)) % layers;
  const gridX = ((col / (cols - 1)) - 0.5) * 13.2;
  const gridY = ((row / (rows - 1)) - 0.5) * 7.4;
  const gridZ = ((layer / Math.max(1, layers - 1)) - 0.5) * 3.4;

  // 3. Generate Mode 2 ("vault") coordinate: Two-Tower neural embedding rings
  //    surrounding a sovereign central spherical core.
  const u = index / total;
  let vaultX = 0;
  let vaultY = 0;
  let vaultZ = 0;
  if (u < 0.42) {
    // Inner Fibonacci geodesic sphere representing the Sovereign Vault core.
    const sphereIdx = index;
    const sphereTotal = Math.floor(total * 0.42);
    const goldenAngle = Math.PI * (3.0 - Math.sqrt(5.0));
    const yNorm = 1.0 - (sphereIdx / Math.max(1, sphereTotal - 1)) * 2.0;
    const rRing = Math.sqrt(Math.max(0.0, 1.0 - yNorm * yNorm));
    const angle = goldenAngle * sphereIdx;
    const coreRadius = 2.65 + (sphereIdx % 3) * 0.28;
    vaultX = Math.cos(angle) * rRing * coreRadius;
    vaultY = yNorm * coreRadius;
    vaultZ = Math.sin(angle) * rRing * coreRadius;
  } else {
    // Outer Two-Tower orbital helices and containment shield rings.
    const orbitIdx = index - Math.floor(total * 0.42);
    const ringIndex = orbitIdx % 4;
    const ringRadius = 4.1 + ringIndex * 1.15;
    const orbitAngle = (orbitIdx * 0.17) + ringIndex * 0.8;
    const tilt = (ringIndex - 1.5) * 0.42;
    vaultX = Math.cos(orbitAngle) * ringRadius;
    vaultY =
      Math.sin(orbitAngle) * Math.sin(tilt) * ringRadius +
      Math.cos(orbitAngle * 3.0) * 0.35;
    vaultZ = Math.sin(orbitAngle) * Math.cos(tilt) * ringRadius * 0.72;
  }

  // 4. Generate Mode 3 ("telemetry") coordinate: Hampstead Heath topographical
  //    elevation contours fused with City market-data stream ribbons.
  const streamCount = 16;
  const streamId = index % streamCount;
  const streamStep = Math.floor(index / streamCount);
  const maxSteps = Math.ceil(total / streamCount);
  const tNorm = (streamStep / Math.max(1, maxSteps - 1)) * 2.0 - 1.0;
  const sNorm = (streamId / (streamCount - 1)) * 2.0 - 1.0;
  const teleX = tNorm * 7.8;
  const ridgeElevation =
    Math.sin(tNorm * 3.6 + sNorm * 1.8) * 1.35 +
    Math.cos(tNorm * 6.2 - sNorm * 2.4) * 0.55;
  const teleY = ridgeElevation + sNorm * 1.15;
  const teleZ = sNorm * 4.4;

  return {
    chaos: [chaosX, chaosY, chaosZ],
    lattice: [gridX, gridY, gridZ],
    vault: [vaultX, vaultY, vaultZ],
    telemetry: [teleX, teleY, teleZ],
    phase: rand(),
    scale: 0.4 + rand() * 0.9,
    colorMix: (index % 7) / 6.0
  };
}

/**
 * Step 7: Define the GPUSceneController class.
 * Manages WebGPU probing, Three.js / Canvas rendering, mode transitions,
 * pointer interaction, and telemetry callbacks.
 */
export class GPUSceneController {
  /**
   * Construct a new GPUSceneController.
   *
   * @param {Object} options - Configuration object.
   * @param {HTMLCanvasElement} options.canvas - Target HTML5 canvas element.
   * @param {function(Object): void} [options.onStatusChange] - Callback invoked
   *   whenever the rendering tier, Frames Per Second (FPS), or scene state
   *   updates.
   */
  constructor({ canvas, onStatusChange }) {
    // 1. Store DOM references and callback hooks.
    this.canvas = canvas;
    this.onStatusChange = onStatusChange || (() => {});

    // 2. Initialise simulation parameters.
    this.currentMode = "lattice";
    this.orderRatio = SCENE_MODES.lattice.defaultOrder;
    this.targetOrderRatio = this.orderRatio;
    this.modeWeights = [1.0, 0.0, 0.0];
    this.targetModeWeights = [1.0, 0.0, 0.0];

    // 3. Initialise pointer and pulse interaction state.
    this.pointer = { x: 0.0, y: 0.0, targetX: 0.0, targetY: 0.0 };
    this.pulseProgress = 0.0;
    this.pulseActive = false;
    this.scrollProgress = 0.0;

    // 4. Initialise hardware and loop state.
    this.engineTier = "INITIALISING";
    this.webgpuAvailable = false;
    this.webgpuAdapterName = "Standard Pipeline";
    this.isPaused = false;
    this.rafId = null;
    this.lastFrameTime = performance.now();
    this.fpsSmoothed = 60;

    // 5. Bind event listeners so they can be cleanly attached and removed.
    this.handleResize = this.handleResize.bind(this);
    this.handlePointerMove = this.handlePointerMove.bind(this);
    this.handleVisibilityChange = this.handleVisibilityChange.bind(this);
    this.animate = this.animate.bind(this);
  }

  /**
   * Probe client graphics capabilities, initialise the best supported
   * rendering backend, and start the animation loop.
   *
   * @returns {Promise<void>} Resolves once the engine is running.
   */
  async init() {
    // 1. Check whether the user has requested reduced motion at the OS level.
    const prefersReducedMotion =
      window.matchMedia &&
      window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    // 2. Probe WebGPU support via navigator.gpu without requiring any special
    //    cross-origin headers.
    await this.probeWebGPU();

    // 3. Attach viewport resize, pointer, and visibility listeners.
    window.addEventListener("resize", this.handleResize, { passive: true });
    window.addEventListener("pointermove", this.handlePointerMove, {
      passive: true
    });
    document.addEventListener("visibilitychange", this.handleVisibilityChange);

    // 4. Attempt to initialise the Three.js 3D shader pipeline; if unavailable
    //    (for example offline or WebGL disabled), fall back to the built-in
    //    3D perspective Canvas engine.
    let threeStarted = false;
    try {
      threeStarted = await this.initThreePipeline();
    } catch (_error) {
      threeStarted = false;
    }

    if (!threeStarted) {
      this.initCanvas3DFallback();
    }

    // 5. Perform initial layout sizing and render the first frame.
    this.handleResize();

    if (prefersReducedMotion) {
      this.isPaused = true;
      this.renderSingleFrame(0.016);
      this.emitStatus("REDUCED MOTION (STATIC FRAME)");
    } else {
      this.lastFrameTime = performance.now();
      this.rafId = requestAnimationFrame(this.animate);
    }
  }

  /**
   * Probe navigator.gpu, request a hardware adapter and device, and compile
   * the verification WGSL shader module.
   *
   * @returns {Promise<void>}
   */
  async probeWebGPU() {
    if (typeof navigator === "undefined" || !("gpu" in navigator)) {
      this.webgpuAvailable = false;
      return;
    }
    try {
      // 1. Request a high-performance WebGPU adapter.
      const adapter = await navigator.gpu.requestAdapter({
        powerPreference: "high-performance"
      });
      if (!adapter) {
        this.webgpuAvailable = false;
        return;
      }

      // 2. Request a logical GPUDevice and compile our WGSL shader probe.
      const device = await adapter.requestDevice();
      const shaderModule = device.createShaderModule({
        label: "HeathAndCityWebGPUProbe",
        code: WEBGPU_PROBE_WGSL
      });

      if (shaderModule) {
        this.webgpuAvailable = true;
        this.webgpuDevice = device;
        const info = adapter.info || {};
        this.webgpuAdapterName =
          info.description || info.vendor || "WebGPU Hardware Device";
      }
    } catch (_err) {
      this.webgpuAvailable = false;
    }
  }

  /**
   * Dynamically load Three.js and construct the 3D scene, custom shader
   * particle cloud, wireframe normalisation rings, and floating document nodes.
   *
   * @returns {Promise<boolean>} True if Three.js initialised successfully.
   */
  async initThreePipeline() {
    if (!this.canvas) {
      return false;
    }

    // 1. Dynamically import Three.js from the configured CDN.
    const THREE = await import(THREE_CDN_URL);
    this.THREE = THREE;

    // 2. Create the WebGLRenderer with alpha transparency and antialiasing.
    const renderer = new THREE.WebGLRenderer({
      canvas: this.canvas,
      antialias: true,
      alpha: true,
      powerPreference: "high-performance"
    });
    renderer.setClearColor(0x000000, 0);
    this.renderer = renderer;

    // 3. Create the 3D Scene and PerspectiveCamera.
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(
      CAMERA_FOV_DEGREES,
      1.0,
      0.1,
      120.0
    );
    camera.position.set(0, 0.4, CAMERA_DISTANCE_Z);
    this.scene = scene;
    this.camera = camera;

    // 4. Create a master root group that responds to pointer parallax.
    const rootGroup = new THREE.Group();
    scene.add(rootGroup);
    this.rootGroup = rootGroup;

    // 5. Build the GPU shader particle cloud (7,200 particles with four
    //    embedded topological coordinate attributes).
    this.buildParticleCloud(THREE, rootGroup);

    // 6. Build the central 3D architectural gyroscope, vault core, and
    //    floating document polyhedra.
    this.buildArchitecturalMeshes(THREE, rootGroup);

    // 7. Record the active engine tier for the telemetry display.
    this.backendType = "three";
    this.engineTier = this.webgpuAvailable
      ? "WEBGPU DEVICE + THREE.JS SHADER PIPELINE"
      : "THREE.JS WEBGL2 SHADER PIPELINE";
    this.emitStatus(this.engineTier);
    return true;
  }

  /**
   * Populate the BufferGeometry and ShaderMaterial for the GPU particle cloud.
   *
   * @param {Object} THREE - Imported Three.js namespace.
   * @param {Object} parentGroup - Three.js Group to attach the Points mesh to.
   */
  buildParticleCloud(THREE, parentGroup) {
    const count = PARTICLE_COUNT_GPU;
    const rand = createSeededRandom(17042026);

    // 1. Allocate typed Float32Arrays for all vertex attributes.
    const chaosArr = new Float32Array(count * 3);
    const latticeArr = new Float32Array(count * 3);
    const vaultArr = new Float32Array(count * 3);
    const telemetryArr = new Float32Array(count * 3);
    const phaseArr = new Float32Array(count);
    const scaleArr = new Float32Array(count);
    const colorMixArr = new Float32Array(count);

    // 2. Populate coordinates for each particle across all topologies.
    for (let i = 0; i < count; i += 1) {
      const topo = computeParticleTopologies(i, count, rand);
      const i3 = i * 3;

      chaosArr[i3] = topo.chaos[0];
      chaosArr[i3 + 1] = topo.chaos[1];
      chaosArr[i3 + 2] = topo.chaos[2];

      latticeArr[i3] = topo.lattice[0];
      latticeArr[i3 + 1] = topo.lattice[1];
      latticeArr[i3 + 2] = topo.lattice[2];

      vaultArr[i3] = topo.vault[0];
      vaultArr[i3 + 1] = topo.vault[1];
      vaultArr[i3 + 2] = topo.vault[2];

      telemetryArr[i3] = topo.telemetry[0];
      telemetryArr[i3 + 1] = topo.telemetry[1];
      telemetryArr[i3 + 2] = topo.telemetry[2];

      phaseArr[i] = topo.phase;
      scaleArr[i] = topo.scale;
      colorMixArr[i] = topo.colorMix;
    }

    // 3. Bind typed arrays to a Three.js BufferGeometry.
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute("position", new THREE.BufferAttribute(latticeArr, 3));
    geometry.setAttribute("aChaosPos", new THREE.BufferAttribute(chaosArr, 3));
    geometry.setAttribute(
      "aLatticePos",
      new THREE.BufferAttribute(latticeArr, 3)
    );
    geometry.setAttribute("aVaultPos", new THREE.BufferAttribute(vaultArr, 3));
    geometry.setAttribute(
      "aTelemetryPos",
      new THREE.BufferAttribute(telemetryArr, 3)
    );
    geometry.setAttribute("aPhase", new THREE.BufferAttribute(phaseArr, 1));
    geometry.setAttribute("aScale", new THREE.BufferAttribute(scaleArr, 1));
    geometry.setAttribute(
      "aColorMix",
      new THREE.BufferAttribute(colorMixArr, 1)
    );

    // 4. Configure uniforms for the custom vertex and fragment shaders.
    const modeConfig = SCENE_MODES[this.currentMode];
    this.uniforms = {
      uTime: { value: 0.0 },
      uOrder: { value: this.orderRatio },
      uModeWeights: { value: [1.0, 0.0, 0.0] },
      uPointer: { value: new THREE.Vector2(0.0, 0.0) },
      uPulse: { value: 0.0 },
      uPixelRatio: {
        value: Math.min(window.devicePixelRatio || 1.0, MAX_PIXEL_RATIO)
      },
      uPrimaryColor: { value: new THREE.Color(modeConfig.primaryHex) },
      uSecondaryColor: { value: new THREE.Color(modeConfig.secondaryHex) }
    };

    // 5. Create the ShaderMaterial with additive glowing blending.
    const material = new THREE.ShaderMaterial({
      vertexShader: PARTICLE_VERTEX_SHADER,
      fragmentShader: PARTICLE_FRAGMENT_SHADER,
      uniforms: this.uniforms,
      transparent: true,
      depthWrite: false,
      blending: THREE.AdditiveBlending
    });

    const points = new THREE.Points(geometry, material);
    parentGroup.add(points);
    this.particleSystem = points;
  }

  /**
   * Build the 3D sculptural centrepiece meshes: the Normalisation Gyroscope
   * rings, the geodesic Sovereign Vault core, and floating document polyhedra.
   *
   * @param {Object} THREE - Imported Three.js namespace.
   * @param {Object} parentGroup - Three.js Group to attach meshes to.
   */
  buildArchitecturalMeshes(THREE, parentGroup) {
    const centreGroup = new THREE.Group();
    parentGroup.add(centreGroup);
    this.centreGroup = centreGroup;

    // 1. Build three concentric gyroscope torus rings representing the
    //    80/20 Reusable Core Normalisation Engine.
    this.gyroRings = [];
    const ringRadii = [2.85, 3.65, 4.55];
    for (let i = 0; i < ringRadii.length; i += 1) {
      const ringGeo = new THREE.TorusGeometry(ringRadii[i], 0.018, 12, 96);
      const ringMat = new THREE.MeshBasicMaterial({
        color: i === 0 ? 0xd4af6a : i === 1 ? 0x34d399 : 0x60a5fa,
        transparent: true,
        opacity: 0.36 - i * 0.07
      });
      const ringMesh = new THREE.Mesh(ringGeo, ringMat);
      ringMesh.rotation.x = i * 0.65;
      ringMesh.rotation.y = i * 0.45;
      centreGroup.add(ringMesh);
      this.gyroRings.push(ringMesh);
    }

    // 2. Build the inner wireframe icosahedron representing the Sovereign
    //    Hampstead hardware vault.
    const coreGeo = new THREE.IcosahedronGeometry(1.75, 1);
    const coreMat = new THREE.MeshBasicMaterial({
      color: 0xd4af6a,
      wireframe: true,
      transparent: true,
      opacity: 0.28
    });
    this.vaultCoreMesh = new THREE.Mesh(coreGeo, coreMat);
    centreGroup.add(this.vaultCoreMesh);

    // 3. Build floating 3D octahedron document nodes that orbit in Chaos and
    //    align into an architectural formation as Order approaches 1.0.
    this.docNodes = [];
    const docGeo = new THREE.OctahedronGeometry(0.18, 0);
    const rand = createSeededRandom(99012026);
    for (let i = 0; i < DOCUMENT_NODE_COUNT; i += 1) {
      const docMat = new THREE.MeshBasicMaterial({
        color: i % 2 === 0 ? 0xd4af6a : 0x34d399,
        wireframe: true,
        transparent: true,
        opacity: 0.55
      });
      const mesh = new THREE.Mesh(docGeo, docMat);
      const topo = computeParticleTopologies(
        i * 31,
        DOCUMENT_NODE_COUNT * 31,
        rand
      );
      mesh.userData = {
        chaos: topo.chaos,
        lattice: topo.lattice,
        vault: topo.vault,
        telemetry: topo.telemetry,
        phase: topo.phase
      };
      parentGroup.add(mesh);
      this.docNodes.push(mesh);
    }
  }

  /**
   * Initialise the self-contained 2D Canvas 3D perspective engine if Three.js
   * or WebGL is unavailable. Projects the exact same 3D topologies and rings
   * so the visual centrepiece works offline and on restricted devices.
   */
  initCanvas3DFallback() {
    this.backendType = "canvas2d";
    this.ctx2d = this.canvas ? this.canvas.getContext("2d") : null;
    const rand = createSeededRandom(17042026);
    this.canvasParticles = [];

    for (let i = 0; i < PARTICLE_COUNT_CANVAS; i += 1) {
      this.canvasParticles.push(
        computeParticleTopologies(i, PARTICLE_COUNT_CANVAS, rand)
      );
    }

    this.engineTier = this.webgpuAvailable
      ? "WEBGPU DEVICE + CANVAS 3D PROJECTION"
      : "CANVAS 3D PERSPECTIVE FALLBACK";
    this.emitStatus(this.engineTier);
  }

  /**
   * Switch the active 3D visual mode ("lattice", "vault", or "telemetry").
   *
   * @param {string} modeId - Target mode identifier from SCENE_MODES.
   * @param {boolean} [syncOrder=true] - Whether to update the order slider to
   *   the mode's recommended default ratio.
   */
  setMode(modeId, syncOrder = true) {
    if (!SCENE_MODES[modeId]) {
      return;
    }
    this.currentMode = modeId;

    // 1. Update target topology blend weights.
    this.targetModeWeights = [
      modeId === "lattice" ? 1.0 : 0.0,
      modeId === "vault" ? 1.0 : 0.0,
      modeId === "telemetry" ? 1.0 : 0.0
    ];

    // 2. Optionally set the target Entropy-to-Order ratio.
    if (syncOrder) {
      this.targetOrderRatio = SCENE_MODES[modeId].defaultOrder;
    }

    // 3. Update shader primary and secondary colours when Three.js is active.
    const cfg = SCENE_MODES[modeId];
    if (this.uniforms && this.THREE) {
      this.uniforms.uPrimaryColor.value.setHex(cfg.primaryHex);
      this.uniforms.uSecondaryColor.value.setHex(cfg.secondaryHex);
    }

    // 4. Trigger a subtle reconciliation shockwave pulse on mode change.
    this.triggerPulse();
    this.emitStatus(this.engineTier);

    if (this.isPaused) {
      this.renderSingleFrame(0.016);
    }
  }

  /**
   * Set the target Entropy-to-Order ratio from the interactive UI slider.
   *
   * @param {number} ratio - Float in [0.0, 1.0], where 0.0 is maximum inbox
   *   chaos and 1.0 is complete architectural order.
   */
  setOrderRatio(ratio) {
    const clamped = Math.max(0.0, Math.min(1.0, Number(ratio) || 0.0));
    this.targetOrderRatio = clamped;
    if (this.isPaused) {
      this.orderRatio = clamped;
      this.renderSingleFrame(0.016);
    }
  }

  /**
   * Trigger a radial reconciliation/neural shockwave pulse across the 3D scene.
   */
  triggerPulse() {
    this.pulseProgress = 0.001;
    this.pulseActive = true;
    if (this.isPaused) {
      this.renderSingleFrame(0.016);
    }
  }

  /**
   * Pause or resume the real-time animation loop.
   *
   * @returns {boolean} True if the animation loop is now running.
   */
  toggleRunning() {
    this.isPaused = !this.isPaused;
    if (!this.isPaused && !this.rafId) {
      this.lastFrameTime = performance.now();
      this.rafId = requestAnimationFrame(this.animate);
    }
    this.emitStatus(this.engineTier);
    return !this.isPaused;
  }

  /**
   * Handle browser viewport resizing and update camera aspect ratio.
   */
  handleResize() {
    if (!this.canvas) {
      return;
    }
    const rect = this.canvas.parentElement
      ? this.canvas.parentElement.getBoundingClientRect()
      : this.canvas.getBoundingClientRect();
    const width = Math.max(300, Math.floor(rect.width));
    const height = Math.max(300, Math.floor(rect.height));
    const dpr = Math.min(window.devicePixelRatio || 1.0, MAX_PIXEL_RATIO);

    this.viewportWidth = width;
    this.viewportHeight = height;
    this.dpr = dpr;

    if (this.backendType === "three" && this.renderer && this.camera) {
      this.renderer.setPixelRatio(dpr);
      this.renderer.setSize(width, height, false);
      this.camera.aspect = width / height;
      this.camera.updateProjectionMatrix();
      if (this.uniforms) {
        this.uniforms.uPixelRatio.value = dpr;
      }
    } else if (this.backendType === "canvas2d" && this.canvas) {
      this.canvas.width = Math.floor(width * dpr);
      this.canvas.height = Math.floor(height * dpr);
    }

    if (this.isPaused) {
      this.renderSingleFrame(0.016);
    }
  }

  /**
   * Track pointer coordinates in Normalized Device Coordinates ([-1, +1]).
   *
   * @param {PointerEvent} event - Browser pointermove event.
   */
  handlePointerMove(event) {
    if (!this.canvas) {
      return;
    }
    const rect = this.canvas.getBoundingClientRect();
    if (rect.width <= 0 || rect.height <= 0) {
      return;
    }
    const normX = ((event.clientX - rect.left) / rect.width) * 2.0 - 1.0;
    const normY = -(((event.clientY - rect.top) / rect.height) * 2.0 - 1.0);
    if (normX >= -1.2 && normX <= 1.2 && normY >= -1.2 && normY <= 1.2) {
      this.pointer.targetX = Math.max(-1.0, Math.min(1.0, normX));
      this.pointer.targetY = Math.max(-1.0, Math.min(1.0, normY));
    }
  }

  /**
   * Pause the requestAnimationFrame loop when the tab is hidden to save battery
   * and GPU resources.
   */
  handleVisibilityChange() {
    if (document.hidden) {
      if (this.rafId) {
        cancelAnimationFrame(this.rafId);
        this.rafId = null;
      }
    } else if (!this.isPaused && !this.rafId) {
      this.lastFrameTime = performance.now();
      this.rafId = requestAnimationFrame(this.animate);
    }
  }

  /**
   * Primary animation loop invoked via requestAnimationFrame.
   *
   * @param {number} nowMs - High-resolution timestamp in milliseconds.
   */
  animate(nowMs) {
    this.rafId = null;
    if (this.isPaused) {
      return;
    }

    // 1. Compute delta time in seconds and smooth the FPS telemetry counter.
    const rawDt = Math.max(0.001, (nowMs - this.lastFrameTime) / 1000.0);
    const dt = Math.min(rawDt, 0.1);
    this.lastFrameTime = nowMs;
    const instantFps = 1.0 / rawDt;
    this.fpsSmoothed = this.fpsSmoothed * 0.92 + instantFps * 0.08;

    // 2. Render a single simulation step.
    this.renderSingleFrame(dt);

    // 3. Schedule the next frame.
    this.rafId = requestAnimationFrame(this.animate);
  }

  /**
   * Advance simulation physics by dt seconds and draw the current frame.
   *
   * @param {number} dt - Frame delta time in seconds.
   */
  renderSingleFrame(dt) {
    this.elapsedTime = (this.elapsedTime || 0.0) + dt;
    const lerpFactor = Math.min(1.0, dt * TOPOLOGY_LERP_RATE);

    // 1. Smoothly interpolate the Entropy-to-Order ratio and mode weights.
    this.orderRatio += (this.targetOrderRatio - this.orderRatio) * lerpFactor;
    for (let i = 0; i < 3; i += 1) {
      this.modeWeights[i] +=
        (this.targetModeWeights[i] - this.modeWeights[i]) * lerpFactor;
    }

    // 2. Smoothly damp pointer coordinates.
    this.pointer.x += (this.pointer.targetX - this.pointer.x) * (dt * 5.0);
    this.pointer.y += (this.pointer.targetY - this.pointer.y) * (dt * 5.0);

    // 3. Advance the radial shockwave pulse if active.
    if (this.pulseActive) {
      this.pulseProgress += dt / PULSE_DURATION_SECONDS;
      if (this.pulseProgress >= 1.0) {
        this.pulseProgress = 0.0;
        this.pulseActive = false;
      }
    }

    // 4. Delegate drawing to the active backend.
    if (this.backendType === "three") {
      this.renderThreeFrame(dt);
    } else if (this.backendType === "canvas2d") {
      this.renderCanvas2DFrame();
    }
  }

  /**
   * Update Three.js shader uniforms, rotate the gyroscope and document nodes,
   * and render the 3D WebGL scene.
   *
   * @param {number} dt - Frame delta time in seconds.
   */
  renderThreeFrame(dt) {
    if (!this.renderer || !this.scene || !this.camera) {
      return;
    }

    // 1. Update shader uniforms.
    if (this.uniforms) {
      this.uniforms.uTime.value = this.elapsedTime;
      this.uniforms.uOrder.value = this.orderRatio;
      this.uniforms.uModeWeights.value = this.modeWeights;
      this.uniforms.uPointer.value.set(this.pointer.x, this.pointer.y);
      this.uniforms.uPulse.value = this.pulseProgress;
    }

    // 2. Apply subtle parallax rotation to the master scene group.
    if (this.rootGroup) {
      this.rootGroup.rotation.y =
        this.pointer.x * 0.28 + Math.sin(this.elapsedTime * 0.18) * 0.12;
      this.rootGroup.rotation.x = -this.pointer.y * 0.18;
    }

    // 3. Animate the concentric Normalisation Gyroscope rings and Vault core.
    if (this.gyroRings) {
      for (let i = 0; i < this.gyroRings.length; i += 1) {
        const ring = this.gyroRings[i];
        const speed = (i % 2 === 0 ? 1 : -1) * (0.22 + i * 0.09);
        ring.rotation.z += dt * speed;
        ring.rotation.y += dt * speed * 0.6;
      }
    }
    if (this.vaultCoreMesh) {
      this.vaultCoreMesh.rotation.y -= dt * 0.32;
      this.vaultCoreMesh.rotation.x += dt * 0.18;
      const coreScale =
        0.75 + this.modeWeights[1] * 0.55 + Math.sin(this.elapsedTime * 2.0) * 0.04;
      this.vaultCoreMesh.scale.setScalar(coreScale);
    }

    // 4. Interpolate floating 3D document polyhedra between Chaos and Order.
    if (this.docNodes) {
      const w0 = this.modeWeights[0];
      const w1 = this.modeWeights[1];
      const w2 = this.modeWeights[2];
      const ord = this.orderRatio;
      for (let i = 0; i < this.docNodes.length; i += 1) {
        const mesh = this.docNodes[i];
        const d = mesh.userData;
        const targetX = d.lattice[0] * w0 + d.vault[0] * w1 + d.telemetry[0] * w2;
        const targetY = d.lattice[1] * w0 + d.vault[1] * w1 + d.telemetry[1] * w2;
        const targetZ = d.lattice[2] * w0 + d.vault[2] * w1 + d.telemetry[2] * w2;

        mesh.position.x = d.chaos[0] * (1.0 - ord) + targetX * ord;
        mesh.position.y =
          d.chaos[1] * (1.0 - ord) +
          targetY * ord +
          Math.sin(this.elapsedTime * 1.5 + d.phase * 6.28) * 0.15;
        mesh.position.z = d.chaos[2] * (1.0 - ord) + targetZ * ord;
        mesh.rotation.x += dt * 0.6;
        mesh.rotation.y += dt * 0.8;
      }
    }

    // 5. Execute the GPU draw call.
    this.renderer.render(this.scene, this.camera);
  }

  /**
   * Render the 3D scene using the built-in 2D Canvas perspective projection
   * engine when Three.js is not active.
   */
  renderCanvas2DFrame() {
    const ctx = this.ctx2d;
    if (!ctx || !this.canvasParticles) {
      return;
    }

    const dpr = this.dpr || 1.0;
    const width = this.viewportWidth * dpr;
    const height = this.viewportHeight * dpr;
    const cx = width * 0.5;
    const cy = height * 0.5;
    const fovScale = Math.min(width, height) * 0.82;

    // 1. Clear the canvas frame.
    ctx.clearRect(0, 0, width, height);

    // 2. Compute camera rotation angles from pointer parallax and time.
    const rotY =
      this.pointer.x * 0.32 + Math.sin(this.elapsedTime * 0.2) * 0.15;
    const rotX = -this.pointer.y * 0.22;
    const cosY = Math.cos(rotY);
    const sinY = Math.sin(rotY);
    const cosX = Math.cos(rotX);
    const sinX = Math.sin(rotX);

    // 3. Draw central normalisation rings.
    ctx.save();
    ctx.translate(cx, cy);
    ctx.strokeStyle = "rgba(212, 175, 106, 0.22)";
    ctx.lineWidth = 1.2 * dpr;
    for (let r = 1; r <= 3; r += 1) {
      ctx.beginPath();
      ctx.ellipse(
        0,
        0,
        r * 68 * dpr,
        r * 44 * dpr,
        this.elapsedTime * 0.25 * (r % 2 === 0 ? 1 : -1),
        0,
        Math.PI * 2
      );
      ctx.stroke();
    }
    ctx.restore();

    // 4. Project and draw each 3D particle.
    const w0 = this.modeWeights[0];
    const w1 = this.modeWeights[1];
    const w2 = this.modeWeights[2];
    const ord = this.orderRatio;

    for (let i = 0; i < this.canvasParticles.length; i += 1) {
      const p = this.canvasParticles[i];
      const ox = p.lattice[0] * w0 + p.vault[0] * w1 + p.telemetry[0] * w2;
      const oy = p.lattice[1] * w0 + p.vault[1] * w1 + p.telemetry[1] * w2;
      const oz = p.lattice[2] * w0 + p.vault[2] * w1 + p.telemetry[2] * w2;

      const swirl = this.elapsedTime * 0.6 + p.phase * 6.2831;
      const cxPos = p.chaos[0] + Math.cos(swirl) * 0.7;
      const cyPos = p.chaos[1] + Math.sin(swirl) * 0.7;
      const czPos = p.chaos[2];

      const x = cxPos * (1.0 - ord) + ox * ord;
      const y = cyPos * (1.0 - ord) + oy * ord;
      const z = czPos * (1.0 - ord) + oz * ord;

      // Rotate around Y and X axes.
      const rx = x * cosY - z * sinY;
      const rz1 = x * sinY + z * cosY;
      const ry = y * cosX - rz1 * sinX;
      const rz = y * sinX + rz1 * cosX + CAMERA_DISTANCE_Z;

      if (rz <= 1.0) {
        continue;
      }

      const invZ = fovScale / rz;
      const screenX = cx + rx * invZ;
      const screenY = cy - ry * invZ;
      const radius = Math.max(1.2, (p.scale * 18.0 * dpr) / rz);

      ctx.fillStyle =
        p.colorMix > 0.5
          ? "rgba(212, 175, 106, 0.82)"
          : "rgba(52, 211, 153, 0.78)";
      ctx.beginPath();
      ctx.arc(screenX, screenY, radius, 0, Math.PI * 2);
      ctx.fill();
    }
  }

  /**
   * Emit the current engine telemetry status to the UI controller.
   *
   * @param {string} tierLabel - Active graphics tier description.
   */
  emitStatus(tierLabel) {
    this.onStatusChange({
      tierLabel,
      webgpuAvailable: this.webgpuAvailable,
      adapterName: this.webgpuAdapterName,
      currentMode: this.currentMode,
      orderRatio: this.orderRatio,
      isPaused: this.isPaused,
      fps: Math.round(this.fpsSmoothed)
    });
  }
}
