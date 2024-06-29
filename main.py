# main.py
import os
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout, QScrollArea, QMenuBar, QAction, QMessageBox
from datetime import datetime
from mod.pretest import PreTestFrame
from mod.posttest import PostTestFrame
from mod.comparison_pre_post import ComparisonPrePostTestFrame
from mod.heartrate import HeartRateFrame
from mod.tobii import TobiiFrame
from mod.face_emotion import FaceEmotionFrame
from mod.dialogflow import DialogFlowFrame
from mod.systemchoice import SystemChoiceFrame
from mod.determination_time import DurationCalculator
from mod.duration_calculator import DurationCalculatorFunction
from fpdf import FPDF


class AguidaMultimodalAnalyzer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Aguida Multimodal Analyzer - Version 2.9.2")
        self.setGeometry(100, 100, 800, 600)

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

        self.duration_calculator_action = QAction("Duration Calculator", self)
        self.duration_calculator_action.triggered.connect(self.duration_calculator_window)
        self.file_menu.addAction(self.duration_calculator_action)

        self.help_action = QAction("Help", self)
        self.help_menu.addAction(self.help_action)

        self.about_action = QAction("About", self)
        self.help_menu.addAction(self.about_action)


    def open_duration_window(self):
        dialog = DurationCalculator(self)
        dialog.exec_()

    def duration_calculator_window(self):
        dialog = DurationCalculatorFunction(self)
        dialog.exec_()

    def print_report(self):
        try:
            pdf = FPDF()

            # Add a page
            pdf.add_page()

            # Set title
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt="Aguida Multimodal Analyzer Report", ln=True, align='C')

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
            pdf_filename = os.path.join(pdf_dir, f"report_{timestamp}.pdf")
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
