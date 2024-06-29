import os
import pandas as pd
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QDialog, QFormLayout, QLineEdit, QPushButton, QFileDialog, QMessageBox, QHBoxLayout, QWidget

def DurationCalculatorFunction(parent=None):
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

        def browse_file(self, line_edit):
            file_path, _ = QFileDialog.getOpenFileName(self, "Select File", "", "CSV Files (*.csv);;Excel Files (*.xlsx)")
            if file_path:
                line_edit.setText(file_path)

        def add_file_input_row(self, layout, label_text, line_edit, button):
            container = QWidget()
            hbox = QHBoxLayout(container)
            hbox.addWidget(line_edit)
            hbox.addWidget(button)
            layout.addRow(label_text, container)

        def calculate_experiment_duration(self):
            try:
                heartrate_df = pd.read_csv(self.heartrate_file_input.text())
                tobii_df = pd.read_csv(self.tobii_file_input.text())
                dialogflow_df = pd.read_csv(self.dialogflow_file_input.text())
                openface_df = pd.read_csv(self.openface_file_input.text())

                # Debugging output to show column names
                print("Heart rate file columns:", heartrate_df.columns)
                print("Tobii file columns:", tobii_df.columns)
                print("Dialogflow file columns:", dialogflow_df.columns)
                print("OpenFace file columns:", openface_df.columns)

                # Normalize column names to lowercase
                heartrate_df.columns = heartrate_df.columns.str.lower()
                tobii_df.columns = tobii_df.columns.str.lower()
                dialogflow_df.columns = dialogflow_df.columns.str.lower()
                openface_df.columns = openface_df.columns.str.lower()

                # Check for Etimestamp columns
                if 'etimestamp' not in heartrate_df.columns:
                    raise ValueError("Heart rate file is missing 'etimestamp' column.")
                if 'etimestamp' not in tobii_df.columns:
                    raise ValueError("Tobii file is missing 'etimestamp' column.")
                if 'etimestamp' not in dialogflow_df.columns:
                    raise ValueError("Dialogflow file is missing 'etimestamp' column.")
                if 'timestamp' not in openface_df.columns:
                    raise ValueError("OpenFace file is missing 'timestamp' column.")

                # Convert all timestamps to datetime and apply timezone where necessary
                heartrate_times = pd.to_datetime(heartrate_df['etimestamp'], unit='ms', errors='coerce').dt.tz_localize('UTC').dt.tz_convert('Asia/Tokyo')
                tobii_times = pd.to_datetime(tobii_df['etimestamp'], unit='ms', errors='coerce').dt.tz_localize('UTC').dt.tz_convert('Asia/Tokyo')
                dialogflow_times = pd.to_datetime(dialogflow_df['etimestamp'], unit='ms', errors='coerce').dt.tz_localize('UTC').dt.tz_convert('Asia/Tokyo')
                openface_times = pd.to_datetime(openface_df['timestamp'], unit='ms', errors='coerce')

                # Convert all timestamps to timezone-naive
                heartrate_times = heartrate_times.dt.tz_localize(None)
                tobii_times = tobii_times.dt.tz_localize(None)
                dialogflow_times = dialogflow_times.dt.tz_localize(None)
                openface_times = openface_times.dt.tz_localize(None)

                # Debugging: Print the min and max times for each data source
                print("Heart Rate Times:", heartrate_times.min(), heartrate_times.max())
                print("Tobii Times:", tobii_times.min(), tobii_times.max())
                print("Dialogflow Times:", dialogflow_times.min(), dialogflow_times.max())
                print("OpenFace Times:", openface_times.min(), openface_times.max())

                # Find the latest start time and the earliest end time
                start_time = max(heartrate_times.dropna().min(), tobii_times.dropna().min(), dialogflow_times.dropna().min(), openface_times.dropna().min())
                end_time = min(heartrate_times.dropna().max(), tobii_times.dropna().max(), dialogflow_times.dropna().max(), openface_times.dropna().max())

                # Extract additional required information
                student_id = heartrate_df['student id'].iloc[0] if 'student id' in heartrate_df.columns else 'Unknown'
                participant_name = heartrate_df['participant input'].iloc[0] if 'participant input' in heartrate_df.columns else 'Unknown'
                strategy_used = dialogflow_df['strategy'].iloc[0] if 'strategy' in dialogflow_df.columns else 'Unknown'

                # Convert start and end times to epoch
                start_time_epoch = int(start_time.timestamp() * 1000)
                end_time_epoch = int(end_time.timestamp() * 1000)

                # Calculate duration in both epoch and human-readable formats
                duration_epoch = end_time_epoch - start_time_epoch
                #duration_human = pd.to_timedelta(duration_epoch, unit='ms')

                # Calculate duration in both epoch and human-readable formats
                #if end_time_epoch >= start_time_epoch:
                #    duration_epoch = end_time_epoch - start_time_epoch
                #else:
                #    duration_epoch = start_time_epoch - end_time_epoch

                # Convert duration to human-readable format
                duration_human = pd.to_timedelta(duration_epoch, unit='ms')
                duration_human_str = f"{duration_human.components.hours} hours, {duration_human.components.minutes} minutes, {duration_human.components.seconds} seconds, {duration_human.components.milliseconds} milliseconds"

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
                    'Duration in Human': [duration_human_str]
                }

                result_df = pd.DataFrame(result_data)
                result_df.to_csv(result_file, index=False)

                # Print result_data to console
                print("Result Data:")
                for key, value in result_data.items():
                    print(f"{key}: {value[0]}")

                # Plot the duration
                plt.figure(figsize=(10, 6))
                plt.barh('Duration', duration_epoch, color='blue')
                plt.xlabel('Duration (ms)')
                plt.title('Experiment Duration')
                plt.savefig(os.path.join(output_dir, f"duration_plot_{student_id}_{participant_name}_{strategy_used}.png"))
                #plt.show()

                # Format result data for display
                result_data_str = "\n".join([f"{key}: {value[0]}" for key, value in result_data.items()])

                # Display the results with warning if duration is negative
                if duration_epoch < 0:
                    QMessageBox.warning(self, "Experiment Duration",
                                        f"Warning: The calculated duration is negative.\n\n"
                                        f"Start Time: {start_time}\nEnd Time: {end_time}\nDuration: {duration_human}\n"
                                        f"Results saved to {result_file}\n\n{result_data_str}")
                else:
                    QMessageBox.information(self, "Experiment Duration",
                                            f"Start Time: {start_time}\nEnd Time: {end_time}\nDuration: {duration_human}\n"
                                            f"Results saved to {result_file}\n\n{result_data_str}")

            except Exception as e:
                QMessageBox.critical(self, "Error", f"An error occurred while calculating duration: {e}")

    return DurationCalculator(parent)
