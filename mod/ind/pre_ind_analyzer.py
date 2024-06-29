# mod/ind/pre_ind_analyzer.py
import os
import pandas as pd
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton, QFileDialog, QMessageBox, QComboBox
from PyQt5.QtCore import Qt


class PreTestBlock(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.data = None  # Store processed data

        self.button_layout = QHBoxLayout()
        self.upload_button_pre = QPushButton("Upload Pre-Test File")
        self.upload_button_pre.clicked.connect(self.upload_pre_test_file)
        self.button_layout.addWidget(self.upload_button_pre)

        self.layout.addLayout(self.button_layout)

        self.combo_box = QComboBox()
        self.combo_box.currentIndexChanged.connect(self.display_selected_scores)
        self.layout.addWidget(self.combo_box)

        self.test_data = None

    def revised_map_ratings_to_scores(self, rating, category):
        if isinstance(rating, str):
            rating = rating.strip()
            if category == 'confidence':
                if '絶対できない' in rating:
                    return 0
                elif 'あまりできない' in rating:
                    return 1
                elif '場合によりけり' in rating:
                    return 2
                elif '多分できる' in rating:
                    return 3
                elif '機会があればやってみたい' in rating:
                    return 4
                elif '簡単にできる' in rating:
                    return 5
            elif category == 'nervousness':
                if 'すごく緊張する' in rating:
                    return 0
                elif 'できれば避けたい' in rating:
                    return 1
                elif 'かなり緊張する' in rating:
                    return 2
                elif 'すこしは緊張する' in rating:
                    return 3
                elif '緊張しない' in rating:
                    return 4
            elif category == 'wtc':
                if 'できれば避けたい' in rating:
                    return 0
                elif '機会があればやってみたい' in rating:
                    return 1
                elif '多分できる' in rating:
                    return 2
                elif '簡単にできる' in rating:
                    return 3
        return None

    def upload_pre_test_file(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Pre-Test File", "", "CSV Files (*.csv);;Excel Files (*.xlsx)", options=options)
        if file_path:
            self.process_pre_test_data(file_path)

    def process_pre_test_data(self, file_path):
        if file_path.endswith('.csv'):
            pre_test_wtc_data = pd.read_csv(file_path)
        else:
            pre_test_wtc_data = pd.read_excel(file_path)

        # Extract relevant columns for confidence, nervousness, and WtC
        confidence_columns = [col for col in pre_test_wtc_data.columns if '自信' in col]
        nervousness_columns = [col for col in pre_test_wtc_data.columns if '緊張' in col]
        wtc_columns = [col for col in pre_test_wtc_data.columns if 'やる気' in col]

        # Extracting relevant columns
        confidence_data = pre_test_wtc_data[confidence_columns]
        nervousness_data = pre_test_wtc_data[nervousness_columns]
        wtc_data = pre_test_wtc_data[wtc_columns]

        # Apply the updated mapping function to convert pre-test WtC ratings to scores
        pre_confidence_scores_updated = confidence_data.applymap(
            lambda x: self.revised_map_ratings_to_scores(x, 'confidence'))
        pre_nervousness_scores_updated = nervousness_data.applymap(
            lambda x: self.revised_map_ratings_to_scores(x, 'nervousness'))
        pre_wtc_scores_updated = wtc_data.applymap(lambda x: self.revised_map_ratings_to_scores(x, 'wtc'))

        # Store the processed data
        self.test_data = pre_test_wtc_data
        self.pre_confidence_scores_updated = pre_confidence_scores_updated
        self.pre_nervousness_scores_updated = pre_nervousness_scores_updated
        self.pre_wtc_scores_updated = pre_wtc_scores_updated

        # Populate the combo box with respondent IDs
        respondent_ids = pre_test_wtc_data['Respondent ID'].astype(str).unique()
        self.combo_box.clear()
        self.combo_box.addItems(respondent_ids)

    def display_selected_scores(self):
        respondent_id = self.combo_box.currentText()
        if respondent_id and self.test_data is not None:
            idx = self.test_data[self.test_data['Respondent ID'].astype(str) == respondent_id].index[0]
            participant_confidence = self.pre_confidence_scores_updated.loc[idx].mean()
            participant_nervousness = self.pre_nervousness_scores_updated.loc[idx].mean()
            participant_wtc = self.pre_wtc_scores_updated.loc[idx].mean()

            max_score_confidence = 5
            max_score_nervousness = 4
            max_score_wtc = 3

            participant_text = (f"Respondent ID {respondent_id} Scores:\n"
                                f"Confidence: {participant_confidence:.2f} on {max_score_confidence}\n"
                                f"Nervousness: {participant_nervousness:.2f} on {max_score_nervousness}\n"
                                f"WtC: {participant_wtc:.2f} on {max_score_wtc}")
            self.display_participant_scores(participant_text)

    def display_participant_scores(self, text):
        # Remove previous scores if any
        if hasattr(self, 'participant_label'):
            self.layout.removeWidget(self.participant_label)
            self.participant_label.deleteLater()

        self.participant_label = QLabel(text)
        self.layout.addWidget(self.participant_label)
