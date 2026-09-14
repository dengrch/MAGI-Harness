# Web experience contract

Reference: the repository's `Linear-ui-design/DESIGN.md`, plus DSH
`ui-conversation` InputBar / QueueDock / ConversationRoot behavior. This is an
original local static client that applies Linear's visual principles; it is not
a port of Linear or DSH components and does not claim pixel-identical rendering.

## Visual hierarchy

- Inter-first system UI stack with `cv01` / `ss03`, plus explicit PingFang SC /
  Microsoft YaHei fallbacks.
- Dark-native luminance hierarchy: `#08090a` canvas, `#0d0e0f` navigation,
  `#111213` functional surfaces, and whisper-thin translucent borders.
- Indigo is reserved for selection, execution state, focus and primary actions.
- Conversation text: 16px; input: 16px / 24px; toolbar selectors: 13px / 20px.
- Conversation content: 748px maximum; composer: 780px maximum, 16px side clearance.
- Secondary controls: 28px; primary: 34px circle with a 16px SVG.
- Send uses DSH's blue accent; stop uses the same primary seat, not a red text button.
- Queue items sit above the draft; status and keyboard hints sit below the card.
- Actions use SVG, accessible names and hover titles. Text remains for content,
  settings choices and explanations, rather than competing action labels.

## Interaction states

| State | Primary button | Enter | Alt+Enter |
|---|---|---|---|
| Idle | Send arrow | Send | Send |
| Running | Stop square | Queue after this run | Insert at checkpoint |
| Suspended | Resume triangle | Queue, requires resume | Insert, requires resume |
| Compaction | Stop square while running | Disabled submission | Disabled submission |

Shift+Enter inserts a newline; IME composition does not submit. Running/suspended
sessions expose secondary insert and queue icons. Empty drafts disable these actions.
Failed submissions retain the draft. Stop means cancellation, not reversible pause;
it does not roll back external side effects. Insertion is checkpoint-based, not
preemption of a currently executing tool.

The underlying next_run queue API remains available, but is not a third permanent
toolbar control. Queue cancellation uses the close icon. Compaction uses a secondary
compress icon and can invoke a paid provider; its tooltip states that it calls a model.

## Verification

jsdom tests cover icon states, queue projection, keyboard dispatch, cancellation,
draft preservation and existing interactions. The launch, conversation, trajectory,
sidebar-expanded narrow layout, and settings dialog were also inspected in the local
browser at the application's real URL. Native tooltip wording remains covered by the
existing DOM contract.
