(function() {
    const root = document.querySelector('[data-weather-stage]');
    if (!root) return;

    // Keep overlay above content but non-blocking for page interactions.
    root.style.zIndex = root.style.zIndex || '9999';
    root.style.pointerEvents = 'none';

    const ds = root.dataset || {};
    const cfg = Object.assign({
        default_type: 'rain',
        intensity: 3,
        auto_rotate: false,
        rotate_seconds: 18,
        show_toggle: true,
        accent_color: '#7dd3fc'
    }, window.__WEATHER_SHOWCASE_CONFIG || {});

    const config = {
        type: (ds.weatherType || cfg.default_type || 'rain').toLowerCase(),
        intensity: clampInt(ds.weatherIntensity || cfg.intensity || 3, 1, 5),
        autoRotate: ds.weatherRotate === 'true' || cfg.auto_rotate === true,
        rotateSeconds: clampInt(ds.weatherRotateSeconds || cfg.rotate_seconds || 18, 5, 120),
        showToggle: ds.weatherToggle !== 'false' && cfg.show_toggle !== false,
        accent: ds.weatherAccent || cfg.accent_color || '#7dd3fc'
    };

    const allowedTypes = ['rain', 'snow', 'stars', 'meteors', 'aurora'];
    setAuroraColors(config.accent);
    if (!allowedTypes.includes(config.type)) {
        config.type = 'rain';
    }

    const stage = root.querySelector('.weather-stage') || root;
    const toggleBtn = root.querySelector('[data-weather-toggle]');
    const legend = root.querySelector('[data-weather-legend]');

    if (!config.showToggle && toggleBtn) {
        toggleBtn.style.display = 'none';
    }

    const canvas = document.createElement('canvas');
    stage && stage.appendChild(canvas);
    const ctx = canvas.getContext('2d');

    // Aurora DOM layer (uses SVG filter for turbulence)
    const auroraLayer = document.createElement('div');
    auroraLayer.className = 'weather-aurora-layer';
    stage && stage.appendChild(auroraLayer);
    const auroraFilter = createAuroraFilter();

    let particles = [];
    let meteors = [];
    let stars = [];
    let auroraOffset = 0;
    let stopped = false;
    let rotateTimer = null;
    let currentType = config.type;
    let rafId = null;
    let auroraFrame = 0;

    function createAuroraFilter() {
        const svgNS = 'http://www.w3.org/2000/svg';
        const svg = document.createElementNS(svgNS, 'svg');
        svg.setAttribute('class', 'weather-aurora-filter');
        svg.setAttribute('aria-hidden', 'true');
        svg.style.position = 'absolute';
        svg.style.width = '0';
        svg.style.height = '0';
        svg.style.pointerEvents = 'none';

        const defs = document.createElementNS(svgNS, 'defs');
        const filter = document.createElementNS(svgNS, 'filter');
        filter.setAttribute('id', 'weather-aurora-noise');

        const turbulence = document.createElementNS(svgNS, 'feTurbulence');
        turbulence.setAttribute('type', 'turbulence');
        turbulence.setAttribute('baseFrequency', '0.003 0.003');
        turbulence.setAttribute('numOctaves', '3');
        turbulence.setAttribute('seed', '10');
        turbulence.setAttribute('result', 'noise');

        const displacement = document.createElementNS(svgNS, 'feDisplacementMap');
        displacement.setAttribute('in', 'SourceGraphic');
        displacement.setAttribute('in2', 'noise');
        displacement.setAttribute('scale', '72');
        displacement.setAttribute('xChannelSelector', 'R');
        displacement.setAttribute('yChannelSelector', 'G');

        filter.appendChild(turbulence);
        filter.appendChild(displacement);
        defs.appendChild(filter);
        svg.appendChild(defs);
        root.appendChild(svg);

        return { svg, filter, turbulence };
    }

    function setAuroraColors(accent) {
        const base = accent || '#7dd3fc';
        const light = colorWithAlpha(base, 0.7, 0.18);
        const glow = colorWithAlpha(base, 0.9, 0.42);
        const core = colorWithAlpha(base, 1, 0.9);
        root.style.setProperty('--weather-aurora-core', core);
        root.style.setProperty('--weather-aurora-glow', glow);
        root.style.setProperty('--weather-aurora-fade', light);
    }

    function hexToRgb(hex) {
        const cleaned = (hex || '').replace('#', '');
        if (cleaned.length !== 3 && cleaned.length !== 6) return [125, 211, 252];
        const full = cleaned.length === 3 ? cleaned.split('').map(c => c + c).join('') : cleaned;
        const num = parseInt(full, 16);
        return [(num >> 16) & 255, (num >> 8) & 255, num & 255];
    }

    function colorWithAlpha(hex, alpha, brighten = 0) {
        const [r, g, b] = hexToRgb(hex);
        const mix = (channel) => Math.min(255, Math.max(0, channel + 255 * brighten));
        const rr = Math.round(mix(r));
        const gg = Math.round(mix(g));
        const bb = Math.round(mix(b));
        return `rgba(${rr}, ${gg}, ${bb}, ${alpha})`;
    }

    function clampInt(val, min, max) {
        const n = parseInt(val, 10);
        if (isNaN(n)) return min;
        return Math.max(min, Math.min(max, n));
    }

    function resize() {
        canvas.width = window.innerWidth * window.devicePixelRatio;
        canvas.height = window.innerHeight * window.devicePixelRatio;
        canvas.style.width = window.innerWidth + 'px';
        canvas.style.height = window.innerHeight + 'px';
        auroraLayer.style.width = window.innerWidth * 1.4 + 'px';
        auroraLayer.style.height = window.innerHeight * 0.9 + 'px';
    }

    function setLegend(text) {
        if (!legend) return;
        const dot = legend.querySelector('.legend-dot');
        if (dot) {
            dot.style.background = `linear-gradient(135deg, ${config.accent}, #60a5fa)`;
            dot.style.boxShadow = `0 0 12px ${config.accent}`;
        }
        const label = legend.querySelector('.legend-text');
        if (label) {
            label.textContent = text;
        }
    }

    function initParticles(type) {
        particles = [];
        meteors = [];
        stars = [];
        const base = config.intensity * 60;
        const width = canvas.width;
        const height = canvas.height;
        if (type === 'rain') {
            for (let i = 0; i < base; i++) {
                particles.push({
                    x: Math.random() * width,
                    y: Math.random() * height,
                    len: 20 + Math.random() * 20,
                    speed: 6 + Math.random() * 10 * config.intensity,
                    alpha: 0.25 + Math.random() * 0.3
                });
            }
        } else if (type === 'snow') {
            for (let i = 0; i < base * 0.6; i++) {
                particles.push({
                    x: Math.random() * width,
                    y: Math.random() * height,
                    r: 1 + Math.random() * (config.intensity + 1),
                    speedY: 0.5 + Math.random() * (1 + config.intensity * 0.4),
                    drift: (Math.random() - 0.5) * 0.8
                });
            }
        } else if (type === 'stars') {
            for (let i = 0; i < base * 0.5; i++) {
                stars.push({
                    x: Math.random() * width,
                    y: Math.random() * height,
                    r: Math.random() * 1.4 + 0.6,
                    alpha: Math.random(),
                    pulse: Math.random() * 0.02 + 0.01
                });
            }
        } else if (type === 'meteors') {
            for (let i = 0; i < base * 0.3; i++) {
                stars.push({
                    x: Math.random() * width,
                    y: Math.random() * height,
                    r: Math.random() * 1.3 + 0.5,
                    alpha: 0.6 + Math.random() * 0.3,
                    pulse: Math.random() * 0.02 + 0.01
                });
            }
        }
    }

    function spawnMeteor() {
        const width = canvas.width;
        const height = canvas.height;
        meteors.push({
            x: Math.random() * width,
            y: -50,
            len: 80 + Math.random() * 120,
            speed: 10 + Math.random() * (6 + config.intensity * 2),
            angle: Math.PI / 3.2,
            life: 0,
            maxLife: 120 + Math.random() * 60
        });
    }

    function drawRain() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.strokeStyle = `rgba(125, 211, 252, 0.55)`;
        ctx.lineWidth = 1.2 * window.devicePixelRatio;
        particles.forEach(p => {
            p.y += p.speed;
            p.x += 0.5;
            if (p.y > canvas.height) {
                p.y = -10;
                p.x = Math.random() * canvas.width;
            }
            ctx.globalAlpha = p.alpha;
            ctx.beginPath();
            ctx.moveTo(p.x, p.y);
            ctx.lineTo(p.x, p.y + p.len);
            ctx.stroke();
        });
    }

    function drawSnow() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = 'rgba(255,255,255,0.9)';
        particles.forEach(p => {
            p.y += p.speedY;
            p.x += p.drift;
            if (p.y > canvas.height) {
                p.y = -5;
                p.x = Math.random() * canvas.width;
            }
            if (p.x > canvas.width) p.x = 0;
            if (p.x < 0) p.x = canvas.width;
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.r * window.devicePixelRatio, 0, Math.PI * 2);
            ctx.fill();
        });
    }

    function drawStars() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = '#c7d2fe';
        stars.forEach(s => {
            s.alpha += s.pulse * (Math.random() > 0.5 ? 1 : -1);
            s.alpha = Math.max(0.1, Math.min(1, s.alpha));
            ctx.globalAlpha = s.alpha;
            ctx.beginPath();
            ctx.arc(s.x, s.y, s.r * window.devicePixelRatio, 0, Math.PI * 2);
            ctx.fill();
        });
    }

    function drawMeteors() {
        drawStars();
        if (Math.random() < 0.02 * config.intensity) {
            spawnMeteor();
        }
        meteors = meteors.filter(m => m.life < m.maxLife);
        meteors.forEach(m => {
            m.x += Math.cos(m.angle) * m.speed * window.devicePixelRatio;
            m.y += Math.sin(m.angle) * m.speed * window.devicePixelRatio;
            m.life += 1;
            const grad = ctx.createLinearGradient(m.x, m.y, m.x - m.len, m.y - m.len * 0.4);
            grad.addColorStop(0, config.accent);
            grad.addColorStop(1, 'rgba(255,255,255,0)');
            ctx.strokeStyle = grad;
            ctx.lineWidth = 2 * window.devicePixelRatio;
            ctx.beginPath();
            ctx.moveTo(m.x, m.y);
            ctx.lineTo(m.x - m.len, m.y - m.len * 0.4);
            ctx.stroke();
        });
    }

    function drawAurora() {
        auroraOffset += 0.002 * (1 + config.intensity * 0.3);
        auroraFrame += 0.8;
        const wobble = 4 + config.intensity * 0.8;
        const shiftX = Math.sin(auroraOffset * 0.6) * wobble * 4;
        const shiftY = Math.cos(auroraOffset * 0.45) * wobble * 2;
        const scale = 1.05 + config.intensity * 0.02;
        auroraLayer.style.transform = `rotate(-10deg) translate(${shiftX}px, ${shiftY}px) scale(${scale})`;

        if (auroraFilter && auroraFilter.turbulence) {
            const bfx = 0.0042 + 0.0012 * Math.cos(auroraFrame * 0.017);
            const bfy = 0.0036 + 0.001 * Math.sin(auroraFrame * 0.021);
            auroraFilter.turbulence.setAttribute('baseFrequency', `${bfx.toFixed(4)} ${bfy.toFixed(4)}`);
        }
    }

    function render() {
        if (stopped) return;
        switch (currentType) {
            case 'rain':
                drawRain();
                break;
            case 'snow':
                drawSnow();
                break;
            case 'stars':
                drawStars();
                break;
            case 'meteors':
                drawMeteors();
                break;
            case 'aurora':
                drawAurora();
                break;
            default:
                drawRain();
        }
        rafId = requestAnimationFrame(render);
    }

    function setType(type) {
        if (!allowedTypes.includes(type)) return;
        currentType = type;
        setLegend(typeLabel(type));
        initParticles(type);
        root.setAttribute('data-weather-type', type);
        if (type === 'aurora') {
            canvas.style.display = 'none';
            auroraLayer.style.display = 'block';
        } else {
            canvas.style.display = 'block';
            auroraLayer.style.display = 'none';
        }
    }

    function typeLabel(type) {
        const map = { rain: '雨', snow: '雪', stars: '星空', meteors: '流星', aurora: '极光' };
        return map[type] || type;
    }

    function toggleVisibility() {
        const hidden = root.getAttribute('data-hidden') === 'true';
        const next = !hidden;
        root.setAttribute('data-hidden', next ? 'true' : 'false');
        if (toggleBtn) {
            toggleBtn.setAttribute('aria-pressed', next ? 'false' : 'true');
            toggleBtn.textContent = next ? '开启天气' : '关闭天气';
        }
        if (auroraLayer) {
            auroraLayer.style.opacity = next ? '0' : '';
        }
        stopped = next;
        if (next) {
            if (rafId) {
                cancelAnimationFrame(rafId);
                rafId = null;
            }
            ctx && ctx.clearRect(0, 0, canvas.width, canvas.height);
        } else {
            canvas.style.display = 'block';
            render();
        }
    }

    function setupRotate() {
        if (!config.autoRotate) return;
        const order = allowedTypes;
        let idx = order.indexOf(currentType);
        rotateTimer = setInterval(function() {
            idx = (idx + 1) % order.length;
            setType(order[idx]);
        }, config.rotateSeconds * 1000);
    }

    function setupToggle() {
        if (!toggleBtn) return;
        toggleBtn.addEventListener('click', function() {
            toggleVisibility();
        });
        toggleBtn.setAttribute('aria-pressed', 'true');
        toggleBtn.textContent = '关闭天气';
        toggleBtn.style.pointerEvents = 'auto';
    }

    function setupLegendCycle() {
        if (!legend) return;
        legend.style.cursor = 'pointer';
        legend.title = '点击切换天气类型';
        legend.addEventListener('click', function() {
            const idx = allowedTypes.indexOf(currentType);
            const next = allowedTypes[(idx + 1) % allowedTypes.length];
            setType(next);
        });
        legend.style.pointerEvents = 'auto';
    }

    function setupVisibilityPause() {
        document.addEventListener('visibilitychange', function() {
            if (document.hidden) {
                stopped = true;
                if (rafId) cancelAnimationFrame(rafId);
                rafId = null;
            } else if (root.getAttribute('data-hidden') !== 'true') {
                stopped = false;
                render();
            }
        });
    }

    // Ensure first render after DOM/layout ready.
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    function init() {
        resize();
        window.addEventListener('resize', resize);
        setLegend(typeLabel(currentType));
        initParticles(currentType);
        if (currentType === 'aurora') {
            canvas.style.display = 'none';
            auroraLayer.style.display = 'block';
        } else {
            auroraLayer.style.display = 'none';
        }
        render();
        setupToggle();
        setupRotate();
        setupLegendCycle();
        setupVisibilityPause();
        root.classList.add('weather-showcase--ready');
    }

})();
