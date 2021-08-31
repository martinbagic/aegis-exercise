import pathlib

from aegis.__main__ import main

generated_path = pathlib.Path(__file__).absolute().parent / "generated"

custom_config_files = (
    path
    for path in generated_path.iterdir()
    if path.name.startswith("test") and path.name.endswith(".yml")
)


for custom_config_file in custom_config_files:
    main(custom_config_file)
