import pathlib
import subprocess

import nox
from nox_poetry import session

PYTHON_VERSIONS = ["3.10"]

# Set default sessions
nox.options.sessions = ["format", "lint", "test", "typing"]

# Main app
app = "."

# Formatters
black = "black"
isort = "isort"

# Linters
flake8 = "flake8"
bandit = "bandit"
mypy = ("mypy", "aiohttp", "pytest", "loguru", "nox", "nox-poetry")
pytest = ("pytest", "pytest-aiohttp", "pytest-cov")


@session(python=PYTHON_VERSIONS)
def format(session: nox.Session):
    session.install(black, isort)

    session.run(
        "black", "--config", "pyproject.toml", "--diff", "--check", *py_files()
    )
    session.run(
        "isort",
        "--settings-path",
        "pyproject.toml",
        "--check-only",
        *py_files()
    )


@session(python=PYTHON_VERSIONS)
def lint(session: nox.Session):
    session.install(flake8, bandit, *pytest)

    session.run("flake8", *py_files())
    session.run("bandit", "-q", "-c", "pyproject.toml", *pkg_files())


@session(python=PYTHON_VERSIONS)
def typing(session: nox.Session):
    session.install(*mypy)
    session.run("mypy", *py_files())


@session(python=PYTHON_VERSIONS)
def test(session: nox.Session):
    session.install(app, *pytest)
    session.run("pytest", "-v", "app/tests")


@session(python=PYTHON_VERSIONS)
def coverage(session: nox.Session):
    session.install(app, *pytest)
    session.run("pytest", "--cov=app", "--cov-report=xml", "app/tests")


def git_files() -> list[str]:
    """Fetches a list of all tracked files in the current repository.

    Returns:
        A list of relative file paths.
    """
    proc = subprocess.check_output(["/usr/bin/git", "ls-files"])
    return proc.decode("utf-8").rstrip("\n").split("\n")


def pkg_files() -> list[str]:
    """Fetches all package (non-test) files in the current repository.

    Returns:
        A list of relative file paths.
    """
    return _glob(py_files(), "tests/*", invert=True)


def py_files() -> list[str]:
    """Fetches all Python source files in the current repository.

    Returns:
        A list of relative file paths.
    """
    return _glob(git_files(), "*.py")


def _glob(filenames, pattern: str, invert: bool = False):
    """Applies a glob pattern to a string list of file names.

    Args:
        filenames: The list of file names.
        pattern: The glob pattern to apply.
        invert: If True, returns file names which evaluate to False.

    Returns:
        A list of filtered file names.
    """

    def match(path: str, pattern: str) -> bool:
        if invert:
            return not pathlib.PurePath(path).match(pattern)
        else:
            return pathlib.PurePath(path).match(pattern)

    return list(filter(lambda f: match(f, pattern), filenames))
