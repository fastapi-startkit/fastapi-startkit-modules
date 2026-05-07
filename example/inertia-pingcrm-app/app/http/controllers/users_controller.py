from fastapi import Request
from fastapi.responses import RedirectResponse
from fastapi_startkit.inertia import Inertia

from app.models.User import User


async def index():
    users = await User.query().limit(10).paginate()

    return Inertia.render('Users/Index', {
        'data': [
            {
                'id': u.id,
                'name': f"{u.first_name} {u.last_name}",
                'email': u.email,
                'owner': u.owner,
                'photo': u.photo_path,
                'deleted_at': None,
            } for u in users.result
        ],
        'meta': {
            'current_page': users.current_page,
            'last_page': users.last_page,
            'per_page': users.last_page,
            'total': users.total,
        },
    })


async def create():
    return Inertia.render('Users/Create', {})


async def store(request: Request):
    form = await request.json()
    await User.create(form)
    return RedirectResponse(url="/users", status_code=303)


async def edit(user: int):
    u = await User.find(user)
    return Inertia.render('Users/Edit', {
        'user': {
            'id': u.id,
            'first_name': u.first_name,
            'last_name': u.last_name,
            'email': u.email,
            'owner': u.owner,
            'photo': u.photo_path,
            'deleted_at': None,
        }
    })


async def update(request: Request, user: int):
    u = await User.find(user)
    form = await request.json()
    await u.update(form)
    return RedirectResponse(url=f"/users/{user}/edit", status_code=303)


async def destroy(user: str):
    return RedirectResponse(url="/users", status_code=303)


async def restore(user: str):
    return RedirectResponse(url="/users", status_code=303)
