import '../css/app.css'
import { createInertiaApp } from "@inertiajs/react"
import { createRoot } from "react-dom/client"

const appName = import.meta.env.VITE_APP_NAME || "Inertia Tickets"

// Route URL map for named routes
const routeMap: Record<string, string> = {
    'dashboard': '/',
    'login': '/login',
    'logout': '/logout',
    'users': '/users',
    'users.create': '/users/create',
    'users.store': '/users',
    'organizations': '/organizations',
    'organizations.create': '/organizations/create',
    'organizations.store': '/organizations',
    'contacts': '/contacts',
    'contacts.create': '/contacts/create',
    'contacts.store': '/contacts',
    'reports': '/reports',
    'profile': '/profile',
    'profile.update': '/profile',
};

// Basic Ziggy route() shim to handle PingCRM's URL generation
// Reverse map: path → route name, for current() lookup
const reverseRouteMap: Record<string, string> = Object.fromEntries(
    Object.entries(routeMap).map(([k, v]) => [v, k])
);

function currentRouteName(): string {
    const pathname = window.location.pathname;
    if (reverseRouteMap[pathname]) return reverseRouteMap[pathname];
    // Match dynamic segments like /organizations/1/edit → organizations.edit
    const parts = pathname.replace(/^\//, '').split('/');
    if (parts.length >= 3 && parts[2] === 'edit') return `${parts[0]}.edit`;
    if (parts.length >= 3 && parts[2] === 'restore') return `${parts[0]}.restore`;
    if (parts.length >= 2 && parts[1] === 'create') return `${parts[0]}.create`;
    if (parts.length >= 2) return `${parts[0]}.show`;
    return parts[0] || 'dashboard';
}

window.route = function (name, params, absolute) {
    let path = "/";
    if (name) {
        if (routeMap[name]) {
            path = routeMap[name];
        } else {
            let parts = name.split('.');
            path = "/" + parts[0];
            if (parts[1] === 'edit' && params) {
                path += "/" + params + "/edit";
            } else if (parts[1] === 'destroy' && params) {
                path += "/" + params;
            } else if (parts[1] === 'update' && params) {
                path += "/" + params;
            } else if (parts[1] === 'restore' && params) {
                path += "/" + params + "/restore";
            } else if (parts[1] === 'create') {
                path += "/create";
            }
        }
    }

    // Return a URL object so Inertia can use it directly (typeof URL === 'object',
    // which is correct — Inertia's visit() handles URL instances natively).
    // Using new String() was broken because typeof new String() === 'object' but
    // it isn't a URL instance, so Inertia tried to read .href from it and got undefined.
    const urlObj = new URL(path, window.location.href) as URL & { current: (pattern?: string) => string | boolean };
    urlObj.current = function(pattern?: string) {
        const pathname = window.location.pathname;
        // Without a pattern, return the current route name (Ziggy behaviour used by FilterBar)
        if (!pattern) return currentRouteName();
        const currentSegment = pathname.replace(/^\//, '').split('/')[0] || 'dashboard';
        const regex = new RegExp('^' + pattern.replace(/\*/g, '.*') + '$');
        return regex.test(currentSegment) || (name != null && regex.test(name));
    };
    return urlObj as any;
};

createInertiaApp({
    title: title => `${title} - ${appName}`,
    resolve: name => {
        const pages = import.meta.glob('./Pages/**/*.tsx', { eager: true })
        let page = pages[`./Pages/${name}.tsx`]
        if (!page) {
            // Also try jsx in case some files haven't been renamed
            const jsxPages = import.meta.glob('./Pages/**/*.jsx', { eager: true })
            page = jsxPages[`./Pages/${name}.jsx`]
        }
        return page
    },
    setup({ el, App, props }) {
        const root = createRoot(el)

        root.render(<App {...props} />)
    },
    progress: {
        color: "#F87415",
    },
})
