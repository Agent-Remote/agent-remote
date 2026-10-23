/* Renderers for the project HUD, Control Center and dialogs. */
(function () {
  'use strict';
  const D = window.Data, V = window.Views, { $, esc } = V;

  function projectLabel(p, i) {
    if (i === 0) return `<span class="title">··· 更多</span><span class="badge">搜索 / 打开</span>`;
    if (!p) return `<span class="title">—</span><span class="sub">空位</span>`;
    const n = D.sessions.filter(s => s.project === p.id).length;
    return `<span class="title" style="font-size:13px">${esc(p.name.replace('agent-remote-', 'ar-'))}</span>
      <span class="badge"><span class="dot" style="--dot:${p.dot}"></span>${p.lang} · ${n} Agent</span>`;
  }

  function projectsHud(state, i, slots) {
    const hud = $('hud-projects'), p = i == null ? null : slots[i];
    if (i === 0) {
      if (!hud.querySelector('input')) hud.innerHTML = `<div class="hud-tag">✦ ⌥X · SPOTLIGHT ✦</div>
        <div class="hud-title" style="font-size:15px">搜索或打开项目</div>
        <input class="search-input" id="proj-search" placeholder="项目名或路径…" autocomplete="off" spellcheck="false">
        <button class="btn" id="open-folder">+ 打开本地文件夹…</button>`;
      return;
    }
    hud.innerHTML = !p
      ? `<div class="hud-tag">✦ ⌥X ✦</div><div class="hud-title">切换项目</div>
         <div class="hud-path">${state.mode === 'peek' ? '移向扇区，松开 ⌥ 切换' : '点击扇区或 ←→ + Enter'}</div>
         <div class="hud-meta">当前 · ${esc(state.projectName())}</div>`
      : `<div class="hud-tag">✦ ${p.lang} PROJECT ✦</div><div class="hud-title">${esc(p.name)}</div>
         <div class="hud-path">${esc(p.path)}</div>
         <div class="hud-meta"><span class="git-pill">⎇ ${esc(p.branch)}</span></div>
         <div class="hud-foot">上次驻留: <strong>${esc(p.lastAgent)}</strong></div>`;
  }

  function results(list, hot) {
    const box = $('results');
    box.hidden = list === null;
    if (list === null) return;
    box.innerHTML = list.length
      ? list.map((p, i) => `<div class="result ${i === hot ? 'hot' : ''}" data-result="${i}"><span>${esc(p.name)}</span><span>${esc(p.path)}</span></div>`).join('')
      : `<div class="result"><span>没有匹配的项目</span><span>Enter 按路径打开</span></div>`;
  }

  function ccHead(state) {
    const th = state.themePref;
    $('cc-head').innerHTML = `<h1>控制中心</h1><span class="acct"><span class="dot" style="--dot:var(--accent-codex)"></span>${esc(D.context.account)}</span>
      <span class="grow"></span><input class="cc-search" id="cc-search" placeholder="搜索命令、页面、会话…  ⌘⇧P">
      <div class="seg">${[['system', '跟随系统'], ['light', '浅色'], ['dark', '深色'], ['kawaii', '次元']].map(([k, l]) =>
        `<button data-theme-pref="${k}" class="${th === k ? 'active' : ''}">${l}</button>`).join('')}</div>
      <button class="close-x" data-dismiss title="关闭 (Esc)">×</button>`;
  }

  function ccGrid(query) {
    const q = (query || '').trim().toLowerCase();
    $('cc-grid').innerHTML = D.ccGroups.map(g => {
      const tiles = g.tiles.filter(t => !q || (t.t + t.s + t.id).toLowerCase().includes(q));
      if (!tiles.length) return '';
      return `<section class="group"><h3>${g.title}</h3><div class="tiles">${tiles.map(t =>
        `<div class="tile press ${t.wide ? 'wide' : ''}" data-tile="${t.id}"><div class="t"><span class="glyph">${t.g}</span>${t.t}</div>
         <div class="s ${t.cls || ''}">${t.s}</div></div>`).join('')}</div></section>`;
    }).join('') || `<p class="note">没有匹配「${esc(q)}」的页面</p>`;
  }

  const ctx = () => `<div class="ctx"><span><b>home</b>${D.context.home}</span><span><b>server</b>${D.context.server}</span>
    <span><b>device</b>${D.context.device}</span><span><b>project</b>~/Documents/Git/agent-remote-desktop</span></div>`;
  const crumb = t => `<div class="crumb"><button class="back" data-back>‹ 控制中心</button><h2>${t}</h2></div>`;

  function syncPage(op) {
    const stage = (name, st, note) => `<li class="stage ${st}"><i></i>${name}<em>${note}</em></li>`;
    const label = { done: '完成', run: '进行中', wait: '等待', unknown: '未知' };
    let body = `<div class="panel"><h4>观察 · sync.status</h4><dl class="kv">
      <dt>Server 状态</dt><dd>${op && op.done && !op.lost ? 'paused' : 'active'}</dd><dt>冲突</dt><dd>none</dd>
      <dt>Mutagen</dt><dd>${op && op.done && !op.lost ? 'paused' : 'watching'}</dd><dt>remote_path</dt><dd>/srv/workspaces/ar-desktop</dd>
      <dt>sync_session_id</dt><dd>sync_7f2c…e91a</dd><dt>fingerprint</dt><dd>fp_3b8d…02c4</dd></dl>`;
    if (!op) body += `<div class="actions" style="margin-top:14px">
        <button class="btn" data-sync="pause">暂停</button><button class="btn" disabled>恢复</button>
        <button class="btn" disabled>解决冲突</button><button class="btn" data-sync="reset">重建基线…</button>
        <label class="note" style="margin:0 0 0 auto"><input type="checkbox"> 跳过本地执行（仍修改 Server 与共享 SQLite）</label></div>`;
    body += `</div>`;
    if (op && op.review) body += `<div class="panel review"><h4>审阅 · 暂停同步</h4>
      <p class="note">确认绑定以上准确目标与指纹。提交后不会自动重试；结果未知时只查询原操作。</p>
      <label class="note"><input type="checkbox" id="lose"> 原型：模拟回执丢失</label>
      <div class="actions" style="justify-content:flex-end;margin-top:12px"><button class="btn" data-sync="cancel">取消</button>
      <button class="btn primary" data-sync="confirm">确认暂停</button></div></div>`;
    if (op && !op.review) {
      if (op.lost && op.done) body = `<div class="banner"><span>⚠</span><span class="grow">结果未知：本地 Mutagen 阶段未返回回执。不会自动重放。</span>
        <button class="btn" data-sync="query">查询原操作</button></div>` + body;
      body += `<div class="panel"><h4>阶段</h4><ul class="stages">${op.stages.map(s => stage(s.name, s.st, label[s.st] || '')).join('')}</ul>
        ${op.running ? `<div class="actions" style="margin-top:12px"><button class="btn">停止等待</button><span class="note" style="margin:0">停止等待不会撤销已提交的远端操作</span></div>` : ''}</div>`;
      if (op.done) body += `<div class="panel"><h4>回执</h4><dl class="kv"><dt>outcome</dt><dd>${op.lost ? 'unknown' : 'completed'}</dd>
        <dt>operation_id</dt><dd>op_51d0…a7e3</dd><dt>method</dt><dd>sync.pause</dd></dl>
        <p class="note">精确回执由 CLI journal 保存；操作中心只保留安全摘要。</p>
        <div class="actions" style="justify-content:flex-end;margin-top:10px"><button class="btn" data-sync="finish">完成</button></div></div>`;
    }
    return crumb('项目同步') + ctx() + body;
  }

  function genericPage(tile) {
    return crumb(tile.t) + ctx() + `<div class="panel"><h4>观察</h4><p class="note" style="margin:0">${tile.s}。进入页面不会自动执行查询或变更，点击「检查」才会调用 CLI。</p>
      <div class="actions" style="margin-top:12px"><button class="btn">检查</button><button class="btn">刷新</button></div></div>
      <div class="panel"><h4>页面模板</h4><p class="note" style="margin:0">所有管理页共用：上下文条 → 观察 → 审阅（冻结计划）→ 阶段 → 回执 → 恢复。详见方案 §4.5。</p></div>`;
  }

  function settingsPage(state) {
    return crumb('设置') + `<div class="panel"><h4>外观</h4><div class="actions">
      <div class="seg">${[['system', '跟随系统'], ['light', '浅色'], ['dark', '深色'], ['kawaii', '次元']].map(([k, l]) =>
        `<button data-theme-pref="${k}" class="${state.themePref === k ? 'active' : ''}">${l}</button>`).join('')}</div></div>
      <p class="note">减弱动效与降低透明度同时跟随系统设置；这里的开关只能额外开启，不能覆盖系统要求。</p></div>
      <div class="panel"><h4>语言</h4><div class="actions"><button class="btn">跟随系统</button><button class="btn">English</button><button class="btn primary">简体中文</button></div></div>
      <div class="panel"><h4>快捷键</h4><dl class="kv"><dt>Agent / 新建 / 项目</dt><dd>⌥A / ⌥C / ⌥X（修饰键可改为 ⌃⌥）</dd>
      <dt>控制中心</dt><dd>⌥S</dd><dt>搜索</dt><dd>⌘⇧P</dd></dl></div>
      <div class="panel"><h4>工具</h4><dl class="kv"><dt>claude</dt><dd>${D.tools.claude.exec}</dd><dt>codex</dt><dd>${D.tools.codex.exec}</dd>
      <dt>fclaude</dt><dd>${D.tools.fclaude.exec}</dd></dl></div>`;
  }

  function dialog(kind, s) {
    const html = kind === 'stop'
      ? `<h3>关闭「${esc(s.name)}」？</h3><p>停止会结束 ${D.tools[s.tool].name} 进程。只隐藏面板则进程继续运行，可从 ⌥A 找回。</p>
         <div class="path">${esc(s.cwd)}</div><div class="actions"><button class="btn" data-dlg="cancel">取消</button>
         <button class="btn" data-dlg="hide">只隐藏</button><button class="btn danger" data-dlg="stop">停止会话</button></div>`
      : `<h3>创建远程 fclaude 会话</h3><p>将在已审阅的上下文中提交一次创建请求；回执丢失时只查询原请求，不会重放。</p>
         <div class="path">server ${D.context.server} · device ${D.context.device} · 账户 claude-main</div>
         <div class="actions"><button class="btn" data-dlg="cancel">取消</button><button class="btn primary" data-dlg="create">确认创建</button></div>`;
    $('dialog').innerHTML = html;
  }

  Object.assign(window.Views, { projectLabel, projectsHud, results, ccHead, ccGrid, syncPage, genericPage, settingsPage, dialog });
})();
