import sys
import os
import re
import markdown
from dotenv import load_dotenv
from pypdf import PdfReader
import docx  # For Word Files

# --- AI Providers ---
import google.generativeai as genai
from openai import OpenAI
from anthropic import Anthropic

# --- PyQt6 Imports ---
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QSplitter, QTreeView, QTextEdit, QPlainTextEdit,
                             QPushButton, QLabel, QFileDialog, QMessageBox,
                             QTabWidget, QComboBox, QProgressBar, QDialog,
                             QFormLayout, QLineEdit, QDialogButtonBox, QGroupBox, QFrame, QStackedWidget)
from PyQt6.QtCore import Qt, QDir, QThread, pyqtSignal, QSettings
from PyQt6.QtGui import (QFileSystemModel, QFont, QColor, QSyntaxHighlighter,
                         QTextCharFormat, QIcon, QPalette)
from PyQt6.QtPrintSupport import QPrinter

# --- Syntax Highlighting ---
import pygments
from pygments.lexers import get_lexer_by_name, guess_lexer_for_filename
from pygments.formatter import Formatter

load_dotenv()

# --- CONFIGURATION ---
MODELS_CONFIG = {
    "Google: Gemini 2.5 Flash": {"provider": "gemini", "model_id": "gemini-2.5-flash"},
    "Google: Gemini 3 Pro":   {"provider": "gemini", "model_id": "gemini-3-pro-preview"},
    "OpenAI: GPT-5.1":          {"provider": "openai", "model_id": "gpt-5.1"},
    "OpenAI: GPT-4o":           {"provider": "openai", "model_id": "gpt-4o"},
    "Anthropic: Claude 3.5 Sonnet": {"provider": "anthropic", "model_id": "claude-3-5-sonnet-20241022"},
    "DeepSeek: V3":             {"provider": "deepseek", "model_id": "deepseek-chat"},
    "Perplexity: Sonar Large":  {"provider": "perplexity", "model_id": "sonar-reasoning-pro"},
}

# --- THEME MANAGER ---
class ThemeManager:
    # LIGHT THEME (macOS Inspired)
    LIGHT = {
        "bg_main": "#f5f5f7",
        "bg_sidebar": "#ebecf0",
        "bg_editor": "#ffffff",
        "text_main": "#333333",
        "text_muted": "#666666",
        "border": "#d1d1d6",
        "accent": "#007aff",
        "accent_hover": "#005bb5",
        "spu_color": "#ff2d55", # Pinkish Red
        "btn_bg": "#ffffff",
        "btn_text": "#333333"
    }

    # DARK THEME (VS Code Inspired)
    DARK = {
        "bg_main": "#1e1e1e",
        "bg_sidebar": "#252526",
        "bg_editor": "#1e1e1e",
        "text_main": "#d4d4d4",
        "text_muted": "#858585",
        "border": "#3e3e42",
        "accent": "#007acc",
        "accent_hover": "#0062a3",
        "spu_color": "#E91E63", # SPU Pink
        "btn_bg": "#3c3c3c",
        "btn_text": "#ffffff"
    }

    @staticmethod
    def get_sheet(theme_dict):
        t = theme_dict
        return f"""
            QMainWindow {{ background-color: {t['bg_main']}; color: {t['text_main']}; }}
            QWidget {{ font-family: 'Segoe UI', 'Helvetica Neue', sans-serif; font-size: 13px; color: {t['text_main']}; }}

            /* Splitter */
            QSplitter::handle {{ background-color: {t['border']}; width: 1px; }}

            /* Panels */
            QTreeView {{ background-color: {t['bg_sidebar']}; border: none; border-right: 1px solid {t['border']}; }}
            QTreeView::item:hover {{ background-color: {t['accent']}33; }}
            QTreeView::item:selected {{ background-color: {t['accent']}66; color: {t['text_main']}; }}

            /* Editor & Tabs */
            QTabWidget::pane {{ border: 1px solid {t['border']}; border-top: none; }}
            QTabBar::tab {{ background: {t['bg_sidebar']}; color: {t['text_muted']}; padding: 8px 15px; border-right: 1px solid {t['border']}; }}
            QTabBar::tab:selected {{ background: {t['bg_editor']}; color: {t['accent']}; border-top: 2px solid {t['accent']}; font-weight: bold; }}

            QPlainTextEdit, QTextEdit {{
                background-color: {t['bg_editor']};
                color: {t['text_main']};
                border: none;
                font-family: 'Consolas', monospace; font-size: 14px;
            }}

            /* Inputs */
            QLineEdit, QComboBox {{
                background-color: {t['btn_bg']};
                border: 1px solid {t['border']};
                color: {t['text_main']};
                padding: 5px;
                border-radius: 4px;
            }}

            /* Buttons */
            QPushButton {{
                background-color: {t['btn_bg']};
                border: 1px solid {t['border']};
                color: {t['btn_text']};
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: 500;
            }}
            QPushButton:hover {{ background-color: {t['accent']}22; border-color: {t['accent']}; }}

            /* Primary Action Button */
            QPushButton#ActionBtn {{ background-color: {t['accent']}; color: white; border: none; font-weight: bold; }}
            QPushButton#ActionBtn:hover {{ background-color: {t['accent_hover']}; }}

            /* SPU Special Button */
            QPushButton#SPUBtn {{ background-color: {t['spu_color']}; color: white; border: none; font-weight: bold; }}
            QPushButton#SPUBtn:hover {{ opacity: 0.8; }}
        """

# --- WORKER ---
class AIWorker(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, mode, model_info, content, instruction, api_keys):
        super().__init__()
        self.mode = mode # "code" or "edu"
        self.provider = model_info["provider"]
        self.model_id = model_info["model_id"]
        self.content = content
        self.instruction = instruction
        self.api_keys = api_keys

    def run(self):
        # Prompt Engineering based on Mode
        if self.mode == "code":
            sys_prompt = "You are an Expert Software Architect."
            user_prompt = f"Instruction: {self.instruction}\n\nCode Context:\n{self.content[:20000]}"
        else: # mode == "edu"
            sys_prompt = "You are an Expert Professor and Tutor."
            user_prompt = f"""
            Instruction: {self.instruction}

            Source Material (Lecture/Notes):
            {self.content[:30000]}

            Task: Explain clearly, summarize key points, or create a quiz as requested.
            Output: Markdown formatted.
            """

        full_prompt = f"{sys_prompt}\n\n{user_prompt}"

        try:
            response_text = ""
            # ... (API Calls Logic - Standardized) ...
            if self.provider == "gemini":
                genai.configure(api_key=self.api_keys["gemini"])
                model = genai.GenerativeModel(self.model_id)
                response_text = model.generate_content(full_prompt).text
            elif self.provider in ["openai", "deepseek", "perplexity"]:
                base_urls = {"openai": None, "deepseek": "https://api.deepseek.com", "perplexity": "https://api.perplexity.ai"}
                client = OpenAI(api_key=self.api_keys[self.provider], base_url=base_urls[self.provider])
                response_text = client.chat.completions.create(model=self.model_id, messages=[{"role": "user", "content": full_prompt}]).choices[0].message.content
            elif self.provider == "anthropic":
                client = Anthropic(api_key=self.api_keys["anthropic"])
                response_text = client.messages.create(model=self.model_id, max_tokens=4096, messages=[{"role": "user", "content": full_prompt}]).content[0].text

            self.finished.emit(response_text)
        except Exception as e:
            self.error.emit(str(e))

# --- MAIN APP ---
class TunnerSuite(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SPU AI CLUB: Tunner Suite (Ultimate Edition)")
        self.resize(1600, 950)

        self.current_theme = "dark" # Default
        self.current_mode = "code"  # code | edu

        self.init_ui()
        self.apply_theme()

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.setSpacing(0)

        # --- TOOLBAR ---
        toolbar = QFrame()
        toolbar.setFixedHeight(50)
        tb_layout = QHBoxLayout(toolbar)
        tb_layout.setContentsMargins(10,0,10,0)

        self.lbl_brand = QLabel("🚀 SPU TUNNER SUITE")
        self.lbl_brand.setStyleSheet("font-weight: 900; font-size: 16px; letter-spacing: 1px;")

        # Mode Switcher
        self.btn_mode_code = QPushButton("💻 Code Tunner")
        self.btn_mode_code.setCheckable(True)
        self.btn_mode_code.setChecked(True)
        self.btn_mode_code.clicked.connect(lambda: self.switch_mode("code"))

        self.btn_mode_edu = QPushButton("🎓 Edu Tunner (PDF/Word)")
        self.btn_mode_edu.setCheckable(True)
        self.btn_mode_edu.clicked.connect(lambda: self.switch_mode("edu"))

        # Theme Toggle
        self.btn_theme = QPushButton("🌙") # Start with moon
        self.btn_theme.setFixedWidth(40)
        self.btn_theme.clicked.connect(self.toggle_theme)

        # Model Selector
        self.model_box = QComboBox()
        self.model_box.addItems(list(MODELS_CONFIG.keys()))

        btn_keys = QPushButton("🔑 Keys")
        btn_keys.clicked.connect(self.open_settings)

        tb_layout.addWidget(self.lbl_brand)
        tb_layout.addSpacing(20)
        tb_layout.addWidget(self.btn_mode_code)
        tb_layout.addWidget(self.btn_mode_edu)
        tb_layout.addStretch()
        tb_layout.addWidget(QLabel("AI Model:"))
        tb_layout.addWidget(self.model_box)
        tb_layout.addWidget(btn_keys)
        tb_layout.addWidget(self.btn_theme)

        main_layout.addWidget(toolbar)

        # --- SPLITTER CONTENT ---
        self.splitter = QSplitter(Qt.Orientation.Horizontal)

        # 1. Left: Explorer
        self.setup_explorer()
        self.splitter.addWidget(self.explorer_container)

        # 2. Center: Stacked Widget (Code Editor OR Doc Viewer)
        self.center_stack = QStackedWidget()

        # 2A. Code Editor Tabs
        self.code_tabs = QTabWidget()
        self.code_tabs.setTabsClosable(True)
        self.code_tabs.tabCloseRequested.connect(lambda i: self.code_tabs.removeTab(i))
        self.add_code_tab("Welcome", "Select a file to start coding...", None)
        self.center_stack.addWidget(self.code_tabs)

        # 2B. Doc Viewer (Edu)
        self.doc_viewer = QTextEdit()
        self.doc_viewer.setReadOnly(True)
        self.doc_viewer.setPlaceholderText("Open a Lecture Slide (PDF) or Notes (Word) to begin education analysis...")
        self.center_stack.addWidget(self.doc_viewer)

        self.splitter.addWidget(self.center_stack)

        # 3. Right: AI Tunner Panel
        self.setup_ai_panel()
        self.splitter.addWidget(self.ai_container)

        self.splitter.setSizes([250, 900, 450])
        main_layout.addWidget(self.splitter)

        # Status Bar
        self.status = self.statusBar()
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        self.status.addPermanentWidget(self.progress)

    def setup_explorer(self):
        self.explorer_container = QWidget()
        layout = QVBoxLayout(self.explorer_container)
        layout.setContentsMargins(0,0,0,0)

        btn_open = QPushButton("📂 Open Folder")
        btn_open.clicked.connect(self.open_folder)
        layout.addWidget(btn_open)

        self.file_model = QFileSystemModel()
        self.file_model.setRootPath("")
        self.tree = QTreeView()
        self.tree.setModel(self.file_model)
        self.tree.setRootIndex(self.file_model.index(QDir.homePath()))
        self.tree.hideColumn(1); self.tree.hideColumn(2); self.tree.hideColumn(3)
        self.tree.clicked.connect(self.on_file_click)
        layout.addWidget(self.tree)

    def setup_ai_panel(self):
        self.ai_container = QWidget()
        layout = QVBoxLayout(self.ai_container)
        layout.setContentsMargins(10,10,10,10)

        self.lbl_ai_title = QLabel("⚡ AI TUNNER")
        self.lbl_ai_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(self.lbl_ai_title)

        self.ai_output = QTextEdit()
        self.ai_output.setReadOnly(True)
        layout.addWidget(self.ai_output)

        self.ai_input = QTextEdit()
        self.ai_input.setMaximumHeight(80)
        self.ai_input.setPlaceholderText("Enter instruction (e.g., 'Refactor this', 'Summarize lecture')...")
        layout.addWidget(self.ai_input)

        hbox = QHBoxLayout()
        self.btn_run = QPushButton("✨ Run Magic")
        self.btn_run.setObjectName("SPUBtn")
        self.btn_run.clicked.connect(self.run_ai)

        btn_exp = QPushButton("📄 Export PDF")
        btn_exp.clicked.connect(self.export_pdf)

        hbox.addWidget(self.btn_run)
        hbox.addWidget(btn_exp)
        layout.addLayout(hbox)

    # --- LOGIC ---
    def apply_theme(self):
        if self.current_theme == "dark":
            t = ThemeManager.DARK
            self.btn_theme.setText("☀️")
        else:
            t = ThemeManager.LIGHT
            self.btn_theme.setText("🌙")

        self.setStyleSheet(ThemeManager.get_sheet(t))

        # Dynamic Colors
        self.lbl_brand.setStyleSheet(f"color: {t['spu_color']}; font-weight: 900; font-size: 16px;")
        self.lbl_ai_title.setStyleSheet(f"color: {t['accent']}; font-weight: bold;")

    def toggle_theme(self):
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        self.apply_theme()

    def switch_mode(self, mode):
        self.current_mode = mode
        if mode == "code":
            self.btn_mode_code.setChecked(True)
            self.btn_mode_edu.setChecked(False)
            self.center_stack.setCurrentWidget(self.code_tabs)
            self.ai_input.setPlaceholderText("Code Mode: Type 'Refactor', 'Fix Bug', 'Explain logic'...")
        else:
            self.btn_mode_code.setChecked(False)
            self.btn_mode_edu.setChecked(True)
            self.center_stack.setCurrentWidget(self.doc_viewer)
            self.ai_input.setPlaceholderText("Edu Mode: Type 'Summarize this', 'Create a Quiz', 'Explain key concepts'...")

    def open_folder(self):
        d = QFileDialog.getExistingDirectory(self)
        if d: self.tree.setRootIndex(self.file_model.index(d))

    def on_file_click(self, index):
        path = self.file_model.filePath(index)
        if not os.path.isfile(path): return
        ext = os.path.splitext(path)[1].lower()

        # Content Extraction
        content = ""
        try:
            if ext == ".pdf":
                reader = PdfReader(path)
                content = "\n".join([p.extract_text() for p in reader.pages])
                self.load_to_viewer(path, content, is_doc=True)
            elif ext == ".docx":
                doc = docx.Document(path)
                content = "\n".join([p.text for p in doc.paragraphs])
                self.load_to_viewer(path, content, is_doc=True)
            else:
                # Code / Text
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                self.load_to_viewer(path, content, is_doc=False)
        except Exception as e:
            self.status.showMessage(f"Error reading file: {e}")

    def load_to_viewer(self, path, content, is_doc):
        filename = os.path.basename(path)

        if is_doc:
            # Auto switch to Edu Mode for Docs
            self.switch_mode("edu")
            self.doc_viewer.setPlainText(f"--- DOCUMENT: {filename} ---\n\n{content}")
        else:
            # Auto switch to Code Mode
            self.switch_mode("code")
            # Check tabs
            for i in range(self.code_tabs.count()):
                if self.code_tabs.tabToolTip(i) == path:
                    self.code_tabs.setCurrentIndex(i)
                    return
            self.add_code_tab(filename, content, path)

    def add_code_tab(self, title, content, path):
        editor = QPlainTextEdit()
        editor.setPlainText(content)
        editor.setFont(QFont("Consolas", 12))
        # (Add Syntax Highlighter here same as previous version)
        self.code_tabs.addTab(editor, title)
        if path:
            self.code_tabs.setTabToolTip(self.code_tabs.count()-1, path)
        self.code_tabs.setCurrentIndex(self.code_tabs.count()-1)

    def run_ai(self):
        instruction = self.ai_input.toPlainText()
        if self.current_mode == "code":
            content = self.code_tabs.currentWidget().toPlainText()
        else:
            content = self.doc_viewer.toPlainText()

        if not content.strip():
            QMessageBox.warning(self, "Empty", "Please select a file first.")
            return

        model_info = MODELS_CONFIG[self.model_box.currentText()]
        keys = self.get_keys()

        if not keys.get(model_info["provider"]):
            self.open_settings()
            return

        self.progress.setVisible(True)
        self.progress.setRange(0,0)
        self.btn_run.setEnabled(False)
        self.status.showMessage(f"AI Working in {self.current_mode.upper()} mode...")

        self.worker = AIWorker(self.current_mode, model_info, content, instruction, keys)
        self.worker.finished.connect(self.on_ai_finished)
        self.worker.error.connect(lambda e: QMessageBox.critical(self, "Error", e))
        self.worker.start()

    def on_ai_finished(self, text):
        self.progress.setVisible(False)
        self.btn_run.setEnabled(True)
        self.status.showMessage("Done.")
        self.ai_output.setMarkdown(text)

    def export_pdf(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export PDF", "TunnerReport.pdf", "PDF (*.pdf)")
        if path:
            printer = QPrinter(QPrinter.PrinterMode.HighResolution)
            printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
            printer.setOutputFileName(path)

            html = markdown.markdown(self.ai_output.toMarkdown(), extensions=['fenced_code', 'tables'])
            doc = QTextEdit()
            doc.setHtml(f"<html><body><h1>SPU Tunner Report</h1>{html}</body></html>")
            doc.print(printer)
            QMessageBox.information(self, "Saved", f"Saved to {path}")

    def get_keys(self):
        s = QSettings("SPU", "Ultimate")
        k = {}
        for p in ["gemini", "openai", "anthropic", "deepseek", "perplexity"]:
            v = s.value(f"{p}_key", "")
            if not v: v = os.getenv(f"{p.upper()}_API_KEY")
            k[p] = v
        return k

    def open_settings(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("API Keys")
        dlg.resize(400, 300)
        l = QFormLayout(dlg)
        inputs = {}
        s = QSettings("SPU", "Ultimate")
        for k in ["gemini", "openai", "anthropic", "deepseek", "perplexity"]:
            le = QLineEdit(s.value(f"{k}_key", ""))
            le.setEchoMode(QLineEdit.EchoMode.Password)
            l.addRow(f"{k.capitalize()}:", le)
            inputs[k] = le
        bb = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        bb.accepted.connect(lambda: [s.setValue(f"{k}_key", v.text()) for k,v in inputs.items()] or dlg.accept())
        bb.rejected.connect(dlg.reject)
        l.addWidget(bb)
        dlg.exec()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TunnerSuite()
    window.show()
    sys.exit(app.exec())
