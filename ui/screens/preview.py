from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import Image as KivyImage
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.checkbox import CheckBox
from kivy.uix.spinner import Spinner
from kivy.core.window import Window


class PreviewScreen(Screen):
    """Preview/Configuration screen."""

    name = "preview"

    def __init__(self, app_instance=None, **kwargs):
        super().__init__(**kwargs)
        self.app = app_instance
        self.selected_images = []
        self.build_ui()

    def build_ui(self):
        """Build preview screen UI."""
        main_layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

        # Header
        header = Label(
            text="Preview & Configure",
            font_size="28sp",
            color=(0.2, 0.6, 0.2, 1),
            size_hint=(1, 0.1),
        )
        main_layout.add_widget(header)

        # Image preview grid
        scroll = ScrollView(size_hint=(1, 0.35))
        self.preview_grid = GridLayout(
            cols=4, spacing=10, size_hint_x=1, size_hint_y=None, padding=10
        )
        self.preview_grid.bind(minimum_height=self.preview_grid.setter("height"))
        scroll.add_widget(self.preview_grid)
        main_layout.add_widget(scroll)

        # Configuration section
        config_layout = BoxLayout(orientation="vertical", size_hint=(1, 0.35), spacing=10)

        # Title
        title_layout = BoxLayout(size_hint=(1, None), height=50, spacing=10)
        title_layout.add_widget(Label(text="Title:", size_hint=(0.3, 1)))
        self.title_input = TextInput(
            text="",
            multiline=False,
            size_hint=(0.7, 1),
            background_color=(0.3, 0.3, 0.3, 1),
        )
        title_layout.add_widget(self.title_input)
        config_layout.add_widget(title_layout)

        # Author
        author_layout = BoxLayout(size_hint=(1, None), height=50, spacing=10)
        author_layout.add_widget(Label(text="Author:", size_hint=(0.3, 1)))
        self.author_input = TextInput(
            text="",
            multiline=False,
            size_hint=(0.7, 1),
            background_color=(0.3, 0.3, 0.3, 1),
        )
        author_layout.add_widget(self.author_input)
        config_layout.add_widget(author_layout)

        # Options
        options_layout = BoxLayout(orientation="vertical", size_hint=(1, None), height=100, spacing=5)

        # Resize checkbox
        resize_layout = BoxLayout(size_hint=(1, 0.5), spacing=10)
        resize_layout.add_widget(Label(text="Auto-resize to fit page", size_hint=(0.7, 1)))
        self.resize_checkbox = CheckBox(active=True, size_hint=(0.3, 1))
        resize_layout.add_widget(self.resize_checkbox)
        options_layout.add_widget(resize_layout)

        # Compression checkbox
        compress_layout = BoxLayout(size_hint=(1, 0.5), spacing=10)
        compress_layout.add_widget(Label(text="Enable compression", size_hint=(0.7, 1)))
        self.compress_checkbox = CheckBox(active=True, size_hint=(0.3, 1))
        compress_layout.add_widget(self.compress_checkbox)
        options_layout.add_widget(compress_layout)

        config_layout.add_widget(options_layout)
        main_layout.add_widget(config_layout)

        # Buttons layout
        buttons_layout = GridLayout(cols=2, spacing=10, size_hint=(1, 0.1), padding=10)

        btn_back = Button(
            text="← Back",
            background_color=(0.4, 0.4, 0.4, 1),
        )
        btn_back.bind(on_press=self.go_back)
        buttons_layout.add_widget(btn_back)

        btn_convert = Button(
            text="Convert →",
            background_color=(0.2, 0.6, 0.2, 1),
        )
        btn_convert.bind(on_press=self.start_conversion)
        buttons_layout.add_widget(btn_convert)

        main_layout.add_widget(buttons_layout)

        self.add_widget(main_layout)

    def set_images(self, image_paths):
        """Set images to preview."""
        self.selected_images = image_paths
        self.update_preview()

    def update_preview(self):
        """Update preview grid with thumbnails."""
        self.preview_grid.clear_widgets()

        for image_path in self.selected_images:
            try:
                img = KivyImage(source=image_path, size_hint=(1, 1))
                self.preview_grid.add_widget(img)
            except Exception as e:
                label = Label(text=f"Error loading\n{image_path}")
                self.preview_grid.add_widget(label)

    def start_conversion(self, instance):
        """Start PDF conversion."""
        if not self.selected_images:
            popup = Popup(
                title="Error",
                content=Label(text="No images selected"),
                size_hint=(0.8, 0.3),
            )
            popup.open()
            return

        # Prepare conversion data
        conversion_data = {
            "images": self.selected_images,
            "title": self.title_input.text or None,
            "author": self.author_input.text or None,
            "resize": self.resize_checkbox.active,
            "compression": self.compress_checkbox.active,
        }

        # Store data and navigate to conversion
        if self.app:
            self.app.conversion_data = conversion_data

        self.manager.current = "conversion"

    def go_back(self, instance):
        """Navigate back to upload."""
        self.manager.current = "upload"
