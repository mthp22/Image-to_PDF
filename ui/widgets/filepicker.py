from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy_garden.filebrowser import FileBrowser
from kivy.core.window import Window
import os


class ImageThumbnail(BoxLayout):
    """Widget to display image thumbnail with remove button."""

    def __init__(self, image_path, on_remove_callback=None, **kwargs):
        super().__init__(orientation="vertical", size_hint=(0.25, 1), **kwargs)
        self.image_path = image_path
        self.on_remove = on_remove_callback

        # Image display
        img = Image(source=image_path, size_hint=(1, 0.85))
        self.add_widget(img)

        # Remove button
        btn_remove = Button(
            text="Remove",
            size_hint=(1, 0.15),
            background_color=(0.8, 0.2, 0.2, 1),
        )
        btn_remove.bind(on_press=self._on_remove)
        self.add_widget(btn_remove)

    def _on_remove(self, instance):
        if self.on_remove:
            self.on_remove(self.image_path)


class ImagePreviewGrid(BoxLayout):
    """Grid layout for image previews."""

    def __init__(self, on_remove_callback=None, **kwargs):
        super().__init__(orientation="vertical", **kwargs)
        self.on_remove = on_remove_callback
        self.selected_images = {}

        # Scroll view for thumbnails
        scroll = ScrollView(size_hint=(1, 0.9))
        self.preview_grid = GridLayout(
            cols=4, spacing=10, size_hint_x=1, size_hint_y=None, padding=10
        )
        self.preview_grid.bind(minimum_height=self.preview_grid.setter("height"))
        scroll.add_widget(self.preview_grid)
        self.add_widget(scroll)

        # Info label
        self.info_label = Label(
            text="No images selected", size_hint=(1, 0.1), color=(0.2, 0.6, 0.2, 1)
        )
        self.add_widget(self.info_label)

    def add_image(self, image_path):
        """Add image to preview grid."""
        if image_path not in self.selected_images:
            thumb = ImageThumbnail(image_path, on_remove_callback=self.remove_image)
            self.selected_images[image_path] = thumb
            self.preview_grid.add_widget(thumb)
            self._update_info()

    def remove_image(self, image_path):
        """Remove image from preview grid."""
        if image_path in self.selected_images:
            thumb = self.selected_images.pop(image_path)
            self.preview_grid.remove_widget(thumb)
            if self.on_remove:
                self.on_remove(image_path)
            self._update_info()

    def clear_all(self):
        """Clear all images."""
        self.selected_images.clear()
        self.preview_grid.clear_widgets()
        self._update_info()

    def get_selected_images(self):
        """Return list of selected image paths."""
        return list(self.selected_images.keys())

    def _update_info(self):
        """Update info label with count."""
        count = len(self.selected_images)
        if count == 0:
            self.info_label.text = "No images selected"
        elif count == 1:
            self.info_label.text = f"1 image selected"
        else:
            self.info_label.text = f"{count} images selected"


class FilePickerBrowser(FileBrowser):
    """Custom file browser for image selection."""

    SUPPORTED_FORMATS = ("jpg", "jpeg", "png", "bmp", "tiff", "tif")

    def __init__(self, on_selection=None, **kwargs):
        super().__init__(**kwargs)
        self.on_selection = on_selection
        self.filters = [lambda f: self._is_image(f)]

    def _is_image(self, filepath):
        """Check if file is supported image format."""
        if os.path.isdir(filepath):
            return True
        ext = os.path.splitext(filepath)[1].lower().lstrip(".")
        return ext in self.SUPPORTED_FORMATS
