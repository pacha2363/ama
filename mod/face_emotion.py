#mod/face_emotion.py

import os
import pandas as pd
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QFrame, QPushButton, QFileDialog, QScrollArea, QWidget, QHBoxLayout, QMessageBox, QTableWidget, QTableWidgetItem
from PyQt5.QtCore import Qt
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.metrics import classification_report
from sklearn.preprocessing import StandardScaler
from matplotlib.backends.backend_pdf import PdfPages


class FaceEmotionFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.data = None  # Store processed data

        # Horizontal layout for buttons
        button_layout = QHBoxLayout()
        self.upload_button = QPushButton("Upload Face Emotion Files")
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

        self.results_scroll = QScrollArea()
        self.results_scroll.setWidgetResizable(True)
        self.results_container = QWidget()
        self.results_layout = QVBoxLayout(self.results_container)
        self.results_container.setLayout(self.results_layout)
        self.results_scroll.setWidget(self.results_container)
        self.layout.addWidget(self.results_scroll)

        self.face_emotion_files = []
        self.au_results = []
        self.svm_report = ""

    def upload_files(self):
        options = QFileDialog.Options()
        files, _ = QFileDialog.getOpenFileNames(self, "Select Face Emotion Files", "",
                                                "CSV Files (*.csv);;Excel Files (*.xlsx)", options=options)
        if files:
            self.face_emotion_files = files
            self.process_files()
            self.report_button.setEnabled(True)  # Enable the report button after files are uploaded
            self.csv_report_button.setEnabled(True)  # Enable the CSV report button after files are uploaded

    def process_files(self):
        self.clear_layout(self.results_layout)  # Clear previous results
        all_data = []
        file_stats = []
        for file in self.face_emotion_files:
            data = pd.read_csv(file) if file.endswith('.csv') else pd.read_excel(file)
            print(f"Processing file: {file}")  # Debugging statement
            print(f"Columns: {data.columns}")  # Debugging statement
            all_data.append(data)

            # Normalize column names
            data.columns = data.columns.str.strip().str.lower()

            # Calculate statistics for the current file
            au_columns = [col for col in data.columns if col.startswith('au') and col.endswith('_r')]
            au_averages = {col: data[col].mean() for col in au_columns}
            au_variances = {col: data[col].var() for col in au_columns}
            au_std_devs = {col: data[col].std() for col in au_columns}
            file_stats.append((file, au_averages, au_variances, au_std_devs))

        combined_data = pd.concat(all_data)
        self.display_results(file_stats)
        unique_classes = combined_data['face_id'].nunique()
        if unique_classes > 1:
            self.perform_svm(combined_data)
        else:
            self.results_layout.addWidget(
                QLabel(f"SVM Classification could not be performed as there is only one class in 'face_id'."))
        self.plot_graphs(combined_data)
        self.plot_data_distribution(combined_data, au_columns)

        # Store data for access
        self.data = {
            'file_stats': file_stats,
            'combined_data': combined_data.to_dict(),
            'svm_report': self.svm_report if isinstance(self.svm_report, dict) else {},
            'au_results': self.au_results
        }

    def display_results(self, file_stats):
        self.clear_layout(self.results_layout)
        self.results_layout.addWidget(QLabel(f"Number of Files Uploaded: {len(self.face_emotion_files)}"))

        self.au_results = []  # Store AU results for the report

        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["AU", "Average", "Variance", "Standard Deviation"])
        table.setMinimumHeight(500)  # Set the minimum height for the table
        table.setMinimumWidth(self.results_scroll.width() - 20)  # Adjust the width to fit the scroll area

        row_height = 30  # Estimate height of each row
        num_visible_rows = 10  # Minimum number of visible rows
        table.setMinimumHeight(row_height * num_visible_rows + table.horizontalHeader().height())

        row = 0
        for file, au_averages, au_variances, au_std_devs in file_stats:
            for au in au_averages.keys():
                table.insertRow(row)
                table.setItem(row, 0, QTableWidgetItem(au.upper()))
                table.setItem(row, 1, QTableWidgetItem(f"{au_averages[au]:.2f}"))
                table.setItem(row, 2, QTableWidgetItem(f"{au_variances[au]:.2f}"))
                table.setItem(row, 3, QTableWidgetItem(f"{au_std_devs[au]:.2f}"))

                self.au_results.append(
                    {"AU": au.upper(), "Average": au_averages[au], "Variance": au_variances[au], "Std Dev": au_std_devs[au]})
                row += 1

        table_scroll = QScrollArea()
        table_scroll.setWidgetResizable(True)
        table_container = QWidget()
        table_layout = QVBoxLayout(table_container)
        table_container.setLayout(table_layout)
        table_layout.addWidget(table)
        table_scroll.setWidget(table_container)

        self.results_layout.addWidget(table_scroll)

    def clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def perform_svm(self, data):
        features = data[['au12_r', 'au14_r', 'au15_r', 'pose_tx', 'pose_ty', 'pose_tz']]
        labels = data['face_id']

        features = features.fillna(features.mean())
        X_train, X_test, y_train, y_test = train_test_split(features, labels, test_size=0.3, random_state=42)
        scaler = StandardScaler()
        X_train = scaler.fit_transform(X_train)
        X_test = scaler.transform(X_test)

        model = SVC(kernel='linear')
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        self.svm_report = classification_report(y_test, y_pred, output_dict=True)
        self.results_layout.addWidget(QLabel(f"SVM Classification Report:\n{classification_report(y_test, y_pred)}"))

    def plot_graphs(self, combined_data):
        self.results_layout.addWidget(
            QLabel("The following plots show the changes in Facial Action Units and Head Position over time."))

        fig, ax = plt.subplots(figsize=(10, 6))
        combined_data.plot(x='timestamp', y=['au12_r', 'au14_r', 'au15_r'], ax=ax)
        ax.set_title('Facial Action Units Over Time')
        ax.set_xlabel('Time')
        ax.set_ylabel('Values')

        canvas = FigureCanvas(fig)
        canvas.setMinimumSize(800, 600)
        self.results_layout.addWidget(canvas)

        self.graph_filename1 = "Output/face_emotion_graph1.png"
        fig.savefig(self.graph_filename1)
        plt.close(fig)

        fig, ax = plt.subplots(figsize=(10, 6))
        combined_data.plot(x='timestamp', y=['pose_tx', 'pose_ty', 'pose_tz'], ax=ax)
        ax.set_title('Head Position Over Time')
        ax.set_xlabel('Time')
        ax.set_ylabel('Position')

        canvas = FigureCanvas(fig)
        canvas.setMinimumSize(800, 600)
        self.results_layout.addWidget(canvas)

        self.graph_filename2 = "Output/face_emotion_graph2.png"
        fig.savefig(self.graph_filename2)
        plt.close(fig)

    def plot_data_distribution(self, data, au_columns):
        self.results_layout.addWidget(
            QLabel("The following histograms and box plots show the distribution of each Action Unit (AU)."))

        self.histogram_filenames = []
        self.boxplot_filenames = []

        for au in au_columns:
            fig, ax = plt.subplots(figsize=(10, 6))
            data[au].plot(kind='hist', bins=30, ax=ax, alpha=0.7, color='blue')
            ax.set_title(f'Distribution of {au.upper()}')
            ax.set_xlabel(f'{au.upper()} Values')
            ax.set_ylabel('Frequency')
            canvas = FigureCanvas(fig)
            canvas.setMinimumSize(800, 600)
            self.results_layout.addWidget(canvas)

            histogram_filename = f"Output/{au}_histogram.png"
            fig.savefig(histogram_filename)
            self.histogram_filenames.append(histogram_filename)
            plt.close(fig)

            self.results_layout.addWidget(
                QLabel(f"This histogram shows the frequency distribution of {au.upper()} values."))

            fig, ax = plt.subplots(figsize=(10, 6))
            data[au].plot(kind='box', ax=ax, vert=False)
            ax.set_title(f'Box Plot of {au.upper()}')
            ax.set_xlabel(f'{au.upper()} Values')
            canvas = FigureCanvas(fig)
            canvas.setMinimumSize(800, 600)
            self.results_layout.addWidget(canvas)

            boxplot_filename = f"Output/{au}_boxplot.png"
            fig.savefig(boxplot_filename)
            self.boxplot_filenames.append(boxplot_filename)
            plt.close(fig)

            self.results_layout.addWidget(
                QLabel(f"This box plot shows the spread and outliers of {au.upper()} values."))

    def generate_report(self):
        try:
            output_dir = "generated_reports"
            os.makedirs(output_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            pdf_filename = os.path.join(output_dir, f"face_emotion_report_{timestamp}.pdf")

            with PdfPages(pdf_filename) as pdf:
                # Add results to PDF
                fig, ax = plt.subplots(figsize=(8, 6))
                ax.axis('off')
                table_data = [
                    ["AU", "Average", "Variance", "Standard Deviation"]
                ]
                table_data += [[result["AU"], result["Average"], result["Variance"], result["Std Dev"]] for result in self.au_results]
                ax.table(cellText=table_data, cellLoc='center', loc='center')
                pdf.savefig(fig)
                plt.close(fig)

                # Add SVM report to PDF
                if hasattr(self, 'svm_report') and isinstance(self.svm_report, dict):
                    fig, ax = plt.subplots(figsize=(8, 6))
                    ax.axis('off')
                    text = self.classification_report_from_dict(self.svm_report)
                    ax.text(0.5, 0.5, text, transform=ax.transAxes, ha='center', va='center', wrap=True)
                    pdf.savefig(fig)
                    plt.close(fig)

                # Add graphs to PDF
                if hasattr(self, 'graph_filename1'):
                    fig, ax = plt.subplots(figsize=(8, 6))
                    img = plt.imread(self.graph_filename1)
                    ax.imshow(img)
                    ax.axis('off')
                    pdf.savefig(fig)
                    plt.close(fig)

                if hasattr(self, 'graph_filename2'):
                    fig, ax = plt.subplots(figsize=(8, 6))
                    img = plt.imread(self.graph_filename2)
                    ax.imshow(img)
                    ax.axis('off')
                    pdf.savefig(fig)
                    plt.close(fig)

                # Add histograms to PDF
                for filename in self.histogram_filenames:
                    fig, ax = plt.subplots(figsize=(8, 6))
                    img = plt.imread(filename)
                    ax.imshow(img)
                    ax.axis('off')
                    pdf.savefig(fig)
                    plt.close(fig)

                # Add boxplots to PDF
                for filename in self.boxplot_filenames:
                    fig, ax = plt.subplots(figsize=(8, 6))
                    img = plt.imread(filename)
                    ax.imshow(img)
                    ax.axis('off')
                    pdf.savefig(fig)
                    plt.close(fig)

            QMessageBox.information(self, "Report Generated", f"PDF report generated successfully:\n{pdf_filename}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate PDF report:\n{str(e)}")

    def classification_report_from_dict(self, report_dict):
        lines = []
        for label, metrics in report_dict.items():
            if isinstance(metrics, dict):
                lines.append(f"Label: {label}")
                for metric, value in metrics.items():
                    lines.append(f"  {metric}: {value:.2f}")
            else:
                lines.append(f"{label}: {metrics:.2f}")
        return "\n".join(lines)

    def generate_csv_report(self):
        try:
            output_dir = "generated_reports"
            os.makedirs(output_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            csv_filename = os.path.join(output_dir, f"face_emotion_report_{timestamp}.csv")

            # Collect results data
            results_data = {
                "AU": [result["AU"] for result in self.au_results],
                "Average": [result["Average"] for result in self.au_results],
                "Variance": [result["Variance"] for result in self.au_results],
                "Std Dev": [result["Std Dev"] for result in self.au_results]
            }
            results_df = pd.DataFrame(results_data)

            # Save results to CSV
            results_df.to_csv(csv_filename, index=False)

            # Save SVM report to CSV
            if hasattr(self, 'svm_report') and isinstance(self.svm_report, dict):
                svm_df = pd.DataFrame(self.svm_report).transpose()
                svm_df.to_csv(csv_filename, mode='a', header=True)

            QMessageBox.information(self, "Report Generated", f"CSV report generated successfully:\n{csv_filename}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate CSV report:\n{str(e)}")

    def get_data(self):
        return self.data