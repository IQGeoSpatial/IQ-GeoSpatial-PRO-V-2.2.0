
import os
import webbrowser
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QLineEdit, QTextEdit, QFormLayout, QSpacerItem, QSizePolicy)
from PyQt5.QtGui import QPixmap, QIcon, QFont
from PyQt5.QtCore import Qt, QSize
from utils.resource_path import resource_path
from Controllers.help_controller import HelpController

class HelpView(QWidget):
    def __init__(self):
        super().__init__()
        self.controller = HelpController(self)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Ayuda y Contacto")
        self.setWindowIcon(QIcon(resource_path(os.path.join("Assets", "Image", "ayuda.png"))))
        self.setMinimumSize(500, 750)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowMaximizeButtonHint)


        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 20, 30, 30)
        main_layout.setSpacing(20)

        # --- Título ---
        title_label = QLabel("IQ GeoSpatial Technology")
        title_label.setFont(QFont("Arial", 24, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # --- Logo ---
        logo_label = QLabel()
        logo_path = resource_path(os.path.join("Assets", "Image", "logo_bg.png"))
        pixmap = QPixmap(logo_path)
        logo_label.setPixmap(pixmap.scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(logo_label)

        # --- Párrafo ---
        inspirational_text = (
            "Somos una startup nacida de la pasión por la innovación. Transformamos el mundo a través "
            "de la tecnología geoespacial y los sistemas de información geográfica. "
            "Nuestro compromiso es desarrollar soluciones de vanguardia que conviertan datos complejos "
            "en decisiones claras y estratégicas."
        )
        slogan_label = QLabel(inspirational_text)
        slogan_label.setWordWrap(True)
        slogan_label.setAlignment(Qt.AlignJustify)
        slogan_label.setFont(QFont("Arial", 12))
        slogan_label.setStyleSheet("color: #333333; line-height: 1.5;")
        main_layout.addWidget(slogan_label)

        # --- Síguenos ---
        follow_label = QLabel("Síguenos:")
        follow_label.setFont(QFont("Arial", 14, QFont.Bold))
        follow_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(follow_label)

        # --- Botones de redes sociales ---
        social_layout = QHBoxLayout()
        social_layout.setSpacing(20)
        social_layout.setAlignment(Qt.AlignCenter)

        social_links = {
            resource_path(os.path.join("Assets", "Image", "instagram.png")): "https://www.instagram.com/iqgeospatial",
            resource_path(os.path.join("Assets", "Image", "tik-tok.png")): "https://tiktok.com/@iq.geospatial",
            resource_path(os.path.join("Assets", "Image", "facebbok.png")): "https://www.facebook.com/share/16sHytUGPq/",
            resource_path(os.path.join("Assets", "Image", "whatsapp.png")): "https://wa.me/51900102921",
            resource_path(os.path.join("Assets", "Image", "yuotube.png")): "https://www.youtube.com/@IQGEOSPATIALTECHNOLOGY",
            resource_path(os.path.join("Assets", "Image", "internet.png")): "https://iqgeospatialtechnology.netlify.app/"
        }

        for icon, url in social_links.items():
            btn = self._create_social_button(icon, url)
            social_layout.addWidget(btn)

        main_layout.addLayout(social_layout)
        main_layout.addSpacerItem(QSpacerItem(20, 30, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # --- Formulario de contacto ---
        form_container = QWidget()
        form_layout_outer = QVBoxLayout(form_container)
        form_layout_outer.setContentsMargins(15, 15, 15, 15)
        form_layout_outer.setSpacing(10)
        form_container.setStyleSheet(
            "background-color: #f9f9f9; border: 1px solid #ccc; border-radius: 10px;"
        )

        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        form_layout.setLabelAlignment(Qt.AlignRight)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Tu correo electrónico")
        self.subject_input = QLineEdit()
        self.subject_input.setPlaceholderText("Asunto del mensaje")
        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText("Escribe tu mensaje aquí...")
        self.message_input.setMinimumHeight(120)

        input_style = (
            "QLineEdit, QTextEdit {"
            "border: 2px solid #aaa;"
            "border-radius: 8px;"
            "padding: 6px;"
            "font-size: 12pt;"
            "background-color: #fff;"
            "}"
        )

        self.email_input.setStyleSheet(input_style)
        self.subject_input.setStyleSheet(input_style)
        self.message_input.setStyleSheet(input_style)

        form_layout.addRow("Correo:", self.email_input)
        form_layout.addRow("Asunto:", self.subject_input)
        form_layout.addRow("Mensaje:", self.message_input)

        form_layout_outer.addLayout(form_layout)
        main_layout.addWidget(form_container)

        # --- Botón de envío ---
        self.send_button = QPushButton("Enviar Mensaje")
        self.send_button.setCursor(Qt.PointingHandCursor)
        self.send_button.setFont(QFont("Arial", 12, QFont.Bold))
        self.send_button.setStyleSheet(
            "QPushButton {"
            "background-color: #007ACC; color: white; border-radius: 8px; padding: 10px;}"
            "QPushButton:hover {background-color: #005999;}"
        )
        self.send_button.clicked.connect(self.handle_send_button)
        main_layout.addWidget(self.send_button)

    def _create_social_button(self, icon_path, url):
        button = QPushButton()
        if os.path.exists(icon_path):
            button.setIcon(QIcon(icon_path))
        button.setIconSize(QSize(36, 36))
        button.setFixedSize(48, 48)
        button.setCursor(Qt.PointingHandCursor)
        button.setStyleSheet("background-color: transparent; border: none;")
        button.clicked.connect(lambda: webbrowser.open(url))
        return button

    def handle_send_button(self):
        email = self.email_input.text()
        subject = self.subject_input.text()
        message = self.message_input.toPlainText()
        self.controller.send_contact_email(email, subject, message)

