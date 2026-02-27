from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QLineEdit,
    QPushButton,
    QDoubleSpinBox,
    QSpinBox,
    QGroupBox,
    QFormLayout,
    QMessageBox,
    QScrollArea,
    QFrame,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont


class SettingsWidget(QWidget):
    settings_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.provider_factory = None
        self.setup_ui()

    def set_provider_factory(self, factory):
        self.provider_factory = factory
        self.populate_providers()
        self.load_settings()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        title = QLabel("Chatbot Settings")
        title.setStyleSheet("""
            QLabel {
                color: #00e676;
                font-size: 20px;
                font-weight: bold;
                margin-bottom: 10px;
            }
        """)
        main_layout.addWidget(title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #121212;
            }
        """)

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(15)

        provider_group = self._create_provider_group()
        scroll_layout.addWidget(provider_group)

        model_group = self._create_model_group()
        scroll_layout.addWidget(model_group)

        parameters_group = self._create_parameters_group()
        scroll_layout.addWidget(parameters_group)

        refresh_group = self._create_refresh_group()
        scroll_layout.addWidget(refresh_group)

        scroll_layout.addStretch()

        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.test_btn = QPushButton("Test Connection")
        self.test_btn.setStyleSheet("""
            QPushButton {
                background-color: #333;
                color: #fff;
                border: 1px solid #555;
                border-radius: 6px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #444;
            }
        """)
        self.test_btn.clicked.connect(self.test_connection)

        self.save_btn = QPushButton("Save Settings")
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #00e676;
                color: #000;
                border: none;
                border-radius: 6px;
                padding: 10px 24px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00c853;
            }
        """)
        self.save_btn.clicked.connect(self.save_settings)

        button_layout.addWidget(self.test_btn)
        button_layout.addWidget(self.save_btn)

        main_layout.addLayout(button_layout)

    def _create_provider_group(self) -> QGroupBox:
        group = QGroupBox("LLM Provider")
        group.setStyleSheet("""
            QGroupBox {
                color: #e0e0e0;
                border: 1px solid #333;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
                background-color: #1a1a1a;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)

        layout = QFormLayout()
        layout.setSpacing(12)

        self.provider_combo = QComboBox()
        self.provider_combo.setStyleSheet("""
            QComboBox {
                background-color: #2d2d2d;
                color: #e0e0e0;
                border: 1px solid #444;
                border-radius: 6px;
                padding: 8px;
                min-width: 250px;
            }
            QComboBox:hover {
                border: 1px solid #00e676;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid #888;
            }
        """)
        self.provider_combo.currentTextChanged.connect(self.on_provider_changed)

        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("Paste your API key here...")
        self.api_key_input.setEchoMode(QLineEdit.Password)
        self.api_key_input.setStyleSheet("""
            QLineEdit {
                background-color: #2d2d2d;
                color: #e0e0e0;
                border: 1px solid #444;
                border-radius: 6px;
                padding: 10px;
                min-width: 300px;
            }
            QLineEdit:focus {
                border: 1px solid #00e676;
            }
        """)

        layout.addRow("Provider:", self.provider_combo)
        layout.addRow("API Key:", self.api_key_input)

        self.provider_help = QLabel(
            "💡 Get API keys from:\n"
            "• OpenAI: platform.openai.com\n"
            "• Anthropic: console.anthropic.com\n"
            "• Google: aistudio.google.com/app/apikey\n"
            "• Ollama: Run locally (no key needed)"
        )
        self.provider_help.setStyleSheet("""
            QLabel {
                color: #888;
                font-size: 11px;
                line-height: 1.4;
            }
        """)
        layout.addRow("", self.provider_help)

        group.setLayout(layout)
        return group

    def _create_model_group(self) -> QGroupBox:
        group = QGroupBox("Model Configuration")
        group.setStyleSheet("""
            QGroupBox {
                color: #e0e0e0;
                border: 1px solid #333;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
                background-color: #1a1a1a;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)

        layout = QFormLayout()
        layout.setSpacing(12)

        self.model_combo = QComboBox()
        self.model_combo.setStyleSheet("""
            QComboBox {
                background-color: #2d2d2d;
                color: #e0e0e0;
                border: 1px solid #444;
                border-radius: 6px;
                padding: 8px;
                min-width: 250px;
            }
        """)

        self.ollama_url = QLineEdit()
        self.ollama_url.setPlaceholderText("http://localhost:11434")
        self.ollama_url.setText("http://localhost:11434")
        self.ollama_url.setStyleSheet("""
            QLineEdit {
                background-color: #2d2d2d;
                color: #e0e0e0;
                border: 1px solid #444;
                border-radius: 6px;
                padding: 10px;
            }
            QLineEdit:focus {
                border: 1px solid #00e676;
            }
        """)

        layout.addRow("Model:", self.model_combo)
        layout.addRow("Ollama URL:", self.ollama_url)

        group.setLayout(layout)
        return group

    def _create_parameters_group(self) -> QGroupBox:
        group = QGroupBox("Generation Parameters")
        group.setStyleSheet("""
            QGroupBox {
                color: #e0e0e0;
                border: 1px solid #333;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
                background-color: #1a1a1a;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)

        layout = QFormLayout()
        layout.setSpacing(12)

        self.temperature = QDoubleSpinBox()
        self.temperature.setRange(0.0, 2.0)
        self.temperature.setSingleStep(0.1)
        self.temperature.setValue(0.7)
        self.temperature.setStyleSheet("""
            QDoubleSpinBox {
                background-color: #2d2d2d;
                color: #e0e0e0;
                border: 1px solid #444;
                border-radius: 6px;
                padding: 8px;
            }
        """)

        self.max_tokens = QSpinBox()
        self.max_tokens.setRange(100, 10000)
        self.max_tokens.setSingleStep(100)
        self.max_tokens.setValue(2000)
        self.max_tokens.setStyleSheet("""
            QSpinBox {
                background-color: #2d2d2d;
                color: #e0e0e0;
                border: 1px solid #444;
                border-radius: 6px;
                padding: 8px;
            }
        """)

        layout.addRow("Temperature:", self.temperature)
        layout.addRow("Max Tokens:", self.max_tokens)

        group.setLayout(layout)
        return group

    def _create_refresh_group(self) -> QGroupBox:
        group = QGroupBox("Data Refresh Settings")
        group.setStyleSheet("""
            QGroupBox {
                color: #e0e0e0;
                border: 1px solid #333;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
                background-color: #1a1a1a;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)

        layout = QFormLayout()
        layout.setSpacing(12)

        self.refresh_interval = QSpinBox()
        self.refresh_interval.setRange(5, 300)
        self.refresh_interval.setSingleStep(5)
        self.refresh_interval.setValue(60)
        self.refresh_interval.setSuffix(" seconds")
        self.refresh_interval.setStyleSheet("""
            QSpinBox {
                background-color: #2d2d2d;
                color: #e0e0e0;
                border: 1px solid #444;
                border-radius: 6px;
                padding: 8px;
            }
        """)

        layout.addRow("Refresh Interval:", self.refresh_interval)

        help_label = QLabel("How often to fetch new market data (5-300 seconds)")
        help_label.setStyleSheet("color: #888; font-size: 11px;")
        layout.addRow("", help_label)

        group.setLayout(layout)
        return group

    def populate_providers(self):
        self.provider_combo.clear()
        if self.provider_factory:
            providers = self.provider_factory.get_available_providers()
            for p in providers:
                self.provider_combo.addItem(p["name"], p["id"])

    def on_provider_changed(self, text):
        provider_id = self.provider_combo.currentData()

        self.model_combo.clear()

        if provider_id and provider_id != "none":
            models = self.provider_factory.get_models_for_provider(provider_id)
            for m in models:
                self.model_combo.addItem(m)

            if provider_id == "ollama":
                self.api_key_input.setEnabled(False)
                self.api_key_input.setPlaceholderText("No API key needed for Ollama")
            else:
                self.api_key_input.setEnabled(True)
                self.api_key_input.setPlaceholderText("Paste your API key here...")
        else:
            self.api_key_input.setEnabled(False)
            self.api_key_input.setPlaceholderText("Offline mode - no API needed")

    def load_settings(self):
        from ..agents.providers import get_settings

        settings = get_settings()

        provider = settings.provider
        for i in range(self.provider_combo.count()):
            if self.provider_combo.itemData(i) == provider:
                self.provider_combo.setCurrentIndex(i)
                break

        self.api_key_input.setText(settings.api_key)
        self.model_combo.setCurrentText(settings.model or "")
        self.temperature.setValue(settings.temperature)
        self.max_tokens.setValue(settings.max_tokens)
        self.refresh_interval.setValue(settings.refresh_interval)

    def save_settings(self):
        from ..agents.providers import get_settings

        settings = get_settings()

        settings.set("provider", self.provider_combo.currentData())
        settings.set("api_key", self.api_key_input.text())
        settings.set("model", self.model_combo.currentText())
        settings.set("temperature", self.temperature.value())
        settings.set("max_tokens", self.max_tokens.value())
        settings.set("refresh_interval", self.refresh_interval.value())

        self.settings_changed.emit()

        QMessageBox.information(
            self, "Settings Saved", "Chatbot settings have been saved successfully!"
        )

    def test_connection(self):
        provider = self.provider_combo.currentData()
        api_key = self.api_key_input.text()
        model = self.model_combo.currentText()

        if provider == "none":
            QMessageBox.information(
                self,
                "Offline Mode",
                "You're in offline mode. No API connection to test.",
            )
            return

        if provider != "ollama" and not api_key:
            QMessageBox.warning(
                self,
                "Missing API Key",
                "Please enter an API key to test the connection.",
            )
            return

        self.test_btn.setEnabled(False)
        self.test_btn.setText("Testing...")

        from ..agents.providers import LLMProviderFactory

        success, message = LLMProviderFactory.test_connection(provider, api_key, model)

        self.test_btn.setEnabled(True)
        self.test_btn.setText("Test Connection")

        if success:
            QMessageBox.information(self, "Connection Success", message)
        else:
            QMessageBox.warning(self, "Connection Failed", f"Error: {message}")
