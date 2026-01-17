"""
Chart widgets for portfolio visualization.
Uses QPainter for custom drawing since we don't have matplotlib in PySide6.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton,
    QButtonGroup, QSizePolicy
)
from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QPainter, QPen, QColor, QBrush, QPainterPath, QLinearGradient
from ..styles import COLORS, format_currency, format_percent
from datetime import datetime, timedelta


class LineChart(QWidget):
    """Simple line chart widget for portfolio value."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.data = []
        self.setMinimumHeight(200)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    
    def set_data(self, data: list[tuple[str, float]]):
        """Set chart data as list of (date_str, value) tuples."""
        self.data = data
        self.update()
    
    def paintEvent(self, event):
        if not self.data:
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Chart dimensions
        margin = 10
        width = self.width() - 2 * margin
        height = self.height() - 2 * margin
        
        if width <= 0 or height <= 0:
            return
        
        # Get value range
        values = [v for _, v in self.data]
        min_val = min(values) * 0.95
        max_val = max(values) * 1.05
        val_range = max_val - min_val if max_val != min_val else 1
        
        # Calculate points
        points = []
        for i, (_, value) in enumerate(self.data):
            x = margin + (i / (len(self.data) - 1)) * width if len(self.data) > 1 else margin + width / 2
            y = margin + height - ((value - min_val) / val_range) * height
            points.append(QPointF(x, y))
        
        # Draw gradient fill
        if points:
            gradient = QLinearGradient(0, margin, 0, margin + height)
            gradient.setColorAt(0, QColor(COLORS['accent_green']).lighter(150))
            gradient.setColorAt(1, QColor(COLORS['bg_secondary']))
            
            fill_path = QPainterPath()
            fill_path.moveTo(points[0].x(), margin + height)
            for pt in points:
                fill_path.lineTo(pt)
            fill_path.lineTo(points[-1].x(), margin + height)
            fill_path.closeSubpath()
            
            painter.fillPath(fill_path, QBrush(gradient))
        
        # Draw line
        pen = QPen(QColor(COLORS['accent_green']))
        pen.setWidth(2)
        painter.setPen(pen)
        
        for i in range(len(points) - 1):
            painter.drawLine(points[i], points[i + 1])
        
        # Draw points
        painter.setBrush(QBrush(QColor(COLORS['accent_green'])))
        for pt in points:
            painter.drawEllipse(pt, 3, 3)


class BarChart(QWidget):
    """Simple bar chart widget for monthly income."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.data = []
        self.setMinimumHeight(150)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    
    def set_data(self, data: list[tuple[str, float]]):
        """Set chart data as list of (label, value) tuples."""
        self.data = data
        self.update()
    
    def paintEvent(self, event):
        if not self.data:
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Chart dimensions
        margin = 10
        width = self.width() - 2 * margin
        height = self.height() - 2 * margin - 20  # Leave room for labels
        
        if width <= 0 or height <= 0 or len(self.data) == 0:
            return
        
        # Get value range
        values = [v for _, v in self.data]
        max_val = max(values) if values else 1
        if max_val == 0:
            max_val = 1
        
        # Bar dimensions
        bar_width = max(4, (width / len(self.data)) * 0.7)
        gap = (width / len(self.data)) * 0.3
        
        for i, (label, value) in enumerate(self.data):
            x = margin + i * (bar_width + gap)
            bar_height = (value / max_val) * height if max_val > 0 else 0
            y = margin + height - bar_height
            
            # Choose color based on whether it's today's month
            color = QColor(COLORS['accent_green'])
            
            # Draw bar
            painter.setBrush(QBrush(color))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(QRectF(x, y, bar_width, bar_height), 2, 2)


class PortfolioChartCard(QWidget):
    """Card containing portfolio value chart with timeframe selectors."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_value = 0
        self.change_value = 0
        self.change_percent = 0
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
        
        # Value display
        value_layout = QHBoxLayout()
        
        self.value_label = QLabel("$0.00")
        self.value_label.setStyleSheet(f"""
            font-size: 32px;
            font-weight: 700;
            color: {COLORS['text_primary']};
        """)
        value_layout.addWidget(self.value_label)
        
        self.change_label = QLabel("$0.00 (0.00%)")
        self.change_label.setStyleSheet(f"""
            font-size: 14px;
            color: {COLORS['accent_green']};
        """)
        value_layout.addWidget(self.change_label)
        value_layout.addStretch()
        
        card_layout.addLayout(value_layout)
        
        # Chart
        self.chart = LineChart()
        card_layout.addWidget(self.chart, 1)
        
        # Timeframe buttons
        timeframe_layout = QHBoxLayout()
        timeframe_layout.addStretch()
        
        self.timeframe_group = QButtonGroup(self)
        timeframes = ["LIVE", "1D", "1W", "1M", "3M", "YTD", "1Y", "ALL"]
        
        for i, tf in enumerate(timeframes):
            btn = QPushButton(tf)
            btn.setCheckable(True)
            btn.setObjectName("tab")
            btn.setStyleSheet(f"""
                QPushButton#tab {{
                    background-color: transparent;
                    border: none;
                    border-radius: 4px;
                    padding: 4px 8px;
                    color: {COLORS['text_secondary']};
                    font-size: 12px;
                }}
                QPushButton#tab:hover {{
                    background-color: {COLORS['bg_hover']};
                    color: {COLORS['text_primary']};
                }}
                QPushButton#tab:checked {{
                    background-color: {COLORS['accent_green_dark']};
                    color: {COLORS['bg_dark']};
                }}
            """)
            if tf == "1W":
                btn.setChecked(True)
            self.timeframe_group.addButton(btn, i)
            timeframe_layout.addWidget(btn)
        
        timeframe_layout.addStretch()
        card_layout.addLayout(timeframe_layout)
        
        layout.addWidget(card)
    
    def update_data(self, value: float, change: float, change_pct: float, chart_data: list):
        """Update the portfolio chart data."""
        self.current_value = value
        self.change_value = change
        self.change_percent = change_pct
        
        self.value_label.setText(format_currency(value))
        
        change_color = COLORS['accent_green'] if change >= 0 else COLORS['accent_red']
        sign = "+" if change >= 0 else ""
        self.change_label.setText(f"▼ {format_currency(abs(change))} ({format_percent(change_pct)})")
        self.change_label.setStyleSheet(f"font-size: 14px; color: {change_color};")
        
        self.chart.set_data(chart_data)


class OptionsIncomeCard(QWidget):
    """Card showing options income bar chart."""
    
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
        
        title = QLabel("Options")
        title.setStyleSheet(f"""
            font-size: 18px;
            font-weight: 600;
            color: {COLORS['text_primary']};
        """)
        header_layout.addWidget(title)
        
        self.value_label = QLabel("+$0.00")
        self.value_label.setStyleSheet(f"""
            font-size: 24px;
            font-weight: 700;
            color: {COLORS['accent_green']};
        """)
        header_layout.addWidget(self.value_label)
        header_layout.addStretch()
        
        card_layout.addLayout(header_layout)
        
        # Stats
        stats_layout = QHBoxLayout()
        
        self.week_change = QLabel("Past week")
        self.week_change.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 12px;")
        stats_layout.addWidget(self.week_change)
        
        self.today_change = QLabel("Today")
        self.today_change.setStyleSheet(f"color: {COLORS['accent_green']}; font-size: 12px;")
        stats_layout.addWidget(self.today_change)
        stats_layout.addStretch()
        
        card_layout.addLayout(stats_layout)
        
        # Bar chart
        self.chart = BarChart()
        card_layout.addWidget(self.chart, 1)
        
        # Timeframe buttons
        timeframe_layout = QHBoxLayout()
        timeframe_layout.addStretch()
        
        self.timeframe_group = QButtonGroup(self)
        timeframes = ["1W", "1M", "3M", "YTD", "1Y", "ALL"]
        
        for i, tf in enumerate(timeframes):
            btn = QPushButton(tf)
            btn.setCheckable(True)
            btn.setObjectName("tab")
            btn.setStyleSheet(f"""
                QPushButton#tab {{
                    background-color: transparent;
                    border: none;
                    border-radius: 4px;
                    padding: 4px 8px;
                    color: {COLORS['text_secondary']};
                    font-size: 12px;
                }}
                QPushButton#tab:hover {{
                    background-color: {COLORS['bg_hover']};
                }}
                QPushButton#tab:checked {{
                    background-color: {COLORS['accent_green_dark']};
                    color: {COLORS['bg_dark']};
                }}
            """)
            if tf == "1W":
                btn.setChecked(True)
            self.timeframe_group.addButton(btn, i)
            timeframe_layout.addWidget(btn)
        
        timeframe_layout.addStretch()
        card_layout.addLayout(timeframe_layout)
        
        layout.addWidget(card)
    
    def update_data(self, total: float, week_change: float, today_change: float, chart_data: list):
        """Update the options income data."""
        self.value_label.setText(f"+{format_currency(total)}")
        
        week_color = COLORS['accent_green'] if week_change >= 0 else COLORS['accent_red']
        self.week_change.setText(f"{format_percent(week_change)} Past week")
        self.week_change.setStyleSheet(f"color: {week_color}; font-size: 12px;")
        
        today_color = COLORS['accent_green'] if today_change >= 0 else COLORS['accent_red']
        self.today_change.setText(f"{format_currency(today_change)} Today")
        self.today_change.setStyleSheet(f"color: {today_color}; font-size: 12px;")
        
        self.chart.set_data(chart_data)
