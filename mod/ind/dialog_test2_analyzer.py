# mod/ind/dialog_test2_analyzer.py
import os
import pandas as pd
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton, QFileDialog, QMessageBox
from PyQt5.QtCore import Qt
from datetime import datetime
from scipy.stats import mode

class DialogTest2Block(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.data = None  # Store processed data

        self.button_layout = QHBoxLayout()
        self.upload_button_dialog = QPushButton("Upload Dialog Test 2 File")
        self.upload_button_dialog.clicked.connect(self.upload_dialog_test2_file)
        self.button_layout.addWidget(self.upload_button_dialog)

        self.layout.addLayout(self.button_layout)

        self.test_data = None

    def upload_dialog_test2_file(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Dialog Test 2 File", "", "CSV Files (*.csv);;Excel Files (*.xlsx)", options=options)
        if file_path:
            self.process_dialog_test2_data(file_path)

    def process_dialog_test2_data(self, file_path):
        if file_path.endswith('.csv'):
            dialog_test2_data = pd.read_csv(file_path)
        else:
            dialog_test2_data = pd.read_excel(file_path)

        # Calculate additional statistics
        self.utterance_counts = dialog_test2_data['Utterance'].value_counts()
        self.category_counts = dialog_test2_data['Category'].value_counts()
        self.strategy_counts = dialog_test2_data['Strategy'].value_counts()
        self.confidence_stats = dialog_test2_data['Confidence'].describe()

        # Create summary text
        summary_text = (
            f"Category Counts:\n{self.category_counts.to_string()}\n\n"
            f"Utterance Counts:\n{self.utterance_counts.to_string()}\n\n"
            f"Strategy Counts:\n{self.strategy_counts.to_string()}\n\n"
            f"Confidence Stats:\n{self.confidence_stats.to_string()}"
        )

        # Assign the summary text to test_data for saving in the PDF
        self.test_data = summary_text

        # Display the summary text
        self.display_dialog_test2_summary(summary_text)

    def display_dialog_test2_summary(self, summary_text):
        # Remove previous summary if any
        if hasattr(self, 'summary_label'):
            self.layout.removeWidget(self.summary_label)
            self.summary_label.deleteLater()

        self.summary_label = QLabel(summary_text)
        self.layout.addWidget(self.summary_label)
