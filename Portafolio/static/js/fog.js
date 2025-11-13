let scene, camera, renderer, uniforms, material, mesh;

function initFog() {
  scene = new THREE.Scene();
  camera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
  renderer = new THREE.WebGLRenderer({
    canvas: document.getElementById('fogCanvas'),
    antialias: true
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
      float b = random(i + vec2(1.0, 0.0));
      float c = random(i + vec2(0.0, 1.0));
      float d = random(i + vec2(1.0, 1.0));
      vec2 u = f*f*(3.0-2.0*f);
      return mix(a, b, u.x) + (c - a)*u.y*(1.0 - u.x) + (d - b)*u.x*u.y;
    }

    float fbm(vec2 st) {
      float value = 0.0;
      float amplitude = 0.5;
      for (int i = 0; i < 6; i++) {
        value += amplitude * noise(st);
        st *= 2.0; // Incrementa la frecuencia para hacer las nubes más pequeñas
        amplitude *= 0.5;
      }
      return value;
    }

    void main() {
      vec2 st = gl_FragCoord.xy / resolution.xy;
      st.x *= resolution.x / resolution.y;

      vec2 q = vec2(fbm(st + vec2(0.0, time * 0.02)),
                    fbm(st + vec2(1.0, time * 0.015)));

      float n = fbm(st + q * 0.5);  // Ajustar la densidad de las nubes

      // Nubes más pequeñas y de tonos más oscuros
      float fog = smoothstep(0.3, 0.8, n);  // Hacemos que la niebla sea más sutil
      // Oscurecemos el color de la niebla
      vec3 color = mix(vec3(0.05), vec3(0.2), fog);  // Color más gris oscuro

      gl_FragColor = vec4(color, 1.0);
    }
  `;

  uniforms = {
    time: { value: 0.0 },
    resolution: { value: new THREE.Vector2() }
  };

  material = new THREE.ShaderMaterial({
    uniforms: uniforms,
    vertexShader: vertexShader,
    fragmentShader: fragmentShader
  });

  mesh = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), material);
  scene.add(mesh);

  onResize();
  window.addEventListener('resize', onResize);
}

function onResize() {
  renderer.setSize(window.innerWidth, window.innerHeight);
  uniforms.resolution.value.x = renderer.domElement.width;
  uniforms.resolution.value.y = renderer.domElement.height;
}

function animate(t) {
  requestAnimationFrame(animate);
  uniforms.time.value = t * 0.001;
  renderer.render(scene, camera);
}

initFog();
animate(0);
