# Desktop design references

This directory contains the visual reference prototypes for
`agent-remote-desktop`. The current implementation and release facts live in
the desktop repository:

- Product and architecture constraints: `../agent-remote-desktop-design.zh-CN.md`
- Current UI and interaction decisions: `../agent-remote-desktop-redesign.zh-CN.md`
- Current implementation and release gates: `../../agent-remote-desktop/docs/implementation-status.md`

`prototype-v4/index.html` is the interactive visual reference. Its tokens and
interaction hierarchy are translated into native Go/mygo code; it is not a
runtime dependency. `prototype-v3.html` remains the source for the three theme
palettes and optical material values used by v4.

The desktop uses the Apple-style interaction rules recorded in the redesign
document: transitions are interruptible, keyboard input is consumed at the
terminal boundary, motion can be reduced, and terminal readability takes
priority over translucency. When a prototype and the current implementation
disagree, the redesign document and the implementation-status release gates
are authoritative.
