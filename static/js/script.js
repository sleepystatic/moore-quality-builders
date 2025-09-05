// Smooth scrolling for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
   anchor.addEventListener('click', function (e) {
       e.preventDefault();
       const target = document.querySelector(this.getAttribute('href'));
       if (target) {
           target.scrollIntoView({
               behavior: 'smooth',
               block: 'start'
           });
       }
   });
});

// Header scroll effect
window.addEventListener('scroll', () => {
   const header = document.getElementById('header');
   if (window.scrollY > 100) {
       header.classList.add('header-scroll');
   } else {
       header.classList.remove('header-scroll');
   }
});

// Gallery slider functionality
let currentSlideIndex = 0;
const slides = document.querySelectorAll('.slide');
const totalSlides = slides.length;

function showSlide(n) {
    const dots = document.querySelectorAll('.dot');

    // Safety check - make sure slides exist
    if (slides.length === 0) return;

    // Hide current slide and remove active dot
    if (slides[currentSlideIndex]) {
        slides[currentSlideIndex].classList.remove('active');
    }
    if (dots.length > 0 && dots[currentSlideIndex]) {
        dots[currentSlideIndex].classList.remove('active');
    }

    // Calculate new slide index with proper wrapping
    currentSlideIndex = ((n % totalSlides) + totalSlides) % totalSlides;

    // Show new slide and activate dot
    if (slides[currentSlideIndex]) {
        slides[currentSlideIndex].classList.add('active');
    }
    if (dots.length > 0 && dots[currentSlideIndex]) {
        dots[currentSlideIndex].classList.add('active');
    }
}

function changeSlide(direction) {
   showSlide(currentSlideIndex + direction);
}

function currentSlide(n) {
   showSlide(n - 1); // Convert to 0-based index
}

// Auto-advance gallery every 10 seconds
setInterval(() => {
   changeSlide(1);
}, 10000);

// Scroll animations
function isElementInViewport(el) {
   const rect = el.getBoundingClientRect();
   return (
       rect.top >= 0 &&
       rect.left >= 0 &&
       rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
       rect.right <= (window.innerWidth || document.documentElement.clientWidth)
   );
}

function handleScrollAnimations() {
   const elements = document.querySelectorAll('.fade-in');
   elements.forEach(el => {
       if (isElementInViewport(el) || window.scrollY + window.innerHeight > el.offsetTop + 100) {
           el.classList.add('visible');
       }
   });
}

window.addEventListener('scroll', handleScrollAnimations);
handleScrollAnimations(); // Initial check

function handleFormSubmit(event) {
    event.preventDefault();

    const submitButton = event.target.querySelector('button[type="submit"]');
    const originalText = submitButton.textContent;
    submitButton.textContent = 'Sending...';
    submitButton.disabled = true;

    const formData = new FormData(event.target);

    fetch('/submit-estimate', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        submitButton.textContent = originalText;
        submitButton.disabled = false;

        if (data.status === 'success') {
            alert(data.message);
            event.target.reset();
        } else {
            alert(data.message);
        }
    })
    .catch(error => {
        submitButton.textContent = originalText;
        submitButton.disabled = false;
        alert('Error submitting form. Please try again.');
    });
}