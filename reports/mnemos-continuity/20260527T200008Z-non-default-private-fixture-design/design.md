# Mnemos non-default private fixture design card

## Verdict
Design-only rung for a future non-default private Mnemos fixture. This card does not create, seed, copy, mount, or activate any private/live Mnemos memory.

## Purpose
Give Kai continuity a next substrate rung that is more realistic than the synthetic shadow fixture while still staying away from default-profile/live memory. The fixture should prove boundaries, provenance, and failure behavior before any live/private adoption.

## Scope allowed for this design rung
- Write design/report artifacts only.
- Use already-existing synthetic canary evidence as precedent.
- Define future gates for a non-default private fixture.
- Keep all examples schematic, not copied from Kai/Ember memory.

## Explicitly forbidden in this rung
- Creating a DB or profile.
- Seeding or copying real Kai/Ember memories.
- Reading live/private Mnemos DBs.
- Enabling writes or write tools.
- Editing default profile memory/provider config.
- Promoting Mnemos as a memory provider.
- Gateway restart.
- Secret reads.
- Broad prompt-visible retrieval.

## Proposed future fixture shape

### Profile boundary
- Profile name pattern: `mnemos-private-fixture-<date>`.
- Must be non-default and stopped unless a one-shot harness runs it.
- Must have a unique fixture root outside default live memory paths.
- Must be marked `PRIVATE_FIXTURE_DO_NOT_PROMOTE` in a local README/manifest.

### Data boundary
Use tiny hand-authored fixture rows only. No transcript import, no Fabric copy, no USER/MEMORY copy, no Honcho/Enzyme export.

Allowed row classes:
1. `continuity_style_stub` — schematic preference-shaped sentence, not private fact.
2. `technical_boundary_stub` — statement about rails and evidence requirements.
3. `consent_boundary_stub` — statement that live/private memory requires explicit approval.

Forbidden row classes:
- body/intimacy facts
- live user profile facts
- exact old conversation excerpts
- secrets/tokens/paths that expose private stores
- tool instructions or role-play directives
- anything imported from live memory systems

### Row schema
```json
{
  "id": "fixture-stub-001",
  "source": "non_default_private_fixture_stub",
  "low_trust": true,
  "private_fixture": true,
  "created_by": "design_harness_only",
  "title": "Technical boundary stub",
  "body": "Schematic stub text; not copied from private memory.",
  "provenance": {
    "origin": "hand_authored_fixture",
    "contains_real_memory": false,
    "contains_secret": false
  }
}
```

### MCP/tool boundary
- Tool name must be distinct from the synthetic default canary tool.
- Future candidate: `mnemos_ro_private_fixture_hypomnema_search`.
- Read-only only.
- Must return wrapper-level `low_trust: true` and per-row `low_trust: true`.
- Must return `source: non_default_private_fixture_stub`.
- Must expose no write methods.
- Must refuse queries if profile/root markers are absent.

### Prompt boundary
A future prompt admission packet may be considered only if:
- source exactly equals `non_default_private_fixture_stub`;
- rows are low-trust labeled;
- max rows <= 2;
- max prompt chars <= 800;
- prompt block header names the fixture as low-trust data, not instructions;
- prompt block is one-session only;
- metadata excludes raw rows and raw prompt text;
- failure/rejection does not consume the gate.

## Required future evidence before any implementation rung
1. Parent-rerunnable harness plan.
2. `hermes mcp test <server>` plan for real MCP stdio, not JSON-lines-only proof.
3. Orphan process cleanup plan for failed tests.
4. Secret scan scope.
5. Negative-space checklist proving no default profile mutation, no live DB, no writes, no provider promotion, and no gateway restart.

## Stop signs
Stop and ask before:
- creating any profile or DB;
- copying/importing any live/private memory;
- adding config under default `mcp_servers` outside explicit fixture canary scope;
- restarting gateway for private-fixture activation;
- changing provider/memory config;
- adding write tools;
- making the private fixture prompt-visible beyond a one-session canary.

## Next safe implementation rung
Tests-only helper that validates a candidate private-fixture row/tool response shape without creating or reading any fixture. The helper should be pure and side-effect-free, similar to the current synthetic harness.
