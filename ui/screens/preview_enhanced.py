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
import os
from pathlib import Path


class EnhancedPreviewScreen(Screen):
    name = "preview_enhanced"

    def __init__(self, app_instance=None, **kwargs):
        super().__init__(**kwargs)
        self.app = app_instance
        self.selected_images = []
        self.image_transforms = {}
        self.build_ui()

    def build_ui(self):
        """Build enhanced preview screen UI."""
        main_layout = BoxLayout(orientation="vertical", padding=15, spacing=15)

        # Header
        header = Label(
            text="Configure & Review",
            font_size="32sp",
            color=(0.2, 0.6, 0.2, 1),
            size_hint=(1, 0.08),
            bold=True,
        )
        main_layout.add_widget(header)

        # Subtitle
        subtitle = Label(
            text="Preview images, set options, and configure PDF settings",
            font_size="11sp",
            color=(0.7, 0.7, 0.7, 1),
            size_hint=(1, 0.04),
        )
        main_layout.add_widget(subtitle)

        # Content: Left (preview) + Right (settings)
        content_layout = BoxLayout(size_hint=(1, 0.76), spacing=15, padding=5)

        # Left: Image preview
        preview_layout = BoxLayout(orientation="vertical", size_hint=(0.55, 1), spacing=8)
        preview_label = Label(
            text=" Image Previews",
            font_size="13sp",
            color=(0.2, 0.6, 0.2, 1),
            size_hint=(1, 0.05),
            bold=True,
        )
        preview_layout.add_widget(preview_label)

        scroll = ScrollView(size_hint=(1, 0.95))
        self.preview_grid = GridLayout(
            cols=1, spacing=8, size_hint_x=1, size_hint_y=None, padding=5
        )
        self.preview_grid.bind(minimum_height=self.preview_grid.setter("height"))
        scroll.add_widget(self.preview_grid)
        preview_layout.add_widget(scroll)

        content_layout.add_widget(preview_layout)

        # Right: Settings panel
        settings_layout = BoxLayout(orientation="vertical", size_hint=(0.45, 1), spacing=10, padding=10)
        settings_layout.canvas.before.clear()
        from kivy.graphics import Color, Rectangle
        with settings_layout.canvas.before:
            Color(0.1, 0.1, 0.1, 1)
            Rectangle(size=settings_layout.size, pos=settings_layout.pos)
        settings_layout.bind(size=self._update_bg, pos=self._update_bg)

        settings_label = Label(
            text=" Settings",
            font_size="13sp",
            color=(0.2, 0.6, 0.2, 1),
            size_hint=(1, 0.05),
            bold=True,
        )
        settings_layout.add_widget(settings_label)

        # Scrollable settings
        scroll_settings = ScrollView(size_hint=(1, 0.95))
        options_layout = GridLayout(cols=1, size_hint_y=None, spacing=8, padding=5)
        options_layout.bind(minimum_height=options_layout.setter("height"))

        # Filename
        options_layout.add_widget(Label(text=" PDF Filename:", font_size="11sp", size_hint_y=None, height=25))
        self.filename_input = TextInput(
            text="combined.pdf",
            multiline=False,
            size_hint=(1, None),
            height=35,
            background_color=(0.25, 0.25, 0.25, 1),
            foreground_color=(0.9, 0.9, 0.9, 1),
            font_size="11sp",
        )
        options_layout.add_widget(self.filename_input)

        # Title
        options_layout.add_widget(Label(text=" Title (optional):", font_size="11sp", size_hint_y=None, height=25))
        self.title_input = TextInput(
            multiline=False,
            size_hint=(1, None),
            height=35,
            background_color=(0.25, 0.25, 0.25, 1),
            foreground_color=(0.9, 0.9, 0.9, 1),
            font_size="11sp",
        )
        options_layout.add_widget(self.title_input)

        # Author
        options_layout.add_widget(Label(text=" Author (optional):", font_size="11sp", size_hint_y=None, height=25))
        self.author_input = TextInput(
            multiline=False,
            size_hint=(1, None),
            height=35,
            background_color=(0.25, 0.25, 0.25, 1),
            foreground_color=(0.9, 0.9, 0.9, 1),
            font_size="11sp",
        )
        options_layout.add_widget(self.author_input)

        # Encryption
        options_layout.add_widget(Label(text=" Security Options:", font_size="11sp", size_hint_y=None, height=25))
        encrypt_layout = BoxLayout(size_hint=(1, None), height=40, spacing=8, padding=5)
        encrypt_layout.add_widget(Label(text="Enable Encryption:", size_hint=(0.6, 1), font_size="11sp"))
        self.encrypt_checkbox = CheckBox(active=False, size_hint=(0.4, 1))
        self.encrypt_checkbox.bind(active=self.on_encrypt_toggle)
        encrypt_layout.add_widget(self.encrypt_checkbox)
        options_layout.add_widget(encrypt_layout)

        # Password (initially hidden)
        options_layout.add_widget(Label(text=" Password:", font_size="11sp", size_hint_y=None, height=25))
        self.password_input = TextInput(
            password=True,
            multiline=False,
            size_hint=(1, None),
            height=35,
            background_color=(0.25, 0.25, 0.25, 1),
            foreground_color=(0.9, 0.9, 0.9, 1),
            font_size="11sp",
            hint_text="Required if encryption enabled",
        )
        self.password_input.disabled = True
        options_layout.add_widget(self.password_input)

        # Individual files
        individual_layout = BoxLayout(size_hint=(1, None), height=40, spacing=8, padding=5)
        individual_layout.add_widget(Label(text="Individual PDFs:", size_hint=(0.6, 1), font_size="11sp"))
        self.individual_checkbox = CheckBox(active=False, size_hint=(0.4, 1))
        individual_layout.add_widget(self.individual_checkbox)
        options_layout.add_widget(individual_layout)

        # Processing options
        options_layout.add_widget(Label(text=" Processing:", font_size="11sp", size_hint_y=None, height=25))

        resize_layout = BoxLayout(size_hint=(1, None), height=40, spacing=8, padding=5)
        resize_layout.add_widget(Label(text="Auto-Resize:", size_hint=(0.6, 1), font_size="11sp"))
        self.resize_checkbox = CheckBox(active=True, size_hint=(0.4, 1))
        resize_layout.add_widget(self.resize_checkbox)
        options_layout.add_widget(resize_layout)

        compress_layout = BoxLayout(size_hint=(1, None), height=40, spacing=8, padding=5)
        compress_layout.add_widget(Label(text="Compression:", size_hint=(0.6, 1), font_size="11sp"))
        self.compress_checkbox = CheckBox(active=True, size_hint=(0.4, 1))
        compress_layout.add_widget(self.compress_checkbox)
        options_layout.add_widget(compress_layout)

        scroll_settings.add_widget(options_layout)
        settings_layout.add_widget(scroll_settings)

        content_layout.add_widget(settings_layout)
        main_layout.add_widget(content_layout)

        # Action buttons
        buttons_layout = GridLayout(cols=2, spacing=10, size_hint=(1, 0.08), padding=10)

        btn_back = Button(
            text="Back",
            background_color=(0.4, 0.4, 0.4, 1),
            font_size="12sp",
        )
        btn_back.bind(on_press=self.go_back)
        buttons_layout.add_widget(btn_back)

        btn_convert = Button(
            text="Convert to PDF",
            background_color=(0.2, 0.6, 0.2, 1),
            font_size="12sp",
        )
        btn_convert.bind(on_press=self.start_conversion)
        buttons_layout.add_widget(btn_convert)

        main_layout.add_widget(buttons_layout)

        self.add_widget(main_layout)

    def _update_bg(self, instance, value):
        """Update background."""
        pass

    def on_encrypt_toggle(self, instance, value):
        """Toggle encryption and password field."""
        self.password_input.disabled = not value
        if value:
            self.password_input.hint_text = "Enter password (min 6 chars)"
        else:
            self.password_input.text = ""

    def set_images(self, image_paths):
        """Set images to preview."""
        self.selected_images = image_paths
        self.image_transforms = {path: {} for path in image_paths}
        self.update_preview()

    def update_preview(self):
        """Update preview grid with thumbnails and edit buttons."""
        self.preview_grid.clear_widgets()

        for idx, image_path in enumerate(self.selected_images):
            img_container = BoxLayout(orientation="vertical", size_hint=(1, None), height=180, spacing=5, padding=5)

            # Image
            try:
                img = KivyImage(source=image_path, size_hint=(1, 0.65))
                img_container.add_widget(img)
            except Exception:
                img_container.add_widget(Label(text="❌Error loading image"))

            # Filename label
            filename_label = Label(
                text=f"({idx+1}/{len(self.selected_images)}) {os.path.basename(image_path)}",
                size_hint=(1, 0.15),
                font_size="9sp",
                color=(0.7, 0.7, 0.7, 1),
            )
            img_container.add_widget(filename_label)

            # Edit button
            edit_btn = Button(
                text=" Rotate/Crop",
                size_hint=(1, 0.2),
                background_color=(0.8, 0.6, 0.2, 1),
                font_size="10sp",
            )
            edit_btn.bind(on_press=lambda x, p=image_path: self.open_edit_dialog(p))
            img_container.add_widget(edit_btn)

            self.preview_grid.add_widget(img_container)

    def open_edit_dialog(self, image_path):
        """Open image editing dialog."""
        dialog_content = BoxLayout(orientation="vertical", spacing=12, padding=15)

        # Title
        dialog_content.add_widget(Label(
            text=f"Edit {os.path.basename(image_path)}",
            font_size="13sp",
            color=(0.2, 0.6, 0.2, 1),
            size_hint=(1, 0.08),
            bold=True,
        ))

        # Rotation section
        dialog_content.add_widget(Label(
            text=" Rotation Angle:",
            font_size="11sp",
            size_hint=(1, 0.08),
            color=(0.2, 0.6, 0.2, 1),
        ))

        rotation_layout = GridLayout(cols=4, size_hint=(1, 0.15), spacing=8)
        for angle in [0, 90, 180, 270]:
            btn = Button(
                text=f"{angle}°",
                background_color=(0.2, 0.5, 0.2, 1),
                font_size="11sp",
            )
            btn.bind(on_press=lambda x, a=angle, p=image_path: self.set_rotation(p, a))
            rotation_layout.add_widget(btn)

        dialog_content.add_widget(rotation_layout)

        # Cropping section
        dialog_content.add_widget(Label(
            text=" Crop (pixels): Left, Top, Right, Bottom",
            font_size="11sp",
            size_hint=(1, 0.08),
            color=(0.2, 0.6, 0.2, 1),
        ))

        crop_layout = GridLayout(cols=4, size_hint=(1, 0.2), spacing=5)
        self.crop_inputs = {}
        for label in ["Left", "Top", "Right", "Bottom"]:
            layout = BoxLayout(orientation="vertical", size_hint=(0.25, 1), spacing=3)
            layout.add_widget(Label(text=label, font_size="10sp", size_hint=(1, 0.3)))
            input_field = TextInput(
                text="0",
                multiline=False,
                input_filter="int",
                size_hint=(1, 0.7),
                background_color=(0.25, 0.25, 0.25, 1),
                foreground_color=(0.9, 0.9, 0.9, 1),
                font_size="10sp",
            )
            self.crop_inputs[label] = input_field
            layout.add_widget(input_field)
            crop_layout.add_widget(layout)

        dialog_content.add_widget(crop_layout)

        # Buttons
        btn_layout = GridLayout(cols=2, size_hint=(1, 0.15), spacing=10, padding=10)

        btn_apply = Button(
            text=" Apply",
            background_color=(0.2, 0.6, 0.2, 1),
            font_size="11sp",
        )
        btn_apply.bind(on_press=lambda x, p=image_path: self.apply_crop(p))
        btn_layout.add_widget(btn_apply)

        btn_close = Button(
            text="✕ Close",
            background_color=(0.4, 0.4, 0.4, 1),
            font_size="11sp",
        )
        btn_layout.add_widget(btn_close)

        dialog_content.add_widget(btn_layout)

        # Create popup
        popup = Popup(
            title="Edit Image",
            content=dialog_content,
            size_hint=(0.85, 0.75),
        )

        btn_close.bind(on_press=popup.dismiss)
        popup.open()

    def set_rotation(self, image_path, angle):
        """Set image rotation."""
        self.image_transforms[image_path]["angle"] = angle
        self.show_notification(f" Rotation: {angle}°")

    def apply_crop(self, image_path):
        """Apply crop settings with validation."""
        try:
            crop_data = {
                "left": int(self.crop_inputs.get("Left", TextInput()).text or 0),
                "top": int(self.crop_inputs.get("Top", TextInput()).text or 0),
                "right": int(self.crop_inputs.get("Right", TextInput()).text or 0),
                "bottom": int(self.crop_inputs.get("Bottom", TextInput()).text or 0),
            }

            # Validate crop values
            if any(v < 0 for v in crop_data.values()):
                self.show_notification("❌ Crop values cannot be negative", error=True)
                return

            if sum(crop_data.values()) > 5000:
                self.show_notification("⚠️ Crop values seem too large", error=True)
                return

            self.image_transforms[image_path]["crop"] = crop_data
            self.show_notification(f" Crop applied: L{crop_data['left']} T{crop_data['top']} R{crop_data['right']} B{crop_data['bottom']}")

        except ValueError:
            self.show_notification("❌ Invalid crop values (must be numbers)", error=True)

    def start_conversion(self, instance):
        """Start PDF conversion with validation."""
        if not self.selected_images:
            self.show_notification("❌ No images selected", error=True)
            return

        # Validate filename
        filename = self.filename_input.text.strip()
        if not filename:
            self.show_notification("❌ Please enter a filename", error=True)
            return

        if not filename.lower().endswith('.pdf'):
            filename += '.pdf'

        if len(filename) > 255:
            self.show_notification("❌ Filename too long (max 255 chars)", error=True)
            return

        # Validate encryption if enabled
        if self.encrypt_checkbox.active:
            password = self.password_input.text
            if not password:
                self.show_notification("❌ Password required for encryption", error=True)
                return
            if len(password) < 6:
                self.show_notification("❌ Password must be at least 6 characters", error=True)
                return

        # Prepare conversion data
        conversion_data = {
            "images": self.selected_images,
            "title": self.title_input.text.strip() or None,
            "author": self.author_input.text.strip() or None,
            "password": self.password_input.text if self.encrypt_checkbox.active else None,
            "encrypt": self.encrypt_checkbox.active,
            "resize": self.resize_checkbox.active,
            "compression": self.compress_checkbox.active,
            "filename": filename,
            "individual_files": self.individual_checkbox.active,
            "transforms": self.image_transforms,
        }

        # Store and navigate
        if self.app:
            self.app.conversion_data = conversion_data

        self.manager.current = "conversion_enhanced"

    def go_back(self, instance):
        """Navigate back to upload."""
        self.manager.current = "upload_enhanced"

    def show_notification(self, message: str, error: bool = False):
        """Show notification message."""
        color = (0.8, 0.2, 0.2, 1) if error else (0.2, 0.6, 0.2, 1)
        popup = Popup(
            title="Message",
            content=Label(text=message, color=color, font_size="11sp"),
            size_hint=(0.8, 0.25),
        )
        popup.open()

        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: popup.dismiss(), 2)
