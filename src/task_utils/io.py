import datetime
from pathlib import Path, WindowsPath
from typing import Type, TypeVar

import yaml
from pydantic import BaseModel

from task_utils._utils import (
    BonsaiSgenSerializers,
    bonsai_sgen,
    export_schema,
    pascal_to_snake_case,
)
from task_utils._yaml import _path_representer, _timedelta_representer,


T = TypeVar("T", bound=BaseModel)


def load_model(cls: Type[T], path: Path) -> T:
    with open(path, "r") as file:
        dict = yaml.safe_load(file)
    return cls(**dict)


def save_model(model: T, path: Path, *, schema: str | None = None) -> None:
    # Convert model to string
    yaml.add_representer(
        datetime.timedelta, _timedelta_representer, Dumper=yaml.SafeDumper
    )
    yaml.add_representer(WindowsPath, _path_representer, Dumper=yaml.SafeDumper)
    text = yaml.safe_dump(
        model.model_dump(exclude_defaults=True),
        default_flow_style=False,
        sort_keys=False,
    )

    # Add header with the schema if it exists
    if schema is not None:
        header = "# yaml-language-server: $schema=" + schema + "\n"
        text = header + text

    # Save file
    with open(path, "w") as file:
        file.write(text)


def generate_schema(cls: Type[T]) -> None:
    json_schema = export_schema(cls)
    schema_name = cls.__name__
    _dashed = pascal_to_snake_case(schema_name).replace("_", "-")
    schema_path = Path(rf"./src/config/schemas/{_dashed}-schema.json")
    with open(schema_path, "w", encoding="utf-8") as f:
        f.write(json_schema)

    bonsai_sgen(
        schema_path=schema_path,
        output_path=Path(r"./src/Extensions"),
        namespace=schema_name,
        serializer=[BonsaiSgenSerializers.JSON, BonsaiSgenSerializers.YAML],
    )
