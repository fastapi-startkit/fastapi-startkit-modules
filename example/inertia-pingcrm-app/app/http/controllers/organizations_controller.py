from fastapi import Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi_startkit.facades import Inertia
from app.models.Organization import Organization

async def index(request: Request):
    search = request.query_params.get('search', '')
    query = Organization.query()
    if search:
        query = query.where('name', 'like', f'%{search}%')
    organizations = await query.limit(10).get()
    return Inertia.render(request, 'Organizations/Index', {
        'filters': {'search': search},
        'organizations': {
            'data': [
                {
                    'id': org.id,
                    'name': org.name,
                    'phone': org.phone,
                    'city': org.city,
                    'deleted_at': None,
                } for org in organizations
            ],
            'links': {'first': None, 'last': None, 'prev': None, 'next': None},
            'meta': {
                'current_page': 1, 'last_page': 1, 'per_page': 10,
                'from': 1, 'to': len(organizations), 'total': len(organizations),
                'path': '/organizations', 'links': [],
            },
        }
    })

async def create(request: Request):
    return Inertia.render(request, 'Organizations/Create', {})

async def store(request: Request):
    form = await request.json()
    form["account_id"] = 1 # hardcoded for demo
    await Organization.create(form)
    return RedirectResponse(url="/organizations", status_code=303)

async def edit(request: Request, organization: str):
    org = await Organization.find(organization)
    return Inertia.render(request, 'Organizations/Edit', {
        'organization': {
            'id': org.id,
            'name': org.name,
            'email': org.email,
            'phone': org.phone,
            'address': org.address,
            'city': org.city,
            'region': org.region,
            'country': org.country,
            'postal_code': org.postal_code,
            'deleted_at': None,
        }
    })

async def update(request: Request, organization: str):
    org = await Organization.find(organization)
    form = await request.json()
    await org.update(form)
    return RedirectResponse(url=f"/organizations/{organization}/edit", status_code=303)

async def destroy(request: Request, organization: str):
    # org = await Organization.find(organization)
    # await org.delete()
    return RedirectResponse(url="/organizations", status_code=303)

async def restore(request: Request, organization: str):
    return RedirectResponse(url="/organizations", status_code=303)

