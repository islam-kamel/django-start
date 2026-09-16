"""Controlled template scaffold engine for Django-Start 2.0.

Deterministic renderer that transforms immutable inputs into an
immutable ``ScaffoldPlan``. Performs no filesystem writes, no
subprocess execution, no network access, and no randomness.

Template tokens use the ``__DJSTART_*__`` namespace to avoid
colliding with Django's ``{{ }}`` template syntax.
"""

import re
from pathlib import PurePosixPath
from typing import final

from django_start.domain.config import AppConfig
from django_start.domain.errors import ConfigurationError
from django_start.domain.recipes import (
    RecipeTemplate,
    RenderedFile,
    ScaffoldPlan,
    ScaffoldRequest,
)
from django_start.recipes.compatibility import (
    validate_recipe_compatibility,
)

# --- Token Registry ---

# The complete set of recognized __DJSTART_*__ tokens.
# Unknown tokens cause rendering failure.
_REGISTERED_TOKENS: frozenset[str] = frozenset({
    "__DJSTART_PROJECT_NAME__",
    "__DJSTART_SECRET_KEY_PY__",
    "__DJSTART_APP_NAME__",
    "__DJSTART_APP_CONFIG_CLASS__",
    "__DJSTART_INSTALLED_APPS__",
    "__DJSTART_APP_URLPATTERNS__",
    "__DJSTART_DJANGO_VERSION_COMMENT__",
    "__DJSTART_DOCS_VERSION__",
})

# Pattern to find all __DJSTART_*__ tokens in content
_TOKEN_PATTERN = re.compile(r"__DJSTART_[A-Z_]+__")

# Engine-owned output paths that recipes must not collide with
_ENGINE_OWNED_PATHS: frozenset[PurePosixPath] = frozenset({
    PurePosixPath("requirements.txt"),
})

# Unsafe path components
_UNSAFE_COMPONENTS: frozenset[str] = frozenset({
    "..", ".venv", ".git",
})


def _app_name_to_config_class(app_name: str) -> str:
    """Convert an app package name to its AppConfig class name.

    Deterministic conversion: split on underscores, title-case
    each segment, join, and append ``Config``.

    Examples:
        ``core`` -> ``CoreConfig``
        ``user_accounts`` -> ``UserAccountsConfig``
        ``my_api_v2`` -> ``MyApiV2Config``
    """
    parts = app_name.split("_")
    class_name = "".join(part.capitalize() for part in parts)
    return f"{class_name}Config"


# --- Public Engine ---


@final
class ControlledTemplateScaffoldEngine:
    """Deterministic scaffold renderer.

    Receives an immutable ``ScaffoldRequest`` and produces an
    immutable ``ScaffoldPlan``. No external I/O once it receives
    the request.

    Composition layers (in precedence order):
    1. Framework baseline (lowest precedence)
    2. Profile templates (may intentionally replace baseline)
    3. Per-app expansion (added for each AppConfig)
    4. Engine-owned files (requirements.txt)

    Duplicate paths within the same layer or between app
    expansions raise ``ConfigurationError``. Collisions with
    engine-owned paths raise ``ConfigurationError``.
    """

    def render(
        self, request: ScaffoldRequest
    ) -> ScaffoldPlan:
        """Render a scaffold plan from a request.

        Args:
            request: Immutable scaffold request with all
                explicit inputs.

        Returns:
            Immutable ``ScaffoldPlan`` with rendered files
            sorted by POSIX path.

        Raises:
            ConfigurationError: On duplicate paths, unsafe paths,
                or unresolved tokens.
            UnsupportedVersionError: On version incompatibility.
        """
        # 1. Validate recipe compatibility
        validate_recipe_compatibility(
            metadata=request.recipe.metadata,
            host_python_version=request.host_python_version,
            release=request.release,
            django_start_version=request.django_start_version,
        )

        # 2. Construct render context
        context = self._build_context(request)

        # 3. Render templates (baseline + profile already merged)
        rendered_files: list[RenderedFile] = []

        # Separate project-level and app-scoped templates
        project_templates: list[RecipeTemplate] = []
        app_templates: list[RecipeTemplate] = []
        for tmpl in request.recipe.templates:
            if tmpl.is_app_scoped:
                app_templates.append(tmpl)
            else:
                project_templates.append(tmpl)

        # 3a. Render project-level templates
        for tmpl in project_templates:
            rendered = self._render_template(
                tmpl, context
            )
            rendered_files.append(rendered)

        # 3b. Expand app-scoped templates for each app
        for app in request.config.apps:
            app_context = {
                **context,
                "__DJSTART_APP_NAME__": app.name,
                "__DJSTART_APP_CONFIG_CLASS__": (
                    _app_name_to_config_class(app.name)
                ),
            }
            for tmpl in app_templates:
                rendered = self._render_template(
                    tmpl, app_context
                )
                rendered_files.append(rendered)

        # 4. Build requirements.txt
        requirements = self._build_requirements(request)
        req_content = "\n".join(requirements) + "\n"
        rendered_files.append(
            RenderedFile(
                relative_path=PurePosixPath(
                    "requirements.txt"
                ),
                content=req_content,
            )
        )

        # 5. Validate all paths
        for rf in rendered_files:
            _validate_rendered_path(rf.relative_path)

        # 6. Detect duplicate paths
        _detect_duplicates(rendered_files)

        # 7. Sort deterministically and return
        sorted_files = tuple(
            sorted(
                rendered_files,
                key=lambda f: str(f.relative_path),
            )
        )

        return ScaffoldPlan(
            files=sorted_files,
            requirements=requirements,
        )

    # --- Context Construction ---

    def _build_context(
        self, request: ScaffoldRequest
    ) -> dict[str, str]:
        """Build the token substitution context.

        All values are explicit and deterministic. The engine
        never generates secrets or random values — the secret
        key is an explicit input.
        """
        project_name = request.config.name
        apps = request.config.apps

        # Build INSTALLED_APPS fragment
        installed_apps = self._build_installed_apps(apps)

        # Build URL patterns fragment
        url_patterns = self._build_url_patterns(apps)

        # Python-safe secret key: repr() wraps in quotes
        secret_key_py = repr(request.secret_key)

        return {
            "__DJSTART_PROJECT_NAME__": project_name,
            "__DJSTART_SECRET_KEY_PY__": secret_key_py,
            "__DJSTART_INSTALLED_APPS__": installed_apps,
            "__DJSTART_APP_URLPATTERNS__": url_patterns,
            "__DJSTART_DJANGO_VERSION_COMMENT__": (
                f"Django {request.release.series}"
            ),
            "__DJSTART_DOCS_VERSION__": (
                request.release.series
            ),
            # App-scoped tokens are set per-app, not here
            "__DJSTART_APP_NAME__": "",
            "__DJSTART_APP_CONFIG_CLASS__": "",
        }

    def _build_installed_apps(
        self, apps: tuple[AppConfig, ...]
    ) -> str:
        """Build the INSTALLED_APPS token value.

        Generates lines like:
            'core.apps.CoreConfig',
            'accounts.apps.AccountsConfig',
        """
        lines: list[str] = []
        for app in apps:
            config_class = _app_name_to_config_class(
                app.name
            )
            lines.append(
                f"    '{app.name}.apps.{config_class}',"
            )
        return "\n".join(lines)

    def _build_url_patterns(
        self, apps: tuple[AppConfig, ...]
    ) -> str:
        """Build the URL patterns token value.

        Generates lines like:
            path('', include('core.urls')),
            path('accounts/', include('accounts.urls')),
        """
        lines: list[str] = []
        for i, app in enumerate(apps):
            if i == 0:
                # First app gets root URL
                prefix = ""
            else:
                prefix = f"{app.name}/"
            lines.append(
                f"    path('{prefix}', "
                f"include('{app.name}.urls')),"
            )
        return "\n".join(lines)

    # --- Template Rendering ---

    def _render_template(
        self,
        template: RecipeTemplate,
        context: dict[str, str],
    ) -> RenderedFile:
        """Render a single template with token substitution.

        Performs literal string replacement only — no eval, exec,
        format expressions, Jinja, or Django template evaluation.

        Django ``{{ }}`` and ``{% %}`` syntax passes through
        byte-for-byte.
        """
        # Validate all tokens in content are registered
        content = template.content
        path_str = str(template.relative_path)

        # Render path tokens first
        rendered_path = self._substitute_tokens(
            path_str, context, "path"
        )

        # Render content tokens
        rendered_content = self._substitute_tokens(
            content, context, rendered_path
        )

        # Verify no unresolved __DJSTART_*__ tokens remain
        _check_unresolved_tokens(
            rendered_path, rendered_content
        )

        return RenderedFile(
            relative_path=PurePosixPath(rendered_path),
            content=rendered_content,
        )

    def _substitute_tokens(
        self,
        text: str,
        context: dict[str, str],
        source_desc: str,
    ) -> str:
        """Replace all __DJSTART_*__ tokens with context values.

        Unknown tokens raise ConfigurationError immediately.
        """
        def replacer(match: re.Match[str]) -> str:
            token = match.group(0)
            if token not in _REGISTERED_TOKENS:
                raise ConfigurationError(
                    f"Unknown template token {token!r} in "
                    f"{source_desc!r}"
                )
            if token not in context:
                raise ConfigurationError(
                    f"Token {token!r} has no value in render "
                    f"context for {source_desc!r}"
                )
            return context[token]

        return _TOKEN_PATTERN.sub(replacer, text)

    # --- Requirements ---

    def _build_requirements(
        self, request: ScaffoldRequest
    ) -> tuple[str, ...]:
        """Build the bounded requirements manifest.

        Django requirement comes first, derived from the
        FrameworkRelease. Recipe dependencies follow in
        declared order.
        """
        django_req = str(request.release.django_requires)
        # Format as proper requirement line
        django_line = f"Django{django_req}"

        reqs: list[str] = [django_line]
        reqs.extend(request.recipe.metadata.dependencies)

        return tuple(reqs)


# --- Path Validation ---


def _validate_rendered_path(path: PurePosixPath) -> None:
    """Validate a rendered target path is safe.

    Rejects absolute paths, traversal, empty paths, and paths
    targeting unsafe directories.
    """
    path_str = str(path)

    if not path_str or path_str.isspace():
        raise ConfigurationError(
            "Rendered file path must not be empty"
        )

    if path.is_absolute():
        raise ConfigurationError(
            f"Rendered file path must be relative, "
            f"got: {path_str!r}"
        )

    for part in path.parts:
        if part in _UNSAFE_COMPONENTS:
            raise ConfigurationError(
                f"Rendered file path contains unsafe "
                f"component {part!r}: {path_str!r}"
            )

    # Check resolved path doesn't escape project root
    # by normalizing and checking for leading ..
    normalized = PurePosixPath(*path.parts)
    if str(normalized).startswith(".."):
        raise ConfigurationError(
            f"Rendered file path escapes project root: "
            f"{path_str!r}"
        )


def _detect_duplicates(
    files: list[RenderedFile],
) -> None:
    """Detect duplicate target paths.

    Engine-owned paths (like requirements.txt) may only appear
    once and only from the engine itself. Recipe templates must
    not target engine-owned paths.
    """
    seen: dict[PurePosixPath, int] = {}
    for i, rf in enumerate(files):
        if rf.relative_path in seen:
            raise ConfigurationError(
                f"Duplicate rendered file path: "
                f"{str(rf.relative_path)!r}. "
                f"Two templates resolve to the same "
                f"target path."
            )
        seen[rf.relative_path] = i


def _check_unresolved_tokens(
    path: str, content: str
) -> None:
    """Verify no __DJSTART_*__ tokens remain after rendering."""
    for text, label in [
        (path, "path"),
        (content, "content"),
    ]:
        remaining = _TOKEN_PATTERN.findall(text)
        if remaining:
            tokens = ", ".join(sorted(set(remaining)))
            raise ConfigurationError(
                f"Unresolved template tokens in {label}: "
                f"{tokens}"
            )
