document.addEventListener("DOMContentLoaded", function() {
    let stars = document.querySelectorAll(".rating-stars .fa-star");
    let ratingValue = document.getElementById("rating-value");
    
    stars.forEach(star => {
      star.addEventListener("click", function() {
        let rating = this.getAttribute("data-value");
  
        // Cập nhật màu cho các ngôi sao
        stars.forEach(star => {
          if (star.getAttribute("data-value") <= rating) {
            star.classList.add("checked");
          } else {
            star.classList.remove("checked");
          }
        });
  
        // Cập nhật giá trị đánh giá
        ratingValue.textContent = rating;
  
        // Gửi đánh giá qua AJAX (hoặc form)
        // Bạn có thể thêm đoạn mã gửi dữ liệu ở đây
      });
    });
  });
  