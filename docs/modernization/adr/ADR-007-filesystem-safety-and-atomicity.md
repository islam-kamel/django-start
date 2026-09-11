# ADR-007: Filesystem Safety, Encoding, and Atomicity

## Status
Accepted

## Context
In Django-Start 1.1.6, filesystem operations suffered from severe safety gaps:
1. Direct file mutation without encoding declaration (`open(file)`), causing text corruption on non-UTF-8 default platforms (e.g. Windows CP1252).
2. Existing files and directories were mutated in-place without backups or conflict checks.
3. Partial generation failures left broken, half-written directories on disk with no cleanup or rollback.
4. Path operations mixed `os.sep`, string concatenation, and `pathlib.Path` inconsistently.

## Decision
1. **Non-Negotiable Invariant: Never Silently Destroy User Data**:
   - Existing projects, applications, settings, URLs, templates, dependency manifests, and configuration files must be treated as user data.
2. **Conflict Detection and `ProjectConflictError`**:
   - Pre-validate target project and application directories before executing any commands or filesystem modifications.
   - If the target directory exists and is non-empty, abort immediately by raising `ProjectConflictError`. Never silently overwrite existing files.
3. **Explicit UTF-8 Encoding**:
   - All text file read, write, and template rendering operations must explicitly specify `encoding="utf-8"`.
   - Relying on platform-default encodings is strictly forbidden.
4. **Atomic File Replacement**:
   - Configuration files and generated outputs must use atomic replacement patterns: write content to a temporary sibling file (`.tmp.XXXXXX`), flush and sync to disk, and atomically replace the destination via `os.replace`.
   - Interrupted writes or crashes will never leave truncated, partial, or corrupted destination files.
5. **Transactional Staging and Rollback**:
   - Scaffolding operations execute through transactional staging.
   - Newly created directories and resources register rollback compensations. If any step (environment creation, package installation, scaffolding, or verification) fails, registered rollback compensations clean up temporary staging resources.
   - If rollback cannot safely delete a resource, exact diagnostic information is reported to the user.
6. **Encapsulated `FileSystem` Port**:
   - Encapsulate all disk I/O behind a `FileSystem` port protocol and `LocalFileSystem` adapter. Provide a `FakeFileSystem` for hermetic in-memory testing.
7. **Strict Path Normalization**:
   - Use `pathlib.Path` exclusively for all path manipulations. Do not use string concatenation or `os.sep`.
   - Project-relative template identifiers use portable POSIX forward-slash identifiers.

## Alternatives Evaluated
- **Direct in-place file editing**: Rejected due to risk of leaving corrupted or truncated files on power loss or crash.
- **Git-based rollback only**: Rejected because target directories may not be initialized as Git repositories.
- **Silent file overwrite with warning**: Rejected because user code and data must never be overwritten without explicit request.

## Consequences
- Positive: Total data safety; platform-independent UTF-8 encoding; clean rollback on failure; robust against crashes during write; complete unit test isolation.
- Negative: Requires staging logic and rollback compensation registration.

## Migration Impact
- Handled during Phase 3 (Ports Definition) and Phase 4 (Infrastructure Adapters).
