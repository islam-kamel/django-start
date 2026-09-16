"""Scaffold engine port for Django-Start 2.0.

Defines the protocol for the deterministic scaffold renderer.
Phase 5 establishes this as a pure planner — no filesystem
writes, no subprocess execution, no network access.
"""

from typing import Protocol

from django_start.domain.recipes import ScaffoldPlan, ScaffoldRequest


class ScaffoldEngine(Protocol):
    """Protocol for deterministic scaffold rendering.

    The engine transforms explicit immutable inputs into an
    immutable ``ScaffoldPlan``. It performs no external I/O.

    Phase 6 will take a ``ScaffoldPlan`` and execute it through
    the ``FileSystem`` port. This separation makes future
    ``--dry-run`` implementation straightforward.
    """

    def render(self, request: ScaffoldRequest) -> ScaffoldPlan:
        """Render a scaffold plan from a request.

        Args:
            request: Immutable request containing project config,
                framework release, recipe bundle, explicit host
                Python version, Django-Start version, and secret
                key.

        Returns:
            Immutable ``ScaffoldPlan`` with rendered files sorted
            by POSIX path and bounded requirements.

        Raises:
            ConfigurationError: On duplicate target paths, unsafe
                paths, unresolved tokens, or recipe incompatibility.
            UnsupportedVersionError: On Python/Django/Django-Start
                version incompatibility with the recipe.
        """
        ...
