const { test } = require('node:test');
const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const { join } = require('node:path');
const { JSDOM } = require('jsdom');
const root = join(__dirname, '..', 'mgh', 'static');
const html = readFileSync(join(root, 'index.html'), 'utf8');
const source = readFileSync(join(root, 'app.js'), 'utf8').replace(
  /\ninit\(\)\.catch[\s\S]*$/,
  '',
);
function setup(t) {
  const dom = new JSDOM(html, {
    url: 'http://localhost',
    runScripts: 'outside-only',
  });
  t.after(() => dom.window.close());
  dom.window.matchMedia = () => ({ matches: false, addEventListener() {} });
  dom.window.HTMLElement.prototype.scrollIntoView = function () {};
  dom.window.fetch = async () => ({ ok: true, json: async () => [] });
  dom.window.eval(
    source +
      '\nwindow.ui={renderChat,renderTrace,renderSessionTree,renderMarkdown,streamingMessage,refresh,loadWorkspaceInstructions,saveDraft,openLaunch,buildTrajectory,selectTraceRecord,selectTimelineRange,timelineEntries,projectTimeline,showModelPopover,selectModel};window.state=(code)=>eval(code);',
  );
  return {
    window: dom.window,
    ui: dom.window.ui,
    state: dom.window.state,
    doc: dom.window.document,
  };
}
test('all HTML ids are unique and every bound control exists', async (t) => {
  const { doc, ui, state } = setup(t);
  state(
    "sid='test';events=[{seq:1,created:1,turn:'t',kind:'error',ref:'event:1',data:{message:'error'}}];traceSelection='evt:1'",
  );
  ui.renderTrace();
  const ids = [...doc.querySelectorAll('[id]')].map((el) => el.id);
  assert.equal(new Set(ids).size, ids.length);
  for (const match of source.matchAll(/\$\(["']([^"']+)["']\)/g))
    assert.ok(doc.getElementById(match[1]), match[1]);
  await new Promise((resolve) => setImmediate(resolve));
});

test('visible selects use the app listbox instead of the native control', (t) => {
  const { doc, state } = setup(t);
  const native = doc.getElementById('permission-mode');
  const custom = native.nextElementSibling;
  assert.ok(native.classList.contains('custom-select-native'));
  assert.ok(custom.classList.contains('custom-select'));
  custom.querySelector('.custom-select-trigger').click();
  assert.equal(custom.querySelector('.custom-select-menu').hidden, false);
  custom.querySelector('[data-value="read_only"]').click();
  assert.equal(native.value, 'read_only');
  assert.equal(custom.querySelector('.custom-select-value').textContent, '只读');
  assert.equal(custom.querySelector('.custom-select-menu').hidden, true);
  assert.equal(doc.getElementById('workspace').hasAttribute('list'), false);
  assert.equal(doc.getElementById('provider-model').hasAttribute('list'), false);
  state("applyLanguage('en')");
  assert.equal(custom.querySelector('[data-value="read_only"] span').textContent, 'Read only');
  assert.equal(doc.getElementById('session-search').placeholder, 'Search chats or workspaces…');
});
test('MAGI Harness branding includes a transparent favicon', (t) => {
  const { doc } = setup(t);
  const favicon = readFileSync(join(root, 'favicon.svg'), 'utf8');
  assert.equal(doc.title, 'MAGI Harness');
  assert.equal(doc.querySelector('link[rel="icon"]').getAttribute('href'), '/static/favicon.svg');
  assert.equal(doc.querySelector('.brand-copy b').textContent, 'MAGI');
  assert.equal(doc.querySelector('.brand-copy small').textContent, 'HARNESS');
  assert.doesNotMatch(favicon, /<rect\b/);
});
test('assistant Markdown escapes executable HTML, including fenced code', (t) => {
  const { ui } = setup(t);
  const rendered = ui.renderMarkdown(
    '**hello**\n<script>alert(1)</script>\n```html\n<img src=x onerror=alert(1)>\n```',
  );
  assert.match(rendered, /<strong>hello<\/strong>/);
  assert.ok(!rendered.includes('<script>'));
  assert.ok(!rendered.includes('<img'));
  assert.match(rendered, /&lt;img/);
});

test('assistant replies start directly with their content', (t) => {
  const { ui, state, doc } = setup(t);
  state("sid='test';events=[{seq:1,kind:'message',data:{role:'assistant',content:'Hello'}}]");
  ui.renderChat();
  assert.equal(doc.querySelector('.message.assistant .role'), null);
  assert.equal(doc.querySelector('.message.assistant .message-body').textContent, 'Hello');
});

test('tool calls show a compact preview and reveal formatted arguments on demand', (t) => {
  const { ui, state, doc } = setup(t);
  state(
    `sid='test';events=[{seq:1,kind:'message',data:{role:'assistant',tool_calls:[{function:{name:'write',arguments:'{"file_path":"README.md","content":"hello"}'}}]}}]`,
  );
  ui.renderChat();
  const tool = doc.querySelector('.tool-use');
  assert.ok(tool);
  assert.equal(tool.open, false);
  assert.match(tool.querySelector('summary').textContent, /write.*README\.md/);
  assert.match(tool.querySelector('pre').textContent, /\n  "file_path"/);
});

test('an expanded tool call stays expanded across polling renders', (t) => {
  const { ui, state, doc } = setup(t);
  state(
    `sid='test';events=[{seq:7,kind:'message',data:{role:'assistant',tool_calls:[{function:{name:'read',arguments:'{"file_path":"README.md"}'}}]}}]`,
  );
  ui.renderChat();
  doc.querySelector('.tool-use').open = true;
  ui.renderChat();
  assert.equal(doc.querySelector('.tool-use').open, true);
});

test('failed requests do not leave a streaming ghost', (t) => {
  const { ui, state } = setup(t);
  state("events=[{seq:1,kind:'request',turn:'t',data:{}},{seq:2,kind:'delta',turn:'t',data:{request_seq:1,field:'content',text:'partial'}},{seq:3,kind:'request_error',turn:'t',data:{request_seq:1}}]");
  assert.equal(ui.streamingMessage(), null);
});

test('running chat exposes instruction queues and hides settled items', (t) => {
  const {ui, state, doc} = setup(t);
  state("sid='test';running=true;events=[{seq:1,kind:'queue_enqueued',data:{id:'pending',queue:'steer',message:{content:'inspect first'}}},{seq:2,kind:'queue_enqueued',data:{id:'settled',queue:'follow_up',message:{content:'old'}}},{seq:3,kind:'queue_consumed',data:{id:'settled'}}]");
  ui.renderChat();
  assert.equal(doc.getElementById('send').disabled, false);
  assert.equal(doc.getElementById('input-mode').hidden, true);
  assert.equal(doc.getElementById('send').getAttribute('aria-label'), '停止运行');
  assert.ok(doc.querySelector('#send svg[data-icon="stop"]'));
  assert.equal(doc.getElementById('insert-input').hidden, false);
  assert.equal(doc.getElementById('queue-input').hidden, false);
  assert.equal(doc.querySelectorAll('.queued-input').length, 1);
  assert.match(doc.getElementById('queued-inputs').textContent, /inspect first/);
  assert.equal(doc.getElementById('compact-context').disabled, true);
});

test('composer routes Enter to queue, Alt Enter to steer, and primary to stop', async (t) => {
  const {ui, state, doc, window} = setup(t);
  state("sid='test';running=true;events=[]");
  ui.renderChat();
  const calls = [];
  window.fetch = async (url, options) => {
    calls.push([url, options?.method]);
    if (options?.method === 'POST') return {ok:false, json:async()=>({detail:'test refusal'})};
    return {ok:true, json:async()=>({events:[],running:true})};
  };
  doc.getElementById('input').value = 'inspect first';
  doc.getElementById('input').dispatchEvent(new window.KeyboardEvent('keydown', {key:'Enter',bubbles:true,cancelable:true}));
  await new Promise(resolve => setImmediate(resolve));
  assert.ok(calls.some(([url]) => url.endsWith('/queue/follow_up')));
  doc.getElementById('input').dispatchEvent(new window.KeyboardEvent('keydown', {key:'Enter',altKey:true,bubbles:true,cancelable:true}));
  await new Promise(resolve => setImmediate(resolve));
  assert.ok(calls.some(([url]) => url.endsWith('/queue/steer')));
  doc.getElementById('send').click();
  await new Promise(resolve => setImmediate(resolve));
  assert.ok(calls.some(([url]) => url.endsWith('/cancel')));
  assert.equal(doc.getElementById('input').value, 'inspect first');
});
test('in-flight content is reconstructed, then removed when completion arrives', (t) => {
  const { ui, state, doc } = setup(t);
  state(
    "events=[{seq:1,turn:'t1',kind:'request',data:{}},{seq:2,kind:'delta',data:{request_seq:1,field:'content',text:'Hello '}},{seq:3,kind:'delta',data:{request_seq:1,field:'content',text:'world'}}];running=true",
  );
  assert.equal(ui.streamingMessage().content, 'Hello world');
  ui.renderChat();
  assert.match(doc.querySelector('.streaming').textContent, /Hello world/);
  state("events.push({seq:4,kind:'response',data:{request_seq:1}})");
  assert.equal(ui.streamingMessage(), null);
});
test('polling preserves an unsaved message edit and its caret', (t) => {
  const { ui, state, doc } = setup(t);
  state(
    "events=[{seq:1,kind:'message',data:{role:'user',content:'original'}}];editSeq=1",
  );
  ui.renderChat();
  const editor = doc.querySelector('.message-editor');
  editor.value = 'unsaved change';
  editor.focus();
  editor.setSelectionRange(3, 7);
  ui.renderChat();
  const next = doc.querySelector('.message-editor');
  assert.equal(next.value, 'unsaved change');
  assert.equal(next.selectionStart, 3);
  assert.equal(next.selectionEnd, 7);
});
test('a poll from the previous session cannot overwrite the current session', async (t) => {
  const { ui, state, window } = setup(t);
  let resolve;
  window.fetch = () =>
    new Promise((done) => {
      resolve = done;
    });
  state("sid='old';events=[]");
  const pending = ui.refresh();
  state(
    "sid='new';sessionGeneration++;events=[{seq:99,kind:'message',data:{role:'user',content:'new'}}]",
  );
  resolve({
    ok: true,
    json: async () => ({ events: [{ seq: 1 }], running: true }),
  });
  await pending;
  assert.equal(state('events[0].seq'), 99);
  assert.equal(state('running'), false);
});
test('workspace search includes paths and collapsed groups can be searched', (t) => {
  const { ui, state, doc } = setup(t);
  state(
    "config.default_workspace='/repo';sessionsCache=[{id:'a',title:'First',config:{workspace:'/repo/project'}},{id:'b',title:'Second',config:{workspace:'/other'}}];collapsedWorkspaces.add('/repo/project')",
  );
  ui.renderSessionTree();
  assert.equal(
    doc.querySelector('[data-fold-workspace]').getAttribute('aria-expanded'),
    'false',
  );
  doc.getElementById('session-search').value = 'PROJECT';
  ui.renderSessionTree();
  assert.ok(doc.querySelector('[data-session="a"]'));
  assert.ok(!doc.querySelector('[data-session="b"]'));
  assert.equal(
    doc.querySelector('[data-fold-workspace]').getAttribute('aria-expanded'),
    'true',
  );
});
test('trace filtering preserves original turn numbers', (t) => {
  const { ui, state, doc } = setup(t);
  state(
    "events=[{seq:1,created:1,turn:'a',kind:'message',data:{role:'user',content:'first'}},{seq:2,created:2,turn:'b',kind:'error',data:{message:'failure'}}]",
  );
  doc.getElementById('trace-search').value = 'failure';
  ui.renderTrace();
  assert.match(doc.querySelector('.ledger-turn').textContent, /Turn 2/);
  assert.equal(doc.querySelectorAll('.trajectory-item').length, 1);
});
test('opening a new chat preserves the previous session draft and attachments', (t) => {
  const { ui, state, doc } = setup(t);
  state(
    "sid='draft';pendingAttachments=[{name:'notes.txt',text:'notes'}];config.default_workspace='/repo'",
  );
  doc.getElementById('input').value = 'unfinished';
  ui.openLaunch('/other');
  assert.equal(state("drafts.get('draft').text"), 'unfinished');
  assert.equal(state("drafts.get('draft').attachments[0].name"), 'notes.txt');
  assert.equal(state('sid'), null);
});
test('failed instruction reads cannot authorize overwriting MAGI.md', async (t) => {
  const { ui, state, window, doc } = setup(t);
  window.fetch = async () => ({
    ok: false,
    json: async () => ({ detail: 'Directory unavailable' }),
  });
  await ui.loadWorkspaceInstructions('/missing');
  assert.equal(state('loadedInstructionsWorkspace'), null);
  assert.equal(doc.getElementById('magi-content').disabled, true);
  assert.match(
    doc.getElementById('context-status').textContent,
    /Directory unavailable/,
  );
});
test('re-rendering the same trace selection retains inspector DOM and scroll', (t) => {
  const { ui, state, doc } = setup(t);
  state(
    "sid='a';events=[{seq:1,created:1,turn:'t',kind:'error',data:{message:'oops'}}];traceSelection='evt:1'",
  );
  ui.renderTrace();
  const detail = doc.querySelector('#trace-inspector .detail-block');
  ui.renderTrace();
  assert.equal(doc.querySelector('#trace-inspector .detail-block'), detail);
});
test('a double submit sends one message and retains text on failure', async (t) => {
  const { state, window, doc } = setup(t);
  state("sid='a';running=false");
  doc.getElementById('input').value = 'keep my draft';
  let resolve,
    count = 0;
  window.fetch = () => {
    count++;
    return new Promise((done) => {
      resolve = done;
    });
  };
  const first = doc
    .getElementById('composer')
    .onsubmit({ preventDefault() {} });
  await doc.getElementById('composer').onsubmit({ preventDefault() {} });
  assert.equal(count, 1);
  resolve({ ok: false, json: async () => ({ detail: 'Request failed' }) });
  await first;
  assert.equal(doc.getElementById('input').value, 'keep my draft');
  assert.equal(doc.getElementById('send').disabled, false);
});
test('older instruction fetches cannot replace the newly selected workspace', async (t) => {
  const { ui, window, doc, state } = setup(t);
  let resolve;
  window.fetch = () =>
    new Promise((done) => {
      resolve = done;
    });
  const old = ui.loadWorkspaceInstructions('/old');
  window.fetch = async () => ({
    ok: true,
    json: async () => ({ workspace: '/new', content: 'new instructions' }),
  });
  await ui.loadWorkspaceInstructions('/new');
  resolve({
    ok: true,
    json: async () => ({ workspace: '/old', content: 'old instructions' }),
  });
  await old;
  assert.equal(doc.getElementById('magi-content').value, 'new instructions');
  assert.equal(state('loadedInstructionsWorkspace'), '/new');
});
test('a provider request owns reasoning and tool returns until the next Step', (t) => {
  const { state, ui } = setup(t);
  state(`events=[
    {seq:1,turn:'t',created:1,kind:'message',data:{role:'user',content:'hello'}},
    {seq:2,turn:'t',created:2,kind:'request',data:{zones:{stable:[{budget_units:20,message:{role:'system',content:'rules'}}]}}},
    {seq:3,turn:'t',created:3,kind:'message',data:{role:'assistant',reasoning_content:'think',tool_calls:[{id:'c'}]}},
    {seq:4,turn:'t',created:4,kind:'tool_start',data:{id:'c',function:{name:'read',arguments:'{}'}}},
    {seq:5,turn:'t',created:5,kind:'message',data:{role:'tool',tool_call_id:'c',content:'result'}},
    {seq:6,turn:'t',created:6,kind:'request',data:{}},
    {seq:7,turn:'t',created:7,kind:'message',data:{role:'assistant',content:'done'}}]`);
  const records = ui.buildTrajectory();
  assert.equal(records.find((r) => r.kind === 'reasoning').step, 1);
  const tool = records.find((r) => r.kind === 'tool_start');
  assert.equal(tool.step, 1);
  assert.equal(tool.result.data.content, 'result');
  assert.equal(records.find((r) => r.seq === 7).step, 2);
  assert.ok(
    !records.some((r) => r.kind === 'context' || r.kind === 'tool_result'),
  );
});
test('Step inspector provides separate context/output/tools tabs and cache metrics', (t) => {
  const { state, ui, doc } = setup(t);
  state(
    `events=[{seq:1,turn:'t',kind:'request',created:1,data:{zones:{stable:[{budget_units:25}],hot:[{budget_units:75}]},payload:{model:'test'}}},{seq:2,turn:'t',kind:'response',created:2,data:{request_seq:1,latency_ms:1000,usage:{input_tokens:100,cache_read_tokens:50},message:{content:'hello'}}}];traceSelection='evt:1'`,
  );
  ui.renderTrace();
  assert.equal(doc.querySelectorAll('.inspector-tabs button').length, 5);
  assert.match(
    doc.querySelector('.inspector-body').textContent,
    /Cache 50 · 50%/,
  );
  assert.equal(doc.querySelector('.inspector-body .zone-hot').style.width, '75%');
  assert.equal(doc.querySelector('.step-anchor'), null);
  assert.equal(doc.getElementById('zone-overview'), null);
  doc.querySelector('[data-inspector-tab="output"]').click();
  assert.match(doc.querySelector('.inspector-body').textContent, /hello/);
});
test('tool details update when the result arrives after selection', (t) => {
  const { state, ui, doc } = setup(t);
  state(
    `events=[{seq:1,turn:'t',kind:'request',created:1,data:{}},{seq:2,turn:'t',kind:'tool_start',created:2,data:{id:'c',function:{name:'read',arguments:'{}'}}}];traceSelection='evt:2'`,
  );
  ui.renderTrace();
  assert.match(
    doc.querySelector('.inspector-body').textContent,
    /等待工具返回/,
  );
  state(
    `events.push({seq:3,turn:'t',kind:'message',created:3,data:{role:'tool',tool_call_id:'c',content:'loaded'}})`,
  );
  ui.renderTrace();
  assert.match(doc.querySelector('.inspector-body').textContent, /loaded/);
});
test('static system messages and tool schemas precede the first Turn', (t) => {
  const { state, ui, doc } = setup(t);
  state(
    `events=[{seq:1,turn:'a',kind:'message',created:1,data:{role:'user',content:'hello'}},{seq:2,turn:'a',kind:'request',created:2,data:{payload:{messages:[{role:'system',content:'actual system prompt'}],tools:[{function:{name:'read_file',parameters:{type:'object'}}}]}}}]`,
  );
  const records = ui.buildTrajectory();
  assert.equal(records[0].label, '系统');
  assert.equal(records[0].data[0].content, 'actual system prompt');
  assert.equal(records[1].label, '工具');
  assert.equal(records[1].data[0].function.name, 'read_file');
  assert.equal(records[2].label, '用户');
  ui.renderTrace();
  const staticRows = [...doc.querySelectorAll('.static-record')];
  assert.equal(staticRows.length, 2);
  assert.equal(
    staticRows[0].querySelector('.trajectory-kind > span').textContent,
    '系统',
  );
  assert.ok(staticRows[0].querySelector('[data-icon="settings"]'));
  assert.equal(
    staticRows[1].querySelector('.trajectory-kind > span').textContent,
    '工具',
  );
  assert.ok(staticRows[1].querySelector('[data-icon="wrench"]'));
});
test('Switch overview summarizes transitions without dumping retained contents', (t) => {
  const { state, ui, doc } = setup(t);
  state(
    `events=[{seq:1,kind:'stage',created:1,data:{number:2,reason:'budget',moved_to_cold:['t1'],moved_to_stubs:['b1'],retained_hot:['t2'],cold:[{content:'verbose hidden payload'}]}}];traceSelection='evt:1'`,
  );
  ui.renderTrace();
  const text = doc.querySelector('.inspector-body').textContent;
  assert.match(text, /Stage 1 → 2/);
  assert.match(text, /Hot → Cold/);
  assert.ok(!text.includes('verbose hidden payload'));
});
test('timeline omits Step blocks and selects visible event intervals', (t) => {
  const { state, ui, doc } = setup(t);
  state(
    `events=[{seq:1,turn:'a',kind:'request',created:1,data:{}},{seq:2,turn:'a',kind:'response',created:10,data:{request_seq:1}},{seq:3,turn:'a',kind:'tool_start',created:11,data:{id:'c',function:{name:'read',arguments:'{}'}}},{seq:4,turn:'a',kind:'message',created:13,data:{role:'tool',tool_call_id:'c',content:'result'}}]`,
  );
  state("timelineMode='duration'");
  ui.renderTrace();
  ui.selectTimelineRange(12, 12);
  assert.equal(state("selectedTraceIds.has('evt:1')"), false);
  assert.equal(state("selectedTraceIds.has('evt:3')"), true);
  assert.equal(doc.getElementById('overview-selection').hidden, false);
  assert.equal(doc.querySelector('.overview-event.request'), null);
  assert.match(doc.querySelector('.overview-event.tool_start').style.width, /%/);
  doc.getElementById('overview-clear').click();
  assert.equal(state('traceRange'), null);
});
test('timeline reasoning opens its inspector without rendering a Step block', (t) => {
  const { state, ui, doc } = setup(t);
  state(
    `events=[{seq:1,turn:'a',kind:'message',created:1,data:{role:'user',content:'hello'}},{seq:2,turn:'a',kind:'request',created:2,data:{}},{seq:3,turn:'a',kind:'delta',created:3,data:{request_seq:2,text:'a',field:'content'}},{seq:4,turn:'a',kind:'response',created:5,data:{request_seq:2,latency_ms:3000}},{seq:5,turn:'a',kind:'message',created:5,data:{role:'assistant',reasoning_content:'think',content:'done'}}]`,
  );
  state("timelineMode='duration'");
  ui.renderTrace();
  assert.equal(doc.querySelector('.overview-event.request'), null);
  assert.equal(doc.querySelector('.step-anchor'), null);
  const point = doc.querySelector('[data-timeline-id="reason:5"]');
  point.click();
  assert.equal(state('traceSelection'), 'reason:5');
  assert.equal(doc.getElementById('trace-inspector').hidden, false);
});

test('Traceline is the default equal-width projection and Timeline uses duration', (t) => {
  const { state, ui, doc } = setup(t);
  state(
    `events=[{seq:1,turn:'a',kind:'message',created:1,data:{role:'user',content:'hello'}},{seq:2,turn:'a',kind:'request',created:2,data:{}},{seq:3,turn:'a',kind:'response',created:3,data:{request_seq:2}},{seq:4,turn:'a',kind:'message',created:3,data:{role:'assistant',reasoning_content:'think',content:'done'}},{seq:5,turn:'a',kind:'tool_start',created:4,data:{id:'c',function:{name:'read'}}},{seq:6,turn:'a',kind:'message',created:9,data:{role:'tool',tool_call_id:'c',content:'ok'}}]`,
  );
  ui.renderTrace();
  assert.equal(state('timelineMode'), 'sequence');
  const equal = [...doc.querySelectorAll('.overview-event')].map(
    (item) => item.style.width,
  );
  assert.equal(equal[0], equal[1]);
  doc.getElementById('timeline-mode').click();
  const timed = [...doc.querySelectorAll('.overview-event.user, .overview-event.tool_start')].map(
    (item) => item.style.width,
  );
  assert.notEqual(timed[0], timed[1]);
  assert.equal(
    doc.getElementById('timeline-mode').getAttribute('aria-pressed'),
    'true',
  );
});

test('wheel zoom narrows the active Traceline viewport', (t) => {
  const { state, ui, doc, window } = setup(t);
  state(
    `events=Array.from({length:8},(_,index)=>({seq:index+1,turn:'t'+index,kind:'message',created:index+1,data:{role:'user',content:'m'+index}}))`,
  );
  ui.renderTrace();
  const before = state('timelineViewport.end-timelineViewport.start');
  doc
    .getElementById('overview-track')
    .dispatchEvent(
      new window.WheelEvent('wheel', {
        deltaY: -300,
        clientX: 1,
        bubbles: true,
      }),
    );
  const after = state('timelineViewport.end-timelineViewport.start');
  assert.ok(after < before);
});

test('sidebar conversation rows contain titles without conversation icons', (t) => {
  const { state, ui, doc } = setup(t);
  state(
    `config.default_workspace='/repo';sessionsCache=[{id:'a',title:'Plain title',config:{workspace:'/repo'}}]`,
  );
  ui.renderSessionTree();
  const row = doc.querySelector('.session-item');
  assert.equal(row.querySelector('.ui-icon'), null);
  assert.equal(row.textContent.trim(), 'Plain title');
});

test('composer model picker discovers and applies a model in place', async (t) => {
  const { ui, doc, window } = setup(t);
  const calls = [];
  window.fetch = async (url, options = {}) => {
    calls.push([url, options.method || 'GET']);
    if (url.endsWith('/settings/provider')) {
      if (options.method === 'PUT')
        return { ok: true, json: async () => ({ model: 'next-model' }) };
      return {
        ok: true,
        json: async () => ({
          binding: 'ollama',
          model: 'old-model',
          host: 'http://localhost:11434/v1',
          timeout: 120,
        }),
      };
    }
    if (url.endsWith('/settings/provider/discover'))
      return {
        ok: true,
        json: async () => ({ models: ['old-model', 'next-model'] }),
      };
    if (url.endsWith('/config'))
      return {
        ok: true,
        json: async () => ({
          binding: 'ollama',
          model: 'next-model',
          version: '0.1.0',
        }),
      };
    throw new Error(url);
  };
  await ui.showModelPopover(doc.getElementById('model-chip'));
  assert.equal(doc.getElementById('app-settings-dialog').open, false);
  assert.equal(doc.querySelectorAll('[data-model-option]').length, 2);
  await ui.selectModel('next-model');
  assert.equal(doc.getElementById('model').textContent, 'next-model');
  assert.equal(doc.getElementById('model-popover').hidden, true);
  assert.ok(
    calls.some(
      ([url, method]) => url.endsWith('/settings/provider') && method === 'PUT',
    ),
  );
});
