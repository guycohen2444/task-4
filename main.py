import csv
import os
import subprocess
import sys
from pathlib import Path

import openpyxl
from PySide6.QtCore import Qt
from PySide6.QtGui import QIntValidator, QPixmap
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QDialog,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

APP_TITLE = "Grades File Editor"
AUTHOR_NAME = "Guy Cohen"
AUTHOR_EMAIL = "guycohen24444@gmail.com"
LINKEDIN_URL = "https://www.linkedin.com/in/guy-cohen-4294a6366/"
GITHUB_REPO_URL = "https://github.com/guycohen2444/task-4"
ABOUT_IMAGE_NAME = "image.png"
DEFAULT_ROW_COUNT = 50
TABLE_HEADERS = ["ID", "Original Grades", "Corrected Grades"]


class AboutWindow(QDialog):
    """Styled About dialog displaying author photo, contact details, LinkedIn, and GitHub repo."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About")
        self.setFixedWidth(420)
        self.setModal(True)

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(20, 20, 20, 20)
        root_layout.setSpacing(14)

        card = QFrame()
        card.setObjectName("aboutCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(10)

        self.image_label = QLabel()
        self.image_label.setObjectName("aboutImage")
        self.image_label.setFixedSize(180, 180)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        image_path = Path(__file__).resolve().parent / ABOUT_IMAGE_NAME
        pixmap = QPixmap(str(image_path))
        if image_path.exists() and not pixmap.isNull():
            scaled = pixmap.scaled(
                self.image_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self.image_label.setPixmap(scaled)
        else:
            self.image_label.setText(f"Missing {ABOUT_IMAGE_NAME}")

        title_label = QLabel(APP_TITLE)
        title_label.setObjectName("aboutTitle")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.name_label = QLabel(f"<b>Name:</b> {AUTHOR_NAME}")
        self.name_label.setObjectName("aboutMeta")

        self.email_label = QLabel(
            f'<b>Email:</b> <a href="mailto:{AUTHOR_EMAIL}">{AUTHOR_EMAIL}</a>'
        )
        self.email_label.setObjectName("aboutMeta")
        self.email_label.setOpenExternalLinks(True)
        self.email_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextBrowserInteraction
        )

        self.link_label = QLabel(
            f'<b>LinkedIn:</b> <a href="{LINKEDIN_URL}">My LinkedIn Profile</a>'
        )
        self.link_label.setObjectName("aboutLink")
        self.link_label.setOpenExternalLinks(True)
        self.link_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextBrowserInteraction
        )

        self.github_label = QLabel(
            f'<b>GitHub Repository:</b><br>'
            f'<a href="{GITHUB_REPO_URL}">{GITHUB_REPO_URL}</a>'
        )
        self.github_label.setObjectName("aboutLink")
        self.github_label.setOpenExternalLinks(True)
        self.github_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextBrowserInteraction
        )
        self.github_label.setWordWrap(True)

        card_layout.addWidget(
            self.image_label, alignment=Qt.AlignmentFlag.AlignHCenter
        )
        card_layout.addWidget(title_label)
        card_layout.addSpacing(4)
        card_layout.addWidget(self.name_label)
        card_layout.addWidget(self.email_label)
        card_layout.addWidget(self.link_label)
        card_layout.addWidget(self.github_label)

        root_layout.addWidget(card)

        button_row = QHBoxLayout()
        button_row.addStretch()

        close_btn = QPushButton("Close")
        close_btn.setObjectName("primaryButton")
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.clicked.connect(self.accept)
        button_row.addWidget(close_btn)

        root_layout.addLayout(button_row)


class GradesEditorWindow(QMainWindow):
    """Main window for the Grades File Editor application."""

    def __init__(self):
        super().__init__()

        # Required data attributes
        self.student_ids = []
        self.original_grades = []
        self.corrected_grades = []
        self.selected_file = ""
        self.file_headers = []

        self.setWindowTitle(APP_TITLE)
        self.resize(860, 640)
        self.setMinimumSize(680, 500)

        self._build_ui()
        self._load_stylesheet()

    def _load_stylesheet(self):
        """Load external QSS stylesheet located in the same directory as main.py."""
        qss_path = Path(__file__).resolve().parent / "style.qss"
        if qss_path.exists():
            with open(qss_path, "r", encoding="utf-8") as stylesheet_file:
                self.setStyleSheet(stylesheet_file.read())

    def _build_ui(self):
        """Construct and arrange all widgets and layouts."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(14)

        # --- Header Card ---
        header_card = QFrame()
        header_card.setObjectName("headerCard")
        header_layout = QHBoxLayout(header_card)
        header_layout.setContentsMargins(18, 14, 18, 14)

        title_col = QVBoxLayout()
        title_col.setSpacing(2)

        title_label = QLabel(APP_TITLE)
        title_label.setObjectName("appTitle")

        subtitle_label = QLabel(
            "Load a grades file (CSV / Excel), apply bonus points, and save the updated grades."
        )
        subtitle_label.setObjectName("appSubtitle")

        title_col.addWidget(title_label)
        title_col.addWidget(subtitle_label)

        self.about_button = QPushButton("About")
        self.about_button.setObjectName("ghostButton")
        self.about_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.about_button.clicked.connect(self.show_about)

        header_layout.addLayout(title_col)
        header_layout.addStretch()
        header_layout.addWidget(self.about_button)
        main_layout.addWidget(header_card)

        # --- Toolbar Card (Load File + Selected File Indicator) ---
        toolbar_card = QFrame()
        toolbar_card.setObjectName("toolbarCard")
        toolbar_layout = QHBoxLayout(toolbar_card)
        toolbar_layout.setContentsMargins(16, 12, 16, 12)
        toolbar_layout.setSpacing(12)

        self.load_file_button = QPushButton("Load Grades File")
        self.load_file_button.setObjectName("secondaryButton")
        self.load_file_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.load_file_button.clicked.connect(self.load_file)

        self.file_status_label = QLabel("No file loaded")
        self.file_status_label.setObjectName("fileStatusLabel")

        toolbar_layout.addWidget(self.load_file_button)
        toolbar_layout.addWidget(self.file_status_label, stretch=1)
        main_layout.addWidget(toolbar_card)

        # --- Grades Table Card ---
        table_card = QFrame()
        table_card.setObjectName("tableCard")
        table_layout = QVBoxLayout(table_card)
        table_layout.setContentsMargins(14, 14, 14, 14)

        self.grades_table = QTableWidget(DEFAULT_ROW_COUNT, len(TABLE_HEADERS))
        self.grades_table.setObjectName("gradesTable")
        self.grades_table.setHorizontalHeaderLabels(TABLE_HEADERS)
        self.grades_table.setAlternatingRowColors(True)
        self.grades_table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self.grades_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.grades_table.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        self.grades_table.setShowGrid(True)

        header = self.grades_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header.setHighlightSections(False)

        vertical_header = self.grades_table.verticalHeader()
        vertical_header.setDefaultSectionSize(32)
        vertical_header.setHighlightSections(False)

        table_layout.addWidget(self.grades_table)
        main_layout.addWidget(table_card, stretch=1)

        # --- Footer Card (Bonus Input + Update File Button) ---
        footer_card = QFrame()
        footer_card.setObjectName("footerCard")
        footer_layout = QHBoxLayout(footer_card)
        footer_layout.setContentsMargins(16, 12, 16, 12)
        footer_layout.setSpacing(12)

        bonus_label = QLabel("Bonus Points (Press Enter to apply):")
        bonus_label.setObjectName("sectionLabel")

        self.bonus_input = QLineEdit()
        self.bonus_input.setObjectName("bonusInput")
        self.bonus_input.setPlaceholderText("e.g. 5")
        self.bonus_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.bonus_input.setValidator(QIntValidator(-100, 100, self))
        self.bonus_input.returnPressed.connect(self.apply_bonus)

        self.update_file_button = QPushButton("Update File")
        self.update_file_button.setObjectName("primaryButton")
        self.update_file_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.update_file_button.clicked.connect(self.update_file)

        footer_layout.addWidget(bonus_label)
        footer_layout.addWidget(self.bonus_input)
        footer_layout.addStretch()
        footer_layout.addWidget(self.update_file_button)
        main_layout.addWidget(footer_card)

    @staticmethod
    def _format_id(value):
        """Format student ID cleanly as a string (avoiding trailing '.0' from Excel)."""
        if isinstance(value, float) and value.is_integer():
            return str(int(value))
        return str(value).strip()

    @staticmethod
    def _parse_grade(value):
        """Parse a numeric grade into int (if whole number) or float."""
        if value is None:
            raise ValueError("Empty grade value")
        text = str(value).strip()
        if not text:
            raise ValueError("Empty grade value")
        num = float(text)
        return int(num) if num.is_integer() else num

    @staticmethod
    def _read_rows(file_path):
        """Read non-empty rows from a CSV or Excel (.xlsx / .xlsm) file."""
        suffix = Path(file_path).suffix.lower()

        if suffix in (".xlsx", ".xlsm"):
            workbook = openpyxl.load_workbook(file_path, data_only=True)
            try:
                sheet = workbook.active
                rows = [
                    list(row)
                    for row in sheet.iter_rows(values_only=True)
                    if row and any(
                        cell is not None and str(cell).strip() != ""
                        for cell in row
                    )
                ]
            finally:
                workbook.close()
            return rows

        if suffix == ".xls":
            raise ValueError(
                "Legacy .xls format is not supported. Please save the file as .xlsx or .csv."
            )

        for encoding in ("utf-8-sig", "cp1255", "latin-1"):
            try:
                with open(file_path, "r", encoding=encoding, newline="") as csv_file:
                    return [
                        row
                        for row in csv.reader(csv_file)
                        if row and any(cell.strip() != "" for cell in row)
                    ]
            except UnicodeDecodeError:
                continue

        raise ValueError("Unable to decode the CSV file.")

    def load_file(self):
        """Open a file dialog to select a CSV or Excel file and load its grades."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Grades File",
            "",
            "Spreadsheet Files (*.csv *.xlsx *.xlsm);;CSV Files (*.csv);;Excel Files (*.xlsx *.xlsm);;All Files (*)",
        )

        if not file_path:
            return

        try:
            rows = self._read_rows(file_path)
        except Exception as exc:
            QMessageBox.critical(
                self,
                "Error Loading File",
                f"Could not read the selected file:\n{exc}",
            )
            return

        if not rows:
            QMessageBox.warning(
                self,
                "Empty File",
                "The selected file contains no data.",
            )
            return

        # Detect whether the first row is a header row
        headers = []
        data_rows = rows
        if len(rows[0]) >= 2:
            try:
                self._parse_grade(rows[0][1])
            except ValueError:
                headers = [
                    str(cell).strip()
                    for cell in rows[0]
                    if cell is not None and str(cell).strip() != ""
                ]
                data_rows = rows[1:]

        student_ids = []
        original_grades = []
        for line_num, row in enumerate(data_rows, start=2 if headers else 1):
            if len(row) < 2 or row[0] is None or row[1] is None:
                continue
            try:
                grade = self._parse_grade(row[1])
            except ValueError:
                QMessageBox.warning(
                    self,
                    "Invalid Data",
                    f"Skipping row {line_num}: invalid grade value '{row[1]}'.",
                )
                continue
            student_ids.append(self._format_id(row[0]))
            original_grades.append(grade)

        self.selected_file = file_path
        self.file_headers = headers
        self.student_ids = student_ids
        self.original_grades = original_grades
        self.corrected_grades = original_grades.copy()

        self.bonus_input.clear()
        self.update_table()

    def update_table(self):
        """Populate the QTableWidget from student_ids, original_grades, and corrected_grades."""
        num_records = max(
            len(self.student_ids),
            len(self.original_grades),
            len(self.corrected_grades),
        )
        row_count = max(DEFAULT_ROW_COUNT, num_records)

        self.grades_table.clearContents()
        self.grades_table.setRowCount(row_count)

        for row in range(num_records):
            values = [
                self.student_ids[row] if row < len(self.student_ids) else "",
                self.original_grades[row] if row < len(self.original_grades) else "",
                self.corrected_grades[row] if row < len(self.corrected_grades) else "",
            ]
            for col, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.grades_table.setItem(row, col, item)

        if self.selected_file:
            file_name = Path(self.selected_file).name
            self.file_status_label.setText(
                f"Loaded: {file_name}  ({num_records} records)"
            )
        else:
            self.file_status_label.setText("No file loaded")

    def apply_bonus(self):
        """Apply integer bonus points when the user presses Enter in the bonus input."""
        if not self.original_grades:
            QMessageBox.warning(
                self,
                "No Data Loaded",
                "Please load a grades file before applying bonus points.",
            )
            return

        bonus_text = self.bonus_input.text().strip()
        try:
            bonus = int(bonus_text)
        except ValueError:
            QMessageBox.warning(
                self,
                "Invalid Bonus",
                "Please enter a valid integer bonus value.",
            )
            return

        updated_grades = []
        for grade in self.original_grades:
            new_grade = max(0, min(grade + bonus, 100))
            if isinstance(new_grade, float) and new_grade.is_integer():
                new_grade = int(new_grade)
            updated_grades.append(new_grade)

        self.corrected_grades = updated_grades
        self.update_table()

    def update_file(self):
        """Overwrite the selected file with the updated grades and open it externally."""
        if not self.selected_file:
            QMessageBox.warning(
                self,
                "No File Selected",
                "Please load a grades file before updating.",
            )
            return

        include_original_column = len(self.file_headers) >= 3
        if include_original_column:
            output_headers = self.file_headers[:3]
            output_rows = [
                [sid, orig, corr]
                for sid, orig, corr in zip(
                    self.student_ids, self.original_grades, self.corrected_grades
                )
            ]
        else:
            output_headers = self.file_headers[:2] if len(self.file_headers) >= 2 else []
            output_rows = [
                [sid, corr]
                for sid, corr in zip(self.student_ids, self.corrected_grades)
            ]

        suffix = Path(self.selected_file).suffix.lower()

        try:
            if suffix in (".xlsx", ".xlsm"):
                workbook = openpyxl.load_workbook(self.selected_file)
                try:
                    sheet = workbook.active
                    if sheet.max_row > 0:
                        sheet.delete_rows(1, sheet.max_row)
                    if output_headers:
                        sheet.append(output_headers)
                    for row in output_rows:
                        sheet.append(row)
                    workbook.save(self.selected_file)
                finally:
                    workbook.close()
            else:
                with open(
                    self.selected_file, "w", encoding="utf-8-sig", newline=""
                ) as csv_file:
                    writer = csv.writer(csv_file)
                    if output_headers:
                        writer.writerow(output_headers)
                    writer.writerows(output_rows)
        except PermissionError:
            QMessageBox.warning(
                self,
                "File Is Open",
                "Cannot save because the file is currently open in another program (e.g., Excel).\n"
                "Please close the file and try again.",
            )
            return
        except Exception as exc:
            QMessageBox.critical(
                self,
                "Error Saving File",
                f"Failed to overwrite the file:\n{exc}",
            )
            return

        self.open_file_externally(self.selected_file)

    def open_file_externally(self, filepath):
        """Open the given file in the operating system's default application."""
        if not filepath or not Path(filepath).exists():
            QMessageBox.warning(
                self,
                "File Not Found",
                f"Could not locate the file to open:\n{filepath or '(empty path)'}",
            )
            return

        try:
            if sys.platform.startswith("win"):
                os.startfile(filepath)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", filepath])
            else:
                subprocess.Popen(["xdg-open", filepath])
        except OSError as exc:
            QMessageBox.critical(
                self,
                "Failed to Open File",
                f"Unable to open the file in the default application:\n{exc}",
            )

    def show_about(self):
        """Display the About window with author info, LinkedIn, and GitHub repo."""
        dialog = AboutWindow(self)
        dialog.exec()


def main():
    app = QApplication(sys.argv)
    window = GradesEditorWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
