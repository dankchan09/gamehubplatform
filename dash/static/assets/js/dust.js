// Lấy đối tượng canvas và context
const canvas = document.getElementById("dustCanvas");
const ctx = canvas.getContext("2d");

// Đảm bảo canvas có kích thước bằng màn hình
canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

// Mảng các hạt bụi
let particles = [];

// Hàm tạo ra các hạt bụi
function createDust() {
    const particle = {
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        size: Math.random() * 1 + 1, // Kích thước ngẫu nhiên
        speedX: Math.random() * 2 - 1, // Tốc độ X
        speedY: Math.random() * 2 - 1, // Tốc độ Y
        opacity: Math.random() * 0.01 + 0.01, // Độ mờ của bụi
    };
    particles.push(particle);
}

// Hàm vẽ các hạt bụi
function drawDust() {
    ctx.clearRect(0, 0, canvas.width, canvas.height); // Xóa canvas mỗi khung hình
    ctx.fillStyle = "rgba(255, 255, 255, 0.9)"; // Màu trắng mờ cho bụi
    particles.forEach((particle, index) => {
        ctx.beginPath();
        ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
        ctx.fill();
        particle.x += particle.speedX;
        particle.y += particle.speedY;
        
        // Xóa các hạt bụi đã ra ngoài canvas
        if (particle.x > canvas.width || particle.x < 0 || particle.y > canvas.height || particle.y < 0) {
            particles.splice(index, 1);
        }
    });
}

// Tạo bụi liên tục
function animateDust() {
    createDust();
    drawDust();
    requestAnimationFrame(animateDust);
}

// Bắt đầu hiệu ứng
animateDust();
