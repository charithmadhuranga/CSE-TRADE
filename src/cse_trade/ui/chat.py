import os
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QLineEdit,
    QPushButton,
    QLabel,
    QScrollArea,
    QFrame,
    QSizePolicy,
)
from PySide6.QtCore import Qt, QThread, Signal, Slot, QTimer
from PySide6.QtGui import QFont, QColor, QTextCursor, QTextDocument


class ChatWorker(QThread):
    chunk_ready = Signal(str)
    response_ready = Signal(str)
    error_occurred = Signal(str)

    def __init__(self, agent, user_input, stream=True):
        super().__init__()
        self.agent = agent
        self.user_input = user_input
        self.stream = stream

    def run(self):
        try:
            if self.stream and hasattr(self.agent, "stream_chat"):
                full_response = ""
                for chunk in self.agent.stream_chat(self.user_input):
                    if chunk:
                        # Only emit if it's new content to simulate streaming
                        # Since our stream_chat currently yields formatted full state
                        # we detect changes or just emit
                        if chunk != full_response:
                            self.chunk_ready.emit(str(chunk))
                            full_response = chunk
                self.response_ready.emit(full_response)
            else:
                response = self.agent.chat(self.user_input)
                if response:
                    self.response_ready.emit(str(response))
                else:
                    self.error_occurred.emit("Empty response received")
        except Exception as e:
            import traceback

            traceback.print_exc()
            self.error_occurred.emit(str(e))


class ChatMessageWidget(QFrame):
    def __init__(self, message: str, is_user: bool, parent=None):
        super().__init__(parent)
        self.is_user = is_user
        self.message = message
        self.setup_ui(message)

    def setup_ui(self, message: str):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)

        # Using QTextEdit instead of QLabel to fix truncation
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setAcceptRichText(True)
        self.text_edit.setMarkdown(message)
        self.text_edit.setFrameStyle(QFrame.NoFrame)
        self.text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.text_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        font = QFont()
        font.setPointSize(11)
        self.text_edit.setFont(font)

        if self.is_user:
            self.text_edit.setStyleSheet("""
                QTextEdit {
                    background-color: #1e3a5f;
                    color: #ffffff;
                    padding: 12px;
                    border-radius: 8px;
                }
            """)
            layout.setAlignment(Qt.AlignRight)
        else:
            self.text_edit.setStyleSheet("""
                QTextEdit {
                    background-color: #2d2d2d;
                    color: #e0e0e0;
                    padding: 12px;
                    border-radius: 8px;
                }
            """)
            layout.setAlignment(Qt.AlignLeft)

        layout.addWidget(self.text_edit)

        # Adjust height based on content
        self.adjust_height()

    def update_message(self, message: str):
        self.message = message
        self.text_edit.setMarkdown(message)
        self.adjust_height()

    def adjust_height(self):
        doc = self.text_edit.document()
        doc.setTextWidth(400)  # Approximate width
        height = doc.size().height() + 30  # Padding
        self.text_edit.setMinimumHeight(int(height))
        self.text_edit.setMaximumHeight(int(height))


class LoadingMessageWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.dot_count = 0
        self.setup_ui()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_dots)
        self.timer.start(500)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setAlignment(Qt.AlignLeft)

        self.label = QLabel("Thinking...")
        self.label.setStyleSheet("""
            QLabel {
                background-color: #2d2d2d;
                color: #888;
                padding: 12px;
                border-radius: 8px;
                font-style: italic;
            }
        """)
        layout.addWidget(self.label)

    def update_dots(self):
        self.dot_count = (self.dot_count + 1) % 4
        self.label.setText("Thinking" + "." * self.dot_count)


class ChatWidget(QWidget):
    def __init__(self, agent=None, parent=None):
        super().__init__(parent)
        self.agent = agent
        self.chat_worker = None
        self.message_widgets = []
        self.loading_widget = None
        self.current_response_widget = None
        self.setup_ui()
        self.update_api_status()
        self.add_welcome_message()

    def set_agent(self, agent):
        self.agent = agent
        # Load history from agent
        if self.agent and hasattr(self.agent, "history"):
            from langchain_core.messages import HumanMessage
            
            # Clear current UI before loading history
            self.clear_chat_ui()
            
            for msg in self.agent.history:
                is_user = isinstance(msg, HumanMessage)
                self.add_message(msg.content, is_user=is_user)
            
            # Re-add welcome if still empty
            if not self.agent.history:
                self.add_welcome_message()
        else:
            self.add_welcome_message()
        self.update_api_status()

    def on_clear_chat(self):
        from PySide6.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self, "Clear Chat",
            "Are you sure you want to clear the entire chat history?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            if self.agent:
                self.agent.clear_chat()
            
            self.clear_chat_ui()
            self.add_welcome_message()

    def clear_chat_ui(self):
        """Clear all message widgets from the UI."""
        for widget in self.message_widgets:
            self.chat_layout.removeWidget(widget)
            widget.deleteLater()
        self.message_widgets.clear()
        
        # Reset scroll area
        self.scroll.verticalScrollBar().setValue(0)

    def update_api_status(self):
        if hasattr(self, "api_status"):
            from ..agents.providers import get_settings

            settings = get_settings()
            provider = settings.provider

            if provider == "none":
                self.api_status.setText("🔴 Offline Mode")
            else:
                provider_names = {
                    "openai": "OpenAI",
                    "anthropic": "Claude",
                    "gemini": "Gemini",
                    "ollama": "Ollama",
                }
                provider_name = provider_names.get(provider, provider)
                self.api_status.setText(f"🟢 {provider_name} Ready")

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        header = QWidget()
        header.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                border-bottom: 1px solid #333;
            }
        """)
        header_layout = QHBoxLayout(header)

        title = QLabel("AI Trading Assistant")
        title.setStyleSheet("color: #00e676; font-size: 18px; font-weight: bold;")
        header_layout.addWidget(title)
        header_layout.addStretch()

        self.clear_btn = QPushButton("Clear Chat")
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #333;
                color: #888;
                border: 1px solid #444;
                border-radius: 4px;
                padding: 4px 10px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #444;
                color: #fff;
            }
        """)
        self.clear_btn.clicked.connect(self.on_clear_chat)
        header_layout.addWidget(self.clear_btn)

        self.api_status = QLabel()
        self.update_api_status()
        self.api_status.setStyleSheet("""
            QLabel {
                color: #888;
                font-size: 12px;
            }
        """)
        header_layout.addWidget(self.api_status)

        main_layout.addWidget(header)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("""
            QScrollArea {
                background-color: #121212;
                border: none;
            }
            QScrollBar:vertical {
                background: #1e1e1e;
                width: 12px;
            }
            QScrollBar::handle:vertical {
                background: #333;
                border-radius: 6px;
            }
        """)

        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.setAlignment(Qt.AlignTop)
        self.chat_layout.setSpacing(10)

        self.scroll.setWidget(self.chat_container)
        main_layout.addWidget(self.scroll)

        input_container = QWidget()
        input_container.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                border-top: 1px solid #333;
            }
        """)
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(10, 10, 10, 10)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText(
            "Ask about CSE stocks, market trends, or analysis..."
        )
        self.input_field.setStyleSheet("""
            QLineEdit {
                background-color: #2d2d2d;
                color: #e0e0e0;
                border: 1px solid #444;
                border-radius: 8px;
                padding: 12px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 1px solid #00e676;
            }
        """)
        self.input_field.setMinimumHeight(45)
        self.input_field.returnPressed.connect(self.send_message)

        send_btn = QPushButton("Send")
        send_btn.setStyleSheet("""
            QPushButton {
                background-color: #00e676;
                color: #000;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #00c853;
            }
            QPushButton:pressed {
                background-color: #00a846;
            }
            QPushButton:disabled {
                background-color: #444;
                color: #666;
            }
        """)
        send_btn.setMinimumHeight(45)
        send_btn.clicked.connect(self.send_message)

        input_layout.addWidget(self.input_field)
        input_layout.addWidget(send_btn)

        main_layout.addWidget(input_container)

        self.send_button = send_btn

    def add_welcome_message(self):
        # Don't add if we already have messages
        if self.message_widgets:
            return

        from ..agents.providers import get_settings

        settings = get_settings()
        provider = settings.provider

        provider_note = ""
        if provider == "none":
            provider_note = "*Note: Configure your LLM provider in Settings for AI-powered analysis.*"
        elif provider == "gemini":
            provider_note = "*Using Google Gemini for AI-powered analysis.*"
        elif provider == "anthropic":
            provider_note = "*Using Anthropic Claude for AI-powered analysis.*"
        elif provider == "openai":
            provider_note = "*Using OpenAI GPT for AI-powered analysis.*"
        elif provider == "ollama":
            provider_note = "*Using Ollama (local) for AI-powered analysis.*"

        welcome = f"""👋 **Welcome to CSE Market Analyst!**

I can help you with:

📊 **Market Analysis**
• Current market trends and indices
• ASPI and S&P SL20 performance

📈 **Stock Information**
• Stock prices and movements
• Top gainers and losers
• Volume and turnover data

💡 **Insights**
• Market sentiment analysis
• Trading patterns
• Investment considerations

**Try asking:**
• "What's the current ASPI?"
• "Show me top gainers today"
• "How is the market performing?"
• "Tell me about [stock symbol]"

{provider_note}"""

        self.add_message(welcome, is_user=False)

    def send_message(self):
        text = self.input_field.text().strip()
        if not text:
            return

        self.add_message(text, is_user=True)
        self.input_field.clear()

        self.send_button.setEnabled(False)
        self.input_field.setPlaceholderText("Analyzing market data...")

        # Add loading indicator
        self.loading_widget = LoadingMessageWidget()
        self.chat_layout.addWidget(self.loading_widget)
        self.scroll_to_bottom()

        self.current_response_widget = None

        self.chat_worker = ChatWorker(self.agent, text)
        self.chat_worker.chunk_ready.connect(self.on_chunk)
        self.chat_worker.response_ready.connect(self.on_response)
        self.chat_worker.error_occurred.connect(self.on_error)
        self.chat_worker.start()

    @Slot(str)
    def on_chunk(self, chunk: str):
        # Remove loading indicator on first chunk
        if self.loading_widget:
            self.loading_widget.deleteLater()
            self.loading_widget = None

        if not self.current_response_widget:
            self.current_response_widget = ChatMessageWidget(chunk, is_user=False)
            self.chat_layout.addWidget(self.current_response_widget)
            self.message_widgets.append(self.current_response_widget)
        else:
            self.current_response_widget.update_message(chunk)

        self.scroll_to_bottom()

    @Slot(str)
    def on_response(self, response: str):
        # Remove loading indicator if it's still there
        if self.loading_widget:
            self.loading_widget.deleteLater()
            self.loading_widget = None

        if not response or not response.strip():
            response = "No response received. Please try again or check settings."

        if not self.current_response_widget:
            self.add_message(response, is_user=False)
        else:
            self.current_response_widget.update_message(response)

        self.finish_loading()

    @Slot(str)
    def on_error(self, error: str):
        if self.loading_widget:
            self.loading_widget.deleteLater()
            self.loading_widget = None

        self.add_message(f"Error: {error}", is_user=False)
        self.finish_loading()

    def finish_loading(self):
        self.send_button.setEnabled(True)
        self.input_field.setPlaceholderText(
            "Ask about CSE stocks, market trends, or analysis..."
        )
        self.scroll_to_bottom()

    def add_message(self, message: str, is_user: bool):
        widget = ChatMessageWidget(message, is_user)
        self.chat_layout.addWidget(widget)
        self.message_widgets.append(widget)
        self.scroll_to_bottom()

    def scroll_to_bottom(self):
        # Small delay to ensure layout is updated
        QTimer.singleShot(50, lambda: self.scroll.verticalScrollBar().setValue(
            self.scroll.verticalScrollBar().maximum()
        ))

    def clear_chat(self):
        for widget in self.message_widgets:
            widget.deleteLater()
        self.message_widgets.clear()
        if self.loading_widget:
            self.loading_widget.deleteLater()
            self.loading_widget = None
        self.add_welcome_message()
