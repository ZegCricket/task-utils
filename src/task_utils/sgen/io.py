import datetime
import json
from enum import StrEnum
from os import PathLike
from pathlib import Path, WindowsPath
from typing import TypeVar

import yaml
from pydantic import BaseModel
from yaml.representer import SafeRepresenter

from task_utils.sgen._utils import (
    BonsaiSgenSerializers,
    bonsai_sgen,
    export_schema,
    pascal_to_snake_case,
)
from task_utils.sgen._yaml import _path_representer, _timedelta_representer

T = TypeVar("T", bound=BaseModel)


def load_model(cls: type[T], file_path: str | Path | PathLike) -> T:
    """
    Loads a model from a file.

    Parameters
    ----------
    cls : Type[T]
        The class for which an instance will be loaded.
    file_path : str | Path | PathLike
        The path to file containing the model.
    Returns
    -------
    T
        The model loaded from the file.
    """
    # Convert to Path object
    path = Path(file_path).expanduser().resolve()
    # Verify if file exists
    if not path.exists():
        raise FileNotFoundError(f"Path does not exist: {path}")

    # Open file according to extension
    with open(path, "r") as file:
        match path.suffix:
            case ".yaml" | ".yml":
                dict = yaml.safe_load(file)
            case ".json":
                dict = json.load(file)
            case _:
                raise ValueError(
                    f"This function only supports YAML and JSON files. Files with extension {path.suffix} are not supported"
                )

    return cls(**dict)


def save_model(
    model: T, file_path: str | Path | PathLike, *, schema: str | None = None
) -> None:
    """
    Saves a model to a file.

    Parameters
    ----------
    model : T
        The model to be saved.
    file_path : str | Path | PathLike
        The path to which the model will be saved.
    schema : str, optional
        The path or URL to the JSON schema of the model.
    """
    # Convert file to
    path = Path(file_path).expanduser().resolve()

    # Convert model to string
    match path.suffix:
        case ".yaml" | ".yml":
            yaml.add_representer(
                datetime.timedelta, _timedelta_representer, Dumper=yaml.SafeDumper
            )
            yaml.add_representer(WindowsPath, _path_representer, Dumper=yaml.SafeDumper)
            yaml.add_multi_representer(
                StrEnum,
                SafeRepresenter.represent_str,
                Dumper=yaml.SafeDumper,
            )
            text = yaml.safe_dump(
                model.model_dump(exclude_defaults=True),
                default_flow_style=False,
                sort_keys=False,
            )

            # Add header with the schema if it exists
            if schema is not None:
                header = "# yaml-language-server: $schema=" + schema + "\n"
                text = header + text

            with open(path, "w") as file:
                file.write(text)
        case ".json":
            model_dict = model.model_dump(exclude_defaults=True)
            # Add header with the schema if it exists
            if schema is not None:
                model_dict["$schema"] = schema

            with open(path, "w") as file:
                json.dump(model_dict, file, default=str)
        case _:
            raise ValueError(
                f"This function only supports YAML and JSON files. Files with extension {path.suffix} are not supported"
            )


def generate_schema(
    cls: type[T],
    *,
    schema_path: Path = Path("../src/config/schemas"),
    extension_path: Path = Path("../src/Extensions"),
) -> None:
    """
    Generates the schema of a Pydantic class as well as the respective Bonsai extensions. This function requires that the Bonsai.Sgen tool is installed.

    Parameters
    ----------
    cls : Type[T]
        The class for which the JSON schema will be generated.
    schema_path : Path, optional
        The path to the directory where the JSON schema will be saved.
    extension_path : Path, optional
        The path to the directory where the Bonsai extensions file will be saved.
    """
    json_schema = export_schema(cls)
    schema_name = cls.__name__
    _dashed = pascal_to_snake_case(schema_name).replace("_", "-")
    schema_file = schema_path / f"{_dashed}-schema.json"
    with open(schema_file, "w", encoding="utf-8") as f:
        f.write(json_schema)

    bonsai_sgen(
        schema_path=schema_file,
        output_path=extension_path,
        namespace=schema_name,
        serializer=[BonsaiSgenSerializers.JSON, BonsaiSgenSerializers.YAML],
    )
