# Mnemos continuity ladder — next rungs

1. **Parent-rerunnable one-session smoke harness**
   - Allowed: mocked/synthetic MCP response, system prompt helper invocation, metadata-only report.
   - Forbidden: live/private DB, writes, provider promotion, gateway restart, secrets.
   - Gate: prompt appears once, second build omits it, metadata has no raw row/prompt text.

2. **Non-default private fixture design only**
   - Allowed: design doc for a private-fixture shape and access rails.
   - Forbidden: copying live Kai/Mnemos memory, creating/seeding private DB, default-profile activation.

3. **Future stop sign**
   - Any live/private Mnemos memory, writes, provider promotion, or broad prompt-visible retrieval requires explicit approval.
