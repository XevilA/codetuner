# GenAI Studio - Full Edition 🚀

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![PyQt6](https://img.shields.io/badge/PyQt6-6.5+-green.svg)](https://pypi.org/project/PyQt6/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-macOS%20|%20Windows%20|%20Linux-lightgrey.svg)]()

> **Complete Professional IDE with Auto-Complete, Git Integration, Debugger & Custom Themes**

<p align="center">
  <img src="https://img.shields.io/badge/Auto--Complete-✅-brightgreen" alt="Auto-Complete">
  <img src="https://img.shields.io/badge/Git%20Integration-✅-orange" alt="Git">
  <img src="https://img.shields.io/badge/Debugger-✅-red" alt="Debugger">
  <img src="https://img.shields.io/badge/Custom%20Themes-✅-purple" alt="Themes">
</p>

---

## 📋 Table of Contents

- [Features](#-features)
- [Screenshots](#-screenshots)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Feature Guide](#-feature-guide)
- [Keyboard Shortcuts](#-keyboard-shortcuts)
- [Customization](#-customization)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)

---

## ✨ Features

### Core Features

| Feature | Description | Status |
|---------|-------------|--------|
| **Auto-Complete** | Smart code completion with Python keywords & functions | ✅ |
| **Git Integration** | Full Git workflow (status, add, commit, push, pull) | ✅ |
| **Python Debugger** | Run & debug Python code with real-time output | ✅ |
| **Custom Themes** | Create and save your own color themes | ✅ |

### Additional Features

| Feature | Description |
|---------|-------------|
| Line Numbers | Gutter with line numbers |
| Syntax Highlighting | 10+ language support via Pygments |
| AI Refactoring | Refactor code using Gemini, GPT-4o, or Claude |
| Multi-Tab Editor | Work with multiple files |
| File Navigator | Tree view file browser |
| Debug Console | Real-time output window |
| Status Bar | File info, Git branch, character count |

---

## 📸 Screenshots

### Main Interface

```
┌─────────────────────────────────────────────────────────────────────────┐
│ GenAI Studio [Lang▼] [Model▼]   [▶Run] [🐛Debug] [✨Refactor] [🎨] [⚙️]│
├──────────┬──────────────────────────────────────────┬───────────────────┤
│          │                                          │                   │
│  📁 FILES│           CODE EDITOR                    │     🔀 GIT        │
│          │  ┌──────────────────────────────────┐    │                   │
│  ▸ src/  │ 1│ def calculate():                 │    │  Branch: main     │
│  ▸ lib/  │ 2│     result = 0                   │    │                   │
│  ▸ test/ │ 3│     return result                │    │  Status:          │
│          │  │                                  │    │  M  main.py       │
│          │  │  ┌─────────────┐                 │    │  A  utils.py      │
│  main.py │  │  │ print      │ ← Auto-complete  │    │                   │
│  app.py  │  │  │ process    │                  │    │  [➕ Stage All]   │
│          │  │  │ property   │                  │    │  [💾 Commit]      │
│          │  │  └─────────────┘                 │    │  [⬆️ Push]        │
│          │  └──────────────────────────────────┘    │                   │
│ [Open]   │     [Untitled] [✨ Refactored]           │                   │
├──────────┴──────────────────────────────────────────┴───────────────────┤
│  🐛 DEBUG CONSOLE                                     [Clear] [Stop]    │
│  ▶ Running code...                                                      │
│  Hello, World!                                                          │
│  ✅ Execution completed successfully                                    │
├─────────────────────────────────────────────────────────────────────────┤
│ Ready │ Git: main │ 256 chars                                           │
└─────────────────────────────────────────────────────────────────────────┘
```

### Theme Editor

```
┌─────────────────────────────────────┐
│         Theme Editor                │
├─────────────────────────────────────┤
│ Theme Name: [My Custom Theme    ]   │
│                                     │
│ Background Colors:                  │
│ ├─ Main:      [#1f1f24] [🎨]       │
│ ├─ Sidebar:   [#292a30] [🎨]       │
│ └─ Toolbar:   [#3a3a3f] [🎨]       │
│                                     │
│ Syntax Colors:                      │
│ ├─ Keyword:   [#fc5fa3] [🎨]       │
│ ├─ String:    [#fc6a5d] [🎨]       │
│ └─ Function:  [#67b7a4] [🎨]       │
│                                     │
│         [Save]  [Cancel]            │
└─────────────────────────────────────┘
```

---

## 🚀 Installation

### Requirements

- Python 3.9+
- Git (for Git integration)
- macOS / Windows / Linux

### Step 1: Clone Repository

```bash
git clone https://github.com/yourusername/genai-studio.git
cd genai-studio
```

### Step 2: Install Dependencies

```bash
pip install -r requirements_full.txt
```

Or install manually:

```bash
pip install PyQt6 PyQt6-WebEngine pygments google-generativeai openai anthropic python-dotenv
```

### Step 3: Configure API Keys (Optional)

Create a `.env` file:

```env
GEMINI_API_KEY=your_gemini_key
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
```

Or configure via Settings (⚙️) in the app.

### Step 4: Run

```bash
python genai_studio_full.py
```

---

## 🎯 Quick Start

### 1. Auto-Complete

```python
# Type 2+ characters to trigger suggestions
pr  # → shows: print, process, property
    # Press Tab or Enter to complete

# Auto-indent after colon
def hello():
    |  # ← Cursor auto-indented 4 spaces
```

### 2. Git Workflow

```bash
# 1. Open a folder with Git repository
# 2. Edit your files
# 3. View status in Git panel (right side)
# 4. Click [➕ Stage All]
# 5. Enter commit message
# 6. Click [💾 Commit]
# 7. Click [⬆️ Push]
```

### 3. Run & Debug

```python
# Write your code
print("Hello, World!")

# Click [▶ Run] to execute
# Click [🐛 Debug] for debug mode
# View output in Debug Console
```

### 4. Custom Themes

1. Click **🎨** in toolbar
2. Select **"Create Custom Theme..."**
3. Pick colors for each element
4. Enter theme name
5. Click **Save**

---

## 📖 Feature Guide

### Auto-Complete

The editor provides intelligent code completion:

| Trigger | Action |
|---------|--------|
| Type 2+ chars | Show suggestions popup |
| `Tab` / `Enter` | Insert selected completion |
| `Escape` | Close popup |
| `:` + `Enter` | Auto-indent next line |

**Supported completions:**

- Python keywords (`def`, `class`, `if`, `for`, etc.)
- Built-in functions (`print`, `len`, `range`, etc.)
- Common imports (`import`, `from`, `numpy`, etc.)

### Git Integration

| Button | Command | Description |
|--------|---------|-------------|
| 🔄 Refresh | `git status` | Update file status |
| ➕ Stage All | `git add .` | Stage all changes |
| 💾 Commit | `git commit -m` | Commit with message |
| ⬆️ Push | `git push` | Push to remote |
| ⬇️ Pull | `git pull` | Pull from remote |

**Status indicators:**

- `M` - Modified
- `A` - Added
- `D` - Deleted
- `??` - Untracked

### Python Debugger

| Button | Action |
|--------|--------|
| ▶ Run | Execute Python code |
| 🐛 Debug | Run with debug mode |
| Stop | Terminate execution |
| Clear | Clear console output |

**Manual breakpoint:**

```python
import pdb; pdb.set_trace()  # Add this line
```

### Theme System

**Built-in themes:**

- 🌙 Xcode Dark (default)
- ☀️ Xcode Light
- 🐙 GitHub Dark
- 🧛 Dracula

**Customizable colors:**

- Background (main, sidebar, toolbar, editor)
- Foreground (text, comments, line numbers)
- Syntax (keywords, strings, functions, variables)
- Accent (selection, buttons, highlights)

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+Space` | Trigger auto-complete |
| `Tab` | Insert completion |
| `Ctrl+R` | Run code |
| `Ctrl+D` | Debug code |
| `Ctrl+S` | Save file |
| `Ctrl+O` | Open file |
| `Ctrl+W` | Close tab |

> **Note:** On macOS, use `Cmd` instead of `Ctrl`

---

## 🔧 Customization

### Add Custom Keywords

Edit `CodeEditor.setup_completer()`:

```python
keywords = [
    # Add your custom keywords
    "MyClass",
    "my_function",
    "CONSTANT_VALUE",
]
```

### Add Git Commands

Extend `GitManager` class:

```python
def my_custom_command(self):
    return self.run_git_command(['your', 'command', 'here'])
```

### Add New Theme

Edit `ThemeManager.DEFAULT_THEMES`:

```python
"My Theme": {
    "name": "My Theme",
    "bg_main": "#000000",
    "bg_sidebar": "#1a1a1a",
    "fg_text": "#ffffff",
    # ... more colors
}
```

### Add Language Support

Edit `LanguageDetector.LANGUAGES`:

```python
"Kotlin": {
    "exts": [".kt", ".kts"],
    "lexer": "kotlin"
}
```

---

## 🐛 Troubleshooting

### Auto-Complete Not Working

**Problem:** Suggestions don't appear

**Solution:**

1. Type at least 2 characters
2. Press `Ctrl+Space` manually
3. Check if `QCompleter` is initialized

### Git Not Found

**Problem:** "No repository path set"

**Solution:**

1. Open a folder containing `.git`
2. Or initialize: `git init` in your project
3. Click 🔄 Refresh

### Debug Not Running

**Problem:** Code doesn't execute

**Solution:**

1. Verify Python installed: `python3 --version`
2. Check for syntax errors
3. Ensure file permissions

### Theme Not Saving

**Problem:** Custom theme disappears

**Solution:**

1. Check write permissions
2. Try saving again
3. Restart application

---

## 📊 System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| CPU | Dual-core 2.0 GHz | Quad-core 3.0 GHz+ |
| RAM | 4 GB | 8 GB+ |
| Storage | 2 GB | 5 GB+ |
| Python | 3.9 | 3.10+ |

**Tested platforms:**

- ✅ macOS 13+ (Ventura, Sonoma)
- ✅ Windows 10/11
- ✅ Ubuntu 22.04+

---

## 📁 Project Structure

```
genai-studio/
├── genai_studio_full.py    # Main application (1,700+ lines)
├── requirements_full.txt   # Dependencies
├── README.md               # This file
├── .env                    # API keys (create this)
└── themes/                 # Custom themes (auto-created)
```

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) - GUI Framework
- [Pygments](https://pygments.org/) - Syntax Highlighting
- [Google Gemini](https://ai.google.dev/) - AI API
- [OpenAI](https://openai.com/) - AI API
- [Anthropic](https://anthropic.com/) - AI API

---

## 📞 Contact

**Author:** Kriangkrai - SPU AI CLUB

**Project Link:** [https://github.com/yourusername/genai-studio](https://github.com/yourusername/genai-studio)

---

<p align="center">
  Made with ❤️ for developers and students
</p>

<p align="center">
  <b>Happy Coding! 🚀💻✨</b>
</p>
