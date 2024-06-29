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

        # Collect and add data from each relevant block
        for block_name, block_instance in self.blocks_instances.items():
            pdf.chapter_title(f"{block_name} Data")
            if isinstance(block_instance, PreTestBlock) or isinstance(block_instance, PostTestBlock) or isinstance(
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
                block_instance, TobiiTest1Block) or isinstance(block_instance, TobiiTest2Block) or isinstance(
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
                block_instance, OpenFacesComparisonBlock) or isinstance(block_instance, DialogsComparisonBlock):
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

        # Collect and add data from each relevant block
        for block_name, block_instance in self.blocks_instances.items():
            pdf.chapter_title(f"{block_name} Data")
            if isinstance(block_instance, PreTestBlock) or isinstance(block_instance, PostTestBlock) or isinstance(
                    block_instance, SystemChoiceBlock):
                participant_label = block_instance.participant_label.text()
                try:
                    participant_label.encode('latin-1')
                    pdf.chapter_body(participant_label)
                except UnicodeEncodeError:
                    participant_label = participant_label.encode('utf-8').decode('latin-1')
                    pdf.chapter_body(participant_label)
            elif isinstance(block_instance, HeartRateTest1Block) or isinstance(block_instance,
                                                                               HeartRateTest2Block) or isinstance(
                    block_instance, TobiiTest1Block) or isinstance(block_instance, TobiiTest2Block) or isinstance(
                    block_instance, OpenFaceTest1Block) or isinstance(block_instance, OpenFaceTest2Block) or isinstance(
                    block_instance, DialogTest1Block) or isinstance(block_instance, DialogTest2Block):
                summary_text = block_instance.test_data
                try:
                    summary_text.encode('latin-1')
                    pdf.chapter_body(summary_text)
                except UnicodeEncodeError:
                    summary_text = summary_text.encode('utf-8').decode('latin-1')
                    pdf.chapter_body(summary_text)
            elif isinstance(block_instance, HRsComparisonBlock) or isinstance(block_instance,
                                                                              TobiisComparisonBlock) or isinstance(
                    block_instance, OpenFacesComparisonBlock) or isinstance(block_instance, DialogsComparisonBlock):
                # Collect table data
                row_count = block_instance.table_widget.rowCount()
                headers = ["Metric", "HR Test 1", "HR Test 2", "Percentage Difference"]
                table_data = []
                for row in range(row_count):
                    table_row = []
                    for col in range(4):
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

        # Collect and add data from each relevant block
        for block_name, block_instance in self.blocks_instances.items():
            pdf.chapter_title(f"{block_name} Data")
            if isinstance(block_instance, PreTestBlock) or isinstance(block_instance, PostTestBlock) or isinstance(
                    block_instance, SystemChoiceBlock):
                participant_label = block_instance.participant_label.text()
                try:
                    participant_label.encode('latin-1')
                    pdf.chapter_body(participant_label)
                except UnicodeEncodeError:
                    participant_label = participant_label.encode('utf-8').decode('latin-1')
                    pdf.chapter_body(participant_label)
            elif isinstance(block_instance, HeartRateTest1Block) or isinstance(block_instance, HeartRateTest2Block):
                summary_text = block_instance.test_data
                try:
                    summary_text.encode('latin-1')
                    pdf.chapter_body(summary_text)
                except UnicodeEncodeError:
                    summary_text = summary_text.encode('utf-8').decode('latin-1')
                    pdf.chapter_body(summary_text)
            elif isinstance(block_instance, HRsComparisonBlock):
                # Collect table data
                row_count = block_instance.table_widget.rowCount()
                headers = ["Metric", "HR Test 1", "HR Test 2", "Percentage Difference"]
                table_data = []
                for row in range(row_count):
                    table_row = []
                    for col in range(4):
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

        pdf = FPDF()
        pdf.add_page()

        # Set title
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt=f"{participant_id} Report", ln=True, align='C')
        pdf.cell(200, 10, txt="Aguida Multimodal Analyzer", ln=True, align='C')

        # Collect and add data from each relevant block
        for block_name, block_instance in self.blocks_instances.items():
            pdf.set_font("Arial", size=10)
            pdf.cell(0, 10, txt=f"{block_name} Data:", ln=True)
            if isinstance(block_instance, PreTestBlock) or isinstance(block_instance, PostTestBlock) or isinstance(
                    block_instance, SystemChoiceBlock) or isinstance(block_instance, HeartRateTest1Block) or isinstance(
                    block_instance, HeartRateTest2Block) or isinstance(block_instance, HRsComparisonBlock):
                participant_label = block_instance.participant_label.text()
                try:
                    participant_label.encode('latin-1')
                    pdf.multi_cell(0, 10, participant_label)
                except UnicodeEncodeError:
                    participant_label = participant_label.encode('utf-8').decode('latin-1')
                    pdf.multi_cell(0, 10, participant_label)
            elif isinstance(block_instance, HeartRateTest1Block):
                summary_text = block_instance.test_data
                try:
                    summary_text.encode('latin-1')
                    pdf.multi_cell(0, 10, summary_text)
                except UnicodeEncodeError:
                    summary_text = summary_text.encode('utf-8').decode('latin-1')
                    pdf.multi_cell(0, 10, summary_text)

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
            pdf.cell(200, 10, txt=f"{participant_id} Report", ln=True, align='C')
            pdf.cell(200, 10, txt="Aguida Multimodal Analyzer", ln=True, align='C')

            # Collect and add data from each relevant block
            for block_name, block_instance in self.blocks_instances.items():
                pdf.chapter_title(f"{block_name} Data")
                if isinstance(block_instance, PreTestBlock) or isinstance(block_instance, PostTestBlock) or isinstance(block_instance, SystemChoiceBlock):
                    participant_label = block_instance.participant_label.text()
                    try:
                        participant_label.encode('latin-1')
                        pdf.chapter_body(participant_label)
                    except UnicodeEncodeError:
                        participant_label = participant_label.encode('utf-8').decode('latin-1')
                        pdf.chapter_body(participant_label)
                elif isinstance(block_instance, HeartRateTest1Block) or isinstance(block_instance, HeartRateTest2Block):
                    summary_text = block_instance.test_data
                    try:
                        summary_text.encode('latin-1')
                        pdf.chapter_body(summary_text)
                    except UnicodeEncodeError:
                        summary_text = summary_text.encode('utf-8').decode('latin-1')
                        pdf.chapter_body(summary_text)
                elif isinstance(block_instance, HRsComparisonBlock) or isinstance(block_instance, TobiisComparisonBlock):
                    # Add table header
                    headers = ["Metric", "Test 1", "Test 2", "Percentage Difference"]
                    data = []
                    row_count = block_instance.table_widget.rowCount()
                    for row in range(row_count):
                        row_data = []
                        for col in range(4):
                            item = block_instance.table_widget.item(row, col)
                            if item:
                                cell_text = item.text()
                                try:
                                    cell_text.encode('latin-1')
                                except UnicodeEncodeError:
                                    cell_text = cell_text.encode('utf-8').decode('latin-1')
                                row_data.append(cell_text)
                        data.append(row_data)
                    pdf.add_comparison_table(headers, data)

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