# mod/tobii.py
import os
import pandas as pd
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QFrame, QPushButton, QFileDialog, QScrollArea, QWidget, QHBoxLayout, QMessageBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from sklearn.svm import SVC
from statsmodels.formula.api import ols
import statsmodels.api as sm
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.impute import SimpleImputer
from matplotlib.backends.backend_pdf import PdfPages

class TobiiFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Horizontal layout for buttons
        button_layout = QHBoxLayout()
        self.upload_button = QPushButton("Upload Tobii Files")
        self.upload_button.clicked.connect(self.upload_files)
        button_layout.addWidget(self.upload_button)

        self.report_button = QPushButton("Generate Report")
        self.report_button.setEnabled(False)  # Initially disabled
        self.report_button.clicked.connect(self.generate_report)
        button_layout.addWidget(self.report_button)

        self.layout.addLayout(button_layout)

        self.results_scroll = QScrollArea()
        self.results_scroll.setWidgetResizable(True)
        self.results_container = QWidget()
        self.results_layout = QVBoxLayout(self.results_container)
        self.results_container.setLayout(self.results_layout)
        self.results_scroll.setWidget(self.results_container)
        self.layout.addWidget(self.results_scroll)

        self.tobii_files = []

    def upload_files(self):
        options = QFileDialog.Options()
        files, _ = QFileDialog.getOpenFileNames(self, "Select Tobii Files", "",
                                                "CSV Files (*.csv);;Excel Files (*.xlsx)", options=options)
        if files:
            self.tobii_files = files
            self.process_files()
            self.report_button.setEnabled(True)  # Enable the report button after files are uploaded

    def process_files(self):
        self.clear_layout(self.results_layout)  # Clear previous results
        all_data = []
        for file in self.tobii_files:
            data = pd.read_csv(file) if file.endswith('.csv') else pd.read_excel(file)
            print(f"Processing file: {file}")  # Debugging statement
            print(f"Columns: {data.columns}")  # Debugging statement
            all_data.append(data)

        combined_data = pd.concat(all_data)

        # Normalize column names
        combined_data.columns = combined_data.columns.str.strip().str.lower()

        # Calculate statistics
        self.left_eye_x_avg = combined_data['left_eye_x'].mean()
        self.left_eye_y_avg = combined_data['left_eye_y'].mean()
        self.right_eye_x_avg = combined_data['right_eye_x'].mean()
        self.right_eye_y_avg = combined_data['right_eye_y'].mean()
        self.head_pos_x_avg = combined_data['head_position_x'].mean()
        self.head_pos_y_avg = combined_data['head_position_y'].mean()
        self.head_pos_z_avg = combined_data['head_position_z'].mean()

        # Display results
        self.display_results()
        self.plot_graphs(combined_data)

        # Perform ANCOVA
        self.perform_ancova(combined_data)

        # Perform SVM Analysis
        self.perform_svm(combined_data)

    def display_results(self):
        self.clear_layout(self.results_layout)
        self.results_layout.addWidget(QLabel(f"Number of Files Uploaded: {len(self.tobii_files)}"))
        self.results_layout.addWidget(QLabel(f"Average Left Eye X: {self.left_eye_x_avg:.2f}"))
        self.results_layout.addWidget(QLabel(f"Average Left Eye Y: {self.left_eye_y_avg:.2f}"))
        self.results_layout.addWidget(QLabel(f"Average Right Eye X: {self.right_eye_x_avg:.2f}"))
        self.results_layout.addWidget(QLabel(f"Average Right Eye Y: {self.right_eye_y_avg:.2f}"))
        self.results_layout.addWidget(QLabel(f"Average Head Position X: {self.head_pos_x_avg:.2f}"))
        self.results_layout.addWidget(QLabel(f"Average Head Position Y: {self.head_pos_y_avg:.2f}"))
        self.results_layout.addWidget(QLabel(f"Average Head Position Z: {self.head_pos_z_avg:.2f}"))

    def clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def plot_graphs(self, combined_data):
        fig, ax = plt.subplots(figsize=(8, 4))  # Set a minimum size for the plot
        combined_data.plot(x='timestamp', y=['left_eye_x', 'right_eye_x', 'head_position_x'], ax=ax)
        ax.set_title('Eye and Head Position Over Time')
        ax.set_xlabel('Time')
        ax.set_ylabel('Position')

        canvas = FigureCanvas(fig)
        canvas.setMinimumSize(800, 300)  # Setting minimum size
        self.results_layout.addWidget(canvas)

        self.graph_filename1 = "Output/tobii_graph1.png"
        fig.savefig(self.graph_filename1)
        plt.close(fig)

        fig, ax = plt.subplots(figsize=(8, 4))  # Set a minimum size for the plot
        combined_data.plot(x='timestamp', y=['left_pupil_diameter', 'right_pupil_diameter'], ax=ax)
        ax.set_title('Pupil Diameter Over Time')
        ax.set_xlabel('Time')
        ax.set_ylabel('Pupil Diameter')

        canvas = FigureCanvas(fig)
        canvas.setMinimumSize(800, 300)  # Setting minimum size
        self.results_layout.addWidget(canvas)

        self.graph_filename2 = "Output/tobii_graph2.png"
        fig.savefig(self.graph_filename2)
        plt.close(fig)

    def perform_ancova(self, data):
        formula = 'left_eye_x ~ C(participant_name) + timestamp'
        model = ols(formula, data=data).fit()
        ancova_table = sm.stats.anova_lm(model, typ=2)
        self.ancova_results = ancova_table
        self.results_layout.addWidget(QLabel(f"ANCOVA Results:\n{ancova_table}"))

    def perform_svm(self, data):
        # Prepare data
        features = data[['left_eye_x', 'left_eye_y', 'right_eye_x', 'right_eye_y', 'head_position_x', 'head_position_y',
                         'head_position_z']]
        labels = data['participant_name']

        # Impute missing values
        imputer = SimpleImputer(strategy='mean')
        features_imputed = imputer.fit_transform(features)

        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(features_imputed)

        X_train, X_test, y_train, y_test = train_test_split(features_scaled, labels, test_size=0.3, random_state=42)

        model = SVC(kernel='linear')
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)

        self.svm_report = classification_report(y_test, y_pred)
        self.results_layout.addWidget(QLabel(f"SVM Classification Report:\n{self.svm_report}"))

    def generate_report(self):
        try:
            output_dir = "pdf_exports"
            os.makedirs(output_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            pdf_filename = os.path.join(output_dir, f"tobii_report_{timestamp}.pdf")

            with PdfPages(pdf_filename) as pdf:
                # Add results to PDF
                fig, ax = plt.subplots(figsize=(8, 6))
                ax.axis('off')
                text = (
                    f"Number of Files Uploaded: {len(self.tobii_files)}\n"
                    f"Average Left Eye X: {self.left_eye_x_avg:.2f}\n"
                    f"Average Left Eye Y: {self.left_eye_y_avg:.2f}\n"
                    f"Average Right Eye X: {self.right_eye_x_avg:.2f}\n"
                    f"Average Right Eye Y: {self.right_eye_y_avg:.2f}\n"
                    f"Average Head Position X: {self.head_pos_x_avg:.2f}\n"
                    f"Average Head Position Y: {self.head_pos_y_avg:.2f}\n"
                    f"Average Head Position Z: {self.head_pos_z_avg:.2f}\n"
                )
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

                # Add ANCOVA results to PDF
                if hasattr(self, 'ancova_results'):
                    fig, ax = plt.subplots(figsize=(8, 6))
                    ax.axis('off')
                    text = f"ANCOVA Results:\n{self.ancova_results}"
                    ax.text(0.5, 0.5, text, transform=ax.transAxes, ha='center', va='center', wrap=True)
                    pdf.savefig(fig)
                    plt.close(fig)

                # Add SVM results to PDF
                if hasattr(self, 'svm_report'):
                    fig, ax = plt.subplots(figsize=(8, 6))
                    ax.axis('off')
                    text = f"SVM Classification Report:\n{self.svm_report}"
                    ax.text(0.5, 0.5, text, transform=ax.transAxes, ha='center', va='center', wrap=True)
                    pdf.savefig(fig)
                    plt.close(fig)

            # Show a success message
            QMessageBox.information(self, "Report Generated", f"PDF report generated successfully:\n{pdf_filename}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate PDF report:\n{str(e)}")
