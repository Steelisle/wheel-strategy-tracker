"""
Trade entry dialog component.
Allows manual entry of CSPs, covered calls, assignments, and closures.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox,
    QDoubleSpinBox, QSpinBox, QDateEdit, QTextEdit, QPushButton,
    QFormLayout, QFrame, QMessageBox, QTabWidget, QWidget
)
from PySide6.QtCore import Qt, QDate, Signal
from ..styles import COLORS
from ..lib.database import get_database


class TradeEntryDialog(QDialog):
    """Dialog for entering new trades."""
    
    trade_added = Signal()
    
    def __init__(self, parent=None, trade_type: str = None):
        super().__init__(parent)
        self.setWindowTitle("Add Trade")
        self.setMinimumWidth(450)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['bg_primary']};
            }}
        """)
        self.setup_ui(trade_type)
    
    def setup_ui(self, initial_type: str = None):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        
        # Title
        title = QLabel("Add New Trade")
        title.setStyleSheet(f"""
            font-size: 20px;
            font-weight: 600;
            color: {COLORS['text_primary']};
        """)
        layout.addWidget(title)
        
        # Tab widget for trade types
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                background-color: {COLORS['bg_secondary']};
            }}
            QTabBar::tab {{
                background-color: {COLORS['bg_secondary']};
                color: {COLORS['text_secondary']};
                padding: 10px 20px;
                border: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }}
            QTabBar::tab:selected {{
                background-color: {COLORS['bg_card']};
                color: {COLORS['text_primary']};
            }}
        """)
        
        # Create tabs for each trade type
        self._create_csp_tab()
        self._create_cc_tab()
        self._create_assignment_tab()
        self._create_close_tab()
        
        layout.addWidget(self.tabs)
        
        # Set initial tab if specified
        if initial_type:
            type_to_index = {'CSP': 0, 'CC': 1, 'ASSIGNMENT': 2, 'CLOSE': 3}
            self.tabs.setCurrentIndex(type_to_index.get(initial_type, 0))
    
    def _create_form_widget(self) -> tuple[QWidget, QFormLayout]:
        """Create a form widget with layout."""
        widget = QWidget()
        form = QFormLayout(widget)
        form.setSpacing(12)
        form.setContentsMargins(16, 16, 16, 16)
        return widget, form
    
    def _create_csp_tab(self):
        """Create Cash-Secured Put entry form."""
        widget, form = self._create_form_widget()
        
        # Ticker
        self.csp_ticker = QLineEdit()
        self.csp_ticker.setPlaceholderText("e.g., AAPL")
        self.csp_ticker.setMaxLength(10)
        form.addRow("Ticker:", self.csp_ticker)
        
        # Strike
        self.csp_strike = QDoubleSpinBox()
        self.csp_strike.setRange(0, 100000)
        self.csp_strike.setDecimals(2)
        self.csp_strike.setPrefix("$")
        form.addRow("Strike Price:", self.csp_strike)
        
        # Expiration
        self.csp_expiration = QDateEdit()
        self.csp_expiration.setDate(QDate.currentDate().addDays(30))
        self.csp_expiration.setCalendarPopup(True)
        form.addRow("Expiration:", self.csp_expiration)
        
        # Premium
        self.csp_premium = QDoubleSpinBox()
        self.csp_premium.setRange(0, 10000)
        self.csp_premium.setDecimals(2)
        self.csp_premium.setPrefix("$")
        self.csp_premium.setSingleStep(0.01)
        form.addRow("Premium (per share):", self.csp_premium)
        
        # Quantity
        self.csp_quantity = QSpinBox()
        self.csp_quantity.setRange(1, 1000)
        self.csp_quantity.setValue(1)
        form.addRow("Contracts:", self.csp_quantity)
        
        # Delta
        self.csp_delta = QDoubleSpinBox()
        self.csp_delta.setRange(-1, 0)
        self.csp_delta.setDecimals(2)
        self.csp_delta.setSingleStep(0.01)
        self.csp_delta.setValue(-0.15)
        form.addRow("Delta (optional):", self.csp_delta)
        
        # Notes
        self.csp_notes = QTextEdit()
        self.csp_notes.setMaximumHeight(60)
        self.csp_notes.setPlaceholderText("Optional notes...")
        form.addRow("Notes:", self.csp_notes)
        
        # Submit button
        submit_btn = QPushButton("Add CSP Trade")
        submit_btn.setObjectName("primary")
        submit_btn.setStyleSheet(f"color: {COLORS['text_primary']};")
        submit_btn.setCursor(Qt.PointingHandCursor)
        submit_btn.clicked.connect(lambda: self._submit_trade('CSP'))
        form.addRow("", submit_btn)
        
        self.tabs.addTab(widget, "Cash-Secured Put")
    
    def _create_cc_tab(self):
        """Create Covered Call entry form."""
        widget, form = self._create_form_widget()
        
        # Ticker
        self.cc_ticker = QLineEdit()
        self.cc_ticker.setPlaceholderText("e.g., AAPL")
        self.cc_ticker.setMaxLength(10)
        form.addRow("Ticker:", self.cc_ticker)
        
        # Strike
        self.cc_strike = QDoubleSpinBox()
        self.cc_strike.setRange(0, 100000)
        self.cc_strike.setDecimals(2)
        self.cc_strike.setPrefix("$")
        form.addRow("Strike Price:", self.cc_strike)
        
        # Expiration
        self.cc_expiration = QDateEdit()
        self.cc_expiration.setDate(QDate.currentDate().addDays(30))
        self.cc_expiration.setCalendarPopup(True)
        form.addRow("Expiration:", self.cc_expiration)
        
        # Premium
        self.cc_premium = QDoubleSpinBox()
        self.cc_premium.setRange(0, 10000)
        self.cc_premium.setDecimals(2)
        self.cc_premium.setPrefix("$")
        self.cc_premium.setSingleStep(0.01)
        form.addRow("Premium (per share):", self.cc_premium)
        
        # Quantity
        self.cc_quantity = QSpinBox()
        self.cc_quantity.setRange(1, 1000)
        self.cc_quantity.setValue(1)
        form.addRow("Contracts:", self.cc_quantity)
        
        # Delta
        self.cc_delta = QDoubleSpinBox()
        self.cc_delta.setRange(0, 1)
        self.cc_delta.setDecimals(2)
        self.cc_delta.setSingleStep(0.01)
        self.cc_delta.setValue(0.15)
        form.addRow("Delta (optional):", self.cc_delta)
        
        # Notes
        self.cc_notes = QTextEdit()
        self.cc_notes.setMaximumHeight(60)
        self.cc_notes.setPlaceholderText("Optional notes...")
        form.addRow("Notes:", self.cc_notes)
        
        # Submit button
        submit_btn = QPushButton("Add Covered Call")
        submit_btn.setObjectName("primary")
        submit_btn.setStyleSheet(f"color: {COLORS['text_primary']};")
        submit_btn.setCursor(Qt.PointingHandCursor)
        submit_btn.clicked.connect(lambda: self._submit_trade('CC'))
        form.addRow("", submit_btn)
        
        self.tabs.addTab(widget, "Covered Call")
    
    def _create_assignment_tab(self):
        """Create Assignment entry form."""
        widget, form = self._create_form_widget()
        
        # Ticker
        self.assign_ticker = QLineEdit()
        self.assign_ticker.setPlaceholderText("e.g., AAPL")
        self.assign_ticker.setMaxLength(10)
        form.addRow("Ticker:", self.assign_ticker)
        
        # Shares
        self.assign_shares = QSpinBox()
        self.assign_shares.setRange(1, 100000)
        self.assign_shares.setValue(100)
        self.assign_shares.setSingleStep(100)
        form.addRow("Shares:", self.assign_shares)
        
        # Cost basis (strike price at assignment)
        self.assign_cost = QDoubleSpinBox()
        self.assign_cost.setRange(0, 100000)
        self.assign_cost.setDecimals(2)
        self.assign_cost.setPrefix("$")
        form.addRow("Cost Basis (per share):", self.assign_cost)
        
        # Assignment type
        self.assign_type = QComboBox()
        self.assign_type.addItems(["PUT Assignment (bought shares)", "CALL Assignment (sold shares)"])
        form.addRow("Type:", self.assign_type)
        
        # Notes
        self.assign_notes = QTextEdit()
        self.assign_notes.setMaximumHeight(60)
        self.assign_notes.setPlaceholderText("Optional notes...")
        form.addRow("Notes:", self.assign_notes)
        
        # Submit button
        submit_btn = QPushButton("Record Assignment")
        submit_btn.setObjectName("primary")
        submit_btn.setStyleSheet(f"color: {COLORS['text_primary']};")
        submit_btn.setCursor(Qt.PointingHandCursor)
        submit_btn.clicked.connect(self._submit_assignment)
        form.addRow("", submit_btn)
        
        self.tabs.addTab(widget, "Assignment")
    
    def _create_close_tab(self):
        """Create Close/Roll position form."""
        widget, form = self._create_form_widget()
        
        info = QLabel("Select an open trade from the positions table and use this to close or roll it.")
        info.setWordWrap(True)
        info.setStyleSheet(f"color: {COLORS['text_secondary']};")
        form.addRow(info)
        
        # Trade ID (would be populated from selection)
        self.close_trade_id = QSpinBox()
        self.close_trade_id.setRange(1, 999999)
        form.addRow("Trade ID:", self.close_trade_id)
        
        # Status
        self.close_status = QComboBox()
        self.close_status.addItems(["CLOSED", "EXPIRED", "ASSIGNED"])
        form.addRow("Status:", self.close_status)
        
        # Submit button
        submit_btn = QPushButton("Close Trade")
        submit_btn.setObjectName("primary")
        submit_btn.setStyleSheet(f"color: {COLORS['text_primary']};")
        submit_btn.setCursor(Qt.PointingHandCursor)
        submit_btn.clicked.connect(self._submit_close)
        form.addRow("", submit_btn)
        
        self.tabs.addTab(widget, "Close/Roll")
    
    def _submit_trade(self, trade_type: str):
        """Submit a CSP or CC trade."""
        db = get_database()
        
        if trade_type == 'CSP':
            ticker = self.csp_ticker.text().strip().upper()
            strike = self.csp_strike.value()
            expiration = self.csp_expiration.date().toString("yyyy-MM-dd")
            premium = self.csp_premium.value()
            quantity = self.csp_quantity.value()
            delta = self.csp_delta.value()
            notes = self.csp_notes.toPlainText().strip()
        else:  # CC
            ticker = self.cc_ticker.text().strip().upper()
            strike = self.cc_strike.value()
            expiration = self.cc_expiration.date().toString("yyyy-MM-dd")
            premium = self.cc_premium.value()
            quantity = self.cc_quantity.value()
            delta = self.cc_delta.value()
            notes = self.cc_notes.toPlainText().strip()
        
        if not ticker:
            QMessageBox.warning(self, "Error", "Please enter a ticker symbol.")
            return
        
        if premium <= 0:
            QMessageBox.warning(self, "Error", "Please enter a premium amount.")
            return
        
        try:
            db.create_trade(
                ticker=ticker,
                trade_type=trade_type,
                strike=strike,
                expiration=expiration,
                premium=premium,
                quantity=quantity,
                delta=delta if delta != 0 else None,
                notes=notes if notes else None
            )
            
            self.trade_added.emit()
            QMessageBox.information(self, "Success", f"{trade_type} trade added successfully!")
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add trade: {str(e)}")
    
    def _submit_assignment(self):
        """Submit an assignment."""
        db = get_database()
        
        ticker = self.assign_ticker.text().strip().upper()
        shares = self.assign_shares.value()
        cost = self.assign_cost.value()
        is_put = self.assign_type.currentIndex() == 0
        notes = self.assign_notes.toPlainText().strip()
        
        if not ticker:
            QMessageBox.warning(self, "Error", "Please enter a ticker symbol.")
            return
        
        try:
            # Get or create position
            position = db.get_or_create_position(ticker)
            
            if is_put:
                # PUT assignment - we bought shares
                new_shares = position.get('shares_owned', 0) + shares
                # Calculate new cost basis
                old_cost = position.get('cost_basis', 0) * position.get('shares_owned', 0)
                new_cost = old_cost + (cost * shares)
                avg_cost = new_cost / new_shares if new_shares > 0 else cost
                
                db.update_position(position['id'], shares=new_shares, cost_basis=avg_cost)
            else:
                # CALL assignment - we sold shares
                new_shares = max(0, position.get('shares_owned', 0) - shares)
                db.update_position(position['id'], shares=new_shares)
            
            # Record the assignment as a trade
            db.create_trade(
                ticker=ticker,
                trade_type='ASSIGNMENT',
                strike=cost,
                premium=0,
                quantity=shares // 100,
                notes=notes if notes else None
            )
            
            self.trade_added.emit()
            QMessageBox.information(self, "Success", "Assignment recorded successfully!")
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to record assignment: {str(e)}")
    
    def _submit_close(self):
        """Close a trade."""
        db = get_database()
        
        trade_id = self.close_trade_id.value()
        status = self.close_status.currentText()
        
        try:
            db.close_trade(trade_id, status)
            self.trade_added.emit()
            QMessageBox.information(self, "Success", "Trade closed successfully!")
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to close trade: {str(e)}")


class QuickTradeButtons(QWidget):
    """Quick action buttons for adding trades."""
    
    trade_added = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Add CSP button
        csp_btn = QPushButton("+ CSP")
        csp_btn.setObjectName("primary")
        csp_btn.setCursor(Qt.PointingHandCursor)
        csp_btn.setStyleSheet(f"""
            QPushButton#primary {{
                background-color: {COLORS['accent_green_dark']};
                border: none;
                color: {COLORS['bg_dark']};
                font-weight: 600;
                padding: 10px 20px;
                border-radius: 6px;
            }}
            QPushButton#primary:hover {{
                background-color: {COLORS['accent_green']};
            }}
        """)
        csp_btn.clicked.connect(lambda: self._open_dialog('CSP'))
        layout.addWidget(csp_btn)
        
        # Add CC button
        cc_btn = QPushButton("+ Covered Call")
        cc_btn.setCursor(Qt.PointingHandCursor)
        cc_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['bg_card']};
                border: 1px solid {COLORS['border']};
                color: {COLORS['text_primary']};
                font-weight: 500;
                padding: 10px 20px;
                border-radius: 6px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['bg_hover']};
                border-color: {COLORS['text_muted']};
            }}
        """)
        cc_btn.clicked.connect(lambda: self._open_dialog('CC'))
        layout.addWidget(cc_btn)
        
        # More options
        more_btn = QPushButton("More...")
        more_btn.setCursor(Qt.PointingHandCursor)
        more_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: none;
                color: {COLORS['text_primary']};
                padding: 10px 16px;
            }}
            QPushButton:hover {{
                color: {COLORS['text_primary']};
            }}
        """)
        more_btn.clicked.connect(lambda: self._open_dialog(None))
        layout.addWidget(more_btn)
        
        layout.addStretch()
    
    def _open_dialog(self, trade_type: str = None):
        """Open the trade entry dialog."""
        dialog = TradeEntryDialog(self, trade_type)
        dialog.trade_added.connect(self.trade_added.emit)
        dialog.exec()
