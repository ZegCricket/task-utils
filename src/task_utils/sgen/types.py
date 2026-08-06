from dataclasses import dataclass
from typing import Annotated, Any, cast

from pydantic import GetCoreSchemaHandler, GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic.types import FilePath, StringConstraints
from pydantic_core import CoreSchema, PydanticCustomError, core_schema

SerialPort = Annotated[
    str, StringConstraints(pattern=r"^(?:COM\d+|/dev/ttyUSB\d+)$", to_lower=False)
]


@dataclass
class FilePathWithExtension:
    extension: Annotated[str, StringConstraints(pattern=r"\.[^.]+$")]

    def __get_pydantic_core_schema__(
        self, source: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return core_schema.with_info_after_validator_function(
            cast(core_schema.WithInfoValidatorFunction, self.validate_extension),
            handler(source),
        )

    def __get_pydantic_json_schema__(
        self, core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        field_schema = handler(core_schema)
        field_schema.update(pattern="\\" + self.extension)
        return field_schema

    def validate_extension(
        self, path: FilePath, _: core_schema.ValidationInfo
    ) -> FilePath:
        if path.suffix == self.extension:
            return path
        else:
            raise PydanticCustomError(
                "path_extension_error", "Path does not have the right extension"
            )
