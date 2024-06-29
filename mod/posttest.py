# mod/posttest.py
import os
import pandas as pd
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton, QFileDialog, QMessageBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from datetime import datetime
from fpdf import FPDF

class PostTestFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.data = None  # Store processed data

        self.button_layout = QHBoxLayout()
        self.upload_button_post = QPushButton("Upload Post-Test File")
        self.upload_button_post.clicked.connect(self.upload_post_test_file)
        self.button_layout.addWidget(self.upload_button_post)

        self.generate_pdf_button_post = QPushButton("Generate report")
        self.generate_pdf_button_post.setEnabled(False)  # Initially disabled
        self.generate_pdf_button_post.clicked.connect(self.generate_pdf_report)
        self.button_layout.addWidget(self.generate_pdf_button_post)

        self.layout.addLayout(self.button_layout)

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

    def upload_post_test_file(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Post-Test File", "", "CSV Files (*.csv);;Excel Files (*.xlsx)", options=options)
        if file_path:
            self.process_post_test_data(file_path)
            self.generate_pdf_button_post.setEnabled(True)  # Initially disabled

    def process_post_test_data(self, file_path):
        if file_path.endswith('.csv'):
            post_test_wtc_data = pd.read_csv(file_path)
        else:
            post_test_wtc_data = pd.read_excel(file_path)

        # Extract relevant columns for confidence, nervousness, and WtC
        confidence_columns = [col for col in post_test_wtc_data.columns if '自信' in col]
        nervousness_columns = [col for col in post_test_wtc_data.columns if '緊張' in col]
        wtc_columns = [col for col in post_test_wtc_data.columns if 'やる気' in col]

        # Extracting relevant columns
        confidence_data = post_test_wtc_data[confidence_columns]
        nervousness_data = post_test_wtc_data[nervousness_columns]
        wtc_data = post_test_wtc_data[wtc_columns]

        # Apply the updated mapping function to convert post-test WtC ratings to scores
        post_confidence_scores_updated = confidence_data.applymap(
            lambda x: self.revised_map_ratings_to_scores(x, 'confidence'))
        post_nervousness_scores_updated = nervousness_data.applymap(
            lambda x: self.revised_map_ratings_to_scores(x, 'nervousness'))
        post_wtc_scores_updated = wtc_data.applymap(lambda x: self.revised_map_ratings_to_scores(x, 'wtc'))

        # Calculate average scores for each category in the post-test
        self.average_post_confidence_score_updated = post_confidence_scores_updated.mean(axis=1).mean()
        self.average_post_nervousness_score_mean_imputed = post_nervousness_scores_updated.mean(axis=1).mean()
        self.average_post_wtc_score_updated = post_wtc_scores_updated.mean(axis=1).mean()

        # Store the processed data
        self.test_data = post_test_wtc_data

        # Store data
        self.data = {
            'confidence': self.average_post_confidence_score_updated,
            'nervousness': self.average_post_nervousness_score_mean_imputed,
            'wtc': self.average_post_wtc_score_updated
        }

        # Display the scores in the Post-Test frame
        self.display_post_test_scores(self.average_post_confidence_score_updated, self.average_post_nervousness_score_mean_imputed,
                                      self.average_post_wtc_score_updated)
        # Display the graph of the scores
        self.display_graph(self.average_post_confidence_score_updated, self.average_post_nervousness_score_mean_imputed,
                           self.average_post_wtc_score_updated)

    def display_post_test_scores(self, confidence, nervousness, wtc):
        scores_text = f"Post-Test Scores:\n\nConfidence: {confidence:.2f}\nNervousness: {nervousness:.2f}\nWtC: {wtc:.2f}"
        scores_label = QLabel(scores_text)
        self.layout.addWidget(scores_label)

    def display_graph(self, confidence, nervousness, wtc):
        categories = ['Confidence', 'Nervousness', 'WtC']
        scores = [confidence, nervousness, wtc]

        plt.figure(figsize=(8, 5))
        plt.bar(categories, scores, color=['blue', 'orange', 'green'])
        plt.xlabel('Categories')
        plt.ylabel('Scores')
        plt.title('Post-Test Scores')
        plt.ylim(0, 5)

        # Ensure the Output directory exists
        output_dir = "Output"
        os.makedirs(output_dir, exist_ok=True)

        # Create a unique filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        self.graph_filename = os.path.join(output_dir, f"post_test_scores_{timestamp}.png")
        plt.savefig(self.graph_filename)
        plt.close()

        # Display the graph in the frame
        pixmap = QPixmap(self.graph_filename)
        graph_label = QLabel()
        graph_label.setPixmap(pixmap)
        graph_label.setAlignment(Qt.AlignCenter)
        graph_label.setMinimumSize(400, 400)
        self.layout.addWidget(graph_label)

    def generate_pdf_report(self):
        try:
            # Create a new PDF document
            pdf = FPDF()

            # Add a page
            pdf.add_page()

            # Set title
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt="Post-Test Report", ln=True, align='C')

            # Add the post-test scores text
            pdf.set_font("Arial", size=10)
            scores_text = f"Post-Test Scores:\n\nConfidence: {self.average_post_confidence_score_updated:.2f}\nNervousness: {self.average_post_nervousness_score_mean_imputed:.2f}\nWtC: {self.average_post_wtc_score_updated:.2f}"
            pdf.multi_cell(0, 10, scores_text)

            # Add the graph
            pdf.image(self.graph_filename, x=10, y=None, w=100)

            # Ensure the pdf_exports directory exists
            pdf_dir = "generated_reports"
            os.makedirs(pdf_dir, exist_ok=True)

            # Create a unique filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            pdf_filename = os.path.join(pdf_dir, f"post_test_report_{timestamp}.pdf")

            # Save the PDF
            pdf.output(pdf_filename)

            # Show a success message
            QMessageBox.information(self, "Report Generated", f"PDF report generated successfully:\n{pdf_filename}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate PDF report:\n{str(e)}")

    def get_test_data(self):
        return self.test_data

    def get_data(self):
        return self.data