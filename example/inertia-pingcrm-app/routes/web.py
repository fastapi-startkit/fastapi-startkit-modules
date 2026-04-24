from fastapi import APIRouter, Request

web = APIRouter()

from app.http.controllers.auth import authenticated_session_controller
from app.http.controllers import (
    dashboard_controller,
    users_controller,
    organizations_controller,
    contacts_controller,
    reports_controller,
    images_controller,
)

# Auth
web.add_api_route("/login", authenticated_session_controller.create, methods=["GET"], name="login")
web.add_api_route("/login", authenticated_session_controller.store, methods=["POST"], name="login.store")
web.add_api_route("/logout", authenticated_session_controller.destroy, methods=["DELETE"], name="logout")

# Dashboard
web.add_api_route("/", dashboard_controller.index, methods=["GET"], name="dashboard")

# Users
web.add_api_route("/users", users_controller.index, methods=["GET"], name="users")
web.add_api_route("/users/create", users_controller.create, methods=["GET"], name="users.create")
web.add_api_route("/users", users_controller.store, methods=["POST"], name="users.store")
web.add_api_route("/users/{user}/edit", users_controller.edit, methods=["GET"], name="users.edit")
web.add_api_route("/users/{user}", users_controller.update, methods=["PUT"], name="users.update")
web.add_api_route("/users/{user}", users_controller.destroy, methods=["DELETE"], name="users.destroy")
web.add_api_route("/users/{user}/restore", users_controller.restore, methods=["PUT"], name="users.restore")

# Organizations
web.add_api_route("/organizations", organizations_controller.index, methods=["GET"], name="organizations")
web.add_api_route("/organizations/create", organizations_controller.create, methods=["GET"], name="organizations.create")
web.add_api_route("/organizations", organizations_controller.store, methods=["POST"], name="organizations.store")
web.add_api_route("/organizations/{organization}/edit", organizations_controller.edit, methods=["GET"], name="organizations.edit")
web.add_api_route("/organizations/{organization}", organizations_controller.update, methods=["PUT"], name="organizations.update")
web.add_api_route("/organizations/{organization}", organizations_controller.destroy, methods=["DELETE"], name="organizations.destroy")
web.add_api_route("/organizations/{organization}/restore", organizations_controller.restore, methods=["PUT"], name="organizations.restore")

# Contacts
web.add_api_route("/contacts", contacts_controller.index, methods=["GET"], name="contacts")
web.add_api_route("/contacts/create", contacts_controller.create, methods=["GET"], name="contacts.create")
web.add_api_route("/contacts", contacts_controller.store, methods=["POST"], name="contacts.store")
web.add_api_route("/contacts/{contact}/edit", contacts_controller.edit, methods=["GET"], name="contacts.edit")
web.add_api_route("/contacts/{contact}", contacts_controller.update, methods=["PUT"], name="contacts.update")
web.add_api_route("/contacts/{contact}", contacts_controller.destroy, methods=["DELETE"], name="contacts.destroy")
web.add_api_route("/contacts/{contact}/restore", contacts_controller.restore, methods=["PUT"], name="contacts.restore")

# Reports
web.add_api_route("/reports", reports_controller.index, methods=["GET"], name="reports")

# Images
web.add_api_route("/img/{path:path}", images_controller.show, methods=["GET"], name="image")
