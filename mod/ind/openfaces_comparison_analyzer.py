# mod/ind/openfaces_comparison_analyzer.py
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox
from PyQt5.QtCore import Qt
import pandas as pd
from scipy.stats import skew, kurtosis, mode, hmean, gmean

class OpenFacesComparisonBlock(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.compare_button = QPushButton("Compare OpenFace Test 1 and OpenFace Test 2")
        self.compare_button.clicked.connect(self.compare_openface_tests)
        self.layout.addWidget(self.compare_button)

        self.table_widget = QTableWidget()
        self.layout.addWidget(self.table_widget)

    def compare_openface_tests(self):
        try:
            parent_window = self.parent().parent().parent()  # Get the parent QDialog
            openface_test1_block = parent_window.blocks_instances.get("OpenFace Test 1")
            openface_test2_block = parent_window.blocks_instances.get("OpenFace Test 2")

            if openface_test1_block is None or openface_test2_block is None:
                raise ValueError("Both OpenFace Test 1 and OpenFace Test 2 blocks must be present")

            openface_test1_data = openface_test1_block.test_data.split("\n")
            openface_test2_data = openface_test2_block.test_data.split("\n")

            headers = ["Metric", "OpenFace Test 1", "OpenFace Test 2"]
            self.table_widget.setColumnCount(3)
            self.table_widget.setHorizontalHeaderLabels(headers)
            self.table_widget.setRowCount(len(openface_test1_data))

            for i, (data1, data2) in enumerate(zip(openface_test1_data, openface_test2_data)):
                metric = data1.split(":")[0]
                value1 = data1.split(":")[1].strip()
                value2 = data2.split(":")[1].strip()

                item1 = QTableWidgetItem(value1)
                item2 = QTableWidgetItem(value2)

                # Convert values to float for comparison
                try:
                    float1 = float(value1)
                    float2 = float(value2)

                    if float1 < float2:
                        item1.setBackground(Qt.red)
                        item2.setBackground(Qt.blue)
                    elif float1 > float2:
                        item1.setBackground(Qt.blue)
                        item2.setBackground(Qt.red)
                    else:
                        item1.setBackground(Qt.green)
                        item2.setBackground(Qt.green)
                except ValueError:
                    pass

                self.table_widget.setItem(i, 0, QTableWidgetItem(metric))
                self.table_widget.setItem(i, 1, item1)
                self.table_widget.setItem(i, 2, item2)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to compare OpenFace tests:\n{str(e)}")
