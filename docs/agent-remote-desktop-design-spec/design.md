# Project UI & Interaction Architecture (Agent Space OS)

## 1. Mandatory Design Skills & Golden Reference (必读规范)
在编写或修改任何 UI、动画、快捷键状态机与样式代码前，**必须同时加载并严格遵守以下文件的准则**：
1. **Apple 流体交互与动效法则**：`@.claude/skills/apple-design/SKILL.md`
2. **三态视觉与光学色彩基准**：`@docs/agent-remote-desktop-design-spec/prototype-v3.html`（色值与光学材质的唯一来源）
3. **可运行交互基准**：`@docs/agent-remote-desktop-design-spec/prototype-v4/index.html`（v3 token + 真实 desktop 功能 + 弹簧物理）
4. **完整重构方案**：`@docs/agent-remote-desktop-redesign.zh-CN.md`（与本文冲突时以方案为准）

## 2. Core Interaction Hierarchy (左手黄金三角: ⌥/Alt + A / C / X)
> 2026-10-23 决策：原「按住 Space」改为 ⌥/Alt。Zen 工作区是终端，扣住空格会造成输入延迟、按键重复失效并与中文输入法冲突。按住浏览、松开 ⌥ 提交；轻点（<250 ms）常驻。

- **Layer 0 (Zen Workspace)**: 100% 全屏终端工作区，无传统顶栏/侧边栏，仅底部保留 44 DIP 状态呼吸条。
- **Layer 1.1 (Project Agents Dock — `⌥A`)**: 顶部降下毛玻璃抽屉，展示当前项目所有 Agent 会话卡片（只显示可观测事实状态）；主工作区向后缩放至 `0.935` 并应用深度高斯模糊。
- **Layer 1.2 (Create Agent Radial Menu — `⌥C`)**: 4 扇区按真实工具：Claude 本地 / Codex 本地 / fclaude 远程 / 高级…；悬停扇区时中心 HUD 刷新工具信息，松开 ⌥ 或点击创建（fclaude 先进入审阅确认）。
- **Layer 2 (Project Switcher Radial Menu — `⌥X`)**: 8 扇区（12 点 `··· 更多` + 7 个最近项目，槽位稳定）。悬停项目显示路径、Git 分支、语言与上次驻留 Agent；悬停 `··· 更多` 时 HUD 原地切换为搜索框与打开本地文件夹按钮。
- **控制中心 (`⌥S` / 点击或上拉呼吸条)**: 从底部升起的 Sheet，承载全部管理页（同步、远程、网络、设备、诊断、设置等）。

## 3. How to Merge Both References (融合执行铁律)
- **严禁 `scale(0)` 弹出**：圆环从 `scale(0.92)` + `opacity: 0` 以无回弹弹簧展开；对话框 0.96→1。
- **可打断与可逆动效**：层之间快速切换或中途松开时，从当前帧平滑逆转或重定向。desktop 为 mygo 原生 Go：使用 `ui.SpringOptions{Duration, Bounce}` / `AnimatePose` / `Draggable`（与原型 `physics.js` 参数一致），不使用 `motion/react`。
- **回弹只给动量**：仅拖拽松手带速度时使用 bounce 0.2；键盘打开、悬停、卡片上浮一律 bounce 0。
- **光学材质与三态主题**：严格保留 v3 的 `light` (雪花石膏白)、`dark` (深空钛黑)、`kawaii` (初樱虹彩亚克力) 三套 CSS 变量、1px 镜面内高光 (`--specular-inset`) 以及极坐标环形扇区公式；v3 未定义的 token（accent-fill/ink、danger、warning、terminal-bg、实色回退）见 v4 `tokens.css` §2。默认跟随系统浅/深，kawaii 可选。
