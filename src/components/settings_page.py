"""
Settings page component.
Manages Polygon.io API configuration and app settings.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox,
    QPushButton, QFrame, QFormLayout, QMessageBox, QGroupBox
)
from PySide6.QtCore import Qt, Signal
from ..styles import COLORS
from ..lib.database import get_database
from ..lib.polygon_api import PolygonAPI, refresh_polygon_api, TIER_FEATURES


class SettingsPage(QWidget):
    """Settings page for app configuration."""
    
    settings_changed = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self._load_settings()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(24)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Title
        title = QLabel("Settings")
        title.setStyleSheet(f"""
            font-size: 28px;
            font-weight: 700;
            color: {COLORS['text_primary']};
        """)
        layout.addWidget(title)
        
        # Polygon.io API Section
        api_group = QGroupBox("Polygon.io API")
        api_group.setStyleSheet(f"""
            QGroupBox {{
                background-color: {COLORS['bg_secondary']};
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
                margin-top: 20px;
                padding: 20px;
                font-size: 16px;
                font-weight: 600;
                color: {COLORS['text_primary']};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 12px;
                background-color: {COLORS['bg_secondary']};
            }}
        """)
        
        api_layout = QFormLayout(api_group)
        api_layout.setSpacing(16)
        api_layout.setContentsMargins(16, 24, 16, 16)
        
        # API Key
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("Enter your Polygon.io API key")
        self.api_key_input.setEchoMode(QLineEdit.Password)
        api_layout.addRow("API Key:", self.api_key_input)
        
        # Show/Hide button
        show_key_btn = QPushButton("Show")
        show_key_btn.setFixedWidth(80)
        show_key_btn.clicked.connect(self._toggle_api_key_visibility)
        self.show_key_btn = show_key_btn
        
        key_layout = QHBoxLayout()
        key_layout.addWidget(self.api_key_input)
        key_layout.addWidget(show_key_btn)
        api_layout.addRow("", key_layout)
        
        # Tier selection
        self.tier_combo = QComboBox()
        self.tier_combo.addItems(["free", "starter", "advanced", "business"])
        self.tier_combo.currentTextChanged.connect(self._update_features_display)
        api_layout.addRow("Subscription Tier:", self.tier_combo)
        
        # Features display
        self.features_label = QLabel()
        self.features_label.setWordWrap(True)
        self.features_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        api_layout.addRow("Available Features:", self.features_label)
        
        # Connection test
        test_layout = QHBoxLayout()
        
        test_btn = QPushButton("Test Connection")
        test_btn.clicked.connect(self._test_connection)
        test_layout.addWidget(test_btn)
        
        self.connection_status = QLabel("Not tested")
        self.connection_status.setStyleSheet(f"color: {COLORS['text_muted']};")
        test_layout.addWidget(self.connection_status)
        test_layout.addStretch()
        
        api_layout.addRow("", test_layout)
        
        layout.addWidget(api_group)
        
        # Tier comparison
        tier_info = QGroupBox("Tier Comparison")
        tier_info.setStyleSheet(f"""
            QGroupBox {{
                background-color: {COLORS['bg_secondary']};
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
                margin-top: 20px;
                padding: 20px;
                font-size: 16px;
                font-weight: 600;
                color: {COLORS['text_primary']};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 12px;
                background-color: {COLORS['bg_secondary']};
            }}
        """)
        
        tier_layout = QVBoxLayout(tier_info)
        tier_layout.setSpacing(12)
        tier_layout.setContentsMargins(16, 24, 16, 16)
        
        tier_data = [
            ("Free", "End-of-day prices, Ticker search", "$0/month"),
            ("Starter", "Delayed quotes, Options chain, Greeks, IV", "~$29/month"),
            ("Advanced", "Real-time quotes, Options chain, Greeks, IV", "~$79/month"),
            ("Business", "All features + Historical options", "~$199/month"),
        ]
        
        for name, features, price in tier_data:
            row = QHBoxLayout()
            
            name_label = QLabel(name)
            name_label.setFixedWidth(100)
            name_label.setStyleSheet(f"color: {COLORS['text_primary']}; font-weight: 600;")
            row.addWidget(name_label)
            
            features_label = QLabel(features)
            features_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
            row.addWidget(features_label, 1)
            
            price_label = QLabel(price)
            price_label.setFixedWidth(100)
            price_label.setAlignment(Qt.AlignRight)
            price_label.setStyleSheet(f"color: {COLORS['accent_green']};")
            row.addWidget(price_label)
            
            tier_layout.addLayout(row)
        
        # Link to Polygon
        link_label = QLabel('<a href="https://polygon.io/pricing" style="color: #3b82f6;">View Polygon.io Pricing →</a>')
        link_label.setOpenExternalLinks(True)
        tier_layout.addWidget(link_label)
        
        layout.addWidget(tier_info)
        
        # Save button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        save_btn = QPushButton("Save Settings")
        save_btn.setObjectName("primary")
        save_btn.setStyleSheet(f"""
            QPushButton#primary {{
                background-color: {COLORS['accent_green_dark']};
                border: none;
                color: {COLORS['bg_dark']};
                font-weight: 600;
                padding: 12px 32px;
                border-radius: 8px;
                font-size: 14px;
            }}
            QPushButton#primary:hover {{
                background-color: {COLORS['accent_green']};
            }}
        """)
        save_btn.clicked.connect(self._save_settings)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
        layout.addStretch()
    
    def _toggle_api_key_visibility(self):
        """Toggle API key visibility."""
        if self.api_key_input.echoMode() == QLineEdit.Password:
            self.api_key_input.setEchoMode(QLineEdit.Normal)
            self.show_key_btn.setText("Hide")
        else:
            self.api_key_input.setEchoMode(QLineEdit.Password)
            self.show_key_btn.setText("Show")
    
    def _update_features_display(self, tier: str):
        """Update the features display for selected tier."""
        features = TIER_FEATURES.get(tier, [])
        feature_names = {
            'endOfDayPrices': 'End-of-day Prices',
            'tickerSearch': 'Ticker Search',
            'delayedQuotes': 'Delayed Quotes (15 min)',
            'realtimeQuotes': 'Real-time Quotes',
            'optionsChain': 'Options Chain',
            'greeks': 'Greeks (Delta, Gamma, Theta, Vega)',
            'iv': 'Implied Volatility',
            'historicalOptions': 'Historical Options Data'
        }
        
        display = ", ".join(feature_names.get(f, f) for f in features)
        self.features_label.setText(display)
    
    def _load_settings(self):
        """Load current settings from database."""
        db = get_database()
        
        api_key = db.get_setting('polygon_api_key') or ""
        tier = db.get_setting('polygon_tier') or "free"
        
        self.api_key_input.setText(api_key)
        self.tier_combo.setCurrentText(tier)
        self._update_features_display(tier)
    
    def _save_settings(self):
        """Save settings to database."""
        db = get_database()
        
        api_key = self.api_key_input.text().strip()
        tier = self.tier_combo.currentText()
        
        db.set_setting('polygon_api_key', api_key)
        db.set_setting('polygon_tier', tier)
        
        # Refresh the API instance
        refresh_polygon_api()
        
        self.settings_changed.emit()
        QMessageBox.information(self, "Success", "Settings saved successfully!")
    
    def _test_connection(self):
        """Test the Polygon.io API connection."""
        api_key = self.api_key_input.text().strip()
        tier = self.tier_combo.currentText()
        
        if not api_key:
            self.connection_status.setText("❌ No API key")
            self.connection_status.setStyleSheet(f"color: {COLORS['accent_red']};")
            return
        
        self.connection_status.setText("Testing...")
        self.connection_status.setStyleSheet(f"color: {COLORS['text_secondary']};")
        
        # Test connection
        api = PolygonAPI(api_key, tier)
        success, message = api.test_connection()
        
        if success:
            self.connection_status.setText(f"✅ {message}")
            self.connection_status.setStyleSheet(f"color: {COLORS['accent_green']};")
        else:
            self.connection_status.setText(f"❌ {message}")
            self.connection_status.setStyleSheet(f"color: {COLORS['accent_red']};")
