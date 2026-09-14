# Stage Contract

Every prompt invocation routes through `orchestrate` and may invoke exactly one state-authorized specialist skill. The skill must record the module, run, act, input artifact versions and hashes, assumptions, mutable paths, protected paths, ordered actions, deterministic verification, output artifact, limitations, gate result, and stop reason. A successful command without the required canonical artifact is not a completed stage.

## Required gate values

```text
PASS | FAIL | BLOCKED
```

`PASS` permits only the transition defined in `config/workflow.yaml`. `FAIL` or `BLOCKED` stops normal progression and may open a bounded recovery loop. A human gate always stops execution regardless of technical result.

## Standard Stage Result

Every prompt response must end with this complete structure:

~~~markdown
## Stage Result

**Module:** <module-id>
**Run:** <run-id>
**Act:** <act-id>
**Skill invoked:** <skill-name or None>
**Input artifact:** <path + version/hash, or None with reason>
**Output artifact:** <path + version/hash, or None with reason>
**Gate:** PASS | FAIL | BLOCKED
**Human approval required:** Yes | No
**Files changed:** <paths or None>
**Protected files unchanged:** Yes | No
**Next permitted command:** <one slash command or None>
**Next action:** <one plain-language sentence explaining what the user must review, decide, supply, or approve>
**Copy/paste next:**
```text
<complete next Copilot message, including command, artifact paths and hashes, approval scope, one permitted skill, and stop point>
```
**Stop reason:** <reason>
~~~

## Copy-ready next-message rules

The `Copy/paste next` block is mandatory. It must be executable as the user's next Copilot Agent Mode message without requiring the user to invent workflow language.

1. Use actual module IDs, run IDs, repository-relative artifact paths, SHA-256 values, and next skill names. Do not emit placeholders when those values are available.
2. Keep `Next permitted command` machine-readable and short. Put the complete bounded instruction in `Copy/paste next`.
3. At a human approval gate, include the exact artifacts and hashes being approved, state that approval is limited to the named gate, authorize only the next permitted skill, and require a stop before any later skill.
4. If a required artifact hash is missing, do not generate approval wording. The next message must request the exact path and hash without advancing or modifying files.
5. For `FAIL` or `BLOCKED`, provide the exact recovery entry command and direct it to the earliest failed owning gate. Do not suggest normal progression.
6. For review or repair integration, identify the exact review artifact or commit hash and keep integration and stage retry in separate messages.
7. If user input is genuinely required, provide a concise choice or response template instead of inventing the answer.
8. At a terminal state, use `None` and state that no command is required.
9. A generated approval message is only a proposal. Approval occurs only if the human reviews the referenced artifact and sends the message.

## Standard next-message patterns

| Situation | `Next permitted command` | Required `Copy/paste next` content |
|---|---|---|
| Technical `PASS`, no human gate | `/run-next-stage <module-id>` | Continue the same run, invoke exactly the named next skill, create and verify one artifact, then stop. |
| Technical `PASS`, human gate | `/run-next-stage <module-id>` | Approve exact artifact paths and hashes for only the named gate; invoke exactly one named next skill; stop at the next gate. |
| Output hash missing | `None` | Request exact paths and SHA-256 values; forbid file changes and stage advancement. |
| `FAIL` or `BLOCKED` with raw evidence | `/analyze-failure <module-id>` | Invoke only `ingest`; normalize evidence and stop. |
| `FAIL` or `BLOCKED` with normalized evidence | `/analyze-failure <module-id>` | Invoke only `diagnose`; identify one hypothesis and owning layer, then stop. |
| Approved repair ready | `/run-next-stage <module-id>` | Invoke only `repair` in an isolated worktree; protect requirements and evidence; stop for independent review. |
| Independent review required | `/review-evidence <module-id>` | Invoke only `review`; rerun recorded checks; do not repair or integrate; stop with review artifact and hash. |
| Terminal workflow | `None` | State that no command is required and name the terminal status. |

## Approval example

```text
/run-next-stage <MODULE-ID>

I approve <artifact-path> at SHA-256 <artifact-hash> for <gate-name> only.
Record this approval in run <run-id>. Invoke exactly <next-skill>, create and verify its named artifact, and stop at the next gate. Do not invoke any later skill.
```

The skill may invoke approved deterministic tools internally. The user is not required to run implementation helpers manually.
