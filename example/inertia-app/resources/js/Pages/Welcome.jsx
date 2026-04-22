export default function Welcome({ user, framework, app_name }) {
    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-950 to-slate-900 flex items-center justify-center p-6">
            <div className="max-w-2xl w-full">
                {/* Badge */}
                <div className="flex justify-center mb-8">
                    <span className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-purple-500/20 border border-purple-500/40 text-purple-300 text-sm font-medium backdrop-blur-sm">
                        <span className="w-2 h-2 rounded-full bg-purple-400 animate-pulse" />
                        {app_name ?? 'FastAPI + Inertia'}
                    </span>
                </div>

                {/* Card */}
                <div className="rounded-2xl border border-white/10 bg-white/5 backdrop-blur-md shadow-2xl p-10 text-center">
                    <h1 className="text-5xl font-extrabold text-white tracking-tight mb-4">
                        Hello, <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-400">{user}</span> 👋
                    </h1>
                    <p className="text-slate-400 text-lg mb-8">
                        You're running <span className="text-white font-semibold">{framework}</span> with{' '}
                        <span className="text-white font-semibold">Inertia.js</span> + React + Tailwind CSS
                    </p>

                    {/* Feature pills */}
                    <div className="flex flex-wrap justify-center gap-3 mb-10">
                        {['FastAPI', 'Inertia.js v2', 'React 18', 'Tailwind v4', 'Vite 8'].map((tech) => (
                            <span
                                key={tech}
                                className="px-3 py-1 rounded-full bg-white/10 border border-white/20 text-white text-sm"
                            >
                                {tech}
                            </span>
                        ))}
                    </div>

                    {/* Links */}
                    <div className="flex justify-center gap-4">
                        <a
                            href="/docs"
                            className="px-5 py-2.5 rounded-xl bg-purple-600 hover:bg-purple-500 text-white text-sm font-medium transition-colors duration-200"
                        >
                            API Docs
                        </a>
                        <a
                            href="/tickets"
                            className="px-5 py-2.5 rounded-xl bg-pink-600/80 hover:bg-pink-500 text-white text-sm font-medium transition-colors duration-200"
                        >
                            🎫 Tickets
                        </a>
                        <a
                            href="/api/health"
                            className="px-5 py-2.5 rounded-xl border border-white/20 hover:bg-white/10 text-white text-sm font-medium transition-colors duration-200"
                        >
                            Health Check
                        </a>
                        <a
                            href="https://inertiajs.com"
                            target="_blank"
                            rel="noreferrer"
                            className="px-5 py-2.5 rounded-xl border border-white/20 hover:bg-white/10 text-white text-sm font-medium transition-colors duration-200"
                        >
                            Inertia Docs ↗
                        </a>
                    </div>
                </div>

                <p className="text-center text-slate-600 text-xs mt-6">
                    Edit <code className="text-slate-400">resources/js/Pages/Welcome.jsx</code> to get started
                </p>
            </div>
        </div>
    )
}
