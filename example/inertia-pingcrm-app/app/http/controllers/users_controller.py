from fastapi import Request
from fastapi.responses import RedirectResponse
from fastapi_startkit.facades import Inertia
from app.models.User import User


async def index(request: Request):
    users = await User.query().limit(10).get()
    return Inertia.render(request, 'Users/Index', {
        'users': {
            'data': [
                {
                    'id': u.id,
                    'name': f"{u.first_name} {u.last_name}",
                    'email': u.email,
                    'owner': u.owner,
                    'photo': u.photo_path,
                    'deleted_at': None,
                } for u in users
            ],
            'links': {'first': None, 'last': None, 'prev': None, 'next': None},
            'meta': {
                'current_page': 1, 'last_page': 1, 'per_page': 10,
                'from': 1, 'to': len(users), 'total': len(users),
                'path': '/users', 'links': [],
            },
        }
    })


async def create(request: Request):
    return Inertia.render(request, 'Users/Create', {})


async def store(request: Request):
    form = await request.json()
    await User.create(form)
    return RedirectResponse(url="/users", status_code=303)


async def edit(request: Request, user: str):
    u = await User.find(user)
    return Inertia.render(request, 'Users/Edit', {
        'user': {
            'id': u.id,
            'first_name': u.first_name,
            'last_name': u.last_name,
            'email': u.email,
            'owner': u.owner,
            'photo': u.photo_path,
            'password': '',
            'deleted_at': None,
        }
    })


async def update(request: Request, user: str):
    u = await User.find(user)
    form = await request.json()
    await u.update(form)
    return RedirectResponse(url=f"/users/{user}/edit", status_code=303)


async def destroy(request: Request, user: str):
    return RedirectResponse(url="/users", status_code=303)


async def restore(request: Request, user: str):
    return RedirectResponse(url="/users", status_code=303)