# mod/ind/tobiis_comparison_analyzer.py
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox
from PyQt5.QtCore import Qt

class TobiisComparisonBlock(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.compare_button = QPushButton("Compare Tobii Test 1 and Tobii Test 2")
        self.compare_button.clicked.connect(self.compare_tobii_tests)
        self.layout.addWidget(self.compare_button)

        self.table_widget = QTableWidget()
        self.layout.addWidget(self.table_widget)

    def compare_tobii_tests(self):
        try:
            parent_window = self.parent().parent().parent()  # Get the parent QDialog
            tobii_test1_block = parent_window.blocks_instances.get("Tobii Test 1")
            tobii_test2_block = parent_window.blocks_instances.get("Tobii Test 2")

            if tobii_test1_block is None or tobii_test2_block is None:
                raise ValueError("Both Tobii Test 1 and Tobii Test 2 blocks must be present")

            tobii_test1_data = tobii_test1_block.test_data.split("\n")
            tobii_test2_data = tobii_test2_block.test_data.split("\n")

            headers = ["Metric", "Tobii Test 1", "Tobii Test 2", "Percentage Difference"]
            self.table_widget.setColumnCount(4)
            self.table_widget.setHorizontalHeaderLabels(headers)
            self.table_widget.setRowCount(len(tobii_test1_data))

            for i, (tobii1, tobii2) in enumerate(zip(tobii_test1_data, tobii_test2_data)):
                metric = tobii1.split(":")[0]
                tobii1_value = tobii1.split(":")[1].strip()
                tobii2_value = tobii2.split(":")[1].strip()

                tobii1_item = QTableWidgetItem(tobii1_value)
                tobii2_item = QTableWidgetItem(tobii2_value)
                percentage_item = QTableWidgetItem()

                # Convert values to float for comparison
                try:
                    tobii1_float = float(tobii1_value)
                    tobii2_float = float(tobii2_value)

                    if tobii1_float < tobii2_float:
                        tobii1_item.setBackground(Qt.red)
                        tobii2_item.setBackground(Qt.blue)
                        if tobii1_float != 0:
                            percentage_diff = ((tobii2_float - tobii1_float) / tobii1_float) * 100
                            percentage_item.setText(f"{percentage_diff:.2f}%")
                        else:
                            percentage_item.setText("N/A")
                    elif tobii1_float > tobii2_float:
                        tobii1_item.setBackground(Qt.blue)
                        tobii2_item.setBackground(Qt.red)
                        if tobii2_float != 0:
                            percentage_diff = ((tobii1_float - tobii2_float) / tobii2_float) * 100
                            percentage_item.setText(f"{percentage_diff:.2f}%")
                        else:
                            percentage_item.setText("N/A")
                    else:
                        tobii1_item.setBackground(Qt.green)
                        tobii2_item.setBackground(Qt.green)
                        percentage_item.setText("N/A")
                except ValueError:
                    percentage_item.setText("N/A")

                self.table_widget.setItem(i, 0, QTableWidgetItem(metric))
                self.table_widget.setItem(i, 1, tobii1_item)
                self.table_widget.setItem(i, 2, tobii2_item)
                self.table_widget.setItem(i, 3, percentage_item)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to compare Tobii tests:\n{str(e)}")