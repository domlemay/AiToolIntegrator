"""GitPython helpers for cloning and managing plugin repositories."""

from __future__ import annotations

import shutil
from pathlib import Path

import git
from git import GitCommandError, InvalidGitRepositoryError, Repo

from aitoolintegrator.utils.logger import get_logger, print_error


logger = get_logger(__name__)


def clone_repo(
    url: str,
    dest: Path,
    branch: str = "main",
    depth: int = 1,
) -> Repo:
    """Clone a Git repository to the destination path.

    Args:
        url: Repository URL (https or git@).
        dest: Target directory for the clone.
        branch: Branch name to clone.
        depth: Clone depth (1 for shallow clone).

    Returns:
        The cloned Repo object.

    Raises:
        RuntimeError: If the clone fails.
    """
    if dest.exists():
        logger.debug("Destination %s already exists, removing", dest)
        shutil.rmtree(dest)

    try:
        repo = Repo.clone_from(
            url,
            str(dest),
            branch=branch,
            depth=depth,
            multi_options=["--single-branch"],
        )
        logger.debug("Cloned %s → %s", url, dest)
        return repo
    except GitCommandError as exc:
        # Fall back to main branch if specified branch not found
        if branch != "main":
            logger.warning("Branch %r not found, falling back to default branch", branch)
            try:
                repo = Repo.clone_from(url, str(dest), depth=depth)
                return repo
            except GitCommandError as exc2:
                raise RuntimeError(f"Failed to clone {url}: {exc2}") from exc2
        raise RuntimeError(f"Failed to clone {url}: {exc}") from exc


def is_git_repo(path: Path) -> bool:
    """Check whether a directory is a valid Git repository.

    Args:
        path: Directory to check.

    Returns:
        True if it's a Git repo, False otherwise.
    """
    try:
        Repo(str(path))
        return True
    except (InvalidGitRepositoryError, Exception):
        return False


def get_repo_default_branch(url: str) -> str:
    """Determine the default branch of a remote repository without cloning.

    Args:
        url: Remote repository URL.

    Returns:
        Branch name (e.g. 'main' or 'master').
    """
    try:
        refs = git.cmd.Git().ls_remote("--symref", url, "HEAD")
        for line in refs.splitlines():
            if line.startswith("ref:"):
                return line.split("/")[-1].split("\t")[0]
    except Exception:
        pass
    return "main"
