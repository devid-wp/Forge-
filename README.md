# Forge

Forge is a CLI tool that analyzes the structure of a software project and shows important information in a clean terminal interface — without any AI.

## Features

- **Project info** — name, size, file/directory counts
- **Languages** — detected by file extensions, with code-line counts and percentages
- **Technologies** — Python, Node.js, Rust, Go, Java, etc. via config files
- **Structure** — file tree with heavy directories ignored
- **Git** — branch, commits, uncommitted changes (when inside a repo)
- **Health** — a simple AI-free scoring system (README, .gitignore, license, deps, tests, CI/CD)
- **Largest files** — identify bloat by size
- **Directory sizes** — visual breakdown of top-level folders
- **File types** — text vs binary ratio
- **JSON output** — machine-readable results for CI/scripting
- **.forgeignore** — your own ignore patterns per project

## Installation

```bash
python -m venv .venv
.venv/bin/pip install -e .
```

## Usage

```bash
devanalyze .                 # full analysis of the current directory
devanalyze /path/to/project  # full analysis of a specific path
devanalyze . -                                      # interactive mode (coming soon)

devanalyze stats             # languages and file statistics
devanalyze tree              # file tree
devanalyze git               # git analysis
devanalyze health            # project health score
```

### Options

```bash
devanalyze analyze . --no-tree              # skip the file tree
devanalyze analyze . --no-git               # skip git analysis
devanalyze analyze . --depth 2              # limit tree depth
devanalyze analyze . --top-files 20         # show 20 largest files
devanalyze analyze . --dir-sizes            # show directory size breakdown
devanalyze analyze . --json                 # machine-readable JSON output
devanalyze stats --no-types                 # hide text/binary summary
```

### .forgeignore

Custom ignore patterns, gitignore-style. Place in the project root:

```bash
# skip generated directories (trailing / = directory only)
generated/
build/

# skip files matching a glob
*.min.js
```

Built-in ignores (node_modules, .git, venv, dist, etc.) always apply.

## Project layout

```
Forge/
├── main.py            # CLI entry point
├── analyzers/         # files, languages, git, health, technologies
├── ui/                # Rich-based display
└── utils/             # ignore rules
```

## License

MIT — see [LICENSE](LICENSE).
