let scene, camera, renderer, uniforms, material, mesh;

function init() {

  // Usar tu canvas real
  const canvas = document.getElementById("fogCanvas");

  scene = new THREE.Scene();
  camera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);

  renderer = new THREE.WebGLRenderer({
    canvas: canvas,
    antialias: true,
    alpha: true   // permite ver a través
  });

  renderer.setSize(window.innerWidth, window.innerHeight);

  const vertexShader = `
        varying vec2 vUv;
        void main() {
            vUv = uv;
            gl_Position = vec4(position, 1.0);
        }
    `;

  const fragmentShader = `
    uniform float time;
    uniform vec2 resolution;
    varying vec2 vUv;

    float random(vec2 st) {
        return fract(sin(dot(st.xy, vec2(12.9898,78.233))) * 43758.5453123);
    }

    float noise(vec2 st) {
        vec2 i = floor(st);
        vec2 f = fract(st);

        float a = random(i);
        float b = random(i + vec2(1., 0.));
        float c = random(i + vec2(0., 1.));
        float d = random(i + vec2(1., 1.));

        vec2 u = f * f * (3. - 2. * f);

        return mix(a, b, u.x) +
               (c - a) * u.y * (1. - u.x) +
               (d - b) * u.x * u.y;
    }

    float fbm(vec2 st) {
        float value = 0.;
        float amp = 0.5;

        for (int i = 0; i < 6; i++) {
            value += amp * noise(st);
            st *= 2.;
            amp *= 0.5;
        }

        return value;
    }

    void main() {
        vec2 st = gl_FragCoord.xy / resolution.xy;
        st.x *= resolution.x / resolution.y;

        vec2 q = vec2(0.);
        q.x = fbm(st + 0.1 * time);
        q.y = fbm(st + vec2(1.0));

        vec2 r = vec2(0.);
        r.x = fbm(st + q + vec2(1.7, 9.2) + 0.15 * time);
        r.y = fbm(st + q + vec2(8.3, 2.8) + 0.126 * time);

        float f = fbm(st + r);

        // ======================
        //   CONTRASTE OSCURO REAL
        // ======================

        // base
        float gray = f;

        // bajar los tonos fuertes (hace todo más oscuro)
        gray *= 0.70;   // AJUSTE CLAVE (0.3 - 0.45 es perfecto)

        // curva suave para que no quede plano
        gray = pow(gray, 1.75);  // >1.0 = hace todo más negro

        // pequeños detalles de contraste
        gray = smoothstep(0.08, 0.6, gray);

        vec3 color = vec3(gray);

        gl_FragColor = vec4(color, 0.80);
    }
`;



  uniforms = {
    time: { value: 1.0 },
    resolution: { value: new THREE.Vector2() }
  };

  material = new THREE.ShaderMaterial({
    uniforms: uniforms,
    vertexShader: vertexShader,
    fragmentShader: fragmentShader,
    transparent: true
  });

  mesh = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), material);
  scene.add(mesh);

  onWindowResize();
  window.addEventListener("resize", onWindowResize, false);
}

function onWindowResize() {
  renderer.setSize(window.innerWidth, window.innerHeight);
  uniforms.resolution.value.x = renderer.domElement.width;
  uniforms.resolution.value.y = renderer.domElement.height;
}

function animateFog(timestamp) {
  requestAnimationFrame(animateFog);
  uniforms.time.value = timestamp * 0.001;
  renderer.render(scene, camera);
}

init();
animateFog();

