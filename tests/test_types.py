from pathlib import Path
from typing import Annotated

import pytest
from pydantic import BaseModel
from pydantic.types import FilePath
from pydantic_core import ValidationError

from task_utils.sgen.types import FilePathWithExtension, SerialPort


class ExampleModel(BaseModel):
    path: Annotated[FilePath, FilePathWithExtension(".py")]
    serial_port: SerialPort


def test_types():
    # TODO: make the first line fail
    # with pytest.raises(ValidationError):
    new_type = Annotated[FilePath, FilePathWithExtension("py")]

    ExampleModel(path=Path("./tests/__init__.py"), serial_port="/dev/ttyUSB92")
    ExampleModel(path=Path("./tests/__init__.py"), serial_port="COM3")

    with pytest.raises(ValidationError):
        ExampleModel(path=Path("./tests/__init__.py"), serial_port="COMx")

    with pytest.raises(ValidationError):
        ExampleModel(path=Path("./tests/__init__.yml"), serial_port="COM3")

    with pytest.raises(ValidationError):
        ExampleModel(path=Path("./tests"), serial_port="COM3")

    json_schema = ExampleModel.model_json_schema()
    assert json_schema["properties"]["path"]["pattern"] == "\\.py"
    assert json_schema["properties"]["path"]["type"] == "string"
    assert (
        json_schema["properties"]["serial_port"]["pattern"]
        == "^(?:COM\\d+|/dev/ttyUSB\\d+)$"
    )
    assert json_schema["properties"]["serial_port"]["type"] == "string"
