import datetime
import json
from enum import StrEnum
from pathlib import Path, WindowsPath
from typing import Optional, Type, TypeVar

import yaml
from pydantic import BaseModel

from task_utils.sgen._utils import (
    BonsaiSgenSerializers,
    bonsai_sgen,
    export_schema,
    pascal_to_snake_case,
)
from task_utils.sgen._yaml import _path_representer, _timedelta_representer

T = TypeVar("T", bound=BaseModel)


class FileType(StrEnum):
    """An enum of the allowed file types."""

    YAML = "yaml"
    JSON = "json"


def load_model(cls: Type[T], path: Path, filetype: FileType) -> T:
    """
    Loads a model from a file.

    Parameters
    ----------
    cls : Type[T]
        The class for which an instance will be loaded.
    path : Path
        The path to file containing the model.
    filetype : FileType
        Indicates whether the model is loaded from a YAML or a JSON file.
    Returns
    -------
    T
        The model loaded from the file.
    """
    with open(path, "r") as file:
        match filetype:
            case FileType.YAML:
                dict = yaml.safe_load(file)
            case FileType.JSON:
                dict = json.load(file)
    return cls(**dict)


def save_model(
    model: T, path: Path, filetype: FileType, *, schema: Optional[str] = None
) -> None:
    """
    Saves a model to a file.

    Parameters
    ----------
    model : T
        The model to be saved.
    path : Path
        The path to which the model will be saved.
    filetype : FileType
        Indicates if the model should be saved as a YAML or a JSON file.
    schema : str, optional
        The path or URL to the JSON schema of the model.
    """
    # Convert model to string
    match filetype:
        case FileType.YAML:
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

            with open(path, "w") as file:
                file.write(text)
        case FileType.JSON:
            model_dict = model.model_dump(exclude_defaults=True)
            # Add header with the schema if it exists
            if schema is not None:
                model_dict["$schema"] = schema

            with open(path, "w") as file:
                json.dump(model_dict, file, default=str)


def generate_schema(cls: Type[T]) -> None:
    """
    Generates the schema of a Pydantic class as well as the respective Bonsai extensions. This function requires that the Bonsai.Sgen tool is installed.

    Parameters
    ----------
    cls : Type[T]
        The class for which the JSON schema will be generated.
    """
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
