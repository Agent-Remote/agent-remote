/* Layer state machine, chord input and gestures (doc §3). Every visual change
 * is a spring re-target, so any transition can be interrupted and reversed. */
(function () {
  'use strict';
  const { Spring, Motion, project, rubberband, VelocityTracker } = window.Physics;
  const D = window.Data, V = window.Views, $ = V.$;
  const root = document.documentElement;

  // ---------------- state ----------------
  const S = {
    layer: 'zen', mode: 'sticky', sel: null, chordAt: 0, moved: false, confirm: null,
    project: 'p1', focus: 's1', tab: 't1', themePref: 'system', ccPage: null, op: null, search: null, searchHot: 0,
    slots: [null, ...D.projects, null],                 // index 0 is "··· 更多"; geometry never changes
    tabsBy: { p1: [{ id: 't1', panes: ['s1', 's2'] }, { id: 't2', panes: ['s3'] }] },
    sessions: D.sessions.slice(), prevFocus: 's2',
    get tabs() { return this.tabsBy[this.project] || []; },
    session(id) { return this.sessions.find(s => s.id === id); },
    projectSessions() { return this.sessions.filter(s => s.project === this.project); },
    projectName() { const p = [...D.projects, ...D.olderProjects].find(p => p.id === this.project); return p ? p.name : ''; },
  };

  // ---------------- springs ----------------
  const ws = $('workspace');
  const W = { scale: 1, y: 0, blur: 0, dim: 1 };
  const paintWs = () => {
    ws.style.transform = `translateY(${W.y}px) scale(${W.scale})`;
    ws.style.filter = W.blur > 0.2 ? `blur(${W.blur}px) saturate(${1 + W.blur / 45})` : 'none';
    ws.style.opacity = W.dim;
  };
  const wsSpring = {};
  for (const k of Object.keys(W)) wsSpring[k] = new Spring(W[k], {}, v => { W[k] = v; paintWs(); }, k === 'dim' ? 'fade' : 'transform');

  const fade = (el, v) => { el.style.opacity = v; };
  const L = {};
  for (const id of ['agents', 'create', 'projects', 'cc', 'confirm'])
    L[id] = { el: $('layer-' + id), o: new Spring(0, { preset: 'smooth' }, v => fade($('layer-' + id), v), 'fade') };

  const dockEl = $('dock'), ccEl = $('cc');
  const dockY = new Spring(-360, { preset: 'sheet' }, v => { dockEl.style.transform = `translateY(${v}px)`; });
  const ccY = new Spring(innerHeight, { preset: 'sheet' }, v => { ccEl.style.transform = `translateY(${v}px)`; });
  const wheelS = {};
  for (const id of ['create', 'projects']) {   // never from scale(0): 0.92 → 1 (design.md §3)
    const el = $('wheel-' + id);
    wheelS[id] = new Spring(0.92, { preset: 'smooth' }, v => { el.style.transform = `scale(${v})`; });
  }
  const dlg = $('dialog');
  const dlgS = new Spring(0.96, { preset: 'snappy' }, v => { dlg.style.transform = `scale(${v})`; });
  const pageX = new Spring(0, { preset: 'page' }, v => {
    $('cc-grid').style.transform = `translateX(${-v * 28}%)`; $("cc-grid").style.opacity = Math.max(0, 1 - v * 1.6); $("cc-grid").style.pointerEvents = v > 0.5 ? "none" : "";
    $('cc-detail').style.transform = `translateX(${(1 - v) * 100}%)`;
    if (v < 0.02 && pageX.target === 0) $('cc-detail').innerHTML = '';
  });

  // Depth per layer (doc §6.2): v3 values; confirm pushes one level further back.
  const DEPTH = {
    zen:      { scale: 1,     y: 0,  blur: 0,  dim: 1 },
    agents:   { scale: 0.935, y: 36, blur: 18, dim: 0.75 },
    create:   { scale: 0.965, y: 0,  blur: 30, dim: 0.65 },
    projects: { scale: 0.965, y: 0,  blur: 30, dim: 0.65 },
    cc:       { scale: 0.94,  y: -18, blur: 14, dim: 0.7 },
  };
  function depth(layer) {
    const d = Object.assign({}, DEPTH[layer]);
    if (S.confirm) { d.scale -= 0.02; d.blur = Math.max(d.blur, 24); d.dim = Math.min(d.dim, 0.6); }
    if (root.dataset.transparency === 'reduced') { d.dim = Math.min(d.dim, layer === 'zen' ? 1 : 0.35); d.blur = 0; }
    return d;
  }
  function applyDepth(opts) { const d = depth(S.layer); for (const k in d) wsSpring[k].to(d[k], opts); }

  // ---------------- layer machine ----------------
  function setLayer(layer, mode, opts) {
    opts = opts || {};
    const prev = S.layer;
    S.layer = layer; S.mode = mode || 'sticky'; S.moved = false;
    S.sel = opts.sel !== undefined ? opts.sel : null;
    if (layer !== 'projects') closeSearch();
    for (const id in L) {
      const on = id === layer || (id === 'confirm' && S.confirm);
      L[id].el.classList.toggle('live', on);
      L[id].o.to(on ? 1 : 0, { preset: 'smooth' });
    }
    dockY.to(layer === 'agents' ? 0 : -360, opts.dockVelocity != null ? { preset: 'flick', velocity: opts.dockVelocity } : { preset: 'sheet' });
    ccY.to(layer === 'cc' ? 0 : ccEl.offsetHeight + 40, opts.ccVelocity != null ? { preset: 'flick', velocity: opts.ccVelocity } : { preset: 'sheet' });
    for (const id in wheelS) wheelS[id].to(layer === id ? 1 : 0.92, { preset: 'smooth' });
    applyDepth();
    if (layer === 'agents') {
      if (prev !== 'agents') { if (opts.sel === undefined) S.sel = defaultAgent(); V.dock(S); } else V.dockHeader(S);
      liftCards();
    }
    if (layer === 'create') { createW.setHot(S.sel); V.createHud(S, S.sel); }
    if (layer === 'projects') { projW.setHot(S.sel); V.projectsHud(S, S.sel, S.slots); if (S.sel === 0) openSearch(); }
    if (layer === 'cc' && prev !== 'cc') { V.ccHead(S); V.ccGrid(''); S.ccPage = null; pageX.jump(0); }
    if (layer === 'zen') { createW.setHot(null); projW.setHot(null); }
    orbit(layer === 'create' || layer === 'projects');
  }
  // Selected card lifts (v3: translateY(-7px) scale(1.03)) on a critically damped
  // spring — the v3 overshoot curve is dropped: nothing was thrown (apple-design §4).
  const lifts = new WeakMap();
  function liftCards() {
    document.querySelectorAll('#cards [data-card]').forEach(el => {
      if (!lifts.has(el)) lifts.set(el, new Spring(0, { preset: 'snappy' }, v => {
        el.style.transform = `translateY(${-7 * v}px) scale(${1 + 0.03 * v})`; }));
      const on = +el.dataset.card === S.sel;
      el.classList.toggle('selected', on); lifts.get(el).to(on ? 1 : 0, { preset: 'snappy' });
    });
  }
  function defaultAgent() { // like ⌘Tab: holding ⌥A pre-selects the previously used Agent
    const list = S.projectSessions(), i = list.findIndex(s => s.id === S.prevFocus);
    return i >= 0 ? i : 0;
  }

  // ---------------- wheels ----------------
  const createW = window.Wheel.create({
    host: $('wheel-create'), count: 4, rInner: 115, rOuter: 220, labelR: 168, gap: 2, deadR: 107,
    items: D.createSectors, enabled: () => true, accent: it => D.tools[it.tool].accent,
    label: it => `<span class="title" style="color:${D.tools[it.tool].accent}">${it.title}</span><span class="sub">${it.sub}</span>`,
  });
  let projW;
  function buildProjects() {
    projW = window.Wheel.create({
      host: $('wheel-projects'), count: 8, rInner: 126, rOuter: 232, labelR: 180, gap: 1.5, deadR: 120,
      items: S.slots, enabled: it => it !== null, accent: () => null,
      label: (it, i) => V.projectLabel(it, i),
    });
    projW.sectors[0].enabled = true; projW.sectors[0].path.classList.remove('empty'); // "更多" is always live
  }
  buildProjects();

  // ---------------- commit ----------------
  function commit(shift) {
    const layer = S.layer, sel = S.sel;
    if (layer === 'agents') {
      const list = S.projectSessions();
      if (sel === list.length) return setLayer('create', 'sticky');
      const s = list[sel]; if (!s) return setLayer('zen');
      focusSession(s.id); setLayer('zen'); toast(`已切入 ${s.name}`);
    } else if (layer === 'create') {
      if (sel == null) return setLayer('zen');
      const it = D.createSectors[sel];
      if (it.tool === 'advanced') { setLayer('zen'); return toast('打开完整创建面板（名称 / 参数 / 继续历史 / 分屏）'); }
      if (it.tool === 'fclaude') return openConfirm('create', null);
      newSession(it.tool, shift); setLayer('zen');
    } else if (layer === 'projects') {
      if (sel === 0) return setLayer('projects', 'sticky', { sel: 0 });
      const p = S.slots[sel]; if (!p) return setLayer('zen');   // released over nothing = cancel
      switchProject(p); setLayer('zen');
    }
  }
  function focusSession(id) {
    if (S.focus !== id) S.prevFocus = S.focus;
    S.focus = id;
    let tab = S.tabs.find(t => t.panes.includes(id));
    if (!tab) { tab = { id: 't' + Date.now(), panes: [id] }; S.tabs.push(tab); } // a hidden session gets its pane back
    S.tab = tab.id; renderWs();
  }
  let seq = 10;
  function newSession(tool, split) {
    const t = D.tools[tool], s = { id: 's' + (++seq), project: S.project, tool, name: `${t.name} ${seq - 9}`, status: 'idle',
      ago: '刚刚', cwd: S.projectName(), preview: `› ${t.name} 已启动 · 等待输入` };
    S.sessions.push(s);
    if (!S.tabsBy[S.project]) S.tabsBy[S.project] = [];
    const cur = S.tabs.find(x => x.id === S.tab);
    if (split && cur && cur.panes.length < 4) cur.panes.push(s.id);
    else S.tabs.push({ id: 't' + seq, panes: [s.id] });
    focusSession(s.id);
    toast(`${t.name} 已在 ${S.projectName()} 启动${split ? '（分屏）' : ''}`);
  }
  function switchProject(p) {
    if (!S.slots.includes(p)) { // spatial stability: fill an empty slot, else replace the oldest
      const empty = S.slots.indexOf(null, 1);
      S.slots[empty > 0 ? empty : 7] = Object.assign({ lang: '项目', dot: '#8E8E93', branch: 'main', lastAgent: '无' }, p);
      buildProjects();
    }
    S.project = p.id;
    const tabs = S.tabs;
    S.tab = tabs.length ? tabs[0].id : null;
    S.focus = tabs.length ? tabs[0].panes[0] : null;
    renderWs(); toast(`已切换到 ${p.name}`);
  }
  function renderWs() { V.panes(S); V.zenBar(S); }

  // ---------------- confirm dialog ----------------
  let confirmReturn = 'zen';
  function openConfirm(kind, id) {
    confirmReturn = S.layer === 'create' ? 'zen' : S.layer;
    S.confirm = { kind, id };
    V.dialog(kind, S.session(id));
    L.confirm.el.classList.add('live'); L.confirm.o.to(1); dlgS.jump(0.96).to(1, { preset: 'snappy' });
    $('confirm-scrim').style.background = 'var(--scrim)';
    applyDepth();
  }
  function closeConfirm(action) {
    const c = S.confirm; S.confirm = null;
    L.confirm.el.classList.remove('live'); L.confirm.o.to(0); dlgS.to(0.96, { preset: 'snappy' });
    if (action === 'create') { newSession('fclaude', false); setLayer('zen'); return; }
    if (action === 'stop') { stopSession(c.id); }
    if (action === 'hide') { hidePane(c.id); }
    if (S.layer === 'create') setLayer('zen'); else applyDepth();
  }
  function hidePane(id) {
    for (const t of S.tabs) t.panes = t.panes.filter(p => p !== id);
    S.tabsBy[S.project] = S.tabs.filter(t => t.panes.length);
    const tab = S.tabs[0]; S.tab = tab ? tab.id : null; S.focus = tab ? tab.panes[0] : null;
    renderWs(); toast('面板已隐藏，进程继续运行 · ⌥A 可找回');
  }
  function stopSession(id) {
    hidePane(id); S.sessions = S.sessions.filter(s => s.id !== id); toast('会话已停止');
  }

  // ---------------- project search (HUD of "··· 更多") ----------------
  const resultsEl = $('results');
  const resultsS = new Spring(0, { preset: 'snappy' }, v => {   // grows down from the HUD it belongs to
    resultsEl.style.opacity = v; resultsEl.style.transform = `translateY(${(1 - v) * -8}px) scale(${0.96 + v * 0.04})`;
  });
  function allProjects() { return [...D.projects, ...D.olderProjects]; }
  function openSearch() {
    S.search = ''; S.searchHot = 0;
    V.projectsHud(S, 0, S.slots);
    const input = $('proj-search');
    if (S.mode === 'sticky') requestAnimationFrame(() => input && input.focus());
    filterSearch();
  }
  function filterSearch() {
    const q = (S.search || '').toLowerCase();
    S.found = allProjects().filter(p => (p.name + p.path).toLowerCase().includes(q)).slice(0, 6);
    S.searchHot = Math.min(S.searchHot, Math.max(0, S.found.length - 1));
    V.results(S.found, S.searchHot); resultsS.to(1);
  }
  function closeSearch() {
    if (S.search === null) return;
    S.search = null; resultsS.to(0, { preset: 'snappy' });
    setTimeout(() => { if (S.search === null) V.results(null); }, 220);
  }

  // ---------------- theme (veil masks the brightness jump, apple-design §14) ----------------
  const veil = $('veil');
  const veilS = new Spring(0, { duration: 0.18, bounce: 0 }, v => { veil.style.opacity = v; }, 'fade');
  const dark = matchMedia('(prefers-color-scheme: dark)');
  const resolved = () => S.themePref === 'system' ? (dark.matches ? 'dark' : 'light') : S.themePref;
  function setTheme(pref, instant) {
    S.themePref = pref;
    const next = resolved();
    if (next === root.dataset.theme || instant) { root.dataset.theme = next; twinkle(); refreshThemeUi(); return; }
    veilS.to(0.92);
    setTimeout(() => { root.dataset.theme = next; twinkle(); refreshThemeUi(); veilS.to(0); }, Motion.reduced ? 160 : 150);
  }
  function refreshThemeUi() {
    document.querySelectorAll('[data-theme-set]').forEach(b => b.classList.toggle('active', b.dataset.themeSet === root.dataset.theme));
    if (S.layer === 'cc') { V.ccHead(S); if (S.ccPage === 'settings') $('cc-detail').innerHTML = V.settingsPage(S); }
  }
  dark.addEventListener('change', () => { if (S.themePref === 'system') setTheme('system'); });
  // Kawaii: sparkles are static; they twinkle once when the theme arrives (no idle loop).
  const sparkles = [...document.querySelectorAll('.sparkle')].map((el, i) =>
    new Spring(1, { duration: 0.5, bounce: 0.3 }, v => { el.style.transform = `scale(${v}) rotate(${(v - 1) * 60}deg)`; }));
  function twinkle() {
    if (root.dataset.theme !== 'kawaii' || Motion.reduced) return;
    sparkles.forEach((s, i) => setTimeout(() => { s.jump(0.6); s.to(1); }, i * 70));
  }

  // Orbit ring: rotates only while a wheel is shown, never under reduced motion.
  let orbitRaf = 0, orbitStart = 0;
  function orbit(on) {
    cancelAnimationFrame(orbitRaf); orbitRaf = 0;
    if (!on || Motion.reduced || root.dataset.theme !== 'kawaii') return;
    orbitStart = orbitStart || performance.now();
    const rings = document.querySelectorAll('.orbit');
    const loop = now => { const deg = ((now - orbitStart) / 28000) * 360; rings.forEach(r => { r.style.transform = `rotate(${deg}deg)`; }); orbitRaf = requestAnimationFrame(loop); };
    orbitRaf = requestAnimationFrame(loop);
  }

  // ---------------- toast ----------------
  const toastEl = $('toast'); let toastTimer = 0;
  const toastS = new Spring(0, { preset: 'snappy' }, v => { toastEl.style.opacity = v; toastEl.style.transform = `translate(-50%, ${(1 - v) * 10}px)`; });
  function toast(text) {
    toastEl.textContent = text; toastS.to(1);
    clearTimeout(toastTimer); toastTimer = setTimeout(() => toastS.to(0), 1800);
  }

  // ---------------- chord input (doc §3.2) ----------------
  // Hold ⌥ + letter → peek; release ⌥ → commit the selection. A quick tap
  // (<250 ms, nothing moved) leaves the layer sticky. Same letter again while
  // held cycles; a different letter re-targets mid-flight (springs keep velocity).
  const TAP_MS = 250, CHORDS = { KeyA: 'agents', KeyC: 'create', KeyX: 'projects', KeyS: 'cc' };
  let held = false, shiftAtRelease = false;
  function select(i) {
    S.sel = i; S.moved = true;
    if (S.layer === 'agents') liftCards();
    if (S.layer === 'create') { createW.setHot(i); V.createHud(S, i); }
    if (S.layer === 'projects') { projW.setHot(i); V.projectsHud(S, i, S.slots); if (i === 0) openSearch(); else closeSearch(); }
  }
  function chordDown(code) {
    const layer = CHORDS[code];
    if (layer === 'cc') return setLayer(S.layer === 'cc' ? 'zen' : 'cc', 'sticky');
    if (held && S.layer === layer) {                            // cycle while held
      if (layer === 'agents') select((S.sel + 1) % (S.projectSessions().length + 1));
      else select((layer === 'create' ? createW : projW).next(1));
      return;
    }
    if (!held && S.layer === layer && S.mode === 'sticky') return setLayer('zen'); // tap again closes
    held = true; S.chordAt = performance.now();
    setLayer(layer, 'peek');
  }
  function chordUp() {
    if (!held) return; held = false;
    if (S.mode !== 'peek') return;
    const quick = performance.now() - S.chordAt < TAP_MS && !S.moved;
    if (quick) { S.mode = 'sticky'; return setLayer(S.layer, 'sticky', { sel: S.sel }); }
    commit(shiftAtRelease);
  }
  addEventListener('blur', () => { if (held) { held = false; if (S.mode === 'peek') setLayer(S.layer, 'sticky', { sel: S.sel }); } });

  function navKeys(e) {
    const wheel = S.layer === 'create' ? createW : S.layer === 'projects' ? projW : null;
    const n = S.layer === 'agents' ? S.projectSessions().length + 1 : 0;
    const k = e.key;
    if (k === 'Escape') { if (S.layer === 'cc' && S.ccPage) return popPage(); return setLayer('zen'); }
    if (k === 'Enter' && S.sel != null) return commit(e.shiftKey);
    const dir = { ArrowRight: 1, ArrowDown: 1, Tab: e.shiftKey ? -1 : 1, ArrowLeft: -1, ArrowUp: -1 }[k];
    if (dir && S.layer === 'agents') { e.preventDefault(); return select(((S.sel == null ? -1 : S.sel) + dir + n) % n); }
    if (dir && wheel) { e.preventDefault(); return select(wheel.next(dir)); }
    if (wheel && /^[1-8]$/.test(k) && +k <= wheel.sectors.length) {
      const i = +k - 1; if (wheel.sectors[i].enabled) select(i);
    }
  }
  function inputKeys(e) {
    if (e.target.id === 'proj-search') {
      if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
        e.preventDefault(); S.searchHot = Math.max(0, Math.min((S.found || []).length - 1, S.searchHot + (e.key === 'ArrowDown' ? 1 : -1)));
        return V.results(S.found, S.searchHot);
      }
      if (e.key === 'Enter') { const p = (S.found || [])[S.searchHot]; if (p) { switchProject(p); setLayer('zen'); } else { toast('按路径打开：将调用原生目录校验'); } return; }
      if (e.key === 'Escape') { e.target.blur(); return setLayer('zen'); }
    }
    if (e.target.id === 'cc-search' && e.key === 'Escape') { e.target.blur(); return setLayer('zen'); }
  }
  addEventListener('keydown', e => {
    shiftAtRelease = e.shiftKey;
    if (S.confirm) { if (e.key === 'Escape') closeConfirm('cancel'); if (e.key === 'Enter') dlg.querySelector('.primary, .danger').click(); return; }
    if (e.altKey && CHORDS[e.code] && !e.metaKey && !e.ctrlKey) { e.preventDefault(); if (!e.repeat) chordDown(e.code); return; }
    if (e.target.tagName === 'INPUT' && e.target.type !== 'checkbox') return inputKeys(e);
    // Reviewer convenience: bare A/C/X/S open the layer sticky (not product behaviour).
    if (!e.altKey && !e.metaKey && !e.ctrlKey && CHORDS[e.code] && S.layer === 'zen') return setLayer(CHORDS[e.code], 'sticky');
    if (S.layer !== 'zen') navKeys(e);
  });
  addEventListener('keyup', e => { shiftAtRelease = e.shiftKey; if (e.key === 'Alt') chordUp(); });

  // ---------------- pointer: feedback on pointer-down, commit on release ----------------
  const pressSprings = new WeakMap();
  function pressFx(el, down) {
    if (!pressSprings.has(el)) pressSprings.set(el, new Spring(1, { preset: 'press' }, v => { el.style.transform = `scale(${v})`; }));
    pressSprings.get(el).to(down ? 0.97 : 1, { preset: down ? 'press' : 'snappy' });
  }
  document.addEventListener('pointerdown', e => { const p = e.target.closest('.press'); if (p) pressFx(p, true); });
  document.addEventListener('pointerup', () => document.querySelectorAll('.press').forEach(p => pressSprings.has(p) && pressFx(p, false)));

  $('cards').addEventListener('pointerover', e => { const c = e.target.closest('[data-card]'); if (c && +c.dataset.card !== S.sel) select(+c.dataset.card); });
  $('cards').addEventListener('click', e => { const c = e.target.closest('[data-card]'); if (c) { S.sel = +c.dataset.card; commit(e.shiftKey); } });

  for (const [id, w] of [['create', () => createW], ['projects', () => projW]]) {
    const stage = $('layer-' + id).querySelector('.radial-stage');
    let last = null;
    stage.addEventListener('pointermove', e => {
      if (last && Math.hypot(e.clientX - last.x, e.clientY - last.y) < 4) return; // hysteresis
      last = { x: e.clientX, y: e.clientY };
      if (e.target.closest('.results, input, button')) return;
      const i = w().hitTest(e.clientX, e.clientY, S.mode === 'peek');
      if (i != null && i !== S.sel && w().sectors[i].enabled) select(i);
    });
    stage.addEventListener('pointerdown', e => {
      if (e.target.closest('.hud, .results')) return;
      const i = w().hitTest(e.clientX, e.clientY, false);
      if (i == null) return setLayer('zen');           // outside the ring dismisses
      w().press(i, true);
    });
    stage.addEventListener('pointerup', e => {
      if (e.target.closest('.hud, .results')) return;
      const i = w().hitTest(e.clientX, e.clientY, false);
      w().sectors.forEach((_, j) => w().press(j, false));
      if (i != null && w().sectors[i].enabled) { S.sel = i; commit(e.shiftKey); }
    });
  }
  $('results').addEventListener('click', e => { const r = e.target.closest('[data-result]'); if (r) { switchProject(S.found[+r.dataset.result]); setLayer('zen'); } });
  $('hud-projects').addEventListener('input', e => { if (e.target.id === 'proj-search') { S.search = e.target.value; S.searchHot = 0; filterSearch(); } });
  $('hud-projects').addEventListener('click', e => { if (e.target.id === 'open-folder') { setLayer('zen'); toast('打开系统目录选择器…'); } });

  // ---------------- drag: dock up / sheet down, 1:1 with momentum (apple-design §2, §5, §6, §9) ----------------
  const lerp = (a, b, t) => a + (b - a) * t;
  function blendDepth(from, to, t) { const a = depth(from), b = depth(to); for (const k in a) wsSpring[k].jump(lerp(a[k], b[k], t)); }
  function draggable(handle, o) {
    const vt = new VelocityTracker(); let start = null;
    handle.addEventListener('pointerdown', e => {
      handle.setPointerCapture(e.pointerId); vt.reset(); vt.add(e.clientX, e.clientY);
      start = { y: e.clientY, base: o.spring.value, moved: false };
    });
    handle.addEventListener('pointermove', e => {
      if (!start) return; vt.add(e.clientX, e.clientY);
      const dy = e.clientY - start.y;
      if (!start.moved && Math.abs(dy) < 10) return;      // ~10px hysteresis before committing to a drag
      start.moved = true;
      o.onStart && o.onStart();
      let y = start.base + dy;
      if (y > o.max) y = o.max + rubberband(y - o.max, innerHeight);
      if (y < o.min) y = o.min - rubberband(o.min - y, innerHeight);
      o.spring.jump(y); o.onMove(y);
    });
    handle.addEventListener('pointerup', () => {
      if (!start) return; const moved = start.moved; start = null;
      if (!moved) return o.onTap && o.onTap();
      const v = vt.velocity().y;
      o.onRelease(o.spring.value + project(v), v);         // choose the target from the projection
    });
  }
  const DOCK_H = 360;
  draggable($('dock-grab'), {
    spring: dockY, min: -DOCK_H, max: 0,
    onMove: y => blendDepth('zen', 'agents', 1 + y / DOCK_H),
    onRelease: (p, v) => setLayer(p < -DOCK_H / 2 ? 'zen' : 'agents', 'sticky', { dockVelocity: v, sel: S.sel }),
  });
  const ccH = () => ccEl.offsetHeight + 40;
  const ccDrag = onTap => ({
    spring: ccY, min: 0, get max() { return ccH(); }, onTap,
    onStart: () => { if (S.layer !== 'cc') { V.ccHead(S); V.ccGrid(''); L.cc.el.classList.add('live'); L.cc.o.jump(1); } },
    onMove: y => blendDepth('zen', 'cc', 1 - y / ccH()),
    onRelease: (p, v) => setLayer(p < ccH() / 2 ? 'cc' : 'zen', 'sticky', { ccVelocity: v }),
  });
  draggable($('zen-bar'), ccDrag(() => setLayer('cc', 'sticky')));   // drag up the breathing bar, or tap it
  draggable($('cc-grab'), ccDrag(() => setLayer('zen')));

  // ---------------- Control Center pages (push / pop, mirrored path) ----------------
  function openPage(id) {
    const tile = D.ccGroups.flatMap(g => g.tiles).find(t => t.id === id);
    S.ccPage = id;
    $('cc-detail').innerHTML = id === 'sync' ? V.syncPage(S.op) : id === 'settings' ? V.settingsPage(S) : V.genericPage(tile);
    $('cc-detail').scrollTop = 0; pageX.to(1, { preset: 'page' });
  }
  function popPage() { S.ccPage = null; pageX.to(0, { preset: 'page' }); }
  const renderSync = () => { if (S.ccPage === 'sync') $('cc-detail').innerHTML = V.syncPage(S.op); V.zenBar(S); };
  function syncAction(a) {
    if (a === 'pause') S.op = { review: true };
    if (a === 'reset') return toast('重建基线：先显示可能恢复旧删除的警告，再进入审阅');
    if (a === 'cancel') S.op = null;
    if (a === 'confirm') {
      const lose = $('lose') && $('lose').checked;
      S.op = { running: true, lost: lose, stages: [{ name: 'Server 记录', st: 'run' }, { name: '本地 Mutagen', st: 'wait' }, { name: '共享 SQLite', st: 'wait' }] };
      const op = S.op;
      setTimeout(() => { op.stages[0].st = 'done'; op.stages[1].st = 'run'; renderSync(); }, 900);
      setTimeout(() => { op.stages[1].st = lose ? 'unknown' : 'done'; op.stages[2].st = lose ? 'unknown' : 'run'; renderSync(); }, 1900);
      setTimeout(() => { if (!lose) op.stages[2].st = 'done'; op.running = false; op.done = true; renderSync();
        if (S.layer !== 'cc' || S.ccPage !== 'sync') toast(lose ? '同步：结果未知，需要查询' : '同步已暂停'); }, 2700);
    }
    if (a === 'query' && S.op) { S.op.lost = false; S.op.stages.forEach(s => { s.st = 'done'; }); toast('已查询原操作：completed'); }
    if (a === 'finish') { S.op = null; D.ccGroups[0].tiles[0].s = '已暂停 · 无冲突'; }
    renderSync();
  }
  $('cc').addEventListener('click', e => {
    const t = e.target.closest('[data-tile]'); if (t) return openPage(t.dataset.tile);
    if (e.target.closest('[data-back]')) return popPage();
    const th = e.target.closest('[data-theme-pref]'); if (th) return setTheme(th.dataset.themePref);
    const sy = e.target.closest('[data-sync]'); if (sy) return syncAction(sy.dataset.sync);
    if (e.target.closest('[data-dismiss]')) setLayer('zen');
  });
  $('cc-head').addEventListener('input', e => { if (e.target.id === 'cc-search') { if (S.ccPage) popPage(); V.ccGrid(e.target.value); } });
  document.querySelectorAll('.scrim[data-dismiss]').forEach(s => s.addEventListener('click', () => setLayer('zen')));

  // ---------------- workspace & dialog ----------------
  $('panes').addEventListener('click', e => {
    const q = e.target.closest('[data-quick]');
    if (q) return q.dataset.quick === 'fclaude' ? openConfirm('create', null) : newSession(q.dataset.quick, false);
    const h = e.target.closest('[data-hide]'); if (h) return hidePane(h.dataset.hide);
    const st = e.target.closest('[data-stop]'); if (st) return openConfirm('stop', st.dataset.stop);
    const p = e.target.closest('[data-pane]'); if (p && p.dataset.pane !== S.focus) focusSession(p.dataset.pane);
  });
  dlg.addEventListener('click', e => { const b = e.target.closest('[data-dlg]'); if (b) closeConfirm(b.dataset.dlg); });
  $('confirm-scrim').addEventListener('click', () => closeConfirm('cancel'));

  // ---------------- prototype chrome ----------------
  $('proto').addEventListener('click', e => {
    const go = e.target.closest('[data-go]');
    if (go) { const v = go.dataset.go; v === 'more' ? setLayer('projects', 'sticky', { sel: 0 }) : setLayer(v === 'zen' ? 'zen' : v, 'sticky'); }
    const th = e.target.closest('[data-theme-set]'); if (th) setTheme(th.dataset.themeSet);
  });
  $('rm').addEventListener('change', e => window.Physics.setReduced(e.target.checked || matchMedia('(prefers-reduced-motion: reduce)').matches));
  const rtMq = matchMedia('(prefers-reduced-transparency: reduce)');
  const applyRt = () => { root.dataset.transparency = ($('rt').checked || rtMq.matches) ? 'reduced' : ''; applyDepth(); };
  $('rt').addEventListener('change', applyRt); rtMq.addEventListener('change', applyRt);
  Motion.listeners.add(v => { $('rm').checked = v; orbit(!v && (S.layer === 'create' || S.layer === 'projects')); });

  // ---------------- init ----------------
  $('layer-cc').querySelector('.scrim').style.background = 'var(--scrim)';
  setTheme('system', true); applyRt(); renderWs();
  ccY.jump(ccH()); dockY.jump(-DOCK_H);
  addEventListener('resize', () => { if (S.layer !== 'cc') ccY.jump(ccH()); });
  $('rm').checked = Motion.reduced;

  window.App = { S, setLayer, commit, setTheme, toast, switchProject, renderWs };
})();
