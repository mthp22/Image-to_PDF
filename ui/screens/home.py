from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import Image as KivyImage
from kivy_garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
import matplotlib.pyplot as plt


class HomeScreen(Screen):
    """Home/Welcome screen."""

    name = "home"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        """Build home screen UI."""
        layout = BoxLayout(orientation="vertical", padding=20, spacing=20)

        # Logo/Title
        title = Label(
            text="Image to PDF",
            font_size="48sp",
            color=(0.2, 0.6, 0.2, 1),
            size_hint=(1, 0.2),
            font_name="/home/lmthp22/Dev/img-to-pdf-app/ui/assets/Inter-VariableFont_opsz,wght.ttf" if self._check_font() else "Roboto",
        )
        layout.add_widget(title)

        # Subtitle
        subtitle = Label(
            text="Convert your images to beautiful PDF documents",
            font_size="18sp",
            color=(0.7, 0.7, 0.7, 1),
            size_hint=(1, 0.15),
        )
        layout.add_widget(subtitle)

        # Features list
        features = Label(
            text="""
Features:
• Single or batch image conversion
• Multiple image formats supported
• Automatic image preprocessing
• Metadata support (title, author)
• Fast and efficient conversion
""",
            font_size="14sp",
            color=(0.8, 0.8, 0.8, 1),
            size_hint=(1, 0.4),
            markup=True,
        )
        layout.add_widget(features)

        # Get Started Button
        btn_start = Button(
            text="Get Started",
            size_hint=(1, 0.15),
            background_color=(0.2, 0.6, 0.2, 1),
            font_size="18sp",
        )
        btn_start.bind(on_press=self.go_to_upload)
        layout.add_widget(btn_start)

        self.add_widget(layout)

    def go_to_upload(self, instance):
        """Navigate to enhanced upload screen."""
        self.manager.current = "upload_enhanced"

    @staticmethod
    def _check_font():        
        try:
            from kivy.core.text import LabelBase
            from kivy.resources import resource_find

            font_path = resource_find("/home/lmthp22/Dev/img-to-pdf-app/ui/assets/Inter-VariableFont_opsz,wght.ttf")
            return font_path is not None
        except:
            return False
