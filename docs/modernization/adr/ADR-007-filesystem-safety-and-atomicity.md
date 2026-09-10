# ADR-007: Filesystem Safety, Encoding, and Atomicity

## Status
Accepted

## Context
In Django-Start 1.1.6, filesystem operations suffered from severe safety gaps:
1. Direct file mutation without encoding declaration (`open(file)`), causing text corruption on non-UTF-8 default platforms (e.g. Windows CP1252).
2. Existing files and directories were mutated in-place without backups.
3. Partial generation failures left broken, half-written directories on disk with no cleanup or rollback.
4. Path operations mixed `os.sep`, string concatenation, and `pathlib.Path` inconsistently.

## Decision
1. Establish the non-negotiable invariant: **Never silently destroy user data**.
2. Encapsulate all disk I/O in a `FileSystem` port and `LocalFileSystem` adapter.
3. Explicitly specify `encoding="utf-8"` on every file read and write operation.
4. Use `pathlib.Path` exclusively for path manipulation.
5. Implement atomic writes for modified configuration files (write to `.tmp` file, flush, and replace atomically via `os.replace`).
6. Pre-validate project and application directories before execution. If target directory exists and contains user files, abort immediately with `ProjectConflictError`.
7. Implement a transactional staging and rollback mechanism: if scaffolding fails midway, clean up safely created temporary staging files or report exact status.

## Alternatives Evaluated
- **Direct in-place file editing**: Rejected due to risk of leaving corrupted/truncated files on power loss or crash.
- **Git-based rollback only**: Rejected because target directories may not be initialized as Git repositories.

## Consequences
- Positive: Total data safety; platform-independent UTF-8 encoding; clean rollback on failure; robust against crashes during write.
- Negative: Requires staging logic and rollback compensation registration.

## Migration Impact
- Handled during Phase 3 (Ports Definition) and Phase 4 (Infrastructure Adapters).
