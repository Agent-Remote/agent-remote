/* Spring physics shared by every moving surface in the prototype.
 * Mirrors mygo's ui.SpringOptions{Duration, Bounce} (SwiftUI/Motion parameters)
 * so values tuned here transfer 1:1 to the Go implementation (doc §6). */
(function () {
  'use strict';

  // Motion tokens (doc §6.1). Durations are perceptual response, not fixed lengths.
  const Presets = {
    smooth:  { duration: 0.40, bounce: 0 },    // reposition, layer depth, wheel enter
    snappy:  { duration: 0.28, bounce: 0 },    // hover lift, sector scale, chips
    press:   { duration: 0.12, bounce: 0 },    // pointer-down feedback
    sheet:   { duration: 0.36, bounce: 0 },    // dock / control center opened by key
    flick:   { duration: 0.30, bounce: 0.2 },  // released from a drag with momentum only
    page:    { duration: 0.34, bounce: 0 },    // control-center push / pop
  };

  const Motion = { reduced: false, presets: Presets, listeners: new Set() };

  // Convert perceptual duration/bounce to stiffness/damping (unit mass).
  function coefficients(o) {
    const d = Math.max(0.05, o.duration);
    const stiffness = Math.pow((2 * Math.PI) / d, 2);
    const ratio = o.bounce >= 0 ? 1 - o.bounce : 1 / (1 + o.bounce);
    return { k: stiffness, c: 4 * Math.PI * ratio / d };
  }

  const active = new Set();
  let last = 0, raf = 0;
  function tick(now) {
    const dt = Math.min(1 / 30, (now - (last || now)) / 1000);
    last = now;
    for (const s of Array.from(active)) s.step(dt);
    raf = active.size ? requestAnimationFrame(tick) : 0;
    if (!raf) last = 0;
  }
  function wake(s) { active.add(s); if (!raf) raf = requestAnimationFrame(tick); }

  class Spring {
    // kind 'transform' jumps under reduced motion; kind 'fade' becomes a short linear tween.
    constructor(value, options, onUpdate, kind) {
      this.value = value; this.target = value; this.velocity = 0;
      this.options = Object.assign({}, Presets.smooth, options);
      this.onUpdate = onUpdate || (() => {});
      this.kind = kind || 'transform';
      this.tween = null;
    }
    to(target, opts) {
      opts = opts || {};
      if (opts.preset) Object.assign(this.options, Presets[opts.preset]);
      if (opts.duration != null) this.options.duration = opts.duration;
      if (opts.bounce != null) this.options.bounce = opts.bounce;
      if (opts.velocity != null) this.velocity = opts.velocity; // §5 velocity handoff
      this.target = target;
      if (Motion.reduced) {
        if (this.kind === 'transform') return this.jump(target);
        this.tween = { from: this.value, start: performance.now(), length: 160 };
      }
      wake(this);
      return this;
    }
    jump(v) { // follow the pointer 1:1; velocity is tracked by the caller
      this.value = this.target = v; this.velocity = 0; this.tween = null;
      active.delete(this); this.onUpdate(v); return this;
    }
    step(dt) {
      if (this.tween) {
        const p = Math.min(1, (performance.now() - this.tween.start) / this.tween.length);
        this.value = this.tween.from + (this.target - this.tween.from) * p;
        if (p >= 1) { this.tween = null; active.delete(this); }
        this.onUpdate(this.value); return;
      }
      const { k, c } = coefficients(this.options);
      const steps = Math.max(1, Math.ceil(dt * 240)), h = dt / steps;
      for (let i = 0; i < steps; i++) {             // semi-implicit Euler, stable at 240 Hz
        const a = -k * (this.value - this.target) - c * this.velocity;
        this.velocity += a * h; this.value += this.velocity * h;
      }
      const span = Math.max(1, Math.abs(this.target));
      if (Math.abs(this.velocity) < 0.002 * span && Math.abs(this.value - this.target) < 0.0005 * span) {
        this.value = this.target; this.velocity = 0; active.delete(this);
      }
      this.onUpdate(this.value);
    }
    get settled() { return !active.has(this); }
  }

  // apple-design §6: Apple's exponential-decay projection (decelerationRate 0.998).
  function project(velocity, rate) { rate = rate || 0.998; return (velocity / 1000) * rate / (1 - rate); }

  // apple-design §9: progressive resistance past a bound.
  function rubberband(overshoot, dimension, constant) {
    constant = constant || 0.55;
    return (overshoot * dimension * constant) / (dimension + constant * Math.abs(overshoot));
  }

  // Last ~80 ms of pointer samples → release velocity in px/s.
  class VelocityTracker {
    constructor() { this.samples = []; }
    reset() { this.samples = []; }
    add(x, y) {
      const t = performance.now();
      this.samples.push({ t, x, y });
      while (this.samples.length > 2 && t - this.samples[0].t > 80) this.samples.shift();
    }
    velocity() {
      const s = this.samples; if (s.length < 2) return { x: 0, y: 0 };
      const a = s[0], b = s[s.length - 1], dt = Math.max(1, b.t - a.t) / 1000;
      return { x: (b.x - a.x) / dt, y: (b.y - a.y) / dt };
    }
  }

  const mq = window.matchMedia('(prefers-reduced-motion: reduce)');
  function setReduced(v) { Motion.reduced = v; Motion.listeners.forEach(fn => fn(v)); }
  setReduced(mq.matches);
  mq.addEventListener('change', e => setReduced(e.matches));

  window.Physics = { Spring, Motion, Presets, project, rubberband, VelocityTracker, setReduced };
})();
