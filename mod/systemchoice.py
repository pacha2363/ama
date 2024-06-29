import os
import pandas as pd
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QFileDialog, QFrame, QPushButton, QHBoxLayout, QMessageBox, \
    QScrollArea, QWidget
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from datetime import datetime, date, time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages


class SystemChoiceFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.data = None  # Store processed data

        # Horizontal layout for buttons
        button_layout = QHBoxLayout()
        self.upload_button = QPushButton("Upload System Choice File")
        self.upload_button.clicked.connect(self.upload_file)
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

    def upload_file(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Select System Choice File", "",
                                                   "Excel Files (*.xlsx);;CSV Files (*.csv)", options=options)
        if file_path:
            self.process_system_choice_data(file_path)
            self.report_button.setEnabled(True)  # Enable the report button after a file is uploaded
            self.csv_report_button.setEnabled(True)  # Enable the CSV report button after a file is uploaded

    def process_system_choice_data(self, file_path):
        if file_path.endswith('.csv'):
            system_choice_data = pd.read_csv(file_path)
        else:
            system_choice_data = pd.read_excel(file_path)

        # Extract relevant data
        today = date.today()

        first_strategy_start = system_choice_data['Start times of First test strategy 1'].apply(
            lambda t: datetime.combine(today, t) if isinstance(t, time) else t
        )
        first_strategy_end = system_choice_data['End Times of First test strategy 1'].apply(
            lambda t: datetime.combine(today, t) if isinstance(t, time) else t
        )
        second_strategy_start = system_choice_data['Start times of Second test  Strategy 2'].apply(
            lambda t: datetime.combine(today, t) if isinstance(t, time) else t
        )
        second_strategy_end = system_choice_data['End Times of Second test Strategy 2'].apply(
            lambda t: datetime.combine(today, t) if isinstance(t, time) else t
        )

        # Calculate interaction times in minutes
        first_strategy_duration = (first_strategy_end - first_strategy_start).dt.total_seconds() / 60
        second_strategy_duration = (second_strategy_end - second_strategy_start).dt.total_seconds() / 60

        # Calculate statistics
        self.first_strategy_stats = {
            'average': first_strategy_duration.mean(),
            'std_dev': first_strategy_duration.std(),
            'min': first_strategy_duration.min(),
            'max': first_strategy_duration.max()
        }

        self.second_strategy_stats = {
            'average': second_strategy_duration.mean(),
            'std_dev': second_strategy_duration.std(),
            'min': second_strategy_duration.min(),
            'max': second_strategy_duration.max()
        }

        # Count preferred systems
        self.preferred_system_counts = system_choice_data['Prefered System'].value_counts()

        self.system_choice_data = system_choice_data  # Store data for report generation

        # Store data for access
        self.data = {
            'first_strategy_stats': self.first_strategy_stats,
            'second_strategy_stats': self.second_strategy_stats,
            'preferred_system_counts': self.preferred_system_counts.to_dict()
        }

        self.display_results()

    def display_results(self):
        self.clear_layout(self.results_layout)  # Clear previous results

        # Create horizontal layout for two blocks
        horizontal_layout = QHBoxLayout()
        self.results_layout.addLayout(horizontal_layout)

        # Block 1: Displaying statistics
        stats_layout = QVBoxLayout()
        stats_text = (
            "First Test Strategy 1:\n"
            f"    Average duration: {self.first_strategy_stats['average']:.2f} minutes\n"
            f"    Standard deviation: {self.first_strategy_stats['std_dev']:.2f} minutes\n"
            f"    Minimum duration: {self.first_strategy_stats['min']:.2f} minutes\n"
            f"    Maximum duration: {self.first_strategy_stats['max']:.2f} minutes\n\n"
            "Second Test Strategy 2:\n"
            f"    Average duration: {self.second_strategy_stats['average']:.2f} minutes\n"
            f"    Standard deviation: {self.second_strategy_stats['std_dev']:.2f} minutes\n"
            f"    Minimum duration: {self.second_strategy_stats['min']:.2f} minutes\n"
            f"    Maximum duration: {self.second_strategy_stats['max']:.2f} minutes\n"
        )
        stats_label = QLabel(stats_text)
        stats_label.setWordWrap(True)
        stats_layout.addWidget(stats_label)

        horizontal_layout.addLayout(stats_layout)

        # Block 2: Displaying demographic and observation/feedback data
        data_layout = QVBoxLayout()

        # Extract demographic information
        demographics = self.system_choice_data[
            ['Gender', 'Education Level', 'Language Proficiency', 'Prefered System']].describe()

        # Display demographic information
        demographics_text = "Demographic Information:\n\n" + demographics.to_string()
        demographics_label = QLabel(demographics_text)
        demographics_label.setWordWrap(True)
        data_layout.addWidget(demographics_label)

        # Extract and display observations and feedback
        observations = self.system_choice_data.filter(like='Observation')
        feedback = self.system_choice_data.filter(like='Feedback')
        obs_text = "Observations:\n" + observations.to_string(index=False)
        feedback_text = "Feedback:\n" + feedback.to_string(index=False)
        combined_text = obs_text + "\n\n" + feedback_text
        combined_label = QLabel(combined_text)
        combined_label.setWordWrap(True)
        data_layout.addWidget(combined_label)

        horizontal_layout.addLayout(data_layout)

        # Display the graph
        self.display_graph()

        # Display preferred system graph
        self.display_preferred_system_graph()

    def display_graph(self):
        categories = ['Average', 'Standard Deviation', 'Min', 'Max']
        first_strategy_values = [self.first_strategy_stats['average'], self.first_strategy_stats['std_dev'],
                                 self.first_strategy_stats['min'], self.first_strategy_stats['max']]
        second_strategy_values = [self.second_strategy_stats['average'], self.second_strategy_stats['std_dev'],
                                  self.second_strategy_stats['min'], self.second_strategy_stats['max']]

        x = range(len(categories))

        plt.figure(figsize=(6, 4))
        plt.bar(x, first_strategy_values, width=0.4, label='First Strategy', align='center')
        plt.bar(x, second_strategy_values, width=0.4, label='Second Strategy', align='edge')
        plt.xticks(x, categories)
        plt.xlabel('Statistics')
        plt.ylabel('Duration (minutes)')
        plt.title('Interaction Times for Test Strategies')
        plt.legend()

        # Ensure the Output directory exists
        output_dir = "Output"
        os.makedirs(output_dir, exist_ok=True)

        # Create a unique filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        self.graph_filename = os.path.join(output_dir, f"system_choice_data_{timestamp}.png")
        plt.savefig(self.graph_filename)
        plt.close()

        # Display the graph in the frame
        pixmap = QPixmap(self.graph_filename)
        graph_label = QLabel()
        graph_label.setPixmap(pixmap)
        graph_label.setAlignment(Qt.AlignCenter)
        self.results_layout.addWidget(graph_label)


    def display_preferred_system_graph(self):
        systems = self.preferred_system_counts.index
        counts = self.preferred_system_counts.values

        plt.figure(figsize=(6, 4))
        plt.bar(systems, counts, color=['blue', 'orange', 'green'])
        plt.xlabel('Systems')
        plt.ylabel('Counts')
        plt.title('Preferred Systems Count')

        # Ensure the Output directory exists
        output_dir = "Output"
        os.makedirs(output_dir, exist_ok=True)

        # Create a unique filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        self.preferred_system_graph_filename = os.path.join(output_dir, f"preferred_system_count_{timestamp}.png")
        plt.savefig(self.preferred_system_graph_filename)
        plt.close()

        # Display the graph in the frame
        pixmap = QPixmap(self.preferred_system_graph_filename)
        graph_label = QLabel()
        graph_label.setPixmap(pixmap)
        graph_label.setAlignment(Qt.AlignCenter)
        self.results_layout.addWidget(graph_label)

    def clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def generate_report(self):
        try:
            output_dir = "generated_reports"
            os.makedirs(output_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            pdf_filename = os.path.join(output_dir, f"system_choice_report_{timestamp}.pdf")

            with PdfPages(pdf_filename) as pdf:
                # Add statistics to PDF
                fig, ax = plt.subplots(figsize=(8, 6))
                ax.axis('off')
                table_data = [
                    ["Statistic", "First Strategy", "Second Strategy"],
                    ["Average", f"{self.first_strategy_stats['average']:.2f}", f"{self.second_strategy_stats['average']:.2f}"],
                    ["Standard Deviation", f"{self.first_strategy_stats['std_dev']:.2f}", f"{self.second_strategy_stats['std_dev']:.2f}"],
                    ["Min", f"{self.first_strategy_stats['min']:.2f}", f"{self.second_strategy_stats['min']:.2f}"],
                    ["Max", f"{self.first_strategy_stats['max']:.2f}", f"{self.second_strategy_stats['max']:.2f}"]
                ]
                ax.table(cellText=table_data, cellLoc='center', loc='center')
                pdf.savefig(fig)
                plt.close(fig)

                # Add demographic information and feedback to PDF
                fig, ax = plt.subplots(figsize=(8, 6))
                ax.axis('off')
                demographics_text = "Demographic Information:\n\n" + self.system_choice_data[['Gender', 'Education Level', 'Language Proficiency', 'Prefered System']].describe().to_string()
                observations = self.system_choice_data.filter(like='Observation').to_string(index=False)
                feedback = self.system_choice_data.filter(like='Feedback').to_string(index=False)
                text = demographics_text + "\n\nObservations:\n" + observations + "\n\nFeedback:\n" + feedback
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

                # Add preferred system graph to PDF
                if hasattr(self, 'preferred_system_graph_filename'):
                    fig, ax = plt.subplots(figsize=(8, 6))
                    img = plt.imread(self.preferred_system_graph_filename)
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
            csv_filename = os.path.join(output_dir, f"system_choice_report_{timestamp}.csv")

            # Collect statistics data
            stats_data = {
                "Statistic": ["Average", "Standard Deviation", "Min", "Max"],
                "First Strategy": [self.first_strategy_stats['average'], self.first_strategy_stats['std_dev'], self.first_strategy_stats['min'], self.first_strategy_stats['max']],
                "Second Strategy": [self.second_strategy_stats['average'], self.second_strategy_stats['std_dev'], self.second_strategy_stats['min'], self.second_strategy_stats['max']]
            }
            stats_df = pd.DataFrame(stats_data)

            # Collect demographic information and feedback data
            demographics = self.system_choice_data[['Gender', 'Education Level', 'Language Proficiency', 'Prefered System']].describe()
            observations = self.system_choice_data.filter(like='Observation')
            feedback = self.system_choice_data.filter(like='Feedback')

            # Save statistics to CSV
            stats_df.to_csv(csv_filename, index=False)

            # Append demographic and feedback data to CSV
            with open(csv_filename, 'a') as f:
                f.write("\nDemographic Information:\n")
                demographics.to_csv(f, mode='a')
                f.write("\nObservations:\n")
                observations.to_csv(f, mode='a', index=False)
                f.write("\nFeedback:\n")
                feedback.to_csv(f, mode='a', index=False)

            QMessageBox.information(self, "Report Generated", f"CSV report generated successfully:\n{csv_filename}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate CSV report:\n{str(e)}")

    def get_data(self):
        return self.data
