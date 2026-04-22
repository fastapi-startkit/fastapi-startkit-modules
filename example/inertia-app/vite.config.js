import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import inertia from '@inertiajs/vite'
import fs from 'node:fs'
import path from 'node:path'

const HOT_FILE = path.resolve('public/hot')

export default defineConfig({
    plugins: [
        react(),
        tailwindcss(),
        inertia({ input: 'resources/js/app.jsx', ssr: 'resources/js/ssr.jsx' }),
        // Write/remove `public/hot` to signal HMR mode to the Python Vite helper
        {
            name: 'vite-python-hot-file',
            apply: 'serve',
            configureServer(server) {
                const writeHotFile = () => {
                    const address = server.httpServer?.address()
                    if (!address || typeof address !== 'object') return
                    const isWildcard = address.address === '0.0.0.0' || address.address === '::'
                    const host = (address.family === 'IPv6' && !isWildcard)
                        ? `[${address.address}]`
                        : (isWildcard ? 'localhost' : address.address)
                    fs.writeFileSync(HOT_FILE, `http://${host}:${address.port}`)
                }

                if (server.httpServer) {
                    server.httpServer.once('listening', writeHotFile)
                } else {
                    const originalListen = server.listen.bind(server)
                    server.listen = async function (...args) {
                        const result = await originalListen(...args)
                        writeHotFile()
                        return result
                    }
                }

                const cleanup = () => {
                    if (fs.existsSync(HOT_FILE)) fs.rmSync(HOT_FILE)
                }
                process.on('exit', cleanup)
                process.on('SIGINT', () => { cleanup(); process.exit(0) })
                process.on('SIGTERM', () => { cleanup(); process.exit(0) })
            },
        },
    ],
    build: {
        outDir: 'public/build',
        emptyOutDir: true,
        manifest: true,
        rollupOptions: {
            input: ['resources/js/app.jsx'],
        },
    },
})