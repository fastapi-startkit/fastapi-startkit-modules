from app.http.controllers import contacts_controller
from app.http.controllers import dashboard_controller
from app.http.controllers import images_controller
from app.http.controllers import organizations_controller
from app.http.controllers import reports_controller
from app.http.controllers import users_controller
from app.http.controllers.auth import authenticated_session_controller
from authentication.middlewares.auth import auth
from fastapi import Depends
from fastapi_startkit.fastapi import Router

# Public routes — no auth required
guest = Router()

guest.get("/login", authenticated_session_controller.create)
guest.post("/login", authenticated_session_controller.store)
guest.delete("/logout", authenticated_session_controller.destroy)
guest.get("/img/{path:path}", images_controller.show)

# Protected routes — auth_required dependency applied to every route
auth = Router(dependencies=[Depends(auth)])
auth.get("/", dashboard_controller.index)
auth.resource("users", users_controller)
auth.resource("organizations", organizations_controller)
auth.resource("contacts", contacts_controller)
auth.get("/reports", reports_controller.index)
