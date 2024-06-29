# mod/ind/heart_rate_test1_analyzer.py
import os
import pandas as pd
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton, QFileDialog, QMessageBox
from PyQt5.QtCore import Qt
from datetime import datetime
from fpdf import FPDF


class HeartRateTest2Block(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.data = None  # Store processed data

        self.button_layout = QHBoxLayout()
        self.upload_button_hr2 = QPushButton("Upload HR Test 2 File")
        self.upload_button_hr2.clicked.connect(self.upload_hr_test2_file)
        self.button_layout.addWidget(self.upload_button_hr2)

        self.layout.addLayout(self.button_layout)

        self.test_data = None

    def upload_hr_test2_file(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Select HR Test 2 File", "", "CSV Files (*.csv);;Excel Files (*.xlsx)", options=options)
        if file_path:
            self.process_hr_test2_data(file_path)

    def process_hr_test2_data(self, file_path):
        if file_path.endswith('.csv'):
            hr_test1_data = pd.read_csv(file_path)
        else:
            hr_test1_data = pd.read_excel(file_path)

        # Extract HR column and calculate statistics
        hr_data = hr_test1_data['HR']
        self.avg = hr_data.mean()
        self.std_dev = hr_data.std()
        self.max_val = hr_data.max()
        self.min_val = hr_data.min()
        self.median_val = hr_data.median()
        self.q1 = hr_data.quantile(0.25)
        self.q3 = hr_data.quantile(0.75)
        self.range_val = self.max_val - self.min_val
        self.iqr = self.q3 - self.q1
        self.total_duration = len(hr_data)
        self.count = hr_data.count()
        self.variance = hr_data.var()
        self.skewness = hr_data.skew()
        self.kurtosis = hr_data.kurt()
        self.mode = hr_data.mode().values[0] if not hr_data.mode().empty else 'N/A'
        self.ci_low, self.ci_high = self.mean_confidence_interval(hr_data)

        # Create summary text
        self.test_data = (
            f"Average Heart Rate: {self.avg:.2f}\n"
            f"Standard Deviation: {self.std_dev:.2f}\n"
            f"Maximum Heart Rate: {self.max_val:.2f}\n"
            f"Minimum Heart Rate: {self.min_val:.2f}\n"
            f"Median Heart Rate: {self.median_val:.2f}\n"
            f"1st Quartile (Q1): {self.q1:.2f}\n"
            f"3rd Quartile (Q3): {self.q3:.2f}\n"
            f"Range: {self.range_val:.2f}\n"
            f"Interquartile Range (IQR): {self.iqr:.2f}\n"
            f"Total Duration (records): {self.total_duration}\n"
            f"Count of Records: {self.count}\n"
            f"Variance: {self.variance:.2f}\n"
            f"Skewness: {self.skewness:.2f}\n"
            f"Kurtosis: {self.kurtosis:.2f}\n"
            f"Mode: {self.mode}\n"
            f"95% Confidence Interval: ({self.ci_low:.2f}, {self.ci_high:.2f})"
        )

        # Display the summary text
        self.display_hr_test2_summary(self.test_data)

    def display_hr_test2_summary(self, participant_label):
        # Remove previous summary if any
        if hasattr(self, 'participant_label'):
            self.layout.removeWidget(self.participant_label)
            self.participant_label.deleteLater()

        self.participant_label = QLabel(participant_label)
        self.layout.addWidget(self.participant_label)

    def mean_confidence_interval(self, data, confidence=0.95):
        import scipy.stats as stats
        n = len(data)
        mean = data.mean()
        sem = stats.sem(data)
        margin = sem * stats.t.ppf((1 + confidence) / 2., n-1)
        return mean - margin, mean + margin
