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
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

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
        self.headers = headers
        self.rows = rows
        self.filtered_rows = rows  # For filtering
        
        # Main window attributes.
        self.setWindowTitle("Search and Visualize Data")
        self.setMinimumSize(QSize(
            SearchWindow.MIN_DIMENSION_X, 
            SearchWindow.MIN_DIMENSION_Y
        ))
        
        # Setup widgets.
        _container = QWidget()
        _layout = QVBoxLayout()

        # Add search bar
        search_layout = QHBoxLayout()
        search_label = QLabel("Search:")
        self.search_input = QLineEdit()
        self.search_button = QPushButton("Filter")
        self.search_button.clicked.connect(self.filter_data)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)

        # Visualization button
        self.visualize_button = QPushButton("Visualize Data")
        self.visualize_button.clicked.connect(self.visualize_data)

        # Create a table to display CSV data
        self.table = QTableWidget()
        self.table.setRowCount(len(rows))
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.populate_table(rows)

        # Sorting functionality
        self.table.setSortingEnabled(True)

        # Add components to layout
        _layout.addLayout(search_layout)
        _layout.addWidget(self.visualize_button)
        _layout.addWidget(self.table)
        _container.setLayout(_layout)
        self.setCentralWidget(_container)

    def populate_table(self, data):
        """Populate the table with data."""
        self.table.setRowCount(len(data))
        for row_idx, row in enumerate(data):
            for col_idx, cell in enumerate(row):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(cell)))

    def filter_data(self):
        """Filter data based on search input."""
        query = self.search_input.text().lower()
        self.filtered_rows = [
            row for row in self.rows if any(query in str(cell).lower() for cell in row)
        ]
        self.populate_table(self.filtered_rows)

    def visualize_data(self):
        """Visualize data, including gender distribution and top positions."""
        gender_counts = {}
        position_counts = {}

        # Extract data for visualization
        for row in self.rows:
            # Gender distribution
            if "Gender" in self.headers:
                gender = row[self.headers.index("Gender")]
                gender_counts[gender] = gender_counts.get(gender, 0) + 1

            # Top positions
            if "Position" in self.headers:
                position = row[self.headers.index("Position")]
                position_counts[position] = position_counts.get(position, 0) + 1

        # Plot data
        if gender_counts:
            self.plot_pie_chart(gender_counts, "Gender Distribution")
        if position_counts:
            self.plot_bar_chart(position_counts, "Top Positions")

    def plot_pie_chart(self, data, title):
        """Plot a pie chart."""
        figure = Figure()
        canvas = FigureCanvas(figure)
        ax = figure.add_subplot(111)
        ax.pie(data.values(), labels=data.keys(), autopct='%1.1f%%')
        ax.set_title(title)

        # Display chart in a new window
        self.show_chart(canvas)

    def plot_bar_chart(self, data, title):
        """Plot a bar chart."""
        figure = Figure()
        canvas = FigureCanvas(figure)
        ax = figure.add_subplot(111)
        sorted_data = sorted(data.items(), key=lambda x: x[1], reverse=True)[:5]
        labels, counts = zip(*sorted_data)
        ax.bar(labels, counts)
        ax.set_title(title)
        ax.set_ylabel("Count")

        # Display chart in a new window
        self.show_chart(canvas)

    def show_chart(self, canvas):
        """Display the chart in a new window."""
        chart_window = QMainWindow(self)
        chart_window.setWindowTitle("Visualization")
        chart_window.setCentralWidget(canvas)
        chart_window.resize(600, 400)
        chart_window.show()

    # SLOTS ##################################################################
    def on_import_prompt_explorer(self):
        print(f"exporting")

