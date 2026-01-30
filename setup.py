from setuptools import setup, find_packages

setup(
    name="image-to-pdf",
    version="1.0.0",
    description="Image to PDF conversion service with FastAPI backend and Kivy UI",
    author="LMTHP22",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "fastapi>=0.128.0",
        "uvicorn>=0.40.0",
        "python-multipart>=0.0.22",
        "python-dotenv>=1.2.1",
        "pillow>=12.1.0",
        "img2pdf>=0.6.3",
        "pikepdf>=10.2.0",
        "pydantic>=2.12.5",
        "requests>=2.32.5",
        "pytest>=9.0.2",
        "Kivy>=2.3.1",
        "Kivy-Garden>=0.1.5",
    ],
    entry_points={
        "console_scripts": [
            "img-to-pdf-backend=backend.main:main",
            "img-to-pdf-ui=ui.main:main",
        ],
    },
)
