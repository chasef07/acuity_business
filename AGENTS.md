## Product Design

### Simplicity

- Build the simplest system that fully solves the real problem.
- Write clean, elegant code that is digestible in one pass.
- Delete stale, dead, duplicated, or unnecessary code whenever it is in scope.
- Prefer boring primitives, clear names, explicit control flow, and fewer moving parts.
- Prefer one owner, one state, and one source of truth.
- New abstractions, dependencies, configuration, and compatibility paths must
  earn their complexity.

### Craft

- Care about the small things. Names, states, contracts, errors, copy, layout,
  timing, and transitions shape the product.
- Work with extreme precision and attention to detail across frontend, backend,
  operations, and the full user journey.
- Make responsibilities narrow, boundaries explicit, state transitions obvious,
  and failure modes visible and recoverable.
- Trace behavior end to end. A locally correct component is not enough when the
  complete experience is wrong.
- Prefer code and interfaces that explain themselves over work that merely looks
  clever or impressive.

### Failure Analysis and Continuous Improvement

- Capture the failing state before changing it: what failed, how to reproduce
  it, the observable evidence, and the boundary that owns it.
- Explain why it failed. Fix the cause at the owning boundary, not only the
  downstream symptom.
- Record what changed, why it improves the system, and any remaining risk.
- Compare the failing state with the new state using the same scenario and
  observable before-and-after proof.
- Turn each useful failure into a stronger invariant, test, diagnostic, or
  simpler design so the system improves continuously.
- Do not hide failures with reassuring language, silent fallbacks, or weaker
  checks. Keep failure visible and recoverable.
- Weak evidence means no-change is valid.
