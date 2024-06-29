# mod/ind/dialogs_comparison_analyzer.py
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox
from PyQt5.QtCore import Qt

class DialogsComparisonBlock(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.compare_button = QPushButton("Compare Dialog Test 1 and Dialog Test 2")
        self.compare_button.clicked.connect(self.compare_dialog_tests)
        self.layout.addWidget(self.compare_button)

        self.table_widget = QTableWidget()
        self.layout.addWidget(self.table_widget)

    def compare_dialog_tests(self):
        try:
            parent_window = self.parent().parent().parent()  # Get the parent QDialog
            dialog_test1_block = parent_window.blocks_instances.get("Dialog Test 1")
            dialog_test2_block = parent_window.blocks_instances.get("Dialog Test 2")

            if dialog_test1_block is None or dialog_test2_block is None:
                raise ValueError("Both Dialog Test 1 and Dialog Test 2 blocks must be present")

            dialog_test1_category_data = dialog_test1_block.category_counts.to_dict()
            dialog_test2_category_data = dialog_test2_block.category_counts.to_dict()
            dialog_test1_utterance_data = dialog_test1_block.utterance_counts.to_dict()
            dialog_test2_utterance_data = dialog_test2_block.utterance_counts.to_dict()

            headers = ["Metric", "Dialog Test 1", "Dialog Test 2"]
            self.table_widget.setColumnCount(3)
            self.table_widget.setHorizontalHeaderLabels(headers)

            all_categories = set(dialog_test1_category_data.keys()).union(set(dialog_test2_category_data.keys()))
            all_utterances = set(dialog_test1_utterance_data.keys()).union(set(dialog_test2_utterance_data.keys()))

            total_rows = len(all_categories) + len(all_utterances)
            self.table_widget.setRowCount(total_rows)

            row = 0
            for category in all_categories:
                value1 = dialog_test1_category_data.get(category, 0)
                value2 = dialog_test2_category_data.get(category, 0)

                item1 = QTableWidgetItem(str(value1))
                item2 = QTableWidgetItem(str(value2))

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

                self.table_widget.setItem(row, 0, QTableWidgetItem(f"Category Count: {category}"))
                self.table_widget.setItem(row, 1, item1)
                self.table_widget.setItem(row, 2, item2)
                row += 1

            for utterance in all_utterances:
                value1 = dialog_test1_utterance_data.get(utterance, 0)
                value2 = dialog_test2_utterance_data.get(utterance, 0)

                item1 = QTableWidgetItem(str(value1))
                item2 = QTableWidgetItem(str(value2))

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

                self.table_widget.setItem(row, 0, QTableWidgetItem(f"Utterance Count: {utterance}"))
                self.table_widget.setItem(row, 1, item1)
                self.table_widget.setItem(row, 2, item2)
                row += 1

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to compare dialog tests:\n{str(e)}")
