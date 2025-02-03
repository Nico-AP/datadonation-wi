function getRandomHeading() {
    const headings = document.querySelectorAll('.heading-effect');
    if (headings.length === 0) return null; // Exit if no elements exist
    const randomIndex = Math.floor(Math.random() * headings.length);
    return headings[randomIndex];
}

function getRandomTimeout(min = 2, max = 8) {
    return Math.random() * (max - min) + min;
}

function triggerFlicker() {
    const element = getRandomHeading();
    element.style.animation = 'flicker 1s infinite linear';
    // Remove animation after 1s to allow delay to reset
    setTimeout(() => {
        element.style.animation = 'none';
        // Randomly set next flicker time (between 2s and 8s)
        setTimeout(triggerFlicker, getRandomTimeout(2, 8) * 1000);
    }, getRandomTimeout(1, 3) * 500);
}

triggerFlicker();
