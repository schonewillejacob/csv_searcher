import sys
import csv
from PyQt5 import QtWidgets, QtGui, QtCore
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import pandas as pd

# Worker thread for loading CSV files
class CSVLoaderThread(QtCore.QThread):
    data_loaded = QtCore.pyqtSignal(list, list)  # Signal to pass data and headers back
    error_occurred = QtCore.pyqtSignal(str)  # Signal to handle errors

    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path

    def run(self):
        try:
            df_iterator = pd.read_csv(self.file_path, chunksize=1000, encoding='utf-8', low_memory=False)
            df = next(df_iterator)  # Read the first chunk

            headers = df.columns.tolist()
            rows = df.values.tolist()
            self.data_loaded.emit(headers, rows)
        except Exception as e:
            self.error_occurred.emit(str(e))

class UnifiedSearchApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.headers = []
        self.data = []
        self.filtered_data = []
        self.search_fields = {}
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Unified CSV Search Application")
        self.setGeometry(200, 100, 1000, 600)
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.layout.addWidget(self.splitter)

        left_layout = QtWidgets.QWidget()
        left_layout.setLayout(QtWidgets.QVBoxLayout())
        self.splitter.addWidget(left_layout)

        top_layout = QtWidgets.QHBoxLayout()
        left_layout.layout().addLayout(top_layout)

        self.file_path_box = QtWidgets.QLineEdit(self)
        self.file_path_box.setPlaceholderText("Select a CSV file...")
        top_layout.addWidget(self.file_path_box)

        browse_btn = QtWidgets.QPushButton("Browse", self)
        browse_btn.clicked.connect(self.open_file_dialog)
        top_layout.addWidget(browse_btn)

        self.general_search_box = QtWidgets.QLineEdit(self)
        self.general_search_box.setPlaceholderText("Enter general search term...")
        top_layout.addWidget(self.general_search_box)

        general_search_btn = QtWidgets.QPushButton("Search All", self)
        general_search_btn.clicked.connect(self.perform_general_search)
        top_layout.addWidget(general_search_btn)

        self.column_search_layout = QtWidgets.QFormLayout()
        left_layout.layout().addLayout(self.column_search_layout)

        specific_search_button = QtWidgets.QPushButton("Search by Column", self)
        specific_search_button.clicked.connect(self.perform_column_search)
        left_layout.layout().addWidget(specific_search_button)

        export_button = QtWidgets.QPushButton("Export Filtered Data", self)
        export_button.clicked.connect(self.export_filtered_data)
        left_layout.layout().addWidget(export_button)

        self.table = QtWidgets.QTableWidget()
        self.layout.addWidget(self.table)

        chart_controls_layout = QtWidgets.QHBoxLayout()
        left_layout.layout().addLayout(chart_controls_layout)

        self.chart_label = QtWidgets.QLabel("Select Column for Graph Visualization:")
        chart_controls_layout.addWidget(self.chart_label)

        self.column_selector = QtWidgets.QComboBox()
        self.column_selector.currentTextChanged.connect(self.update_graph)
        chart_controls_layout.addWidget(self.column_selector)

        right_layout = QtWidgets.QWidget()
        right_layout.setLayout(QtWidgets.QVBoxLayout())
        self.splitter.addWidget(right_layout)

        self.chart_canvas = FigureCanvas(Figure(figsize=(6, 4)))
        right_layout.layout().addWidget(self.chart_canvas)
        self.ax = self.chart_canvas.figure.add_subplot(111)

        self.splitter.setSizes([300, 700])

    def open_file_dialog(self):
        options = QtWidgets.QFileDialog.Options()
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Open CSV File", "", "CSV Files (*.csv);;All Files (*)", options=options
        )
        if file_path:
            self.file_path_box.setText(file_path)
            self.load_csv_data(file_path)

    def load_csv_data(self, file_path):
        self.setEnabled(False)

        self.csv_loader_thread = CSVLoaderThread(file_path)
        self.csv_loader_thread.data_loaded.connect(self.on_csv_loaded)
        self.csv_loader_thread.error_occurred.connect(self.on_csv_load_error)
        self.csv_loader_thread.finished.connect(lambda: self.setEnabled(True))
        self.csv_loader_thread.start()

    def on_csv_loaded(self, headers, rows):
        self.headers = headers
        self.data = [headers] + rows
        self.filtered_data = rows

        self.update_search_fields()
        self.populate_column_selector()
        self.update_table(rows)
        print("CSV Data Loaded Successfully!")

    def on_csv_load_error(self, error_message):
        QtWidgets.QMessageBox.warning(self, "Error", f"Failed to load CSV file:\n{error_message}")
        print(f"Error loading CSV: {error_message}")

    def update_table(self, rows):
        max_rows_to_display = 500
        display_rows = rows[:max_rows_to_display]

        self.table.setRowCount(len(display_rows))
        self.table.setColumnCount(len(self.headers))
        self.table.setHorizontalHeaderLabels(self.headers)

        for row_num, row_data in enumerate(display_rows):
            for col_num, cell_data in enumerate(row_data):
                self.table.setItem(row_num, col_num, QtWidgets.QTableWidgetItem(str(cell_data)))

    def update_search_fields(self):
        for i in reversed(range(self.column_search_layout.count())):
            self.column_search_layout.itemAt(i).widget().deleteLater()

        self.search_fields = {}

        for col_idx, header in enumerate(self.headers):
            dropdown = QtWidgets.QComboBox(self)
            dropdown.setEditable(True)
            dropdown.addItem("All")
            
            # Ensure all unique values are converted to strings
            unique_values = sorted(set(str(row[col_idx]) for row in self.filtered_data if row[col_idx] is not None))
            
            dropdown.addItems(unique_values)
            self.column_search_layout.addRow(header + ":", dropdown)
            self.search_fields[header] = dropdown


    def perform_general_search(self):
        search_query = self.general_search_box.text().strip().lower()
        if not self.data or len(self.data) <= 1:
            QtWidgets.QMessageBox.warning(self, "Warning", "Please load a CSV file first.")
            return
        if not search_query:
            QtWidgets.QMessageBox.warning(self, "Warning", "Please enter a search term.")
            return

        results = [
            row for row in self.filtered_data
            if any(str(cell).strip().lower() == search_query for cell in row)
        ]

        self.filtered_data = results
        self.update_table(results)

    def perform_column_search(self):
        if not self.data or len(self.data) <= 1:
            QtWidgets.QMessageBox.warning(self, "Warning", "Please load a CSV file first.")
            return

        search_terms = {
            header: dropdown.currentText().strip().lower()
            for header, dropdown in self.search_fields.items()
            if dropdown.currentText() != "All"
        }

        results = []
        for row in self.filtered_data:
            match = True
            for header, term in search_terms.items():
                column_index = self.headers.index(header)
                cell_value = str(row[column_index]).strip().lower()

                if cell_value != term:
                    match = False
                    break
            if match:
                results.append(row)

        self.filtered_data = results
        self.update_table(results)

    def export_filtered_data(self):
        if not self.filtered_data:
            QtWidgets.QMessageBox.warning(self, "Warning", "No filtered data to export.")
            return

        options = QtWidgets.QFileDialog.Options()
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Save CSV File", "", "CSV Files (*.csv);;All Files (*)", options=options
        )

        if file_path:
            try:
                with open(file_path, mode="w", newline="", encoding="utf-8") as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(self.headers)
                    writer.writerows(self.filtered_data)
                QtWidgets.QMessageBox.information(self, "Success", "Filtered data exported successfully!")
            except Exception as e:
                QtWidgets.QMessageBox.warning(self, "Error", f"Failed to export CSV file:\n{e}")

    def populate_column_selector(self):
        if self.headers:
            self.column_selector.clear()
            # Filter headers for categorical columns
            categorical_columns = [
                header for header in self.headers
                if len(set(row[self.headers.index(header)] for row in self.filtered_data if row[self.headers.index(header)])) <= 20
            ]
            self.column_selector.addItems(categorical_columns)


    def update_graph(self):
        column = self.column_selector.currentText()
        
        if self.data and column:
            print(f"Updating graph for column: {column}")
            col_idx = self.headers.index(column)
            column_data = [row[col_idx] for row in self.filtered_data if row[col_idx]]

            # Identify if the column is categorical
            unique_values = set(column_data)
            max_unique_values = 20  # Define the threshold for categorical columns
            
            if len(unique_values) > max_unique_values:
                QtWidgets.QMessageBox.warning(
                    self, 
                    "Invalid Selection", 
                    f"The column '{column}' has too many unique values to be considered categorical."
                )
                self.ax.clear()
                self.ax.set_title("Select a valid categorical column for visualization")
                self.chart_canvas.draw()
                return

            try:
                # Generate bar chart for categorical columns
                value_counts = pd.Series(column_data).value_counts()
                self.ax.clear()
                value_counts.plot(kind='bar', ax=self.ax, color='skyblue', edgecolor='black')
                self.ax.set_title(f"Bar Chart of {column}")
                self.ax.set_xlabel(column)
                self.ax.set_ylabel("Count")
            except Exception as e:
                print(f"Error updating graph for column {column}: {e}")
                self.ax.clear()
                self.ax.set_title(f"Error visualizing column {column}")
            self.chart_canvas.draw()
        else:
            # No valid column selected or no data to visualize
            self.ax.clear()
            self.ax.set_title("No data to visualize")
            self.chart_canvas.draw()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = UnifiedSearchApp()
    window.setWindowIcon(QtGui.QIcon('assets/csv_icon.svg'))
    window.show()
    sys.exit(app.exec_())
