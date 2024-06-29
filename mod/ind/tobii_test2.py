import os
import pandas as pd
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton, QFileDialog, QMessageBox
from PyQt5.QtCore import Qt
from datetime import datetime


class TobiiTest2Block(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.data = None  # Store processed data

        self.button_layout = QHBoxLayout()
        self.upload_button_tobii = QPushButton("Upload Tobii Test 2 File")
        self.upload_button_tobii.clicked.connect(self.upload_tobii_test2_file)
        self.button_layout.addWidget(self.upload_button_tobii)

        self.layout.addLayout(self.button_layout)

        self.test_data = None

    def upload_tobii_test2_file(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Tobii Test 2 File", "",
                                                   "CSV Files (*.csv);;Excel Files (*.xlsx)", options=options)
        if file_path:
            self.process_tobii_test2_data(file_path)

    def process_tobii_test2_data(self, file_path):
        if file_path.endswith('.csv'):
            tobii_test2_data = pd.read_csv(file_path)
        else:
            tobii_test2_data = pd.read_excel(file_path)

        # Extract relevant columns and calculate statistics
        pupil_diameter_data = pd.concat(
            [tobii_test2_data['Left_Pupil_Diameter'], tobii_test2_data['Right_Pupil_Diameter']])
        head_position_data = pd.concat([tobii_test2_data['Head_Position_X'], tobii_test2_data['Head_Position_Y'],
                                        tobii_test2_data['Head_Position_Z']])
        head_rotation_data = pd.concat([tobii_test2_data['Head_Rotation_X'], tobii_test2_data['Head_Rotation_Y'],
                                        tobii_test2_data['Head_Rotation_Z']])
        left_eye_data = pd.concat([tobii_test2_data['Left_Eye_X'], tobii_test2_data['Left_Eye_Y']])
        right_eye_data = pd.concat([tobii_test2_data['Right_Eye_X'], tobii_test2_data['Right_Eye_Y']])

        # Pupil Diameter Statistics
        self.avg_pupil_diameter = pupil_diameter_data.mean()
        self.std_dev_pupil_diameter = pupil_diameter_data.std()
        self.max_pupil_diameter = pupil_diameter_data.max()
        self.min_pupil_diameter = pupil_diameter_data.min()
        self.median_pupil_diameter = pupil_diameter_data.median()
        self.range_pupil_diameter = self.max_pupil_diameter - self.min_pupil_diameter

        # Head Position Statistics
        self.avg_head_position = head_position_data.mean()
        self.std_dev_head_position = head_position_data.std()
        self.max_head_position = head_position_data.max()
        self.min_head_position = head_position_data.min()
        self.range_head_position = self.max_head_position - self.min_head_position

        # Head Rotation Statistics
        self.avg_head_rotation = head_rotation_data.mean()
        self.std_dev_head_rotation = head_rotation_data.std()
        self.max_head_rotation = head_rotation_data.max()
        self.min_head_rotation = head_rotation_data.min()
        self.range_head_rotation = self.max_head_rotation - self.min_head_rotation

        # Eye Gaze Coordinates Statistics
        self.avg_left_eye_x = tobii_test2_data['Left_Eye_X'].mean()
        self.avg_left_eye_y = tobii_test2_data['Left_Eye_Y'].mean()
        self.std_dev_left_eye_x = tobii_test2_data['Left_Eye_X'].std()
        self.std_dev_left_eye_y = tobii_test2_data['Left_Eye_Y'].std()

        self.avg_right_eye_x = tobii_test2_data['Right_Eye_X'].mean()
        self.avg_right_eye_y = tobii_test2_data['Right_Eye_Y'].mean()
        self.std_dev_right_eye_x = tobii_test2_data['Right_Eye_X'].std()
        self.std_dev_right_eye_y = tobii_test2_data['Right_Eye_Y'].std()

        # Create summary text
        self.test_data = (
            f"Average Pupil Diameter: {self.avg_pupil_diameter:.2f}\n"
            f"Standard Deviation of Pupil Diameter: {self.std_dev_pupil_diameter:.2f}\n"
            f"Maximum Pupil Diameter: {self.max_pupil_diameter:.2f}\n"
            f"Minimum Pupil Diameter: {self.min_pupil_diameter:.2f}\n"
            f"Median Pupil Diameter: {self.median_pupil_diameter:.2f}\n"
            f"Range of Pupil Diameter: {self.range_pupil_diameter:.2f}\n"
            f"Average Head Position: {self.avg_head_position:.2f}\n"
            f"Standard Deviation of Head Position: {self.std_dev_head_position:.2f}\n"
            f"Maximum Head Position: {self.max_head_position:.2f}\n"
            f"Minimum Head Position: {self.min_head_position:.2f}\n"
            f"Range of Head Position: {self.range_head_position:.2f}\n"
            f"Average Head Rotation: {self.avg_head_rotation:.2f}\n"
            f"Standard Deviation of Head Rotation: {self.std_dev_head_rotation:.2f}\n"
            f"Maximum Head Rotation: {self.max_head_rotation:.2f}\n"
            f"Minimum Head Rotation: {self.min_head_rotation:.2f}\n"
            f"Range of Head Rotation: {self.range_head_rotation:.2f}\n"
            f"Average Left Eye X Coordinate: {self.avg_left_eye_x:.2f}\n"
            f"Average Left Eye Y Coordinate: {self.avg_left_eye_y:.2f}\n"
            f"Standard Deviation of Left Eye X Coordinate: {self.std_dev_left_eye_x:.2f}\n"
            f"Standard Deviation of Left Eye Y Coordinate: {self.std_dev_left_eye_y:.2f}\n"
            f"Average Right Eye X Coordinate: {self.avg_right_eye_x:.2f}\n"
            f"Average Right Eye Y Coordinate: {self.avg_right_eye_y:.2f}\n"
            f"Standard Deviation of Right Eye X Coordinate: {self.std_dev_right_eye_x:.2f}\n"
            f"Standard Deviation of Right Eye Y Coordinate: {self.std_dev_right_eye_y:.2f}"
        )

        # Display the summary text
        self.display_tobii_test2_summary(self.test_data)

    def display_tobii_test2_summary(self, summary_text):
        # Remove previous summary if any
        if hasattr(self, 'summary_label'):
            self.layout.removeWidget(self.summary_label)
            self.summary_label.deleteLater()

        self.summary_label = QLabel(summary_text)
        self.layout.addWidget(self.summary_label)
