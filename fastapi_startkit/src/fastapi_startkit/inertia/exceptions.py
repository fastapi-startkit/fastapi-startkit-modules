from fastapi.exceptions import RequestValidationError
from starlette.requests import Request
from starlette.responses import RedirectResponse


class InertiaValidationHandler:
    def report(self, exc: RequestValidationError) -> None:
        pass

    async def render(self, request: Request, exc: RequestValidationError) -> RedirectResponse:
        errors = {}
        for err in exc.errors():
            field = ".".join(str(x) for x in err["loc"][1:])
            errors.setdefault(field, []).append(err["msg"])

        if "session" in request.scope:
            request.session["errors"] = errors

        return RedirectResponse(
            url=request.headers.get("referer", "/"),
            status_code=303,
        )
