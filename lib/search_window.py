""" SearchMainWindow: explores csv.
   - Allows recovery, user can exit before importing.
   - Explore & select a CSV.
   - Prompts ImportDialog.
   - Provides search functionality.
      - provide keyword searchbar and search tools
      - provide filter by value range
      - provide sorting by value
      - allow navigation to help & version window
"""

import sys
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QLabel, 
    QLineEdit, QHBoxLayout, QVBoxLayout, QWidget, QLayout, QTableWidget, QTableWidgetItem
)


# Define main window properties and behaviour. 🔎︎
class SearchWindow(QMainWindow):
    """
    QMainWindow, transitions into the search window
    used for branding
    """
    
    # Class-scope members.
    MIN_DIMENSION_X = 600
    MIN_DIMENSION_Y = 450

    # CONSTRUCTOR ############################################################
    def __init__(self, headers, rows):
        """
        Initialize the SearchWindow with headers and rows from the CSV file.
        """
        super().__init__()
        
        # Main window attributes.
        self.setWindowTitle("Search Data")
        self.setMinimumSize(QSize(
            SearchWindow.MIN_DIMENSION_X, 
            SearchWindow.MIN_DIMENSION_Y
            )
        )
        
        # Setup widgets.
        _container = QWidget()
        _layout = QVBoxLayout()

        # Create a table to display CSV data
        self.table = QTableWidget()
        self.table.setRowCount(len(rows))
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)

        # Populate the table with data
        for row_idx, row in enumerate(rows):
            for col_idx, cell in enumerate(row):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(cell)))

        _layout.addWidget(self.table)
        _container.setLayout(_layout)
        self.setCentralWidget(_container)

    # SLOTS ##################################################################
    def on_import_prompt_explorer(self):
        print(f"exporting")

