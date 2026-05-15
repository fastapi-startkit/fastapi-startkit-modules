const routeMap: Record<string, string> = {
    dashboard: '/',
    login: '/login',
    'login.store': '/login',
    logout: '/logout',
    users: '/users',
    'users.create': '/users/create',
    'users.store': '/users',
    organizations: '/organizations',
    'organizations.create': '/organizations/create',
    'organizations.store': '/organizations',
    contacts: '/contacts',
    'contacts.create': '/contacts/create',
    'contacts.store': '/contacts',
    reports: '/reports',
};

const reverseRouteMap: Record<string, string> = Object.fromEntries(
    Object.entries(routeMap).map(([k, v]) => [v, k])
);

function currentRouteName(): string {
    const pathname = window.location.pathname;
    if (reverseRouteMap[pathname]) return reverseRouteMap[pathname];
    const parts = pathname.replace(/^\//, '').split('/');
    if (parts.length >= 3 && parts[2] === 'edit') return `${parts[0]}.edit`;
    if (parts.length >= 3 && parts[2] === 'restore') return `${parts[0]}.restore`;
    if (parts.length >= 2 && parts[1] === 'create') return `${parts[0]}.create`;
    if (parts.length >= 2) return `${parts[0]}.show`;
    return parts[0] || 'dashboard';
}

interface RouteFunction {
    (name?: string, params?: unknown): string;
    /** Returns the current route name, or checks if it matches a glob pattern. */
    current(pattern?: string): string | boolean;
}

const route = function (name?: string, params?: unknown): string {
    if (!name) return '/';
    if (routeMap[name]) return routeMap[name];

    const parts = name.split('.');
    let path = '/' + parts[0];
    if (parts[1] === 'edit' && params) path += `/${params}/edit`;
    else if (parts[1] === 'destroy' && params) path += `/${params}`;
    else if (parts[1] === 'update' && params) path += `/${params}`;
    else if (parts[1] === 'restore' && params) path += `/${params}/restore`;
    else if (parts[1] === 'create') path += '/create';
    return path;
} as RouteFunction;

route.current = function (pattern?: string): string | boolean {
    if (!pattern) return currentRouteName();
    const currentSegment =
        window.location.pathname.replace(/^\//, '').split('/')[0] || 'dashboard';
    const regex = new RegExp('^' + pattern.replace(/\*/g, '.*') + '$');
    return regex.test(currentSegment);
};

export { route };