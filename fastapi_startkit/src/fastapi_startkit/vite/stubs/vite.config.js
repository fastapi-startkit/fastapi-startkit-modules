import fastapi from "fastapi-vite-plugin"
import { defineConfig } from "vite"
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
    plugins: [
        fastapi({
            input: "resources/js/app.js",
            refresh: true,
        }),
        tailwindcss()
    ],
})
