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
        ratingValue.textContent = "(" + rating + " / 5)";
  
        // Gửi đánh giá qua AJAX (hoặc form)
        submitRating(rating);
      });
    });
  });
  
  function submitRating(rating) {
    fetch("{% url 'submit_rating' %}", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": "{{ csrf_token }}"
      },
      body: JSON.stringify({ "rating": rating })
    }).then(response => {
      if (response.ok) {
        alert("Đánh giá đã được gửi!");
      }
    });
  }

  $(document).ready(function() {
    $(".fa-star").click(function() {
        var rating = $(this).data("value");

        $.ajax({
            type: "POST",
            url: "{% url 'submit_rating' product.id %}",
            data: JSON.stringify({ rating: rating }),
            contentType: "application/json",
            headers: {
                "X-CSRFToken": $("input[name='csrfmiddlewaretoken']").val()
            },
            success: function(response) {
                alert(response.message);
                // Cập nhật điểm đánh giá trung bình nếu cần
                location.reload();
            },
            error: function(xhr, errmsg, err) {
                alert(xhr.responseJSON.message);
            }
        });
    });
});
