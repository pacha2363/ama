# main.py
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout, QScrollArea
from mod.pretest import PreTestFrame
from mod.posttest import PostTestFrame
from mod.comparison_pre_post import ComparisonPrePostTestFrame
from mod.heartrate import HeartRateFrame
from mod.tobii import TobiiFrame
from mod.face_emotion import FaceEmotionFrame

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
            # Initialize and add other frames similarly

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = AguidaMultimodalAnalyzer()
    mainWin.show()
    sys.exit(app.exec_())