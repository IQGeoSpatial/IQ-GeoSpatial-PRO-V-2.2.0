LIGHT_THEME = """
/* ------------------- GENERAL ------------------- */
QWidget {
    background-color: #f0f0f0;
    color: #333;
    font-family: Segoe UI, Arial, sans-serif;
}
QMessageBox, QDialog {
    background-color: #f0f0f0;
}

/* ------------------- DASHBOARD ------------------- */
QWidget#DashboardWindow {
    background: #f0f0f0;
}
QLabel#HeaderTitle {
    color: #4A90E2;
    font-size: 36px;
    font-weight: bold;
    letter-spacing: 1px;
}
QLabel#HeaderSlogan {
    color: #555;
    font-size: 14px;
    letter-spacing: 0.5px;
}
QToolButton {
    background-color: #ffffff;
    color: #333;
    border: 1px solid #ddd;
    border-radius: 15px;
    padding: 15px;
    font-size: 13px;
    font-weight: bold;
}
QToolButton:hover {
    background-color: #f7f7f7;
    border: 1px solid #3498db;
}
QToolButton:disabled {
    background-color: #f0f0f0;
    color: #aaa;
    border: 1px solid #e0e0e0;
}
QPushButton#DetallesBtn {
    background: #e9e9e9;
    color: #3498db;
    border: 1px solid #ccc;
    border-radius: 5px;
    font-size: 12px;
    font-weight: bold;
    padding: 5px 10px;
    letter-spacing: 1px;
}
QPushButton#DetallesBtn:hover {
    background: #f0f0f0;
    color: #2980b9;
    border-color: #3498db;
}
QPushButton#Infobtn, QPushButton#ThemeBtn {
    color: #555;
    background: transparent;
    border: 1px solid #ccc;
    border-radius: 14px;
    font-size: 13px;
    font-weight: bold;
    min-width: 28px;
    min-height: 28px;
}
QPushButton#Infobtn:hover, QPushButton#ThemeBtn:hover {
    color: #3498db;
    border-color: #3498db;
}

/* ------------------- ESTRUCTURA Y FORMULARIOS ------------------- */
QWidget#EstructuraWindow, QDialog#FormulariosDialog {
    background: #f0f0f0;
}
QLabel#Titulo {
    color: #2c3e50;
    font-size: 24px;
    font-weight: bold;
}
QLineEdit, QComboBox {
    background: #ffffff;
    color: #333;
    border: 1px solid #ccc;
    border-radius: 5px;
    font-size: 12px;
    padding: 8px;
}
QComboBox QAbstractItemView {
    background: #fff;
    color: #333;
    selection-background-color: #3498db;
}
QCheckBox {
    color: #333;
    font-size: 12px;
}
QPushButton {
    background: #3498db;
    color: #fff;
    border: none;
    border-radius: 5px;
    font-size: 12px;
    padding: 8px 16px;
    font-weight: bold;
}
QPushButton:hover {
    background: #2980b9;
}
QPushButton#Secundario {
    background: #16a085; /* Verde azulado */
    color: #ffffff;
    border: none;
}
QPushButton#Secundario:hover {
    background: #1abc9c;
}
QGroupBox {
    border: 1px solid #ccc;
    border-radius: 10px;
    margin-top: 8px;
}
QGroupBox::title {
    color: #3498db;
    font-size: 16px;
    font-weight: bold;
    subcontrol-origin: margin;
    left: 15px;
    padding: 0 5px;
}
QTableWidget {
    background: #ffffff;
    color: #333;
    font-size: 11px;
    border: 1px solid #ccc;
    border-radius: 5px;
    gridline-color: #e0e0e0;
}
QHeaderView::section {
    background: #e9e9e9;
    color: #333;
    font-size: 11px;
    border: 1px solid #ccc;
    padding: 6px;
    font-weight: bold;
}

/* ------------------- EFEMERIDES ------------------- */
QDialog#EfemeridesDialog { background-color: #232526; }
QDialog#EfemeridesDialog QWidget#RightPanel {
    background-color: #f0f0f0;
}
QDialog#EfemeridesDialog QWidget#RightPanel QGroupBox {
    border: 1px solid #ccc;
}
QDialog#EfemeridesDialog QWidget#RightPanel QRadioButton,
QDialog#EfemeridesDialog QWidget#RightPanel QLabel#InfoLabel {
    color: #333;
}
QDialog#EfemeridesDialog QCalendarWidget QWidget { background-color: #f0f0f0; color: #333; }
QDialog#EfemeridesDialog QCalendarWidget QAbstractItemView:enabled { color: #333; selection-background-color: #357ABD; selection-color: #fff; }
QDialog#EfemeridesDialog QCalendarWidget QAbstractItemView:disabled { color: #aaa; }
QDialog#EfemeridesDialog QCalendarWidget QToolButton { color: #333; }
QDialog#EfemeridesDialog QCalendarWidget QMenu { background-color: #fff; color: #333; }
QDialog#EfemeridesDialog QCalendarWidget QSpinBox { color: #333; background-color: #fff; border: 1px solid #ccc; }
QDialog#EfemeridesDialog QCalendarWidget QHeaderView::section { color: #3498db; background-color: #f0f0f0; border: none; font-weight: bold; }

/* ------------------- LICENCIA ------------------- */
QDialog#LicenciaDialog QWidget#Container {
    background-color: rgba(240, 240, 240, 0.85);
    border-radius: 20px;
}
QDialog#LicenciaDialog QLabel { color: #333; background: transparent; }
QDialog#LicenciaDialog QLineEdit { background: #fff; color: #333; border: 1px solid #ccc; }
QDialog#LicenciaDialog QPushButton { background: #3498db; color: #fff; }
QDialog#LicenciaDialog QPushButton:hover { background: #2980b9; }

/* ------------------- PDF CONVERTER DIALOG ------------------- */
QPushButton#SelectSourceButton {
    background-color: #ffffff;
    border: 1px solid #ddd;
    border-radius: 30px;
    font-size: 18px;
    font-weight: bold;
    color: #3498db;
}
QPushButton#SelectSourceButton:hover {
    border: 2px solid #3498db;
    background-color: #f7f7f7;
}

/* ------------------- AYUDA DIALOG ------------------- */
QDialog#AyudaDialog {
    background-color: #f0f0f0;
}
"""

DARK_THEME = """
/* ------------------- GENERAL ------------------- */
QWidget {
    background-color: #2b2b2b;
    color: #e0e0e0;
    font-family: Segoe UI, Arial, sans-serif;
}
QMessageBox, QDialog {
    background-color: #2b2b2b;
}

QWidget#Header {
    background: transparent;
}
QLabel#HeaderTitle, QLabel#HeaderSlogan {
    background: transparent;
}

/* ------------------- DASHBOARD ------------------- */
QWidget#DashboardWindow {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #414345, stop:1 #232526);
}
QLabel#HeaderTitle {
    color: #4A90E2;
    font-size: 36px;
    font-weight: bold;
    letter-spacing: 1px;
}
QLabel#HeaderSlogan {
    color: #b0b0b0;
    font-size: 14px;
    letter-spacing: 0.5px;
}
QToolButton {
    background-color: #2e3133;
    color: #E0E0E0;
    border: 1px solid #444;
    border-radius: 15px;
    padding: 15px;
    font-size: 13px;
    font-weight: bold;
}
QToolButton:hover {
    background-color: #3a3f44;
    border: 1px solid #3498db;
}
QToolButton:disabled {
    background-color: #282a2c;
    color: #666;
    border: 1px solid #333;
}
QPushButton#DetallesBtn {
    background: #3a3f44;
    color: #3498db;
    border: 1px solid #555;
    border-radius: 5px;
    font-size: 12px;
    font-weight: bold;
    padding: 5px 10px;
    letter-spacing: 1px;
}
QPushButton#DetallesBtn:hover {
    background: #4a4f54;
    color: #5dade2;
    border-color: #3498db;
}
QPushButton#Infobtn, QPushButton#ThemeBtn {
    color: #ccc;
    background: transparent;
    border: 1px solid #555;
    border-radius: 14px;
    font-size: 13px;
    font-weight: bold;
    min-width: 28px;
    min-height: 28px;
}
QPushButton#Infobtn:hover, QPushButton#ThemeBtn:hover {
    color: #3498db;
    border-color: #3498db;
}

/* ------------------- ESTRUCTURA Y FORMULARIOS ------------------- */
QWidget#EstructuraWindow, QDialog#FormulariosDialog {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #414345, stop:1 #232526);
}
QLabel#Titulo {
    color: #4A90E2;
    font-size: 24px;
    font-weight: bold;
}
QLineEdit, QComboBox {
    background: #232526;
    color: #fff;
    border: 1px solid #555;
    border-radius: 5px;
    font-size: 12px;
    padding: 8px;
}
QComboBox QAbstractItemView {
    background: #232526;
    color: #fff;
    selection-background-color: #357ABD;
}
QCheckBox {
    color: #ccc;
    font-size: 12px;
}
QPushButton {
    background: #3498db;
    color: #fff;
    border: none;
    border-radius: 5px;
    font-size: 12px;
    padding: 8px 16px;
    font-weight: bold;
}
QPushButton:hover {
    background: #2980b9;
}
QPushButton#Secundario {
    background: #1abc9c; /* Verde azulado claro */
    color: #fff;
}
QPushButton#Secundario:hover {
    background: #2ecc71; /* Un verde más brillante al pasar el mouse */
}
QGroupBox {
    border: 1px solid #555;
    border-radius: 10px;
    margin-top: 8px;
}
QGroupBox::title {
    color: #4A90E2;
    font-size: 16px;
    font-weight: bold;
    subcontrol-origin: margin;
    left: 15px;
    padding: 0 5px;
}
QTableWidget {
    background: #232526;
    color: #fff;
    font-size: 11px;
    border: 1px solid #555;
    border-radius: 5px;
    gridline-color: #357ABD;
}
QHeaderView::section {
    background: #3a3f44;
    color: #fff;
    font-size: 11px;
    border: 1px solid #555;
    padding: 6px;
    font-weight: bold;
}

/* ------------------- EFEMERIDES ------------------- */
QDialog#EfemeridesDialog { background-color: #232526; }
QDialog#EfemeridesDialog QWidget#RightPanel {
    background-color: #2b2b2b;
}
QDialog#EfemeridesDialog QWidget#RightPanel QGroupBox {
    border: 1px solid #555;
}
QDialog#EfemeridesDialog QWidget#RightPanel QRadioButton,
QDialog#EfemeridesDialog QWidget#RightPanel QLabel#InfoLabel {
    color: #e0e0e0;
}
QDialog#EfemeridesDialog QCalendarWidget QWidget { background-color: #2b2b2b; color: #fff; }
QDialog#EfemeridesDialog QCalendarWidget QAbstractItemView:enabled { color: #fff; selection-background-color: #357ABD; selection-color: #fff; }
QDialog#EfemeridesDialog QCalendarWidget QAbstractItemView:disabled { color: #888; }
QDialog#EfemeridesDialog QCalendarWidget QToolButton { color: #fff; }
QDialog#EfemeridesDialog QCalendarWidget QMenu { background-color: #232526; color: #fff; }
QDialog#EfemeridesDialog QCalendarWidget QSpinBox { color: #fff; background-color: #232526; border: 1px solid #555; }
QDialog#EfemeridesDialog QCalendarWidget QHeaderView::section { color: #FFD600; background-color: #2b2b2b; border: none; font-weight: bold; }

/* ------------------- LICENCIA ------------------- */
QDialog#LicenciaDialog QWidget#Container {
    background-color: rgba(35, 37, 38, 0.85);
    border-radius: 20px;
}
QDialog#LicenciaDialog QLabel { color: #E0E0E0; background: transparent; }
QDialog#LicenciaDialog QLineEdit { background: #2e3133; color: #fff; border: 1px solid #555; }
QDialog#LicenciaDialog QPushButton { background: #3498db; color: #fff; }
QDialog#LicenciaDialog QPushButton:hover { background: #2980b9; }

/* ------------------- PDF CONVERTER DIALOG ------------------- */
QPushButton#SelectSourceButton {
    background-color: #3a3f44;
    border: 1px solid #555;
    border-radius: 30px;
    font-size: 18px;
    font-weight: bold;
    color: #4A90E2;
}
QPushButton#SelectSourceButton:hover {
    border: 2px solid #4A90E2;
    background-color: #4a4f54;
}

/* ------------------- AYUDA DIALOG ------------------- */
QDialog#AyudaDialog {
    background-color: #2b2b2b;
}
"""