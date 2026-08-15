from __future__ import annotations

import ast
import platform
import subprocess
from pathlib import Path
from collections import Counter


# ============================================================
# CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = PROJECT_ROOT / "_AI_CONTEXT"

EXCLUDED_DIRS = {
    ".git",
    ".hg",
    ".svn",

    "venv",
    ".venv",
    "env",
    ".env",

    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",

    ".idea",
    ".vscode",

    "node_modules",
    "dist",
    "build",

    "htmlcov",
    ".coverage",

    "logs",
    "uploads",
}

EXCLUDED_FILES = {
    ".env",
    ".env.local",
    ".env.production",
    ".env.development",

    ".DS_Store",
    "Thumbs.db",
}

INCLUDED_EXTENSIONS = {
    ".py",
    ".html",
    ".htm",
    ".css",
    ".js",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".ini",
    ".cfg",
    ".md",
    ".txt",
    ".sql",
    ".sh",
    ".bat",
    ".ps1",
}

IMPORTANT_FILES = {
    "Dockerfile",
    "Procfile",
    "passenger_wsgi.py",
    "requirements.txt",
    "pyproject.toml",
    "setup.py",
    "setup.cfg",
    "Pipfile",
    "Pipfile.lock",
    "pytest.ini",
    "tox.ini",
    "Makefile",
    ".gitignore",
}

MAX_FILE_SIZE = 2 * 1024 * 1024


# ============================================================
# OUTPUT FILES
# ============================================================

OUTPUT_FILES = {
    "overview": OUTPUT_DIR / "00_PROJECT_OVERVIEW.md",
    "structure": OUTPUT_DIR / "01_PROJECT_STRUCTURE.md",
    "dependencies": OUTPUT_DIR / "02_DEPENDENCIES.md",

    "domain": OUTPUT_DIR / "10_DOMAIN.md",
    "application": OUTPUT_DIR / "20_APPLICATION.md",
    "infrastructure": OUTPUT_DIR / "30_INFRASTRUCTURE.md",
    "interfaces": OUTPUT_DIR / "40_INTERFACES.md",
    "tests": OUTPUT_DIR / "50_TESTS.md",

    "other": OUTPUT_DIR / "90_OTHER_FILES.md",

    "git": OUTPUT_DIR / "99_GIT_STATUS.md",
}


# ============================================================
# HELPERS
# ============================================================

def relative_path(path: Path) -> str:
    return path.relative_to(PROJECT_ROOT).as_posix()


def is_excluded(path: Path) -> bool:

    try:
        rel = path.relative_to(PROJECT_ROOT)
    except ValueError:
        return True

    parts = rel.parts

    for part in parts[:-1]:
        if part in EXCLUDED_DIRS:
            return True

    if path.name in EXCLUDED_FILES:
        return True

    if path.name.startswith(".env"):
        return True

    return False


def should_include(path: Path) -> bool:

    if is_excluded(path):
        return False

    if path.name in IMPORTANT_FILES:
        return True

    return path.suffix.lower() in INCLUDED_EXTENSIONS


def safe_read(path: Path) -> str | None:

    try:

        if path.stat().st_size > MAX_FILE_SIZE:
            return None

        return path.read_text(
            encoding="utf-8"
        )

    except Exception:
        return None


def count_lines(text: str) -> int:

    if not text:
        return 0

    return len(text.splitlines())


def format_bytes(size: int) -> str:

    if size < 1024:
        return f"{size} B"

    if size < 1024 ** 2:
        return f"{size / 1024:.1f} KB"

    if size < 1024 ** 3:
        return f"{size / (1024 ** 2):.1f} MB"

    return f"{size / (1024 ** 3):.1f} GB"


# ============================================================
# FILE COLLECTION
# ============================================================

def collect_files() -> list[Path]:

    files = []

    for path in PROJECT_ROOT.rglob("*"):

        if not path.is_file():
            continue

        if should_include(path):
            files.append(path)

    return sorted(
        files,
        key=lambda p: relative_path(p).lower()
    )


# ============================================================
# PROJECT SECTION DETECTION
# ============================================================

def get_section(path: Path) -> str:

    rel = path.relative_to(PROJECT_ROOT)

    if not rel.parts:
        return "other"

    root = rel.parts[0].lower()

    if root == "domain":
        return "domain"

    if root == "application":
        return "application"

    if root == "infrastructure":
        return "infrastructure"

    if root == "interfaces":
        return "interfaces"

    if root in {
        "test",
        "tests",
    }:
        return "tests"

    return "other"


# ============================================================
# PYTHON IMPORT ANALYSIS
# ============================================================

def extract_imports(path: Path) -> list[str]:

    try:
        source = path.read_text(
            encoding="utf-8"
        )

        tree = ast.parse(source)

    except Exception:
        return []

    imports = set()

    for node in ast.walk(tree):

        if isinstance(node, ast.Import):

            for alias in node.names:
                imports.add(alias.name)

        elif isinstance(node, ast.ImportFrom):

            if node.module:
                imports.add(node.module)

    return sorted(imports)


def collect_import_summary(files):

    counter = Counter()

    for path in files:

        if path.suffix.lower() != ".py":
            continue

        for imported in extract_imports(path):

            root = imported.split(".")[0]

            counter[root] += 1

    return counter


# ============================================================
# GIT
# ============================================================

def git(args):

    try:

        result = subprocess.run(
            ["git", *args],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

        if result.returncode != 0:
            return ""

        return result.stdout.strip()

    except Exception:
        return ""


# ============================================================
# MARKDOWN LANGUAGE
# ============================================================

def markdown_language(path: Path) -> str:

    mapping = {
        ".py": "python",
        ".html": "html",
        ".htm": "html",
        ".css": "css",
        ".js": "javascript",
        ".json": "json",
        ".yaml": "yaml",
        ".yml": "yaml",
        ".toml": "toml",
        ".ini": "ini",
        ".cfg": "ini",
        ".md": "markdown",
        ".sql": "sql",
        ".sh": "bash",
        ".bat": "bat",
        ".ps1": "powershell",
    }

    return mapping.get(
        path.suffix.lower(),
        "text"
    )


# ============================================================
# WRITE FILE CONTENT
# ============================================================

def write_file_block(output, path: Path):

    rel = relative_path(path)

    output.write(
        f"# FILE: `{rel}`\n\n"
    )

    text = safe_read(path)

    if text is None:

        output.write(
            "> [CONTENT SKIPPED: "
            "binary, unreadable, or too large]\n\n"
        )

        output.write("---\n\n")

        return

    language = markdown_language(path)

    output.write(
        f"```{language}\n"
    )

    output.write(text)

    if not text.endswith("\n"):
        output.write("\n")

    output.write(
        "```\n\n"
    )

    output.write(
        "---\n\n"
    )


# ============================================================
# PROJECT STRUCTURE
# ============================================================

def create_structure(files):

    directories = set()

    for path in files:

        rel = path.relative_to(PROJECT_ROOT)

        for i in range(
            1,
            len(rel.parts)
        ):

            directories.add(
                Path(
                    *rel.parts[:i]
                )
            )

    paths = list(directories)

    paths.extend(
        p.relative_to(PROJECT_ROOT)
        for p in files
    )

    paths = sorted(
        set(paths),
        key=lambda p: str(p).lower()
    )

    lines = [
        f"{PROJECT_ROOT.name}/"
    ]

    for path in paths:

        depth = len(path.parts)

        prefix = "    " * depth

        if path in directories:

            lines.append(
                f"{prefix}{path.name}/"
            )

        else:

            lines.append(
                f"{prefix}{path.name}"
            )

    return "\n".join(lines)


# ============================================================
# OVERVIEW
# ============================================================

def generate_overview(files):

    total_size = 0
    total_lines = 0

    extensions = Counter()

    for path in files:

        try:
            size = path.stat().st_size
        except OSError:
            continue

        total_size += size

        text = safe_read(path)

        if text is not None:
            total_lines += count_lines(text)

        extension = (
            path.suffix.lower()
            if path.suffix
            else "[no extension]"
        )

        extensions[extension] += 1

    git_branch = git(
        ["branch", "--show-current"]
    )

    last_commit = git(
        ["log", "-1", "--oneline"]
    )

    with OUTPUT_FILES["overview"].open(
        "w",
        encoding="utf-8"
    ) as output:

        output.write(
            "# Project Overview\n\n"
        )

        output.write(
            "This document was automatically generated "
            "for AI-assisted project analysis.\n\n"
        )

        output.write(
            "## Environment\n\n"
        )

        output.write(
            f"- OS: `{platform.system()} "
            f"{platform.release()}`\n"
        )

        output.write(
            f"- Python: `{platform.python_version()}`\n"
        )

        output.write(
            f"- Project Root: `{PROJECT_ROOT}`\n"
        )

        output.write(
            f"- Files: `{len(files)}`\n"
        )

        output.write(
            f"- Lines: `{total_lines:,}`\n"
        )

        output.write(
            f"- Size: `{format_bytes(total_size)}`\n\n"
        )

        output.write(
            "## Git\n\n"
        )

        output.write(
            f"- Branch: `{git_branch or 'Unknown'}`\n"
        )

        output.write(
            f"- Last Commit: `{last_commit or 'Unknown'}`\n\n"
        )

        output.write(
            "## File Types\n\n"
        )

        output.write(
            "| Extension | Files |\n"
            "|---|---:|\n"
        )

        for extension, count in sorted(
            extensions.items()
        ):

            output.write(
                f"| `{extension}` | {count} |\n"
            )


# ============================================================
# STRUCTURE
# ============================================================

def generate_structure(files):

    with OUTPUT_FILES["structure"].open(
        "w",
        encoding="utf-8"
    ) as output:

        output.write(
            "# Project Structure\n\n"
        )

        output.write(
            "```text\n"
        )

        output.write(
            create_structure(files)
        )

        output.write(
            "\n```\n"
        )


# ============================================================
# DEPENDENCIES
# ============================================================

def generate_dependencies(files):

    imports = collect_import_summary(files)

    config_files = []

    for filename in IMPORTANT_FILES:

        path = PROJECT_ROOT / filename

        if path.exists():

            config_files.append(path)

    with OUTPUT_FILES["dependencies"].open(
        "w",
        encoding="utf-8"
    ) as output:

        output.write(
            "# Dependencies & Configuration\n\n"
        )

        output.write(
            "## Configuration Files\n\n"
        )

        for path in config_files:

            output.write(
                f"- `{relative_path(path)}`\n"
            )

        output.write(
            "\n## Python Import Summary\n\n"
        )

        output.write(
            "| Module | Count |\n"
            "|---|---:|\n"
        )

        for module, count in imports.most_common():

            output.write(
                f"| `{module}` | {count} |\n"
            )

        output.write("\n")

        # Include requirements/config content
        for path in config_files:

            if path.name in {
                "requirements.txt",
                "pyproject.toml",
                "setup.py",
                "setup.cfg",
                "Pipfile",
                "Pipfile.lock",
            }:

                write_file_block(
                    output,
                    path
                )


# ============================================================
# SECTION FILES
# ============================================================

def generate_section(
    section_name: str,
    files: list[Path],
):

    output_path = OUTPUT_FILES[section_name]

    title = section_name.title()

    with output_path.open(
        "w",
        encoding="utf-8"
    ) as output:

        output.write(
            f"# {title}\n\n"
        )

        output.write(
            f"Files belonging to the "
            f"`{section_name}` section of the project.\n\n"
        )

        output.write(
            f"**Files in this section:** "
            f"`{len(files)}`\n\n"
        )

        output.write(
            "---\n\n"
        )

        for index, path in enumerate(
            files,
            start=1
        ):

            print(
                f"[{section_name}] "
                f"{index}/{len(files)} "
                f"{relative_path(path)}"
            )

            write_file_block(
                output,
                path
            )


# ============================================================
# GIT REPORT
# ============================================================

def generate_git_report():

    branch = git(
        ["branch", "--show-current"]
    )

    status = git(
        ["status", "--short"]
    )

    last_commit = git(
        ["log", "-1", "--oneline"]
    )

    remotes = git(
        ["remote", "-v"]
    )

    with OUTPUT_FILES["git"].open(
        "w",
        encoding="utf-8"
    ) as output:

        output.write(
            "# Git Status\n\n"
        )

        output.write(
            f"## Branch\n\n"
            f"`{branch or 'Unknown'}`\n\n"
        )

        output.write(
            "## Last Commit\n\n"
        )

        output.write(
            f"`{last_commit or 'Unknown'}`\n\n"
        )

        output.write(
            "## Working Tree\n\n"
        )

        if status:

            output.write(
                "```text\n"
            )

            output.write(
                status
            )

            output.write(
                "\n```\n\n"
            )

        else:

            output.write(
                "Working tree is clean.\n\n"
            )

        output.write(
            "## Remotes\n\n"
        )

        if remotes:

            output.write(
                "```text\n"
            )

            output.write(
                remotes
            )

            output.write(
                "\n```\n"
            )

        else:

            output.write(
                "No Git remote detected.\n"
            )


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 70)
    print("AI PROJECT CONTEXT BUILDER")
    print("=" * 70)

    print(
        f"Project: {PROJECT_ROOT}"
    )

    print()

    # Recreate output directory
    OUTPUT_DIR.mkdir(
        exist_ok=True
    )

    files = collect_files()

    print(
        f"Files found: {len(files)}"
    )

    print()

    # Generate general reports
    generate_overview(files)
    generate_structure(files)
    generate_dependencies(files)
    generate_git_report()

    # Group project files
    sections = {
        "domain": [],
        "application": [],
        "infrastructure": [],
        "interfaces": [],
        "tests": [],
        "other": [],
    }

    for path in files:

        section = get_section(path)

        sections[section].append(path)

    # Generate section files
    for section_name, section_files in sections.items():

        generate_section(
            section_name,
            section_files
        )

    print()
    print("=" * 70)
    print("COMPLETED")
    print("=" * 70)

    print(
        f"Output directory: {OUTPUT_DIR}"
    )

    print()

    for name, path in OUTPUT_FILES.items():

        if path.exists():

            try:
                size = path.stat().st_size
                print(
                    f"{path.name:<35} "
                    f"{format_bytes(size)}"
                )
            except OSError:
                pass

    print("=" * 70)


if __name__ == "__main__":
    main()