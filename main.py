#!/usr/bin/env python3
"""
Wheel Strategy Options Tracker
A Mac desktop application for tracking options trading using the Wheel Strategy.
"""

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from src.main_window import MainWindow


def main():
    """Main entry point."""
    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    app = QApplication(sys.argv)
    
    # Set application metadata
    app.setApplicationName("Wheel Strategy Tracker")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("WheelTracker")
    
    # Set default font
    font = QFont("SF Pro Display", 13)
    if not font.exactMatch():
        font = QFont("Helvetica Neue", 13)
    if not font.exactMatch():
        font = QFont("Segoe UI", 13)
    app.setFont(font)
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Run the application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
