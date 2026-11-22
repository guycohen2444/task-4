import csv
import sys
from pathlib import Path

import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

GITHUB_REPO_URL = "https://github.com/guycohen2444/task-4"


class IceCreamGraphWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.temperatures = []
        self.profits = []

        self.setWindowTitle("Ice Cream Sales Graph")
        self.resize(800, 600)

        qss_path = Path(__file__).resolve().parent / "style.qss"
        if qss_path.exists():
            self.setStyleSheet(qss_path.read_text(encoding="utf-8"))

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        # Top bar
        top_bar = QHBoxLayout()
        load_btn = QPushButton("Load File")
        load_btn.clicked.connect(self.load_file)

        about_btn = QPushButton("About")
        about_btn.setObjectName("aboutButton")
        about_btn.clicked.connect(self.show_about)

        top_bar.addWidget(load_btn)
        top_bar.addStretch()
        top_bar.addWidget(about_btn)
        layout.addLayout(top_bar)

        # Embedded Matplotlib figure + toolbar
        self.figure = Figure(figsize=(7, 5), tight_layout=True)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.toolbar = NavigationToolbar2QT(self.canvas, self)

        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas, stretch=1)

    def load_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select CSV File", "", "CSV Files (*.csv);;All Files (*)"
        )
        if not file_path:
            return

        self.temperatures.clear()
        self.profits.clear()

        try:
            with open(file_path, "r", encoding="utf-8-sig", newline="") as file:
                reader = csv.reader(file)
                next(reader, None)  # Skip header row
                for row in reader:
                    if len(row) < 2:
                        continue
                    self.temperatures.append(float(row[0].strip()))
                    self.profits.append(float(row[1].strip()))
        except Exception as exc:
            QMessageBox.critical(
                self, "Error", f"Could not read CSV file:\n{exc}"
            )
            return

        self.plot_graph()

    def plot_graph(self):
        self.ax.clear()
        if not self.temperatures or not self.profits:
            self.canvas.draw()
            return

        text_color = (0.3, 0.3, 0.3)

        self.ax.scatter(self.temperatures, self.profits, s=1)
        self.ax.spines["top"].set_visible(False)
        self.ax.spines["right"].set_visible(False)

        self.ax.set_title("Ice Cream Sales vs. Temperature", color=text_color)
        self.ax.set_xlabel("Temperature", color=text_color)
        self.ax.set_ylabel("Profits", color=text_color)

        x = np.array(self.temperatures)
        y = np.array(self.profits)
        m, b = np.polyfit(x, y, 1)

        x_line = np.linspace(x.min(), x.max(), 100)
        y_line = m * x_line + b
        self.ax.plot(x_line, y_line, color="#2638DC", linewidth=1.5)

        sign = "+" if b >= 0 else "-"
        equation = f"y = {m:.2f}x {sign} {abs(b):.2f}"
        self.ax.text(
            0.05,
            0.92,
            equation,
            transform=self.ax.transAxes,
            color=text_color,
            fontsize=10,
            verticalalignment="top",
        )

        self.canvas.draw()

    def show_about(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("About")
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.setText(
            f"<b>Ice Cream Sales Graph</b><br><br>"
            f"Author: Guy Cohen<br>"
            f'GitHub: <a href="{GITHUB_REPO_URL}">{GITHUB_REPO_URL}</a>'
        )
        msg.exec()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = IceCreamGraphWindow()
    window.show()
    sys.exit(app.exec())
