import json
import sys
from pathlib import Path
from typing import Dict, List

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QApplication,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)


class StudyTrackerApp(QMainWindow):
    """Main window for the Study Session Tracker application."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Study Session Tracker")
        self.setMinimumSize(900, 700)

        # Store session data and where it will be persisted on disk.
        self.sessions_file = Path("sessions.json")
        self.sessions: List[Dict[str, str | int]] = []

        self._build_ui()
        self._apply_styles()
        self.load_sessions()
        self.refresh_history()

    def _build_ui(self) -> None:
        """Build all UI widgets and layouts."""
        central = QWidget()
        self.setCentralWidget(central)

        outer_layout = QVBoxLayout(central)
        outer_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        outer_layout.setContentsMargins(40, 30, 40, 30)

        # Main card that holds form + history sections.
        self.main_card = QFrame()
        self.main_card.setObjectName("mainCard")
        self.main_card.setMaximumWidth(760)
        card_layout = QVBoxLayout(self.main_card)
        card_layout.setSpacing(18)
        card_layout.setContentsMargins(32, 28, 32, 28)

        title = QLabel("Study Tracker")
        title.setObjectName("appTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(title)

        # Form section
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        form_layout.setFormAlignment(Qt.AlignmentFlag.AlignTop)
        form_layout.setHorizontalSpacing(14)
        form_layout.setVerticalSpacing(14)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g., Alex")

        self.subject_input = QLineEdit()
        self.subject_input.setPlaceholderText("e.g., Mathematics")

        self.topic_input = QLineEdit()
        self.topic_input.setPlaceholderText("e.g., Linear Algebra")

        self.minutes_input = QSpinBox()
        self.minutes_input.setRange(1, 1440)
        self.minutes_input.setValue(30)
        self.minutes_input.setSuffix(" min")
        self.minutes_input.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)

        form_layout.addRow("Name", self.name_input)
        form_layout.addRow("Subject", self.subject_input)
        form_layout.addRow("Topic", self.topic_input)
        form_layout.addRow("Minutes Studied", self.minutes_input)
        card_layout.addLayout(form_layout)

        self.save_button = QPushButton("Save Session")
        self.save_button.setObjectName("saveButton")
        self.save_button.clicked.connect(self.save_session)
        card_layout.addWidget(self.save_button)

        history_title = QLabel("Study History")
        history_title.setObjectName("sectionTitle")
        card_layout.addWidget(history_title)

        # Scrollable history section to display all past study sessions.
        self.history_scroll = QScrollArea()
        self.history_scroll.setWidgetResizable(True)
        self.history_scroll.setObjectName("historyScroll")

        history_container = QWidget()
        self.history_layout = QVBoxLayout(history_container)
        self.history_layout.setContentsMargins(4, 4, 4, 4)
        self.history_layout.setSpacing(12)
        self.history_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.history_scroll.setWidget(history_container)
        card_layout.addWidget(self.history_scroll, stretch=1)

        outer_layout.addWidget(self.main_card)

    def _apply_styles(self) -> None:
        """Apply a modern stylesheet inspired by productivity tools."""
        self.setFont(QFont("Segoe UI", 10))
        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #f4f6fb;
            }

            #mainCard {
                background-color: #ffffff;
                border: 1px solid #e8ecf4;
                border-radius: 22px;
            }

            QLabel#appTitle {
                font-size: 30px;
                font-weight: 700;
                color: #1e2432;
                margin-bottom: 4px;
            }

            QLabel#sectionTitle {
                font-size: 18px;
                font-weight: 600;
                color: #2f3950;
                margin-top: 12px;
            }

            QLabel {
                color: #364154;
                font-weight: 500;
            }

            QLineEdit, QSpinBox {
                background: #f8faff;
                border: 1px solid #d9e1ee;
                border-radius: 12px;
                padding: 10px 12px;
                color: #1f2937;
                min-height: 20px;
            }

            QLineEdit:focus, QSpinBox:focus {
                border: 2px solid #4f7cff;
                background: #ffffff;
            }

            QPushButton#saveButton {
                background-color: #3662ff;
                color: white;
                border: none;
                border-radius: 14px;
                padding: 13px 20px;
                font-size: 15px;
                font-weight: 600;
                margin-top: 4px;
            }

            QPushButton#saveButton:hover {
                background-color: #2d56e2;
            }

            QPushButton#saveButton:pressed {
                background-color: #274dc8;
            }

            QScrollArea#historyScroll {
                border: none;
                background: transparent;
            }
            """
        )

    def load_sessions(self) -> None:
        """Load study sessions from sessions.json when the app starts."""
        if not self.sessions_file.exists():
            return

        try:
            with self.sessions_file.open("r", encoding="utf-8") as file:
                data = json.load(file)
                if isinstance(data, list):
                    self.sessions = data
        except (json.JSONDecodeError, OSError):
            QMessageBox.warning(
                self,
                "Load Error",
                "Could not load sessions.json. The app will start with an empty history.",
            )
            self.sessions = []

    def save_sessions_to_file(self) -> None:
        """Persist all sessions to sessions.json."""
        with self.sessions_file.open("w", encoding="utf-8") as file:
            json.dump(self.sessions, file, indent=2)

    def save_session(self) -> None:
        """Collect form input, save the session, and refresh the history list."""
        name = self.name_input.text().strip()
        subject = self.subject_input.text().strip()
        topic = self.topic_input.text().strip()
        minutes = int(self.minutes_input.value())

        if not name or not subject or not topic:
            QMessageBox.information(
                self,
                "Missing Information",
                "Please fill in Name, Subject, and Topic before saving.",
            )
            return

        session = {
            "name": name,
            "subject": subject,
            "topic": topic,
            "minutes": minutes,
        }

        self.sessions.insert(0, session)
        self.save_sessions_to_file()
        self.refresh_history()

        # Clear fields to make entering the next session fast.
        self.topic_input.clear()
        self.subject_input.clear()
        self.minutes_input.setValue(30)
        self.topic_input.setFocus()

    def refresh_history(self) -> None:
        """Rebuild the visual history list from session data."""
        while self.history_layout.count():
            child = self.history_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        if not self.sessions:
            empty_label = QLabel("No study sessions yet. Save your first session above.")
            empty_label.setStyleSheet(
                "color: #68758f; background: #f8faff; border: 1px dashed #d9e1ee; border-radius: 12px; padding: 16px;"
            )
            self.history_layout.addWidget(empty_label)
            return

        for session in self.sessions:
            self.history_layout.addWidget(self._make_history_card(session))

    def _make_history_card(self, session: Dict[str, str | int]) -> QFrame:
        """Create one styled row/card representing a study session."""
        card = QFrame()
        card.setStyleSheet(
            """
            QFrame {
                background: #ffffff;
                border: 1px solid #dde5f1;
                border-radius: 14px;
            }
            """
        )

        layout = QHBoxLayout(card)
        layout.setContentsMargins(14, 12, 14, 12)

        details = QLabel(
            f"<b>{session['name']}</b> studied <b>{session['subject']}</b> - "
            f"{session['topic']}"
        )
        details.setTextFormat(Qt.TextFormat.RichText)
        details.setWordWrap(True)

        minutes = QLabel(f"{session['minutes']} min")
        minutes.setStyleSheet(
            "background: #edf2ff; color: #2a4fcc; border-radius: 10px; padding: 6px 10px; font-weight: 600;"
        )

        layout.addWidget(details, stretch=1)
        layout.addWidget(minutes, stretch=0)

        return card


def main() -> None:
    """Entry point used to launch the PyQt desktop app."""
    app = QApplication(sys.argv)
    window = StudyTrackerApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
