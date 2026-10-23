# agent-remote-desktop 前端界面与交互重构方案

状态：设计定稿待评审（2026-10-23）。视觉与交互以 [prototype-v4](agent-remote-desktop-design-spec/prototype-v4/index.html) 为可运行基准，色彩与光学材质 1:1 继承 [prototype-v3](agent-remote-desktop-design-spec/prototype-v3.html)，动效遵循 `.claude/skills/apple-design`。本方案只替换 desktop 的**呈现层与操作逻辑**；产品约束、CLI 契约、i18n、`tests/` 布局、安全语义继续以[产品与技术方案](agent-remote-desktop-design.zh-CN.md)为准。

## 1. 已拍板的决策与原因

| # | 决策 | 原因 |
| --- | --- | --- |
| D1 | 三层快捷键改为 **⌥A / ⌥C / ⌥X**（Windows/Linux 为 Alt），新增 **⌥S** 控制中心 | Zen 工作区是终端。「按住 Space」需扣住每个空格等待组合判定，带来输入延迟、按键重复失效，并与中文输入法空格选字冲突，违反 apple-design §1「消除延迟」与 p95<50 ms 预算 |
| D2 | ⌥C 圆环 4 扇区按真实工具：Claude 本地 / Codex 本地 / fclaude 远程 / 高级… | desktop 只支持这三种 Provider；展示做不到的能力违反 Purpose 原则 |
| D3 | 约 25 个管理页收进从底部呼吸条升起的**控制中心** Sheet | Layer 0 去掉侧栏/顶栏后仍需完整 CLI 覆盖；从呼吸条升起保持空间一致 |
| D4 | 主题默认**跟随系统**浅/深，kawaii 为可选；移除 Sakura 立绘 | 存储 ID `daybreak/midnight/sakura` 不变，映射为 light/dark/kawaii，免迁移 |

技术栈说明：v3 规范写的是 `motion/react`，但 desktop 为 mygo 原生 Go（AGENTS.md 强制）。本方案把每条 Web 规则翻译为 mygo 的等价能力（§6、§7），不引入 WebView。

## 2. 现状盘点（已逐项核对代码）

当前布局：顶栏（品牌/搜索/专注/主题/新建）＋侧栏（项目、10 个导航按钮、会话列表、进行中操作入口、立绘）＋内容区（标签栏、1–4 分屏、详情栏）＋状态栏。`a.page` 字符串切换 26 个页面，`ui.Modal` 承载 10 个对话框。

| 区域 | 现有功能 | 新归宿 |
| --- | --- | --- |
| 工作台 | 项目增删选、会话新建/命名/参数、标签拖拽、1–4 分屏、焦点、隐藏、停止、历史会话继续、文件拖放、终端字体 | Layer 0 / 1.1 / 1.2 / 2 |
| 远程 | 远程会话库存（筛选、创建、停止、删除、恢复、attach）、账户（创建/绑定/验证/停用/详情）、默认账户、配置导入、运行时恢复、开发凭据、Skills（目录/启停/状态/冲突/详情）、登录/注销 | 控制中心 · 远程 |
| 项目 | 同步 6 动作＋旧映射恢复、端口转发、项目详情 | 控制中心 · 当前项目 |
| 连接与设备 | WireGuard 配置/检查/状态/隧道、设备、ego-browser（绑定/请求/生命周期/删除）、节点安装、Mutagen 运行环境 | 控制中心 · 连接与设备 |
| 系统 | 操作中心、环境诊断、命令诊断、依赖、本地初始化、初始化向导、能力说明＋通用 CLI 表单、设置（语言/工具/外观/动效/字体） | 控制中心 · 系统 |
| 全局 | 命令面板 `⌘⇧P`、退出确认、关窗后台、托盘 | 保留；命令面板改用 HUD 材质 |

全部业务 worker、`poll*`、CLI 契约、确认/回执语义**不改**；重构只移动入口并统一外观。

## 3. 交互层级与状态机

### 3.1 层级

| 层 | 呼出 | 工作区景深（v3 数值） | 内容 |
| --- | --- | --- | --- |
| 0 Zen | Esc | scale 1 | 全屏 1–4 终端面板＋44 DIP 呼吸条 |
| 1.1 Agents Dock | ⌥A | scale .935 · y +36 · blur 18 · opacity .75 | 顶部降下 332 DIP 毛玻璃抽屉，当前项目全部会话卡片＋「新建」幽灵卡 |
| 1.2 新建圆环 | ⌥C | scale .965 · blur 30 · opacity .65 | 4 扇区＋中心 HUD |
| 2 项目圆环 | ⌥X | 同上 | 8 扇区（12 点「··· 更多」＋7 个最近项目）＋HUD |
| 控制中心 | ⌥S / 点击或上拉呼吸条 | scale .94 · y −18 · blur 14 · opacity .7 ＋ scrim | 底部 Sheet，分组宫格 → 页面推入 |
| 确认 | 由操作触发 | 再退一级：scale −0.02 · blur ≥24 · opacity ≤.6 | 居中玻璃对话框，叠在任意层之上 |

### 3.2 组合键规则（统一、可预测）

- **按住 ⌥＋字母 → peek**：层立即出现。按住期间再按同一字母轮换选择；鼠标移向扇区/卡片即选中（按住时按角度判定，可「甩」向扇区）。
- **松开 ⌥ → 提交**当前选择；没有选择则取消。⌥A 预选上一个使用的 Agent（同 ⌘Tab）。
- **轻点（<250 ms 且未移动）→ sticky**：层常驻，点击/Enter 提交，方向键/Tab/数字键选择，Esc 或点击环外关闭，再按同一组合键关闭。
- **按住时换字母**（⌥A→⌥X）：直接重定向，所有弹簧从当前帧出发并继承速度。
- **⇧ 松开**（⌥C）：在当前面板旁分屏（上限 4）。
- 窗口失焦时 peek 转为 sticky，绝不因失焦误提交。
- 设置中可把修饰键改为 ⌃⌥，供依赖终端 Meta-a/c/x 的用户。

实现依据（R0 已在三平台注入验证，见 desktop `docs/implementation-status.md`）：

- **终端聚焦时由终端 `Options.OnKey` 承接 ⌥A/C/X/S**，返回 true 同时吞掉按键与其文本；窗口 `OnShortcut` 只在焦点不在终端时注册。不能只用窗口快捷键：macOS 会把 `å ç ≈ ß` 送进 Agent，Windows 会进入系统菜单循环并丢失全部后续手势。
- 松开 ⌥ 由 `c.Modifiers()` 观察，三平台延迟 0.2–3.9 ms。
- 状态机为 `internal/chord.Recognizer`（纯逻辑，已有单测），R2 直接接入。
- 单独轻点 Alt 在 Windows/Linux 会显示自动隐藏的菜单栏并吞掉下一个键（平台行为，现有工作台也一样）；不影响组合键，但用户按住 ⌥ 犹豫后松开会进入菜单而非误触发。

### 3.3 状态机

```text
state  = Zen | Agents | Create | Projects | Projects·Search | ControlCenter(page?) ; overlay Confirm?
mode   = peek | sticky
events = chordDown(L) chordRepeat chordUp(dt, moved) select(i) commit(shift) escape dismiss
         dragStart dragMove(y) dragEnd(y, v)
Zen      --chordDown(L)-->            L·peek
L·peek   --chordUp(dt<250,!moved)-->  L·sticky
L·peek   --chordUp-->                 commit(sel) → Zen | Confirm | Projects·Search(sel=更多)
L·any    --chordDown(L')-->           L'·peek   (springs retarget)
L·sticky --escape | dismiss-->        Zen       (CC：先 pop 页面)
any      --dragEnd(project(y,v))-->   nearest(open, closed)
```

视觉由 `target(state)` 纯函数给出，视图每帧向目标做弹簧；状态机不持有动画，所以任何切换都可中断。

## 4. 界面规格

### 4.1 Layer 0 · Zen 工作区

- 窗口边距 14 DIP，面板间距 10 DIP，面板圆角 16，背景用 `--terminal-bg`（`code-bg` 合成到画布后的**不透明色**，不实时模糊，保证终端可读与性能）。kawaii 下面板顶边 3 DIP 三色棱光（v3 `.code-box::before`）。
- 面板标题栏取消，改为右上角悬浮玻璃胶囊：状态点、会话名·工具·位置、隐藏「–」、关闭「×」；终端顶部预留 44 DIP 留白，胶囊不遮挡输出。聚焦面板边框为工具色 55%。
- 呼吸条 44 DIP：`项目 · Agent · [进行中操作] · ⌥A ⌥C ⌥X ⌥S` 与 home indicator。只有存在进行中操作时显示状态点；无动画呼吸（避免 apple-design §14 警告的慢速循环）。
- 空状态：无项目 → 欢迎页（打开项目目录 / 查看环境）；项目无 Agent → 「为 X 选择 Agent」＋三个工具按钮；历史会话 → 未连接卡片＋「继续历史会话」「移除记录」。
- 文件拖放到聚焦面板时边框高亮为工具色；远程面板维持「仅本地拖放」提示语义。

### 4.2 Layer 1.1 · Agents Dock（⌥A）

- 卡片 188 DIP 高、最大 300 宽，间距 22；选中卡上浮 −7 DIP、scale 1.03（v3 数值，改用无回弹弹簧）。
- 卡片内容：工具色名称、**事实状态**胶囊、最近 4 行输出预览、`工具 · 位置 · cwd · 分屏 n/m`、相对时间。
- 状态只用可观测事实：`有新输出`（2 s 内有输出）/ `空闲` / `已连接` / `未连接` / `已退出 · code`。不显示「思考中」「等待审批」，与产品方案 §3 一致。
- 预览：Dock 打开时从 `terminal.Text()` 取末 4 行，去控制字符，仅内存、不持久化；关闭后停止采样。
- 隐藏的会话仍出现在 Dock；选择后为它新建一个标签。超过 4 张卡横向滚动并按卡片吸附。
- 底部抓手 1:1 上推收起：橡皮筋、按速度投影选择开合，松手继承速度（flick 弹簧）。

### 4.3 Layer 1.2 · 新建圆环（⌥C）

| 方位 | 扇区 | 强调色 | 提交行为 |
| --- | --- | --- | --- |
| 12 点 | Claude · 本地 | `--accent-claude` | 立即在项目目录启动 |
| 3 点 | Codex · 本地 | `--accent-codex` | 立即启动 |
| 6 点 | fclaude · 远程 | `--accent-gemini` | 打开新建会话对话框（已选 fclaude）完成审阅后启动，不直接提交 |
| 9 点 | 高级… | `--accent-custom` | 打开完整创建面板：工具、名称、JSON 参数、继续历史、分屏方向 |

- HUD 显示：标签（本地/远程 AGENT）、工具名（工具色）、动作说明、可执行文件版本或登录状态、⇧ 分屏提示。
- 工具缺失：扇区为 `blocked` 填充，HUD 显示「未安装 · 查看安装指引」，提交打开现有指引；需要登录时提交进入控制中心登录页。检测沿用现有缓存，启动前复检。
- 无项目时圆环仍打开，HUD 提示「先选择项目」，提交转到 ⌥X。

### 4.4 Layer 2 · 项目圆环（⌥X）

- 8 扇区几何固定：12 点「··· 更多」，其余为最近项目；不足 7 个显示 40% 透明「空位」。**槽位稳定**：新项目只占空位或替换最久未用的槽位，不按 MRU 每次重排，保证肌肉记忆。
- 扇区：项目名（过长时省略）＋徽章 `语言色点 · 语言 · n Agent`。不用 emoji（三平台字形不一致）。
- HUD：语言 PROJECT 标签、名称、路径（mono 胶囊）、Git 分支胶囊、上次驻留 Agent。
- 元数据只做轻量本地探测：读取 `.git/HEAD`（兼容 worktree `gitdir:` 与 detached），按标记文件判断语言（`go.mod`/`Cargo.toml`/`package.json`/`pyproject.toml`/`Package.swift`/`CMakeLists.txt`）；后台 goroutine 执行、按项目缓存、HEAD mtime 变化才刷新；不调用 `git` 可执行文件，不判定 dirty。
- 「更多」：HUD 原地变为搜索框（sticky 时自动聚焦，支持 IME）与「+ 打开本地文件夹…」；结果列表从 HUD 下方生长，最多 6 行，↑↓/Enter；无匹配时 Enter 按路径打开并走原有目录校验。
- 右键扇区：从最近移除 / 项目同步 / 项目详情。

### 4.5 控制中心（⌥S）

- Sheet 宽 min(1080, 窗口−48)，高 min(74%, 760)，顶圆角 28，`--glass-dock` 材质；工作区后退并叠 `--scrim`。点击/上拉呼吸条 1:1 拉起，抓手下拉关闭。
- 头部：标题、账户胶囊（登录状态，点击进入登录/注销）、搜索（同时搜索页面、命令、项目、会话，取代侧栏导航）、外观分段（跟随系统/浅色/深色/次元）、关闭。
- 宫格四组，宽块承载需要状态的模块：

| 组 | 宫格 |
| --- | --- |
| 当前项目 | **项目同步**、会话端口、项目详情 |
| 远程 | **远程会话**、账户、开发凭据、Skills、默认账户、配置导入记录、运行时恢复 |
| 连接与设备 | **网络 · WireGuard**、设备、浏览器连接、节点安装、同步运行环境 |
| 系统 | **操作中心**、环境诊断、依赖、初始化向导、能力说明、设置 |

- 副标题只写已观察事实；未查询显示「未检查」，进入页面**不自动执行** CLI 查询（沿用现有规则）。平台不支持的入口从宫格隐藏并在能力说明中解释；有权限未安装的显示安装入口。
- 页面在 Sheet 内水平推入/返回（同一路径镜像），Esc 先返回再关闭。原 sidebar 中的「进行中操作」按钮全部并入操作中心宽块计数与呼吸条状态。

### 4.6 统一操作页模板

全部管理页共用一个模板，替代现在各页手写的 `Text` 列表：

1. **上下文条**：home / server / device / project 的 mono 胶囊，始终可见（满足「必须显示实际关联的配置环境」）。
2. **观察面板**：键值网格；完整 ID 截断显示＋复制；查询中显示阶段与「取消查询」。
3. **动作行**：按能力启用；dry-run 类开关紧贴动作并以 warning 色写明副作用（如同步「仍修改 Server 与共享 SQLite」）。
4. **审阅面板**：强调色描边，冻结计划摘要；主按钮写具体动作（「确认暂停」而非「确定」）；危险动作用 danger 按钮。
5. **阶段**：完成（实心 success）、进行中（强调色环）、等待（空心）、**未知（虚线 warning 环）**；无百分比；「停止等待」与「取消远程任务」分开表达。
6. **回执**：outcome、operation_id、method；注明精确回执在 CLI journal。
7. **恢复横幅**：结果未知时置顶「查询原操作」，永不自动重放。

### 4.7 对话框与命令面板

- 确认对话框 440 宽、圆角 24、HUD 材质，scale .96→1 出现；按钮右对齐：取消 / 次要（如「只隐藏」）/ 主动作。仅不可逆动作使用 danger（停止进程、删除、撤销）。退出确认沿用现有会话列表与超时强制逻辑。
- `⌘⇧P` 命令面板改为屏幕上方 1/3 处的 HUD 材质搜索框，结果来自控制中心同一索引。

## 5. 视觉 Token

### 5.1 继承

`prototype-v4/tokens.css` §1 原样复制 v3 三套变量（画布、mesh、三级文字、dock/card/hud 玻璃、扇区、hairline、`--specular-inset`、阴影、代码与语法色、四个 accent、kawaii 装饰透明度）。修改 v3 时同步 v4。

### 5.2 补充（v3 未定义）

| Token | light | dark | kawaii | 用途 |
| --- | --- | --- | --- | --- |
| `--accent` | #0071E3 | #3898FF | #EC4899 | 焦点环、边框、光晕等非文字元素（取自 v3 mesh-1 / kawaii 激活色） |
| `--accent-fill` | #0071E3 | #0A6CD9 | #C81E6F | 主按钮底色，配白字（4.7 / 5.1 / 5.4:1） |
| `--accent-ink` | #0066CC | #3898FF | #C81E6F | 画布上的强调色文字、链接（5.1 / 6.7 / 5.2:1） |
| `--danger` | #D70015 | #FF6961 | #E11D48 | 错误文字与图标 |
| `--danger-fill` | #D70015 | #C62828 | #E11D48 | 破坏性按钮底色，配白字（5.4 / 5.6 / 4.7:1） |
| `--warning` | #B25000 | #FFB340 | #C2410C | 未知结果、dry-run 副作用 |
| `--success` | = accent-codex | 同 | 同 | 阶段完成 |
| `--terminal-bg` | #FCFCFD | #0F0F13 | #FFFDFE | 不透明终端底 |
| `--surface-solid(-raised)` | #FFF / #F2F2F5 | #1C1C1F / #26262B | #FFF4F8 / #FFF | 降低透明度回退 |
| `--scrim` | slate 18% | black 50% | 莓色 14% | 模态背景 |

工具色映射：Claude→accent-claude、Codex→accent-codex、fclaude→accent-gemini、高级→accent-custom。

对比度（WCAG 公式，相对各自画布 `--bg-canvas` 计算）：

| | light | dark | kawaii |
| --- | --- | --- | --- |
| 主文字 | 15.5 | 18.3 | 13.0 |
| 次级文字 | 4.7 | 7.7 | **4.4** |
| 三级文字 | 3.3 | 3.9 | 2.5 |
| warning / danger 文字 | 4.8 / 4.9 | 11.2 / — | 5.0 / — |

规则：三级文字只用于非必需提示且 ≥11 DIP，不承载状态或操作。v3 的强调色直接作白字按钮底时 dark 仅 3.0、kawaii 仅 3.5，因此拆出 `--accent-fill`/`--accent-ink`，`--accent` 只用于非文字。kawaii 次级文字 4.4 略低于 4.5：如评审判定不清，调为 #7E6278（5.1:1），这是唯一允许偏离 v3 的文字色。毛玻璃上的实际对比度随背景变化，R4 需在真实内容上复测；完整 WCAG 合规还需要辅助技术实测和专业无障碍评审。

### 5.3 字体与尺寸

系统字体栈（SF / Segoe UI Variable / PingFang / 微软雅黑 / Noto CJK），终端 SF Mono → JetBrains Mono → Cascadia Mono → Consolas。

| 级别 | 尺寸 / 字重 | 字距 | 行高 |
| --- | --- | --- | --- |
| 欢迎标题 | 38 / 700 | −0.02em | 1.05 |
| Sheet 标题 | 22 / 700 | −0.015em | 1.15 |
| 页面标题 | 20 / 700 | −0.012em | 1.2 |
| HUD 标题 | 18 / 700 | −0.01em | 1.2 |
| 正文 / 卡片名 | 13–14.5 / 500–600 | 0 | 1.5 |
| 胶囊、页脚 | 11–11.5 / 500–600 | +0.01em | 1.4 |
| HUD 标签（大写） | 10 / 700 | +0.12em | 1.2 |
| 终端 | 默认 14，可调 10–32 | 0 | 终端自身 |

圆角：胶囊 999、Sheet 28、对话框 24、卡片 22、宫格 18、面板 16、预览 14、控件 10。间距基于 mygo `Theme.Spacing=4`，尺寸随 `TextScale` 用 `t.Rem` 缩放。

## 6. 动效规格

### 6.1 弹簧 Token（mygo `ui.SpringOptions{Duration, Bounce}`）

| Token | Duration | Bounce | 用途 |
| --- | --- | --- | --- |
| `Smooth` | 400 ms | 0 | 层级景深、圆环出现、重定位 |
| `Snappy` | 280 ms | 0 | 悬停、扇区缩放 1.038、卡片上浮、胶囊 |
| `Press` | 120 ms | 0 | 按下 scale .97 / 扇区 .985，pointer-down 即触发 |
| `Sheet` | 360 ms | 0 | 键盘打开 Dock / 控制中心 |
| `Flick` | 300 ms | 0.2 | **仅**拖拽松手且带速度时 |
| `Page` | 340 ms | 0 | 控制中心推入/返回 |

原型 `physics.js` 用同一参数化（stiffness=(2π/d)²，damping=4π·ratio/d），调好的值可直接搬到 Go。v3 中的 `cubic-bezier(.34,1.56,.64,1)` 卡片回弹按 apple-design §4 取消：没有动量就不过冲。

### 6.2 规则

- **全部可中断**：视觉值用 `AnimateTo`/`Spring` 向目标移动，不用 Keyframes/Timeline 表达层切换；重定向保留速度。
- **从不 scale(0)**：圆环 .92→1、对话框 .96→1、结果列表 .96→1 自 HUD 下沿生长。
- **空间一致**：Dock 自顶降下、原路返回；控制中心自呼吸条升起、原路落下；页面右进右出。
- **只动 transform/opacity**：用 `AnimatePose` 做位移/缩放/淡入（只重绘不重建视图）；卡片、扇区悬停同样用 Pose。
- **拖拽**：Dock/Sheet 用 `Draggable`（Axis Vertical、Bounds、`Snap: ui.Nearest` 基于 `ui.Project` 投影）；工作区景深跟随 `DragOffset()` 插值。
- **主题切换**：220 ms 画布色遮罩淡入→换主题→淡出，避免亮度突变；终端 `SetTheme` 不重建会话。
- **装饰**：kawaii 星芒静止，切到 kawaii 时闪一次；星轨环只在圆环打开时 28 s/圈；窗口不可见时 mygo 不绘帧。
- **反馈**：只在提交、完成、错误时给出 toast（呼吸条上方玻璃胶囊，1.8 s）；不加声音。

### 6.3 无障碍

| 信号 | 处理 |
| --- | --- |
| 减少动态（系统或设置） | 位移/缩放直接到位，透明度 160 ms 线性交叉淡化；星芒、星轨停止；拖拽仍 1:1 跟手、松手即到位（mygo 默认行为） |
| 降低透明度（设置新增；mygo 无系统信号） | 玻璃改 `--surface-solid*`，去掉模糊，scrim 加深代替景深 |
| 增强对比度（`Preferences().HighContrast`） | hairline 改次级文字色、去掉镜面高光、表面实色 |
| 键盘 | 所有层可纯键盘完成；焦点环用 `--accent`；Tab 顺序与视觉一致 |
| 读屏 | 扇区、卡片、宫格均设 `Access` 标签（i18n），状态同时用文字表达 |

## 7. mygo 实现映射

### 7.1 材质与效果

| v3 / Web | mygo |
| --- | --- |
| `backdrop-filter: blur(60px) saturate(220%)` + 半透明底 | `glass.Blur{Radius}` 材质层 + `LinearGradient`/`Background` 着色层（饱和度无直接等价，以着色补偿，视觉验收确认） |
| `--specular-inset` | `InsetShadow(0,1,0.5,0,白)` + `InsetShadow(0,-1,1,0,黑/粉)` |
| `--shadow-elevated` | 两层 `Shadow` |
| 工作区 `filter: blur()` | `Blur(sigma)`；**性能回退**：帧耗时 P95 超 16 ms 或 CPU 渲染时改为不模糊＋scrim |
| 扇区 SVG path | `Draw` 中 `Path`：外弧/内弧各用一段三次贝塞尔近似（86°/43.5° 误差 <0.1 DIP），`FillPath`/`StrokePath` |
| 扇区 drop-shadow | 同一路径偏移填充阴影色后 `Blur`，缓存为位图，主题/尺寸变化时重建 |
| mesh 背景 radial-gradient | 按窗口尺寸与主题生成位图并缓存，`Image` 铺底 |
| 圆环命中 | 指针 → 极坐标：`d<deadR` 不选；`angle=(atan2(dx,−dy)+360)%360`，`i=floor((angle+step/2)%360/step)` |

### 7.2 代码结构（desktop 仓库）

```text
internal/theme/
  tokens.go        三主题完整 token（含 §5.2）＋ Resolve(pref, systemDark)
  motion.go        Spring token、Reduced/ReducedTransparency 策略（替换单一 MotionDuration）
internal/chrome/   与业务无关的原生组件
  glass.go  pill.go  button.go  wheel.go（几何、命中、扇区绘制）  hud.go  sheet.go  stages.go
internal/app/
  layers.go        层状态机（纯逻辑，可测）＋ target(state) 景深
  chord.go         组合键识别：down/repeat/modifiers-released/tap
  zen.go           面板、胶囊、呼吸条、空状态（取代 toolbar/sidebar/statusbar）
  dock.go  create_wheel.go  project_wheel.go
  control_center.go  pages.go（页面注册表，取代 content() 的 if 链）
  operation_page.go  统一模板；现有 *_view.go 改为填充模板
internal/workspace/
  probe.go         Git 分支/语言探测与缓存；Project 增 LastOpened（omitempty）
internal/terminalhost/
  host.go          增 LastOutput 时间戳（原子）
```

`a.page` 字符串 ID 保留为页面注册表的 key，现有持久化与大部分页面逻辑不动。

### 7.3 存储兼容

- `Preferences` 新增 `FollowSystemTheme bool`、`ReduceTransparency bool`、`ChordModifier string`，均 `omitempty`。新安装默认跟随系统；**已有用户**保持当前主题（不静默改变外观）。
- `Theme` 仍只写 `midnight/daybreak/sakura`，旧版本可读。`SidebarWidth`、`ShowDetails` 保留读取但不再使用。
- 存储版本不升；新增字段对旧版本透明（JSON 未知字段忽略），需用回归测试锁定。

## 8. 实施阶段

| 阶段 | 内容 | 通过条件 |
| --- | --- | --- |
| R0 原型验证 | ① 三平台 spike：⌥+字母在终端聚焦时被 app 取得、`Modifiers()` 松开可观察、Windows Alt 不触发菜单栏、macOS 不输入 å；② 工作区 `Blur` 对流式终端的帧耗时；③ 扇区路径绘制与命中 | **2026-10-23 完成（非正式目标主机）**：①② ③ 均通过，前提是采用 `OnKey` 路线；GPU 模糊 p95 ≤13 ms，CPU 渲染 17 ms 超预算，启用 scrim 回退。待补：输入法组字中的组合键人工复测、windows/linux amd64 与真实 X11/Wayland |
| R1 Token 与组件 | tokens.go、motion.go、chrome/*；设置页外观分段与新开关 | **2026-10-23 完成（macOS）**：9 张组件基线（3 主题 × 默认/降低透明度/高对比）＋ Sheet 减弱动效对比；WCAG 单测覆盖全部承诺组合。顺带修复「减少动效」实际仍播放 500 ms 弹簧的既有缺陷。Windows/Linux 基线待目标主机录制 |
| R2 Zen + 三层 | layers/chord/zen/dock/两个圆环；迁移快捷键与命令面板；移除 toolbar/sidebar/details | **2026-10-23 完成（macOS headless）**：Zen、⌥A/⌥C/⌥X/⌥S 与控制中心最小版（宫格仍打开整页）；视图构建 p95 0.032 ms（R1 为 0.045 ms）。fclaude 扇区改为打开现有新建对话框完成审阅（非直接提交）。待补：三平台原生主机验证真实 app、抽屉上推关闭、呼吸条上拉、⌃⌥ 设置 |
| R3 控制中心 | Sheet、宫格、搜索索引、页面注册表；全部现有页面迁入并套用操作页模板 | **2026-10-23 完成（macOS headless）**：注册表收录 25 个原页面＋项目详情，从任何入口打开都推入 Sheet；页头、上下文条、Well 记录卡、Stages、未知结果横幅统一；搜索与命令面板共用同一索引；呼吸条上拉、抽屉上推关闭。上下文条只在远程管理页显示服务器/设备（其他页面显示各自查询到的上下文，不用缓存）。能力门禁、「不自动查询」与 CLI 调用未改。待补：⌃⌥ 设置、命令面板 HUD 材质、景深随拖拽插值 |
| R4 收敛 | 无障碍、性能回退、i18n 长文本（en-XA）、900×600 最小窗口、三平台视觉验收 | **2026-10-23 headless 部分完成**：§10.1 纯键盘、900×600 下三语言（en、zh-Hans、en-XA）的层与页面、§10.2 逐帧中途反向（修复 R3 反向时 Sheet 缺一帧）、§10.3 无 scale(0)、§10.5 新增表面对比度（新增 PillText，次元 Success/Solid 微调）、§10.7 分状态视图构建 P95 ≤0.07 ms、GPU 慢帧回退（BlurBudget）、Linux/Windows arm64 截图基线。待原生主机：真实键盘与输入法组字、BlurBudget 实际触发、输入反馈 P95、读屏器、amd64/X11/Wayland |

每阶段同时提交 en/zh-Hans 文案与 `tests/` 下测试，遵守 `bash scripts/check.sh`。

## 9. 风险与回退

| 风险 | 影响 | 回退 |
| --- | --- | --- |
| 某平台 ⌥+字母被系统/IME 先吞 | 组合键失效 | R0：经 `OnKey` 三平台均可取得；输入法组字中仍待人工复测。保留设置切换 ⌃⌥，`⌘T/⌘O` 等原快捷键保留打开 sticky 层 |
| 修饰键松开事件不可靠 | peek 无法提交 | R0：三平台 ≤3.9 ms 可观察。保留仅 sticky 模式作为兜底 |
| 流式终端下全屏模糊掉帧 | 层切换卡顿 | R0：CPU 渲染实测 17 ms 超预算，**必须**在无 GPU 时降级为 scrim＋缩放 |
| 窗口快捷键与终端 OnKey 同时注册 | 重复触发或文本泄漏 | 按焦点二选一注册；R2 测试锁定「终端聚焦时进程收到 0 字节」 |
| Linux 无 vibrancy | 观感差异 | 全部材质由 glass 插件自绘，与平台无关 |
| 测试大量依赖侧栏按钮文案 | R2/R3 测试失败 | 以页面注册表 ID 打开页面的测试辅助，替换按文案点击侧栏 |
| 900×600 下 490 DIP 圆环与 332 DIP Dock | 拥挤 | 窗口高 <700 时圆环整体 scale .85、Dock 卡片高 160 |

## 10. 验收

1. 三层＋控制中心均可用 peek 与 sticky 两种方式完成，且全程可纯键盘操作。
2. 任意两层之间快速切换、拖拽中途反向，无跳变（逐帧录屏检查）。
3. 所有出现动画不从 scale(0) 开始；进入/退出路径一致。
4. 状态只显示可观测事实；未知结果不自动重试，界面明确提示查询原操作。
5. 减少动态、降低透明度、增强对比度三种设置下截图通过；对比度表复测。
6. 现有全部功能可从新入口到达，`docs/cli-coverage.md` 无回退。
7. 终端输入反馈 p95 <50 ms；10 会话/4 可见面板下层切换无明显卡顿（性能探针＋主机证据）。
8. i18n、`tests/` 目录门禁、`bash scripts/check.sh` 通过。

## 11. 原型使用

直接用浏览器打开 `agent-remote-desktop-design-spec/prototype-v4/index.html`，无网络或构建依赖。

- ⌥A/⌥C/⌥X/⌥S 按住浏览、松开提交，轻点常驻；为方便评审，无修饰键的 A/C/X/S 也会打开 sticky 层（产品无此行为）。
- 左下角「原型 ▸」悬停展开：直接跳转各层、切换主题、模拟减弱动效/降低透明度。
- 控制中心 → 项目同步 → 暂停 → 勾选「模拟回执丢失」可查看未知结果与恢复横幅。
- 原型的浏览器 `backdrop-filter` 模糊比 mygo 实现更廉价，性能结论以 R0 主机测量为准。
