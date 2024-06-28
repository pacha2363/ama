# mod/heartrate.py
import os
import pandas as pd
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QFrame, QPushButton, QFileDialog, QMessageBox, QHBoxLayout
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np
from datetime import datetime
from scipy import stats
from matplotlib.backends.backend_pdf import PdfPages

class HeartRateFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Horizontal layout for buttons
        button_layout = QHBoxLayout()
        self.upload_button = QPushButton("Upload Heart Rate Files")
        self.upload_button.clicked.connect(self.upload_files)
        button_layout.addWidget(self.upload_button)

        self.report_button = QPushButton("Generate Report")
        self.report_button.setEnabled(False)  # Initially disabled
        self.report_button.clicked.connect(self.generate_report)
        button_layout.addWidget(self.report_button)

        self.layout.addLayout(button_layout)

        self.results_layout = QVBoxLayout()
        self.layout.addLayout(self.results_layout)

        self.heart_rate_files = []

    def upload_files(self):
        options = QFileDialog.Options()
        files, _ = QFileDialog.getOpenFileNames(self, "Select Heart Rate Files", "",
                                                "CSV Files (*.csv);;Excel Files (*.xlsx)", options=options)
        if files:
            self.heart_rate_files = files
            self.process_files()
            self.report_button.setEnabled(True)  # Enable the report button after files are uploaded

    def process_files(self):
        self.clear_layout(self.results_layout)  # Clear previous results
        all_data = []
        for file in self.heart_rate_files:
            data = pd.read_csv(file) if file.endswith('.csv') else pd.read_excel(file)
            print(f"Processing file: {file}")  # Debugging statement
            print(f"Columns: {data.columns}")  # Debugging statement
            all_data.append(data)

        combined_data = pd.concat(all_data)

        # Normalize column names
        combined_data.columns = combined_data.columns.str.strip().str.lower()
        heart_rate_column = 'hr'
        if heart_rate_column in combined_data.columns:
            heart_rate_data = combined_data[heart_rate_column].dropna()

            self.avg = heart_rate_data.mean()
            self.std_dev = heart_rate_data.std()
            self.max_val = heart_rate_data.max()
            self.min_val = heart_rate_data.min()
            self.median_val = heart_rate_data.median()
            self.q1 = heart_rate_data.quantile(0.25)
            self.q3 = heart_rate_data.quantile(0.75)
            self.range_val = self.max_val - self.min_val
            self.iqr = self.q3 - self.q1
            self.total_duration = len(heart_rate_data)  # Assuming each record represents one unit of time
            self.count = heart_rate_data.count()
            self.variance = heart_rate_data.var()
            self.skewness = heart_rate_data.skew()
            self.kurtosis = heart_rate_data.kurtosis()
            self.mode = heart_rate_data.mode()[0] if not heart_rate_data.mode().empty else None
            self.ci_low, self.ci_high = stats.norm.interval(0.95, loc=self.avg,
                                                            scale=self.std_dev / np.sqrt(self.count))

            self.display_results()
            self.plot_graph(heart_rate_data)
            self.plot_histogram(heart_rate_data)
        else:
            self.display_error("Heart rate column not found in the uploaded files.")

    def display_results(self):
        self.clear_layout(self.results_layout)

        horizontal_layout = QHBoxLayout()
        self.results_layout.addLayout(horizontal_layout)

        # Block 1
        block1_layout = QVBoxLayout()
        block1_layout.addWidget(QLabel(f"Number of Files Uploaded: {len(self.heart_rate_files)}"))
        block1_layout.addWidget(QLabel(f"Average Heart Rate: {self.avg:.2f}"))
        block1_layout.addWidget(QLabel(f"Standard Deviation: {self.std_dev:.2f}"))
        block1_layout.addWidget(QLabel(f"Maximum Heart Rate: {self.max_val:.2f}"))
        block1_layout.addWidget(QLabel(f"Minimum Heart Rate: {self.min_val:.2f}"))
        block1_layout.addWidget(QLabel(f"Median Heart Rate: {self.median_val:.2f}"))
        block1_layout.addWidget(QLabel(f"1st Quartile (Q1): {self.q1:.2f}"))
        block1_layout.addWidget(QLabel(f"3rd Quartile (Q3): {self.q3:.2f}"))
        block1_layout.addWidget(QLabel(f"Range: {self.range_val:.2f}"))

        # Block 2
        block2_layout = QVBoxLayout()
        block2_layout.addWidget(QLabel(f"Interquartile Range (IQR): {self.iqr:.2f}"))
        block2_layout.addWidget(QLabel(f"Total Duration (records): {self.total_duration}"))
        block2_layout.addWidget(QLabel(f"Count of Records: {self.count}"))
        block2_layout.addWidget(QLabel(f"Variance: {self.variance:.2f}"))
        block2_layout.addWidget(QLabel(f"Skewness: {self.skewness:.2f}"))
        block2_layout.addWidget(QLabel(f"Kurtosis: {self.kurtosis:.2f}"))
        block2_layout.addWidget(QLabel(f"Mode: {self.mode:.2f}"))
        block2_layout.addWidget(QLabel(f"95% Confidence Interval: ({self.ci_low:.2f}, {self.ci_high:.2f})"))

        horizontal_layout.addLayout(block1_layout)
        horizontal_layout.addLayout(block2_layout)

    def display_error(self, message):
        self.clear_layout(self.results_layout)
        self.results_layout.addWidget(QLabel(message))

    def clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def plot_graph(self, heart_rate_data):
        # Create the graph
        fig, ax = plt.subplots()
        ax.plot(heart_rate_data)
        ax.set_title('Heart Rate Over Time')
        ax.set_xlabel('Time')
        ax.set_ylabel('Heart Rate')

        # Normal heart rate
        normal_heart_rate = 70
        ax.axhline(y=normal_heart_rate, color='green', linestyle='--', label='Normal Heart Rate')

        # High abnormal heart rate (tachycardia)
        high_abnormal_heart_rate = 100
        ax.axhline(y=high_abnormal_heart_rate, color='red', linestyle='--', label='High Abnormal Heart Rate')

        # Low abnormal heart rate (bradycardia)
        low_abnormal_heart_rate = 60
        ax.axhline(y=low_abnormal_heart_rate, color='blue', linestyle='--', label='Low Abnormal Heart Rate')

        # Add the legend to the plot
        ax.legend()

        # Add the graph to the results layout
        canvas = FigureCanvas(fig)
        self.results_layout.addWidget(canvas)

        # Save the graph filename for PDF export
        self.graph_filename = "Output/heart_rate_graph.png"
        fig.savefig(self.graph_filename)
        plt.close(fig)

    def plot_histogram(self, heart_rate_data):
        # Create the histogram
        fig, ax = plt.subplots()
        ax.hist(heart_rate_data, bins=20, edgecolor='black')
        ax.set_title('Distribution of Heart Rate')
        ax.set_xlabel('Heart Rate')
        ax.set_ylabel('Frequency')

        # Add the histogram to the results layout
        canvas = FigureCanvas(fig)
        self.results_layout.addWidget(canvas)

        # Save the histogram filename for PDF export
        self.histogram_filename = "Output/heart_rate_histogram.png"
        fig.savefig(self.histogram_filename)
        plt.close(fig)

    def generate_report(self):
        try:
            output_dir = "pdf_exports"
            os.makedirs(output_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            pdf_filename = os.path.join(output_dir, f"heart_rate_report_{timestamp}.pdf")

            with PdfPages(pdf_filename) as pdf:
                # Add results to PDF
                fig, ax = plt.subplots(figsize=(8, 6))
                ax.axis('off')
                text = (
                    f"Number of Files Uploaded: {len(self.heart_rate_files)}\n"
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
                    f"Mode: {self.mode:.2f}\n"
                    f"95% Confidence Interval: ({self.ci_low:.2f}, {self.ci_high:.2f})"
                )
                ax.text(0.5, 0.5, text, transform=ax.transAxes, ha='center', va='center', wrap=True)
                pdf.savefig(fig)
                plt.close(fig)

                # Add graph to PDF
                if hasattr(self, 'graph_filename'):
                    fig, ax = plt.subplots(figsize=(8, 6))
                    img = plt.imread(self.graph_filename)
                    ax.imshow(img)
                    ax.axis('off')
                    pdf.savefig(fig)
                    plt.close(fig)

                # Add histogram to PDF
                if hasattr(self, 'histogram_filename'):
                    fig, ax = plt.subplots(figsize=(8, 6))
                    img = plt.imread(self.histogram_filename)
                    ax.imshow(img)
                    ax.axis('off')
                    pdf.savefig(fig)
                    plt.close(fig)

            # Show a success message
            QMessageBox.information(self, "Report Generated", f"PDF report generated successfully:\n{pdf_filename}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate PDF report:\n{str(e)}")

"""
Median Heart Rate: The middle value when the heart rates are sorted.
Quartiles: The values that divide the data into four equal parts.
Range: The difference between the maximum and minimum heart rate.
Interquartile Range (IQR): The range between the first quartile (25th percentile) and the third quartile (75th percentile).
Total Duration: The total time duration of the heart rate data.
Count of Records: The total number of heart rate records.

Median Heart Rate: Provides the central tendency of the heart rate data.
Quartiles (Q1 and Q3): Helps understand the spread and distribution of the data.
Range: Shows the difference between the highest and lowest values.
Interquartile Range (IQR): Measures the variability of the middle 50% of the data.
Total Duration (records): Gives an idea of the total number of heart rate readings.
Count of Records: Shows how many valid heart rate records are present.

Variance: Measures how much the heart rates are spread out from their average value.
Skewness: Indicates the asymmetry of the heart rate distribution.
Kurtosis: Measures the "tailedness" of the heart rate distribution.
Mode: The most frequently occurring value in the heart rate data.
95% Confidence Interval: Provides an estimate of the range in which the true mean heart rate lies with 95% confidence.
Histograms: Visual representation of the distribution of heart rate values.
Time-based Analysis: If timestamps are available, analyze and display the heart rate over different time intervals (e.g., hourly, daily).
Comparison to Normal Ranges: Compare the heart rate data against standard normal ranges for different age groups, if applicable.
Outlier Detection: Identify and report any outliers in the heart rate data.
"""
