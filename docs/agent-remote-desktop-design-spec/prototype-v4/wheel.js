/* Radial wheel: v3 polar sector math + polar hit-testing + per-sector springs.
 * The same geometry is specified for the Go implementation in doc §7.3. */
(function () {
  'use strict';
  const { Spring } = window.Physics;
  const SIZE = 490, C = SIZE / 2;

  // v3 formulas, unchanged: 0° is 12 o'clock, angles grow clockwise.
  function polarToCartesian(cx, cy, r, deg) {
    const rad = (deg - 90) * Math.PI / 180;
    return { x: cx + r * Math.cos(rad), y: cy + r * Math.sin(rad) };
  }
  function annularSectorPath(cx, cy, rInner, rOuter, start, end) {
    const p1 = polarToCartesian(cx, cy, rOuter, end), p2 = polarToCartesian(cx, cy, rOuter, start);
    const p3 = polarToCartesian(cx, cy, rInner, start), p4 = polarToCartesian(cx, cy, rInner, end);
    const large = end - start <= 180 ? '0' : '1';
    return ['M', p1.x, p1.y, 'A', rOuter, rOuter, 0, large, 0, p2.x, p2.y,
            'L', p3.x, p3.y, 'A', rInner, rInner, 0, large, 1, p4.x, p4.y, 'Z'].join(' ');
  }

  /* opts: host, count, rInner, rOuter, labelR, gap (deg each side), deadR (HUD radius),
   *       items, label(item, i) → html, enabled(item) → bool, accent(item) → css|null */
  function create(opts) {
    const step = 360 / opts.count;
    const svg = opts.host.querySelector('svg');
    svg.innerHTML = '';
    opts.host.querySelectorAll('.wheel-label').forEach(n => n.remove());
    const sectors = opts.items.map((item, i) => {
      const start = i * step - step / 2 + opts.gap, end = (i + 1) * step - step / 2 - opts.gap;
      const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
      path.setAttribute('d', annularSectorPath(C, C, opts.rInner, opts.rOuter, start, end));
      path.setAttribute('class', 'sector');
      const enabled = opts.enabled(item);
      if (!enabled) path.classList.add(item ? 'blocked' : 'empty');
      const accent = opts.accent(item);
      if (accent) { path.dataset.accent = '1'; path.style.setProperty('--sector-accent', accent); }
      svg.appendChild(path);

      const pos = polarToCartesian(C, C, opts.labelR, (start + end) / 2);
      const label = document.createElement('div');
      label.className = 'wheel-label' + (item ? '' : ' empty');
      label.style.left = pos.x + 'px'; label.style.top = pos.y + 'px';
      label.innerHTML = opts.label(item, i);
      opts.host.appendChild(label);

      // hover 1.038 / press 0.985 (v3 values) — springs, so hover-out mid-flight reverses smoothly
      const s = { path, item, enabled, hover: false, pressed: false };
      s.scale = new Spring(1, { preset: 'snappy' }, v => { path.style.transform = `scale(${v})`; });
      return s;
    });

    function refresh(s) { s.scale.to(s.pressed ? 0.985 : s.hover ? 1.038 : 1, { preset: s.pressed ? 'press' : 'snappy' }); }
    const api = {
      sectors, hot: null,
      setHot(i) {
        if (i === api.hot) return;
        sectors.forEach((s, j) => { s.hover = j === i && s.enabled; s.path.classList.toggle('hot', s.hover); refresh(s); });
        api.hot = i;
      },
      press(i, down) { const s = sectors[i]; if (s && s.enabled) { s.pressed = down; refresh(s); } },
      // Polar hit-test: inside the HUD selects nothing (it hosts search). While a
      // chord is held (`byAngle`) any distance past the HUD selects by angle, so a
      // quick flick toward a sector works; clicks keep ~12% padding past the rim.
      hitTest(x, y, byAngle) {
        const r = svg.getBoundingClientRect();
        const k = r.width / SIZE, dx = (x - r.left - r.width / 2) / k, dy = (y - r.top - r.height / 2) / k;
        const dist = Math.hypot(dx, dy);
        if (dist < opts.deadR || (!byAngle && dist > opts.rOuter * 1.12)) return null;
        const angle = (Math.atan2(dx, -dy) * 180 / Math.PI + 360) % 360;
        return Math.floor(((angle + step / 2) % 360) / step);
      },
      next(dir) { // keyboard rotation, skipping disabled slots
        let i = api.hot == null ? (dir > 0 ? -1 : 0) : api.hot;
        for (let n = 0; n < opts.count; n++) {
          i = (i + dir + opts.count) % opts.count;
          if (sectors[i].enabled) return i;
        }
        return api.hot;
      },
    };
    return api;
  }

  window.Wheel = { create, polarToCartesian, annularSectorPath };
})();
