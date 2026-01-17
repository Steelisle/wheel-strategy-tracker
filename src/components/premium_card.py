"""
Premium tracking card component.
Displays weekly, monthly, YTD premiums and year-end projection.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout
)
from PySide6.QtCore import Qt
from ..styles import COLORS, format_currency


class PremiumCard(QWidget):
    """Card showing premium summary by time period."""
    
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
        card_layout.setSpacing(16)
        
        # Header
        header = QLabel("Premiums")
        header.setStyleSheet(f"""
            font-size: 16px;
            font-weight: 600;
            color: {COLORS['text_primary']};
            background-color: {COLORS['bg_card']};
            padding: 8px 16px;
            border-radius: 16px;
        """)
        header.setAlignment(Qt.AlignCenter)
        header.setFixedWidth(120)
        
        header_layout = QHBoxLayout()
        header_layout.addWidget(header)
        header_layout.addStretch()
        card_layout.addLayout(header_layout)
        
        # Current period section
        self.week_label = self._create_period_row("Week", "$0", "")
        self.month_label = self._create_period_row("January", "$0", "")
        self.ytd_label = self._create_period_row("2026 YTD", "$0", "")
        self.projected_label = self._create_period_row("Year-End Projection:", "$0", "", is_projection=True)
        
        card_layout.addLayout(self.week_label['layout'])
        card_layout.addLayout(self.month_label['layout'])
        card_layout.addLayout(self.ytd_label['layout'])
        card_layout.addLayout(self.projected_label['layout'])
        
        # Separator
        separator = QFrame()
        separator.setFixedHeight(1)
        separator.setStyleSheet(f"background-color: {COLORS['border']};")
        card_layout.addWidget(separator)
        
        # Historical years
        self.year_widgets = {}
        for year in ['2025', '2024', '2023']:
            row = self._create_period_row(year, "$0", "")
            card_layout.addLayout(row['layout'])
            self.year_widgets[year] = row
        
        card_layout.addStretch()
        layout.addWidget(card)
    
    def _create_period_row(self, label: str, value: str, avg_dte: str, is_projection: bool = False) -> dict:
        """Create a row for a time period."""
        layout = QHBoxLayout()
        
        label_widget = QLabel(label)
        label_widget.setStyleSheet(f"""
            color: {COLORS['text_secondary']};
            font-size: 14px;
        """)
        
        value_widget = QLabel(value)
        if is_projection:
            value_widget.setStyleSheet(f"""
                color: {COLORS['text_muted']};
                font-size: 13px;
            """)
        else:
            value_widget.setStyleSheet(f"""
                color: {COLORS['accent_green']};
                font-size: 16px;
                font-weight: 600;
            """)
        value_widget.setAlignment(Qt.AlignRight)
        
        layout.addWidget(label_widget)
        layout.addStretch()
        layout.addWidget(value_widget)
        
        return {'layout': layout, 'label': label_widget, 'value': value_widget}
    
    def update_data(self, data: dict):
        """Update the premium data display."""
        from datetime import date
        import calendar
        
        today = date.today()
        month_name = calendar.month_name[today.month]
        
        # Get week number from data (based on first trade date)
        week_num = data.get('week_number', 0)
        first_trade = data.get('first_trade_date')
        
        # Update current periods
        if week_num > 0:
            self.week_label['label'].setText(f"Week {week_num}")
            self.week_label['value'].setText(format_currency(data.get('week', 0)))
        else:
            self.week_label['label'].setText("Week 1")
            self.week_label['value'].setText("—")
            self.week_label['value'].setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 16px;")
        
        self.month_label['label'].setText(month_name)
        if data.get('month', 0) > 0 or week_num > 0:
            self.month_label['value'].setText(format_currency(data.get('month', 0)))
        else:
            self.month_label['value'].setText("—")
            self.month_label['value'].setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 16px;")
        
        # Use first trade year for YTD label
        display_year = first_trade.year if first_trade else today.year
        self.ytd_label['label'].setText(f"{display_year} YTD")
        if data.get('ytd', 0) > 0 or week_num > 0:
            self.ytd_label['value'].setText(format_currency(data.get('ytd', 0)))
        else:
            self.ytd_label['value'].setText("—")
            self.ytd_label['value'].setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 16px;")
        
        if data.get('projected', 0) > 0:
            self.projected_label['value'].setText(f"Year-End Projection: {format_currency(data.get('projected', 0))}")
        else:
            self.projected_label['value'].setText("Year-End Projection: —")
        
        # Update historical years (hide if no data)
        yearly = data.get('yearly', {})
        for year, widget in self.year_widgets.items():
            amount = yearly.get(year, 0)
            if amount > 0:
                widget['value'].setText(format_currency(amount))
                widget['label'].setVisible(True)
                widget['value'].setVisible(True)
            else:
                widget['label'].setVisible(False)
                widget['value'].setVisible(False)
