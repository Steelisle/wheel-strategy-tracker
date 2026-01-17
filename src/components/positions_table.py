"""
Positions table component.
Displays all positions with covered call and put premiums.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
    QTableWidget, QTableWidgetItem, QHeaderView, QProgressBar,
    QAbstractItemView
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from ..styles import COLORS, format_currency


class PremiumBar(QWidget):
    """Custom progress bar for showing premium amount."""
    
    def __init__(self, value: float, max_value: float, parent=None):
        super().__init__(parent)
        self.value = value
        self.max_value = max_value
        self.setup_ui()
    
    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Value label
        value_label = QLabel(format_currency(self.value))
        value_label.setStyleSheet(f"color: {COLORS['accent_green']}; font-weight: 500;")
        value_label.setFixedWidth(80)
        layout.addWidget(value_label)
        
        # Progress bar
        if self.max_value > 0:
            progress = QProgressBar()
            progress.setMaximum(int(self.max_value))
            progress.setValue(int(self.value))
            progress.setTextVisible(False)
            progress.setFixedHeight(8)
            progress.setStyleSheet(f"""
                QProgressBar {{
                    background-color: {COLORS['bg_primary']};
                    border: none;
                    border-radius: 4px;
                }}
                QProgressBar::chunk {{
                    background-color: {COLORS['accent_green']};
                    border-radius: 4px;
                }}
            """)
            layout.addWidget(progress, 1)
        else:
            layout.addStretch()


class PositionsTable(QWidget):
    """Table showing all positions with premium breakdown."""
    
    position_selected = Signal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.positions_data = []
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
        card_layout.setSpacing(0)
        card_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Ticker", "Covered Call", "PUT", "Total Premium"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.table.setColumnWidth(0, 80)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(True)
        
        self.table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {COLORS['bg_secondary']};
                border: none;
                border-radius: 12px;
            }}
            QTableWidget::item {{
                padding: 8px;
                border-bottom: 1px solid {COLORS['border']};
            }}
            QTableWidget::item:selected {{
                background-color: {COLORS['bg_hover']};
            }}
            QTableWidget::item:alternate {{
                background-color: {COLORS['bg_card']};
            }}
            QHeaderView::section {{
                background-color: {COLORS['bg_card']};
                color: {COLORS['text_secondary']};
                padding: 12px 8px;
                border: none;
                border-bottom: 1px solid {COLORS['border']};
                font-weight: 600;
                font-size: 12px;
            }}
        """)
        
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        
        card_layout.addWidget(self.table)
        layout.addWidget(card)
    
    def _on_selection_changed(self):
        """Handle row selection."""
        rows = self.table.selectionModel().selectedRows()
        if rows and self.positions_data:
            row_idx = rows[0].row()
            if row_idx < len(self.positions_data):
                self.position_selected.emit(self.positions_data[row_idx])
    
    def update_data(self, positions: list[dict]):
        """Update the table with position data."""
        self.positions_data = positions
        self.table.setRowCount(len(positions) + 1)  # +1 for total row
        
        # Find max total for progress bar scaling
        max_total = max((p.get('total_premium', 0) for p in positions), default=1) or 1
        
        total_cc = 0
        total_put = 0
        total_premium = 0
        
        for row, pos in enumerate(positions):
            ticker = pos.get('ticker', '')
            cc = pos.get('cc_premium', 0)
            put = pos.get('csp_premium', 0)
            total = pos.get('total_premium', 0)
            
            total_cc += cc
            total_put += put
            total_premium += total
            
            # Ticker
            ticker_item = QTableWidgetItem(ticker)
            ticker_item.setForeground(QColor(COLORS['text_primary']))
            ticker_item.setFlags(ticker_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 0, ticker_item)
            
            # Covered Call
            cc_item = QTableWidgetItem(format_currency(cc) if cc > 0 else "-")
            cc_item.setForeground(QColor(COLORS['accent_green'] if cc > 0 else COLORS['text_muted']))
            cc_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            cc_item.setFlags(cc_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 1, cc_item)
            
            # PUT
            put_item = QTableWidgetItem(format_currency(put) if put > 0 else "-")
            put_item.setForeground(QColor(COLORS['accent_green'] if put > 0 else COLORS['text_muted']))
            put_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            put_item.setFlags(put_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 2, put_item)
            
            # Total Premium with bar
            total_item = QTableWidgetItem(format_currency(total))
            total_item.setForeground(QColor(COLORS['accent_green']))
            total_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            total_item.setFlags(total_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 3, total_item)
        
        # Total row
        total_row = len(positions)
        
        total_label = QTableWidgetItem("TOTAL")
        total_label.setForeground(QColor(COLORS['text_primary']))
        total_label.setFlags(total_label.flags() & ~Qt.ItemIsEditable)
        self.table.setItem(total_row, 0, total_label)
        
        total_cc_item = QTableWidgetItem(format_currency(total_cc))
        total_cc_item.setForeground(QColor(COLORS['accent_green']))
        total_cc_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        total_cc_item.setFlags(total_cc_item.flags() & ~Qt.ItemIsEditable)
        self.table.setItem(total_row, 1, total_cc_item)
        
        total_put_item = QTableWidgetItem(format_currency(total_put))
        total_put_item.setForeground(QColor(COLORS['accent_green']))
        total_put_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        total_put_item.setFlags(total_put_item.flags() & ~Qt.ItemIsEditable)
        self.table.setItem(total_row, 2, total_put_item)
        
        total_premium_item = QTableWidgetItem(format_currency(total_premium))
        total_premium_item.setForeground(QColor(COLORS['accent_green']))
        total_premium_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        total_premium_item.setFlags(total_premium_item.flags() & ~Qt.ItemIsEditable)
        self.table.setItem(total_row, 3, total_premium_item)
