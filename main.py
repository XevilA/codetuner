import sys
import os
import re
import json
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from abc import ABC, abstractmethod
from dotenv import load_dotenv

# --- PyQt6 Imports ---
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QTreeView, QTextEdit, QPushButton, QLabel, QFileDialog, QMessageBox,
    QComboBox, QProgressBar, QDialog, QFormLayout, QLineEdit,
    QDialogButtonBox, QFrame, QTabWidget, QMenu, QSizePolicy,
    QStatusBar, QToolBar, QCheckBox, QSpinBox, QTextBrowser, QListWidget,
    QListWidgetItem, QStackedWidget, QScrollArea, QPlainTextEdit,
    QCompleter, QColorDialog, QInputDialog
)
from PyQt6.QtCore import (
    Qt, QDir, QThread, pyqtSignal, QSettings, QSize, QTimer,
    QPropertyAnimation, QEasingCurve, QPoint, QMimeData, QUrl, QProcess,
    QStringListModel, QRect, QObject
)
from PyQt6.QtGui import (
    QFileSystemModel, QFont, QColor, QSyntaxHighlighter, QTextCharFormat,
    QIcon, QAction, QKeySequence, QShortcut, QPalette, QDrag, QPixmap,
    QTextCursor, QPainter, QTextOption
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineSettings

# --- AI Clients ---
import google.generativeai as genai
from openai import OpenAI
from anthropic import Anthropic

# --- Syntax Highlighting ---
import pygments
from pygments import lexers, styles, token

load_dotenv()

# ==========================================
# 1. THEME MANAGER WITH CUSTOM THEMES
# ==========================================

class ThemeManager:
    """Advanced theme manager with custom theme editor"""

    DEFAULT_THEMES = {
        "Xcode Dark": {
            "name": "Xcode Dark",
            "bg_main": "#1f1f24",
            "bg_sidebar": "#292a30",
            "bg_toolbar": "#3a3a3f",
            "bg_editor": "#1f1f24",
            "bg_preview": "#2d2d32",
            "fg_text": "#ffffff",
            "fg_sub": "#8e8e93",
            "fg_comment": "#6c7986",
            "accent": "#0a84ff",
            "accent_hover": "#0070e0",
            "border": "#3a3a3f",
            "selection": "#0a84ff",
            "line_number": "#6e6e73",
            "current_line": "#2d2d32",
            "success": "#30d158",
            "error": "#ff453a",
            "warning": "#ffd60a",
            "keyword": "#fc5fa3",
            "string": "#fc6a5d",
            "function": "#67b7a4",
            "variable": "#acf2e4",
            "pygment": "monokai"
        },
        "Xcode Light": {
            "name": "Xcode Light",
            "bg_main": "#ffffff",
            "bg_sidebar": "#f5f5f7",
            "bg_toolbar": "#ececec",
            "bg_editor": "#ffffff",
            "bg_preview": "#f5f5f7",
            "fg_text": "#1d1d1f",
            "fg_sub": "#86868b",
            "fg_comment": "#707f8c",
            "accent": "#007aff",
            "accent_hover": "#0051d5",
            "border": "#d2d2d7",
            "selection": "#b3d7ff",
            "line_number": "#86868b",
            "current_line": "#f0f0f0",
            "success": "#34c759",
            "error": "#ff3b30",
            "warning": "#ff9500",
            "keyword": "#ad3da4",
            "string": "#d12f1b",
            "function": "#3e8087",
            "variable": "#0f68a0",
            "pygment": "xcode"
        },
        "GitHub Dark": {
            "name": "GitHub Dark",
            "bg_main": "#0d1117",
            "bg_sidebar": "#161b22",
            "bg_toolbar": "#21262d",
            "bg_editor": "#0d1117",
            "bg_preview": "#161b22",
            "fg_text": "#c9d1d9",
            "fg_sub": "#8b949e",
            "fg_comment": "#8b949e",
            "accent": "#58a6ff",
            "accent_hover": "#388bfd",
            "border": "#30363d",
            "selection": "#58a6ff",
            "line_number": "#6e7681",
            "current_line": "#161b22",
            "success": "#3fb950",
            "error": "#f85149",
            "warning": "#d29922",
            "keyword": "#ff7b72",
            "string": "#a5d6ff",
            "function": "#d2a8ff",
            "variable": "#ffa657",
            "pygment": "monokai"
        },
        "Dracula": {
            "name": "Dracula",
            "bg_main": "#282a36",
            "bg_sidebar": "#21222c",
            "bg_toolbar": "#343746",
            "bg_editor": "#282a36",
            "bg_preview": "#21222c",
            "fg_text": "#f8f8f2",
            "fg_sub": "#6272a4",
            "fg_comment": "#6272a4",
            "accent": "#bd93f9",
            "accent_hover": "#9580d4",
            "border": "#44475a",
            "selection": "#44475a",
            "line_number": "#6272a4",
            "current_line": "#44475a",
            "success": "#50fa7b",
            "error": "#ff5555",
            "warning": "#ffb86c",
            "keyword": "#ff79c6",
            "string": "#f1fa8c",
            "function": "#8be9fd",
            "variable": "#50fa7b",
            "pygment": "dracula"
        }
    }

    @staticmethod
    def load_custom_themes():
        """Load custom themes from settings"""
        settings = QSettings("GenAI_Studio", "CustomThemes")
        custom_themes = {}

        theme_count = settings.beginReadArray("themes")
        for i in range(theme_count):
            settings.setArrayIndex(i)
            theme_name = settings.value("name")
            if theme_name:
                custom_themes[theme_name] = {
                    key: settings.value(key, "#000000")
                    for key in ThemeManager.DEFAULT_THEMES["Xcode Dark"].keys()
                }
        settings.endArray()

        return custom_themes

    @staticmethod
    def save_custom_theme(theme_name, theme_data):
        """Save custom theme"""
        settings = QSettings("GenAI_Studio", "CustomThemes")

        # Load existing themes
        all_themes = ThemeManager.load_custom_themes()
        all_themes[theme_name] = theme_data

        # Save back
        settings.beginWriteArray("themes")
        for i, (name, data) in enumerate(all_themes.items()):
            settings.setArrayIndex(i)
            settings.setValue("name", name)
            for key, value in data.items():
                settings.setValue(key, value)
        settings.endArray()

    @staticmethod
    def get_all_themes():
        """Get all themes (default + custom)"""
        themes = dict(ThemeManager.DEFAULT_THEMES)
        themes.update(ThemeManager.load_custom_themes())
        return themes

    @staticmethod
    def get_stylesheet(theme_name):
        """Generate stylesheet from theme"""
        all_themes = ThemeManager.get_all_themes()
        t = all_themes.get(theme_name, ThemeManager.DEFAULT_THEMES["Xcode Dark"])

        css = f"""
            /* Global */
            * {{
                font-family: -apple-system, "SF Mono", "Menlo", monospace;
                font-size: 13px;
            }}

            QMainWindow {{
                background-color: {t['bg_main']};
            }}

            /* Toolbar */
            QToolBar {{
                background-color: {t['bg_toolbar']};
                border: none;
                border-bottom: 1px solid {t['border']};
                spacing: 8px;
                padding: 4px 12px;
            }}

            QToolBar QLabel {{
                color: {t['fg_text']};
                font-weight: 600;
                padding: 0 8px;
            }}

            QToolBar QPushButton {{
                background-color: transparent;
                color: {t['fg_text']};
                border: 1px solid {t['border']};
                padding: 6px 16px;
                border-radius: 6px;
                font-weight: 500;
            }}

            QToolBar QPushButton:hover {{
                background-color: {t['accent']};
                color: white;
                border-color: {t['accent']};
            }}

            QToolBar QPushButton#PlayButton {{
                background-color: {t['accent']};
                color: white;
                border: none;
                padding: 6px 20px;
                font-weight: 600;
            }}

            QToolBar QPushButton#PlayButton:hover {{
                background-color: {t['accent_hover']};
            }}

            /* Sidebar */
            #NavigatorPane {{
                background-color: {t['bg_sidebar']};
                border-right: 1px solid {t['border']};
            }}

            QTreeView {{
                background-color: {t['bg_sidebar']};
                border: none;
                outline: none;
                padding: 8px;
                color: {t['fg_text']};
            }}

            QTreeView::item {{
                padding: 6px 12px;
                border-radius: 6px;
                margin: 1px 4px;
            }}

            QTreeView::item:selected {{
                background-color: {t['selection']};
                color: white;
            }}

            QTreeView::item:hover {{
                background-color: {t['selection']}33;
            }}

            /* Editor */
            #EditorPane {{
                background-color: {t['bg_editor']};
            }}

            QPlainTextEdit, QTextEdit {{
                background-color: {t['bg_editor']};
                color: {t['fg_text']};
                border: none;
                padding: 8px;
                font-family: "SF Mono", "Menlo", monospace;
                font-size: 13px;
                line-height: 1.5;
                selection-background-color: {t['selection']};
                selection-color: white;
            }}

            /* Line Number Area */
            #LineNumberArea {{
                background-color: {t['bg_sidebar']};
                color: {t['line_number']};
                border-right: 1px solid {t['border']};
            }}

            /* Preview Pane */
            #PreviewPane {{
                background-color: {t['bg_preview']};
                border-left: 1px solid {t['border']};
            }}

            #PreviewControls {{
                background-color: {t['bg_toolbar']};
                border-bottom: 1px solid {t['border']};
                padding: 8px 12px;
            }}

            /* Git Panel */
            #GitPanel {{
                background-color: {t['bg_sidebar']};
                border-left: 1px solid {t['border']};
            }}

            /* Debug Console */
            #DebugConsole {{
                background-color: {t['bg_editor']};
                color: {t['fg_text']};
                border-top: 1px solid {t['border']};
                font-family: "SF Mono", monospace;
                font-size: 12px;
            }}

            /* Controls */
            QComboBox {{
                background-color: {t['bg_toolbar']};
                border: 1px solid {t['border']};
                border-radius: 6px;
                padding: 6px 12px;
                color: {t['fg_text']};
                min-width: 120px;
            }}

            QComboBox:hover {{
                border-color: {t['accent']};
            }}

            QComboBox::drop-down {{
                border: none;
                width: 24px;
            }}

            QComboBox QAbstractItemView {{
                background-color: {t['bg_toolbar']};
                border: 1px solid {t['border']};
                border-radius: 8px;
                padding: 4px;
                selection-background-color: {t['accent']};
                selection-color: white;
            }}

            QLineEdit {{
                background-color: {t['bg_toolbar']};
                border: 1px solid {t['border']};
                border-radius: 6px;
                padding: 6px 12px;
                color: {t['fg_text']};
            }}

            QLineEdit:focus {{
                border-color: {t['accent']};
            }}

            /* List Widgets */
            QListWidget {{
                background-color: {t['bg_sidebar']};
                border: none;
                outline: none;
                padding: 4px;
                color: {t['fg_text']};
            }}

            QListWidget::item {{
                padding: 8px 12px;
                border-radius: 6px;
                margin: 2px;
            }}

            QListWidget::item:selected {{
                background-color: {t['selection']};
                color: white;
            }}

            QListWidget::item:hover {{
                background-color: {t['selection']}33;
            }}

            /* Status Bar */
            QStatusBar {{
                background-color: {t['bg_toolbar']};
                border-top: 1px solid {t['border']};
                color: {t['fg_sub']};
                font-size: 11px;
            }}

            /* Splitter */
            QSplitter::handle {{
                background-color: {t['border']};
                width: 1px;
            }}

            /* Scrollbar */
            QScrollBar:vertical {{
                background: transparent;
                width: 10px;
                margin: 0px;
            }}

            QScrollBar::handle:vertical {{
                background: {t['fg_sub']};
                min-height: 30px;
                border-radius: 5px;
                margin: 2px;
            }}

            QScrollBar::handle:vertical:hover {{
                background: {t['border']};
            }}

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                height: 0px;
            }}

            /* Tabs */
            QTabWidget::pane {{
                border: none;
                border-top: 1px solid {t['border']};
            }}

            QTabBar::tab {{
                background: {t['bg_toolbar']};
                color: {t['fg_sub']};
                padding: 10px 20px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                margin-right: 2px;
            }}

            QTabBar::tab:selected {{
                background: {t['bg_editor']};
                color: {t['fg_text']};
                font-weight: 600;
                border-top: 2px solid {t['accent']};
            }}

            QTabBar::tab:hover {{
                background: {t['selection']}33;
            }}
        """

        return css, t

# ==========================================
# 2. CODE EDITOR WITH AUTO-COMPLETE
# ==========================================

class LineNumberArea(QWidget):
    """Line number area for code editor"""

    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self):
        return QSize(self.editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self.editor.line_number_area_paint_event(event)


class CodeEditor(QPlainTextEdit):
    """Advanced code editor with line numbers and auto-complete"""

    def __init__(self, parent=None):
        super().__init__(parent)

        # Line numbers
        self.line_number_area = LineNumberArea(self)

        # Auto-completion
        self.completer = None
        self.setup_completer()

        # Connect signals
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)

        # Settings
        self.setTabStopDistance(40)  # 4 spaces
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)

        # Initialize
        self.update_line_number_area_width(0)
        self.highlight_current_line()

    def setup_completer(self):
        """Setup auto-completion"""
        # Python keywords and common functions
        keywords = [
            # Python keywords
            "False", "None", "True", "and", "as", "assert", "async", "await",
            "break", "class", "continue", "def", "del", "elif", "else", "except",
            "finally", "for", "from", "global", "if", "import", "in", "is",
            "lambda", "nonlocal", "not", "or", "pass", "raise", "return",
            "try", "while", "with", "yield",
            # Common functions
            "print", "len", "range", "str", "int", "float", "list", "dict",
            "set", "tuple", "open", "input", "type", "isinstance", "enumerate",
            "zip", "map", "filter", "sorted", "reversed", "sum", "min", "max",
            # Common imports
            "import", "from", "numpy", "pandas", "requests", "json", "sys",
            "os", "datetime", "math", "random", "re", "collections"
        ]

        self.completer = QCompleter(keywords, self)
        self.completer.setWidget(self)
        self.completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.completer.activated.connect(self.insert_completion)

    def insert_completion(self, completion):
        """Insert completion text"""
        if self.completer.widget() != self:
            return

        tc = self.textCursor()
        extra = len(completion) - len(self.completer.completionPrefix())
        tc.movePosition(QTextCursor.MoveOperation.Left)
        tc.movePosition(QTextCursor.MoveOperation.EndOfWord)
        tc.insertText(completion[-extra:])
        self.setTextCursor(tc)

    def text_under_cursor(self):
        """Get text under cursor for completion"""
        tc = self.textCursor()
        tc.select(QTextCursor.SelectionType.WordUnderCursor)
        return tc.selectedText()

    def keyPressEvent(self, event):
        """Handle key press for auto-completion"""
        # Handle completion popup
        if self.completer and self.completer.popup().isVisible():
            if event.key() in (
                Qt.Key.Key_Enter,
                Qt.Key.Key_Return,
                Qt.Key.Key_Escape,
                Qt.Key.Key_Tab,
                Qt.Key.Key_Backtab
            ):
                event.ignore()
                return

        # Handle auto-indent
        if event.key() == Qt.Key.Key_Return:
            # Get current line indentation
            cursor = self.textCursor()
            cursor.select(QTextCursor.SelectionType.LineUnderCursor)
            line = cursor.selectedText()
            indent = len(line) - len(line.lstrip())

            super().keyPressEvent(event)

            # Add same indentation to new line
            self.insertPlainText(" " * indent)

            # Add extra indent after colon
            if line.rstrip().endswith(":"):
                self.insertPlainText("    ")

            return

        # Regular key press
        super().keyPressEvent(event)

        # Trigger completion
        completion_prefix = self.text_under_cursor()

        if len(completion_prefix) < 2:
            if self.completer:
                self.completer.popup().hide()
            return

        if self.completer:
            if completion_prefix != self.completer.completionPrefix():
                self.completer.setCompletionPrefix(completion_prefix)
                self.completer.popup().setCurrentIndex(
                    self.completer.completionModel().index(0, 0)
                )

            cr = self.cursorRect()
            cr.setWidth(
                self.completer.popup().sizeHintForColumn(0) +
                self.completer.popup().verticalScrollBar().sizeHint().width()
            )
            self.completer.complete(cr)

    def line_number_area_width(self):
        """Calculate line number area width"""
        digits = len(str(max(1, self.blockCount())))
        space = 10 + self.fontMetrics().horizontalAdvance('9') * digits
        return space

    def update_line_number_area_width(self, _):
        """Update line number area width"""
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        """Update line number area on scroll"""
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())

        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    def resizeEvent(self, event):
        """Handle resize"""
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height()))

    def line_number_area_paint_event(self, event):
        """Paint line numbers"""
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor("#292a30"))

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(QColor("#6e6e73"))
                painter.drawText(0, int(top), self.line_number_area.width() - 5,
                               self.fontMetrics().height(), Qt.AlignmentFlag.AlignRight, number)

            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            block_number += 1

    def highlight_current_line(self):
        """Highlight current line"""
        extra_selections = []

        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            line_color = QColor("#2d2d32")
            selection.format.setBackground(line_color)
            selection.format.setProperty(QTextCharFormat.Property.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)

        self.setExtraSelections(extra_selections)

# ==========================================
# 3. GIT INTEGRATION
# ==========================================

class GitManager(QObject):
    """Git integration manager"""

    status_updated = pyqtSignal(dict)
    output_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, repo_path=None):
        super().__init__()
        self.repo_path = repo_path

    def set_repo_path(self, path):
        """Set repository path"""
        self.repo_path = path

    def run_git_command(self, args):
        """Run git command"""
        if not self.repo_path:
            self.error_occurred.emit("No repository path set")
            return None

        try:
            result = subprocess.run(
                ['git'] + args,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                return result.stdout
            else:
                self.error_occurred.emit(result.stderr)
                return None

        except Exception as e:
            self.error_occurred.emit(str(e))
            return None

    def get_status(self):
        """Get git status"""
        output = self.run_git_command(['status', '--porcelain'])
        if output is None:
            return {}

        status = {
            'modified': [],
            'added': [],
            'deleted': [],
            'untracked': []
        }

        for line in output.strip().split('\n'):
            if not line:
                continue

            status_code = line[:2]
            filepath = line[3:]

            if status_code == ' M' or status_code == 'M ':
                status['modified'].append(filepath)
            elif status_code == 'A ':
                status['added'].append(filepath)
            elif status_code == 'D ':
                status['deleted'].append(filepath)
            elif status_code == '??':
                status['untracked'].append(filepath)

        self.status_updated.emit(status)
        return status

    def get_branch(self):
        """Get current branch"""
        output = self.run_git_command(['branch', '--show-current'])
        return output.strip() if output else "unknown"

    def add_files(self, files):
        """Add files to staging"""
        if isinstance(files, str):
            files = [files]

        output = self.run_git_command(['add'] + files)
        if output is not None:
            self.output_ready.emit(f"Added files: {', '.join(files)}")
            self.get_status()

    def commit(self, message):
        """Commit changes"""
        output = self.run_git_command(['commit', '-m', message])
        if output is not None:
            self.output_ready.emit(f"Committed: {message}")
            self.get_status()

    def push(self, remote='origin', branch=None):
        """Push to remote"""
        if branch is None:
            branch = self.get_branch()

        output = self.run_git_command(['push', remote, branch])
        if output is not None:
            self.output_ready.emit(f"Pushed to {remote}/{branch}")

    def pull(self, remote='origin', branch=None):
        """Pull from remote"""
        if branch is None:
            branch = self.get_branch()

        output = self.run_git_command(['pull', remote, branch])
        if output is not None:
            self.output_ready.emit(f"Pulled from {remote}/{branch}")
            self.get_status()

    def get_diff(self, filepath=None):
        """Get diff"""
        args = ['diff']
        if filepath:
            args.append(filepath)

        return self.run_git_command(args)

    def get_log(self, count=10):
        """Get commit log"""
        output = self.run_git_command(['log', f'-{count}', '--oneline'])
        return output if output else ""

# ==========================================
# 4. PYTHON DEBUGGER
# ==========================================

class PythonDebugger(QObject):
    """Python debugger integration"""

    output_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    breakpoint_hit = pyqtSignal(int, dict)

    def __init__(self):
        super().__init__()
        self.process = None
        self.breakpoints = set()

    def add_breakpoint(self, line):
        """Add breakpoint"""
        self.breakpoints.add(line)
        self.output_ready.emit(f"Breakpoint added at line {line}")

    def remove_breakpoint(self, line):
        """Remove breakpoint"""
        self.breakpoints.discard(line)
        self.output_ready.emit(f"Breakpoint removed from line {line}")

    def clear_breakpoints(self):
        """Clear all breakpoints"""
        self.breakpoints.clear()
        self.output_ready.emit("All breakpoints cleared")

    def run_code(self, code, filepath=None):
        """Run code"""
        try:
            # Save code to temp file
            if filepath is None:
                with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                    f.write(code)
                    filepath = f.name

            # Run with python
            self.process = QProcess()
            self.process.readyReadStandardOutput.connect(self._handle_stdout)
            self.process.readyReadStandardError.connect(self._handle_stderr)
            self.process.finished.connect(self._handle_finished)

            self.process.start('python3', [filepath])

            self.output_ready.emit(f"Running {filepath}...")

        except Exception as e:
            self.error_occurred.emit(f"Failed to run code: {e}")

    def debug_code(self, code, filepath=None):
        """Debug code with pdb"""
        try:
            # Insert pdb breakpoints
            lines = code.split('\n')
            for bp in sorted(self.breakpoints, reverse=True):
                if 0 < bp <= len(lines):
                    lines.insert(bp - 1, "import pdb; pdb.set_trace()")

            code_with_bp = '\n'.join(lines)

            # Save and run
            if filepath is None:
                with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                    f.write(code_with_bp)
                    filepath = f.name

            self.output_ready.emit(f"Debugging {filepath}...")
            self.run_code(code_with_bp, filepath)

        except Exception as e:
            self.error_occurred.emit(f"Failed to debug: {e}")

    def stop(self):
        """Stop execution"""
        if self.process and self.process.state() == QProcess.ProcessState.Running:
            self.process.kill()
            self.output_ready.emit("Execution stopped")

    def _handle_stdout(self):
        """Handle stdout"""
        if self.process:
            data = self.process.readAllStandardOutput().data().decode()
            self.output_ready.emit(data)

    def _handle_stderr(self):
        """Handle stderr"""
        if self.process:
            data = self.process.readAllStandardError().data().decode()
            self.error_occurred.emit(data)

    def _handle_finished(self, exit_code, exit_status):
        """Handle process finished"""
        if exit_code == 0:
            self.output_ready.emit("\n✅ Execution completed successfully")
        else:
            self.error_occurred.emit(f"\n❌ Execution failed with code {exit_code}")

# ==========================================
# 5. LANGUAGE DETECTOR & AI (Simplified)
# ==========================================

class LanguageDetector:
    LANGUAGES = {
        "Python": {"exts": [".py"], "lexer": "python"},
        "JavaScript": {"exts": [".js", ".jsx"], "lexer": "javascript"},
        "TypeScript": {"exts": [".ts", ".tsx"], "lexer": "typescript"},
        "HTML": {"exts": [".html"], "lexer": "html"},
        "CSS": {"exts": [".css"], "lexer": "css"},
        "Rust": {"exts": [".rs"], "lexer": "rust"},
        "Go": {"exts": [".go"], "lexer": "go"},
        "Swift": {"exts": [".swift"], "lexer": "swift"},
        "Dart": {"exts": [".dart"], "lexer": "dart"}
    }

    @staticmethod
    def detect(filename):
        ext = os.path.splitext(filename)[1].lower()
        for lang, info in LanguageDetector.LANGUAGES.items():
            if ext in info["exts"]:
                return lang
        return "Text"

    @staticmethod
    def get_lexer_name(lang):
        return LanguageDetector.LANGUAGES.get(lang, {}).get("lexer", "text")

class ConfigManager:
    @staticmethod
    def get_key(provider_type):
        key = os.getenv(f"{provider_type.upper()}_API_KEY")
        if not key:
            key = QSettings("GenAI_Studio", "SecureKeys").value(provider_type, "")
        return key

class AIProviderFactory:
    MODELS = {
        "Gemini 2.0 Flash": {"type": "gemini", "model": "gemini-2.0-flash-exp"},
        "GPT-4o": {"type": "openai", "model": "gpt-4o"},
        "Claude 3.5 Sonnet": {"type": "anthropic", "model": "claude-3-5-sonnet-latest"}
    }

    @staticmethod
    def create(config_name):
        conf = AIProviderFactory.MODELS.get(config_name)
        if not conf:
            raise ValueError("Model Not Found")

        p_type = conf["type"]
        api_key = ConfigManager.get_key(p_type)

        if not api_key:
            raise ValueError(f"Missing API Key for {p_type}")

        if p_type == "gemini":
            genai.configure(api_key=api_key)
            return genai.GenerativeModel(conf["model"])
        elif p_type == "openai":
            return OpenAI(api_key=api_key)
        elif p_type == "anthropic":
            return Anthropic(api_key=api_key)

class RefactorWorker(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, model_name, code, lang):
        super().__init__()
        self.model_name = model_name
        self.code = code
        self.lang = lang

    def run(self):
        try:
            backend = AIProviderFactory.create(self.model_name)
            conf = AIProviderFactory.MODELS.get(self.model_name)

            prompt = f"""Refactor this {self.lang} code:

```{self.lang}
{self.code}
```

Provide:
1. Summary
2. Complete refactored code
3. Key improvements"""

            if conf["type"] == "gemini":
                resp = backend.generate_content(prompt)
                self.finished.emit(resp.text)
            elif conf["type"] == "openai":
                resp = backend.chat.completions.create(
                    model=conf["model"],
                    messages=[{"role": "user", "content": prompt}]
                )
                self.finished.emit(resp.choices[0].message.content)
            elif conf["type"] == "anthropic":
                msg = backend.messages.create(
                    model=conf["model"],
                    max_tokens=8192,
                    messages=[{"role": "user", "content": prompt}]
                )
                self.finished.emit(msg.content[0].text)
        except Exception as e:
            self.error.emit(str(e))

# ==========================================
# 6. SYNTAX HIGHLIGHTER
# ==========================================

class PygmentsHighlighter(QSyntaxHighlighter):
    def __init__(self, document, lexer_name='python', style='monokai'):
        super().__init__(document)
        try:
            self._lexer = lexers.get_lexer_by_name(lexer_name)
        except:
            self._lexer = lexers.get_lexer_by_name("text")

        try:
            self._style = styles.get_style_by_name(style)
        except:
            self._style = styles.get_style_by_name("monokai")

    def highlightBlock(self, text):
        try:
            tokens = list(pygments.lex(text, self._lexer))
            index = 0

            for token_type, value in tokens:
                text_fmt = QTextCharFormat()

                try:
                    style = self._style.style_for_token(token_type)
                    if style['color']:
                        text_fmt.setForeground(QColor(f"#{style['color']}"))
                    if style.get('bold'):
                        text_fmt.setFontWeight(QFont.Weight.Bold)

                    length = len(value)
                    self.setFormat(index, length, text_fmt)
                    index += length
                except:
                    index += len(value)
        except:
            pass

# ==========================================
# 7. THEME EDITOR DIALOG
# ==========================================

class ThemeEditorDialog(QDialog):
    """Theme editor for creating custom themes"""

    def __init__(self, parent=None, base_theme=None):
        super().__init__(parent)
        self.setWindowTitle("Theme Editor")
        self.resize(600, 700)

        self.theme_data = dict(base_theme) if base_theme else dict(ThemeManager.DEFAULT_THEMES["Xcode Dark"])

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Theme name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Theme Name:"))
        self.name_input = QLineEdit()
        self.name_input.setText(self.theme_data.get("name", "My Custom Theme"))
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)

        # Color pickers
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QFormLayout(scroll_widget)

        self.color_buttons = {}

        color_categories = {
            "Background Colors": ["bg_main", "bg_sidebar", "bg_toolbar", "bg_editor", "bg_preview"],
            "Foreground Colors": ["fg_text", "fg_sub", "fg_comment"],
            "Accent Colors": ["accent", "accent_hover", "selection"],
            "Line Colors": ["border", "line_number", "current_line"],
            "Status Colors": ["success", "error", "warning"],
            "Syntax Colors": ["keyword", "string", "function", "variable"]
        }

        for category, keys in color_categories.items():
            scroll_layout.addRow(QLabel(f"<b>{category}</b>"))

            for key in keys:
                if key in self.theme_data:
                    btn = QPushButton(self.theme_data[key])
                    btn.setStyleSheet(f"background-color: {self.theme_data[key]}; color: white; padding: 8px;")
                    btn.clicked.connect(lambda checked, k=key, b=btn: self.pick_color(k, b))

                    self.color_buttons[key] = btn
                    scroll_layout.addRow(key.replace("_", " ").title() + ":", btn)

        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.save_theme)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def pick_color(self, key, button):
        """Pick color"""
        color = QColorDialog.getColor(QColor(self.theme_data[key]), self)
        if color.isValid():
            hex_color = color.name()
            self.theme_data[key] = hex_color
            button.setText(hex_color)
            button.setStyleSheet(f"background-color: {hex_color}; color: white; padding: 8px;")

    def save_theme(self):
        """Save theme"""
        theme_name = self.name_input.text().strip()
        if not theme_name:
            QMessageBox.warning(self, "Error", "Please enter a theme name")
            return

        self.theme_data["name"] = theme_name
        ThemeManager.save_custom_theme(theme_name, self.theme_data)

        QMessageBox.information(self, "Success", f"Theme '{theme_name}' saved!")
        self.accept()

# ==========================================
# 8. MAIN WINDOW (COMPLETE)
# ==========================================

class FullFeatureIDE(QMainWindow):
    """Complete IDE with all features"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("GenAI Studio - Full Edition")
        self.resize(1800, 1000)

        self.current_theme = "Xcode Dark"
        self.current_file = None
        self.current_repo_path = None

        # Managers
        self.git_manager = GitManager()
        self.debugger = PythonDebugger()

        self.setup_ui()
        self.apply_theme()
        self.connect_signals()

    def setup_ui(self):
        """Setup complete UI"""

        # === TOOLBAR ===
        self.toolbar = QToolBar()
        self.toolbar.setMovable(False)
        self.addToolBar(self.toolbar)

        self.toolbar.addWidget(QLabel("GenAI Studio"))
        self.toolbar.addSeparator()

        # Language
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(sorted(LanguageDetector.LANGUAGES.keys()) + ["Text"])
        self.lang_combo.currentTextChanged.connect(self.on_language_changed)
        self.toolbar.addWidget(QLabel("Language:"))
        self.toolbar.addWidget(self.lang_combo)

        self.toolbar.addSeparator()

        # Model
        self.model_combo = QComboBox()
        self.model_combo.addItems(AIProviderFactory.MODELS.keys())
        self.toolbar.addWidget(QLabel("Model:"))
        self.toolbar.addWidget(self.model_combo)

        # Spacer
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.toolbar.addWidget(spacer)

        # Actions
        self.btn_run = QPushButton("▶ Run")
        self.btn_run.setObjectName("PlayButton")
        self.btn_run.clicked.connect(self.run_code)
        self.toolbar.addWidget(self.btn_run)

        self.btn_debug = QPushButton("🐛 Debug")
        self.btn_debug.clicked.connect(self.debug_code)
        self.toolbar.addWidget(self.btn_debug)

        self.btn_refactor = QPushButton("✨ Refactor")
        self.btn_refactor.clicked.connect(self.refactor_code)
        self.toolbar.addWidget(self.btn_refactor)

        self.toolbar.addSeparator()

        # Theme menu
        btn_theme = QPushButton("🎨")
        theme_menu = QMenu()
        for theme_name in ThemeManager.get_all_themes().keys():
            theme_menu.addAction(theme_name, lambda t=theme_name: self.switch_theme(t))
        theme_menu.addSeparator()
        theme_menu.addAction("Create Custom Theme...", self.create_custom_theme)
        btn_theme.setMenu(theme_menu)
        self.toolbar.addWidget(btn_theme)

        btn_settings = QPushButton("⚙️")
        btn_settings.clicked.connect(self.open_settings)
        self.toolbar.addWidget(btn_settings)

        # === MAIN LAYOUT ===
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Top splitter (Navigator + Editor + Git)
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)

        # === LEFT: NAVIGATOR ===
        navigator = self.create_navigator()
        self.main_splitter.addWidget(navigator)

        # === CENTER: EDITOR ===
        editor_container = self.create_editor()
        self.main_splitter.addWidget(editor_container)

        # === RIGHT: GIT PANEL ===
        git_panel = self.create_git_panel()
        self.main_splitter.addWidget(git_panel)

        self.main_splitter.setSizes([250, 1000, 300])

        # Bottom splitter (Main + Debug Console)
        self.v_splitter = QSplitter(Qt.Orientation.Vertical)
        self.v_splitter.addWidget(self.main_splitter)

        # === DEBUG CONSOLE ===
        debug_console = self.create_debug_console()
        self.v_splitter.addWidget(debug_console)

        self.v_splitter.setSizes([700, 300])

        main_layout.addWidget(self.v_splitter)

        # === STATUS BAR ===
        self.status_bar = QStatusBar()
        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label)

        self.git_status_label = QLabel("No Git")
        self.status_bar.addPermanentWidget(self.git_status_label)

        self.char_count = QLabel("0 chars")
        self.status_bar.addPermanentWidget(self.char_count)

        self.setStatusBar(self.status_bar)

    def create_navigator(self):
        """Create navigator pane"""
        navigator = QFrame()
        navigator.setObjectName("NavigatorPane")
        nav_layout = QVBoxLayout(navigator)
        nav_layout.setContentsMargins(0, 0, 0, 0)

        nav_header = QLabel("  📁 FILES")
        nav_header.setStyleSheet("padding: 12px; font-weight: 600;")
        nav_layout.addWidget(nav_header)

        self.fs_model = QFileSystemModel()
        self.fs_model.setRootPath(QDir.homePath())

        self.tree = QTreeView()
        self.tree.setModel(self.fs_model)
        self.tree.setRootIndex(self.fs_model.index(QDir.homePath()))
        self.tree.setHeaderHidden(True)

        for i in range(1, 4):
            self.tree.hideColumn(i)

        self.tree.doubleClicked.connect(self.open_file)
        nav_layout.addWidget(self.tree)

        btn_open = QPushButton("Open Folder...")
        btn_open.clicked.connect(self.select_folder)
        nav_layout.addWidget(btn_open)

        return navigator

    def create_editor(self):
        """Create editor pane"""
        container = QFrame()
        container.setObjectName("EditorPane")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)

        self.editor_tabs = QTabWidget()
        self.editor_tabs.setTabsClosable(True)
        self.editor_tabs.setMovable(True)
        self.editor_tabs.tabCloseRequested.connect(self.close_tab)

        # Main editor with line numbers and auto-complete
        self.editor = CodeEditor()
        self.editor.setPlaceholderText("Open a file or start coding...")
        self.editor.setFont(QFont("SF Mono", 13))
        self.editor.textChanged.connect(self.on_text_changed)

        self.editor_tabs.addTab(self.editor, "Untitled")

        layout.addWidget(self.editor_tabs)

        return container

    def create_git_panel(self):
        """Create Git panel"""
        panel = QFrame()
        panel.setObjectName("GitPanel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(8, 8, 8, 8)

        # Header
        header = QLabel("🔀 GIT")
        header.setStyleSheet("font-weight: 600; padding: 8px;")
        layout.addWidget(header)

        # Branch
        self.git_branch_label = QLabel("Branch: -")
        layout.addWidget(self.git_branch_label)

        # Status
        layout.addWidget(QLabel("Status:"))
        self.git_status_list = QListWidget()
        self.git_status_list.setMaximumHeight(200)
        layout.addWidget(self.git_status_list)

        # Commit
        layout.addWidget(QLabel("Commit Message:"))
        self.git_commit_input = QLineEdit()
        self.git_commit_input.setPlaceholderText("Enter commit message...")
        layout.addWidget(self.git_commit_input)

        # Buttons
        btn_layout = QVBoxLayout()

        btn_refresh = QPushButton("🔄 Refresh")
        btn_refresh.clicked.connect(self.git_refresh)
        btn_layout.addWidget(btn_refresh)

        btn_add_all = QPushButton("➕ Stage All")
        btn_add_all.clicked.connect(self.git_add_all)
        btn_layout.addWidget(btn_add_all)

        btn_commit = QPushButton("💾 Commit")
        btn_commit.clicked.connect(self.git_commit)
        btn_layout.addWidget(btn_commit)

        btn_push = QPushButton("⬆️ Push")
        btn_push.clicked.connect(self.git_push)
        btn_layout.addWidget(btn_push)

        btn_pull = QPushButton("⬇️ Pull")
        btn_pull.clicked.connect(self.git_pull)
        btn_layout.addWidget(btn_pull)

        layout.addLayout(btn_layout)
        layout.addStretch()

        # Log
        layout.addWidget(QLabel("Recent Commits:"))
        self.git_log_text = QTextBrowser()
        self.git_log_text.setMaximumHeight(150)
        layout.addWidget(self.git_log_text)

        return panel

    def create_debug_console(self):
        """Create debug console"""
        console_frame = QFrame()
        console_frame.setObjectName("DebugConsole")
        layout = QVBoxLayout(console_frame)
        layout.setContentsMargins(8, 8, 8, 8)

        # Header
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("🐛 DEBUG CONSOLE"))

        btn_clear = QPushButton("Clear")
        btn_clear.clicked.connect(self.clear_console)
        header_layout.addWidget(btn_clear)

        btn_stop = QPushButton("Stop")
        btn_stop.clicked.connect(self.stop_execution)
        header_layout.addWidget(btn_stop)

        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Console output
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setFont(QFont("SF Mono", 12))
        layout.addWidget(self.console)

        return console_frame

    def connect_signals(self):
        """Connect all signals"""
        # Git
        self.git_manager.status_updated.connect(self.update_git_status)
        self.git_manager.output_ready.connect(self.append_console)
        self.git_manager.error_occurred.connect(self.append_console_error)

        # Debugger
        self.debugger.output_ready.connect(self.append_console)
        self.debugger.error_occurred.connect(self.append_console_error)

    def switch_theme(self, theme_name):
        """Switch theme"""
        self.current_theme = theme_name
        self.apply_theme()
        self.status_label.setText(f"Theme: {theme_name}")

    def apply_theme(self):
        """Apply theme"""
        css, theme_data = ThemeManager.get_stylesheet(self.current_theme)
        self.setStyleSheet(css)

        # Update highlighter
        if hasattr(self, 'highlighter'):
            self.on_language_changed()

    def create_custom_theme(self):
        """Create custom theme"""
        # Ask for base theme
        themes = list(ThemeManager.get_all_themes().keys())
        base_theme, ok = QInputDialog.getItem(
            self,
            "Select Base Theme",
            "Choose a theme to start from:",
            themes,
            0,
            False
        )

        if ok and base_theme:
            base_data = ThemeManager.get_all_themes()[base_theme]
            dialog = ThemeEditorDialog(self, base_data)

            if dialog.exec() == QDialog.DialogCode.Accepted:
                # Refresh theme menu
                self.status_label.setText("Custom theme created!")

    def on_language_changed(self):
        """Handle language change"""
        lang = self.lang_combo.currentText()
        lexer = LanguageDetector.get_lexer_name(lang)

        _, theme = ThemeManager.get_stylesheet(self.current_theme)
        self.highlighter = PygmentsHighlighter(
            self.editor.document(),
            lexer,
            theme['pygment']
        )

    def select_folder(self):
        """Select folder"""
        folder = QFileDialog.getExistingDirectory(self, "Open Folder")
        if folder:
            self.tree.setRootIndex(self.fs_model.index(folder))
            self.current_repo_path = folder
            self.git_manager.set_repo_path(folder)
            self.git_refresh()

    def open_file(self, index):
        """Open file"""
        path = self.fs_model.filePath(index)

        if os.path.isfile(path):
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                self.editor.setPlainText(content)
                self.current_file = path

                filename = os.path.basename(path)
                detected = LanguageDetector.detect(filename)

                idx = self.lang_combo.findText(detected)
                if idx >= 0:
                    self.lang_combo.setCurrentIndex(idx)

                self.editor_tabs.setTabText(0, filename)
                self.status_label.setText(f"Opened: {filename}")

            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def close_tab(self, index):
        """Close tab"""
        if self.editor_tabs.count() > 1:
            self.editor_tabs.removeTab(index)

    def on_text_changed(self):
        """Handle text change"""
        count = len(self.editor.toPlainText())
        self.char_count.setText(f"{count:,} chars")

    def run_code(self):
        """Run code"""
        code = self.editor.toPlainText()
        if code.strip():
            self.console.clear()
            self.append_console("▶ Running code...\n")
            self.debugger.run_code(code, self.current_file)

    def debug_code(self):
        """Debug code"""
        code = self.editor.toPlainText()
        if code.strip():
            self.console.clear()
            self.append_console("🐛 Debugging code...\n")
            self.debugger.debug_code(code, self.current_file)

    def refactor_code(self):
        """Refactor code"""
        code = self.editor.toPlainText().strip()
        if not code:
            self.status_label.setText("❌ No code to refactor")
            return

        self.btn_refactor.setEnabled(False)
        self.btn_refactor.setText("⏳ Processing...")

        model = self.model_combo.currentText()
        lang = self.lang_combo.currentText()

        self.worker = RefactorWorker(model, code, lang)
        self.worker.finished.connect(self.on_refactor_success)
        self.worker.error.connect(self.on_refactor_error)
        self.worker.start()

    def on_refactor_success(self, result):
        """Handle refactor success"""
        result_editor = QTextEdit()
        result_editor.setReadOnly(True)
        result_editor.setMarkdown(result)

        self.editor_tabs.addTab(result_editor, "✨ Refactored")
        self.editor_tabs.setCurrentWidget(result_editor)

        self.btn_refactor.setEnabled(True)
        self.btn_refactor.setText("✨ Refactor")
        self.status_label.setText("✅ Refactoring complete!")

    def on_refactor_error(self, error):
        """Handle refactor error"""
        self.btn_refactor.setEnabled(True)
        self.btn_refactor.setText("✨ Refactor")
        self.status_label.setText(f"❌ Error: {error}")
        QMessageBox.critical(self, "Error", error)

    def stop_execution(self):
        """Stop execution"""
        self.debugger.stop()

    def append_console(self, text):
        """Append to console"""
        self.console.append(text)

    def append_console_error(self, text):
        """Append error to console"""
        self.console.append(f'<span style="color: #ff453a;">{text}</span>')

    def clear_console(self):
        """Clear console"""
        self.console.clear()

    def git_refresh(self):
        """Refresh Git status"""
        if not self.current_repo_path:
            return

        branch = self.git_manager.get_branch()
        self.git_branch_label.setText(f"Branch: {branch}")
        self.git_status_label.setText(f"Git: {branch}")

        self.git_manager.get_status()

        log = self.git_manager.get_log()
        self.git_log_text.setPlainText(log)

    def update_git_status(self, status):
        """Update Git status display"""
        self.git_status_list.clear()

        for filepath in status.get('modified', []):
            self.git_status_list.addItem(f"M  {filepath}")

        for filepath in status.get('added', []):
            self.git_status_list.addItem(f"A  {filepath}")

        for filepath in status.get('deleted', []):
            self.git_status_list.addItem(f"D  {filepath}")

        for filepath in status.get('untracked', []):
            self.git_status_list.addItem(f"?? {filepath}")

    def git_add_all(self):
        """Git add all"""
        self.git_manager.add_files(['.'])

    def git_commit(self):
        """Git commit"""
        message = self.git_commit_input.text().strip()
        if not message:
            QMessageBox.warning(self, "Error", "Enter commit message")
            return

        self.git_manager.commit(message)
        self.git_commit_input.clear()

    def git_push(self):
        """Git push"""
        self.git_manager.push()

    def git_pull(self):
        """Git pull"""
        self.git_manager.pull()

    def open_settings(self):
        """Open settings"""
        dlg = QDialog(self)
        dlg.setWindowTitle("Settings")
        dlg.resize(400, 250)

        layout = QFormLayout(dlg)

        inputs = {}
        for provider in ["gemini", "openai", "anthropic"]:
            le = QLineEdit()
            le.setEchoMode(QLineEdit.EchoMode.Password)
            le.setText(ConfigManager.get_key(provider))
            layout.addRow(f"{provider.capitalize()}:", le)
            inputs[provider] = le

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save |
            QDialogButtonBox.StandardButton.Cancel
        )

        def save():
            settings = QSettings("GenAI_Studio", "SecureKeys")
            for k, v in inputs.items():
                if v.text().strip():
                    settings.setValue(k, v.text().strip())
            dlg.accept()
            self.status_label.setText("✅ Settings saved")

        buttons.accepted.connect(save)
        buttons.rejected.connect(dlg.reject)
        layout.addRow(buttons)

        dlg.exec()

# ==========================================
# 9. MAIN
# ==========================================

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Check dependencies
    try:
        import pygments
    except ImportError:
        QMessageBox.critical(None, "Error", "Install: pip install pygments")
        sys.exit(1)

    window = FullFeatureIDE()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
