from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.progressbar import ProgressBar
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.clock import Clock
from kivy_garden.filebrowser import FileBrowser
import threading
import requests
import json
import os
import shutil
from pathlib import Path


class EnhancedConversionScreen(Screen):
    name = "conversion_enhanced"

    def __init__(self, app_instance=None, **kwargs):
        super().__init__(**kwargs)
        self.app = app_instance
        self.conversion_thread = None
        self.download_directory = str(Path.home() / "Downloads")
        self.pdf_filenames = []
        self.api_url = "http://localhost:8000"
        self.build_ui()

    def build_ui(self):
        self.layout = BoxLayout(orientation="vertical", padding=20, spacing=15)

        # Header
        self.header = Label(
            text="Converting to PDF...",
            font_size="32sp",
            color=(0.2, 0.6, 0.2, 1),
            size_hint=(1, 0.12),
            bold=True,
        )
        self.layout.add_widget(self.header)

        # Status label
        self.status_label = Label(
            text="Preparing images...",
            font_size="13sp",
            color=(0.8, 0.8, 0.8, 1),
            size_hint=(1, 0.08),
        )
        self.layout.add_widget(self.status_label)

        # Progress bar
        self.progress_bar = ProgressBar(
            max=100,
            value=0,
            size_hint=(1, 0.08),
        )
        self.layout.add_widget(self.progress_bar)

        # Details label
        self.details_label = Label(
            text="",
            font_size="11sp",
            color=(0.7, 0.7, 0.7, 1),
            size_hint=(1, 0.2),
        )
        self.layout.add_widget(self.details_label)

        # Download directory selector
        self.dir_layout = BoxLayout(size_hint=(1, 0.12), spacing=10, padding=10)
        self.dir_layout.canvas.before.clear()
        from kivy.graphics import Color, Rectangle
        with self.dir_layout.canvas.before:
            Color(0.15, 0.15, 0.15, 1)
            Rectangle(size=self.dir_layout.size, pos=self.dir_layout.pos)
        self.dir_layout.bind(size=self._update_bg, pos=self._update_bg)

        self.dir_label = Label(
            text=f" Save to: {self.download_directory[:50]}...",
            size_hint=(0.7, 1),
            color=(0.8, 0.8, 0.8, 1),
            font_size="10sp",
        )
        self.dir_layout.add_widget(self.dir_label)

        btn_change_dir = Button(
            text="Change",
            size_hint=(0.3, 1),
            background_color=(0.2, 0.6, 0.2, 1),
            font_size="11sp",
        )
        btn_change_dir.bind(on_press=self.change_download_directory)
        self.dir_layout.add_widget(btn_change_dir)
        self.layout.add_widget(self.dir_layout)

        # Buttons
        self.button_layout = BoxLayout(size_hint=(1, 0.08), spacing=10, padding=10)
        self.cancel_button = Button(
            text="Cancel",
            background_color=(0.8, 0.2, 0.2, 1),
            font_size="11sp",
        )
        self.cancel_button.bind(on_press=self.cancel_conversion)
        self.button_layout.add_widget(self.cancel_button)

        self.layout.add_widget(self.button_layout)

        self.add_widget(self.layout)

    def _update_bg(self, instance, value):
        """Update background."""
        pass

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
        try:
            images = conversion_data.get("images", [])
            title = conversion_data.get("title")
            author = conversion_data.get("author")
            password = conversion_data.get("password")
            encrypt = conversion_data.get("encrypt", False)
            resize = conversion_data.get("resize", True)
            compression = conversion_data.get("compression", True)
            filename = conversion_data.get("filename")
            individual_files = conversion_data.get("individual_files", False)

            api_url = self.app.api_url if hasattr(self.app, "api_url") else "http://localhost:8000"
            self.api_url = api_url

            Clock.schedule_once(
                lambda dt: self.update_status(f"Processing {len(images)} image(s)..."),
                0,
            )

            # Prepare form data
            data = {
                "resize": "true" if resize else "false",
                "compression": "true" if compression else "false",
                "encrypt": "true" if encrypt else "false",
                "individual_files": "true" if individual_files else "false",
            }
            if title:
                data["title"] = title
            if author:
                data["author"] = author
            if password:
                data["password"] = password
            if filename:
                data["filename"] = filename

            Clock.schedule_once(
                lambda dt: self.update_status(" Uploading to server..."),
                0,
            )

            # Make request with proper file handling
            files_list = [
                ("files", (os.path.basename(img), open(img, "rb")))
                for img in images
            ]

            try:
                response = requests.post(
                    f"{api_url}/convert" if not individual_files else f"{api_url}/convert",
                    files=[(f[0], f[1]) for f in files_list],
                    data=data,
                    timeout=300,
                )
            finally:
                # Close files
                for _, (_, f) in files_list:
                    f.close()

            if response.status_code == 200:
                result = response.json()
                pdf_filenames = result.get("file_paths") or [result.get("file_path")]
                # Extract just the filenames if full paths are returned
                if pdf_filenames and isinstance(pdf_filenames, list):
                    pdf_filenames = [os.path.basename(p) if os.path.sep in p else p for p in pdf_filenames]
                else:
                    pdf_filenames = [os.path.basename(pdf_filenames) if os.path.sep in str(pdf_filenames) else str(pdf_filenames)]

                file_sizes = result.get("file_sizes") or [result.get("file_size")]

                Clock.schedule_once(
                    lambda dt: self.conversion_complete(pdf_filenames, file_sizes, api_url),
                    0,
                )
            else:
                error_msg = response.json().get("error_details", "Unknown error")
                Clock.schedule_once(
                    lambda dt: self.conversion_failed(error_msg),
                    0,
                )

        except Exception as e:
            error_msg = str(e)
            Clock.schedule_once(
                lambda dt, msg=error_msg: self.conversion_failed(msg),
                0,
            )

    def update_status(self, message):
        """Update status label."""
        self.status_label.text = message
        self.progress_bar.value = min(100, self.progress_bar.value + 5)

    def conversion_complete(self, pdf_filenames, file_sizes, api_url):
        """Handle successful conversion."""
        self.header.text = " Conversion Complete!"
        self.header.color = (0.2, 0.6, 0.2, 1)
        self.status_label.text = f" Successfully created {len(pdf_filenames)} PDF(s)"

        details = ""
        for filename, size in zip(pdf_filenames, file_sizes):
            file_size_mb = size / (1024 * 1024) if size else 0
            details += f"\n   {filename} ({file_size_mb:.2f} MB)"

        self.details_label.text = f"Files created:{details}"

        self.progress_bar.value = 100

        # Store filenames and API URL for download
        self.pdf_filenames = pdf_filenames
        self.api_url = api_url

        # Update buttons
        self.button_layout.clear_widgets()

        btn_download = Button(
            text="Save to Directory",
            background_color=(0.2, 0.6, 0.2, 1),
            font_size="11sp",
        )
        btn_download.bind(on_press=self.download_and_save)
        self.button_layout.add_widget(btn_download)

        btn_home = Button(
            text="Home",
            background_color=(0.4, 0.4, 0.4, 1),
            font_size="11sp",
        )
        btn_home.bind(on_press=self.go_home)
        self.button_layout.add_widget(btn_home)

        if self.button_layout.parent is None:
            self.layout.add_widget(self.button_layout)

    def download_and_save(self, instance):
        """Download PDFs from API and save to selected directory."""
        def _download_thread():
            try:
                os.makedirs(self.download_directory, exist_ok=True)
                saved_files = []

                for idx, pdf_filename in enumerate(self.pdf_filenames):
                    Clock.schedule_once(
                        lambda dt, i=idx: self.update_status(f" Downloading {i+1}/{len(self.pdf_filenames)}..."),
                        0,
                    )

                    # Download PDF from API
                    download_url = f"{self.api_url}/download/{pdf_filename}"
                    response = requests.get(download_url, timeout=300)

                    if response.status_code == 200:
                        dest_path = os.path.join(self.download_directory, pdf_filename)
                        with open(dest_path, 'wb') as f:
                            f.write(response.content)
                        saved_files.append(dest_path)
                    else:
                        Clock.schedule_once(
                            lambda dt, fn=pdf_filename: self.show_error_popup(f" Failed to download {fn}"),
                            0,
                        )

                if saved_files:
                    message = f" Successfully saved {len(saved_files)} file(s) to:\n{self.download_directory}"
                    Clock.schedule_once(
                        lambda dt: self.show_success_popup(message),
                        0,
                    )
                else:
                    Clock.schedule_once(
                        lambda dt: self.show_error_popup(" No files saved"),
                        0,
                    )
            except Exception as e:
                Clock.schedule_once(
                    lambda dt: self.show_error_popup(f" Save failed: {str(e)}"),
                    0,
                )

        # Run download in thread
        download_thread = threading.Thread(target=_download_thread, daemon=True)
        download_thread.start()

    def change_download_directory(self, instance):
        """Open directory picker for download location."""
        try:
            browser = FileBrowser(
                select_string="Select",
                cancel_string="Cancel",
                filters=["type=dir"],
            )

            popup = Popup(
                title="Select Download Directory",
                content=browser,
                size_hint=(0.9, 0.9),
            )

            def select_dir(selection):
                if selection:
                    self.download_directory = selection[0] if isinstance(selection, list) else selection
                    self.dir_label.text = f" Save to: {self.download_directory[:50]}..."
                    self.show_notification(" Directory updated")
                popup.dismiss()

            browser.bind(on_success=lambda x: select_dir(x.selection))
            browser.bind(on_cancel=lambda x: popup.dismiss())
            popup.open()
        except Exception as e:
            self.show_notification(f" Error: {str(e)}", error=True)

    def conversion_failed(self, error_message):
        """Handle conversion failure."""
        self.header.text = " Conversion Failed"
        self.header.color = (0.8, 0.2, 0.2, 1)
        self.status_label.text = "Error during conversion"
        self.details_label.text = f" {error_message}"

        # Update buttons
        self.button_layout.clear_widgets()

        btn_retry = Button(
            text="Retry",
            background_color=(0.8, 0.6, 0.2, 1),
            font_size="11sp",
        )
        btn_retry.bind(on_press=lambda x: self.start_conversion())
        self.button_layout.add_widget(btn_retry)

        btn_home = Button(
            text="Home",
            background_color=(0.4, 0.4, 0.4, 1),
            font_size="11sp",
        )
        btn_home.bind(on_press=self.go_home)
        self.button_layout.add_widget(btn_home)

    def cancel_conversion(self, instance):
        """Cancel ongoing conversion."""
        self.manager.current = "home"

    def go_home(self, instance):
        """Navigate back to home."""
        self.manager.current = "home"

    def show_notification(self, message: str, error: bool = False):
        """Show notification."""
        color = (0.8, 0.2, 0.2, 1) if error else (0.2, 0.6, 0.2, 1)
        popup = Popup(
            title="Notification",
            content=Label(text=message, color=color, font_size="11sp"),
            size_hint=(0.8, 0.25),
        )
        popup.open()
        Clock.schedule_once(lambda dt: popup.dismiss(), 2)

    def show_success_popup(self, message):
        """Show success popup."""
        popup = Popup(
            title=" Success",
            content=Label(text=message, color=(0.2, 0.6, 0.2, 1), font_size="11sp"),
            size_hint=(0.8, 0.35),
        )
        popup.open()

    def show_error_popup(self, message):
        """Show error popup."""
        popup = Popup(
            title=" Error",
            content=Label(text=message, color=(0.8, 0.2, 0.2, 1), font_size="11sp"),
            size_hint=(0.8, 0.25),
        )
        popup.open()
