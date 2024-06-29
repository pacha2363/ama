# mod/lesfonctions.py
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget
from fpdf import FPDF, HTMLMixin

def create_standard_block(block):
    block_label = QLabel(block)
    block_label.setAlignment(Qt.AlignCenter)
    block_label.setStyleSheet("font-weight: bold; margin-bottom: 10px;")

    block_content = QLabel(f"Content for {block} goes here. Add your text, images, or any other widgets.")
    block_content.setWordWrap(True)

    block_layout = QVBoxLayout()
    block_layout.addWidget(block_label)
    block_layout.addWidget(block_content)

    block_widget = QWidget()
    block_widget.setLayout(block_layout)

    return block_widget

class MyFPDF(FPDF, HTMLMixin):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'Aguida Multimodal Analyzer', 0, 1, 'C')

    def chapter_title(self, title):
        # Arial 22, underline
        self.set_font('Arial', 'U', 18)
        # Title centered
        self.cell(0, 10, title, 0, 1, 'C')
        self.ln(10)

    def chapter_body(self, body):
        # Read text file
        self.set_font('Arial', '', 10)
        self.multi_cell(0, 10, body)
        self.ln()

    def add_comparison_table(self, headers, data):
        self.set_font('Arial', 'B', 10)
        for header in headers:
            self.cell(45, 10, header, 1, 0, 'C')
        self.ln()
        self.set_font('Arial', '', 10)
        for row in data:
            for item in row:
                self.cell(45, 10, item, 1, 0, 'C')
            self.ln()

    def footer(self):
        # Go to 1.5 cm from bottom
        self.set_y(-15)
        # Select Arial italic 8
        self.set_font('Arial', 'I', 12)
        # Print centered page number
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')
