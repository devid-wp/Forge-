<p align="center">
  <img src="https://img.shields.io/badge/version-1.0.0-blue.svg" alt="Version">
  <img src="https://img.shields.io/badge/python-3.10%2B-blue.svg" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="MIT License">
  <img src="https://img.shields.io/badge/dependencies-2-orange.svg" alt="2 dependencies">
</p>

<h1 align="center">⚒️ Forge</h1>

<p align="center">
  <strong>Instant project analysis for developers — no AI, no cloud, just your terminal.</strong><br>
  Point Forge at any codebase and get languages, structure, git state, and a health score in seconds.
</p>

---

## ✨ Why Forge?

Every developer has been there: you clone a repo, open it, and have **no idea** what you're looking at. Is it Python or a monorepo? Where are the tests? Is there CI? Is it healthy?

Forge answers all of that in a single command — **locally, instantly, and privately**. There is no AI, no data leaves your machine, and nothing is uploaded anywhere.

```text
forge
```

That's it. One command, a beautiful report, and you understand the project.

## 🚀 Features

| | |
|---|---|
| 📊 **Project overview** | Name, size, file and directory counts |
| 🌍 **Language analysis** | Extensions → languages, code-line counts, percentages |
| 🗂 **File tree** | Interactive-depth structure view, heavy dirs auto-skipped |
| 🧩 **Technology detection** | Python, Node.js, Rust, Go, Java, Docker and 30+ more via config files |
| 🌿 **Git analysis** | Branch, commits, last commit, staged/untracked changes |
| 💚 **Health score** | AI-free checklist: README, license, deps, tests, CI/CD → 0–100 |
| 🐘 **Largest files** | Spot bloat instantly |
| 📦 **Directory sizes** | Visual bar breakdown of top-level folders |
| 🧬 **File types** | Text vs. binary ratio |
| 🔧 **`.forgeignore`** | gitignore-style custom ignore patterns |
| 🖥 **JSON output** | Machine-readable results for scripts and CI |
| ⚡ **Fast** | Pure `pathlib` + `rich`, no heavy dependencies |

## 🖥 Screenshot

```text
╭──────────────────────────────────────────────────────────────────────────────╮
│                                                                              │
│  Forge - Project Analysis                                                    │
│  /home/you/your-project                                                      │
│                                                                              │
╰──────────────────────────────────────────────────────────────────────────────╯

            Project Information
┌─────────────┬────────────────────────────┐
│ Name        │ your-project               │
│ Path        │ /home/you/your-project     │
│ Size        │ 53.0 KB                    │
│ Files       │ 20                         │
│ Directories │ 4                          │
└─────────────┴────────────────────────────┘

           Programming Languages
┏━━━━━━━━━━┳━━━━━━━┳━━━━━━━┳━━━━━━━┳━━━━━━━┓
┃ Language ┃ Files ┃ Lines ┃  Code ┃     % ┃
┡━━━━━━━━━━╇━━━━━━━╇━━━━━━━╇━━━━━━━╇━━━━━━━┩
│ Python   │    15 │ 1,567 │ 1,267 │ 89.6% │
│ Markdown │     1 │    86 │    65 │  4.6% │
│ Shell    │     1 │    65 │    44 │  3.1% │
│ TOML     │     1 │    43 │    38 │  2.7% │
│ Total    │    18 │ 1,761 │ 1,414 │  100% │
└──────────┴───────┴───────┴───────┴───────┘

                Project Health - 83/100
┏━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Check        ┃ Status ┃ Description                 ┃
┡━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ README       │ ✓ PASS │ README file present         │
│ .gitignore   │ ✓ PASS │ .gitignore present          │
│ License      │ ✓ PASS │ License file present        │
│ Dependencies │ ✓ PASS │ Dependency config present   │
│ Tests        │ ✓ PASS │ Test files present          │
│ CI/CD        │ ✗ FAIL │ CI/CD configuration present │
└──────────────┴────────┴─────────────────────────────┘

╭──────────────────────────── ✨ Analysis Complete ────────────────────────────╮
│  your-project · 20 files | 53.0 KB · Python (4 languages) · Health: 83/100  │
╰──────────────────────────────────────────────────────────────────────────────╯
```

> Run it yourself with `forge` — this is the real output.

## 📦 Installation

### Option 1 — One-command installer (recommended)

Requires **Python ≥ 3.10** and `git`:

```bash
git clone https://github.com/your-user/forge.git
cd forge
./install.sh           # creates .venv and installs everything
```

Add `forge` to your system `PATH` so you can use it from any project:

```bash
./install.sh --global  # symlinks forge into ~/.local/bin
```

### Option 2 — Manual / pip

```bash
python -m venv .venv
.venv/bin/pip install -e .
.venv/bin/activate  # then `forge` is available
```

## 🪄 Usage

### Run anywhere

```bash
forge                      # analyze the current directory
forge /path/to/project     # analyze any project
forge --version            # show version
forge --help               # show help
```

### Subcommands

```bash
forge stats                # languages, file types, largest files
forge tree                 # file structure tree
forge git                  # git repository analysis
forge health               # project health checklist
```

### Options for `forge` / `forge analyze`

| Option | Description |
|---|---|
| `--depth N`, `-d N` | Maximum tree depth (default `4`) |
| `--no-tree` | Skip the file tree |
| `--no-git` | Skip git analysis |
| `--top-files N`, `-f N` | Show N largest files (`0` to hide) |
| `--dir-sizes` | Show directory size breakdown |
| `--json` | Machine-readable JSON output |

```bash
forge --top-files 20                 # largest files
forge --dir-sizes                    # directory size bars
forge /path/to/project --depth 2     # shallow tree
forge --json                         # JSON to pipe anywhere
```

### JSON output

`forge --json` produces a structured report perfect for scripts and CI:

```bash
forge --json | jq '.languages[0], .health.score'
```

```json
{
  "project": { "name": "your-project", "file_count": 20, "dir_count": 4 },
  "languages": [{ "name": "Python", "files": 15, "code_lines": 1267, "percent": 89.6 }],
  "technologies": [{ "name": "Python (pyproject)", "config_file": "pyproject.toml" }],
  "git": { "is_repo": true, "branch": "main", "total_commits": 10 },
  "health": { "score": 83, "checks": [] },
  "largest_files": [],
  "directory_sizes": [],
  "file_types": { "text": 19, "binary": 1 }
}
```

## 🔧 Customizing analysis — `.forgeignore`

Forge ignores heavy machinery by default: `node_modules`, `.git`, `.venv`,
`__pycache__`, `dist`, `build`, `target` and more.

Add a `.forgeignore` file at the project root to skip anything else, using
gitignore-style patterns:

```gitignore
# skip generated directories (trailing / = directory only)
generated/
build/

# skip files matching a glob
*.min.js

# skip a nested directory anywhere
vendor/
```

## 🏗 Project structure

```
forge/
├── main.py                  # CLI entry point & command routing
├── install.sh               # one-command installer
├── analyzers/               # analysis engines
│   ├── files.py             # scanning, tree, sizes, file types
│   ├── languages.py         # extension map & line counting
│   ├── technologies.py      # config-file detection
│   ├── git.py               # git subprocess queries
│   └── health.py            # health checklist & scoring
├── ui/
│   └── display.py           # rich tables, panels, JSON builder
├── utils/
│   └── ignore.py            # built-in + .forgeignore rules
└── tests/                   # pytest suite
```

## 🧪 Development

```bash
pip install -e ".[dev]"   # install with test dependencies
pytest tests/             # run the test suite
```

The codebase is deliberately small and modular — each analyzer is independent,
so extending Forge is as easy as adding one file and one command.

## 🗺 Roadmap

- [ ] HTML / PDF report export
- [ ] Compare two projects side by side
- [ ] Duplicate file detection
- [ ] Dependency graph count
- [ ] Dead code hints (unused imports)

## 📄 License

[MIT](LICENSE) © Forge Team