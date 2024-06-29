# mod/ind_analyzer_window.py
import os
from datetime import datetime
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QGridLayout, QScrollArea, QPushButton, QVBoxLayout, QLabel, QSizePolicy, QMessageBox
from fpdf import FPDF
from fpdf import FPDF, HTMLMixin

from mod.ind.dialog_test1_analyzer import DialogTest1Block
from mod.ind.dialog_test2_analyzer import DialogTest2Block
from mod.ind.dialogs_comparison_analyzer import DialogsComparisonBlock
from mod.ind.openface_test1_analyzer import OpenFaceTest1Block
from mod.ind.openface_test2_analyzer import OpenFaceTest2Block
from mod.ind.openfaces_comparison_analyzer import OpenFacesComparisonBlock
from mod.ind.pre_ind_analyzer import PreTestBlock
from mod.ind.post_ind_analyzer import PostTestBlock
from mod.ind.system_choice_analyzer import SystemChoiceBlock
from mod.lesfonctions import create_standard_block, MyFPDF
from mod.ind.heartrate_test1 import HeartRateTest1Block
from mod.ind.heartrate_test2 import HeartRateTest2Block
from mod.ind.hrs_comparison_analyzer import HRsComparisonBlock
from mod.ind.tobii_test1 import TobiiTest1Block
from mod.ind.tobii_test2 import TobiiTest2Block
from mod.ind.tobiis_comparison_analyzer import TobiisComparisonBlock

class IndividualAnalyzerWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Individual Analyzer")
        self.setModal(True)
        self.setMinimumSize(1200, 1000)
        self.setWindowFlags(self.windowFlags() | Qt.WindowMaximizeButtonHint)

        self.grid_layout = QGridLayout()

        # Dictionary to store block instances
        self.blocks_instances = {}

        # Blocks for individual analysis
        blocks = [
            "Pre-Test", "Post-Test", "System Choice",
            "HR Test 1", "HR Test 2", "HRs Comparison",
            "Tobii Test 1", "Tobii Test 2", "Tobiis Comparison",
            "OpenFace Test 1", "OpenFace Test 2", "OpenFaces Comparison",
            "Dialog Test 1", "Dialog Test 2", "Dialogs Comparison"
        ]

        for i, block in enumerate(blocks):
            if block == "Pre-Test":
                block_widget = PreTestBlock()
            elif block == "Post-Test":
                block_widget = PostTestBlock()
            elif block == "System Choice":
                block_widget = SystemChoiceBlock()
            elif block == "HR Test 1":
                block_widget = HeartRateTest1Block()
            elif block == "HR Test 2":
                block_widget = HeartRateTest2Block()
            elif block == "HRs Comparison":
                block_widget = HRsComparisonBlock()
            elif block == "Tobii Test 1":
                block_widget = TobiiTest1Block()
            elif block == "Tobii Test 2":
                block_widget = TobiiTest2Block()
            elif block == "Tobiis Comparison":
                block_widget = TobiisComparisonBlock()
            elif block == "OpenFace Test 1":
                block_widget = OpenFaceTest1Block()
            elif block == "OpenFace Test 2":
                block_widget = OpenFaceTest2Block()
            elif block == "OpenFaces Comparison":
                block_widget = OpenFacesComparisonBlock()
            elif block == "Dialog Test 1":
                block_widget = DialogTest1Block()
            elif block == "Dialog Test 2":
                block_widget = DialogTest2Block()
            elif block == "Dialogs Comparison":
                block_widget = DialogsComparisonBlock()
            else:
                block_widget = create_standard_block(block)

            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setWidget(block_widget)
            self.grid_layout.addWidget(scroll_area, i // 3, i % 3)

            # Store block instances
            if block in ["Pre-Test", "Post-Test", "System Choice", "HR Test 1", "HR Test 2", "HRs Comparison", "Dialog Test 1", "Dialog Test 2", "Dialogs Comparison", "Tobii Test 1", "Tobii Test 2", "Tobiis Comparison", "OpenFace Test 1", "OpenFace Test 2", "OpenFaces Comparison"]:
                self.blocks_instances[block] = block_widget

        self.main_layout = QVBoxLayout()
        self.main_layout.addLayout(self.grid_layout)

        # Add the "Generate Individual Report" button
        self.generate_report_button = QPushButton("Generate Individual Report")
        self.generate_report_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.generate_report_button.clicked.connect(self.generate_individual_report)
        self.main_layout.addWidget(self.generate_report_button)

        # Create the footnote label
        footnote = QLabel("Aguida Multimodal Analyzer (Offline Data) by Aboul Hassane CISSE - Knowledge Information System Lab<br>version 2024.05")
        footnote.setAlignment(Qt.AlignCenter)
        footnote.setStyleSheet("color: gray; font-size: 12px; margin-top: 20px;")
        self.main_layout.addWidget(footnote)

        self.setLayout(self.main_layout)

    def generate_individual_report(self):
        try:
            # Get the participant ID from the SystemChoiceBlock
            participant_id = None
            for block_instance in self.blocks_instances.values():
                if isinstance(block_instance, SystemChoiceBlock):
                    combo_box = block_instance.combo_box
                    if combo_box.count() > 0:
                        participant_id = combo_box.currentText()
                        break

            if not participant_id:
                QMessageBox.warning(self, 'Input Error', 'You must select a participant ID.')
                return

            pdf = MyFPDF()
            pdf.add_page()

            # Set title
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt=f"Participant ID {participant_id} Report", ln=True, align='C')
            # pdf.cell(200, 10, txt="Aguida Multimodal Analyzer", ln=True, align='C')

            # Specify the order of blocks
            block_order = [
                "Pre-Test", "Post-Test", "System Choice",
                "HR Test 1", "HR Test 2", "HRs Comparison",
                "Dialog Test 1", "Dialog Test 2", "Dialogs Comparison",
                "Tobii Test 1", "Tobii Test 2", "Tobiis Comparison",
                "OpenFace Test 1", "OpenFace Test 2", "OpenFaces Comparison"
            ]

            # Collect and add data from each relevant block in the specified order
            for block_name in block_order:
                block_instance = self.blocks_instances.get(block_name)
                if block_instance:
                    pdf.chapter_title(f"{block_name} Data")
                    if isinstance(block_instance, PreTestBlock) or isinstance(block_instance,
                                                                              PostTestBlock) or isinstance(
                            block_instance, SystemChoiceBlock):
                        participant_label = block_instance.participant_label.text() if block_instance.participant_label else ""
                        try:
                            participant_label.encode('latin-1')
                            pdf.chapter_body(participant_label)
                        except UnicodeEncodeError:
                            participant_label = participant_label.encode('utf-8').decode('latin-1')
                            pdf.chapter_body(participant_label)
                    elif isinstance(block_instance, HeartRateTest1Block) or isinstance(block_instance,
                                                                                       HeartRateTest2Block) or isinstance(
                            block_instance, TobiiTest1Block) or isinstance(block_instance,
                                                                           TobiiTest2Block) or isinstance(
                            block_instance, OpenFaceTest1Block) or isinstance(block_instance,
                                                                              OpenFaceTest2Block) or isinstance(
                            block_instance, DialogTest1Block) or isinstance(block_instance, DialogTest2Block):
                        summary_text = block_instance.test_data if block_instance.test_data else ""
                        try:
                            summary_text.encode('latin-1')
                            pdf.chapter_body(summary_text)
                        except UnicodeEncodeError:
                            summary_text = summary_text.encode('utf-8').decode('latin-1')
                            pdf.chapter_body(summary_text)
                    elif isinstance(block_instance, HRsComparisonBlock) or isinstance(block_instance,
                                                                                      TobiisComparisonBlock) or isinstance(
                            block_instance, OpenFacesComparisonBlock) or isinstance(block_instance,
                                                                                    DialogsComparisonBlock):
                        # Collect table data
                        row_count = block_instance.table_widget.rowCount()
                        headers = ["Metric", "Test 1", "Test 2"]
                        table_data = []
                        for row in range(row_count):
                            table_row = []
                            for col in range(3):
                                item = block_instance.table_widget.item(row, col)
                                if item:
                                    cell_text = item.text()
                                    try:
                                        cell_text.encode('latin-1')
                                        table_row.append(cell_text)
                                    except UnicodeEncodeError:
                                        cell_text = cell_text.encode('utf-8').decode('latin-1')
                                        table_row.append(cell_text)
                            table_data.append(table_row)
                        pdf.add_comparison_table(headers, table_data)

            # Ensure the generated_reports directory exists
            pdf_dir = "generated_reports"
            os.makedirs(pdf_dir, exist_ok=True)

            # Create a unique filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            pdf_filename = os.path.join(pdf_dir, f"{participant_id}_report_individual_{timestamp}.pdf")
            pdf.output(pdf_filename)

            # Show success message
            QMessageBox.information(self, "Report Generated", f"PDF report generated successfully:\n{pdf_filename}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate PDF report:\n{str(e)}")