class ValidationExceptionHandler:
    """
    Handles RequestValidationError and returns errors in Laravel style:
    {
        "message": "The email field is required. (and 1 more error)",
        "errors": {
            "email": ["The email field is required."],
            "password": ["The password field is required."]
        }
    }
    """

    _LOCATION_PREFIXES = {"body", "query", "path", "header", "cookie"}

    def _loc_to_field(self, loc: tuple) -> str:
        parts = loc[1:] if loc and loc[0] in self._LOCATION_PREFIXES else loc
        return ".".join(str(p) for p in parts)

    def _format_message(self, field: str, error: dict) -> str:
        error_type = error.get("type", "")
        msg = error.get("msg", "")

        if error_type == "missing":
            return f"The {field} field is required."

        if error_type == "enum":
            return f"The selected {field} is invalid."

        # Strip Pydantic's "Value error, " prefix on custom field_validator errors
        if error_type == "value_error" and msg.lower().startswith("value error, "):
            msg = msg[len("value error, "):]

        return f"The {field} {msg[0].lower()}{msg[1:]}."

    async def render(self, request, exc):
        from fastapi.responses import JSONResponse

        errors: dict[str, list[str]] = {}
        for error in exc.errors():
            field = self._loc_to_field(error.get("loc", ()))
            errors.setdefault(field, []).append(self._format_message(field, error))

        total = sum(len(msgs) for msgs in errors.values())
        first_msg = next(iter(next(iter(errors.values()))))
        if total > 1:
            rest = total - 1
            summary = f"{first_msg} (and {rest} more {'error' if rest == 1 else 'errors'})"
        else:
            summary = first_msg

        return JSONResponse(
            status_code=422,
            content={"message": summary, "errors": errors},
        )


class HTTPExceptionHandler:
    """
    The base exception handler for FastAPI applications.
    """

    async def render(self, request, exc):
        import traceback
        from fastapi.responses import JSONResponse
        from fastapi_startkit.container import Container

        app = Container.instance()
        if app.is_debug():
            tb = exc.__traceback__
            frames = traceback.extract_tb(tb)
            content = {
                "message": str(exc),
                "exception": f"{type(exc).__module__}.{type(exc).__qualname__}",
                "file": frames[-1].filename if frames else None,
                "line": frames[-1].lineno if frames else None,
                "trace": [
                    {"file": f.filename, "line": f.lineno, "function": f.name}
                    for f in frames
                ],
            }
        else:
            content = {"message": "Server Error"}

        return JSONResponse(status_code=500, content=content)
