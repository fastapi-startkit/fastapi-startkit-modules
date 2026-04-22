import { useState } from 'react'

// ─── Mock Data ────────────────────────────────────────────────────────────────

const TEAMS = [
    { id: 1, name: 'Flare', color: '#f97316', count: 54 },
    { id: 2, name: 'Mailcoach', color: '#8b5cf6', count: 49 },
    { id: 3, name: 'Ray', color: '#06b6d4', count: 0 },
]

const NAV_MINE = [
    { id: 'open', label: 'My open tickets', count: 26, icon: '📬' },
    { id: 'waiting', label: 'My waiting tickets', count: 0, icon: '⏳' },
    { id: 'closed', label: 'My closed tickets', count: 18, icon: '✅' },
]

const NAV_WORKSPACE = [
    { id: 'ws-open', label: 'Open', count: 204 },
    { id: 'ws-waiting', label: 'Waiting', count: 27 },
    { id: 'ws-closed', label: 'Closed', count: 175 },
    { id: 'ws-spam', label: 'Spam', count: 0 },
    { id: 'ws-assigned', label: 'Assigned', count: 151 },
    { id: 'ws-all', label: 'All', count: 406 },
]

const TICKETS = [
    {
        id: 405,
        title: 'Large CSV subscriber import silently failing at ~12k rows',
        team: 'Mailcoach Support',
        status: 'Open',
        statusColor: 'green',
        from: 'Elena Vasquez',
        to: 'Freek Van der Herten',
        tags: ['Bug'],
        time: '21m ago',
        preview: 'Elena reports 45k subscriber CSV import only importing ~12k rows with no errors shown. Caused by Redis memory exhaustion during chunked import processing.',
        assignee: { name: 'Freek Van der Herten', avatar: 'FV' },
        channel: 'Mailcoach Support',
        customerSince: 'Jan 12, 2024',
        plan: 'Business (annual)',
        monthlySends: '187,420',
        messages: [
            { id: 1, author: 'Elena Vasquez', avatar: 'EV', time: '59m ago', body: 'Hi there, We\'re trying to import a CSV with about 45,000 subscribers but only ~12k are being imported. There are no errors shown anywhere. Can you help?' },
            { id: 2, author: 'Freek Van der Herten', avatar: 'FV', time: '41m ago', body: 'Hi Elena, This is a known issue with large imports when Redis memory is constrained. Fixed by reducing import_chunk_size to 1000 in mailcoach.php config.', isReply: true },
            { id: 3, author: 'Elena Vasquez', avatar: 'EV', time: '31m ago', body: 'Freek, That worked perfectly! All 45,247 subscribers imported successfully. Thank you so much!' },
        ],
    },
    {
        id: 404,
        title: 'Tag changes not reflecting on subscribers',
        team: 'Mailcoach Support',
        status: 'Open',
        statusColor: 'green',
        from: 'Myron Kohler',
        to: 'Freek Van der Herten',
        tags: ['Bug', 'Question'],
        time: '21m ago',
        preview: 'User reports subscriber tags not updating or syncing correctly.',
        assignee: { name: 'Freek Van der Herten', avatar: 'FV' },
        channel: 'Mailcoach Support',
        customerSince: 'Mar 5, 2023',
        plan: 'Starter (monthly)',
        monthlySends: '12,300',
        messages: [
            { id: 1, author: 'Myron Kohler', avatar: 'MK', time: '21m ago', body: 'Tags I assign to subscribers in the UI don\'t seem to stick. After refreshing they\'re gone.' },
        ],
    },
    {
        id: 381,
        title: 'Ray consuming too much memory',
        team: 'Spatie support',
        status: 'Open',
        statusColor: 'green',
        from: 'Helmer Zboncak',
        to: 'Freek Van der Herten',
        tags: ['Urgent'],
        time: '3h ago',
        preview: 'User concerned about Ray\'s memory usage with large datasets in long-running processes.',
        assignee: { name: 'Freek Van der Herten', avatar: 'FV' },
        channel: 'Spatie Support',
        customerSince: 'Jun 18, 2022',
        plan: 'Enterprise',
        monthlySends: '—',
        messages: [
            { id: 1, author: 'Helmer Zboncak', avatar: 'HZ', time: '3h ago', body: 'Ray seems to keep all dump data in memory during long-running artisan commands. After a few hours our process OOM crashes.' },
        ],
    },
    {
        id: 379,
        title: 'Webhook delivery retries not working after 24h',
        team: 'Flare',
        status: 'Waiting',
        statusColor: 'yellow',
        from: 'Casimir Tromp',
        to: 'Ruben Van Assche',
        tags: ['Bug'],
        time: '5h ago',
        preview: 'Webhook events are not retried after the first 24 hour window expires, even though retry policy is set.',
        assignee: { name: 'Ruben Van Assche', avatar: 'RV' },
        channel: 'Flare',
        customerSince: 'Sep 2, 2021',
        plan: 'Business (annual)',
        monthlySends: '—',
        messages: [
            { id: 1, author: 'Casimir Tromp', avatar: 'CT', time: '5h ago', body: 'Our webhook retry policy is set to retry for 72 hours but after 24h all retries stop.' },
        ],
    },
    {
        id: 377,
        title: 'Cannot set reply-to address per campaign',
        team: 'Mailcoach Support',
        status: 'Closed',
        statusColor: 'slate',
        from: 'Petra Morar',
        to: 'Freek Van der Herten',
        tags: ['Question'],
        time: '1d ago',
        preview: 'User asking how to configure a different reply-to address for individual campaigns.',
        assignee: { name: 'Freek Van der Herten', avatar: 'FV' },
        channel: 'Mailcoach Support',
        customerSince: 'Feb 14, 2023',
        plan: 'Business (annual)',
        monthlySends: '58,100',
        messages: [
            { id: 1, author: 'Petra Morar', avatar: 'PM', time: '1d ago', body: 'Is it possible to set a different reply-to for each campaign individually?' },
            { id: 2, author: 'Freek Van der Herten', avatar: 'FV', time: '23h ago', body: 'Yes! In the campaign settings under "From & Reply-to" you can override the default per campaign.', isReply: true },
        ],
    },
]

// ─── Sub-components ───────────────────────────────────────────────────────────

const TAG_COLORS = {
    Bug: 'bg-red-500/20 text-red-300 border-red-500/30',
    Urgent: 'bg-orange-500/20 text-orange-300 border-orange-500/30',
    Question: 'bg-blue-500/20 text-blue-300 border-blue-500/30',
    Feature: 'bg-green-500/20 text-green-300 border-green-500/30',
}

const STATUS_COLORS = {
    Open: 'bg-emerald-400',
    Waiting: 'bg-yellow-400',
    Closed: 'bg-slate-500',
}

function Avatar({ initials, size = 'sm', color }) {
    const colors = {
        FV: 'bg-purple-600', EV: 'bg-pink-600', MK: 'bg-blue-600',
        HZ: 'bg-orange-600', RV: 'bg-cyan-600', CT: 'bg-rose-600',
        PM: 'bg-teal-600',
    }
    const sz = size === 'sm' ? 'w-7 h-7 text-xs' : 'w-9 h-9 text-sm'
    return (
        <div className={`${sz} ${colors[initials] ?? 'bg-slate-600'} rounded-full flex items-center justify-center font-semibold text-white flex-shrink-0`}>
            {initials}
        </div>
    )
}

function Tag({ label }) {
    return (
        <span className={`px-2 py-0.5 rounded-full text-xs border ${TAG_COLORS[label] ?? 'bg-slate-500/20 text-slate-300 border-slate-500/30'}`}>
            {label}
        </span>
    )
}

// ─── Sidebar ─────────────────────────────────────────────────────────────────

function Sidebar({ activeNav, setActiveNav, selectedTicket }) {
    return (
        <aside className="w-52 flex-shrink-0 bg-slate-900 border-r border-white/5 flex flex-col overflow-y-auto">
            {/* Logo / Workspace */}
            <div className="p-4 border-b border-white/5">
                <div className="flex items-center gap-2">
                    <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center text-white text-xs font-bold">S</div>
                    <span className="text-white font-semibold text-sm">Spatie Support</span>
                </div>
            </div>

            {/* Search */}
            <div className="p-3 border-b border-white/5">
                <div className="flex items-center gap-2 bg-white/5 rounded-lg px-3 py-1.5">
                    <svg className="w-3.5 h-3.5 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>
                    <span className="text-slate-500 text-xs">Search all tickets...</span>
                </div>
            </div>

            {/* Mine */}
            <div className="pt-3 px-2">
                <p className="text-slate-600 text-[10px] font-semibold uppercase tracking-widest px-2 mb-1">Mine</p>
                {NAV_MINE.map(item => (
                    <button
                        key={item.id}
                        onClick={() => setActiveNav(item.id)}
                        className={`w-full flex items-center justify-between px-2 py-1.5 rounded-lg text-xs transition-colors ${activeNav === item.id ? 'bg-purple-500/20 text-purple-300' : 'text-slate-400 hover:bg-white/5 hover:text-white'}`}
                    >
                        <span className="flex items-center gap-2">
                            <span>{item.icon}</span>
                            {item.label}
                        </span>
                        {item.count > 0 && (
                            <span className={`font-semibold ${activeNav === item.id ? 'text-purple-300' : 'text-slate-500'}`}>{item.count}</span>
                        )}
                    </button>
                ))}
            </div>

            {/* Workspace */}
            <div className="pt-4 px-2">
                <p className="text-slate-600 text-[10px] font-semibold uppercase tracking-widest px-2 mb-1">Workspace</p>
                {NAV_WORKSPACE.map(item => (
                    <button
                        key={item.id}
                        onClick={() => setActiveNav(item.id)}
                        className={`w-full flex items-center justify-between px-2 py-1.5 rounded-lg text-xs transition-colors ${activeNav === item.id ? 'bg-purple-500/20 text-purple-300' : 'text-slate-400 hover:bg-white/5 hover:text-white'}`}
                    >
                        <span>{item.label}</span>
                        {item.count > 0 && (
                            <span className={`font-semibold ${activeNav === item.id ? 'text-purple-300' : 'text-slate-500'}`}>{item.count}</span>
                        )}
                    </button>
                ))}
            </div>

            {/* Teams */}
            <div className="pt-4 px-2 pb-4">
                <p className="text-slate-600 text-[10px] font-semibold uppercase tracking-widest px-2 mb-1">My Teams</p>
                {TEAMS.map(team => (
                    <button
                        key={team.id}
                        className="w-full flex items-center justify-between px-2 py-1.5 rounded-lg text-xs text-slate-400 hover:bg-white/5 hover:text-white transition-colors"
                    >
                        <span className="flex items-center gap-2">
                            <span className="w-2 h-2 rounded-full" style={{ background: team.color }} />
                            {team.name}
                        </span>
                        {team.count > 0 && <span className="text-slate-500 font-semibold">{team.count}</span>}
                    </button>
                ))}
            </div>
        </aside>
    )
}

// ─── Ticket List ──────────────────────────────────────────────────────────────

function TicketList({ tickets, selectedId, onSelect }) {
    return (
        <div className="w-80 flex-shrink-0 bg-slate-900/50 border-r border-white/5 flex flex-col overflow-hidden">
            {/* Header */}
            <div className="px-4 py-3 border-b border-white/5 flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <svg className="w-4 h-4 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2a1 1 0 01-.293.707L13 13.414V19a1 1 0 01-.553.894l-4 2A1 1 0 017 21v-7.586L3.293 6.707A1 1 0 013 6V4z" /></svg>
                    <span className="text-white text-sm font-medium">Filters</span>
                </div>
            </div>

            {/* Ticket rows */}
            <div className="flex-1 overflow-y-auto">
                {tickets.map(ticket => (
                    <button
                        key={ticket.id}
                        onClick={() => onSelect(ticket)}
                        className={`w-full text-left px-4 py-3 border-b border-white/5 transition-colors ${selectedId === ticket.id ? 'bg-purple-500/10 border-l-2 border-l-purple-500' : 'hover:bg-white/5'}`}
                    >
                        <div className="flex items-start justify-between gap-2 mb-1">
                            <span className="text-slate-500 text-[10px]">{ticket.time} · {ticket.team}</span>
                            <span className={`text-[10px] px-1.5 py-0.5 rounded font-medium ${ticket.status === 'Open' ? 'bg-emerald-500/20 text-emerald-400' : ticket.status === 'Waiting' ? 'bg-yellow-500/20 text-yellow-400' : 'bg-slate-500/20 text-slate-400'}`}>
                                {ticket.status}
                            </span>
                        </div>
                        <p className="text-white text-xs font-semibold mb-0.5 leading-snug">
                            <span className="text-slate-500">#{ticket.id} </span>
                            {ticket.title}
                        </p>
                        <p className="text-slate-500 text-[10px] mb-1.5">
                            {ticket.from} → {ticket.to}
                        </p>
                        <div className="flex flex-wrap gap-1 mb-2">
                            {ticket.tags.map(t => <Tag key={t} label={t} />)}
                        </div>
                        <p className="text-slate-500 text-[10px] leading-relaxed line-clamp-2">{ticket.preview}</p>
                    </button>
                ))}
            </div>
        </div>
    )
}

// ─── Ticket Detail ────────────────────────────────────────────────────────────

function TicketDetail({ ticket }) {
    const [reply, setReply] = useState('')

    if (!ticket) {
        return (
            <div className="flex-1 flex items-center justify-center bg-slate-950/30">
                <div className="text-center text-slate-600">
                    <div className="text-4xl mb-3">💬</div>
                    <p className="text-sm">Select a ticket to view it</p>
                </div>
            </div>
        )
    }

    return (
        <div className="flex-1 flex flex-col overflow-hidden bg-slate-950/20">
            {/* Ticket header */}
            <div className="px-6 py-4 border-b border-white/5 flex items-start justify-between">
                <div>
                    <div className="flex items-center gap-2 mb-1">
                        <div className={`w-2 h-2 rounded-full ${STATUS_COLORS[ticket.status]}`} />
                        <span className={`text-xs font-medium ${ticket.status === 'Open' ? 'text-emerald-400' : ticket.status === 'Waiting' ? 'text-yellow-400' : 'text-slate-400'}`}>{ticket.status}</span>
                        <span className="text-slate-600 text-xs">·</span>
                        <span className="text-slate-500 text-xs">#{ticket.id}</span>
                    </div>
                    <h1 className="text-white font-semibold text-lg leading-tight">{ticket.title}</h1>
                </div>
                <button className="p-1.5 rounded-lg hover:bg-white/5 text-slate-500 hover:text-white transition-colors">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h.01M12 12h.01M19 12h.01" /></svg>
                </button>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto px-6 py-5 space-y-5">
                {ticket.messages.map(msg => (
                    <div key={msg.id} className={`flex gap-3 ${msg.isReply ? 'flex-row-reverse' : ''}`}>
                        <Avatar initials={msg.avatar} size="md" />
                        <div className={`max-w-lg ${msg.isReply ? 'items-end' : ''} flex flex-col gap-1`}>
                            <div className="flex items-center gap-2">
                                <span className="text-white text-xs font-semibold">{msg.author}</span>
                                {msg.isReply && <span className="text-xs text-purple-400 bg-purple-500/20 border border-purple-500/30 px-1.5 py-0.5 rounded-full">Reply</span>}
                                <span className="text-slate-500 text-[10px]">{msg.time}</span>
                            </div>
                            <div className={`rounded-xl px-4 py-3 text-sm leading-relaxed ${msg.isReply ? 'bg-purple-500/15 border border-purple-500/20 text-slate-200' : 'bg-white/5 border border-white/10 text-slate-300'}`}>
                                {msg.body}
                            </div>
                        </div>
                    </div>
                ))}
            </div>

            {/* Reply box */}
            <div className="px-6 pb-5">
                <div className="rounded-xl border border-white/10 bg-white/5 overflow-hidden">
                    <textarea
                        value={reply}
                        onChange={e => setReply(e.target.value)}
                        placeholder="Write a reply..."
                        rows={3}
                        className="w-full bg-transparent px-4 pt-3 text-sm text-white placeholder-slate-600 resize-none focus:outline-none"
                    />
                    <div className="flex items-center justify-between px-4 pb-3">
                        <div className="flex gap-2 text-slate-600">
                            <button className="hover:text-slate-400 transition-colors">
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" /></svg>
                            </button>
                        </div>
                        <button
                            disabled={!reply.trim()}
                            className="px-4 py-1.5 rounded-lg bg-purple-600 hover:bg-purple-500 disabled:opacity-40 disabled:cursor-not-allowed text-white text-xs font-medium transition-colors"
                        >
                            Send Reply
                        </button>
                    </div>
                </div>
            </div>
        </div>
    )
}

// ─── Metadata Panel ───────────────────────────────────────────────────────────

function MetaPanel({ ticket }) {
    if (!ticket) return <aside className="w-64 flex-shrink-0 border-l border-white/5 bg-slate-900/30" />

    return (
        <aside className="w-64 flex-shrink-0 border-l border-white/5 bg-slate-900/30 overflow-y-auto">
            {/* Assignee / Team / etc. */}
            <div className="px-5 py-4 border-b border-white/5">
                <p className="text-slate-500 text-[10px] font-semibold uppercase tracking-widest mb-3">Ticket Info</p>
                {[
                    { label: 'Assignee', value: ticket.assignee.name, icon: <Avatar initials={ticket.assignee.avatar} size="sm" /> },
                    { label: 'Team', value: ticket.team },
                    { label: 'Workflow', value: 'Choose workflow', muted: true },
                    { label: 'Channel', value: ticket.channel, dot: true },
                ].map(({ label, value, icon, muted, dot }) => (
                    <div key={label} className="flex items-center justify-between py-1.5 group">
                        <span className="text-slate-500 text-xs">{label}</span>
                        <button className="flex items-center gap-1.5 text-xs text-white hover:text-purple-300 transition-colors">
                            {icon}
                            {dot && <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />}
                            <span className={muted ? 'text-slate-500' : ''}>{value}</span>
                        </button>
                    </div>
                ))}
            </div>

            {/* Tags */}
            <div className="px-5 py-4 border-b border-white/5">
                <p className="text-slate-500 text-[10px] font-semibold uppercase tracking-widest mb-2">Tags</p>
                <div className="flex flex-wrap gap-1.5">
                    {ticket.tags.map(t => <Tag key={t} label={t} />)}
                    <button className="text-slate-600 hover:text-slate-400 text-xs transition-colors">+ Add</button>
                </div>
            </div>

            {/* Customer info */}
            <div className="px-5 py-4">
                <div className="flex items-center justify-between mb-3">
                    <p className="text-white text-xs font-semibold">Customer Info</p>
                    <div className="w-2 h-2 rounded-full bg-emerald-400" />
                </div>
                {[
                    { label: 'PLAN', value: ticket.plan },
                    { label: 'MONTHLY SENDS', value: ticket.monthlySends },
                    { label: 'CUSTOMER SINCE', value: ticket.customerSince },
                ].map(({ label, value }) => (
                    <div key={label} className="mb-3">
                        <p className="text-slate-600 text-[9px] font-semibold uppercase tracking-widest mb-0.5">{label}</p>
                        <p className="text-white text-xs">{value}</p>
                    </div>
                ))}

                {/* AI suggestion */}
                <div className="mt-5 rounded-xl bg-white/5 border border-white/10 p-3">
                    <p className="text-slate-400 text-xs leading-relaxed">
                        How did we solve this the last time someone had import issues?
                    </p>
                    <div className="mt-2 pt-2 border-t border-white/10">
                        <p className="text-slate-500 text-[10px]">
                            Last similar case: <span className="text-purple-400 underline cursor-pointer">#{ticket.id - 24}</span>
                        </p>
                    </div>
                </div>

                <button className="mt-3 w-full text-center text-slate-600 hover:text-slate-400 text-xs transition-colors">Clear</button>
            </div>
        </aside>
    )
}

// ─── Page ─────────────────────────────────────────────────────────────────────

export default function Tickets({ tickets: propTickets }) {
    const data = propTickets ?? TICKETS
    const [activeNav, setActiveNav] = useState('open')
    const [selected, setSelected] = useState(data[0] ?? null)

    return (
        <div className="h-screen flex bg-slate-950 overflow-hidden text-white">
            <Sidebar activeNav={activeNav} setActiveNav={setActiveNav} selectedTicket={selected} />
            <TicketList tickets={data} selectedId={selected?.id} onSelect={setSelected} />
            <TicketDetail ticket={selected} />
            <MetaPanel ticket={selected} />
        </div>
    )
}
