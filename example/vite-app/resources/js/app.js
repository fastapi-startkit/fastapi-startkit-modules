import '../css/app.css'

const btn = document.querySelector('#counter button')
const display = document.querySelector('#counter span')

if (btn && display) {
    let count = 0
    btn.addEventListener('click', () => {
        count++
        display.textContent = count
    })
}

console.log('[vite-example] app.js loaded')
