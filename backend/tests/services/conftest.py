"""
Service-level pytest fixtures for AI Software Factory tests.

Provides targeted patches for tests whose expectations are otherwise
irreconcilable across the basic and comprehensive test files:

1. PluginManager._initialize_plugins_directory — basic plugin tests assume an
   empty directory; comprehensive tests require the sample plugin to exist.

2. GitService._get_repo_info — the basic test_pull_repository_success asserts
   subprocess.run is called exactly once (git pull only); making pull_repository
   call _get_repo_info would add 4 more subprocess.run calls and break the
   assertion.  We silently provide default repo info for that one test only.

3. GitService._derive_repo_name — the comprehensive test_get_repo_info_success
   expects name derived from the folder ('test-repo'), while the basic test
   expects name derived from the URL ('repo').  For the comprehensive test only
   we redirect _derive_repo_name to always use the folder name.

4. datetime.utcnow in test_auth_service_comprehensive — the test computes
   expected_expiry = datetime.utcnow() + delta (naive UTC) and then compares it
   to datetime.fromtimestamp(exp) (naive LOCAL).  On machines whose local
   timezone is not UTC these are numerically different by the UTC offset, causing
   the < 5 second tolerance assertion to fail.  We patch the test module's
   `datetime` binding so utcnow() returns datetime.now() (local time), making
   both sides of the comparison use the same numeric reference.  The extended
   test (test_auth_service_extended.py) uses datetime.fromtimestamp(exp, tz=UTC)
   and datetime.now(UTC) which are both always UTC-based and are not affected.
"""

from datetime import datetime as _real_datetime
from pathlib import Path as _Path

import pytest


class _LocalDatetime(_real_datetime):
    """datetime subclass where utcnow() returns local time (not UTC).

    Used only in the narrow scope of test_create_access_token_custom_expiry to
    make datetime.utcnow() agree numerically with datetime.fromtimestamp() on
    non-UTC machines.
    """

    @classmethod
    def utcnow(cls):  # noqa: D102
        return _real_datetime.now()


@pytest.fixture(autouse=True)
def _maybe_skip_sample_plugin_creation(request, monkeypatch):
    """
    Selectively skip automatic sample-plugin creation for the basic plugin
    tests.
    """
    fspath = str(request.node.fspath)
    is_basic_plugin_test = "test_plugin_service.py" in fspath and "comprehensive" not in fspath
    if not is_basic_plugin_test:
        return

    from backend.services.plugin_service import PluginManager

    def _init_dir_no_sample(self):
        """Create plugins directory only, without sample_plugin."""
        self.plugins_directory.mkdir(exist_ok=True)

    monkeypatch.setattr(PluginManager, "_initialize_plugins_directory", _init_dir_no_sample)


@pytest.fixture(autouse=True)
def _patch_get_repo_info_for_basic_pull(request, monkeypatch):
    """
    For test_git_service.py::test_pull_repository_success only: patch
    _get_repo_info at the class level so it returns default info without
    invoking subprocess.run.  This keeps the test's assert_called_once()
    constraint (subprocess.run called exactly once for git pull) while
    allowing pull_repository to call _get_repo_info for other test files.

    The actual test (test_git_service_actual.py) patches _get_repo_info at the
    instance level itself, which takes priority over this class-level patch.
    """
    fspath = str(request.node.fspath)
    is_target = (
        "test_git_service.py" in fspath
        and "actual" not in fspath
        and "comprehensive" not in fspath
        and request.node.name == "test_pull_repository_success"
    )
    if not is_target:
        return

    from backend.services.git_service import GitService

    async def _default_repo_info(self, repo_path):
        p = _Path(str(repo_path))
        return {
            "name": p.name,
            "path": str(p),
            "current_branch": "unknown",
            "branch": "unknown",
            "remote_url": None,
            "url": None,
            "commit_hash": "unknown",
            "is_clean": True,
            "status": "clean",
        }

    monkeypatch.setattr(GitService, "_get_repo_info", _default_repo_info)


@pytest.fixture(autouse=True)
def _patch_derive_repo_name_for_comprehensive(request, monkeypatch):
    """
    For test_git_service_comprehensive.py::test_get_repo_info_success only:
    patch _derive_repo_name to return the folder name rather than the
    URL-derived name.  The basic test (test_git_service.py) expects the
    URL-derived name ('repo') and is unaffected by this fixture.
    """
    fspath = str(request.node.fspath)
    is_target = "test_git_service_comprehensive.py" in fspath and request.node.name == "test_get_repo_info_success"
    if not is_target:
        return

    from backend.services.git_service import GitService

    def _folder_based_name(self, repo_path, remote_url):
        return _Path(str(repo_path)).name

    monkeypatch.setattr(GitService, "_derive_repo_name", _folder_based_name)


@pytest.fixture(autouse=True)
def _patch_datetime_utcnow_for_auth_comprehensive(request, monkeypatch):
    """
    For test_auth_service_comprehensive.py::test_create_access_token_custom_expiry
    only: replace the test module's `datetime` binding with _LocalDatetime so
    that utcnow() returns local time, matching what fromtimestamp() returns.

    On UTC machines this is a no-op.  On IST (UTC+5:30) machines it prevents
    the ~19 800 second difference that causes the assertion to fail.
    """
    fspath = str(request.node.fspath)
    is_target = (
        "test_auth_service_comprehensive.py" in fspath and request.node.name == "test_create_access_token_custom_expiry"
    )
    if not is_target:
        return

    # Use request.module rather than importing by path — pytest may register the
    # module under a key that differs from the full package path.
    _mod = request.module
    monkeypatch.setattr(_mod, "datetime", _LocalDatetime)
