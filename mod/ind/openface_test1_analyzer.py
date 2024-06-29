# mod/ind/openface_test1_analyzer.py
import os
import pandas as pd
from scipy.stats import skew, kurtosis, mode, hmean, gmean
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton, QFileDialog, QMessageBox
from PyQt5.QtCore import Qt
from datetime import datetime

class OpenFaceTest1Block(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.data = None  # Store processed data

        self.button_layout = QHBoxLayout()
        self.upload_button_openface = QPushButton("Upload OpenFace Test 1 File")
        self.upload_button_openface.clicked.connect(self.upload_openface_test1_file)
        self.button_layout.addWidget(self.upload_button_openface)

        self.layout.addLayout(self.button_layout)

        self.test_data = None

    def upload_openface_test1_file(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Select OpenFace Test 1 File", "", "CSV Files (*.csv);;Excel Files (*.xlsx)", options=options)
        if file_path:
            self.process_openface_test1_data(file_path)

    def process_openface_test1_data(self, file_path):
        if file_path.endswith('.csv'):
            openface_test1_data = pd.read_csv(file_path)
        else:
            openface_test1_data = pd.read_excel(file_path)

        # Extract relevant columns and calculate statistics
        metrics = {
            'AU01_r': openface_test1_data['AU01_r'],
            'AU02_r': openface_test1_data['AU02_r'],
            'AU04_r': openface_test1_data['AU04_r'],
            'AU05_r': openface_test1_data['AU05_r'],
            'AU06_r': openface_test1_data['AU06_r'],
            'AU07_r': openface_test1_data['AU07_r'],
            'AU09_r': openface_test1_data['AU09_r'],
            'AU10_r': openface_test1_data['AU10_r'],
            'AU12_r': openface_test1_data['AU12_r'],
            'AU14_r': openface_test1_data['AU14_r'],
            'AU15_r': openface_test1_data['AU15_r'],
            'AU17_r': openface_test1_data['AU17_r'],
            'AU20_r': openface_test1_data['AU20_r'],
            'AU23_r': openface_test1_data['AU23_r'],
            'AU25_r': openface_test1_data['AU25_r'],
            'AU26_r': openface_test1_data['AU26_r'],
            'AU45_r': openface_test1_data['AU45_r'],
        }

        # Calculate statistics
        stats = {}
        for metric, data in metrics.items():
            stats[f'Average {metric}'] = data.mean()
            stats[f'Standard Deviation {metric}'] = data.std()
            stats[f'Maximum {metric}'] = data.max()
            stats[f'Minimum {metric}'] = data.min()
            stats[f'Median {metric}'] = data.median()
            stats[f'Range {metric}'] = data.max() - data.min()
            stats[f'Skewness {metric}'] = skew(data)
            stats[f'Kurtosis {metric}'] = kurtosis(data)
            stats[f'Variance {metric}'] = data.var()
            stats[f'Coefficient of Variation {metric}'] = data.std() / data.mean() if data.mean() != 0 else 0
            mode_result = mode(data, keepdims=True)
            stats[f'Mode {metric}'] = mode_result.mode[0] if len(mode_result.mode) > 0 else 'N/A'
            stats[f'1st Quartile (Q1) {metric}'] = data.quantile(0.25)
            stats[f'3rd Quartile (Q3) {metric}'] = data.quantile(0.75)
            stats[f'IQR {metric}'] = data.quantile(0.75) - data.quantile(0.25)
            stats[f'10th Percentile {metric}'] = data.quantile(0.10)
            stats[f'90th Percentile {metric}'] = data.quantile(0.90)
            stats[f'Mean Absolute Deviation {metric}'] = self.mean_absolute_deviation(data)
            stats[f'Harmonic Mean {metric}'] = hmean(data[data > 0]) if (data > 0).any() else 'N/A'
            stats[f'Geometric Mean {metric}'] = gmean(data[data > 0]) if (data > 0).any() else 'N/A'
            stats[f'Count {metric}'] = data.count()
            stats[f'Sum {metric}'] = data.sum()
            stats[f'95% Confidence Interval {metric}'] = self.mean_confidence_interval(data)

        # Create summary text
        self.test_data = '\n'.join([f"{key}: {value}" for key, value in stats.items()])

        # Display the summary text
        self.display_openface_test1_summary(self.test_data)

    def display_openface_test1_summary(self, summary_text):
        # Remove previous summary if any
        if hasattr(self, 'summary_label'):
            self.layout.removeWidget(self.summary_label)
            self.summary_label.deleteLater()

        self.summary_label = QLabel(summary_text)
        self.layout.addWidget(self.summary_label)

    def mean_absolute_deviation(self, data):
        mean = data.mean()
        return (data - mean).abs().mean()

    def mean_confidence_interval(self, data, confidence=0.95):
        import scipy.stats as stats
        n = len(data)
        mean = data.mean()
        sem = stats.sem(data)
        margin = sem * stats.t.ppf((1 + confidence) / 2., n-1)
        return mean - margin, mean + margin