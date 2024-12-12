import sys
import csv
from PyQt5 import QtWidgets, QtGui, QtCore
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import pandas as pd


class UnifiedSearchApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.headers = []  # To store column headers dynamically
        self.data = []  # To store CSV data
        self.filtered_data = []  # To store filtered data for export
        self.search_fields = {}  # To store column-specific dropdown menus dynamically
        self.initUI()

    def initUI(self):
        # Window setup
        self.setWindowTitle("Unified CSV Search Application")
        self.setGeometry(200, 100, 1000, 600)
        self.layout = QtWidgets.QVBoxLayout()
        
        #Main window
        self.setLayout(self.layout)

        # Main layout with splitter
        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.layout.addWidget(self.splitter)

        # Left layout: search fields and graph
        left_layout = QtWidgets.QWidget()
        left_layout.setLayout(QtWidgets.QVBoxLayout())
        self.splitter.addWidget(left_layout)

        # File selection
        top_layout = QtWidgets.QHBoxLayout()
        left_layout.layout().addLayout(top_layout)

        # File selection (Browse CSV)
        self.file_path_box = QtWidgets.QLineEdit(self)
        self.file_path_box.setPlaceholderText("Select a CSV file...")
        top_layout.addWidget(self.file_path_box)

        browse_btn = QtWidgets.QPushButton("Browse", self)
        browse_btn.clicked.connect(self.open_file_dialog)
        top_layout.addWidget(browse_btn)

        # General search bar
        self.general_search_box = QtWidgets.QLineEdit(self)
        self.general_search_box.setPlaceholderText("Enter general search term...")
        top_layout.addWidget(self.general_search_box)

        # Search button
        general_search_btn = QtWidgets.QPushButton("Search All", self)
        general_search_btn.clicked.connect(self.perform_general_search)
        top_layout.addWidget(general_search_btn)

        # Column-specific search fields (editable dropdowns)
        self.column_search_layout = QtWidgets.QFormLayout()
        left_layout.layout().addLayout(self.column_search_layout)

        # Specific search button
        specific_search_button = QtWidgets.QPushButton("Search by Column", self)
        specific_search_button.clicked.connect(self.perform_column_search)
        left_layout.layout().addWidget(specific_search_button)

        # Export filtered data button
        export_button = QtWidgets.QPushButton("Export Filtered Data", self)
        export_button.clicked.connect(self.export_filtered_data)
        left_layout.layout().addWidget(export_button)

        # Table for displaying results
        self.table = QtWidgets.QTableWidget()
        self.layout.addWidget(self.table)

        # Chart controls (renamed and reduced space)
        chart_controls_layout = QtWidgets.QHBoxLayout()
        left_layout.layout().addLayout(chart_controls_layout)

        self.chart_label = QtWidgets.QLabel("Select Column for Graph Visualization:")
        chart_controls_layout.addWidget(self.chart_label)

        self.column_selector = QtWidgets.QComboBox()
        self.column_selector.currentTextChanged.connect(self.update_graph)
        chart_controls_layout.addWidget(self.column_selector)

        # Right layout: Graph area
        right_layout = QtWidgets.QWidget()
        right_layout.setLayout(QtWidgets.QVBoxLayout())
        self.splitter.addWidget(right_layout)

        # Chart canvas setup
        self.chart_canvas = FigureCanvas(Figure(figsize=(6, 4)))
        right_layout.layout().addWidget(self.chart_canvas)
        self.ax = self.chart_canvas.figure.add_subplot(111)

        # Set minimum width for graph section
        self.splitter.setSizes([300, 700])  # Set left section smaller and right section (graph) larger        

    def open_file_dialog(self):
        # Open file dialog to select a CSV file
        options = QtWidgets.QFileDialog.Options()
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Open CSV File", "", "CSV Files (*.csv);;All Files (*)", options=options
        )
        if file_path:
            self.file_path_box.setText(file_path)
            self.load_csv_data(file_path)

    def load_csv_data(self, file_path):
        try:
            # Attempt to load with utf-8 encoding
            try:
                with open(file_path, newline='', encoding='utf-8') as csvfile:
                    self.data = list(csv.reader(csvfile))
            except UnicodeDecodeError:
                # Fallback to ISO-8859-1 encoding
                with open(file_path, newline='', encoding='ISO-8859-1') as csvfile:
                    self.data = list(csv.reader(csvfile))

            if len(self.data) == 0:
                QtWidgets.QMessageBox.warning(self, "Warning", "The file is empty.")
                return

            # Extract headers
            self.headers = self.data[0]
            self.update_search_fields()

            # Set up the table headers
            self.table.setColumnCount(len(self.headers))
            self.table.setHorizontalHeaderLabels(self.headers)

            # Load all rows into the table
            self.table.setRowCount(len(self.data) - 1)
            for row_num, row_data in enumerate(self.data[1:]):
                for col_num, cell_data in enumerate(row_data):
                    self.table.setItem(
                        row_num, col_num, QtWidgets.QTableWidgetItem(cell_data)
                    )

            # Reset filtered data
            self.filtered_data = self.data[1:]
            self.populate_column_selector()
            print("CSV Data Loaded Successfully!")

        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Error", f"Failed to load CSV file:\n{e}")
            print(f"Error loading CSV: {e}")

    def update_search_fields(self):
        # Clear existing fields
        for i in reversed(range(self.column_search_layout.count())):
            self.column_search_layout.itemAt(i).widget().deleteLater()

        self.search_fields = {}

        # Dynamically add editable dropdown menus for each column
        for col_idx, header in enumerate(self.headers):
            dropdown = QtWidgets.QComboBox(self)
            dropdown.setEditable(True)  # Make the dropdown editable
            dropdown.addItem("All")  # Default "All" option
            unique_values = sorted(set(row[col_idx].strip() for row in self.data[1:] if row[col_idx].strip()))
            dropdown.addItems(unique_values)
            self.column_search_layout.addRow(header + ":", dropdown)
            self.search_fields[header] = dropdown

    def perform_general_search(self):
        """Searches across all columns for the given query."""
        search_query = self.general_search_box.text().strip().lower()
        if not self.data or len(self.data) <= 1:
            QtWidgets.QMessageBox.warning(self, "Warning", "Please load a CSV file first.")
            return
        if not search_query:
            QtWidgets.QMessageBox.warning(self, "Warning", "Please enter a search term.")
            return

        results = [
            row for row in self.data[1:]
            if any(str(cell).strip().lower() == search_query for cell in row)  # Ensure exact match
        ]

        self.filtered_data = results  # Update filtered data
        self.display_results(results)

    def perform_column_search(self):
        """Searches specific columns based on dropdown values."""
        if not self.data or len(self.data) <= 1:
            QtWidgets.QMessageBox.warning(self, "Warning", "Please load a CSV file first.")
            return

        # Collect selected or typed values from dropdowns
        search_terms = {
            header: dropdown.currentText().strip().lower()
            for header, dropdown in self.search_fields.items()
            if dropdown.currentText() != "All"
        }

        results = []
        for row in self.data[1:]:
            match = True
            for header, term in search_terms.items():
                column_index = self.headers.index(header)
                cell_value = str(row[column_index]).strip().lower()

                # Check for exact match
                if cell_value != term:
                    match = False
                    break
            if match:
                results.append(row)

        self.filtered_data = results  # Update filtered data
        self.display_results(results)

    def display_results(self, results):
        """Displays search results in the table."""
        self.table.setRowCount(len(results))
        for row_num, row_data in enumerate(results):
            for col_num, cell_data in enumerate(row_data):
                self.table.setItem(row_num, col_num, QtWidgets.QTableWidgetItem(cell_data))

        print(f"Number of results found: {len(results)}")

    def export_filtered_data(self):
        """Exports the filtered data to a new CSV file."""
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
                    writer.writerow(self.headers)  # Write headers
                    writer.writerows(self.filtered_data)  # Write filtered data
                QtWidgets.QMessageBox.information(self, "Success", "Filtered data exported successfully!")
            except Exception as e:
                QtWidgets.QMessageBox.warning(self, "Error", f"Failed to export CSV file:\n{e}")

    def populate_column_selector(self):
        if self.headers:
            self.column_selector.clear()
            self.column_selector.addItems(self.headers)

    def update_graph(self):
        """Update the graph based on the selected column."""
        column = self.column_selector.currentText()
        if self.data and column:
            try:
                # Clear the current graph
                self.ax.clear()

                # Get the column index
                col_idx = self.headers.index(column)
                column_data = [row[col_idx] for row in self.data[1:] if row[col_idx]]  # Exclude empty cells

                # Check if the column is numeric or categorical
                try:
                    # Try converting to numeric for histogram
                    numeric_data = list(map(float, column_data))
                    self.ax.hist(numeric_data, bins=10, color='skyblue', edgecolor='black')
                    self.ax.set_title(f"Histogram of {column}")
                    self.ax.set_xlabel(column)
                    self.ax.set_ylabel("Frequency")
                except ValueError:
                    # Handle categorical data
                    value_counts = pd.Series(column_data).value_counts()
                    value_counts.plot(kind='bar', ax=self.ax, color='skyblue', edgecolor='black')
                    self.ax.set_title(f"Bar Chart of {column}")
                    self.ax.set_xlabel(column)
                    self.ax.set_ylabel("Count")

                # Redraw the canvas
                self.chart_canvas.draw()

            except Exception as e:
                QtWidgets.QMessageBox.warning(self, "Error", f"Failed to update graph for column '{column}':\n{e}")
                print(f"Graph update error: {e}")


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    
    window = UnifiedSearchApp()
    window.setWindowIcon(QtGui.QIcon('assets\csv_icon.svg'))
    window.show()

    sys.exit(app.exec_())