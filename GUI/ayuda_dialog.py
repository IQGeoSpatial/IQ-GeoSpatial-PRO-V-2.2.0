import os
from PyQt5.QtWidgets import QDialog, QVBoxLayout
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from utils.resource_path import resource_path

class AyudaDialog(QDialog):
    """
    Un diálogo que muestra un video tutorial embebido desde Google Drive.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Ayuda y Video Tutorial")
        self.setObjectName("AyudaDialog")
        icon_path = resource_path(os.path.join("Assets", "Image", "ayuda.png"))
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        self.setMinimumSize(1300, 800)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.webview = QWebEngineView()
        layout.addWidget(self.webview)

        youtube_video_id = "AZY0F_B5gw0" 
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Video Tutorial</title>
            <style>
                body, html {{ 
                    margin: 0; 
                    padding: 0; 
                    overflow: hidden; 
                    height: 100%; 
                    background-color: #000; 
                }}
                #player {{ 
                    position: absolute; 
                    top: 0; 
                    left: 0; 
                    width: 100%; 
                    height: 100%; 
                }}
            </style>
        </head>
        <body>
            <div id="player"></div>

            <script>
                var tag = document.createElement('script');
                tag.src = "https://www.youtube.com/iframe_api";
                var firstScriptTag = document.getElementsByTagName('script')[0];
                firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);
                var player;
                var qualitySet = false; // Para asegurar que forzamos la calidad solo una vez.

                function onYouTubeIframeAPIReady() {{
                    player = new YT.Player('player', {{
                        height: '100%',
                        width: '100%',
                        videoId: '{youtube_video_id}',
                        playerVars: {{
                            'autoplay': 0, // Desactivamos autoplay para controlar el inicio
                            'controls': 1,
                            'rel': 0
                        }},
                        events: {{
                            'onReady': onPlayerReady,
                            'onStateChange': onPlayerStateChange
                        }}
                    }});
                }}
                function onPlayerReady(event) {{
                    // Cuando el reproductor está listo, iniciamos el video.
                    // La calidad se forzará en onPlayerStateChange.
                    event.target.playVideo();
                }}
                function onPlayerStateChange(event) {{
                    // Cuando el video empieza a reproducirse (estado 1) y aún no hemos forzado la calidad.
                    if (event.data == YT.PlayerState.PLAYING && !qualitySet) {{
                        // Usamos un pequeño retraso para asegurar que la lista de calidades esté disponible.
                        setTimeout(function() {{
                            var availableQualities = event.target.getAvailableQualityLevels();
                            // La API devuelve la mejor calidad primero en el array.
                            if (availableQualities && availableQualities.length > 0) {{
                                // Forzamos la calidad más alta disponible.
                                event.target.setPlaybackQuality(availableQualities[0]);
                            }}
                        }}, 100); // 100ms de espera es suficiente.
                        
                        // Marcamos que ya hemos intentado forzar la calidad para no hacerlo de nuevo
                        // si el usuario pausa y reanuda el video.
                        qualitySet = true;
                    }}
                }}
            </script>
        </body>
        </html>
        """
        self.webview.setHtml(html_content)