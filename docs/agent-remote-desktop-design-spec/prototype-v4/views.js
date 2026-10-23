/* Pure renderers: state in, DOM out. No motion here — app.js owns springs. */
(function () {
  'use strict';
  const D = window.Data;
  const $ = id => document.getElementById(id);
  const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const tool = s => D.tools[s.tool];
  const STATUS = { output: '有新输出', idle: '空闲', connected: '已连接', disconnected: '未连接', exited: '已退出 · 0' };
  const dot = st => `<span class="dot ${st === 'output' ? 'output' : ''} ${st === 'disconnected' ? 'hollow' : ''}" style="--dot:${
    st === 'output' ? 'var(--accent-codex)' : st === 'connected' ? 'var(--tool-fclaude)' : 'var(--text-tertiary)'}"></span>`;

  // Terminal mock — what an Agent TUI looks like inside the opaque pane.
  const TERM = {
    claude: `<span class="dim">╭─ claude · ~/Documents/Git/agent-remote-desktop</span>
<span class="dim">│</span> &gt; 把工作台改成 Zen 布局，侧栏和顶栏全部移走，入口改到 ⌥A/⌥C/⌥X

<span class="ok">●</span> Read(internal/app/view.go) <span class="dim">· 525 lines</span>
<span class="ok">●</span> Update(internal/app/zen.go)
  <span class="dim">⎿</span>  <span class="kw">func</span> (a *App) <span class="fn">zenView</span>(c *ui.Context) {
       ui.Box(c).Fill().Children(<span class="kw">func</span>() {
         a.<span class="fn">panes</span>(c, a.state.Board.Current(a.project()))
         a.<span class="fn">breathingBar</span>(c) <span class="cmt">// 状态呼吸条，44 DIP</span>
       })
     }
<span class="ok">●</span> Bash(go test ./tests/app/...)
  <span class="dim">⎿</span>  <span class="ok">ok</span>  github.com/Agent-Remote/agent-remote-desktop/tests/app  3.12s

&gt; <span class="caret"></span>`,
    codex: `<span class="dim">codex · locales/</span>

› add zh-Hans strings for control center tiles
• Edited <span class="str">locales/zh-Hans.json</span> (+36 -0)
• Edited <span class="str">locales/en.json</span> (+36 -0)
• Ran <span class="fn">go run github.com/egoist/mygo/cmd/mygo i18n check</span>
  <span class="ok">✓ 2 locales, 0 missing</span>

› <span class="caret"></span>`,
    fclaude: `<span class="dim">fclaude attach · node-01 · tmux a1f3c9e2</span>

<span class="ok">●</span> 已连接远程会话（单写入连接）
<span class="dim">  account claude-main · backend docker</span>

&gt; <span class="caret"></span>`,
  };

  function panes(state) {
    const host = $('panes'), tab = state.tabs.find(t => t.id === state.tab);
    if (!tab) {
      host.innerHTML = `<div class="pane"><div class="pane-empty">
        <h2>为 ${esc(state.projectName())} 选择 Agent</h2>
        <p>按 <b>⌥C</b> 新建，或从下方入口直接启动</p>
        <div class="actions" style="justify-content:center">
          <button class="btn" data-quick="claude">Claude · 本地</button>
          <button class="btn" data-quick="codex">Codex · 本地</button>
          <button class="btn" data-quick="fclaude">fclaude · 远程</button></div></div></div>`;
      return;
    }
    host.innerHTML = tab.panes.map(id => {
      const s = state.session(id), t = tool(s);
      return `<div class="pane ${id === state.focus ? 'focused' : ''}" data-pane="${id}" style="--pane-accent:${t.accent}">
        <div class="pane-chip">${dot(s.status)}<span>${esc(s.name)} · ${t.name} ${t.where}</span>
          <button class="chip-btn" title="隐藏面板（进程保留）" data-hide="${id}">–</button>
          <button class="chip-btn" title="关闭会话…" data-stop="${id}">×</button></div>
        <div class="term">${TERM[s.tool]}</div></div>`;
    }).join('');
  }

  function zenBar(state) {
    const s = state.session(state.focus), op = state.op && state.op.running;
    $('zen-context').innerHTML = `<span>项目 <strong>${esc(state.projectName())}</strong></span><span>·</span>
      <span>${s ? `Agent <strong>${esc(s.name)}</strong> · ${tool(s).name}` : '无 Agent'}</span><span>·</span>
      ${op ? `<span class="op-badge"><span class="dot output" style="--dot:var(--accent)"></span>同步 · 暂停中</span><span>·</span>` : ''}
      <span><kbd>⌥A</kbd> <kbd>⌥C</kbd> <kbd>⌥X</kbd> <kbd>⌥S</kbd></span>`;
  }

  function dockHeader(state) {
    $('dock-header').innerHTML = `<span>✦ ⌥A · 项目 <strong>${esc(state.projectName().toUpperCase())}</strong> — ${state.projectSessions().length} 个 AGENT</span>
      <span>${state.mode === 'peek' ? '按住 ⌥ 再按 A 轮换 · 松开 ⌥ 切入' : '←/→ 选择 · Enter 切入 · 上推收起 · Esc 返回'}</span>`;
  }

  function dock(state) {
    const list = state.projectSessions();
    dockHeader(state);
    $('cards').innerHTML = list.map((s, i) => {
      const t = tool(s), tab = state.tabs.find(x => x.panes.includes(s.id));
      const split = tab && tab.panes.length > 1 ? ` · 分屏 ${tab.panes.indexOf(s.id) + 1}/${tab.panes.length}` : '';
      return `<div class="agent-card ${i === state.sel ? 'selected' : ''}" data-card="${i}">
        <div class="card-top"><span class="name" style="color:${t.accent}">✦ ${esc(s.name)}</span>
          <span class="status-pill">${dot(s.status)} ${STATUS[s.status]}</span></div>
        <div class="card-preview">${esc(s.preview)}</div>
        <div class="card-footer"><span>${t.name} · ${t.where} · ${esc(s.cwd)}${split}</span><span>${s.ago}</span></div></div>`;
    }).join('') + `<div class="agent-card ghost ${state.sel === list.length ? 'selected' : ''}" data-card="${list.length}" style="max-width:150px">＋<span>新建 Agent</span><span style="font-weight:500;font-size:11px">⌥C</span></div>`;
  }

  function createHud(state, i) {
    const p = state.projectName(), s = i == null ? null : D.createSectors[i];
    $('hud-create').innerHTML = !s
      ? `<div class="hud-tag">✦ ⌥C ✦</div><div class="hud-title">新建 Agent</div>
         <div class="hud-path">${state.mode === 'peek' ? '移向扇区，松开 ⌥ 创建' : '点击扇区或 ↑↓ + Enter'}</div>
         <div class="hud-meta">所属项目 · ${esc(p)}</div>`
      : `<div class="hud-tag">✦ ${s.tool === 'advanced' ? 'ADVANCED' : D.tools[s.tool].where + ' AGENT'} ✦</div>
         <div class="hud-title" style="color:${D.tools[s.tool].accent}">${s.title}</div>
         <div class="hud-path">${esc(s.desc)}</div>
         <div class="hud-meta">${esc(s.meta)}</div>
         <div class="hud-foot">${s.tool === 'advanced' ? '' : '按住 ⇧ 松开 = 在当前面板旁分屏'}</div>`;
  }

  window.Views = { $, esc, panes, zenBar, dock, dockHeader, createHud, dot, STATUS, TERM };
})();
