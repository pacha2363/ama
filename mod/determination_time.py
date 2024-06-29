import os
import pandas as pd
from PyQt5.QtWidgets import QDialog, QFormLayout, QLineEdit, QPushButton, QFileDialog, QMessageBox, QHBoxLayout, QWidget


class DurationCalculator(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Calculate Duration")
        self.setModal(True)

        layout = QFormLayout(self)

        # Create file input rows
        self.heartrate_file_input = QLineEdit(self)
        self.tobii_file_input = QLineEdit(self)
        self.dialogflow_file_input = QLineEdit(self)
        self.openface_file_input = QLineEdit(self)

        # Create browse buttons
        heartrate_button = QPushButton("Browse")
        heartrate_button.clicked.connect(lambda: self.browse_file(self.heartrate_file_input))

        tobii_button = QPushButton("Browse")
        tobii_button.clicked.connect(lambda: self.browse_file(self.tobii_file_input))

        dialogflow_button = QPushButton("Browse")
        dialogflow_button.clicked.connect(lambda: self.browse_file(self.dialogflow_file_input))

        openface_button = QPushButton("Browse")
        openface_button.clicked.connect(lambda: self.browse_file(self.openface_file_input))

        # Add rows to layout
        self.add_file_input_row(layout, "Heart Rate File:", self.heartrate_file_input, heartrate_button)
        self.add_file_input_row(layout, "Tobii File:", self.tobii_file_input, tobii_button)
        self.add_file_input_row(layout, "Dialogflow File:", self.dialogflow_file_input, dialogflow_button)
        self.add_file_input_row(layout, "OpenFace File:", self.openface_file_input, openface_button)

        # Calculate button
        calculate_button = QPushButton("Calculate")
        layout.addRow(calculate_button)
        calculate_button.clicked.connect(self.calculate_experiment_duration)

        self.setLayout(layout)

    def add_file_input_row(self, layout, label, line_edit, button):
        widget = QWidget()
        h_layout = QHBoxLayout(widget)
        h_layout.addWidget(line_edit)
        h_layout.addWidget(button)
        layout.addRow(label, widget)

    def browse_file(self, line_edit):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File", "", "CSV Files (*.csv);;Excel Files (*.xlsx)")
        if file_path:
            line_edit.setText(file_path)

    def calculate_experiment_duration(self):
        try:
            heartrate_file = self.heartrate_file_input.text()
            tobii_file = self.tobii_file_input.text()
            dialogflow_file = self.dialogflow_file_input.text()
            openface_file = self.openface_file_input.text()

            # Ensure all files are provided
            if not heartrate_file or not tobii_file or not dialogflow_file or not openface_file:
                QMessageBox.critical(self, "Error", "All files must be provided.")
                return

            # Load data
            heartrate_data = pd.read_csv(heartrate_file) if heartrate_file.endswith('.csv') else pd.read_excel(heartrate_file)
            tobii_data = pd.read_csv(tobii_file) if tobii_file.endswith('.csv') else pd.read_excel(tobii_file)
            dialogflow_data = pd.read_csv(dialogflow_file) if dialogflow_file.endswith('.csv') else pd.read_excel(dialogflow_file)
            openface_data = pd.read_csv(openface_file) if openface_file.endswith('.csv') else pd.read_excel(openface_file)

            # Normalize column names to lowercase
            heartrate_data.columns = heartrate_data.columns.str.lower()
            tobii_data.columns = tobii_data.columns.str.lower()
            dialogflow_data.columns = dialogflow_data.columns.str.lower()
            openface_data.columns = openface_data.columns.str.lower()

            # Check for the correct timestamp columns and convert to datetime
            if 'etimestamp' in heartrate_data.columns:
                heartrate_times = pd.to_datetime(heartrate_data['etimestamp'], unit='ms', errors='coerce')
            else:
                raise ValueError("Heart Rate file does not contain 'etimestamp' column")

            if 'etimestamp' in tobii_data.columns:
                tobii_times = pd.to_datetime(tobii_data['etimestamp'], unit='ms', errors='coerce')
            else:
                raise ValueError("Tobii file does not contain 'etimestamp' column")

            if 'etimestamp' in dialogflow_data.columns:
                dialogflow_times = pd.to_datetime(dialogflow_data['etimestamp'], unit='ms', errors='coerce')
            else:
                raise ValueError("Dialogflow file does not contain 'etimestamp' column")

            # Localize OpenFace timestamps to GMT-9
            if 'timestamp' in openface_data.columns:
                openface_times = pd.to_datetime(openface_data['timestamp'], unit='ms', errors='coerce').dt.tz_localize('Etc/GMT+9')
            else:
                raise ValueError("OpenFace file does not contain 'timestamp' column")

            # Check for any conversion errors
            if heartrate_times.isnull().any():
                raise ValueError("Heart Rate file contains invalid timestamps")

            if tobii_times.isnull().any():
                raise ValueError("Tobii file contains invalid timestamps")

            if dialogflow_times.isnull().any():
                raise ValueError("Dialogflow file contains invalid timestamps")

            if openface_times.isnull().any():
                raise ValueError("OpenFace file contains invalid timestamps")

            # Extract additional required information
            student_id = heartrate_data['student id'].iloc[0] if 'student id' in heartrate_data.columns else 'Unknown'
            participant_name = heartrate_data['participant input'].iloc[0] if 'participant input' in heartrate_data.columns else 'Unknown'
            strategy_used = dialogflow_data['strategy'].iloc[0] if 'strategy' in dialogflow_data.columns else 'Unknown'

            # Debugging statements for timestamp ranges
            print("Heart Rate Times:", heartrate_times.min(), heartrate_times.max())
            print("Tobii Times:", tobii_times.min(), tobii_times.max())
            print("Dialogflow Times:", dialogflow_times.min(), dialogflow_times.max())
            print("OpenFace Times:", openface_times.min(), openface_times.max())

            # Find the latest start time and the earliest end time
            start_time = max(heartrate_times.min(), tobii_times.min(), dialogflow_times.min(), openface_times.min())
            end_time = min(heartrate_times.max(), tobii_times.max(), dialogflow_times.max(), openface_times.max())

            # Convert start and end times to epoch
            start_time_epoch = int(start_time.timestamp() * 1000)
            end_time_epoch = int(end_time.timestamp() * 1000)

            # Calculate duration in both epoch and human-readable formats
            duration_epoch = end_time_epoch - start_time_epoch
            duration_human = pd.to_timedelta(duration_epoch, unit='ms')

            # Debugging statements for start and end times
            print("Calculated Start Time:", start_time)
            print("Calculated End Time:", end_time)

            # Save results to CSV
            output_dir = "generated_duration"
            os.makedirs(output_dir, exist_ok=True)
            result_file = os.path.join(output_dir, f"duration_{student_id}_{participant_name}_{strategy_used}.csv")

            result_data = {
                'Student ID': [student_id],
                'Participant Name': [participant_name],
                'Used Strategy': [strategy_used],
                'Start Time in Epoch': [start_time_epoch],
                'Start Time in Human': [start_time.strftime('%Y-%m-%d %H:%M:%S.%f')],
                'End Time in Epoch': [end_time_epoch],
                'End Time in Human': [end_time.strftime('%Y-%m-%d %H:%M:%S.%f')],
                'Duration in Epoch (ms)': [duration_epoch],
                'Duration in Human': [str(duration_human)]
            }

            result_df = pd.DataFrame(result_data)
            result_df.to_csv(result_file, index=False)

            # Print result_data to console
            print("Result Data:")
            for key, value in result_data.items():
                print(f"{key}: {value[0]}")

            # Format result data for display
            result_data_str = "\n".join([f"{key}: {value[0]}" for key, value in result_data.items()])

            # Display the results
            QMessageBox.information(self, "Experiment Duration",
                                    f"Start Time: {start_time}\nEnd Time: {end_time}\nDuration: {duration_human}\nResults saved to {result_file}\n\n{result_data_str}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to calculate experiment duration:\n{str(e)}")