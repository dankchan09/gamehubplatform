document.addEventListener("DOMContentLoaded", function () {
    console.log("TemplateMo Lugx Gaming script loaded.");

    // Example script for menu toggle
    const menuTrigger = document.querySelector(".menu-trigger");
    const nav = document.querySelector("nav ul");

    if (menuTrigger && nav) {
        menuTrigger.addEventListener("click", () => {
            nav.classList.toggle("show");
        });
    }
});