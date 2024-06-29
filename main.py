# main.py
import os
import sys

from PyQt5 import Qt
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout, QScrollArea, QMenuBar, QAction, \
    QMessageBox, QLabel, QVBoxLayout, QDialog, QInputDialog
from datetime import datetime

from mod.about import about_text
from mod.help import help_text
from mod.pretest import PreTestFrame
from mod.posttest import PostTestFrame
from mod.comparison_pre_post import ComparisonPrePostTestFrame
from mod.heartrate import HeartRateFrame
from mod.tobii import TobiiFrame
from mod.face_emotion import FaceEmotionFrame
from mod.dialogflow import DialogFlowFrame
from mod.systemchoice import SystemChoiceFrame
from mod.ind_analyzer_window import IndividualAnalyzerWindow
from mod.determination_time import DurationCalculator
from mod.duration_calculator import DurationCalculatorFunction
from fpdf import FPDF


class AguidaMultimodalAnalyzer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Aguida Multimodal Analyzer - Version 2.9.2")
        self.setGeometry(100, 100, 400, 800)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QGridLayout(self.central_widget)
        self.layout.setSpacing(10)

        # Create frames for each block
        blocks = [
            "Pre-Test",
            "Post-Test",
            "Comparison of Pre-Test and Post-Test",
            "Heart Rate",
            "Tobii (Eye Tracking)",
            "Face Emotion (OpenFace)",
            "DialogFlow (Conversation with Peter)",
            "System Choice",
            "Interpretation"
        ]

        # Initialize frames as None
        self.pre_test_frame = None
        self.post_test_frame = None
        self.comparison_pre_post = None
        self.heart_rate_frame = None
        self.system_choice_frame = None
        self.dialogflow_frame = None
        self.tobii_frame = None
        self.face_emotion_frame = None

        # Add frames to the grid layout
        for i, block in enumerate(blocks):
            if block == "Pre-Test":
                self.pre_test_frame = PreTestFrame()
                scroll_area = QScrollArea()
                scroll_area.setWidgetResizable(True)
                scroll_area.setWidget(self.pre_test_frame)
                self.layout.addWidget(scroll_area, i // 3, i % 3)
            elif block == "Post-Test":
                self.post_test_frame = PostTestFrame()
                scroll_area = QScrollArea()
                scroll_area.setWidgetResizable(True)
                scroll_area.setWidget(self.post_test_frame)
                self.layout.addWidget(scroll_area, i // 3, i % 3)
            elif block == "Comparison of Pre-Test and Post-Test":
                self.comparison_pre_post = ComparisonPrePostTestFrame(self.pre_test_frame, self.post_test_frame)
                scroll_area = QScrollArea()
                scroll_area.setWidgetResizable(True)
                scroll_area.setWidget(self.comparison_pre_post)
                self.layout.addWidget(self.comparison_pre_post, i // 3, i % 3)
            elif block == "Heart Rate":
                self.heart_rate_frame = HeartRateFrame()
                self.layout.addWidget(self.heart_rate_frame, i // 3, i % 3)
            elif block == "Tobii (Eye Tracking)":
                self.tobii_frame = TobiiFrame()
                self.layout.addWidget(self.tobii_frame, i // 3, i % 3)
            elif block == "Face Emotion (OpenFace)":
                self.face_emotion_frame = FaceEmotionFrame()
                self.layout.addWidget(self.face_emotion_frame, i // 3, i % 3)
            elif block == "DialogFlow (Conversation with Peter)":
                self.dialogflow_frame = DialogFlowFrame()
                self.layout.addWidget(self.dialogflow_frame, i // 3, i % 3)
            elif block == "System Choice":
                self.system_choice_frame = SystemChoiceFrame()
                self.layout.addWidget(self.system_choice_frame, i // 3, i % 3)
            # Initialize and add other frames similarly


        # Create the footnote label
        footnote = QLabel("Aguida Multimodal Analyzer (Offline Data) by Aboul Hassane CISSE - Knowledge Information System Lab<br>version 2024.05")
        footnote.setAlignment(Qt.AlignCenter)
        footnote.setStyleSheet("color: gray; font-size: 12px; margin-top: 20px;")
        self.layout.addWidget(footnote)

        # Create menu bar
        self.menu_bar = QMenuBar(self)
        self.setMenuBar(self.menu_bar)

        # Add menus
        self.file_menu = self.menu_bar.addMenu("Functions")
        self.help_menu = self.menu_bar.addMenu(" ? ")

        # Add actions to the file menu
        self.print_action = QAction("Generate Global Report and Print", self)
        self.print_action.triggered.connect(self.print_report)
        self.file_menu.addAction(self.print_action)

        #self.calculate_duration_action = QAction("Calculate Duration", self)
        #self.calculate_duration_action.triggered.connect(self.open_duration_window)
        #self.file_menu.addAction(self.calculate_duration_action)

        self.ind_analyzer_window_action = QAction("Individual Analyzer", self)
        self.ind_analyzer_window_action.triggered.connect(self.individual_analyzer_window)
        self.file_menu.addAction(self.ind_analyzer_window_action)

        self.duration_calculator_action = QAction("Duration Calculator", self)
        self.duration_calculator_action.triggered.connect(self.duration_calculator_window)
        self.file_menu.addAction(self.duration_calculator_action)

        self.help_action = QAction("Help", self)
        self.help_action.triggered.connect(self.show_help_dialog)  # Connect action to function
        self.help_menu.addAction(self.help_action)

        self.about_action = QAction("About", self)
        self.about_action.triggered.connect(self.show_about_dialog)
        self.help_menu.addAction(self.about_action)

    def show_about_dialog(self):
        # Create a dialog
        dialog = QDialog(self)
        dialog.setWindowTitle('About Aguida Multimodal Analyzer')
        dialog.setMinimumSize(500, 400)

        # Create a QVBoxLayout for the dialog
        layout = QVBoxLayout()

        # Create a QLabel to display the about text
        label = QLabel(about_text)
        label.setWordWrap(True)

        # Create a QScrollArea
        scroll_area = QScrollArea()
        scroll_area.setWidget(label)
        scroll_area.setWidgetResizable(True)
        scroll_area.setFixedHeight(400)

        # Add the scroll area to the layout
        layout.addWidget(scroll_area)

        # Set the layout on the dialog
        dialog.setLayout(layout)

        # Show the dialog
        dialog.exec_()


    def show_help_dialog(self):
        # Create a dialog
        dialog = QDialog(self)
        dialog.setWindowTitle('Help for Aguida Multimodal Analyzer')
        dialog.setMinimumSize(500, 400)

        # Create a QVBoxLayout for the dialog
        layout = QVBoxLayout()

        # Create a QLabel to display the help text
        label = QLabel(help_text)
        label.setWordWrap(True)

        # Create a QScrollArea
        scroll_area = QScrollArea()
        scroll_area.setWidget(label)
        scroll_area.setWidgetResizable(True)
        scroll_area.setFixedHeight(400)

        # Add the scroll area to the layout
        layout.addWidget(scroll_area)

        # Set the layout on the dialog
        dialog.setLayout(layout)

        # Show the dialog
        dialog.exec_()

    def open_duration_window(self):
        dialog = DurationCalculator(self)
        dialog.exec_()

    def duration_calculator_window(self):
        dialog = DurationCalculatorFunction(self)
        dialog.exec_()

    def individual_analyzer_window(self):
        dialog = IndividualAnalyzerWindow(self)
        dialog.exec_()

    def print_report(self):
        try:
            # Get the report name from the user
            text, ok = QInputDialog.getText(self, 'Report Name', 'Enter the name for the report:')
            if not ok or not text.strip():
                QMessageBox.warning(self, 'Input Error', 'You must enter a valid report name.')
                return
            report_name = text.strip()

            pdf = FPDF()

            # Add a page
            pdf.add_page()

            # Set title
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt=f"{report_name} Report", ln=True, align='C')
            pdf.cell(200, 10, txt="Aguida Multimodal Analyzer", ln=True, align='C')

            # Collect data from each frame and add to the PDF
            frames = [
                ("Pre-Test", self.pre_test_frame),
                ("Post-Test", self.post_test_frame),
                ("Comparison of Pre-Test and Post-Test", self.comparison_pre_post),
                ("Heart Rate", self.heart_rate_frame),
                ("Tobii (Eye Tracking)", self.tobii_frame),
                ("Face Emotion (OpenFace)", self.face_emotion_frame),
                ("DialogFlow (Conversation with Peter)", self.dialogflow_frame),
                ("System Choice", self.system_choice_frame)
            ]

            for title, frame in frames:
                if frame and frame.get_data():
                    data = frame.get_data()
                    pdf.set_font("Arial", size=10)
                    pdf.cell(0, 10, txt=f"{title} Data:", ln=True)
                    for key, value in data.items():
                        pdf.cell(0, 10, txt=f"{key.capitalize()}: {value}", ln=True)
                    pdf.ln(10)

            # Save the PDF
            pdf_dir = "generated_reports"
            os.makedirs(pdf_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            pdf_filename = os.path.join(pdf_dir, f"{report_name}_report_{timestamp}.pdf")
            pdf.output(pdf_filename)

            # Show success message
            QMessageBox.information(self, "Report Generated", f"PDF report generated successfully:\n{pdf_filename}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate PDF report:\n{str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = AguidaMultimodalAnalyzer()
    mainWin.show()
    sys.exit(app.exec_())
