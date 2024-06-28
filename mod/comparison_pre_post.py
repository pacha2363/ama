# mod/comparison_pre_post.py
import os
import pandas as pd
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QFrame, QHBoxLayout, QPushButton, QMessageBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from datetime import datetime
from scipy.stats import ttest_rel, wilcoxon
from sklearn import svm
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from sklearn.impute import SimpleImputer
from matplotlib.backends.backend_pdf import PdfPages


class ComparisonPrePostTestFrame(QFrame):
    def __init__(self, pre_test_frame, post_test_frame, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.pre_test_frame = pre_test_frame
        self.post_test_frame = post_test_frame

        # Horizontal layout for buttons
        button_layout = QHBoxLayout()
        self.compare_button = QPushButton("Compare Pre-Test and Post-Test")
        self.compare_button.clicked.connect(self.compare_test_results)
        button_layout.addWidget(self.compare_button)

        self.export_button = QPushButton("Generate the report")
        self.export_button.setEnabled(False)  # Initially disabled
        self.export_button.clicked.connect(self.export_comparison_to_pdf)
        button_layout.addWidget(self.export_button)

        self.layout.addLayout(button_layout)

        self.results_layout = QHBoxLayout()
        self.layout.addLayout(self.results_layout)

        self.confidence_frame = QFrame()
        self.confidence_layout = QVBoxLayout()
        self.confidence_frame.setLayout(self.confidence_layout)
        self.results_layout.addWidget(self.confidence_frame)

        self.nervousness_frame = QFrame()
        self.nervousness_layout = QVBoxLayout()
        self.nervousness_frame.setLayout(self.nervousness_layout)
        self.results_layout.addWidget(self.nervousness_frame)

        self.wtc_frame = QFrame()
        self.wtc_layout = QVBoxLayout()
        self.wtc_frame.setLayout(self.wtc_layout)
        self.results_layout.addWidget(self.wtc_frame)

        self.svm_frame = QFrame()
        self.svm_layout = QVBoxLayout()
        self.svm_frame.setLayout(self.svm_layout)
        self.layout.addWidget(self.svm_frame)

        self.comparison_results = {}

    def compare_test_results(self):
        pre_test_data = self.pre_test_frame.get_test_data()
        post_test_data = self.post_test_frame.get_test_data()
        self.process_comparison(pre_test_data, post_test_data)
        self.export_button.setEnabled(True)  # Initially disabled

    def export_comparison_to_pdf(self):
        try:
            output_dir = "pdf_exports"
            os.makedirs(output_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            pdf_filename = os.path.join(output_dir, f"comparison_pre_post_test_results_{timestamp}.pdf")

            with PdfPages(pdf_filename) as pdf:
                # Add comparison scores to PDF
                for category, results in self.comparison_results.items():
                    if category == 'graph':
                        continue
                    if isinstance(results, dict):  # Ensure results is a dictionary
                        pre_score = results.get('pre_score', 'N/A')
                        post_score = results.get('post_score', 'N/A')
                        cohen_d = results.get('cohen_d', 'N/A')
                        wilcoxon_result = results.get('wilcoxon', 'N/A')
                        ttest_result = results.get('ttest', 'N/A')
                        text = (
                            f"{category} Comparison:\n"
                            f"Pre-Test: {pre_score:.2f}\n"
                            f"Post-Test: {post_score:.2f}\n"
                            f"Cohen's d: {cohen_d:.2f}\n"
                            f"Wilcoxon: W={wilcoxon_result.statistic:.2f}, p={wilcoxon_result.pvalue:.4f}\n"
                            f"Paired t-test: t={ttest_result.statistic:.2f}, p={ttest_result.pvalue:.4f}"
                        )
                        pdf.savefig(self.text_to_fig(text))

                # Add SVM results to PDF
                if 'svm_accuracy' in self.comparison_results and 'svm_report' in self.comparison_results:
                    svm_accuracy = self.comparison_results['svm_accuracy']
                    svm_report = self.comparison_results['svm_report']
                    svm_text = (
                        f"SVM Accuracy: {svm_accuracy:.2f}\n"
                        f"SVM Classification Report:\n{svm_report}"
                    )
                    pdf.savefig(self.text_to_fig(svm_text))

                # Add comparison graph to PDF
                if 'graph' in self.comparison_results:
                    graph_filename = self.comparison_results['graph']
                    fig, ax = plt.subplots(figsize=(5, 3))
                    img = plt.imread(graph_filename)
                    ax.imshow(img)
                    ax.axis('off')
                    pdf.savefig(fig)
                    plt.close(fig)

            # Show a success message
            QMessageBox.information(self, "Report Generated", f"PDF report generated successfully:\n{pdf_filename}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate PDF report:\n{str(e)}")

    def process_comparison(self, pre_test_data, post_test_data):
        # Extract relevant columns for confidence, nervousness, and WtC
        pre_confidence_columns = [col for col in pre_test_data.columns if '自信' in col]
        pre_nervousness_columns = [col for col in pre_test_data.columns if '緊張' in col]
        pre_wtc_columns = [col for col in pre_test_data.columns if 'やる気' in col]

        post_confidence_columns = [col for col in post_test_data.columns if '自信' in col]
        post_nervousness_columns = [col for col in post_test_data.columns if '緊張' in col]
        post_wtc_columns = [col for col in post_test_data.columns if 'やる気' in col]

        # Extracting relevant columns
        pre_confidence_data = pre_test_data[pre_confidence_columns]
        pre_nervousness_data = pre_test_data[pre_nervousness_columns]
        pre_wtc_data = pre_test_data[pre_wtc_columns]

        post_confidence_data = post_test_data[post_confidence_columns]
        post_nervousness_data = post_test_data[post_nervousness_columns]
        post_wtc_data = post_test_data[post_wtc_columns]

        # Apply the updated mapping function to convert pre-test and post-test WtC ratings to scores
        pre_confidence_scores = pre_confidence_data.applymap(
            lambda x: self.revised_map_ratings_to_scores(x, 'confidence'))
        pre_nervousness_scores = pre_nervousness_data.applymap(
            lambda x: self.revised_map_ratings_to_scores(x, 'nervousness'))
        pre_wtc_scores = pre_wtc_data.applymap(lambda x: self.revised_map_ratings_to_scores(x, 'wtc'))

        post_confidence_scores = post_confidence_data.applymap(
            lambda x: self.revised_map_ratings_to_scores(x, 'confidence'))
        post_nervousness_scores = post_nervousness_data.applymap(
            lambda x: self.revised_map_ratings_to_scores(x, 'nervousness'))
        post_wtc_scores = post_wtc_data.applymap(lambda x: self.revised_map_ratings_to_scores(x, 'wtc'))

        # Calculate average scores for each category in the pre-test and post-test
        average_pre_confidence_score = pre_confidence_scores.mean(axis=1).mean()
        average_pre_nervousness_score = pre_nervousness_scores.mean(axis=1).mean()
        average_pre_wtc_score = pre_wtc_scores.mean(axis=1).mean()

        average_post_confidence_score = post_confidence_scores.mean(axis=1).mean()
        average_post_nervousness_score = post_nervousness_scores.mean(axis=1).mean()
        average_post_wtc_score = post_wtc_scores.mean(axis=1).mean()

        # Calculate Cohen's d for each category
        cohen_d_confidence = self.calculate_cohens_d(pre_confidence_scores.mean(axis=1),
                                                     post_confidence_scores.mean(axis=1))
        cohen_d_nervousness = self.calculate_cohens_d(pre_nervousness_scores.mean(axis=1),
                                                      post_nervousness_scores.mean(axis=1))
        cohen_d_wtc = self.calculate_cohens_d(pre_wtc_scores.mean(axis=1), post_wtc_scores.mean(axis=1))

        # Perform Wilcoxon Signed-Rank Test for each category
        wilcoxon_confidence = wilcoxon(pre_confidence_scores.mean(axis=1), post_confidence_scores.mean(axis=1))
        wilcoxon_nervousness = wilcoxon(pre_nervousness_scores.mean(axis=1), post_nervousness_scores.mean(axis=1))
        wilcoxon_wtc = wilcoxon(pre_wtc_scores.mean(axis=1), post_wtc_scores.mean(axis=1))

        # Perform Paired t-test for each category
        ttest_confidence = ttest_rel(pre_confidence_scores.mean(axis=1), post_confidence_scores.mean(axis=1))
        ttest_nervousness = ttest_rel(pre_nervousness_scores.mean(axis=1), post_nervousness_scores.mean(axis=1))
        ttest_wtc = ttest_rel(pre_wtc_scores.mean(axis=1), post_wtc_scores.mean(axis=1))

        # Store results for exporting
        self.comparison_results['Confidence'] = {
            'pre_score': average_pre_confidence_score,
            'post_score': average_post_confidence_score,
            'cohen_d': cohen_d_confidence,
            'wilcoxon': wilcoxon_confidence,
            'ttest': ttest_confidence
        }
        self.comparison_results['Nervousness'] = {
            'pre_score': average_pre_nervousness_score,
            'post_score': average_post_nervousness_score,
            'cohen_d': cohen_d_nervousness,
            'wilcoxon': wilcoxon_nervousness,
            'ttest': ttest_nervousness
        }
        self.comparison_results['WtC'] = {
            'pre_score': average_pre_wtc_score,
            'post_score': average_post_wtc_score,
            'cohen_d': cohen_d_wtc,
            'wilcoxon': wilcoxon_wtc,
            'ttest': ttest_wtc
        }

        # Display the comparison scores
        self.display_comparison_scores(self.confidence_layout, average_pre_confidence_score,
                                       average_post_confidence_score, cohen_d_confidence, wilcoxon_confidence,
                                       ttest_confidence, 'Confidence')
        self.display_comparison_scores(self.nervousness_layout, average_pre_nervousness_score,
                                       average_post_nervousness_score, cohen_d_nervousness, wilcoxon_nervousness,
                                       ttest_nervousness, 'Nervousness')
        self.display_comparison_scores(self.wtc_layout, average_pre_wtc_score, average_post_wtc_score, cohen_d_wtc,
                                       wilcoxon_wtc, ttest_wtc, 'WtC')

        # Display the comparison graph
        self.display_comparison_graph(average_pre_confidence_score, average_post_confidence_score,
                                      average_pre_nervousness_score, average_post_nervousness_score,
                                      average_pre_wtc_score, average_post_wtc_score)

        # Perform SVM classification and display results
        self.perform_svm_classification(pre_confidence_scores, pre_nervousness_scores, pre_wtc_scores,
                                        post_confidence_scores, post_nervousness_scores, post_wtc_scores)

    def revised_map_ratings_to_scores(self, rating, category):
        if isinstance(rating, str):
            rating = rating.strip()
            if category == 'confidence':
                if '絶対できない' in rating:
                    return 0
                elif 'あまりできない' in rating:
                    return 1
                elif '場合によりけり' in rating:
                    return 2
                elif '多分できる' in rating:
                    return 3
                elif '機会があればやってみたい' in rating:
                    return 4
                elif '簡単にできる' in rating:
                    return 5
            elif category == 'nervousness':
                if 'すごく緊張する' in rating:
                    return 0
                elif 'できれば避けたい' in rating:
                    return 1
                elif 'かなり緊張する' in rating:
                    return 2
                elif 'すこしは緊張する' in rating:
                    return 3
                elif '緊張しない' in rating:
                    return 4
            elif category == 'wtc':
                if 'できれば避けたい' in rating:
                    return 0
                elif '機会があればやってみたい' in rating:
                    return 1
                elif '多分できる' in rating:
                    return 2
                elif '簡単にできる' in rating:
                    return 3
        return None

    def calculate_cohens_d(self, pre_scores, post_scores):
        diff = post_scores - pre_scores
        cohen_d = diff.mean() / diff.std(ddof=1)
        return cohen_d

    def display_comparison_scores(self, layout, pre_score, post_score, cohen_d, wilcoxon_result, ttest_result,
                                  category):
        scores_text = (
            f"{category} Comparison:\n"
            f"Pre-Test: {pre_score:.2f}\n"
            f"Post-Test: {post_score:.2f}\n"
            f"Cohen's d: {cohen_d:.2f}\n"
            f"Wilcoxon: W={wilcoxon_result.statistic:.2f}, p={wilcoxon_result.pvalue:.4f}\n"
            f"Paired t-test: t={ttest_result.statistic:.2f}, p={ttest_result.pvalue:.4f}"
        )
        scores_label = QLabel(scores_text)
        layout.addWidget(scores_label)

    def display_comparison_graph(self, pre_confidence, post_confidence, pre_nervousness, post_nervousness, pre_wtc,
                                 post_wtc):
        categories = ['Confidence', 'Nervousness', 'WtC']
        pre_scores = [pre_confidence, pre_nervousness, pre_wtc]
        post_scores = [post_confidence, post_nervousness, post_wtc]

        x = range(len(categories))

        plt.figure(figsize=(5, 3))
        plt.bar(x, pre_scores, width=0.4, label='Pre-Test', align='center')
        plt.bar(x, post_scores, width=0.4, label='Post-Test', align='edge')
        plt.xticks(x, categories)
        plt.xlabel('Categories')
        plt.ylabel('Scores')
        plt.title('Comparison of Pre-Test and Post-Test Scores')
        plt.legend()

        # Ensure the Output directory exists
        output_dir = "Output"
        os.makedirs(output_dir, exist_ok=True)

        # Create a unique filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = os.path.join(output_dir, f"comparison_scores_{timestamp}.png")
        plt.savefig(filename)
        plt.close()

        # Display the graph in the frame
        pixmap = QPixmap(filename)
        graph_label = QLabel()
        graph_label.setPixmap(pixmap)
        graph_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(graph_label)

        # Save the graph filename for PDF export
        self.comparison_results['graph'] = filename

    def perform_svm_classification(self, pre_confidence_scores, pre_nervousness_scores, pre_wtc_scores,
                                   post_confidence_scores, post_nervousness_scores, post_wtc_scores):
        # Combine pre-test and post-test data with labels
        pre_scores = pd.concat(
            [pre_confidence_scores.mean(axis=1), pre_nervousness_scores.mean(axis=1), pre_wtc_scores.mean(axis=1)],
            axis=1)
        pre_scores['label'] = 'pre'

        post_scores = pd.concat(
            [post_confidence_scores.mean(axis=1), post_nervousness_scores.mean(axis=1), post_wtc_scores.mean(axis=1)],
            axis=1)
        post_scores['label'] = 'post'

        combined_data = pd.concat([pre_scores, post_scores], axis=0)
        combined_data.columns = ['confidence', 'nervousness', 'wtc', 'label']

        # Handle missing values
        imputer = SimpleImputer(strategy='mean')
        X = imputer.fit_transform(combined_data[['confidence', 'nervousness', 'wtc']])
        y = combined_data['label']

        # Split the data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

        # Train the SVM model
        model = svm.SVC(kernel='linear')
        model.fit(X_train, y_train)

        # Predict and evaluate
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        report = classification_report(y_test, y_pred)

        # Display SVM results
        self.display_svm_results(accuracy, report)

    def display_svm_results(self, accuracy, report):
        accuracy_label = QLabel(f"SVM Accuracy: {accuracy:.2f}")
        report_label = QLabel(f"SVM Classification Report:\n{report}")
        self.svm_layout.addWidget(accuracy_label)
        self.svm_layout.addWidget(report_label)

        # Store SVM results for PDF export
        self.comparison_results['svm_accuracy'] = accuracy
        self.comparison_results['svm_report'] = report

    def text_to_fig(self, text):
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.text(0.5, 0.5, text, transform=ax.transAxes, ha='center', va='center', wrap=True)
        ax.axis('off')
        return fig
