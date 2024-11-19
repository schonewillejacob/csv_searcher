import sys
import csv
from PyQt5 import QtWidgets, QtGui, QtCore

class CSVSearchApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.showGUI()

    def showGUI(self):
        # Window setup
        self.setWindowTitle("CSV Filter application")
        self.setGeometry(200, 100, 900, 600)

        # Layouts
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        # File selection
        file_layout = QtWidgets.QHBoxLayout()
        layout.addLayout(file_layout)
        
        self.file_path_box = QtWidgets.QLineEdit(self)
        self.file_path_box.setPlaceholderText("Select a CSV file...")
        file_layout.addWidget(self.file_path_box)
        
        browse_btn = QtWidgets.QPushButton("Browse", self)
        browse_btn.clicked.connect(self.open_file_dialog)
        file_layout.addWidget(browse_btn)
        
        # Search functionality
        
        search_layout = QtWidgets.QHBoxLayout()
        layout.addLayout(search_layout)
        
        self.search_edit = QtWidgets.QLineEdit(self)
        self.search_edit.setPlaceholderText("Enter search term...")
        search_layout.addWidget(self.search_edit)
        
        search_button = QtWidgets.QPushButton("Search", self)
        search_button.clicked.connect(self.perform_search)
        search_layout.addWidget(search_button)

        # Table for displaying results
        self.table = QtWidgets.QTableWidget()
        layout.addWidget(self.table)

    def open_file_dialog(self):
        # This method opens the QFileDialog for selecting a CSV file
        options = QtWidgets.QFileDialog.Options()
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Open CSV File", "", "CSV Files (*.csv);;All Files (*)", options=options
        )
        if file_path:
            self.file_path_box.setText(file_path)
            self.load_csv_data(file_path)

    def load_csv_data(self, file_path):
        try:
            with open(file_path, newline='', encoding='utf-8') as csvfile:
                self.data = list(csv.reader(csvfile))
                
                # Check if the data was loaded
                if len(self.data) == 0:
                    print("No data found in the CSV.")
                    return
                
                headers = self.data[0]
                self.table.setColumnCount(len(headers))
                self.table.setHorizontalHeaderLabels(headers)
                
                # Populate the table with initial data
                self.table.setRowCount(len(self.data) - 1)
                for row_num, row_data in enumerate(self.data[1:]):
                    for col_num, cell_data in enumerate(row_data):
                        self.table.setItem(row_num, col_num, QtWidgets.QTableWidgetItem(cell_data))
                
                # Debugging: Check data loaded successfully
                print("CSV Data Loaded Successfully!")
                print("Headers:", headers)
                print("Data Row:", self.data[1] if len(self.data) > 1 else "No data rows")

        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Error", f"Failed to load CSV file:\n{e}")
            print(f"Error loading CSV: {e}")

    def perform_search(self):
        search_term = self.search_edit.text().strip().lower()
        
        if not hasattr(self, 'data') or len(self.data) == 0:
             QtWidgets.QMessageBox.warning(self, "Warning", "Please load a CSV file.")
             print("No CSV data loaded.")
             return
        
        if not search_term:
             QtWidgets.QMessageBox.warning(self, "Warning", "Please enter a search term.")
             return

        # # Clear the table
        self.table.setRowCount(0)
        
        # #Search through each row and collect matching rows
        headers = self.data[0]
        results = []
        for row_data in self.data[1:]:
             if any(search_term in cell.lower() for cell in row_data):
                 results.append(row_data)

        # # Debugging: Output number of results found
        print(f"Number of results found: {len(results)}")

        # # Display the search results in the table
        self.table.setRowCount(len(results))
        for row_num, row_data in enumerate(results):
             for col_num, cell_data in enumerate(row_data):
                 self.table.setItem(row_num, col_num, QtWidgets.QTableWidgetItem(cell_data))

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = CSVSearchApp()
    window.show()
    sys.exit(app.exec_())
