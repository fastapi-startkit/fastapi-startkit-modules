from fastapi import Depends, Request
from fastapi.responses import RedirectResponse
from fastapi_startkit.inertia import Inertia
from app.http.requests.contact import ContactListRequest
from app.models.Contact import Contact
from app.models.Organization import Organization


async def index(filters: ContactListRequest = Depends()):
    contacts = await (
        Contact.query()
        .when(filters.search, lambda q: q.where('first_name', 'like', f'%{filters.search}%').or_where('last_name', 'like', f'%{filters.search}%'))
        .limit(10)
        .get()
    )
    return Inertia.render('Contacts/Index', {
        'filters': {'search': filters.search},
        'contacts': {
            'data': [
                {
                    'id': c.id,
                    'name': f"{c.first_name} {c.last_name}",
                    'organization_id': c.organization_id,
                    'organization': None,
                    'city': c.city,
                    'phone': c.phone,
                    'deleted_at': None,
                } for c in contacts
            ],
            'links': {'first': None, 'last': None, 'prev': None, 'next': None},
            'meta': {
                'current_page': 1, 'last_page': 1, 'per_page': 10,
                'from': 1, 'to': len(contacts), 'total': len(contacts),
                'path': '/contacts', 'links': [],
            },
        }
    })


async def create():
    organizations = await Organization.query().limit(100).get()
    return Inertia.render('Contacts/Create', {
        'organizations': [
            {'id': o.id, 'name': o.name} for o in organizations
        ]
    })


async def store(request: Request):
    form = await request.json()
    await Contact.create(form)
    return RedirectResponse(url="/contacts", status_code=303)


async def edit(contact: str):
    c = await Contact.find(contact)
    organizations = await Organization.query().limit(100).get()
    return Inertia.render('Contacts/Edit', {
        'contact': {
            'id': c.id,
            'first_name': c.first_name,
            'last_name': c.last_name,
            'organization_id': c.organization_id,
            'email': c.email,
            'phone': c.phone,
            'address': c.address,
            'city': c.city,
            'region': c.region,
            'country': c.country,
            'postal_code': c.postal_code,
            'deleted_at': None,
        },
        'organizations': [
            {'id': o.id, 'name': o.name} for o in organizations
        ]
    })


async def update(request: Request, contact: str):
    c = await Contact.find(contact)
    form = await request.json()
    await c.update(form)
    return RedirectResponse(url=f"/contacts/{contact}/edit", status_code=303)


async def destroy(contact: str):
    return RedirectResponse(url="/contacts", status_code=303)


async def restore(contact: str):
    return RedirectResponse(url="/contacts", status_code=303)
