import '../css/app.css';

document.addEventListener('DOMContentLoaded', () => {
    let count: number = 0;
    const incrementBtn = document.querySelector<HTMLButtonElement>('#increment');
    const decrementBtn = document.querySelector<HTMLButtonElement>('#decrement');
    const display = document.querySelector<HTMLElement>('#count');

    if (display) {
        if (incrementBtn) {
            incrementBtn.addEventListener('click', () => {
                count++;
                display.textContent = count.toString();
            });
        }
        if (decrementBtn) {
            decrementBtn.addEventListener('click', () => {
                count--;
                display.textContent = count.toString();
            });
        }
    }
});
