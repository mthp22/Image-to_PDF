from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy_garden.filebrowser import FileBrowser
import os
from pathlib import Path


class EnhancedUploadScreen(Screen):
    name = "upload_enhanced"

    def __init__(self, app_instance=None, **kwargs):
        super().__init__(**kwargs)
        self.app = app_instance
        self.selected_files = []
        self.current_directory = str(Path.home())
        self.build_ui()

    def build_ui(self):
        main_layout = BoxLayout(orientation="vertical", padding=15, spacing=15)

        # Header section
        header = Label(
            text="Upload Images",
            font_size="32sp",
            color=(0.2, 0.6, 0.2, 1),
            size_hint=(1, 0.08),
            bold=True,
        )
        main_layout.add_widget(header)

        # Subtitle
        subtitle = Label(
            text="Select images to convert to PDF (JPG, PNG, BMP, TIFF)",
            font_size="12sp",
            color=(0.7, 0.7, 0.7, 1),
            size_hint=(1, 0.05),
        )
        main_layout.add_widget(subtitle)

        # Content area with navigation and file chooser
        content_layout = BoxLayout(orientation="vertical", spacing=10, size_hint=(1, 0.75))

        # Navigation bar
        nav_layout = BoxLayout(size_hint=(1, 0.08), spacing=5, padding=5)

        btn_home = Button(
            text=" Home",
            size_hint=(0.2, 1),
            background_color=(0.15, 0.4, 0.15, 1),
            font_size="11sp",
        )
        btn_home.bind(on_press=self.go_to_home_dir)
        nav_layout.add_widget(btn_home)

        btn_browse = Button(
            text=" Browse",
            size_hint=(0.2, 1),
            background_color=(0.15, 0.4, 0.15, 1),
            font_size="11sp",
        )
        btn_browse.bind(on_press=self.browse_directory)
        nav_layout.add_widget(btn_browse)

        self.path_label = Label(
            text=f" {self.current_directory[:60]}...",
            size_hint=(0.6, 1),
            color=(0.8, 0.8, 0.8, 1),
            font_size="10sp",
        )
        nav_layout.add_widget(self.path_label)

        content_layout.add_widget(nav_layout)

        # File chooser with scroll
        self.file_chooser = FileChooserListView(
            filters=["*.jpg", "*.jpeg", "*.png", "*.bmp", "*.tiff", "*.tif"],
            path=self.current_directory,
            size_hint=(1, 1),
        )
        content_layout.add_widget(self.file_chooser)

        main_layout.add_widget(content_layout)

        # Info section with file list
        info_layout = BoxLayout(orientation="vertical", size_hint=(1, 0.15), spacing=5, padding=5)

        info_label = Label(
            text="Selected Files:",
            font_size="11sp",
            color=(0.2, 0.6, 0.2, 1),
            size_hint=(1, 0.2),
            bold=True,
        )
        info_layout.add_widget(info_label)

        self.info_label = Label(
            text="No files selected",
            color=(0.7, 0.7, 0.7, 1),
            size_hint=(1, 0.8),
            font_size="10sp",
        )
        info_layout.add_widget(self.info_label)

        main_layout.add_widget(info_layout)

        # Action buttons
        buttons_layout = GridLayout(cols=4, spacing=8, size_hint=(1, 0.08), padding=5)

        btn_add = Button(
            text=" Add File",
            background_color=(0.2, 0.6, 0.2, 1),
            font_size="11sp",
        )
        btn_add.bind(on_press=self.add_file)
        buttons_layout.add_widget(btn_add)

        btn_remove = Button(
            text=" Remove",
            background_color=(0.6, 0.3, 0.2, 1),
            font_size="11sp",
        )
        btn_remove.bind(on_press=self.remove_last_file)
        buttons_layout.add_widget(btn_remove)

        btn_clear = Button(
            text=" Clear All",
            background_color=(0.8, 0.2, 0.2, 1),
            font_size="11sp",
        )
        btn_clear.bind(on_press=self.clear_files)
        buttons_layout.add_widget(btn_clear)

        btn_next = Button(
            text="Next",
            background_color=(0.2, 0.5, 0.2, 1),
            font_size="11sp",
        )
        btn_next.bind(on_press=self.go_to_preview)
        buttons_layout.add_widget(btn_next)

        main_layout.add_widget(buttons_layout)

        # Footer
        footer_layout = BoxLayout(size_hint=(1, 0.04), spacing=5)
        btn_back = Button(
            text="Back",
            background_color=(0.4, 0.4, 0.4, 1),
            font_size="10sp",
        )
        btn_back.bind(on_press=self.go_back)
        footer_layout.add_widget(btn_back)

        main_layout.add_widget(footer_layout)

        self.add_widget(main_layout)

    def go_to_home_dir(self, instance):
        """Go to home directory."""
        self.current_directory = str(Path.home())
        self.file_chooser.path = self.current_directory
        self.update_path_label()
        self.show_notification(" Home directory loaded")

    def browse_directory(self, instance):
        """Open directory browser popup."""
        try:
            browser = FileBrowser(
                select_string="Select",
                cancel_string="Cancel",
                filters=["type=dir"],
            )

            popup = Popup(
                title="Select Directory",
                content=browser,
                size_hint=(0.9, 0.9),
            )

            def select_dir(path):
                if path:
                    self.current_directory = path[0] if isinstance(path, list) else path
                    self.file_chooser.path = self.current_directory
                    self.update_path_label()
                    self.show_notification(f" {os.path.basename(self.current_directory)}")
                popup.dismiss()

            browser.bind(on_success=lambda x: select_dir(x.selection))
            browser.bind(on_cancel=lambda x: popup.dismiss())
            popup.open()
        except Exception as e:
            self.show_notification(f"Error: {str(e)}", error=True)

    def update_path_label(self):
        """Update path label."""
        display_path = self.current_directory
        if len(display_path) > 60:
            display_path = "..." + display_path[-57:]
        self.path_label.text = f" {display_path}"

    def add_file(self, instance):
        """Add selected file to list with validation."""
        if not self.file_chooser.selection:
            self.show_notification(" Please select a file", error=True)
            return

        file_path = self.file_chooser.selection[0]

        # Validate file
        if not self._validate_file(file_path):
            return

        if file_path not in self.selected_files:
            self.selected_files.append(file_path)
            self.update_info()
            self.show_notification(f" Added: {os.path.basename(file_path)}")
        else:
            self.show_notification(" File already selected", error=True)

    def _validate_file(self, file_path):
        """Validate selected file."""
        # Check if file exists
        if not os.path.exists(file_path):
            self.show_notification(" File does not exist", error=True)
            return False

        # Check if it's a file (not directory)
        if not os.path.isfile(file_path):
            self.show_notification(" Please select a file, not a directory", error=True)
            return False

        # Check file size
        file_size = os.path.getsize(file_path)
        max_size = 100 * 1024 * 1024  # 100 MB
        if file_size > max_size:
            size_mb = file_size / (1024 * 1024)
            self.show_notification(f" File too large: {size_mb:.1f} MB (max 100 MB)", error=True)
            return False

        # Check file extension
        ext = Path(file_path).suffix.lower().lstrip('.')
        allowed = {'jpg', 'jpeg', 'png', 'bmp', 'tiff', 'tif'}
        if ext not in allowed:
            self.show_notification(f" Unsupported format: .{ext}", error=True)
            return False

        return True

    def remove_last_file(self, instance):
        """Remove last file from selection."""
        if self.selected_files:
            removed = self.selected_files.pop()
            self.update_info()
            self.show_notification(f" Removed: {os.path.basename(removed)}")
        else:
            self.show_notification(" No files to remove", error=True)

    def clear_files(self, instance):
        """Clear all selected files with confirmation."""
        if not self.selected_files:
            self.show_notification(" No files selected", error=True)
            return

        # Confirmation dialog
        popup_content = BoxLayout(orientation="vertical", padding=10, spacing=10)
        popup_content.add_widget(Label(
            text=f"Clear {len(self.selected_files)} selected file(s)?",
            size_hint=(1, 0.4),
        ))

        btn_layout = BoxLayout(size_hint=(1, 0.3), spacing=10)

        btn_yes = Button(text="Yes", background_color=(0.8, 0.2, 0.2, 1))
        btn_layout.add_widget(btn_yes)

        btn_no = Button(text="No", background_color=(0.4, 0.4, 0.4, 1))
        btn_layout.add_widget(btn_no)

        popup_content.add_widget(btn_layout)

        popup = Popup(
            title="Confirm Clear",
            content=popup_content,
            size_hint=(0.7, 0.3),
        )

        btn_yes.bind(on_press=lambda x: self._confirm_clear(popup))
        btn_no.bind(on_press=popup.dismiss)

        popup.open()

    def _confirm_clear(self, popup):
        """Confirm clearing files."""
        self.selected_files = []
        self.update_info()
        self.show_notification(" All files cleared")
        popup.dismiss()

    def update_info(self):
        """Update file count label."""
        count = len(self.selected_files)
        if count == 0:
            self.info_label.text = "No files selected"
        elif count == 1:
            self.info_label.text = f"1 file: {os.path.basename(self.selected_files[0])}"
        else:
            files_str = ", ".join([os.path.basename(f) for f in self.selected_files[:2]])
            if count > 2:
                files_str += f"... +{count-2} more"
            self.info_label.text = f"{count} files: {files_str}"

    def go_to_preview(self, instance):
        """Navigate to preview screen with validation."""
        if not self.selected_files:
            self.show_notification(" Please select at least one image", error=True)
            return

        if self.app and hasattr(self.app, "preview_screen"):
            self.app.preview_screen.set_images(self.selected_files)

        self.manager.current = "preview_enhanced"

    def go_back(self, instance):
        """Navigate back to home."""
        self.manager.current = "home"

    def show_notification(self, message: str, error: bool = False):
        """Show notification message."""
        color = (0.8, 0.2, 0.2, 1) if error else (0.2, 0.6, 0.2, 1)
        popup = Popup(
            title="Message",
            content=Label(text=message, color=color, font_size="12sp"),
            size_hint=(0.8, 0.25),
        )
        popup.open()

        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: popup.dismiss(), 2)
