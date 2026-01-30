from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
import asynckivy
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Import screens - Using enhanced versions
from screens.home_enhanced import HomeScreenEnhanced
from screens.upload_enhanced import EnhancedUploadScreen
from screens.preview_enhanced import EnhancedPreviewScreen
from screens.conversion_enhanced import EnhancedConversionScreen


class ImageToPDFApp(App):
    """Main application class."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "Image to PDF Converter v2.0"
        self.api_url = os.getenv("API_URL", "http://localhost:8000")
        self.conversion_data = None
        self.firebase_token = None
        self.api_key = None

        # Window configuration
        Window.size = (1200, 800)
        Window.minimum_width = 1000
        Window.minimum_height = 700
        
        # Configure window icon and title
        Window.left = 100
        Window.top = 100

    def build(self):
        """Build the application."""
        # Create screen manager
        screen_manager = ScreenManager()

        # Create screens 
        home_screen = HomeScreenEnhanced(name="home")
        upload_screen = EnhancedUploadScreen(app_instance=self, name="upload_enhanced")
        preview_screen = EnhancedPreviewScreen(app_instance=self, name="preview_enhanced")
        conversion_screen = EnhancedConversionScreen(app_instance=self, name="conversion_enhanced")

        # Store references to screens
        self.home_screen = home_screen
        self.upload_screen = upload_screen
        self.preview_screen = preview_screen
        self.conversion_screen = conversion_screen

        # Add screens to manager
        screen_manager.add_widget(home_screen)
        screen_manager.add_widget(upload_screen)
        screen_manager.add_widget(preview_screen)
        screen_manager.add_widget(conversion_screen)

        # Set home as default screen
        screen_manager.current = "home"

        return screen_manager

    def on_start(self):
        """Called when app starts."""
        print(f"=" * 60)
        print(f"Image to PDF Converter")
        print(f"=" * 60)
        print(f"API URL: {self.api_url}")
        print(f"" )

    def on_stop(self):
        """Called when app closes."""
        print(f"\nImage to PDF Converter closed")
        print(f"Thank you for using our app!")

    def set_firebase_token(self, token: str):
        """Set Firebase authentication token."""
        self.firebase_token = token
        print(f"Firebase token set: {token[:20]}...")

    def set_api_key(self, key: str):
        """Set API key for authentication."""
        self.api_key = key
        print(f"API key set: {key[:20]}...")


def main():
    app = ImageToPDFApp()
    app.run()


if __name__ == "__main__":
    main()
