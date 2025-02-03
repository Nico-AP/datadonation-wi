function triggerFlicker() {
    const elements = document.querySelectorAll('.heading-effect');

    // Apply animation
    elements.forEach(element => {
        element.style.animation = 'flicker 1s linear';
    })

    // Remove animation after 1s to allow delay to reset
    setTimeout(() => {
        elements.forEach(element => {
            element.style.animation = 'none';
        })

        // Randomly set next flicker time (between 5s and 15s)
        const nextFlickerTime = Math.random() * (10 - 3) + 5;
        setTimeout(triggerFlicker, nextFlickerTime * 1000);
    }, 1000);
}

triggerFlicker();
