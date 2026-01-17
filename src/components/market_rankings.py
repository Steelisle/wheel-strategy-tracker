"""
Market rankings component.
Compares options performance vs major market indices.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
    QPushButton, QButtonGroup, QGridLayout
)
from PySide6.QtCore import Qt
from ..styles import COLORS, format_percent


class RankingItem(QWidget):
    """Single ranking item with name and performance."""
    
    def __init__(self, name: str, performance: float, highlighted: bool = False, parent=None):
        super().__init__(parent)
        self.setup_ui(name, performance, highlighted)
    
    def setup_ui(self, name: str, performance: float, highlighted: bool):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        
        # Container styling
        bg_color = COLORS['accent_green_dark'] if highlighted else COLORS['bg_card']
        text_color = COLORS['bg_dark'] if highlighted else COLORS['text_primary']
        perf_color = COLORS['bg_dark'] if highlighted else (COLORS['accent_green'] if performance >= 0 else COLORS['accent_red'])
        
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {bg_color};
                border-radius: 6px;
            }}
        """)
        
        name_label = QLabel(name)
        name_label.setStyleSheet(f"color: {text_color}; font-weight: 500; background: transparent;")
        layout.addWidget(name_label)
        
        layout.addStretch()
        
        perf_label = QLabel(format_percent(performance))
        perf_label.setStyleSheet(f"color: {perf_color}; font-weight: 600; background: transparent;")
        layout.addWidget(perf_label)


class MarketRankingsCard(QWidget):
    """Card showing market performance rankings."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_period = 'ytd'
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Main card frame
        card = QFrame()
        card.setObjectName("card")
        card.setStyleSheet(f"""
            QFrame#card {{
                background-color: {COLORS['bg_secondary']};
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
            }}
        """)
        
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(12)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("📊 Market Rankings")
        title.setStyleSheet(f"""
            font-size: 16px;
            font-weight: 600;
            color: {COLORS['text_primary']};
        """)
        header_layout.addWidget(title)
        header_layout.addStretch()
        card_layout.addLayout(header_layout)
        
        # Period tabs
        tab_layout = QHBoxLayout()
        
        self.tab_group = QButtonGroup(self)
        
        ytd_btn = QPushButton("YTD Performance")
        ytd_btn.setCheckable(True)
        ytd_btn.setChecked(True)
        ytd_btn.setObjectName("tab")
        ytd_btn.clicked.connect(lambda: self._set_period('ytd'))
        self.tab_group.addButton(ytd_btn, 0)
        tab_layout.addWidget(ytd_btn)
        
        year_btn = QPushButton("1 Year Performance")
        year_btn.setCheckable(True)
        year_btn.setObjectName("tab")
        year_btn.clicked.connect(lambda: self._set_period('1y'))
        self.tab_group.addButton(year_btn, 1)
        tab_layout.addWidget(year_btn)
        
        tab_layout.addStretch()
        card_layout.addLayout(tab_layout)
        
        # Rankings container
        self.rankings_layout = QVBoxLayout()
        self.rankings_layout.setSpacing(4)
        card_layout.addLayout(self.rankings_layout)
        
        card_layout.addStretch()
        layout.addWidget(card)
        
        # Initial data
        self._update_rankings([])
    
    def _set_period(self, period: str):
        """Set the display period."""
        self.current_period = period
    
    def _update_rankings(self, data: list):
        """Update the rankings display."""
        # Clear existing items
        while self.rankings_layout.count():
            item = self.rankings_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Default sample data if no data provided
        if not data:
            data = [
                ("Russell 2000", 7.89, False),
                ("Expired Options", 3.17, True),
                ("Dow Jones", 2.70, False),
                ("S&P 500", 1.38, False),
                ("Nasdaq", 1.18, False),
            ]
        
        for name, perf, highlighted in data:
            item = RankingItem(name, perf, highlighted)
            self.rankings_layout.addWidget(item)
    
    def update_data(self, options_perf: float, market_data: dict):
        """Update with actual performance data."""
        # Build rankings list
        rankings = []
        
        # Add market indices
        for name, data in market_data.items():
            rankings.append((name, data.get('return', 0), False))
        
        # Add options performance
        rankings.append(("Expired Options", options_perf, True))
        
        # Sort by performance
        rankings.sort(key=lambda x: x[1], reverse=True)
        
        self._update_rankings(rankings)


class TopPerformersCard(QWidget):
    """Card showing top performing tickers."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Main card frame
        card = QFrame()
        card.setObjectName("card")
        card.setStyleSheet(f"""
            QFrame#card {{
                background-color: {COLORS['bg_secondary']};
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
            }}
        """)
        
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(12)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("🏆 Top Performers")
        title.setStyleSheet(f"""
            font-size: 16px;
            font-weight: 600;
            color: {COLORS['text_primary']};
        """)
        header_layout.addWidget(title)
        header_layout.addStretch()
        card_layout.addLayout(header_layout)
        
        # Period tabs
        tab_layout = QHBoxLayout()
        
        self.tab_group = QButtonGroup(self)
        
        mtd_btn = QPushButton("Top 5 MTD")
        mtd_btn.setCheckable(True)
        mtd_btn.setChecked(True)
        mtd_btn.setObjectName("tab")
        self.tab_group.addButton(mtd_btn, 0)
        tab_layout.addWidget(mtd_btn)
        
        ytd_btn = QPushButton("Top 5 YTD")
        ytd_btn.setCheckable(True)
        ytd_btn.setObjectName("tab")
        self.tab_group.addButton(ytd_btn, 1)
        tab_layout.addWidget(ytd_btn)
        
        tab_layout.addStretch()
        card_layout.addLayout(tab_layout)
        
        # Two column layout for MTD and YTD
        columns_layout = QHBoxLayout()
        
        # MTD column
        self.mtd_layout = QVBoxLayout()
        self.mtd_layout.setSpacing(4)
        columns_layout.addLayout(self.mtd_layout)
        
        # YTD column  
        self.ytd_layout = QVBoxLayout()
        self.ytd_layout.setSpacing(4)
        columns_layout.addLayout(self.ytd_layout)
        
        card_layout.addLayout(columns_layout)
        
        card_layout.addStretch()
        layout.addWidget(card)
    
    def _create_performer_row(self, ticker: str, amount: float) -> QWidget:
        """Create a single performer row."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(8, 4, 8, 4)
        
        ticker_label = QLabel(ticker)
        ticker_label.setStyleSheet(f"color: {COLORS['text_primary']}; font-weight: 500;")
        layout.addWidget(ticker_label)
        
        layout.addStretch()
        
        amount_label = QLabel(f"${amount:,.0f}")
        amount_label.setStyleSheet(f"color: {COLORS['accent_green']}; font-weight: 600;")
        layout.addWidget(amount_label)
        
        return widget
    
    def update_data(self, mtd_performers: list, ytd_performers: list):
        """Update the top performers data."""
        # Clear MTD
        while self.mtd_layout.count():
            item = self.mtd_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Clear YTD
        while self.ytd_layout.count():
            item = self.ytd_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Add MTD performers
        for performer in mtd_performers[:5]:
            ticker = performer.get('ticker', 'N/A')
            amount = performer.get('total_premium', 0)
            self.mtd_layout.addWidget(self._create_performer_row(ticker, amount))
        
        # Add YTD performers
        for performer in ytd_performers[:5]:
            ticker = performer.get('ticker', 'N/A')
            amount = performer.get('total_premium', 0)
            self.ytd_layout.addWidget(self._create_performer_row(ticker, amount))
