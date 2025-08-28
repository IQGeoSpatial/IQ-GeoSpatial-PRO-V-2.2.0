
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from PyQt5.QtWidgets import QMessageBox
from utils.resource_path import resource_path
import os

class HelpController:
    def __init__(self, view):
        self.view = view

    def send_contact_email(self, user_email, subject, message_body):
        if not all([user_email, subject, message_body]):
            QMessageBox.warning(self.view, "Campos incompletos", "Por favor, rellena todos los campos del formulario.")
            return

        sender_email = "iqgeospatial@gmail.com"  # Tu correo
        app_password = "llvc ubgz oipr izmp"  # Contraseña de aplicación
        recipient_email = "iqgeospatial@gmail.com"

        # Construir correo HTML
        body_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; color: #222;">
            <p>Hola IQ GeoSpatial Technolofy,</p>
            <p>Se ha recibido un nuevo mensaje desde el formulario de contacto de <b>IQ GeoSpatial Technology</b>.</p>
            <h4>Datos del remitente:</h4>
            <table style="border-collapse:collapse;">
                <tr><td><b>Correo electrónico:</b></td><td>{user_email}</td></tr>
                <tr><td><b>Asunto:</b></td><td>{subject}</td></tr>
                <tr><td style="vertical-align:top;"><b>Mensaje:</b></td><td>{message_body}</td></tr>
            </table>
            <p style="margin-top:24px;">Por favor, revise la información y proceda según corresponda.</p>
            <br>
            <div style="text-align:center; width: 100%; max-width: 600px; margin: auto;">
                <img src="cid:logoimg" style="width:100%; height:auto;" alt="Logo IQ GeoSpatial"/>
                <span style="font-size:13px;color:#888;">IQ GeoSpatial Technology</span>
            </div>
        </body>
        </html>
        """

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = f"Contacto desde App: {subject}"

        msg.attach(MIMEText(body_html, 'html'))

        # Adjuntar logo
        logo_path = resource_path(os.path.join("Assets", "Image", "portada.jpeg"))
        if os.path.exists(logo_path):
            with open(logo_path, 'rb') as f:
                logo = MIMEImage(f.read())
                logo.add_header('Content-ID', '<logoimg>')
                msg.attach(logo)

        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(sender_email, app_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
            QMessageBox.information(self.view, "Envío exitoso", "Tu mensaje ha sido enviado correctamente. ¡Gracias por contactarnos!")
            self.view.clear_form()
        except smtplib.SMTPAuthenticationError:
            QMessageBox.critical(self.view, "Error de autenticación", "No se pudo iniciar sesión. Verifica el correo y la contraseña de aplicación en el código.")
        except Exception as e:
            # QMessageBox.critical(self.view, "Error de envío", f"Ocurrió un error al enviar el mensaje: {e}")
            pass
        finally:
            try:
                server.quit()
            except:
                pass

