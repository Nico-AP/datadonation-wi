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

window.addEventListener("scroll", () => {
    let scrollY = window.scrollY;
    let maxOffset = 165; // Maximum movement downwards

    // Limit shadow movement so it doesn't go beyond maxOffset
    let offset = Math.min(scrollY / 3, maxOffset);
    const offset1 = 60;
    const offset2 = 100;
    const offset3 = 130;
    const offset4 = 150;
    const offset5 = 165;
    document.getElementsByClassName("grey-box-shadows")[0].style.boxShadow = `
        0px ${-offset1 + Math.min(offset, offset1)}px 0 rgb(93, 93, 93),
        0px ${-offset2 + Math.min(offset, offset2)}px 0 gray,
        0px ${-offset3 + Math.min(offset, offset3)}px 0 lightgray,
        0px ${-offset4 + Math.min(offset, offset4)}px 0 #eaeaea,
        0px ${-offset5 + Math.min(offset, offset5)}px 0 #f4f4f4
    `;
    document.getElementsByClassName("scroll-note")[0].style.opacity = Math.max(0, 1 - scrollY / 100);
});
