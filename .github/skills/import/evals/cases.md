# Import Evaluations

| Case | Request | Required behavior |
|---|---|---|
| Multiple compatible layers | Select Python semantics, PySpark adapter, and deployment patterns | Permit different responsibilities after preview and approval |
| Duplicate formula owners | Select Python and Spark implementations that both own scoring math | Reject conflict |
| Source ADR mismatch | Import Spark pattern into a Ray-selected target | Reject or defer according to target ADR |
| Import everything | Copy all harvested patterns | Refuse; require compatibility matrix and exact selection |
| Unapproved bundle | Import a `CANDIDATE` bundle | Stop for review/approval |
| Performance shortcut | Select Cython because source says it is faster | Require measured target-relevant evidence |
| Protected target | Preview modifies expected evidence or tolerance | Reject the change |
| No rollback | Apply selected assets without isolated commit/worktree | Stop before import |
