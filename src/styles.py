"""
Stylesheet definitions for Wheel Strategy Tracker.
Dark theme with green accents matching the reference design.
"""

# Color palette
COLORS = {
    'bg_dark': '#0d0d0d',
    'bg_primary': '#1a1a1a',
    'bg_secondary': '#242424',
    'bg_card': '#2a2a2a',
    'bg_hover': '#333333',
    'border': '#3a3a3a',
    'text_primary': '#ffffff',
    'text_secondary': '#a0a0a0',
    'text_muted': '#666666',
    'accent_green': '#4ade80',
    'accent_green_dark': '#22c55e',
    'accent_red': '#ef4444',
    'accent_red_dark': '#dc2626',
    'accent_blue': '#3b82f6',
    'accent_yellow': '#eab308',
}

DARK_STYLESHEET = f"""
/* Main Window */
QMainWindow {{
    background-color: {COLORS['bg_dark']};
}}

QWidget {{
    background-color: transparent;
    color: {COLORS['text_primary']};
    font-family: 'SF Pro Display', 'Segoe UI', 'Helvetica Neue', sans-serif;
    font-size: 13px;
}}

/* Scroll Areas */
QScrollArea {{
    border: none;
    background-color: transparent;
}}

QScrollBar:vertical {{
    background-color: {COLORS['bg_secondary']};
    width: 10px;
    border-radius: 5px;
}}

QScrollBar::handle:vertical {{
    background-color: {COLORS['border']};
    border-radius: 5px;
    min-height: 30px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {COLORS['text_muted']};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

/* Frames / Cards */
QFrame {{
    background-color: {COLORS['bg_secondary']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
}}

QFrame#card {{
    background-color: {COLORS['bg_card']};
    border: 1px solid {COLORS['border']};
    border-radius: 12px;
    padding: 16px;
}}

/* Labels */
QLabel {{
    background-color: transparent;
    border: none;
    padding: 0;
}}

QLabel#title {{
    font-size: 24px;
    font-weight: 600;
    color: {COLORS['text_primary']};
}}

QLabel#subtitle {{
    font-size: 14px;
    color: {COLORS['text_secondary']};
}}

QLabel#value {{
    font-size: 32px;
    font-weight: 700;
    color: {COLORS['text_primary']};
}}

QLabel#value_positive {{
    font-size: 18px;
    font-weight: 600;
    color: {COLORS['accent_green']};
}}

QLabel#value_negative {{
    font-size: 18px;
    font-weight: 600;
    color: {COLORS['accent_red']};
}}

QLabel#section_title {{
    font-size: 16px;
    font-weight: 600;
    color: {COLORS['text_primary']};
}}

/* Buttons */
QPushButton {{
    background-color: {COLORS['bg_card']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    padding: 8px 16px;
    color: {COLORS['text_primary']};
    font-weight: 500;
}}

QPushButton:hover {{
    background-color: {COLORS['bg_hover']};
    border-color: {COLORS['text_muted']};
}}

QPushButton:pressed {{
    background-color: {COLORS['bg_secondary']};
}}

QPushButton#primary {{
    background-color: {COLORS['accent_green_dark']};
    border: none;
    color: {COLORS['bg_dark']};
    font-weight: 600;
}}

QPushButton#primary:hover {{
    background-color: {COLORS['accent_green']};
}}

QPushButton#danger {{
    background-color: {COLORS['accent_red_dark']};
    border: none;
    color: white;
}}

QPushButton#danger:hover {{
    background-color: {COLORS['accent_red']};
}}

QPushButton#tab {{
    background-color: transparent;
    border: none;
    border-radius: 4px;
    padding: 6px 12px;
    color: {COLORS['text_secondary']};
}}

QPushButton#tab:hover {{
    background-color: {COLORS['bg_hover']};
    color: {COLORS['text_primary']};
}}

QPushButton#tab:checked {{
    background-color: {COLORS['accent_green_dark']};
    color: {COLORS['bg_dark']};
}}

/* Input Fields */
QLineEdit {{
    background-color: {COLORS['bg_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    padding: 8px 12px;
    color: {COLORS['text_primary']};
    selection-background-color: {COLORS['accent_green_dark']};
}}

QLineEdit:focus {{
    border-color: {COLORS['accent_green']};
}}

QLineEdit:disabled {{
    background-color: {COLORS['bg_secondary']};
    color: {COLORS['text_muted']};
}}

QTextEdit {{
    background-color: {COLORS['bg_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    padding: 8px;
    color: {COLORS['text_primary']};
}}

/* Combo Box */
QComboBox {{
    background-color: {COLORS['bg_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    padding: 8px 12px;
    color: {COLORS['text_primary']};
    min-width: 100px;
}}

QComboBox:hover {{
    border-color: {COLORS['text_muted']};
}}

QComboBox:focus {{
    border-color: {COLORS['accent_green']};
}}

QComboBox::drop-down {{
    border: none;
    width: 20px;
}}

QComboBox::down-arrow {{
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 6px solid {COLORS['text_secondary']};
    margin-right: 8px;
}}

QComboBox QAbstractItemView {{
    background-color: {COLORS['bg_card']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    selection-background-color: {COLORS['bg_hover']};
    color: {COLORS['text_primary']};
}}

/* Spin Box */
QSpinBox, QDoubleSpinBox {{
    background-color: {COLORS['bg_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    padding: 8px 12px;
    color: {COLORS['text_primary']};
}}

QSpinBox:focus, QDoubleSpinBox:focus {{
    border-color: {COLORS['accent_green']};
}}

/* Date Edit */
QDateEdit {{
    background-color: {COLORS['bg_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    padding: 8px 12px;
    color: {COLORS['text_primary']};
}}

QDateEdit:focus {{
    border-color: {COLORS['accent_green']};
}}

QDateEdit::drop-down {{
    border: none;
    width: 20px;
}}

QCalendarWidget {{
    background-color: {COLORS['bg_card']};
}}

QCalendarWidget QToolButton {{
    color: {COLORS['text_primary']};
    background-color: transparent;
}}

QCalendarWidget QMenu {{
    background-color: {COLORS['bg_card']};
    color: {COLORS['text_primary']};
}}

/* Tables */
QTableWidget {{
    background-color: {COLORS['bg_secondary']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    gridline-color: {COLORS['border']};
}}

QTableWidget::item {{
    padding: 8px;
    border-bottom: 1px solid {COLORS['border']};
}}

QTableWidget::item:selected {{
    background-color: {COLORS['bg_hover']};
}}

QHeaderView::section {{
    background-color: {COLORS['bg_card']};
    color: {COLORS['text_secondary']};
    padding: 10px 8px;
    border: none;
    border-bottom: 1px solid {COLORS['border']};
    font-weight: 600;
}}

/* Tab Widget */
QTabWidget::pane {{
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    background-color: {COLORS['bg_secondary']};
}}

QTabBar::tab {{
    background-color: {COLORS['bg_secondary']};
    color: {COLORS['text_secondary']};
    padding: 8px 16px;
    border: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
}}

QTabBar::tab:selected {{
    background-color: {COLORS['bg_card']};
    color: {COLORS['text_primary']};
}}

QTabBar::tab:hover:!selected {{
    background-color: {COLORS['bg_hover']};
}}

/* Progress Bar */
QProgressBar {{
    background-color: {COLORS['bg_primary']};
    border: none;
    border-radius: 4px;
    height: 8px;
    text-align: center;
}}

QProgressBar::chunk {{
    background-color: {COLORS['accent_green']};
    border-radius: 4px;
}}

/* Tool Tips */
QToolTip {{
    background-color: {COLORS['bg_card']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 4px;
    padding: 4px 8px;
}}

/* Menu */
QMenuBar {{
    background-color: {COLORS['bg_dark']};
    color: {COLORS['text_primary']};
}}

QMenuBar::item:selected {{
    background-color: {COLORS['bg_hover']};
}}

QMenu {{
    background-color: {COLORS['bg_card']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    padding: 4px;
}}

QMenu::item {{
    padding: 8px 24px;
    border-radius: 4px;
}}

QMenu::item:selected {{
    background-color: {COLORS['bg_hover']};
}}

/* Dialogs */
QDialog {{
    background-color: {COLORS['bg_primary']};
}}

QMessageBox {{
    background-color: {COLORS['bg_primary']};
}}

/* Group Box */
QGroupBox {{
    background-color: {COLORS['bg_secondary']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    margin-top: 16px;
    padding-top: 16px;
}}

QGroupBox::title {{
    color: {COLORS['text_secondary']};
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 8px;
    background-color: {COLORS['bg_secondary']};
}}
"""


def get_stylesheet() -> str:
    """Get the application stylesheet."""
    return DARK_STYLESHEET


def format_currency(value: float) -> str:
    """Format a value as currency."""
    if value >= 0:
        return f"${value:,.2f}"
    return f"-${abs(value):,.2f}"


def format_percent(value: float) -> str:
    """Format a value as percentage."""
    sign = "+" if value >= 0 else ""
    return f"{sign}{value:.2f}%"
