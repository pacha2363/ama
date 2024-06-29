# mod/dialogflow.py

import os
import pandas as pd
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QFileDialog, QFrame, QPushButton, QMessageBox, QScrollArea, QWidget, QHBoxLayout
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from datetime import datetime
from matplotlib.backends.backend_pdf import PdfPages


class DialogFlowFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.data = None  # Store processed data

        # Horizontal layout for buttons
        button_layout = QHBoxLayout()
        self.upload_button = QPushButton("Upload DialogFlow Files")
        self.upload_button.clicked.connect(self.upload_files)
        button_layout.addWidget(self.upload_button)

        self.report_button = QPushButton("Generate Report")
        self.report_button.setEnabled(False)  # Initially disabled
        self.report_button.clicked.connect(self.generate_report)
        button_layout.addWidget(self.report_button)

        self.csv_report_button = QPushButton("Generate Report in CSV")
        self.csv_report_button.setEnabled(False)  # Initially disabled
        self.csv_report_button.clicked.connect(self.generate_csv_report)
        button_layout.addWidget(self.csv_report_button)

        self.layout.addLayout(button_layout)

        # Add a scroll area for results
        self.scroll_area = QScrollArea()
        self.scroll_area_widget = QWidget()
        self.scroll_area_layout = QVBoxLayout(self.scroll_area_widget)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.scroll_area_widget)
        self.layout.addWidget(self.scroll_area)

        self.dialogflow_files = []

    def upload_files(self):
        options = QFileDialog.Options()
        files, _ = QFileDialog.getOpenFileNames(self, "Select DialogFlow Files", "", "CSV Files (*.csv)", options=options)
        if files:
            self.dialogflow_files = files
            self.process_files()
            self.report_button.setEnabled(True)  # Enable the report button after files are uploaded
            self.csv_report_button.setEnabled(True)  # Enable the CSV report button after files are uploaded

    def process_files(self):
        all_data = []
        for file in self.dialogflow_files:
            data = pd.read_csv(file)
            print(f"Processing file: {file}")  # Debugging statement
            print(f"Columns: {data.columns}")  # Debugging statement
            all_data.append(data)

        combined_data = pd.concat(all_data)

        # Perform analysis
        self.analyze_data(combined_data)

    def analyze_data(self, combined_data):
        # Analyze the data based on 'Utterance', 'Category', 'Confidence', and 'Strategy'
        self.utterance_counts = combined_data['Utterance'].value_counts()
        self.category_counts = combined_data['Category'].value_counts()
        self.strategy_counts = combined_data['Strategy'].value_counts()
        self.confidence_stats = combined_data['Confidence'].describe()

        self.display_results(self.utterance_counts, self.category_counts, self.strategy_counts, self.confidence_stats)
        self.plot_graphs(self.utterance_counts, self.category_counts, self.strategy_counts, self.confidence_stats)

        # Store data for access
        self.data = {
            'utterance_counts': self.utterance_counts.to_dict(),
            'category_counts': self.category_counts.to_dict(),
            'strategy_counts': self.strategy_counts.to_dict(),
            'confidence_stats': self.confidence_stats.to_dict()
        }

    def display_results(self, utterance_counts, category_counts, strategy_counts, confidence_stats):
        self.clear_layout(self.scroll_area_layout)
        self.scroll_area_layout.addWidget(QLabel(f"Number of Files Uploaded: {len(self.dialogflow_files)}"))
        self.scroll_area_layout.addWidget(QLabel("Utterance Counts:"))
        for utterance, count in utterance_counts.items():
            self.scroll_area_layout.addWidget(QLabel(f"{utterance}: {count}"))
        self.scroll_area_layout.addWidget(QLabel("\nCategory Counts:"))
        for category, count in category_counts.items():
            self.scroll_area_layout.addWidget(QLabel(f"{category}: {count}"))
        self.scroll_area_layout.addWidget(QLabel("\nStrategy Counts:"))
        for strategy, count in strategy_counts.items():
            self.scroll_area_layout.addWidget(QLabel(f"{strategy}: {count}"))
        self.scroll_area_layout.addWidget(QLabel("\nConfidence Statistics:"))
        self.scroll_area_layout.addWidget(QLabel(confidence_stats.to_string()))

    def display_error(self, message):
        self.clear_layout(self.scroll_area_layout)
        self.scroll_area_layout.addWidget(QLabel(message))

    def clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def plot_graphs(self, utterance_counts, category_counts, strategy_counts, confidence_stats):
        # Plot graphs for the different analyses

        fig, axs = plt.subplots(2, 2, figsize=(10, 10))

        utterance_counts.plot(kind='bar', ax=axs[0, 0], color='skyblue')
        axs[0, 0].set_title('Utterance Counts')
        axs[0, 0].set_xlabel('Utterance')
        axs[0, 0].set_ylabel('Count')

        category_counts.plot(kind='bar', ax=axs[0, 1], color='lightgreen')
        axs[0, 1].set_title('Category Counts')
        axs[0, 1].set_xlabel('Category')
        axs[0, 1].set_ylabel('Count')

        strategy_counts.plot(kind='bar', ax=axs[1, 0], color='salmon')
        axs[1, 0].set_title('Strategy Counts')
        axs[1, 0].set_xlabel('Strategy')
        axs[1, 0].set_ylabel('Count')

        confidence_stats.plot(kind='box', ax=axs[1, 1])
        axs[1, 1].set_title('Confidence Statistics')
        axs[1, 1].set_ylabel('Confidence')

        plt.tight_layout()

        # Save and display the plots
        output_dir = "Output"
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        self.plot_filename = os.path.join(output_dir, f"dialogflow_analysis_{timestamp}.png")
        plt.savefig(self.plot_filename)
        plt.close()

        pixmap = QPixmap(self.plot_filename)
        graph_label = QLabel()
        graph_label.setPixmap(pixmap)
        graph_label.setAlignment(Qt.AlignCenter)
        self.scroll_area_layout.addWidget(graph_label)

    def generate_report(self):
        try:
            output_dir = "generated_reports"
            os.makedirs(output_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            pdf_filename = os.path.join(output_dir, f"dialogflow_report_{timestamp}.pdf")

            with PdfPages(pdf_filename) as pdf:
                # Add results to PDF
                fig, ax = plt.subplots(figsize=(8, 6))
                ax.axis('off')
                table_data = [
                    ["Type", "Count"]
                ]
                table_data += [["Utterance: " + str(k), v] for k, v in self.utterance_counts.items()]
                table_data += [["Category: " + str(k), v] for k, v in self.category_counts.items()]
                table_data += [["Strategy: " + str(k), v] for k, v in self.strategy_counts.items()]
                table_data += [["Confidence", str(self.confidence_stats)]]
                ax.table(cellText=table_data, cellLoc='center', loc='center')
                pdf.savefig(fig)
                plt.close(fig)

                # Add plots to PDF
                if hasattr(self, 'plot_filename'):
                    fig, ax = plt.subplots(figsize=(8, 6))
                    img = plt.imread(self.plot_filename)
                    ax.imshow(img)
                    ax.axis('off')
                    pdf.savefig(fig)
                    plt.close(fig)

            QMessageBox.information(self, "Report Generated", f"PDF report generated successfully:\n{pdf_filename}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate PDF report:\n{str(e)}")

    def generate_csv_report(self):
        try:
            output_dir = "generated_reports"
            os.makedirs(output_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            csv_filename = os.path.join(output_dir, f"dialogflow_report_{timestamp}.csv")

            # Collect results data
            results_data = {
                "Type": ["Utterance"] * len(self.utterance_counts) + ["Category"] * len(self.category_counts) + ["Strategy"] * len(self.strategy_counts),
                "Value": list(self.utterance_counts.index) + list(self.category_counts.index) + list(self.strategy_counts.index),
                "Count": list(self.utterance_counts.values) + list(self.category_counts.values) + list(self.strategy_counts.values)
            }
            results_df = pd.DataFrame(results_data)

            # Save results to CSV
            results_df.to_csv(csv_filename, index=False)

            # Save confidence stats to CSV
            confidence_stats_data = self.confidence_stats.to_dict()
            confidence_stats_df = pd.DataFrame(list(confidence_stats_data.items()), columns=['Metric', 'Value'])
            confidence_stats_df.to_csv(csv_filename, mode='a', index=False)

            QMessageBox.information(self, "Report Generated", f"CSV report generated successfully:\n{csv_filename}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate CSV report:\n{str(e)}")

    def get_data(self):
        return self.data