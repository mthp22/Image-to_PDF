from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
from kivy.uix.relativelayout import RelativeLayout
from kivy_garden.filebrowser import FileBrowser
from kivy.core.window import Window
import os


class UploadScreen(Screen):
    """Upload/File Selection screen."""

    name = "upload"

    def __init__(self, app_instance=None, **kwargs):
        super().__init__(**kwargs)
        self.app = app_instance
        self.selected_files = []
        self.build_ui()

    def build_ui(self):
        """Build upload screen UI."""
        main_layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

        # Header
        header = Label(
            text="Select Images to Convert",
            font_size="28sp",
            color=(0.2, 0.6, 0.2, 1),
            size_hint=(1, 0.1),
        )
        main_layout.add_widget(header)

        # File chooser
        self.file_chooser = FileChooserListView(
            filters=["*.jpg", "*.jpeg", "*.png", "*.bmp", "*.tiff"],
            size_hint=(1, 0.6),
        )
        main_layout.add_widget(self.file_chooser)

        # Selected files info
        self.info_label = Label(
            text="No files selected",
            color=(0.2, 0.6, 0.2, 1),
            size_hint=(1, 0.1),
        )
        main_layout.add_widget(self.info_label)

        # Buttons layout
        buttons_layout = GridLayout(cols=3, spacing=10, size_hint=(1, 0.15), padding=10)

        btn_select = Button(
            text="Add Selected",
            background_color=(0.2, 0.6, 0.2, 1),
        )
        btn_select.bind(on_press=self.add_file)
        buttons_layout.add_widget(btn_select)

        btn_clear = Button(
            text="Clear All",
            background_color=(0.8, 0.2, 0.2, 1),
        )
        btn_clear.bind(on_press=self.clear_files)
        buttons_layout.add_widget(btn_clear)

        btn_next = Button(
            text="Next →",
            background_color=(0.2, 0.5, 0.2, 1),
        )
        btn_next.bind(on_press=self.go_to_preview)
        buttons_layout.add_widget(btn_next)

        main_layout.add_widget(buttons_layout)

        # Back button
        btn_back = Button(
            text="← Back",
            size_hint=(1, 0.08),
            background_color=(0.4, 0.4, 0.4, 1),
        )
        btn_back.bind(on_press=self.go_back)
        main_layout.add_widget(btn_back)

        self.add_widget(main_layout)

    def add_file(self, instance):
        """Add selected file to list."""
        if self.file_chooser.selection:
            file_path = self.file_chooser.selection[0]
            if file_path not in self.selected_files:
                self.selected_files.append(file_path)
                self.update_info()

    def clear_files(self, instance):
        """Clear all selected files."""
        self.selected_files = []
        self.update_info()

    def update_info(self):
        """Update file count label."""
        count = len(self.selected_files)
        if count == 0:
            self.info_label.text = "No files selected"
        elif count == 1:
            self.info_label.text = f"1 file selected"
        else:
            self.info_label.text = f"{count} files selected"

    def go_to_preview(self, instance):
        """Navigate to preview screen."""
        if self.selected_files:
            # Pass files to preview screen
            if self.app and hasattr(self.app, "preview_screen"):
                self.app.preview_screen.set_images(self.selected_files)
            self.manager.current = "preview"
        else:
            # Show error
            popup = Popup(
                title="Error",
                content=Label(text="Please select at least one image"),
                size_hint=(0.8, 0.3),
            )
            popup.open()

    def go_back(self, instance):
        """Navigate back to home."""
        self.manager.current = "home"
