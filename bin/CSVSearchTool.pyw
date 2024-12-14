import sys
import pandas as pd
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QAbstractTableModel, Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# Custom Table Model for Pandas DataFrame
class PandasModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parent=None):
        return self._data.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return str(self._data.iloc[index.row(), index.column()])
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self._data.columns[section]
            if orientation == Qt.Vertical:
                return str(self._data.index[section])
        return None
    
    def sort(self, column, order):
        """Sort the data based on the column and order."""
        ascending = order == Qt.AscendingOrder
        self._data = self._data.sort_values(
            by=self._data.columns[column], ascending=ascending
        )
        self.layoutChanged.emit()

class CSVLoaderThread(QtCore.QThread):
    data_loaded = QtCore.pyqtSignal(list, list)  # Signal to emit headers and rows
    error_occurred = QtCore.pyqtSignal(str)  # Signal for errors

    def __init__(self, file_path, encoding="utf-8"):
        super().__init__()
        self.file_path = file_path
        self.encoding = encoding

    def run(self):
        try:
            df = pd.read_csv(self.file_path, encoding=self.encoding, low_memory=False)
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
        self.setGeometry(200, 100, 1200, 800)

        self.main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.main_layout)

        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        self.main_layout.addWidget(self.splitter)

        # Top section for controls and chart
        top_section = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.splitter.addWidget(top_section)

        # Left panel for column-specific filters
        left_panel = QtWidgets.QWidget()
        left_layout = QtWidgets.QVBoxLayout()
        left_panel.setLayout(left_layout)
        top_section.addWidget(left_panel)

        # File selection and search controls
        top_layout = QtWidgets.QHBoxLayout()
        left_layout.addLayout(top_layout)

        self.file_path_box = QtWidgets.QLineEdit()
        self.file_path_box.setPlaceholderText("Select a CSV file...")
        top_layout.addWidget(self.file_path_box)

        browse_btn = QtWidgets.QPushButton("Browse")
        browse_btn.clicked.connect(self.open_file_dialog)
        top_layout.addWidget(browse_btn)

        self.general_search_box = QtWidgets.QLineEdit()
        self.general_search_box.setPlaceholderText("Enter general search term...")
        top_layout.addWidget(self.general_search_box)

        general_search_btn = QtWidgets.QPushButton("Search All")
        general_search_btn.clicked.connect(self.perform_general_search)
        top_layout.addWidget(general_search_btn)

        reset_btn = QtWidgets.QPushButton("Reset Filters")
        reset_btn.clicked.connect(self.reset_filters)
        top_layout.addWidget(reset_btn)

        # Column-specific filters
        self.column_search_scroll_area = QtWidgets.QScrollArea()
        self.column_search_container_widget = QtWidgets.QWidget()
        self.column_search_form_layout = QtWidgets.QFormLayout()
        self.column_search_container_widget.setLayout(self.column_search_form_layout)
        self.column_search_scroll_area.setWidget(self.column_search_container_widget)
        self.column_search_scroll_area.setWidgetResizable(True)
        left_layout.addWidget(self.column_search_scroll_area)

        specific_search_btn = QtWidgets.QPushButton("Search by Column")
        specific_search_btn.clicked.connect(self.perform_column_search)
        left_layout.addWidget(specific_search_btn)

        # Right panel for chart
        chart_panel = QtWidgets.QWidget()
        chart_layout = QtWidgets.QVBoxLayout()
        chart_panel.setLayout(chart_layout)
        top_section.addWidget(chart_panel)

        chart_title = QtWidgets.QLabel("Chart View")
        chart_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        chart_layout.addWidget(chart_title)

        chart_controls_layout = QtWidgets.QHBoxLayout()
        chart_layout.addLayout(chart_controls_layout)

        self.chart_label = QtWidgets.QLabel("Select Column for Graph Visualization:")
        chart_controls_layout.addWidget(self.chart_label)

        self.column_selector = QtWidgets.QComboBox()
        self.column_selector.currentTextChanged.connect(self.update_graph)
        chart_controls_layout.addWidget(self.column_selector)

        # Chart canvas
        self.chart_canvas = FigureCanvas(Figure(figsize=(8, 6)))
        chart_layout.addWidget(self.chart_canvas)
        self.ax = self.chart_canvas.figure.add_subplot(111)

        # Bottom section for table
        table_section = QtWidgets.QWidget()
        table_layout = QtWidgets.QVBoxLayout()
        table_section.setLayout(table_layout)
        self.splitter.addWidget(table_section)

        table_title = QtWidgets.QLabel("Table View")
        table_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        table_layout.addWidget(table_title)

        self.table = QtWidgets.QTableView()
        self.table.setSortingEnabled(True)
        table_layout.addWidget(self.table)

        # Resize splitter
        self.splitter.setSizes([500, 300])

        # Loading label
        self.loading_label = QtWidgets.QLabel(" ")
        self.loading_label.setStyleSheet("color: blue;")
        self.main_layout.addWidget(self.loading_label)

    def open_file_dialog(self):
        options = QtWidgets.QFileDialog.Options()
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Open CSV File", "", "CSV Files (*.csv);;All Files (*)", options=options
        )
        if file_path:
            self.file_path_box.setText(file_path)
            self.loading_label.setText("Loading \"" + str(file_path) + "\", please be patient...")
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
        self.loading_label.setText("CSV loaded successfully.")

    def on_csv_load_error(self, error_message):
        QtWidgets.QMessageBox.warning(self, "Error", f"Failed to load CSV file:\n{error_message}")
        self.loading_label.setText("Failed to load CSV.")

    def update_table(self, rows):
        df = pd.DataFrame(rows, columns=self.headers)
        model = PandasModel(df)
        self.table.setModel(model)

    def update_search_fields(self):
        for i in reversed(range(self.column_search_form_layout.count())):
            self.column_search_form_layout.itemAt(i).widget().deleteLater()

        self.search_fields = {}

        for col_idx, header in enumerate(self.headers):
            dropdown = QtWidgets.QComboBox(self)
            dropdown.setEditable(True)
            dropdown.addItem("All")
            
            # Ensure all unique values are converted to strings
            unique_values = sorted(set(str(row[col_idx]) for row in self.filtered_data if row[col_idx] is not None))

            dropdown.addItems(unique_values)
            self.column_search_form_layout.addRow(header + ":", dropdown)
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
            if any(search_query in str(cell).strip().lower() for cell in row)
        ]

        self.filtered_data = results
        self.update_table(results)
        self.update_graph()

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
        self.update_graph()

    def reset_filters(self):
        if not self.data or len(self.data) <= 1:
            QtWidgets.QMessageBox.warning(self, "Warning", "Please load a CSV file first.")
            return

        self.filtered_data = self.data[1:]  # Exclude headers
        self.general_search_box.clear()
        for header, dropdown in self.search_fields.items():
            dropdown.setCurrentIndex(0)  # Reset to "All"

        self.update_table(self.filtered_data)
        self.update_graph()

    def populate_column_selector(self):
        if self.headers:
            self.column_selector.clear()
            # Only include categorical columns for graphing (<= 20 unique values)
            for header in self.headers:
                unique_values = set(row[self.headers.index(header)] for row in self.filtered_data if row[self.headers.index(header)] is not None)
                if len(unique_values) <= 20:
                    self.column_selector.addItem(header)

    def update_graph(self):
        column = self.column_selector.currentText()

        if self.data and column:
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

                # Make the x-axis labels smaller and rotated for readability
                self.ax.tick_params(axis='x', labelsize=8)  # Adjust font size
                self.ax.set_xticklabels(self.ax.get_xticklabels(), rotation=45, ha='right')  # Rotate labels
            except Exception as e:
                print(f"Error updating graph for column {column}: {e}")
                self.ax.clear()
                self.ax.set_title(f"Error visualizing column {column}")
            self.chart_canvas.draw()
        else:
            # No valid column selected or no data to visualize
            self.ax.clear()
            self.ax.set_title("No categorical data to visualize")
            self.chart_canvas.draw()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = UnifiedSearchApp()
    window.show()
    window.setWindowIcon(QtGui.QIcon('assets/csv_icon_2.svg'))
    sys.exit(app.exec_())
