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
