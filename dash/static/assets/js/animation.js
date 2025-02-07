document.addEventListener("DOMContentLoaded", function () {
    console.log("Animation script loaded.");

    // Example animation script
    document.querySelectorAll(".animate").forEach(el => {
        el.style.transition = "all 0.5s ease-in-out";
        el.addEventListener("mouseover", () => {
            el.style.transform = "scale(1.1)";
        });
        el.addEventListener("mouseout", () => {
            el.style.transform = "scale(1)";
        });
    });
});
