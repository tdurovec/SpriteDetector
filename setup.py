from setuptools import setup

setup(
    name="SpriteDetection",
    version="0.1",
    long_description="Spritesheet automatic detection",
    packages=["Spritesheet_cutter"],
    zip_file=False,
    include_package_data=True,
    install_requires=[
            "Flask==2.1.2",
            "opencv-python",
            "Pillow"
    ]
)