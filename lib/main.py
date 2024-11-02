""" Intro: start of program.
   - Allows recovery, user can exit before importing.
   - Explore & select a CSV.
   - Prompts import dialog.
"""
# Jacob Schonewille, 300135438
# COMP455: group assignment 1
# Good resources:
#   - docs: https://doc.qt.io/qtforpython-5/PySide2/
#   - 



import sys
from PyQt6.QtCore import QSize, Qt, QTimer
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QLabel, QLineEdit, QHBoxLayout, QVBoxLayout, 
    QWidget, QLayout, QFileDialog, QDialog
)
from search_window import SearchWindow



# Define intro window properties and behaviour.
class IntroWindow(QMainWindow):
    """
    Navigates the app
    """
    
    # Class-scope members.
    FIXED_DIMENSION_X = 590
    FIXED_DIMENSION_Y = 332
    VERSION = "1.0.1"



    # CONSTRUCTOR ############################################################
    def __init__(self):
        # Runs Qt setup code.
        super().__init__()
        

        # Qt window attributes.
        self.setWindowTitle("dotCSV")
        self.setFixedSize(
            QSize(
                IntroWindow.FIXED_DIMENSION_X, 
                IntroWindow.FIXED_DIMENSION_Y
            )
        )
        

        # About dialog window
        self.intro_about_dialog = QDialog()
        _intro_about_layout = QVBoxLayout()
        self.intro_about_dialog.setContentsMargins(0, 0, 0, 0)
        self.intro_about_dialog.setFixedSize(QSize(332, 96))
        self.intro_about_dialog.setWindowTitle("dotCSV")
        _intro_about_paragraph = QLabel(
            f"Version v{IntroWindow.VERSION}.\n"
            +"J. Schonewille © 2024"
        )
        _intro_about_layout.addWidget(QWidget())
        _intro_about_layout.addWidget(_intro_about_paragraph)
        self.intro_about_dialog.setLayout(_intro_about_layout)

        # Wrapping container.
        _intro_container = QWidget()
        _intro_container.setContentsMargins(0,0,0,0)
        _intro_container_layout = QVBoxLayout()
        # About button prompts about dialog.
        _intro_about_button = QPushButton("?")
        _intro_about_button.clicked.connect(self.on_about)
        _intro_about_button.setFixedSize(QSize(48, 48))
        _intro_container_layout.addWidget(_intro_about_button)
        # TODO:Replace with asset
        _intro_container_layout.addWidget(QWidget())
        # Import bar 
        _intro_importbar_layout = QHBoxLayout()
        _intro_importbar = QWidget()
        _intro_importbar.setMaximumSize(QSize(99999, 48))
        _intro_importbar.setContentsMargins(0,0,0,0)
        #
        _intro_label = QLabel("file:")
        _intro_importbar_layout.addWidget(_intro_label)
        #
        self.intro_path_lineedit = QLineEdit()
        _intro_importbar_layout.addWidget(self.intro_path_lineedit)
        #
        _intro_path_button = QPushButton("browse")
        _intro_path_button.clicked.connect(self.on_browse)
        _intro_importbar_layout.addWidget(_intro_path_button)
        #
        self.intro_start_import_button = QPushButton("load")
        self.intro_start_import_button.setDisabled(True)
        self.intro_start_import_button.clicked.connect(self.on_load)
        _intro_importbar_layout.addWidget(self.intro_start_import_button)

        _intro_importbar.setLayout(_intro_importbar_layout)
        _intro_container_layout.addWidget(_intro_importbar)
        _intro_container.setLayout(_intro_container_layout)
        self.setCentralWidget(_intro_container)
        # / Wrapping container.



    # SLOTS ##################################################################
    def on_browse(self):
        fileName = QFileDialog.getOpenFileName(self, str("Open File"),
                                       "*.csv",
                                       str("csv files (*.csv)"))

        self.intro_path_lineedit.setText(fileName[0])
        self.intro_start_import_button.setDisabled(False)

        
    
    def on_load(self):
        pass

    def on_about(self):
        self.intro_about_dialog.exec()


    




# PyQt MAIN LOOP #############################################################
def main(args):
    # Creates PyQt application.
    pyqt_app = QApplication(sys.argv)
    # Create main windows. loop will close once each of these holds the close 
    intro_window = IntroWindow()
    search_window = SearchWindow()
    intro_window.show()
    # Starts the PyQt's event loop.
    pyqt_app.exec()



main(sys.argv)