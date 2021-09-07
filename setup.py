import setuptools
import pathlib

setuptools.setup(
    name="aegis-sim",
    version="2.0.0",
    description="",
    long_description=(pathlib.Path(__file__).parent / "README.md").read_text(),
    long_description_content_type="text/markdown",
    author="Martin Bagic, Will Bradshaw, Arian Sajina and Dario Valenzano",
    author_email="martin.bagic@outlook.com, wbradshaw@age.mpg.de, asajina@age.mpg.de, Dario.Valenzano@age.mpg.de",
    url="https://github.com/valenzano-lab/aegis",
    package_dir={"": "src"},
    packages=[
        "aegis",
        "aegis.modules",
        "aegis.parameters",
    ],
    package_data={
        "aegis": ["parameters/default.yml"],
        "": ["tests/*.py"],
    },
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "aegis = aegis.__main__:main",
        ]
    },
    install_requires=[
        "numpy",
        "pandas",
        "PyYAML",
        "pyarrow",
    ],
    extras_require={
        "dev": [
            "pytest==6.2.4",
        ]
    },
)
