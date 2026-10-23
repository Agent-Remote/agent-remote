/* Mock data shaped like the desktop's real models (workspace.Project,
 * session.Record, storage.Session). Status values are the fact-only set the
 * product can actually observe from a PTY — never "thinking" or "awaiting approval". */
(function () {
  'use strict';

  const tools = {
    claude:   { name: 'Claude',  where: '本地', accent: 'var(--tool-claude)',  exec: '/opt/homebrew/bin/claude' },
    codex:    { name: 'Codex',   where: '本地', accent: 'var(--tool-codex)',   exec: '/opt/homebrew/bin/codex' },
    fclaude:  { name: 'fclaude', where: '远程', accent: 'var(--tool-fclaude)', exec: '~/.cargo/bin/fclaude' },
    advanced: { name: '高级…',   where: '',     accent: 'var(--tool-advanced)' },
  };

  // Space+C sectors in the fixed spatial order: 12 → 3 → 6 → 9 o'clock.
  const createSectors = [
    { tool: 'claude',   title: 'Claude',  sub: '本地 · 当前项目', desc: '在项目目录启动 claude', meta: '可用 · 2.1.3' },
    { tool: 'codex',    title: 'Codex',   sub: '本地 · 当前项目', desc: '在项目目录启动 codex',  meta: '可用 · 0.48.0' },
    { tool: 'fclaude',  title: 'fclaude', sub: '远程 · 已登录',   desc: '审阅后在远程节点创建',  meta: 'server · dev.agent-remote.test' },
    { tool: 'advanced', title: '高级…',   sub: '名称 / 参数 / 历史', desc: '打开完整创建面板', meta: '分屏、继续历史会话' },
  ];

  const projects = [
    { id: 'p1', name: 'agent-remote-desktop', lang: 'Go',     dot: '#00ADD8', path: '~/Documents/Git/agent-remote-desktop', branch: 'feature/desktop-workbench', lastAgent: 'Claude · 本地' },
    { id: 'p2', name: 'agent-remote-cli',     lang: 'Rust',   dot: '#DEA584', path: '~/Documents/Git/agent-remote-cli',     branch: 'feature/desktop-machine-contract', lastAgent: 'Codex · 本地' },
    { id: 'p3', name: 'agent-remote-server',  lang: 'Python', dot: '#3572A5', path: '~/Documents/Git/agent-remote-server',  branch: 'main', lastAgent: 'fclaude · 远程' },
    { id: 'p4', name: 'agent-remote-node',    lang: 'Go',     dot: '#00ADD8', path: '~/Documents/Git/agent-remote-node',    branch: 'main', lastAgent: 'Claude · 本地' },
    { id: 'p5', name: 'agent-remote-admin-web', lang: 'TypeScript', dot: '#3178C6', path: '~/Documents/Git/agent-remote-admin-web', branch: 'main', lastAgent: '无' },
    { id: 'p6', name: 'agent-remote',         lang: '文档',   dot: '#8E8E93', path: '~/Documents/Git/agent-remote',         branch: 'main', lastAgent: 'Claude · 本地' },
  ]; // six recents → one empty slot keeps the 8-sector geometry stable
  const olderProjects = [
    { id: 'p7', name: 'agent-remote-ego-browser', path: '~/Documents/Git/agent-remote-ego-browser' },
    { id: 'p8', name: 'MoviePilot', path: '~/Documents/Git/MoviePilot' },
  ];

  const sessions = [
    { id: 's1', project: 'p1', tool: 'claude', name: 'Zen 布局重构', status: 'output', ago: '刚刚', cwd: 'internal/app',
      preview: '● Update(internal/app/zen.go)\n  ⎿  Updated with 42 additions\n● Bash(go test ./tests/app/...)\n  ⎿  ok  tests/app  3.12s' },
    { id: 's2', project: 'p1', tool: 'codex', name: 'i18n 文案', status: 'idle', ago: '2 分钟前', cwd: 'locales',
      preview: '› add zh-Hans strings for control center\n• Edited locales/zh-Hans.json (+36 -0)\n• Ran mygo i18n check — ok' },
    { id: 's3', project: 'p1', tool: 'fclaude', name: '同步联调', status: 'connected', ago: '12 分钟前', cwd: 'node-01 · tmux',
      preview: '● 已连接 node-01 · tmux 会话 a1f3…\n> 等待输入' },
  ];

  // Control Center groups (doc §4.4). `s` is a fact-only one-line status.
  const ccGroups = [
    { title: '当前项目', tiles: [
      { id: 'sync', g: '⇄', t: '项目同步', s: '运行中 · 无冲突', cls: 'good', wide: true },
      { id: 'forward', g: '⇢', t: '会话端口', s: '1 个本地转发' },
      { id: 'details', g: 'ⓘ', t: '项目详情', s: 'Go · feature/desktop-workbench' },
    ]},
    { title: '远程', tiles: [
      { id: 'remote', g: '☁', t: '远程会话', s: '2 运行中 · 1 已停止', wide: true },
      { id: 'accounts', g: '◉', t: '账户', s: '3 个账户 · 默认 claude-main' },
      { id: 'credentials', g: '⚿', t: '开发凭据', s: 'Git 身份 · 2 个绑定' },
      { id: 'skills', g: '✦', t: 'Skills', s: '1 个冲突待审阅', cls: 'warn' },
      { id: 'account-import', g: '⤓', t: '配置导入记录', s: '无未决请求' },
      { id: 'runtime-recovery', g: '⟲', t: '运行时恢复', s: '管理员维护' },
    ]},
    { title: '连接与设备', tiles: [
      { id: 'network', g: '⌁', t: '网络 · WireGuard', s: '未检查', wide: true },
      { id: 'device', g: '⌘', t: '设备', s: '本机已登记' },
      { id: 'ego-browser', g: '◎', t: '浏览器连接', s: '1 个绑定 · 已暂停' },
      { id: 'nodes', g: '⬢', t: '节点安装', s: '需要管理员' },
      { id: 'mutagen', g: '⚙', t: '同步运行环境', s: 'daemon 运行中' },
    ]},
    { title: '系统', tiles: [
      { id: 'operations', g: '◷', t: '操作中心', s: '1 个进行中', cls: 'good', wide: true },
      { id: 'diagnostics', g: '✚', t: '环境诊断', s: '上次 10:42 · 全部通过' },
      { id: 'dependencies', g: '⧉', t: '依赖', s: 'mutagen 0.18.1' },
      { id: 'init', g: '✧', t: '初始化向导', s: '已完成' },
      { id: 'capabilities', g: '≡', t: '能力说明', s: '86 条命令' },
      { id: 'settings', g: '⚙', t: '设置', s: '语言 · 工具 · 外观' },
    ]},
  ];

  const context = { home: '~/.agent-remote', server: 'dev.agent-remote.test', device: 'mac-rem-01', account: 'rem@agent-remote' };

  window.Data = { tools, createSectors, projects, olderProjects, sessions, ccGroups, context };
})();
