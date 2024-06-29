# mod/ind/system_choice_analyzer.py
import pandas as pd
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton, QFileDialog, QMessageBox, QComboBox
from PyQt5.QtCore import Qt
from datetime import datetime, time

class SystemChoiceBlock(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.data = None  # Store processed data

        self.button_layout = QHBoxLayout()
        self.upload_button = QPushButton("Upload Feedback File")
        self.upload_button.clicked.connect(self.upload_system_choice_file)
        self.button_layout.addWidget(self.upload_button)

        self.layout.addLayout(self.button_layout)

        self.combo_box = QComboBox()
        self.combo_box.currentIndexChanged.connect(self.display_selected_info)
        self.layout.addWidget(self.combo_box)

        self.test_data = None

    def upload_system_choice_file(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Select System Choice File", "", "Excel Files (*.xlsx);;CSV Files (*.csv)", options=options)
        if file_path:
            self.process_system_choice_data(file_path)

    def process_system_choice_data(self, file_path):
        if file_path.endswith('.xlsx'):
            data = pd.read_excel(file_path)
        elif file_path.endswith('.csv'):
            data = pd.read_csv(file_path)
        else:
            QMessageBox.critical(self, "Error", "Unsupported file format.")
            return

        self.test_data = data
        participant_ids = data['Participant ID'].astype(str).unique()
        self.combo_box.clear()
        self.combo_box.addItems(participant_ids)

    def display_selected_info(self):
        participant_id = self.combo_box.currentText()
        if participant_id and self.test_data is not None:
            participant_data = self.test_data[self.test_data['Participant ID'].astype(str) == participant_id].iloc[0]

            first_test_strategy = participant_data['First test strategy 1']
            second_test_strategy = participant_data['Second test Strategiy 2']
            wear_glasses = participant_data['Wear Glassees']
            education_level = participant_data['Education Level']
            language_proficiency = participant_data['Language Proficiency']
            preferred_system = participant_data['Prefered System']

            start_time_first_test = self.convert_to_time(participant_data['Start times of First test strategy 1'])
            end_time_first_test = self.convert_to_time(participant_data['End Times of First test strategy 1'])
            duration_first_test = self.calculate_duration(start_time_first_test, end_time_first_test)

            start_time_second_test = self.convert_to_time(participant_data['Start times of Second test  Strategy 2'])
            end_time_second_test = self.convert_to_time(participant_data['End Times of Second test Strategy 2'])
            duration_second_test = self.calculate_duration(start_time_second_test, end_time_second_test)

            info_text = (f"Participant ID: {participant_id}\n"
                         f"First test strategy used: {first_test_strategy}\n"
                         f"Duration of first test: {duration_first_test}\n"
                         f"Second test strategy used: {second_test_strategy}\n"
                         f"Duration of second test: {duration_second_test}\n"
                         f"Wear Glasses: {wear_glasses}\n"
                         f"Education Level: {education_level}\n"
                         f"Language Proficiency: {language_proficiency}\n"
                         f"Preferred System: {preferred_system}")

            self.display_participant_info(info_text)

            # Store the processed data for report generation
            self.participant_text = info_text

    def convert_to_time(self, time_value):
        if isinstance(time_value, time):
            return time_value
        if isinstance(time_value, str):
            return datetime.strptime(time_value, '%H:%M:%S').time()
        return time_value

    def calculate_duration(self, start_time, end_time):
        # Convert time to datetime for the same date to perform subtraction
        if isinstance(start_time, time):
            start_time = datetime.combine(datetime.min, start_time)
        if isinstance(end_time, time):
            end_time = datetime.combine(datetime.min, end_time)
        duration = end_time - start_time
        return duration

    def display_participant_info(self, text):
        # Remove previous info if any
        if hasattr(self, 'participant_label'):
            self.layout.removeWidget(self.participant_label)
            self.participant_label.deleteLater()

        self.participant_label = QLabel(text)
        self.layout.addWidget(self.participant_label)