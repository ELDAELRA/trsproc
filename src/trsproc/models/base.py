from types import NoneType
from typing import Any, get_args

from pydantic import (
    BaseModel,
    ConfigDict,
    ValidationError,
    ValidationInfo,
    ValidatorFunctionWrapHandler,
    field_validator,
)


class TrsprocModel(BaseModel):
    """A BaseModel that also runs validation when overwriting a property"""

    model_config = ConfigDict(validate_assignment=True)

    @field_validator("*", mode="wrap")
    @classmethod
    def _drop_invalid_if_optional(
        cls,
        value: Any,
        handler: ValidatorFunctionWrapHandler,
        info: ValidationInfo,
    ) -> Any:
        """Tries to validate the field.
        If validation fails but the field is optional, fallback to None."""

        field_annotation = cls.model_fields[info.field_name].annotation  # type: ignore (field_name is always set in field_validators)
        is_optional = any(t is NoneType for t in get_args(field_annotation))
        try:
            return handler(value)
        except ValidationError as e:
            if not is_optional:
                raise
            error_details = e.errors()[0]
            error_message = error_details["msg"]
            print(
                f"Invalid value for optional field {info.field_name} in class {cls.__name__}. \
                {error_message}, but is {type(value)} : {value}. Falling back to None"
            )
            return None
