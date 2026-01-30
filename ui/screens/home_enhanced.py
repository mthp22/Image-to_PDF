from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle
from kivy.core.window import Window
from pathlib import Path


class HomeScreenEnhanced(Screen):
    name = "home"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        """Build home screen UI with improved layout."""
        main_layout = BoxLayout(orientation="vertical", padding=0, spacing=0)

        # Top section (Hero)
        hero_layout = BoxLayout(
            orientation="vertical",
            padding=30,
            spacing=20,
            size_hint=(1, 0.5),
        )

        # Add subtle background color
        with hero_layout.canvas.before:
            Color(0.08, 0.12, 0.08, 1)
            Rectangle(size=hero_layout.size, pos=hero_layout.pos)

        hero_layout.bind(size=self._update_hero_bg, pos=self._update_hero_bg)

        # Logo/Title
        title = Label(
            text="Image to PDF",
            font_size="48sp",
            color=(0.2, 0.8, 0.2, 1),
            size_hint=(1, 0.3),
            bold=True,
        )
        hero_layout.add_widget(title)

        # Subtitle
        subtitle = Label(
            text="Convert your images to professional PDF documents",
            font_size="16sp",
            color=(0.85, 0.85, 0.85, 1),
            size_hint=(1, 0.2),
        )
        hero_layout.add_widget(subtitle)


        main_layout.add_widget(hero_layout)

        # Features section
        features_layout = BoxLayout(
            orientation="vertical",
            padding=25,
            spacing=15,
            size_hint=(1, 0.5),
        )

        features_title = Label(
            text="Features",
            font_size="18sp",
            color=(0.2, 0.7, 0.2, 1),
            size_hint=(1, 0.08),
            bold=True,
        )
        features_layout.add_widget(features_title)

        # Features grid
        features_grid = GridLayout(cols=2, spacing=15, size_hint=(1, 0.7), padding=10)

        features = [
            ("File Upload", "Browse and select images easily"),
            ("Image Editing", "Rotate and crop with precision"),
            ("Secure PDFs", "Encrypt with password protection"),
            ("Fast Processing", "Convert images instantly"),
            ("Batch Convert", "Process multiple images at once"),
            ("Save Anywhere", "Download to any directory"),
        ]

        for title, desc in features:
            feature_card = BoxLayout(
                orientation="vertical",
                padding=10,
                spacing=5,
                size_hint=(0.5, None),
                height=80,
            )

            with feature_card.canvas.before:
                Color(0.12, 0.12, 0.12, 1)
                self.feature_bg = Rectangle(size=feature_card.size, pos=feature_card.pos)

            feature_card.bind(
                size=lambda inst, val: setattr(self.feature_bg, "size", val),
                pos=lambda inst, val: setattr(self.feature_bg, "pos", val),
            )

            title_label = Label(
                text=f"{title}",
                font_size="11sp",
                color=(0.2, 0.7, 0.2, 1),
                size_hint=(1, 0.5),
                bold=True,
            )
            feature_card.add_widget(title_label)

            desc_label = Label(
                text=desc,
                font_size="9sp",
                color=(0.7, 0.7, 0.7, 1),
                size_hint=(1, 0.5),
            )
            feature_card.add_widget(desc_label)

            features_grid.add_widget(feature_card)

        features_layout.add_widget(features_grid)

        # Action button
        btn_layout = BoxLayout(size_hint=(1, 0.15), padding=10, spacing=10)

        btn_start = Button(
            text="Get Started",
            size_hint=(0.7, 1),
            background_color=(0.2, 0.7, 0.2, 1),
            font_size="16sp",
            bold=True,
        )
        btn_start.bind(on_press=self.go_to_upload)
        btn_layout.add_widget(btn_start)

        btn_info = Button(
            text="Info",
            size_hint=(0.3, 1),
            background_color=(0.3, 0.5, 0.3, 1),
            font_size="13sp",
        )
        btn_info.bind(on_press=self.show_info)
        btn_layout.add_widget(btn_info)

        features_layout.add_widget(btn_layout)

        main_layout.add_widget(features_layout)

        self.add_widget(main_layout)

    def _update_hero_bg(self, instance, value):
        """Update hero background."""
        pass

    def go_to_upload(self, instance):
        self.manager.current = "upload_enhanced"

    def show_info(self, instance):
        """Show info popup."""
        from kivy.uix.popup import Popup

        content = BoxLayout(orientation="vertical", padding=15, spacing=10)

        info_text = """Image to PDF Converter

Features:
  • Batch image conversion
  • Image rotation & cropping
  • AES-256 PDF encryption
  • Custom filenames & metadata
  • Fast processing
  • Multi-format support

Supported Formats:
  JPEG, PNG, BMP, TIFF

Security:
  • Password-protected PDFs
  • Secure file handling
  • No data retention"""

        content.add_widget(Label(
            text=info_text,
            font_size="10sp",
            color=(0.8, 0.8, 0.8, 1),
            size_hint=(1, 0.9),
        ))

        btn_close = Button(
            text="Close",
            background_color=(0.4, 0.4, 0.4, 1),
            size_hint=(1, 0.1),
        )

        popup = Popup(
            title="About",
            content=content,
            size_hint=(0.8, 0.6),
        )

        btn_close.bind(on_press=popup.dismiss)
        content.add_widget(btn_close)

        popup.open()