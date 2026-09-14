# Source Intake Runbook

Place files without modification under the matching local `intake/` directory. Preserve original names and relative relationships where possible. Never store credentials, raw restricted data, or proprietary source in the public template branch.

```text
intake/sas/       SAS programs, includes, and macros
intake/logs/      SAS and job execution logs
intake/lst/       SAS listing or procedure output
intake/data/      approved inputs, expected outputs, fixtures, or manifests
intake/patterns/  optional approved source workspaces, ADRs, or pattern bundles
```

Start through GitHub Copilot Agent Mode:

```text
/start-migration new <MODULE-ID>

Start with intake readiness only. Invoke exactly one authorized skill and stop.
```

The intake skill may invoke `python3 scripts/project.py intake` internally to inventory and hash files. It must not execute them. Review `artifacts/evidence/intake_manifest.json`, classify missing dependencies, and approve the intake boundary before proceeding to interview or specification.
