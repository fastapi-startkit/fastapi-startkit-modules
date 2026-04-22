import { defineConfig } from 'vite'
import fs from 'node:fs'
import path from 'node:path'

const HOT_FILE = path.resolve('public/hot')

export default defineConfig({
    build: {
        // Write hashed output into public/build/
        outDir: 'public/build',
        emptyOutDir: true,
        // Required: generates manifest.json used by the Python Vite helper
        manifest: true,
        rollupOptions: {
            input: [
                'resources/js/app.js',
                'resources/css/app.css',
            ],
        },
    },
    plugins: [
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
                    // Vite 6: httpServer may not be created yet at configureServer time;
                    // patch server.listen so we write the file after it binds.
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
})