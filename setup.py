import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sinolify", # Replace with your own username
    version="0.1",
    author="Szymon Karpiński",
    author_email="hugo@informatykanastart.org.pl",
    description="A small utility for convering Sowa task packages to Sinol.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    python_requires='>=3.8',
    entry_points={
        'console_scripts': [
            'sinolify-convert = sinolify.tools.convert:main'
        ]
    },
)