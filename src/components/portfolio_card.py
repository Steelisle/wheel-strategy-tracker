"""
Portfolio overview card component.
Displays investment philosophy and milestones (configurable).
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout,
    QPushButton, QDialog, QLineEdit, QTextEdit, QFormLayout, QMessageBox,
    QScrollArea, QSpinBox, QDoubleSpinBox
)
from PySide6.QtCore import Qt, Signal
from ..styles import COLORS, format_currency
from ..lib.database import get_database


class EditPortfolioDialog(QDialog):
    """Dialog to edit portfolio information."""
    
    saved = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Portfolio Info")
        self.setMinimumWidth(500)
        self.setMinimumHeight(600)
        self.setStyleSheet(f"QDialog {{ background-color: {COLORS['bg_primary']}; }}")
        self.milestone_widgets = []
        self.setup_ui()
        self._load_data()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        
        # Title
        title = QLabel("Edit Portfolio Information")
        title.setStyleSheet(f"font-size: 20px; font-weight: 600; color: {COLORS['text_primary']};")
        layout.addWidget(title)
        
        # Scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        
        content = QWidget()
        form = QVBoxLayout(content)
        form.setSpacing(16)
        
        # Started investing
        form.addWidget(QLabel("Started Investing:"))
        self.started_input = QLineEdit()
        self.started_input.setPlaceholderText("e.g., May 2015")
        form.addWidget(self.started_input)
        
        # Philosophy
        form.addWidget(QLabel("Investment Philosophy:"))
        self.philosophy_input = QTextEdit()
        self.philosophy_input.setPlaceholderText("Describe your investment approach...")
        self.philosophy_input.setMaximumHeight(120)
        form.addWidget(self.philosophy_input)
        
        # Milestones section
        milestone_header = QHBoxLayout()
        milestone_label = QLabel("Portfolio Milestones:")
        milestone_label.setStyleSheet(f"font-weight: 600; color: {COLORS['text_primary']};")
        milestone_header.addWidget(milestone_label)
        
        add_milestone_btn = QPushButton("+ Add Milestone")
        add_milestone_btn.clicked.connect(self._add_milestone_row)
        milestone_header.addWidget(add_milestone_btn)
        milestone_header.addStretch()
        form.addLayout(milestone_header)
        
        # Milestones container
        self.milestones_layout = QVBoxLayout()
        self.milestones_layout.setSpacing(8)
        form.addLayout(self.milestones_layout)
        
        form.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll, 1)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Save")
        save_btn.setObjectName("primary")
        save_btn.setStyleSheet(f"""
            QPushButton#primary {{
                background-color: {COLORS['accent_green_dark']};
                border: none;
                color: {COLORS['bg_dark']};
                font-weight: 600;
                padding: 10px 24px;
                border-radius: 6px;
            }}
            QPushButton#primary:hover {{
                background-color: {COLORS['accent_green']};
            }}
        """)
        save_btn.clicked.connect(self._save)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
    
    def _add_milestone_row(self, amount: float = 0, date_reached: str = "", time_to_reach: str = ""):
        """Add a milestone input row."""
        row = QHBoxLayout()
        
        amount_input = QDoubleSpinBox()
        amount_input.setRange(0, 100000000)
        amount_input.setPrefix("$")
        amount_input.setDecimals(0)
        amount_input.setValue(amount)
        amount_input.setFixedWidth(150)
        row.addWidget(amount_input)
        
        date_input = QLineEdit()
        date_input.setPlaceholderText("Date (e.g., Jan 2021)")
        date_input.setText(date_reached)
        date_input.setFixedWidth(120)
        row.addWidget(date_input)
        
        time_input = QLineEdit()
        time_input.setPlaceholderText("Time (e.g., 5 Yrs, 8 Mths)")
        time_input.setText(time_to_reach)
        row.addWidget(time_input)
        
        remove_btn = QPushButton("✕")
        remove_btn.setFixedWidth(30)
        remove_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['accent_red']};
                border: none;
                color: white;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['accent_red_dark']};
            }}
        """)
        
        widget_data = {'amount': amount_input, 'date': date_input, 'time': time_input, 'layout': row}
        remove_btn.clicked.connect(lambda: self._remove_milestone_row(widget_data))
        row.addWidget(remove_btn)
        
        self.milestone_widgets.append(widget_data)
        self.milestones_layout.addLayout(row)
    
    def _remove_milestone_row(self, widget_data: dict):
        """Remove a milestone row."""
        if widget_data in self.milestone_widgets:
            self.milestone_widgets.remove(widget_data)
            
            # Clear the layout
            layout = widget_data['layout']
            while layout.count():
                item = layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            
            self.milestones_layout.removeItem(layout)
    
    def _load_data(self):
        """Load existing portfolio data."""
        db = get_database()
        
        info = db.get_portfolio_info()
        self.started_input.setText(info.get('started_investing', ''))
        self.philosophy_input.setPlainText(info.get('philosophy', ''))
        
        milestones = db.get_milestones()
        for m in milestones:
            self._add_milestone_row(
                m.get('amount', 0),
                m.get('date_reached', ''),
                m.get('time_to_reach', '')
            )
    
    def _save(self):
        """Save portfolio data."""
        db = get_database()
        
        # Save portfolio info
        db.save_portfolio_info(
            self.started_input.text().strip(),
            self.philosophy_input.toPlainText().strip(),
            ""  # options_strategy no longer used
        )
        
        # Save milestones
        milestones = []
        for w in self.milestone_widgets:
            amount = w['amount'].value()
            if amount > 0:
                milestones.append({
                    'amount': amount,
                    'date_reached': w['date'].text().strip(),
                    'time_to_reach': w['time'].text().strip()
                })
        db.save_milestones(milestones)
        
        self.saved.emit()
        self.accept()


class PortfolioCard(QWidget):
    """Card showing portfolio overview and milestones."""
    
    data_changed = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.refresh_data()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Main card frame
        self.card = QFrame()
        self.card.setObjectName("card")
        self.card.setStyleSheet(f"""
            QFrame#card {{
                background-color: {COLORS['bg_secondary']};
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
            }}
        """)
        
        self.card_layout = QVBoxLayout(self.card)
        self.card_layout.setSpacing(16)
        
        # Header with edit button
        header_layout = QHBoxLayout()
        
        header = QLabel("Portfolio*")
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
        header_layout.addWidget(header)
        header_layout.addStretch()
        
        edit_btn = QPushButton("✏️")
        edit_btn.setFixedSize(32, 32)
        edit_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['bg_hover']};
            }}
        """)
        edit_btn.clicked.connect(self._open_edit_dialog)
        header_layout.addWidget(edit_btn)
        
        self.card_layout.addLayout(header_layout)
        
        # Content container (will be populated by refresh_data)
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(12)
        self.card_layout.addWidget(self.content_widget)
        
        self.card_layout.addStretch()
        layout.addWidget(self.card)
    
    def _open_edit_dialog(self):
        """Open the edit dialog."""
        dialog = EditPortfolioDialog(self)
        dialog.saved.connect(self.refresh_data)
        dialog.saved.connect(self.data_changed.emit)
        dialog.exec()
    
    def refresh_data(self):
        """Refresh the card with current data."""
        # Clear existing content
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        db = get_database()
        info = db.get_portfolio_info()
        milestones = db.get_milestones()
        
        # Check if there's any data
        has_data = (
            info.get('started_investing') or 
            info.get('philosophy') or 
            milestones
        )
        
        if not has_data:
            # Show placeholder
            placeholder = QLabel("Click ✏️ to add your portfolio information")
            placeholder.setStyleSheet(f"color: {COLORS['text_muted']}; font-style: italic;")
            placeholder.setAlignment(Qt.AlignCenter)
            self.content_layout.addWidget(placeholder)
            return
        
        # Philosophy text
        if info.get('philosophy'):
            philosophy = QLabel(info['philosophy'])
            philosophy.setWordWrap(True)
            philosophy.setStyleSheet(f"""
                color: {COLORS['text_secondary']};
                font-size: 13px;
                line-height: 1.5;
            """)
            self.content_layout.addWidget(philosophy)
        
        # Milestones grid
        if info.get('started_investing') or milestones:
            grid = QGridLayout()
            grid.setSpacing(12)
            
            # Started investing header
            if info.get('started_investing'):
                started_label = QLabel("Started Investing")
                started_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
                grid.addWidget(started_label, 0, 0)
                
                started_value = QLabel(info['started_investing'])
                started_value.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 12px;")
                grid.addWidget(started_value, 0, 1)
            
            # Milestones
            for row, m in enumerate(milestones, start=1):
                amount_label = QLabel(format_currency(m['amount']))
                amount_label.setStyleSheet(f"color: {COLORS['text_primary']}; font-weight: 500;")
                grid.addWidget(amount_label, row, 0)
                
                date_label = QLabel(m.get('date_reached', ''))
                date_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
                grid.addWidget(date_label, row, 1)
                
                time_label = QLabel(m.get('time_to_reach', ''))
                time_label.setStyleSheet(f"color: {COLORS['text_muted']};")
                grid.addWidget(time_label, row, 2)
            
            grid_widget = QWidget()
            grid_widget.setLayout(grid)
            self.content_layout.addWidget(grid_widget)
        
        # Footer note
        footer = QLabel("*Portfolio includes all activity including options.")
        footer.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 11px;")
        self.content_layout.addWidget(footer)
