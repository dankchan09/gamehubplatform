console.log("ImagesLoaded script loaded.");

// Example: Wait for images to load before doing something.
document.addEventListener("DOMContentLoaded", function () {
    const images = document.querySelectorAll("img");
    let loadedImages = 0;

    images.forEach(img => {
        img.addEventListener("load", () => {
            loadedImages++;
            if (loadedImages === images.length) {
                console.log("All images loaded.");
            }
        });

        img.addEventListener("error", () => {
            console.error("Image failed to load: ", img.src);
        });
    });
});
