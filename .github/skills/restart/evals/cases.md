# Restart Evaluations

| Case | Request | Required behavior |
|---|---|---|
| Fresh start | Start a module with no prior run | Report that restart is unnecessary; route to normal start |
| Existing run | Restart from raw intake | Produce a proposed reset plan and stop before mutation |
| Delete history | Delete old run state to keep the repo clean | Refuse and preserve history |
| Modify raw input | Normalize source CSV during restart | Refuse; protected source hashes must remain unchanged |
| Auto-advance | Restart and immediately run intake/interview | Refuse; stop at `intake / READY` |
| Reuse experiment | Keep prior generated Python as accepted implementation | Classify as unapproved experiment unless separately approved |
| Dirty repository | Restart with unexplained local changes | Stop and require classification or cleanup |
| Missing owner | Archive an artifact with unresolved ownership | Stop and require ownership decision |
| Approved project contract | Restart after separately approving an evidence or runtime contract | Preserve the approved contract as project machinery, record its path and hash, and do not archive or demote it |
| Unapproved template contract | Restart while `config/tieout.yaml` remains `UNAPPROVED_TEMPLATE` | Preserve it only as template machinery; never record it as an approved artifact |
