import inspect

from pydantic import BaseModel


def _openapi_response_entry(spec: type) -> dict:
    description = inspect.cleandoc(spec.__doc__ or "").strip()
    if isinstance(spec, type) and issubclass(spec, BaseModel):
        return {"description": description, "model": spec}
    return {
        "description": description,
        "content": {"application/octet-stream": {}},
    }


def openapi_responses(mapping: dict[int, type]) -> dict[int | str, dict]:
    """Собирает словарь ``responses`` для FastAPI из карты ``{код: класс}``."""

    return {code: _openapi_response_entry(spec) for code, spec in mapping.items()}
