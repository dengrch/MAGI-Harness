const iconPaths = {
  send: '<path d="M12 20V4m-7 7 7-7 7 7"/>',
  stop: '<rect x="5" y="5" width="14" height="14" rx="3" fill="currentColor" stroke="none"/>',
  play: '<path d="m8 5 11 7-11 7Z"/>',
  queue: '<path d="M4 6h16M4 12h10M4 18h10m5-6v8m-3-3 3 3 3-3"/>',
  insert: '<path d="M4 5h16M12 21V10m-5 5 5-5 5 5"/>',
  compress: '<path d="m4 4 6 6m-6 0h6V4m10 16-6-6m6 0h-6v6"/>',
  folder:
    '<path d="M20 20a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.9a2 2 0 0 1-1.69-.9L9.6 3.9A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2Z"></path>',
  message:
    '<path d="M22 17a2 2 0 0 1-2 2H6.828a2 2 0 0 0-1.414.586l-2.202 2.202A.71.71 0 0 1 2 21.286V5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2z"></path>',
  terminal: '<path d="M12 19h8"></path><path d="m4 17 6-6-6-6"></path>',
  thought:
    '<path d="M12 18V5"></path><path d="M15 13a4.17 4.17 0 0 1-3-4 4.17 4.17 0 0 1-3 4"></path><path d="M17.598 6.5A3 3 0 1 0 12 5a3 3 0 1 0-5.598 1.5"></path><path d="M17.997 5.125a4 4 0 0 1 2.526 5.77"></path><path d="M18 18a4 4 0 0 0 2-7.464"></path><path d="M19.967 17.483A4 4 0 1 1 12 18a4 4 0 1 1-7.967-.517"></path><path d="M6 18a4 4 0 0 1-2-7.464"></path><path d="M6.003 5.125a4 4 0 0 0-2.526 5.77"></path>',
  user: '<path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle>',
  switch:
    '<path d="M8 3 4 7l4 4"></path><path d="M4 7h16"></path><path d="m16 21 4-4-4-4"></path><path d="M20 17H4"></path>',
  close: '<path d="M18 6 6 18"></path><path d="m6 6 12 12"></path>',
  right: '<path d="m9 18 6-6-6-6"></path>',
  down: '<path d="m6 9 6 6 6-6"></path>',
  plus: '<path d="M5 12h14"></path><path d="M12 5v14"></path>',
  settings:
    '<path d="M9.671 4.136a2.34 2.34 0 0 1 4.659 0 2.34 2.34 0 0 0 3.319 1.915 2.34 2.34 0 0 1 2.33 4.033 2.34 2.34 0 0 0 0 3.831 2.34 2.34 0 0 1-2.33 4.033 2.34 2.34 0 0 0-3.319 1.915 2.34 2.34 0 0 1-4.659 0 2.34 2.34 0 0 0-3.32-1.915 2.34 2.34 0 0 1-2.33-4.033 2.34 2.34 0 0 0 0-3.831A2.34 2.34 0 0 1 6.35 6.051a2.34 2.34 0 0 0 3.319-1.915"></path><circle cx="12" cy="12" r="3"></circle>',
  wrench:
    '<path d="M14.7 6.3a4 4 0 0 0-5-5l2.1 2.1-2.4 2.4-2.1-2.1a4 4 0 0 0 5 5l7.4 7.4a2.1 2.1 0 0 1-3 3l-7.4-7.4"></path>',
  sliders:
    '<path d="M10 5H3"></path><path d="M12 19H3"></path><path d="M14 3v4"></path><path d="M16 17v4"></path><path d="M21 12h-9"></path><path d="M21 19h-5"></path><path d="M21 5h-7"></path><path d="M8 10v4"></path><path d="M8 12H3"></path>',
  cpu: '<path d="M12 20v2"></path><path d="M12 2v2"></path><path d="M17 20v2"></path><path d="M17 2v2"></path><path d="M2 12h2"></path><path d="M2 17h2"></path><path d="M2 7h2"></path><path d="M20 12h2"></path><path d="M20 17h2"></path><path d="M20 7h2"></path><path d="M7 20v2"></path><path d="M7 2v2"></path><rect x="4" y="4" width="16" height="16" rx="2"></rect><rect x="8" y="8" width="8" height="8" rx="1"></rect>',
  activity:
    '<path d="M22 12h-2.48a2 2 0 0 0-1.93 1.46l-2.35 8.36a.25.25 0 0 1-.48 0L9.24 2.18a.25.25 0 0 0-.48 0l-2.35 8.36A2 2 0 0 1 4.49 12H2"></path>',
  panel:
    '<rect width="18" height="18" x="3" y="3" rx="2"></rect><path d="M9 3v18"></path>',
  copy: '<rect x="9" y="9" width="11" height="11" rx="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>',
};
function icon(name) {
  return `<svg class="ui-icon" data-icon="${name}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${iconPaths[name] || iconPaths.message}</svg>`;
}
const $ = (id) => document.getElementById(id);
let sid = null,
  events = [],
  running = false,
  operation = null,
  page = 'launch',
  config = {},
  prefs = {},
  polling = false;
let pendingAttachments = [],
  editSeq = null,
  traceSelection = null,
  foldTurns = false,
  foldCalls = false,
  timelineMode = 'sequence',
  timelineViewport = null;
let traceRange = null,
  traceRecordsCache = [],
  lineSelection = false;
const selectedTraceIds = new Set();
const collapsedTurnKeys = new Set();
const collapsedWorkspaces = new Set();
const expandedWorkspaces = new Set();
const drafts = new Map();
let sessionsCache = [],
  sessionGeneration = 0,
  launching = false,
  sending = false;
let noticeTimer,
  settingsGeneration = 0,
  loadedInstructionsWorkspace = null,
  instructionsGeneration = 0;
let inspectorKey = null;
let modelPopoverGeneration = 0;
function saveDraft() {
  if (sid)
    drafts.set(sid, {
      text: $('input').value,
      attachments: [...pendingAttachments],
    });
}
function resizeInput(el) {
  el.style.height = 'auto';
  el.style.height = `${Math.min(el.scrollHeight, 200)}px`;
}
function isNearBottom(el) {
  return el.scrollHeight - el.scrollTop - el.clientHeight < 80;
}
function streamingMessage() {
  const request = requests().at(-1);
  if (!request || responseFor(request)) return null;
  if (events.some((e) =>
    (e.kind === 'request_error' && e.data.request_seq === request.seq) ||
    (e.kind === 'turn_end' && e.turn === request.turn && e.seq > request.seq)
  )) return null;
  const deltas = events.filter(
    (e) => e.kind === 'delta' && e.data.request_seq === request.seq,
  );
  return {
    content: deltas
      .filter((e) => e.data.field === 'content')
      .map((e) => e.data.text || '')
      .join(''),
    reasoning: deltas
      .filter((e) => e.data.field === 'reasoning_content')
      .map((e) => e.data.text || '')
      .join(''),
  };
}
// Escape first; support a deliberately small, HTML-free Markdown subset.
function renderMarkdown(text) {
  return String(text || '')
    .split(/(```[^\n]*\n[\s\S]*?```)/g)
    .map((part) => {
      if (part.startsWith('```') && part.endsWith('```')) {
        const line = part.indexOf('\n');
        return `<pre class="code-block"><div>${esc(part.slice(3, line) || 'code')}</div><code>${esc(part.slice(line + 1, -3))}</code></pre>`;
      }
      return esc(part)
        .replace(/`([^`\n]+)`/g, '<code>$1</code>')
        .replace(/\*\*([^*\n]+)\*\*/g, '<strong>$1</strong>')
        .replace(/^### (.+)$/gm, '<h4>$1</h4>')
        .replace(/^## (.+)$/gm, '<h3>$1</h3>')
        .replace(/^# (.+)$/gm, '<h2>$1</h2>');
    })
    .join('');
}
const esc = (v) =>
  String(v ?? '').replace(
    /[&<>"']/g,
    (c) =>
      ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[
        c
      ],
  );
const json = (v) => JSON.stringify(v, null, 2);
function parseToolArguments(value) {
  if (typeof value !== 'string') return value || {};
  try {
    return JSON.parse(value);
  } catch {
    return value;
  }
}
function toolArgumentPreview(value) {
  const parsed = parseToolArguments(value);
  if (typeof parsed === 'string') return parsed.split('\n')[0].slice(0, 100);
  const preferred =
    parsed.file_path ||
    parsed.path ||
    parsed.command ||
    parsed.query ||
    parsed.expression ||
    parsed.url;
  if (preferred != null) return String(preferred).split('\n')[0].slice(0, 100);
  return Object.keys(parsed).slice(0, 4).join(' · ');
}
const prettyToolArguments = (value) => {
  const parsed = parseToolArguments(value);
  return typeof parsed === 'string' ? parsed : json(parsed);
};
const fmt = (n) => (n == null ? '—' : Number(n).toLocaleString());
const compact = (n) =>
  n < 1000
    ? String(Math.round(n))
    : n < 1e6
      ? `${Math.round(n / 100) / 10}K`
      : `${Math.round(n / 1e5) / 10}M`;
const duration = (ms) =>
  ms < 60000
    ? `${Math.round(ms / 100) / 10}s`
    : `${Math.floor(ms / 60000)}m${Math.round(ms / 1000) % 60}s`;
const translations = {
  zh: {
    newChat: '新对话',
    settings: '设置',
    chat: '对话',
    trajectory: '轨迹',
    startWork: '开始新任务',
    startHint: '描述目标，MAGI 会在所选工作区中完成它。',
    workspace: '工作区',
    contextMode: '上下文模式',
    permissions: '文件权限',
    startChat: '开始对话',
    traceline: 'Traceline',
    timeline: '时间线',
    turns: '轮次',
    tools: '工具',
    zoomHint: '横向滚动平移 · 滚轮缩放 · 单击查看 · 拖动选择',
    clearSelection: '清除选择',
    collapseSidebar: '收起侧栏',
    expandSidebar: '展开侧栏',
    chooseWorkspace: '选择工作区',
    searchSessions: '搜索对话或工作区…',
    selectWorkspaceChip: '选择一个工作区',
    firstMessage: '第一条消息',
    absoluteWorkspace: '工作区绝对路径',
    recentWorkspace: '选择最近工作区',
    permissionAsk: '批准写入',
    permissionReadOnly: '只读',
    permissionAllowEdits: '允许写入',
    transcript: '对话记录',
    jumpLatest: '回到最新',
    message: '消息',
    addFile: '添加文件',
    compactContext: '压缩旧上下文',
    compactContextTitle: '压缩旧上下文 · 调用模型，保留原文引用',
    stopRun: '停止运行',
    resumeRun: '继续运行',
    sendMessage: '发送消息',
    traceProjection: '轨迹投影方式',
    searchTrace: '搜索执行过程…',
    selectModel: '选择模型',
    closeModelSelect: '关闭模型选择',
    configureModel: '配置模型连接',
    settingsSubtitle: '语言、外观与模型连接',
    close: '关闭',
    general: '通用',
    models: '模型',
    context: '上下文',
    generalDescription: '语言和外观会立即应用到 WebUI。',
    language: '语言',
    appearance: '界面外观',
    systemTheme: '跟随系统',
    lightTheme: '浅色',
    darkTheme: '深色',
    save: '保存',
    modelDescription: '下一次 Agent 运行使用的 Provider 与模型。',
    timeoutSeconds: '请求超时 · 秒',
    discoverModels: '发现模型',
    keepUnchanged: '保持不变',
    applyModel: '应用模型',
    contextDescription: '新会话默认值、全局 Stable Prompt 与工作区 MAGI.md。',
    fourZoneDescription: 'Stable / Stubs / Cold / Hot，显式 SWITCH 与原文恢复。',
    fullHistoryDescription: '保留所有消息，不执行阶段迁移。',
    contextBudget: '上下文预算',
    turnsPerStage: '每个 Stage 的轮数',
    basePrompt: '基础 Stable Prompt',
    workspacePrompt: '工作区专属提示词',
    refreshOverview: '刷新总览',
    workspacePathPlaceholder: '工作区绝对路径',
    magiContentPlaceholder: 'MAGI.md 内容',
    workspaceDialogDescription: '选择最近使用的文件夹，或输入本机目录的绝对路径。',
    workingDirectory: '工作目录',
    workspaceStartNote: '将在此目录开始新对话',
    useWorkspace: '使用此工作区',
    fullRecord: '完整记录',
    requestFailed: '请求失败',
    chooseOption: '选择选项',
    copy: '复制',
    inspect: '查看',
    toolResult: '工具结果',
    reasoning: '推理',
    reasoningProcess: '模型思考过程',
    thinking: '正在思考',
    cancel: '取消',
    approvalRequired: '需要批准',
    reject: '拒绝',
    allowOnce: '允许一次',
    viewTrace: '查看轨迹',
    runningDetail: '正在处理 · 可追加指令，或停止运行',
    running: '运行中',
    runPaused: '运行已暂停',
    resumeFromSaved: '可从保存位置继续',
    chatEmptyTitle: '可以开始了',
    chatEmptyBody: '在当前工作区中提问、修改文件或执行任务。',
    compressingPlaceholder: '正在压缩上下文…',
    followupPlaceholder: '追加指令，在所选边界生效…',
    checkpoint: '检查点',
    afterTurn: '本轮之后',
    nextRun: '下次运行',
    cancelQueued: '取消排队指令',
    newInWorkspace: '在此工作区新建对话',
    collapseMore: '收起更多',
    expandRemaining: '展开其余 {count} 条',
    noMatchingChats: '没有匹配的对话',
    noWorkspaces: '还没有工作区',
    tryAnotherSearch: '试试其他标题或路径',
    startFirstWork: '点击 + 选择文件夹，开始第一段工作。',
    noRecentWorkspace: '尚无最近工作区，请输入目录路径。',
    overview: '概览',
    output: '输出',
    rawRecord: '原始记录',
    viewFullSource: '查看完整原文 ↗',
    completed: '完成',
    waitingResponse: '等待响应',
    elapsed: '耗时',
    cacheRead: '缓存读取',
    fourZoneContext: '四区上下文',
    emptyZone: '此区为空',
    noTextOutput: '尚无文本输出',
    returned: '已返回',
    waitingReturn: '等待返回',
    arguments: '参数',
    result: '返回',
    noToolCalls: '本 Step 没有工具调用',
    callArguments: '调用参数',
    toolReturn: '工具返回',
    waitingToolReturn: '等待工具返回',
    definition: '定义',
    noTools: '未提供工具',
    noSystemMessage: '未提供系统消息',
    closeDetails: '关闭详情',
    contextAndCache: '上下文与缓存',
    eventContentTime: '事件 · 内容 · 时间',
    noTraceTitle: '尚无执行记录',
    noTraceBody: '发送消息后，按 Turn 与 Step 查看执行过程。',
    loadingModels: '正在读取可用模型…',
    current: '当前',
    noModels: '没有发现可用模型',
    applying: '正在应用…',
    demoBindingNote: '离线演示不产生真实用量。',
    remoteBindingNote: 'Host 与密钥仅保存在本机；当前运行中的 Turn 不受设置变更影响。',
    keySaved: '已保存；留空保持',
    keyMissing: '未保存',
    unavailableDirectory: '目录不可用',
    noMagiFile: '尚无 MAGI.md',
    loadingWorkspacePrompt: '正在读取工作区提示词…',
    connecting: '连接中…',
    selectedModel: '已选择 {model}',
    discoveredModels: '已发现 {count} 个模型',
    applied: '已应用',
    saved: '已保存',
    contextSaved: '已保存，新会话生效',
    user: '用户',
    assistant: '助手',
    system: '系统',
    switch: '切换',
    approval: '批准',
    error: '错误',
    input: '输入',
    model: '模型',
    toolLane: '工具',
    startMarker: '开始标记',
    newChatChip: '新对话',
    compactionStatus: '压缩中 · 原文保留',
    activeRunStatus: '运行中 · 插入不会撤销已执行操作',
    pausedRunStatus: '已暂停 · 追加后需继续运行',
    contextBudgetTrigger: '上下文预算触发',
    turnThresholdTrigger: '轮次阈值触发',
    retainedHot: '保留在 Hot',
    rounds: '轮',
    blocks: '块',
    queuedAttachmentsUnsupported: '追加指令暂不支持附件，请先移除附件。',
    fileTooLarge: '{name} 超过 2 MB',
    loadWorkspaceBeforeSave: '请先读取此工作区的 MAGI.md，再保存修改。',
    turnCount: '{count} 轮',
    stepCount: '{count} 步',
    toolCall: '工具调用',
    average: '平均',
    cacheHit: '缓存命中',
    tokenInput: '输入',
    tokenOutput: '输出',
    cached: '缓存',
  },
  en: {
    newChat: 'New chat',
    settings: 'Settings',
    chat: 'Chat',
    trajectory: 'Trajectory',
    startWork: 'Start a new task',
    startHint: 'Describe the outcome. MAGI will work in the selected workspace.',
    workspace: 'Workspace',
    contextMode: 'Context mode',
    permissions: 'File access',
    startChat: 'Start chat',
    traceline: 'Traceline',
    timeline: 'Timeline',
    turns: 'Turns',
    tools: 'Tools',
    zoomHint: 'Horizontal scroll to pan · wheel to zoom · click to inspect · drag to select',
    clearSelection: 'Clear selection',
    collapseSidebar: 'Collapse sidebar',
    expandSidebar: 'Expand sidebar',
    chooseWorkspace: 'Choose workspace',
    searchSessions: 'Search chats or workspaces…',
    selectWorkspaceChip: 'Choose a workspace',
    firstMessage: 'First message',
    absoluteWorkspace: 'Absolute workspace path',
    recentWorkspace: 'Choose a recent workspace',
    permissionAsk: 'Ask before edits',
    permissionReadOnly: 'Read only',
    permissionAllowEdits: 'Allow edits',
    transcript: 'Conversation',
    jumpLatest: 'Jump to latest',
    message: 'Message',
    addFile: 'Add file',
    compactContext: 'Compact old context',
    compactContextTitle: 'Compact old context · calls the model and keeps source references',
    stopRun: 'Stop run',
    resumeRun: 'Resume run',
    sendMessage: 'Send message',
    traceProjection: 'Trace projection',
    searchTrace: 'Search execution…',
    selectModel: 'Select model',
    closeModelSelect: 'Close model selector',
    configureModel: 'Configure model connection',
    settingsSubtitle: 'Language, appearance, and model connections',
    close: 'Close',
    general: 'General',
    models: 'Models',
    context: 'Context',
    generalDescription: 'Language and appearance apply immediately to the WebUI.',
    language: 'Language',
    appearance: 'Appearance',
    systemTheme: 'System',
    lightTheme: 'Light',
    darkTheme: 'Dark',
    save: 'Save',
    modelDescription: 'Provider and model used for the next agent run.',
    timeoutSeconds: 'Request timeout · seconds',
    discoverModels: 'Discover models',
    keepUnchanged: 'Leave unchanged',
    applyModel: 'Apply model',
    contextDescription: 'Defaults for new sessions, the global Stable Prompt, and workspace MAGI.md.',
    fourZoneDescription: 'Stable / Stubs / Cold / Hot with explicit SWITCH and source recovery.',
    fullHistoryDescription: 'Keep every message without stage transitions.',
    contextBudget: 'Context budget',
    turnsPerStage: 'Turns per Stage',
    basePrompt: 'Base Stable Prompt',
    workspacePrompt: 'Workspace prompt',
    refreshOverview: 'Refresh overview',
    workspacePathPlaceholder: 'Absolute workspace path',
    magiContentPlaceholder: 'MAGI.md content',
    workspaceDialogDescription: 'Choose a recent folder or enter an absolute local path.',
    workingDirectory: 'Working directory',
    workspaceStartNote: 'A new chat will start in this directory',
    useWorkspace: 'Use this workspace',
    fullRecord: 'Full record',
    requestFailed: 'Request failed',
    chooseOption: 'Choose an option',
    copy: 'Copy',
    inspect: 'Inspect',
    toolResult: 'Tool result',
    reasoning: 'Reasoning',
    reasoningProcess: 'Model reasoning',
    thinking: 'Thinking',
    cancel: 'Cancel',
    approvalRequired: 'Approval required',
    reject: 'Reject',
    allowOnce: 'Allow once',
    viewTrace: 'View trace',
    runningDetail: 'Working · add instructions or stop the run',
    running: 'Running',
    runPaused: 'Run paused',
    resumeFromSaved: 'Resume from the saved position',
    chatEmptyTitle: 'Ready when you are',
    chatEmptyBody: 'Ask a question, edit files, or run a task in this workspace.',
    compressingPlaceholder: 'Compacting context…',
    followupPlaceholder: 'Add an instruction for the selected boundary…',
    checkpoint: 'Checkpoint',
    afterTurn: 'After this turn',
    nextRun: 'Next run',
    cancelQueued: 'Cancel queued instruction',
    newInWorkspace: 'New chat in this workspace',
    collapseMore: 'Show less',
    expandRemaining: 'Show {count} more',
    noMatchingChats: 'No matching chats',
    noWorkspaces: 'No workspaces yet',
    tryAnotherSearch: 'Try another title or path',
    startFirstWork: 'Choose a folder with + to begin.',
    noRecentWorkspace: 'No recent workspaces. Enter a directory path.',
    overview: 'Overview',
    output: 'Output',
    rawRecord: 'Raw record',
    viewFullSource: 'View full source ↗',
    completed: 'Completed',
    waitingResponse: 'Waiting for response',
    elapsed: 'Elapsed',
    cacheRead: 'Cache read',
    fourZoneContext: 'Four-zone context',
    emptyZone: 'This zone is empty',
    noTextOutput: 'No text output yet',
    returned: 'Returned',
    waitingReturn: 'Waiting',
    arguments: 'Arguments',
    result: 'Result',
    noToolCalls: 'No tool calls in this Step',
    callArguments: 'Call arguments',
    toolReturn: 'Tool result',
    waitingToolReturn: 'Waiting for tool result',
    definition: 'Definition',
    noTools: 'No tools provided',
    noSystemMessage: 'No system message provided',
    closeDetails: 'Close details',
    contextAndCache: 'Context and cache',
    eventContentTime: 'Event · Content · Time',
    noTraceTitle: 'No execution records',
    noTraceBody: 'Send a message, then inspect execution by Turn and Step.',
    loadingModels: 'Loading available models…',
    current: 'Current',
    noModels: 'No models found',
    applying: 'Applying…',
    demoBindingNote: 'Offline demo does not produce real usage.',
    remoteBindingNote: 'Host and key stay on this device. Settings do not affect the current Turn.',
    keySaved: 'Saved; leave blank to keep',
    keyMissing: 'Not saved',
    unavailableDirectory: 'Directory unavailable',
    noMagiFile: 'No MAGI.md',
    loadingWorkspacePrompt: 'Loading workspace prompt…',
    connecting: 'Connecting…',
    selectedModel: 'Selected {model}',
    discoveredModels: 'Found {count} models',
    applied: 'Applied',
    saved: 'Saved',
    contextSaved: 'Saved; applies to new sessions',
    user: 'User',
    assistant: 'Assistant',
    system: 'System',
    switch: 'Switch',
    approval: 'Approval',
    error: 'Error',
    input: 'Input',
    model: 'Model',
    toolLane: 'Tools',
    startMarker: 'Start marker',
    newChatChip: 'New chat',
    compactionStatus: 'Compacting · source retained',
    activeRunStatus: 'Running · inserted instructions do not undo completed actions',
    pausedRunStatus: 'Paused · resume after adding an instruction',
    contextBudgetTrigger: 'Triggered by context budget',
    turnThresholdTrigger: 'Triggered by turn threshold',
    retainedHot: 'Retained in Hot',
    rounds: 'turns',
    blocks: 'blocks',
    queuedAttachmentsUnsupported: 'Queued instructions do not support attachments yet. Remove the attachment first.',
    fileTooLarge: '{name} is larger than 2 MB',
    loadWorkspaceBeforeSave: 'Load this workspace MAGI.md before saving changes.',
    turnCount: '{count} turns',
    stepCount: '{count} steps',
    toolCall: 'Tool call',
    average: 'avg',
    cacheHit: 'Cache hit',
    tokenInput: 'Input',
    tokenOutput: 'Output',
    cached: 'cached',
  },
};
let currentLanguage = 'zh';
function tr(key, values = {}) {
  const table = translations[currentLanguage] || translations.zh;
  let value = table[key] || translations.zh[key] || key;
  for (const [name, replacement] of Object.entries(values))
    value = value.replaceAll(`{${name}}`, String(replacement));
  return value;
}

async function api(path, method = 'GET', body) {
  const response = await fetch('/api' + path, {
    method,
    headers: body ? { 'Content-Type': 'application/json' } : {},
    body: body ? JSON.stringify(body) : undefined,
  });
  const data = await response.json();
  if (!response.ok)
    throw new Error(typeof data.detail === 'string' ? data.detail : tr('requestFailed'));
  return data;
}
function notice(text = '') {
  clearTimeout(noticeTimer);
  $('notice').textContent = text;
  $('notice').hidden = !text;
  if (text)
    noticeTimer = setTimeout(() => {
      $('notice').hidden = true;
    }, 7000);
}
function applyTheme(theme) {
  const dark =
    theme === 'dark' ||
    (theme === 'system' && matchMedia('(prefers-color-scheme: dark)').matches);
  document.documentElement.classList.toggle('dark', dark);
}
function applyLanguage(language) {
  currentLanguage = language === 'en' ? 'en' : 'zh';
  document.documentElement.lang = language === 'en' ? 'en' : 'zh-CN';
  const table = translations[language] || translations.zh;
  document.querySelectorAll('[data-i18n]').forEach((el) => {
    if (table[el.dataset.i18n]) el.textContent = table[el.dataset.i18n];
  });
  document.querySelectorAll('[data-i18n-placeholder]').forEach((el) => {
    el.placeholder = tr(el.dataset.i18nPlaceholder);
  });
  document.querySelectorAll('[data-i18n-label]').forEach((el) => {
    el.setAttribute('aria-label', tr(el.dataset.i18nLabel));
  });
  document.querySelectorAll('[data-i18n-title]').forEach((el) => {
    el.title = tr(el.dataset.i18nTitle);
  });
  const input = $('input');
  if (input) input.placeholder = language === 'en' ? 'Send a message…' : '发送消息…';
  const launchInput = $('launch-input');
  if (launchInput)
    launchInput.placeholder =
      language === 'en' ? 'Describe what you want to accomplish…' : '描述你想完成的工作…';
  const hint = document.querySelector('[data-i18n="zoomHint"]');
  if (hint) hint.textContent = table.zoomHint;
  syncCustomSelects();
  if (sessionsCache.length) renderSessionTree();
  if (sid) renderChat();
  if (page === 'trace') renderTrace();
}
function syncCustomSelect(select) {
  const root = select.nextElementSibling;
  if (!root?.classList.contains('custom-select')) return;
  const selected = select.options[select.selectedIndex];
  root.querySelector('.custom-select-value').textContent =
    selected?.textContent || '';
  const trigger = root.querySelector('.custom-select-trigger');
  trigger.disabled = select.disabled;
  trigger.setAttribute(
    'aria-label',
    select.getAttribute('aria-label') || tr('chooseOption'),
  );
  root.querySelectorAll('[role="option"]').forEach((option) => {
    const source = [...select.options].find(
      (item) => item.value === option.dataset.value,
    );
    const label = option.querySelector('span:first-child');
    if (source && label) label.textContent = source.textContent;
    const active = option.dataset.value === select.value;
    option.classList.toggle('selected', active);
    option.setAttribute('aria-selected', String(active));
  });
}
function syncCustomSelects() {
  document
    .querySelectorAll('select.custom-select-native')
    .forEach(syncCustomSelect);
}
function closeCustomSelects(except) {
  document.querySelectorAll('.custom-select').forEach((root) => {
    if (root === except) return;
    root.classList.remove('open');
    root.querySelector('.custom-select-menu').hidden = true;
    root
      .querySelector('.custom-select-trigger')
      .setAttribute('aria-expanded', 'false');
  });
}
function enhanceCustomSelect(select) {
  if (select.hidden || select.classList.contains('custom-select-native')) return;
  select.classList.add('custom-select-native');
  select.tabIndex = -1;
  select.setAttribute('aria-hidden', 'true');
  const root = document.createElement('div');
  root.className = 'custom-select';
  root.innerHTML = `<button type="button" class="custom-select-trigger" aria-haspopup="listbox" aria-expanded="false"><span class="custom-select-value"></span>${icon('down')}</button><div class="custom-select-menu" role="listbox" hidden>${[...select.options]
    .map(
      (option) =>
        `<button type="button" role="option" data-value="${esc(option.value)}"><span>${esc(option.textContent)}</span><span class="custom-select-check">✓</span></button>`,
    )
    .join('')}</div>`;
  select.insertAdjacentElement('afterend', root);
  const trigger = root.querySelector('.custom-select-trigger');
  const menu = root.querySelector('.custom-select-menu');
  trigger.setAttribute(
    'aria-label',
    select.getAttribute('aria-label') || tr('chooseOption'),
  );
  trigger.onclick = () => {
    syncCustomSelect(select);
    const opening = menu.hidden;
    closeCustomSelects(opening ? root : null);
    root.classList.toggle('open', opening);
    menu.hidden = !opening;
    trigger.setAttribute('aria-expanded', String(opening));
    if (opening)
      setTimeout(() => menu.querySelector('.selected')?.focus(), 0);
  };
  menu.onclick = (event) => {
    const option = event.target.closest('[role="option"]');
    if (!option) return;
    select.value = option.dataset.value;
    select.dispatchEvent(new Event('change', { bubbles: true }));
    syncCustomSelect(select);
    closeCustomSelects();
    trigger.focus();
  };
  select.addEventListener('change', () => syncCustomSelect(select));
  syncCustomSelect(select);
}
function enhanceCustomSelects() {
  document.querySelectorAll('select').forEach(enhanceCustomSelect);
}
function setPage(next) {
  page = next;
  $('launch').hidden = next !== 'launch';
  $('chat').hidden = next !== 'chat';
  $('trace').hidden = next !== 'trace';
  $('chat-tab').classList.toggle('active', next === 'chat');
  $('trace-tab').classList.toggle('active', next === 'trace');
  if (next === 'trace') renderTrace();
}
function effectiveMessages() {
  const edits = new Map();
  for (const event of events)
    if (event.kind === 'message_edit')
      edits.set(event.data.target_seq, event.data.content);
  return events
    .filter((e) => e.kind === 'message')
    .map((e) => ({
      ...e,
      data: { ...e.data, content: edits.get(e.seq) ?? e.data.content },
      edited: edits.has(e.seq),
    }));
}
function requests() {
  return events.filter((e) => e.kind === 'request');
}
function responseFor(req) {
  return events.find(
    (e) => e.kind === 'response' && e.data.request_seq === req.seq,
  );
}
function sessionStats() {
  const reqs = requests(),
    responses = events.filter((e) => e.kind === 'response');
  const turns = new Set(reqs.map((e) => e.turn)).size;
  const llmMs = responses.reduce((n, e) => n + (e.data.latency_ms || 0), 0);
  let toolMs = 0;
  for (const start of events.filter((e) => e.kind === 'tool_start')) {
    const id = start.data.id;
    const end = events.find(
      (e) =>
        e.kind === 'message' &&
        e.data.role === 'tool' &&
        e.data.tool_call_id === id,
    );
    if (end) toolMs += Math.max(0, (end.created - start.created) * 1000);
  }
  const ttfts = reqs.flatMap((req) => {
    const delta = events.find(
      (e) =>
        e.kind === 'delta' && e.data.request_seq === req.seq && e.data.text,
    );
    return delta ? [(delta.created - req.created) * 1000] : [];
  });
  const usage = responses.map((e) => e.data.usage || {});
  const input = usage.reduce((n, u) => n + (u.input_tokens || 0), 0),
    output = usage.reduce((n, u) => n + (u.output_tokens || 0), 0),
    cache = usage.reduce((n, u) => n + (u.cache_read_tokens || 0), 0);
  const decodeMs = Math.max(0, llmMs - ttfts.reduce((a, b) => a + b, 0));
  return {
    turns,
    steps: reqs.length,
    llmMs,
    toolMs,
    ttft: ttfts.length ? ttfts.reduce((a, b) => a + b, 0) / ttfts.length : null,
    tps: decodeMs && output ? output / (decodeMs / 1000) : null,
    input,
    output,
    cache,
  };
}
function renderStats() {
  const s = sessionStats(),
    groups = [];
  if (s.steps) groups.push(`${tr('turnCount', {count: s.turns})} · ${tr('stepCount', {count: s.steps})}`);
  if (s.llmMs)
    groups.push(
      `LLM ${duration(s.llmMs)}${s.toolMs ? ` · ${tr('toolCall')} ${duration(s.toolMs)}` : ''}`,
    );
  if (s.ttft != null)
    groups.push(
      `TTFT ${tr('average')} ${duration(s.ttft)}${s.tps != null ? ` · ${Math.round(s.tps)} tok/s` : ''}`,
    );
  if (s.input)
    groups.push(
      `${tr('cacheHit')} ${Math.round((100 * s.cache) / s.input)}% · ${tr('tokenInput')} ${compact(s.input)} tok · ${tr('tokenOutput')} ${compact(s.output)} tok`,
    );
  $('session-stats').innerHTML = groups
    .map((g) => `<span>${esc(g)}</span>`)
    .join('<i>|</i>');
}
function messageMetrics(message) {
  if (message.data.role !== 'assistant') return '';
  const req = [...requests()]
      .reverse()
      .find((r) => r.turn === message.turn && r.seq < message.seq),
    response = req && responseFor(req),
    usage = response?.data.usage || {};
  if (!req) return '';
  return `<span class="message-meta">${tr('tokenInput')} ${fmt(usage.input_tokens)} · ${tr('tokenOutput')} ${fmt(usage.output_tokens)} · ${tr('cached')} ${fmt(usage.cache_read_tokens)} · ${response ? duration(response.data.latency_ms) : tr('running')}</span><button class="message-inspect" data-trace-seq="${req.seq}">${tr('inspect')}</button>`;
}
function messageActions(message) {
  if (
    !message.data.content ||
    !['user', 'assistant'].includes(message.data.role)
  )
    return '';
  return `<div class="message-actions"><button class="copy-button" data-copy-seq="${message.seq}" title="${tr('copy')}" aria-label="${tr('copy')}">${icon('copy')}</button>${messageMetrics(message)}</div>`;
}
function renderChat() {
  const transcript = $('transcript'),
    follow = isNearBottom(transcript),
    scroll = transcript.scrollTop;
  const editor = transcript.querySelector('.message-editor');
  const editDraft = editor
    ? {
        value: editor.value,
        start: editor.selectionStart,
        end: editor.selectionEnd,
        focused: document.activeElement === editor,
      }
    : null;
  const openReasoning = [
    ...transcript.querySelectorAll('.reasoning[open]'),
  ].map((el) => el.closest('[data-message-seq]')?.dataset.messageSeq);
  const openTools = [...transcript.querySelectorAll('.tool-use[open]')].map(
    (el) => el.dataset.toolKey,
  );
  let html = '';
  for (const message of effectiveMessages()) {
    const m = message.data;
    if (m.role === 'tool') {
      html += `<div class="tool-row tool-result"><span class="tool-label">${icon('terminal')}<span>${tr('toolResult')}</span></span><button class="tool-action" data-source="${esc(message.ref)}">${tr('inspect')} ${icon('right')}</button></div>`;
      continue;
    }
    if (m.tool_calls?.length)
      html += m.tool_calls
        .map(
          (c, index) =>
            `<details class="tool-row tool-use" data-tool-key="${message.seq}:${index}"><summary><span class="tool-label">${icon('terminal')}<span>${esc(c.function.name)}</span></span><span class="tool-preview">${esc(toolArgumentPreview(c.function.arguments))}</span><span class="tool-disclosure">›</span></summary><pre>${esc(prettyToolArguments(c.function.arguments))}</pre></details>`,
        )
        .join('');
    if (!m.content && !m.reasoning_content) continue;
    const editing = editSeq === message.seq;
    html += `<article class="message ${m.role}" data-message-seq="${message.seq}">${m.reasoning_content ? `<details class="reasoning"><summary>${icon('thought')}<span>${tr('reasoning')}</span><small>${tr('reasoningProcess')}</small></summary><pre>${esc(m.reasoning_content)}</pre></details>` : ''}${editing ? `<textarea class="message-editor">${esc(m.content)}</textarea><div class="edit-actions"><button data-cancel-edit>${tr('cancel')}</button><button class="primary" data-save-edit="${message.seq}">${tr('save')}</button></div>` : `<div class="message-body">${m.role === 'assistant' ? renderMarkdown(m.content) : esc(m.content)}</div>`}${messageActions(message)}</article>`;
  }
  const unresolved = events.filter(
    (e) =>
      e.kind === 'approval_required' &&
      !events.some(
        (x) =>
          x.kind === 'approval_resolved' &&
          x.data.approval_id === e.data.approval_id,
      ),
  );
  for (const a of unresolved)
    html += `<article class="approval-card"><div><b>${tr('approvalRequired')} · ${esc(a.data.tool)}</b><p>${esc(a.data.arguments.description || a.data.arguments.command || a.data.arguments.file_path)}</p><pre>${esc(json(a.data.arguments))}</pre></div><div><button data-approval="${a.data.approval_id}" data-allow="false">${tr('reject')}</button><button class="primary" data-approval="${a.data.approval_id}" data-allow="true">${tr('allowOnce')}</button></div></article>`;
  const lastError = [...events].reverse().find((e) => e.kind === 'error');
  const lastEnd = [...events].reverse().find((e) => e.kind === 'turn_end');
  if (
    lastError &&
    lastError.turn === lastEnd?.turn &&
    lastEnd.data.status === 'failed'
  )
    html += `<div class="turn-error"><b>${esc(lastError.data.error)}</b><span>${esc(lastError.data.message)}</span><button data-trace-seq="${lastError.seq}">${tr('viewTrace')}</button></div>`;
  const stream = streamingMessage();
  if (stream && (stream.content || stream.reasoning))
    html += `<article class="message assistant streaming">${stream.reasoning ? `<details class="reasoning"><summary>${icon('thought')}<span>${tr('reasoning')}</span><small>${tr('thinking')}</small></summary><pre>${esc(stream.reasoning)}</pre></details>` : ''}<div class="message-body">${renderMarkdown(stream.content)}</div></article>`;
  if (running)
    html +=
      `<div class="running-indicator" role="status"><span></span> ${tr('runningDetail')}</div>`;
  if (operation && !running)
    html += `<div class="turn-error" role="status"><b>${tr('runPaused')}</b><span>${tr('resumeFromSaved')}</span><button class="icon-action" data-resume-operation="true" aria-label="${tr('resumeRun')}" title="${tr('resumeRun')}">${icon('play')}</button></div>`;
  $('transcript').innerHTML =
    html ||
    `<div class="chat-empty"><h2>${tr('chatEmptyTitle')}</h2><p>${tr('chatEmptyBody')}</p></div>`;
  const structural = operation?.data?.kind === 'compaction';
  $('send').disabled = sending || structural;
  $('input-mode').hidden = true;
  $('send').innerHTML = icon(running ? 'stop' : operation ? 'play' : 'send');
  $('send').setAttribute('aria-label', running ? tr('stopRun') : operation ? tr('resumeRun') : tr('sendMessage'));
  $('send').title = $('send').getAttribute('aria-label');
  $('send').disabled = sending;
  $('insert-input').hidden = !running && !operation;
  $('queue-input').hidden = !running && !operation;
  $('insert-input').innerHTML = icon('insert');
  $('queue-input').innerHTML = icon('queue');
  $('compact-context').innerHTML = icon('compress');
  $('attach').innerHTML = icon('plus');
  $('attach').setAttribute('aria-label', tr('addFile'));
  $('insert-input').disabled = structural || sending || !$('input').value.trim();
  $('queue-input').disabled = structural || sending || !$('input').value.trim();
  $('input-hint').textContent = '';
  $('input').placeholder = structural ? tr('compressingPlaceholder') : running || operation ? tr('followupPlaceholder') : currentLanguage === 'en' ? 'Send a message…' : '发送消息…';
  $('run-status').textContent = structural ? tr('compactionStatus') : running ? tr('activeRunStatus') : operation ? tr('pausedRunStatus') : '';
  $('compact-context').disabled = Boolean(operation) || running || sending;
  $('composer-permission').disabled = Boolean(operation) || running;
  $('attach').disabled = Boolean(operation) || running;
  syncCustomSelects();
  const settled = new Set(events.filter(e => ['queue_consumed', 'queue_cancelled'].includes(e.kind)).map(e => e.data.id));
  const queued = events.filter(e => e.kind === 'queue_enqueued' && !settled.has(e.data.id));
  const queueLabels = {steer: tr('checkpoint'), follow_up: tr('afterTurn'), next_run: tr('nextRun')};
  $('queued-inputs').innerHTML = queued.map(e => `<div class="queued-input"><span title="${esc(queueLabels[e.data.queue])}">${icon(e.data.queue === 'steer' ? 'insert' : 'queue')}</span><p>${esc(e.data.message.content)}</p><button class="icon-action" type="button" data-cancel-queue="${esc(e.data.id)}" aria-label="${tr('cancelQueued')}" title="${tr('cancelQueued')}">${icon('close')}</button></div>`).join('');
  $('stop').hidden = true;
  $('trace-count').textContent = requests().length;
  if (editDraft) {
    const next = transcript.querySelector('.message-editor');
    if (next) {
      next.value = editDraft.value;
      if (editDraft.focused) {
        next.focus({ preventScroll: true });
        next.setSelectionRange(editDraft.start, editDraft.end);
      }
    }
  }
  for (const key of openReasoning)
    transcript
      .querySelector(`[data-message-seq="${key}"] .reasoning`)
      ?.setAttribute('open', '');
  for (const key of openTools)
    transcript
      .querySelector(`.tool-use[data-tool-key="${key}"]`)
      ?.setAttribute('open', '');
  transcript.scrollTop = follow ? transcript.scrollHeight : scroll;
  $('jump-latest').hidden = follow;
  renderStats();
}
function renderAttachments() {
  $('attachments').innerHTML = pendingAttachments
    .map(
      (f, i) =>
        `<span>${esc(f.name)}<button data-remove-attachment="${i}">×</button></span>`,
    )
    .join('');
}

function workspaceKey(session) {
  return session.config.workspace || config.default_workspace;
}
function renderSessionTree() {
  const query = $('session-search').value.trim().toLowerCase(),
    groups = new Map();
  for (const session of sessionsCache) {
    const path = workspaceKey(session);
    if (query && !`${path} ${session.title}`.toLowerCase().includes(query))
      continue;
    if (!groups.has(path)) groups.set(path, []);
    groups.get(path).push(session);
  }
  $('workspace-paths').innerHTML = [
    ...new Set([config.default_workspace, ...sessionsCache.map(workspaceKey)]),
  ]
    .filter(Boolean)
    .map((path) => `<option value="${esc(path)}"></option>`)
    .join('');
  $('workspaces').innerHTML =
    [...groups]
      .map(([path, children]) => {
        const closed = !query && collapsedWorkspaces.has(path),
          visible =
            query || expandedWorkspaces.has(path)
              ? children
              : children.slice(0, 5);
        return `<section class="workspace-group"><div class="workspace-group-head"><button class="workspace-folder" data-fold-workspace="${esc(path)}" aria-expanded="${!closed}" title="${esc(path)}">${icon(closed ? 'right' : 'down')}${icon('folder')}<b>${esc(path.split('/').filter(Boolean).at(-1) || path)}</b><small>${children.length}</small></button><button data-new-workspace="${esc(path)}" title="${tr('newInWorkspace')}" aria-label="${tr('newInWorkspace')}">＋</button></div><div class="workspace-children ${closed ? 'is-collapsed' : ''}"><div class="workspace-children-inner">${visible.map((item) => `<button class="session-item ${item.id === sid ? 'selected' : ''}" data-session="${esc(item.id)}" aria-current="${item.id === sid ? 'page' : 'false'}" title="${esc(item.title)}"><span class="session-title">${esc(item.title)}</span></button>`).join('')}${!query && children.length > 5 ? `<button class="show-more" data-expand-workspace="${esc(path)}">${expandedWorkspaces.has(path) ? tr('collapseMore') : tr('expandRemaining', {count: children.length - 5})}</button>` : ''}</div></div></section>`;
      })
      .join('') ||
    `<div class="sidebar-empty">${query ? tr('noMatchingChats') : tr('noWorkspaces')}<p>${query ? tr('tryAnotherSearch') : tr('startFirstWork')}</p></div>`;
}
async function renderSessions() {
  sessionsCache = await api('/sessions');
  renderSessionTree();
  return sessionsCache;
}
async function pickWorkspace() {
  const items = await api('/workspaces');
  $('workspace-options').innerHTML =
    items
      .map(
        (w) =>
          `<button type="button" data-pick-path="${esc(w.path)}">${icon('folder')}<span><b>${esc(w.name)}</b><small>${esc(w.path)}</small></span></button>`,
      )
      .join('') ||
    `<p class="section-description">${tr('noRecentWorkspace')}</p>`;
  $('workspace-path').value = $('workspace').value || config.default_workspace;
  $('workspace-dialog').showModal();
}
async function openSession(id) {
  saveDraft();
  const generation = ++sessionGeneration;
  const data = await api('/sessions/' + id);
  if (generation !== sessionGeneration) return;
  sid = id;
  events = data.events;
  running = data.running;
  operation = data.operation || null;
  traceSelection = null;
  traceRange = null;
  timelineViewport = null;
  selectedTraceIds.clear();
  localStorage.setItem('magi-harness-session', sid);
  const workspace = data.session.config.workspace || config.default_workspace;
  $('title').textContent = data.session.title;
  $('workspace-chip').textContent = workspace;
  $('workspace-chip').title = workspace;
  $('composer-permission').value = data.session.config.permission_mode || 'ask';
  syncCustomSelects();
  $('magi-workspace').value = workspace;
  const draft = drafts.get(sid);
  $('input').value = draft?.text || '';
  pendingAttachments = draft?.attachments || [];
  renderAttachments();
  resizeInput($('input'));
  editSeq = null;
  collapsedTurnKeys.clear();
  $('transcript').innerHTML = '';
  await renderSessions();
  if (generation !== sessionGeneration) return;
  renderChat();
  if (page !== 'trace') setPage('chat');
  else renderTrace();
}
function openLaunch(workspace = config.default_workspace) {
  saveDraft();
  sessionGeneration++;
  sid = null;
  running = false;
  operation = null;
  editSeq = null;
  traceSelection = null;
  traceRange = null;
  timelineViewport = null;
  selectedTraceIds.clear();
  $('trace-count').textContent = '0';
  renderSessionTree();
  events = [];
  $('workspace').value = workspace;
  $('policy').value = prefs.context_policy || 'four_zone';
  $('permission-mode').value = 'ask';
  syncCustomSelects();
  $('launch-input').value = '';
  $('launch-error').textContent = '';
  $('title').textContent = 'MAGI Harness';
  $('workspace-chip').textContent = tr('newChatChip');
  setPage('launch');
  setTimeout(() => $('launch-input').focus(), 0);
}

const zoneMeta = {
  stable: ['◆', 'Stable'],
  stubs: ['◇', 'Stubs'],
  cold: ['◫', 'Cold'],
  hot: ['●', 'Hot'],
};
function rawTraceEvents() {
  return events.filter(
    (e) =>
      !['delta', 'canonical', 'attachment', 'message_edit'].includes(e.kind),
  );
}
function rawKind(event) {
  if (event.kind === 'message')
    return event.data.role === 'tool'
      ? 'tool_result'
      : event.data.tool_calls?.length
        ? 'assistant_call'
        : event.data.role;
  if (event.kind === 'stage') return 'switch';
  return event.kind;
}
function rawPreview(event) {
  if (event.kind === 'message')
    return (
      event.data.content ||
      event.data.tool_calls
        ?.map((c) => c.function?.name || 'Tool')
        .join(', ') ||
      ''
    );
  if (event.kind === 'request')
    return `${event.data.provider_binding || ''} · ${event.data.payload?.model || ''} · Stage ${event.data.stage}`;
  if (event.kind === 'response')
    return `${event.data.finish_reason || 'response'} · ${duration(event.data.latency_ms || 0)} · ${fmt(event.data.usage?.input_tokens)} in`;
  if (event.kind === 'stage')
    return `Hot → Cold ${event.data.moved_to_cold?.length || 0} · Cold → Stubs ${event.data.moved_to_stubs?.length || 0}`;
  if (event.kind === 'tool_start')
    return `${event.data.function?.name || event.data.name || 'tool'}(${event.data.function?.arguments || event.data.arguments || ''})`;
  return event.data.message || event.data.status || json(event.data);
}
// A request starts a Step; its assistant output and tool results belong to that Step.
function buildTrajectory() {
  const records = [],
    turns = new Map(),
    steps = new Map(),
    active = new Map();
  for (const event of events) {
    if (event.turn && !turns.has(event.turn))
      turns.set(event.turn, turns.size + 1);
    if (
      [
        'delta',
        'canonical',
        'attachment',
        'message_edit',
        'turn_start',
        'turn_end',
        'response',
        'approval_resolved',
      ].includes(event.kind)
    )
      continue;
    if (event.kind === 'request') {
      steps.set(event.turn, (steps.get(event.turn) || 0) + 1);
      active.set(event.turn, event);
    }
    const request = active.get(event.turn),
      kind = rawKind(event);
    if (kind === 'tool_result') continue;
    const record = {
      id: `evt:${event.seq}`,
      seq: event.seq,
      turn: event.turn,
      turnNumber: turns.get(event.turn),
      step: steps.get(event.turn) || 0,
      kind,
      created: event.created,
      request,
      ref: event.ref,
      data: event.data,
      event,
      label: kind,
      preview: rawPreview(event),
    };
    if (kind === 'request') {
      record.label = `Step ${record.step}`;
      const next = events.find(
        (e) =>
          e.kind === 'request' && e.turn === event.turn && e.seq > event.seq,
      );
      record.members = events.filter(
        (e) =>
          e.turn === event.turn &&
          e.seq >= event.seq &&
          (!next || e.seq < next.seq),
      );
      record.response = responseFor(event);
    } else if (kind === 'tool_start') {
      const id = event.data.id;
      record.result = events.find(
        (e) =>
          e.kind === 'message' &&
          e.turn === event.turn &&
          e.data.role === 'tool' &&
          e.data.tool_call_id === id &&
          e.seq > event.seq,
      );
      record.label = event.data.function?.name || event.data.name || 'Tool';
      record.preview =
        event.data.function?.arguments || event.data.arguments || '';
    } else if (kind === 'assistant_call' || kind === 'assistant') {
      const effective =
        effectiveMessages().find((m) => m.seq === event.seq)?.data ||
        event.data;
      if (effective.reasoning_content)
        records.push({
          ...record,
          id: `reason:${event.seq}`,
          kind: 'reasoning',
          label: tr('reasoning'),
          preview: effective.reasoning_content,
          data: { content: effective.reasoning_content },
        });
      if (!effective.content) continue;
      record.label = tr('assistant');
      record.preview = effective.content;
      record.data = effective;
    } else if (kind === 'user') record.label = tr('user');
    else if (kind === 'switch') record.label = tr('switch');
    else if (kind === 'approval_required') record.label = tr('approval');
    else if (kind === 'error' || kind === 'request_error')
      record.label = tr('error');
    else continue;
    records.push(record);
  }
  // Show partial output only for the current, unfinished provider request.
  const stream = streamingMessage(),
    request = requests().at(-1);
  if (stream && request)
    for (const [kind, content] of [
      ['reasoning', stream.reasoning],
      ['assistant', stream.content],
    ])
      if (content)
        records.push({
          id: `live:${request.seq}:${kind}`,
          seq: request.seq,
          turn: request.turn,
          turnNumber: turns.get(request.turn),
          step: steps.get(request.turn),
          kind,
          label: kind === 'reasoning' ? tr('reasoning') : tr('assistant'),
          preview: content,
          data: { content },
          request,
          created: request.created,
          partial: true,
        });
  const result = [],
    seenTurns = new Set();
  let previousStatic = '';
  for (const record of records) {
    if (record.turn && !seenTurns.has(record.turn)) {
      seenTurns.add(record.turn);
      const request = records.find(
        (r) => r.kind === 'request' && r.turn === record.turn,
      )?.event;
      if (request) {
        const messages = (request.data.payload?.messages || []).filter((m) =>
          ['system', 'developer'].includes(m.role),
        );
        const tools = request.data.payload?.tools || [];
        const signature = json({ messages, tools });
        if (signature !== previousStatic) {
          previousStatic = signature;
          result.push({
            id: `static:${request.seq}:system`,
            kind: 'static',
            icon: 'settings',
            label: tr('system'),
            preview: messages.map((m) => m.content).join('\n'),
            data: messages,
            request,
            ref: request.ref,
            seq: request.seq,
            created: request.created,
          });
          result.push({
            id: `static:${request.seq}:tools`,
            kind: 'static',
            icon: 'wrench',
            label: tr('tools'),
            preview: tools
              .map((t) => t.function?.name || t.name || 'Tool')
              .join(', '),
            data: tools,
            request,
            ref: request.ref,
            seq: request.seq,
            created: request.created,
          });
        }
      }
    }
    result.push(record);
  }
  return result;
}
// Timings are derived from durable events; never invent a duration for pending work.
function timelineEntries(records) {
  return records
    .filter((r) => ['static', 'user', 'reasoning', 'assistant', 'tool_start', 'error', 'switch'].includes(r.kind))
    .map((r) => {
      const finish =
        r.kind === 'request' ? r.response?.created : r.result?.created;
      const firstDelta =
        r.kind === 'request'
          ? r.members.find((e) => e.kind === 'delta' && e.data.text)?.created
          : null;
      return {
        id: r.id,
        label:
          r.kind === 'request'
            ? `Turn ${r.turnNumber} / Step ${r.step}`
            : r.label,
        start: r.created,
        end: finish ?? r.created,
          lane: ['static', 'user'].includes(r.kind) ? 0 : r.kind === 'tool_start' ? 2 : 1,
        kind: r.kind,
        firstDelta,
      };
    });
}

function projectTimeline(records) {
  const source = timelineEntries(records);
  const items = source.map((item, index) =>
      timelineMode === 'sequence'
      ? {
          ...item,
          start: source.slice(0, index).filter((entry) => entry.kind !== 'switch').length,
          end: source.slice(0, index).filter((entry) => entry.kind !== 'switch').length + (item.kind === 'switch' ? 0 : 1),
          sourceStart: item.start,
          sourceEnd: item.end,
        }
      : item,
  );
  const start = items.length ? Math.min(...items.map((item) => item.start)) : 0;
  const end = items.length ? Math.max(...items.map((item) => item.end)) : 1;
  return { items, start, end: Math.max(end, start + 0.001) };
}

function selectTimelineRange(lo, hi) {
  traceRange = { lo: Math.min(lo, hi), hi: Math.max(lo, hi) };
  traceSelection = null;
  selectedTraceIds.clear();
  for (const item of projectTimeline(traceRecordsCache).items)
    if (item.end >= traceRange.lo && item.start <= traceRange.hi) {
      selectedTraceIds.add(item.id);
      if (item.kind === 'request')
        for (const record of traceRecordsCache)
          if (
            record.request?.seq === Number(item.id.split(':')[1]) &&
            ['request', 'assistant', 'reasoning'].includes(record.kind)
          )
            selectedTraceIds.add(record.id);
    }
  renderTrace();
}
function renderOverview(records) {
  const projection = projectTimeline(records),
    items = projection.items,
    plot = $('trace-overview');
  const fullSpan = projection.end - projection.start;
  if (
    !timelineViewport ||
    timelineViewport.start < projection.start ||
    timelineViewport.end > projection.end
  ) {
    timelineViewport = { start: projection.start, end: projection.end };
  }
  const first = timelineViewport.start,
    last = timelineViewport.end,
    span = Math.max(last - first, 0.001);
  const ratio = (value) => (100 * (value - first)) / span;
  const visible = items.filter(
    (item) => item.end >= first && item.start <= last,
  );
  const label = (item) => {
    if (timelineMode === 'sequence')
      return `${item.label} · #${items.indexOf(item) + 1}`;
    const durationLabel =
      item.end > item.start
        ? ` · ${duration((item.end - item.start) * 1000)}`
        : ` · ${tr('startMarker')}`;
    return `${item.label} · +${(item.start - projection.start).toFixed(2)}s${durationLabel}`;
  };
  plot.innerHTML = `<div class="overview-labels"><span>${tr('input')}</span><span>${tr('model')}</span><span>${tr('toolLane')}</span></div><div class="overview-track" id="overview-track">${visible
    .map((item) => {
      const left = Math.max(0, ratio(item.start));
      const right = Math.min(100, ratio(item.end));
      const ttft =
        timelineMode === 'duration' && item.firstDelta && item.end > item.start
          ? Math.min(
              100,
              (100 * (item.firstDelta - item.start)) / (item.end - item.start),
            )
          : 0;
      const visualWidth = timelineMode === 'duration' && items.indexOf(item) === 0 ? Math.max(0.6, right - left) : Math.max(0.3, right - left);
      return `<button class="overview-event ${item.kind} ${selectedTraceIds.has(item.id) ? 'selected' : ''}" data-timeline-id="${item.id}" style="--lane:${item.lane};left:${left}%;width:${visualWidth}%;--ttft:${ttft}%" title="${esc(label(item))}" aria-label="${esc(item.label)}"></button>`;
    })
    .join(
      '',
    )}<div id="overview-selection" class="overview-selection" ${traceRange ? '' : 'hidden'} style="left:${traceRange ? Math.max(0, ratio(traceRange.lo)) : 0}%;width:${traceRange ? Math.max(0, Math.min(100, ratio(traceRange.hi)) - Math.max(0, ratio(traceRange.lo))) : 0}%"></div></div>`;
  $('overview-scale').innerHTML = Array.from({ length: 5 }, (_, i) => {
    const value = first + ((last - first) * i) / 4;
    return `<span>${timelineMode === 'sequence' ? Math.round(value + 1) : `+${(value - projection.start).toFixed(2)}s`}</span>`;
  }).join('');
  $('overview-clear').disabled = !traceRange && !traceSelection;
  const track = $('overview-track');
  let start = null;
  const coordinate = (e) => {
    const bounds = track.getBoundingClientRect();
    return (
      first +
      Math.max(
        0,
        Math.min(1, (e.clientX - bounds.left) / Math.max(1, bounds.width)),
      ) *
        span
    );
  };
  track.onpointerdown = (e) => {
    if (e.button !== 0 || e.target.closest('button')) return;
    start = coordinate(e);
    track.setPointerCapture?.(e.pointerId);
  };
  track.onpointermove = (e) => {
    if (start === null) return;
    const end = coordinate(e),
      overlay = $('overview-selection');
    overlay.hidden = false;
    overlay.style.left = `${ratio(Math.min(start, end))}%`;
    overlay.style.width = `${Math.abs(ratio(end) - ratio(start))}%`;
  };
  track.onpointerup = (e) => {
    if (start === null) return;
    const end = coordinate(e);
    selectTimelineRange(start, end);
    start = null;
  };
  track.onpointercancel = () => {
    start = null;
    renderOverview(traceRecordsCache);
  };
  track.oncontextmenu = (e) => {
    e.preventDefault();
    clearTraceSelection();
  };
  track.onwheel = (e) => {
    e.preventDefault();
    if (!items.length) return;
    // Trackpad horizontal gestures (or Shift+wheel) pan the viewport. A
    // vertical wheel keeps the established cursor-centred zoom behaviour.
    const horizontal = Math.abs(e.deltaX) > 0.5 || (e.shiftKey && Math.abs(e.deltaY) > 0.5);
    if (horizontal) {
      const delta = Math.abs(e.deltaX) > 0.5 ? e.deltaX : e.deltaY;
      const amount = (delta / Math.max(1, track.clientWidth)) * span;
      const maxStart = projection.end - span;
      const nextStart = Math.max(
        projection.start,
        Math.min(maxStart, first + amount),
      );
      timelineViewport = { start: nextStart, end: nextStart + span };
      renderOverview(traceRecordsCache);
      return;
    }
    const bounds = track.getBoundingClientRect();
    const cursor = Math.max(
      0,
      Math.min(1, (e.clientX - bounds.left) / Math.max(1, bounds.width)),
    );
    const minimum =
      timelineMode === 'sequence'
        ? Math.max(fullSpan / 100, 0.5)
        : Math.max(fullSpan / 100, 0.05);
    const nextSpan = Math.max(
      minimum,
      Math.min(fullSpan, span * Math.exp(e.deltaY * 0.0015)),
    );
    let nextStart = first + span * cursor - nextSpan * cursor;
    nextStart = Math.max(
      projection.start,
      Math.min(nextStart, projection.end - nextSpan),
    );
    timelineViewport = { start: nextStart, end: nextStart + nextSpan };
    renderOverview(traceRecordsCache);
  };
}
function contextUsage(request) {
  return Object.keys(zoneMeta).map((zone) => ({
    zone,
    blocks: request?.data.zones?.[zone] || [],
    units: (request?.data.zones?.[zone] || []).reduce(
      (sum, b) => sum + (Number(b.budget_units) || 0),
      0,
    ),
  }));
}
function contextBar(request) {
  const zones = contextUsage(request),
    total = zones.reduce((n, z) => n + z.units, 0);
  return `<span class="step-context-bar" role="img" aria-label="${esc(zones.map((z) => `${z.zone}: ${z.units} units`).join(', '))}">${zones.map((z) => `<span class="zone-${z.zone}" style="width:${total ? (100 * z.units) / total : 0}%" title="${z.zone} · ${fmt(z.units)} units"></span>`).join('')}</span>`;
}
function cacheInfo(response) {
  const usage = response?.data.usage;
  if (usage?.cache_read_tokens == null) return 'Cache —';
  const ratio =
    usage.input_tokens > 0
      ? ` · ${Math.round((100 * usage.cache_read_tokens) / usage.input_tokens)}%`
      : '';
  return `Cache ${compact(usage.cache_read_tokens)}${ratio}`;
}
let inspectorTab = 'overview';
function detailBlock(title, value) {
  return `<section class="detail-block"><h4>${esc(title)}</h4><pre>${esc(typeof value === 'string' ? value : json(value))}</pre></section>`;
}
function renderInspector(record) {
  const panel = $('trace-inspector');
  if (!record) {
    inspectorKey = null;
    panel.hidden = true;
    panel.innerHTML = '';
    return;
  }
  const key = `${sid}:${record.id}:${inspectorTab}:${record.kind === 'request' ? record.members.length : `${record.preview.length}:${record.result?.seq || 0}`}`;
  if (key === inspectorKey) return;
  inspectorKey = key;
  panel.hidden = false;
  const step =
    record.kind === 'request'
      ? record
      : traceRecordsCache.find(
          (r) => r.kind === 'request' && r.seq === record.request?.seq,
        );
  const tabs =
    record.kind === 'request'
      ? [
          ['overview', tr('overview')],
          ['context', tr('context')],
          ['output', tr('output')],
          ['tools', tr('tools')],
          ['raw', tr('rawRecord')],
        ]
      : [
          ['overview', tr('overview')],
          ['raw', tr('rawRecord')],
        ];
  if (!tabs.some(([id]) => id === inspectorTab)) inspectorTab = 'overview';
  let body = '';
  if (inspectorTab === 'raw') {
    body = detailBlock(
      tr('rawRecord'),
      record.kind === 'request' ? record.members : record.data,
    );
    const refs = [...new Set([record.ref, record.result?.ref].filter(Boolean))];
    body += refs
      .map(
        (ref) =>
          `<button class="source-button" data-source="${esc(ref)}">${tr('viewFullSource')}</button>`,
      )
      .join('');
  } else if (record.kind === 'request') {
    const req = record.event,
      response = record.response,
      usage = response?.data.usage,
      zones = contextUsage(req);
    if (inspectorTab === 'overview') {
      body = `<div class="step-model">${esc(req.data.payload?.model || req.data.provider_binding || 'Provider request')}<small>${response ? esc(response.data.finish_reason || tr('completed')) : tr('waitingResponse')}</small></div><div class="metric-grid"><div><small>${tr('input')}</small><b>${fmt(usage?.input_tokens)}</b></div><div><small>${tr('output')}</small><b>${fmt(usage?.output_tokens)}</b></div><div><small>${tr('elapsed')}</small><b>${response ? duration(response.data.latency_ms) : '—'}</b></div><div><small>${tr('cacheRead')}</small><b>${esc(cacheInfo(response))}</b></div></div><section class="context-composition"><h4>${tr('fourZoneContext')}</h4>${contextBar(req)}<div class="context-key">${zones.map((z) => `<span><i class="zone-${z.zone}"></i>${z.zone}<b>${fmt(z.units)}</b></span>`).join('')}</div></section>`;
    } else if (inspectorTab === 'context') {
      body =
        `<section class="context-composition">${contextBar(req)}</section>` +
        zones
          .map(
            (z) =>
              `<details class="context-zone"><summary><i class="zone-${z.zone}"></i>${z.zone}<span>${z.blocks.length} blocks · ${fmt(z.units)} units</span></summary>${z.blocks.map((block) => detailBlock(block.message?.role || block.id, block.message || block)).join('') || `<p>${tr('emptyZone')}</p>`}</details>`,
          )
          .join('');
    } else if (inspectorTab === 'output') {
      const message = response?.data.message;
      const deltas = record.members.filter((e) => e.kind === 'delta');
      const reasoning =
        message?.reasoning_content ||
        deltas
          .filter((e) => e.data.field === 'reasoning_content')
          .map((e) => e.data.text)
          .join('');
      const content =
        message?.content ||
        deltas
          .filter((e) => e.data.field === 'content')
          .map((e) => e.data.text)
          .join('');
      body =
        (reasoning ? detailBlock(tr('reasoning'), reasoning) : '') +
          (content ? detailBlock('Assistant', content) : '') ||
        `<p class="detail-empty">${tr('noTextOutput')}</p>`;
    } else if (inspectorTab === 'tools') {
      const tools = traceRecordsCache.filter(
        (r) => r.kind === 'tool_start' && r.request?.seq === req.seq,
      );
      body =
        tools
          .map(
            (tool) =>
              `<details class="context-zone" open><summary>${esc(tool.label)}<span>${tool.result ? tr('returned') : tr('waitingReturn')}</span></summary>${detailBlock(tr('arguments'), tool.preview)}${tool.result ? detailBlock(tr('result'), tool.result.data.content) : ''}</details>`,
          )
          .join('') || `<p class="detail-empty">${tr('noToolCalls')}</p>`;
    }
  } else if (record.kind === 'tool_start')
    body =
      detailBlock(tr('callArguments'), record.preview) +
      (record.result
        ? detailBlock(tr('toolReturn'), record.result.data.content)
        : `<p class="detail-empty">${tr('waitingToolReturn')}</p>`);
  else if (record.kind === 'switch')
    body = `<div class="switch-summary"><h4>Stage ${Math.max(0, (record.data.number || 1) - 1)} → ${record.data.number || '—'}</h4><p>${record.data.reason === 'budget' ? tr('contextBudgetTrigger') : tr('turnThresholdTrigger')}</p><dl><dt>Hot → Cold</dt><dd>${record.data.moved_to_cold?.length || 0} ${tr('rounds')}</dd><dt>Cold → Stubs</dt><dd>${record.data.moved_to_stubs?.length || 0} ${tr('blocks')}</dd><dt>${tr('retainedHot')}</dt><dd>${record.data.retained_hot?.length || 0} ${tr('rounds')}</dd></dl></div>`;
  else if (record.kind === 'static')
    body =
      record.label === 'Tools'
        ? record.data
            .map(
              (tool) =>
                `<details class="context-zone"><summary>${esc(tool.function?.name || tool.name || 'Tool')}</summary>${detailBlock(tr('definition'), tool.function || tool)}</details>`,
            )
            .join('') || `<p>${tr('noTools')}</p>`
        : record.data.map((m) => detailBlock(m.role, m.content)).join('') ||
          `<p>${tr('noSystemMessage')}</p>`;
  else body = detailBlock(record.label, record.preview);
  const trail =
    record.kind === 'static'
      ? 'REQUEST CONFIGURATION'
      : record.kind === 'switch'
        ? 'CONTEXT TRANSITION'
        : `Turn ${record.turnNumber || '—'}${record.step ? ` / Step ${record.step}` : ''}`;
  panel.innerHTML = `<div class="inspector-head"><div><small>${esc(trail)}</small><h3>${esc(record.label)}</h3></div><button id="close-inspector" aria-label="${tr('closeDetails')}">${icon('close')}</button></div><nav class="inspector-tabs" role="tablist">${tabs.map(([id, label]) => `<button role="tab" aria-selected="${inspectorTab === id}" data-inspector-tab="${id}">${label}</button>`).join('')}</nav><div class="inspector-body">${record.kind !== 'request' && step ? `<button class="back-to-step" data-trace-id="${step.id}">← Step ${step.step} · ${tr('contextAndCache')}</button>` : ''}${body}</div>`;
}
function selectTraceRecord(id, fromLine = false) {
  traceSelection = id;
  lineSelection = fromLine;
  document.body.classList.add('inspector-open');
  traceRange = null;
  selectedTraceIds.clear();
  selectedTraceIds.add(id);
  inspectorTab = 'overview';
  inspectorKey = null;
  renderTrace();
}
function renderTrace() {
  const ledger = $('timeline'),
    scroll = ledger.scrollTop,
    records = buildTrajectory();
  traceRecordsCache = records;
  renderOverview(records);
  const query = $('trace-search').value.trim().toLowerCase();
  let html = '',
    activeTurn = null,
    visibleCount = 0;
  const row = (record) => {
    visibleCount++;
    const tool = record.kind === 'tool_start',
      end = record.result;
    return `<button class="trajectory-item kind-${record.kind} ${traceRange && !selectedTraceIds.has(record.id) ? 'outside-range' : ''} ${traceSelection === record.id ? 'selected' : ''} ${lineSelection && traceSelection && traceSelection !== record.id ? 'dimmed' : ''} ${record.kind === 'error' ? 'is-error' : ''}" data-trace-id="${record.id}" title="${esc(record.preview.slice(0, 400))}"><span class="record-index">${record.seq}</span><span class="trajectory-kind">${icon(tool ? 'terminal' : record.kind === 'reasoning' ? 'thought' : record.kind === 'user' ? 'user' : 'message')}<span>${esc(record.label)}</span></span><span class="trajectory-preview">${esc(record.preview.slice(0, 260))}</span><time>${tool ? (end ? duration(Math.max(0, (end.created - record.created) * 1000)) : '…') : record.partial ? '…' : ''}</time></button>`;
  };
  const matches = (r) =>
    !query ||
    `${r.label} ${r.preview} Turn ${r.turnNumber} Step ${r.step}`
      .toLowerCase()
      .includes(query);
  for (const record of records) {
    if (record.kind === 'request') continue;
    if (record.kind === 'static') {
      html += `<button class="trajectory-item static-record ${lineSelection && traceSelection !== record.id ? 'dimmed' : ''}" data-trace-id="${record.id}"><span class="record-index">—</span><span class="trajectory-kind">${icon(record.icon)}<span>${esc(record.label)}</span></span><span class="trajectory-preview">${esc(record.preview.slice(0, 260) || (record.icon === 'wrench' ? tr('noTools') : tr('noSystemMessage')))}</span><time>${record.data.length}</time></button>`;
      continue;
    }
    if (record.kind === 'switch') {
      html += `<button class="switch-divider ${lineSelection && traceSelection !== record.id ? 'dimmed' : ''}" data-trace-id="${record.id}">${icon('switch')}<b>Switch</b><span>${esc(record.preview)}</span></button>`;
      continue;
    }
    const relevant =
      matches(record) ||
      (record.kind === 'request' &&
        records.some((r) => r.request?.seq === record.seq && matches(r)));
    if (!relevant) continue;
    if (activeTurn !== record.turn) {
      activeTurn = record.turn;
      html += `<div class="ledger-turn"><button data-fold-turn="${esc(activeTurn)}" aria-expanded="${!collapsedTurnKeys.has(activeTurn)}">${icon(collapsedTurnKeys.has(activeTurn) ? 'right' : 'down')}Turn ${record.turnNumber}</button><span>${tr('eventContentTime')}</span></div>`;
    }
    if (collapsedTurnKeys.has(record.turn)) continue;
    if (foldCalls && record.kind === 'tool_start') continue;
    html += row(record);
  }
  ledger.innerHTML =
    html ||
    `<div class="trace-empty">${tr('noTraceTitle')}<p>${tr('noTraceBody')}</p></div>`;
  ledger.scrollTop = scroll;
  $('trace-summary').textContent =
    `${new Set(records.filter((r) => r.turn).map((r) => r.turn)).size} Turns · ${records.filter((r) => r.kind === 'request').length} Steps`;
  renderInspector(records.find((r) => r.id === traceSelection));
}

function providerDraft() {
  return {
    binding: $('provider-binding-input').value,
    model: $('provider-model').value.trim(),
    host: $('provider-host').value.trim(),
    api_key: $('provider-key').value,
    timeout: Number($('provider-timeout').value),
  };
}
function syncProvider() {
  $('provider-binding').textContent = (config.binding || 'demo').toUpperCase();
  $('model').textContent = config.model;
  $('launch-model-name').textContent = config.model;
  $('version').textContent = `v${config.version}`;
}

function closeModelPopover() {
  modelPopoverGeneration++;
  $('model-popover').hidden = true;
}

function positionModelPopover(anchor) {
  const panel = $('model-popover');
  const rect = anchor.getBoundingClientRect();
  const width = 300;
  const left = Math.max(
    12,
    Math.min(innerWidth - width - 12, rect.right - width),
  );
  panel.style.left = `${left}px`;
  panel.style.top = `${Math.max(12, rect.top - panel.offsetHeight - 8)}px`;
}

async function showModelPopover(anchor) {
  const generation = ++modelPopoverGeneration;
  const panel = $('model-popover');
  panel.hidden = false;
  $('model-options').innerHTML = '';
  $('model-popover-status').textContent = tr('loadingModels');
  positionModelPopover(anchor);
  try {
    const provider = await api('/settings/provider');
    if (generation !== modelPopoverGeneration) return;
    $('model-popover-binding').textContent = provider.binding.toUpperCase();
    const result =
      provider.binding === 'demo'
        ? { models: [provider.model] }
        : await api('/settings/provider/discover', 'POST', {
            binding: provider.binding,
            model: provider.model,
            host: provider.host,
            api_key: '',
            timeout: provider.timeout,
          });
    if (generation !== modelPopoverGeneration) return;
    const models = [...new Set([provider.model, ...result.models])];
    $('model-options').innerHTML = models
      .map(
        (model) =>
          `<button data-model-option="${esc(model)}" class="${model === provider.model ? 'selected' : ''}"><span>${esc(model)}</span>${model === provider.model ? `<small>${tr('current')}</small>` : ''}</button>`,
      )
      .join('');
    $('model-popover-status').textContent = models.length
      ? ''
      : tr('noModels');
    panel.dataset.provider = JSON.stringify(provider);
    positionModelPopover(anchor);
  } catch (error) {
    if (generation === modelPopoverGeneration)
      $('model-popover-status').textContent = error.message;
  }
}

async function selectModel(model) {
  const provider = JSON.parse($('model-popover').dataset.provider || '{}');
  $('model-popover-status').textContent = tr('applying');
  await api('/settings/provider', 'PUT', {
    binding: provider.binding,
    model,
    host: provider.host,
    api_key: '',
    timeout: provider.timeout,
  });
  config = await api('/config');
  syncProvider();
  closeModelPopover();
}

function applyBindingPreset(settings, force = false) {
  const binding = $('provider-binding-input').value,
    demo = binding === 'demo';
  if (force || !$('provider-host').value)
    $('provider-host').value = settings.default_hosts?.[binding] || '';
  $('provider-host').disabled = demo;
  $('provider-model').disabled = demo;
  $('provider-key').disabled = demo;
  $('discover-models').disabled = demo;
  $('binding-note').textContent = demo
    ? tr('demoBindingNote')
    : tr('remoteBindingNote');
  syncCustomSelects();
}
async function loadSettings() {
  const [provider, preferences] = await Promise.all([
    api('/settings/provider'),
    api('/settings/preferences'),
  ]);
  prefs = preferences;
  $('provider-binding-input').value = provider.binding;
  $('provider-model').value = provider.model;
  $('provider-host').value = provider.host;
  $('provider-key').value = '';
  $('provider-timeout').value = provider.timeout;
  $('key-state').textContent = provider.has_api_key
    ? tr('keySaved')
    : tr('keyMissing');
  applyBindingPreset(provider);
  $('language-setting').value = prefs.language;
  $('theme-setting').value = prefs.theme;
  syncCustomSelects();
  $('base-prompt').value = prefs.base_prompt;
  $('context-window').value = prefs.window;
  $('stage-turns').value = prefs.stage_turns;
  document.querySelector(
    `input[name="context-policy"][value="${prefs.context_policy}"]`,
  ).checked = true;
  applyTheme(prefs.theme);
  applyLanguage(prefs.language);
  await loadWorkspaceOverview();
  if ($('magi-workspace').value.trim())
    await loadWorkspaceInstructions($('magi-workspace').value.trim());
}
async function loadWorkspaceOverview() {
  const workspaces = await api('/workspaces');
  $('workspace-overview').innerHTML =
    workspaces
      .map(
        (w) =>
          `<button type="button" data-workspace-prompt="${esc(w.path)}"><b>${esc(w.name)}</b><span>${w.unavailable ? tr('unavailableDirectory') : w.instructions ? esc(w.instructions.slice(0, 90)) : tr('noMagiFile')}</span></button>`,
      )
      .join('') || `<p>${tr('noWorkspaces')}</p>`;
}
async function loadWorkspaceInstructions(path) {
  const generation = ++instructionsGeneration;
  loadedInstructionsWorkspace = null;
  $('magi-content').disabled = true;
  $('context-status').textContent = tr('loadingWorkspacePrompt');
  try {
    const data = await api(
      `/workspace/instructions?workspace=${encodeURIComponent(path)}`,
    );
    if (generation !== instructionsGeneration) return;
    $('magi-workspace').value = data.workspace;
    $('magi-content').value = data.content;
    loadedInstructionsWorkspace = data.workspace;
    $('magi-content').disabled = false;
    $('context-status').textContent = '';
  } catch (error) {
    if (generation === instructionsGeneration)
      $('context-status').textContent = error.message;
  }
}
function showSettings(section = 'general') {
  const generation = ++settingsGeneration;
  loadSettings()
    .then(() => {
      if (generation !== settingsGeneration) return;
      document.querySelector(`[data-settings-page="${section}"]`).click();
      $('app-settings-dialog').showModal();
    })
    .catch((e) => notice(e.message));
}

$('new').onclick = () => openLaunch();
$('launch-form').onsubmit = async (e) => {
  e.preventDefault();
  const text = $('launch-input').value.trim();
  if (!text || launching) return;
  launching = true;
  $('create').disabled = true;
  $('launch-error').textContent = '';
  try {
    const generation = sessionGeneration;
    const session = await api('/sessions', 'POST', {
      workspace: $('workspace').value.trim(),
      policy: $('policy').value,
      permission_mode: $('permission-mode').value,
    });
    await api(`/sessions/${session.id}/messages`, 'POST', {
      text,
      attachments: [],
    });
    if (generation === sessionGeneration) {
      await openSession(session.id);
      await refresh();
    } else await renderSessions();
  } catch (err) {
    $('launch-error').textContent = err.message;
    notice(err.message);
  } finally {
    launching = false;
    $('create').disabled = false;
  }
};
$('launch-input').onkeydown = (e) => {
  if (e.key === 'Enter' && !e.shiftKey && !e.isComposing) {
    e.preventDefault();
    $('launch-form').requestSubmit();
  }
};
$('composer').onsubmit = async (e) => {
  e.preventDefault();
  const text = $('input').value.trim();
  if (!text || sending || !sid || operation?.data?.kind === 'compaction') return;
  sending = true;
  const target = sid;
  const attachments = [...pendingAttachments];
  const queued = running || Boolean(operation);
  $('send').disabled = true;
  try {
    if (queued && attachments.length) throw new Error(tr('queuedAttachmentsUnsupported'));
    await api(queued ? `/sessions/${target}/queue/${$('input-mode').value}` : `/sessions/${target}/messages`, 'POST', queued ? {text} : { text, attachments });
    drafts.delete(target);
    if (sid !== target) return;
    $('input').value = '';
    resizeInput($('input'));
    pendingAttachments = [];
    renderAttachments();
    if (!queued) running = true;
    await refresh();
  } catch (err) {
    notice(err.message);
  } finally {
    sending = false;
    $('send').disabled = operation?.data?.kind === 'compaction';
  }
};
$('input').onkeydown = (e) => {
  if (e.key === 'Enter' && !e.shiftKey && !e.isComposing) {
    e.preventDefault();
    $('input-mode').value = e.altKey ? 'steer' : 'follow_up';
    $('composer').requestSubmit();
  }
};
$('insert-input').onclick = () => {
  $('input-mode').value = 'steer';
  $('composer').requestSubmit();
};
$('queue-input').onclick = () => {
  $('input-mode').value = 'follow_up';
  $('composer').requestSubmit();
};
$('send').onclick = async (event) => {
  if (!running && !operation) return;
  event.preventDefault();
  if (running) return $('stop').onclick();
  $('send').disabled = true;
  try {
    await api(`/sessions/${sid}/resume`, 'POST');
    await refresh(true);
  } catch (error) {
    notice(error.message);
  } finally {
    $('send').disabled = false;
  }
};
$('attach').onclick = () => $('file-input').click();
$('file-input').onchange = async () => {
  for (const file of [...$('file-input').files]) {
    if (file.size > 2e6) {
      notice(tr('fileTooLarge', {name: file.name}));
      continue;
    }
    pendingAttachments.push({
      name: file.name,
      type: file.type || 'text/plain',
      text: await file.text(),
    });
  }
  $('file-input').value = '';
  renderAttachments();
};
$('composer-permission').onchange = async () => {
  if (!sid) return;
  try {
    await api(`/sessions/${sid}`, 'PATCH', {
      permission_mode: $('composer-permission').value,
    });
  } catch (e) {
    notice(e.message);
  }
};
$('stop').onclick = async () => {
  $('stop').disabled = true;
  try {
    await api(`/sessions/${sid}/cancel`, 'POST');
    await refresh();
  } catch (e) {
    notice(e.message);
  } finally {
    $('stop').disabled = false;
  }
};
$('compact-context').onclick = async () => {
  if (!sid || running || operation) return;
  $('compact-context').disabled = true;
  try {
    await api(`/sessions/${sid}/compact`, 'POST');
    await refresh(true);
  } catch (error) {
    notice(error.message);
  } finally {
    $('compact-context').disabled = running || Boolean(operation);
  }
};
$('queued-inputs').onclick = async (event) => {
  const button = event.target.closest('[data-cancel-queue]');
  if (!button) return;
  button.disabled = true;
  try {
    await api(`/sessions/${sid}/queue/${button.dataset.cancelQueue}`, 'DELETE');
    await refresh(true);
  } catch (error) {
    notice(error.message);
    button.disabled = false;
  }
};
$('chat-tab').onclick = () => (sid ? setPage('chat') : setPage('launch'));
$('trace-tab').onclick = () => (sid ? setPage('trace') : setPage('launch'));
$('open-settings').onclick = () => showSettings('general');
$('model-chip').onclick = (event) =>
  showModelPopover(event.currentTarget).catch((error) => notice(error.message));
$('close-settings').onclick = () => $('app-settings-dialog').close();
$('close-source').onclick = () => $('source-dialog').close();
$('launch-model').onclick = (event) =>
  showModelPopover(event.currentTarget).catch((error) => notice(error.message));
$('sidebar-toggle').onclick = () => {
  const collapsed = document.body.classList.toggle('sidebar-collapsed');
  localStorage.setItem('magi-sidebar-collapsed', collapsed ? '1' : '0');
  $('sidebar-toggle').setAttribute('aria-expanded', String(!collapsed));
  $('sidebar-toggle').innerHTML = icon('panel');
  $('sidebar-toggle').title = collapsed ? tr('expandSidebar') : tr('collapseSidebar');
};
$('fold-turns').onclick = () => {
  foldTurns = !foldTurns;
  if (foldTurns) {
    for (const record of buildTrajectory())
      if (record.turn) collapsedTurnKeys.add(record.turn);
  } else collapsedTurnKeys.clear();
  $('fold-turns').setAttribute('aria-pressed', String(foldTurns));
  renderTrace();
};
$('fold-calls').onclick = () => {
  foldCalls = !foldCalls;
  $('fold-calls').setAttribute('aria-pressed', String(foldCalls));
  renderTrace();
};
$('traceline-mode').onclick = () => {
  timelineMode = 'sequence';
  timelineViewport = null;
  clearTraceSelection();
  $('traceline-mode').setAttribute('aria-pressed', 'true');
  $('timeline-mode').setAttribute('aria-pressed', 'false');
};
$('timeline-mode').onclick = () => {
  timelineMode = 'duration';
  timelineViewport = null;
  clearTraceSelection();
  $('traceline-mode').setAttribute('aria-pressed', 'false');
  $('timeline-mode').setAttribute('aria-pressed', 'true');
};
$('trace-search').oninput = renderTrace;
$('provider-binding-input').onchange = async () => {
  try {
    applyBindingPreset(await api('/settings/provider'), true);
  } catch (e) {
    notice(e.message);
  }
};
$('discover-models').onclick = async () => {
  $('settings-status').textContent = tr('connecting');
  try {
    const r = await api('/settings/provider/discover', 'POST', providerDraft());
    const options = $('provider-model-options');
    options.innerHTML = r.models
      .map((m) => `<button type="button" data-discovered-model="${esc(m)}">${esc(m)}</button>`)
      .join('');
    options.hidden = !r.models.length;
    options.querySelectorAll('[data-discovered-model]').forEach((button) => {
      button.onclick = () => {
        $('provider-model').value = button.dataset.discoveredModel;
        options.hidden = true;
        $('settings-status').textContent = tr('selectedModel', {model: button.dataset.discoveredModel});
      };
    });
    $('settings-status').textContent = tr('discoveredModels', {count: r.models.length});
  } catch (e) {
    $('settings-status').textContent = e.message;
  }
};
$('provider-settings').onsubmit = async (e) => {
  e.preventDefault();
  try {
    await api('/settings/provider', 'PUT', providerDraft());
    config = await api('/config');
    syncProvider();
    $('settings-status').textContent = tr('applied');
  } catch (err) {
    $('settings-status').textContent = err.message;
  }
};
$('general-settings').onsubmit = async (e) => {
  e.preventDefault();
  try {
    prefs = await api('/settings/preferences', 'PUT', {
      ...prefs,
      language: $('language-setting').value,
      theme: $('theme-setting').value,
    });
    applyTheme(prefs.theme);
    applyLanguage(prefs.language);
    $('general-status').textContent = tr('saved');
  } catch (err) {
    $('general-status').textContent = err.message;
  }
};
$('theme-setting').onchange = () => applyTheme($('theme-setting').value);
$('language-setting').onchange = () =>
  applyLanguage($('language-setting').value);
$('context-settings').onsubmit = async (e) => {
  e.preventDefault();
  try {
    if (
      $('magi-workspace').value.trim() &&
      loadedInstructionsWorkspace !== $('magi-workspace').value.trim()
    )
      throw new Error(tr('loadWorkspaceBeforeSave'));
    prefs = await api('/settings/preferences', 'PUT', {
      ...prefs,
      context_policy: document.querySelector(
        'input[name="context-policy"]:checked',
      ).value,
      window: Number($('context-window').value),
      stage_turns: Number($('stage-turns').value),
      base_prompt: $('base-prompt').value,
    });
    if (loadedInstructionsWorkspace)
      await api('/workspace/instructions', 'PUT', {
        workspace: $('magi-workspace').value.trim(),
        content: $('magi-content').value,
      });
    $('context-status').textContent = tr('contextSaved');
    await loadWorkspaceOverview();
  } catch (err) {
    $('context-status').textContent = err.message;
  }
};
$('magi-workspace').onchange = () =>
  loadWorkspaceInstructions($('magi-workspace').value.trim());
$('refresh-workspaces').onclick = () =>
  loadWorkspaceOverview().catch(
    (e) => ($('context-status').textContent = e.message),
  );
document.querySelectorAll('[data-settings-page]').forEach(
  (button) =>
    (button.onclick = () => {
      document
        .querySelectorAll('[data-settings-page]')
        .forEach((b) => b.classList.toggle('active', b === button));
      ['general', 'models', 'context'].forEach(
        (p) =>
          ($(`${p === 'models' ? 'provider' : p}-settings`).hidden =
            button.dataset.settingsPage !== p),
      );
    }),
);

document.addEventListener('click', async (e) => {
  const b = e.target.closest('button');
  if (!b) return;
  try {
    if (b.dataset.foldWorkspace) {
      const key = b.dataset.foldWorkspace;
      collapsedWorkspaces.has(key)
        ? collapsedWorkspaces.delete(key)
        : collapsedWorkspaces.add(key);
      expandedWorkspaces.delete(key);
      localStorage.setItem(
        'magi-folders',
        JSON.stringify([...collapsedWorkspaces]),
      );
      renderSessionTree();
    }
    if (b.dataset.expandWorkspace) {
      const key = b.dataset.expandWorkspace;
      expandedWorkspaces.has(key)
        ? expandedWorkspaces.delete(key)
        : expandedWorkspaces.add(key);
      renderSessionTree();
    }
    if (b.dataset.pickPath) {
      $('workspace-path').value = b.dataset.pickPath;
      $('workspace-path').focus();
    }
    if (b.dataset.session) await openSession(b.dataset.session);
    if (b.dataset.newWorkspace) openLaunch(b.dataset.newWorkspace);
    if (b.dataset.removeAttachment != null) {
      pendingAttachments.splice(Number(b.dataset.removeAttachment), 1);
      renderAttachments();
    }
    if (b.dataset.copySeq) {
      const m = effectiveMessages().find(
        (x) => x.seq === Number(b.dataset.copySeq),
      );
      await navigator.clipboard.writeText(m?.data.content || '');
      b.textContent = '✓';
      setTimeout(() => (b.textContent = '⧉'), 900);
    }
    if (b.dataset.editSeq) {
      editSeq = Number(b.dataset.editSeq);
      renderChat();
      document
        .querySelector(`[data-message-seq="${editSeq}"] .message-editor`)
        ?.focus();
    }
    if (b.hasAttribute('data-cancel-edit')) {
      editSeq = null;
      renderChat();
    }
    if (b.dataset.saveEdit) {
      const article = b.closest('article');
      await api(`/sessions/${sid}/messages/${b.dataset.saveEdit}`, 'PATCH', {
        content: article.querySelector('.message-editor').value,
      });
      editSeq = null;
      await refresh(true);
    }
    if (b.dataset.approval) {
      await api(
        `/sessions/${sid}/approvals/${b.dataset.approval}?allow=${b.dataset.allow}`,
        'POST',
      );
      await refresh(true);
    }
    if (b.dataset.resumeOperation) {
      await api(`/sessions/${sid}/resume`, 'POST');
      await refresh(true);
    }
    if (b.dataset.traceSeq) {
      setPage('trace');
      selectTraceRecord(`evt:${b.dataset.traceSeq}`);
    }
    if (b.dataset.inspectorTab) {
      inspectorTab = b.dataset.inspectorTab;
      inspectorKey = null;
      renderInspector(traceRecordsCache.find((r) => r.id === traceSelection));
    }
    if (b.dataset.timelineId) {
      selectTraceRecord(b.dataset.timelineId, true);
      document
        .querySelector(`[data-trace-id="${b.dataset.timelineId}"]`)
        ?.scrollIntoView({ block: 'nearest' });
    }
    if (b.dataset.modelOption) await selectModel(b.dataset.modelOption);
    if (b.dataset.traceId) {
      selectTraceRecord(b.dataset.traceId);
    }
    if (b.dataset.foldTurn) {
      collapsedTurnKeys.has(b.dataset.foldTurn)
        ? collapsedTurnKeys.delete(b.dataset.foldTurn)
        : collapsedTurnKeys.add(b.dataset.foldTurn);
      renderTrace();
    }
    if (b.dataset.source) {
      const d = await api(
        `/sessions/${sid}/source?ref=${encodeURIComponent(b.dataset.source)}`,
      );
      $('source-ref').textContent = d.ref;
      $('source-content').textContent = json(d.value);
      $('source-dialog').showModal();
    }
    if (b.id === 'close-inspector') clearTraceSelection();
    if (b.dataset.workspacePrompt)
      await loadWorkspaceInstructions(b.dataset.workspacePrompt);
  } catch (err) {
    notice(err.message);
  }
});

async function refresh(force = false) {
  if (!sid || polling) return;
  polling = true;
  const target = sid,
    generation = sessionGeneration;
  try {
    const d = await api(
      `/sessions/${sid}?after=${force ? 0 : events.at(-1)?.seq || 0}`,
    );
    if (target !== sid || generation !== sessionGeneration) return;
    if (force) events = d.events;
    else events.push(...d.events);
    const changed = force || d.events.length || running !== d.running || operation?.turn !== d.operation?.turn;
    running = d.running;
    operation = d.operation || null;
    if (changed) {
      renderChat();
      if (page === 'trace') renderTrace();
      if (!running) await renderSessions();
    }
  } catch (e) {
    notice(e.message);
  } finally {
    polling = false;
  }
}
async function init() {
  config = await api('/config');
  syncProvider();
  prefs = await api('/settings/preferences');
  applyTheme(prefs.theme);
  applyLanguage(prefs.language);
  if (
    localStorage.getItem('magi-sidebar-collapsed') === '1' ||
    (localStorage.getItem('magi-sidebar-collapsed') === null &&
      matchMedia('(max-width: 760px)').matches)
  ) {
    document.body.classList.add('sidebar-collapsed');
    $('sidebar-toggle').innerHTML = icon('panel');
    $('sidebar-toggle').setAttribute('aria-expanded', 'false');
  }
  $('workspace').value = config.default_workspace;
  const list = await renderSessions(),
    saved = localStorage.getItem('magi-harness-session');
  if (list.length)
    await openSession(list.find((s) => s.id === saved)?.id || list[0].id);
  else openLaunch();
  setInterval(() => refresh(), 750);
}
function clearTraceSelection() {
  traceSelection = null;
  lineSelection = false;
  document.body.classList.remove('inspector-open');
  traceRange = null;
  selectedTraceIds.clear();
  renderTrace();
}

$('overview-clear').onclick = clearTraceSelection;
$('close-model-popover').onclick = closeModelPopover;
$('open-model-settings').onclick = () => {
  closeModelPopover();
  showSettings('models');
};
$('session-search').oninput = renderSessionTree;
$('pick-workspace').onclick = $('launch-workspace-picker').onclick = () =>
  pickWorkspace().catch((e) => notice(e.message));
$('close-workspace').onclick = () => $('workspace-dialog').close();
$('workspace-form').onsubmit = (e) => {
  e.preventDefault();
  const path = $('workspace-path').value.trim();
  if (!path) return;
  openLaunch(path);
  $('workspace-dialog').close();
};
$('input').oninput = () => {
  resizeInput($('input'));
  saveDraft();
  const disabled = sending || operation?.data?.kind === 'compaction' || !$('input').value.trim();
  $('insert-input').disabled = disabled;
  $('queue-input').disabled = disabled;
};
$('launch-input').oninput = () => resizeInput($('launch-input'));
$('jump-latest').onclick = () => {
  $('transcript').scrollTop = $('transcript').scrollHeight;
  $('jump-latest').hidden = true;
};
$('transcript').onscroll = () => {
  $('jump-latest').hidden = isNearBottom($('transcript'));
};
matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
  if (prefs.theme === 'system') applyTheme('system');
});
document.querySelectorAll('dialog').forEach((dialog) =>
  dialog.addEventListener('click', (e) => {
    if (e.target !== dialog) return;
    const r = dialog.getBoundingClientRect();
    if (
      e.clientX < r.left ||
      e.clientX > r.right ||
      e.clientY < r.top ||
      e.clientY > r.bottom
    )
      dialog.close();
  }),
);
document.addEventListener('keydown', (e) => {
  if ((e.metaKey || e.ctrlKey) && e.key === ',') {
    e.preventDefault();
    showSettings();
  }
  if (e.key === 'Escape' && !$('model-popover').hidden) closeModelPopover();
  if (e.key === 'Escape') closeCustomSelects();
  if (e.key === 'Escape') $('provider-model-options').hidden = true;
  if (
    e.key === 'Escape' &&
    page === 'trace' &&
    !document.querySelector('dialog[open]')
  )
    clearTraceSelection();
});
document.addEventListener('pointerdown', (event) => {
  if (!event.target.closest('.custom-select')) closeCustomSelects();
  if (!event.target.closest('.model-discovery'))
    $('provider-model-options').hidden = true;
  if (
    !$('model-popover').hidden &&
    !event.target.closest('#model-popover') &&
    !event.target.closest('#model-chip') &&
    !event.target.closest('#launch-model')
  )
    closeModelPopover();
});
try {
  const saved = JSON.parse(localStorage.getItem('magi-folders') || '[]');
  if (Array.isArray(saved))
    saved.forEach((path) => collapsedWorkspaces.add(path));
} catch {
  /* Ignore invalid local viewing preferences. */
}
document
  .querySelectorAll('[data-icon]')
  .forEach((el) => (el.innerHTML = icon(el.dataset.icon)));
enhanceCustomSelects();
init().catch((e) => notice(e.message));
