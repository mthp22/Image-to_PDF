from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.progressbar import ProgressBar
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.clock import Clock
import threading
import requests
import json
import os


class ConversionScreen(Screen):
    """Conversion/Processing screen."""

    name = "conversion"

    def __init__(self, app_instance=None, **kwargs):
        super().__init__(**kwargs)
        self.app = app_instance
        self.conversion_thread = None
        self.build_ui()

    def build_ui(self):
        """Build conversion screen UI."""
        self.layout = BoxLayout(orientation="vertical", padding=20, spacing=20)

        # Header
        self.header = Label(
            text="Converting to PDF...",
            font_size="28sp",
            color=(0.2, 0.6, 0.2, 1),
            size_hint=(1, 0.2),
        )
        self.layout.add_widget(self.header)

        # Status label
        self.status_label = Label(
            text="Preparing images...",
            font_size="16sp",
            color=(0.8, 0.8, 0.8, 1),
            size_hint=(1, 0.2),
        )
        self.layout.add_widget(self.status_label)

        # Progress bar
        self.progress_bar = ProgressBar(
            max=100,
            value=0,
            size_hint=(1, 0.1),
        )
        self.layout.add_widget(self.progress_bar)

        # Details label
        self.details_label = Label(
            text="",
            font_size="12sp",
            color=(0.7, 0.7, 0.7, 1),
            size_hint=(1, 0.3),
        )
        self.layout.add_widget(self.details_label)

        # Buttons
        self.button_layout = BoxLayout(size_hint=(1, 0.15), spacing=10)
        self.cancel_button = Button(
            text="Cancel",
            background_color=(0.8, 0.2, 0.2, 1),
        )
        self.cancel_button.bind(on_press=self.cancel_conversion)
        self.button_layout.add_widget(self.cancel_button)

        self.layout.add_widget(self.button_layout)

        self.add_widget(self.layout)

    def on_enter(self):
        """Start conversion when entering screen."""
        if self.app and hasattr(self.app, "conversion_data"):
            self.start_conversion()

    def start_conversion(self):
        """Start the conversion process."""
        conversion_data = self.app.conversion_data

        # Start conversion in thread
        self.conversion_thread = threading.Thread(
            target=self._do_conversion,
            args=(conversion_data,),
            daemon=True,
        )
        self.conversion_thread.start()

    def _do_conversion(self, conversion_data):
        """Perform actual conversion (runs in thread)."""
        try:
            images = conversion_data.get("images", [])
            title = conversion_data.get("title")
            author = conversion_data.get("author")
            resize = conversion_data.get("resize", True)
            compression = conversion_data.get("compression", True)

            api_url = self.app.api_url if hasattr(self.app, "api_url") else "http://localhost:8000"

            # Prepare files
            files = []
            for idx, image_path in enumerate(images):
                Clock.schedule_once(
                    lambda dt, i=idx: self.update_status(
                        f"Processing {i+1}/{len(images)}..."
                    ),
                    0,
                )
                
                with open(image_path, "rb") as f:
                    files.append(("files", f.read()))

            # Prepare form data
            data = {
                "resize": "true" if resize else "false",
                "compression": "true" if compression else "false",
            }
            if title:
                data["title"] = title
            if author:
                data["author"] = author

            # Make request
            Clock.schedule_once(
                lambda dt: self.update_status("Uploading to server..."),
                0,
            )

            # Create proper files dict for requests
            files_dict = [("files", (os.path.basename(img), open(img, "rb"))) for img in images]

            response = requests.post(
                f"{api_url}/convert",
                files=files_dict,
                data=data,
            )

            # Close opened files
            for _, (_, f) in files_dict:
                f.close()

            if response.status_code == 200:
                result = response.json()
                pdf_path = result.get("file_path")
                file_size = result.get("file_size")

                Clock.schedule_once(
                    lambda dt: self.conversion_complete(pdf_path, file_size),
                    0,
                )
            else:
                error_msg = response.json().get("error_details", "Unknown error")
                Clock.schedule_once(
                    lambda dt: self.conversion_failed(error_msg),
                    0,
                )

        except Exception as e:
            Clock.schedule_once(
                lambda dt: self.conversion_failed(str(e)),
                0,
            )

    def update_status(self, message):
        """Update status label."""
        self.status_label.text = message
        self.progress_bar.value = min(100, self.progress_bar.value + 10)

    def conversion_complete(self, pdf_path, file_size):
        """Handle successful conversion."""
        self.header.text = "Conversion Complete!"
        self.header.color = (0.2, 0.6, 0.2, 1)
        self.status_label.text = "PDF created successfully"

        file_size_mb = file_size / (1024 * 1024) if file_size else 0
        self.details_label.text = f"File: {os.path.basename(pdf_path)}\nSize: {file_size_mb:.2f} MB"

        self.progress_bar.value = 100

        # Update buttons
        self.button_layout.clear_widgets()

        btn_download = Button(
            text="Download",
            background_color=(0.2, 0.6, 0.2, 1),
        )
        btn_download.bind(on_press=lambda x: self.download_pdf(pdf_path))
        self.button_layout.add_widget(btn_download)

        btn_home = Button(
            text="Home",
            background_color=(0.4, 0.4, 0.4, 1),
        )
        btn_home.bind(on_press=self.go_home)
        self.button_layout.add_widget(btn_home)

    def conversion_failed(self, error_message):
        """Handle conversion failure."""
        self.header.text = "Conversion Failed"
        self.header.color = (0.8, 0.2, 0.2, 1)
        self.status_label.text = "Error during conversion"
        self.details_label.text = f"Error: {error_message}"

        # Update buttons
        self.button_layout.clear_widgets()

        btn_retry = Button(
            text="Retry",
            background_color=(0.8, 0.6, 0.2, 1),
        )
        btn_retry.bind(on_press=lambda x: self.start_conversion())
        self.button_layout.add_widget(btn_retry)

        btn_home = Button(
            text="Home",
            background_color=(0.4, 0.4, 0.4, 1),
        )
        btn_home.bind(on_press=self.go_home)
        self.button_layout.add_widget(btn_home)

    def cancel_conversion(self, instance):
        """Cancel ongoing conversion."""
        if self.conversion_thread and self.conversion_thread.is_alive():
            # Note: Python doesn't have a clean way to kill threads
            # This is a limitation - the thread will continue but we navigate away
            pass
        self.manager.current = "home"

    def download_pdf(self, pdf_path):
        """Download the generated PDF."""
        try:
            if os.path.exists(pdf_path):
                # Copy to downloads folder or show success message
                popup = Popup(
                    title="Success",
                    content=Label(text=f"PDF saved to:\n{pdf_path}"),
                    size_hint=(0.8, 0.4),
                )
                popup.open()
        except Exception as e:
            popup = Popup(
                title="Error",
                content=Label(text=f"Error: {str(e)}"),
                size_hint=(0.8, 0.3),
            )
            popup.open()

    def go_home(self, instance):
        """Navigate back to home."""
        self.manager.current = "home"
