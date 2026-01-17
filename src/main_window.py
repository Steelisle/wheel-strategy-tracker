"""
Main application window for Wheel Strategy Tracker.
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QScrollArea, QFrame, QPushButton, QStackedWidget, QSplitter,
    QSizePolicy, QMenuBar, QMenu, QMessageBox, QFileDialog
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction
from datetime import datetime, timedelta
import csv

from .styles import COLORS, get_stylesheet, format_currency
from .lib.database import get_database, set_demo_mode, is_demo_mode
from .lib.polygon_api import get_polygon_api

from .components.premium_card import PremiumCard
from .components.portfolio_card import PortfolioCard
from .components.positions_table import PositionsTable
from .components.chart_widgets import PortfolioChartCard, OptionsIncomeCard
from .components.trade_dialog import QuickTradeButtons
from .components.market_rankings import MarketRankingsCard, TopPerformersCard
from .components.settings_page import SettingsPage


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Wheel Strategy Tracker")
        self.setMinimumSize(1400, 900)
        self.resize(1600, 1000)
        
        # Apply stylesheet
        self.setStyleSheet(get_stylesheet())
        
        # Setup UI
        self._setup_menu()
        self._setup_ui()
        
        # Load initial data
        self._refresh_data()
        
        # Setup auto-refresh timer (every 5 minutes)
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self._refresh_data)
        self.refresh_timer.start(300000)  # 5 minutes
    
    def _setup_menu(self):
        """Setup the menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        export_action = QAction("Export to CSV...", self)
        export_action.triggered.connect(self._export_csv)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        refresh_action = QAction("Refresh Data", self)
        refresh_action.setShortcut("Cmd+R")
        refresh_action.triggered.connect(self._refresh_data)
        file_menu.addAction(refresh_action)
        
        # View menu
        view_menu = menubar.addMenu("View")
        
        dashboard_action = QAction("Dashboard", self)
        dashboard_action.setShortcut("Cmd+1")
        dashboard_action.triggered.connect(lambda: self._show_page(0))
        view_menu.addAction(dashboard_action)
        
        settings_action = QAction("Settings", self)
        settings_action.setShortcut("Cmd+,")
        settings_action.triggered.connect(lambda: self._show_page(1))
        view_menu.addAction(settings_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _setup_ui(self):
        """Setup the main UI."""
        # Central widget with stacked pages
        self.stacked = QStackedWidget()
        self.setCentralWidget(self.stacked)
        
        # Dashboard page
        dashboard = self._create_dashboard()
        self.stacked.addWidget(dashboard)
        
        # Settings page
        self.settings_page = SettingsPage()
        self.settings_page.settings_changed.connect(self._refresh_data)
        self.stacked.addWidget(self.settings_page)
    
    def _create_dashboard(self) -> QWidget:
        """Create the main dashboard page."""
        # Main container with scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        container = QWidget()
        container.setStyleSheet(f"background-color: {COLORS['bg_dark']};")
        
        main_layout = QVBoxLayout(container)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(24, 24, 24, 24)
        
        # Header with title and quick actions
        header = self._create_header()
        main_layout.addLayout(header)
        
        # Top row: Premium, Portfolio, Options cards
        top_row = QHBoxLayout()
        top_row.setSpacing(20)
        
        self.premium_card = PremiumCard()
        self.premium_card.setMinimumWidth(320)
        self.premium_card.setMaximumWidth(400)
        top_row.addWidget(self.premium_card, 1)
        
        self.portfolio_card = PortfolioCard()
        self.portfolio_card.data_changed.connect(self._on_portfolio_changed)
        top_row.addWidget(self.portfolio_card, 2)  # Give portfolio more space
        
        main_layout.addLayout(top_row)
        
        # Middle row: Positions table, Charts
        middle_row = QHBoxLayout()
        middle_row.setSpacing(20)
        
        # Left column: Positions table
        self.positions_table = PositionsTable()
        self.positions_table.setMinimumWidth(400)
        self.positions_table.setMaximumWidth(450)
        middle_row.addWidget(self.positions_table)
        
        # Center: Portfolio chart
        self.portfolio_chart = PortfolioChartCard()
        middle_row.addWidget(self.portfolio_chart, 2)
        
        # Right: Options income chart
        self.options_income = OptionsIncomeCard()
        self.options_income.setMinimumWidth(300)
        middle_row.addWidget(self.options_income, 1)
        
        main_layout.addLayout(middle_row)
        
        # Bottom row: Market rankings, Top performers
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(20)
        
        self.market_rankings = MarketRankingsCard()
        bottom_row.addWidget(self.market_rankings, 1)
        
        self.top_performers = TopPerformersCard()
        bottom_row.addWidget(self.top_performers, 1)
        
        main_layout.addLayout(bottom_row)
        
        main_layout.addStretch()
        
        scroll.setWidget(container)
        return scroll
    
    def _create_header(self) -> QHBoxLayout:
        """Create the header with title and actions."""
        header = QHBoxLayout()
        
        # Title section
        title_layout = QVBoxLayout()
        
        title = QLabel("Wheel Strategy Tracker")
        title.setStyleSheet(f"""
            font-size: 28px;
            font-weight: 700;
            color: {COLORS['text_primary']};
        """)
        title_layout.addWidget(title)
        
        subtitle = QLabel(f"Updated: {datetime.now().strftime('%b %d, %Y %I:%M %p')}")
        subtitle.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 13px;")
        self.subtitle_label = subtitle
        title_layout.addWidget(subtitle)
        
        header.addLayout(title_layout)
        header.addStretch()
        
        # Quick trade buttons
        self.quick_trade = QuickTradeButtons()
        self.quick_trade.trade_added.connect(self._refresh_data)
        header.addWidget(self.quick_trade)
        
        # Demo mode toggle
        self.demo_toggle = QPushButton("📊 Demo Mode")
        self.demo_toggle.setCheckable(True)
        self.demo_toggle.setChecked(is_demo_mode())
        self._update_demo_button_style()
        self.demo_toggle.clicked.connect(self._toggle_demo_mode)
        header.addWidget(self.demo_toggle)
        
        # Settings button
        settings_btn = QPushButton("⚙️ Settings")
        settings_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: 1px solid {COLORS['border']};
                color: {COLORS['text_secondary']};
                padding: 8px 16px;
                border-radius: 6px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['bg_hover']};
                color: {COLORS['text_primary']};
            }}
        """)
        settings_btn.clicked.connect(lambda: self._show_page(1))
        header.addWidget(settings_btn)
        
        return header
    
    def _show_page(self, index: int):
        """Switch to a specific page."""
        self.stacked.setCurrentIndex(index)
    
    def _toggle_demo_mode(self):
        """Toggle between demo and active mode."""
        is_demo = self.demo_toggle.isChecked()
        set_demo_mode(is_demo)
        self._update_demo_button_style()
        self._refresh_data()
    
    def _on_portfolio_changed(self):
        """Handle portfolio data changes."""
        self.portfolio_card.refresh_data()
    
    def _update_demo_button_style(self):
        """Update the demo toggle button style based on state."""
        if is_demo_mode():
            self.demo_toggle.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLORS['accent_yellow']};
                    border: none;
                    color: {COLORS['bg_dark']};
                    font-weight: 600;
                    padding: 8px 16px;
                    border-radius: 6px;
                }}
                QPushButton:hover {{
                    background-color: #fbbf24;
                }}
            """)
            self.demo_toggle.setText("📊 Demo Mode")
        else:
            self.demo_toggle.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLORS['accent_green_dark']};
                    border: none;
                    color: {COLORS['bg_dark']};
                    font-weight: 600;
                    padding: 8px 16px;
                    border-radius: 6px;
                }}
                QPushButton:hover {{
                    background-color: {COLORS['accent_green']};
                }}
            """)
            self.demo_toggle.setText("📈 Active Mode")
    
    def _refresh_data(self):
        """Refresh all dashboard data."""
        db = get_database()
        api = get_polygon_api()
        
        # Update timestamp
        self.subtitle_label.setText(f"Updated: {datetime.now().strftime('%b %d, %Y %I:%M %p')}")
        
        # Load premium summary
        premium_data = db.get_premium_summary()
        self.premium_card.update_data(premium_data)
        
        # Refresh portfolio card
        self.portfolio_card.refresh_data()
        
        # Load positions
        positions = db.get_all_positions()
        self.positions_table.update_data(positions)
        
        # Calculate total portfolio value (simplified)
        total_premium = sum(p.get('total_premium', 0) for p in positions)
        
        # Generate sample chart data (would be from snapshots in production)
        chart_data = self._generate_sample_chart_data(total_premium)
        
        change = total_premium * 0.02  # Placeholder
        change_pct = 2.0
        self.portfolio_chart.update_data(total_premium, -change, -change_pct, chart_data)
        
        # Options income
        week_data = self._generate_sample_bar_data()
        self.options_income.update_data(
            premium_data.get('ytd', 0),
            1.14,  # Placeholder week change
            premium_data.get('week', 0) * 0.1,  # Placeholder today
            week_data
        )
        
        # Top performers
        mtd_performers = db.get_top_performers('mtd', 5)
        ytd_performers = db.get_top_performers('ytd', 5)
        self.top_performers.update_data(mtd_performers, ytd_performers)
        
        # Market rankings (try to fetch from API)
        try:
            market_data = api.get_index_performance(365)
            options_ytd = premium_data.get('ytd', 0)
            # Calculate percentage return (simplified)
            options_pct = (options_ytd / 100000) * 100 if options_ytd > 0 else 0
            self.market_rankings.update_data(options_pct, market_data)
        except Exception:
            # Use default data if API fails
            pass
    
    def _generate_sample_chart_data(self, current_value: float) -> list:
        """Generate sample chart data points."""
        data = []
        base_value = current_value * 0.95
        
        for i in range(30):
            date = (datetime.now() - timedelta(days=29-i)).strftime("%Y-%m-%d")
            # Add some variation
            variation = (i / 30) * (current_value - base_value)
            noise = (i % 5 - 2) * (current_value * 0.005)
            value = base_value + variation + noise
            data.append((date, max(0, value)))
        
        return data
    
    def _generate_sample_bar_data(self) -> list:
        """Generate sample bar chart data."""
        import random
        data = []
        for i in range(7):
            day = (datetime.now() - timedelta(days=6-i)).strftime("%a")
            value = random.uniform(100, 500)
            data.append((day, value))
        return data
    
    def _export_csv(self):
        """Export trades to CSV."""
        db = get_database()
        trades = db.get_all_trades()
        
        if not trades:
            QMessageBox.information(self, "Export", "No trades to export.")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Trades", "trades.csv", "CSV Files (*.csv)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=trades[0].keys())
                    writer.writeheader()
                    writer.writerows(trades)
                QMessageBox.information(self, "Success", f"Exported {len(trades)} trades to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export: {str(e)}")
    
    def _show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About Wheel Strategy Tracker",
            "Wheel Strategy Options Tracker\n\n"
            "A desktop application for tracking options trading using the Wheel Strategy.\n\n"
            "Features:\n"
            "• Track cash-secured puts and covered calls\n"
            "• Premium tracking by period\n"
            "• Portfolio performance visualization\n"
            "• Polygon.io market data integration\n\n"
            "Version 1.0.0"
        )
