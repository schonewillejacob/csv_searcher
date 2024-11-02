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
    QLineEdit, QHBoxLayout, QVBoxLayout, QWidget, QLayout
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
    def __init__(self):
        # Run Qt setup code.
        super().__init__()
        
        # Main window attributes.
        self.setWindowTitle(" ")
        self.setMinimumSize(QSize(
            SearchWindow.MIN_DIMENSION_X, 
            SearchWindow.MIN_DIMENSION_Y
            )
        )
        # Setup widgets.
        _container = QWidget()
        _searchbar_layout = QHBoxLayout()
        
        _container.setLayout(_searchbar_layout)
        self.setCentralWidget(_container)
    

    # SLOTS ##################################################################
    def on_import_prompt_explorer(self):
        print(f"exporting")