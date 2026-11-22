import sys
from pathlib import Path

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
        if file_path:
            # TODO: Read the CSV file at `file_path` into `self.temperatures` and `self.profits`.
            self.plot_graph()

    def plot_graph(self):
        self.ax.clear()
        self.ax.plot([20, 25, 30, 35], [100, 180, 260, 340], marker="o")
        self.ax.set_title("Ice Cream Sales (Placeholder)")
        self.ax.set_xlabel("Temperature")
        self.ax.set_ylabel("Profits")
        self.ax.grid(True, linestyle="--", alpha=0.5)
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
