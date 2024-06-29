# mod/ind/hrs_comparison_analyzer.py
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox
from PyQt5.QtCore import Qt

class HRsComparisonBlock(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.compare_button = QPushButton("Compare HR Test 1 and HR Test 2")
        self.compare_button.clicked.connect(self.compare_hr_tests)
        self.layout.addWidget(self.compare_button)

        self.table_widget = QTableWidget()
        self.layout.addWidget(self.table_widget)

    def compare_hr_tests(self):
        try:
            parent_window = self.parent().parent().parent()  # Get the parent QDialog
            hr_test1_block = parent_window.blocks_instances.get("HR Test 1")
            hr_test2_block = parent_window.blocks_instances.get("HR Test 2")

            if hr_test1_block is None or hr_test2_block is None:
                raise ValueError("Both HR Test 1 and HR Test 2 blocks must be present")

            hr_test1_data = hr_test1_block.test_data.split("\n")
            hr_test2_data = hr_test2_block.test_data.split("\n")

            headers = ["Metric", "HR Test 1", "HR Test 2", "Percentage Difference"]
            self.table_widget.setColumnCount(4)
            self.table_widget.setHorizontalHeaderLabels(headers)
            self.table_widget.setRowCount(len(hr_test1_data))

            for i, (hr1, hr2) in enumerate(zip(hr_test1_data, hr_test2_data)):
                metric = hr1.split(":")[0]
                hr1_value = hr1.split(":")[1].strip()
                hr2_value = hr2.split(":")[1].strip()

                hr1_item = QTableWidgetItem(hr1_value)
                hr2_item = QTableWidgetItem(hr2_value)
                percentage_item = QTableWidgetItem()

                # Convert values to float for comparison
                try:
                    hr1_float = float(hr1_value)
                    hr2_float = float(hr2_value)

                    if hr1_float < hr2_float:
                        hr1_item.setBackground(Qt.red)
                        hr2_item.setBackground(Qt.blue)
                        if hr1_float != 0:
                            percentage_diff = ((hr2_float - hr1_float) / hr1_float) * 100
                            percentage_item.setText(f"{percentage_diff:.2f}%")
                        else:
                            percentage_item.setText("N/A")
                    elif hr1_float > hr2_float:
                        hr1_item.setBackground(Qt.blue)
                        hr2_item.setBackground(Qt.red)
                        if hr2_float != 0:
                            percentage_diff = ((hr1_float - hr2_float) / hr2_float) * 100
                            percentage_item.setText(f"{percentage_diff:.2f}%")
                        else:
                            percentage_item.setText("N/A")
                    else:
                        hr1_item.setBackground(Qt.green)
                        hr2_item.setBackground(Qt.green)
                        percentage_item.setText("N/A")
                except ValueError:
                    percentage_item.setText("N/A")

                self.table_widget.setItem(i, 0, QTableWidgetItem(metric))
                self.table_widget.setItem(i, 1, hr1_item)
                self.table_widget.setItem(i, 2, hr2_item)
                self.table_widget.setItem(i, 3, percentage_item)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to compare HR tests:\n{str(e)}")