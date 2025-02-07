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
        // Randomly set next flicker time (between 2s and 5s)
        setTimeout(triggerFlicker, getRandomTimeout(2, 5) * 1000);
    }, getRandomTimeout(1, 3) * 500);
}

triggerFlicker();

window.addEventListener("scroll", () => {
    let scrollY = window.scrollY;

    let maxOffset = 230; // Maximum movement downwards

    // Limit shadow movement so it doesn't go beyond maxOffset
    let offset = Math.min(scrollY / 3, maxOffset);
    const offset1 = 120;
    const offset2 = 160;
    const offset3 = 190;
    const offset4 = 210;
    const offset5 = 225;

    const boxes = document.getElementsByClassName("grey-box-shadows");

    if (boxes.length > 0) {
        boxes[0].style.boxShadow = `
            0px ${-offset1 + Math.min(offset, offset1)}px 0 #292929,
            0px ${-offset2 + Math.min(offset, maxOffset)}px 0 gray,
            0px ${-offset3 + Math.min(offset, offset3)}px 0 lightgray,
            0px ${-offset4 + Math.min(offset, offset4)}px 0 #eaeaea,
            0px ${-offset5 + Math.min(offset, offset5)}px 0 #f4f4f4
        `;
    }
    const scrollOffset = -1;

    const scrollNote = document.getElementById("scroll-note");
    if (scrollNote) {
        scrollNote.style.opacity = Math.max(0, 1 - scrollY / 100);
    }

    const personalHighlight = document.getElementById("personal-highlight");
    if (personalHighlight) {
        personalHighlight.style.textShadow = `
            2px -1px rgba(255, 191, 0, ${Math.min(1, scrollOffset + scrollY / 200)})
        `;
    }

    const reportFirstText = document.getElementById("report-first-text");
    if (reportFirstText) {
        reportFirstText.style.opacity = Math.min(1, scrollOffset + scrollY / 220);
    }

    const firstBlock = document.getElementById("first-block");
    if (firstBlock) {

        let c = Math.min( 241, Math.round(41 + (244 - 41) * scrollY/500));

        firstBlock.style.backgroundColor = `rgb(${c}, ${c}, ${c})`;
    }

});


// Run after the DOM is fully loaded
document.addEventListener("DOMContentLoaded", function () {
    const svgs = document.querySelectorAll(".wordcloud-container svg");
    svgs.forEach(svg => {
        svg.setAttribute("viewBox", "0 0 800 600");
        svg.setAttribute("width", "95%");
        svg.setAttribute("height", "");
        svg.style.maxHeight = "600px";
    });
});
