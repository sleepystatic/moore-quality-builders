// ===================================
// MASTER SCRIPT.JS - Moore Quality Builders
// All site functionality in one file
// ===================================

document.addEventListener('DOMContentLoaded', function() {

    // ===================================
    // 1. SMOOTH SCROLLING FOR NAVIGATION
    // ===================================
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

    // ===================================
    // 2. HEADER SCROLL EFFECT
    // ===================================
    window.addEventListener('scroll', () => {
        const header = document.getElementById('header');
        if (header) {
            if (window.scrollY > 100) {
                header.classList.add('header-scroll');
            } else {
                header.classList.remove('header-scroll');
            }
        }
    });

    // ===================================
    // 3. HOMEPAGE GALLERY SLIDER
    // ===================================
    const homeSlider = document.querySelector('.gallery-slider');
    if (homeSlider) {
        let currentSlideIndex = 0;
        const slides = document.querySelectorAll('.gallery-slider .slide');
        const totalSlides = slides.length;

        if (totalSlides > 0) {
            function showSlide(n) {
                const dots = document.querySelectorAll('.gallery-slider .dot');

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

            // Make functions globally accessible for onclick handlers
            window.changeSlide = function(direction) {
                showSlide(currentSlideIndex + direction);
            };

            window.currentSlide = function(n) {
                showSlide(n - 1); // Convert to 0-based index
            };

            // Auto-advance gallery every 10 seconds
            setInterval(() => {
                showSlide(currentSlideIndex + 1);
            }, 10000);
        }
    }

    // ===================================
    // 4. GALLERY PAGE FILTERING
    // ===================================
    const filterButtons = document.querySelectorAll('.filter-btn');
    const galleryCategories = document.querySelectorAll('.gallery-category');

    if (filterButtons.length > 0 && galleryCategories.length > 0) {
        // Show all categories initially
        showCategory('all');

        // Add click event to filter buttons
        filterButtons.forEach(button => {
            button.addEventListener('click', function() {
                const category = this.getAttribute('data-category');

                // Update active button
                filterButtons.forEach(btn => btn.classList.remove('active'));
                this.classList.add('active');

                // Show selected category
                showCategory(category);

                // Smooth scroll to gallery
                const galleryContent = document.querySelector('.gallery-page-content');
                if (galleryContent) {
                    const header = document.getElementById('header');
                    const headerHeight = header ? header.offsetHeight : 0;
                    const targetPosition = galleryContent.offsetTop - headerHeight - 20;

                    window.scrollTo({
                        top: targetPosition,
                        behavior: 'smooth'
                    });
                }
            });
        });

        function showCategory(category) {
            galleryCategories.forEach(cat => {
                if (category === 'all') {
                    cat.classList.add('active');
                } else {
                    if (cat.getAttribute('data-category') === category) {
                        cat.classList.add('active');
                    } else {
                        cat.classList.remove('active');
                    }
                }
            });
        }
    }

    // ===================================
    // 5. GALLERY LIGHTBOX
    // ===================================
    const galleryItems = document.querySelectorAll('.gallery-item img');

    if (galleryItems.length > 0) {
        galleryItems.forEach(item => {
            item.addEventListener('click', function() {
                openLightbox(this.src, this.alt);
            });
        });
    }

    function openLightbox(src, alt) {
        let lightbox = document.querySelector('.lightbox');

        if (!lightbox) {
            lightbox = document.createElement('div');
            lightbox.className = 'lightbox';
            lightbox.innerHTML = `
                <span class="lightbox-close">&times;</span>
                <img src="" alt="">
            `;
            document.body.appendChild(lightbox);

            // Close lightbox on click
            lightbox.addEventListener('click', function(e) {
                if (e.target === lightbox || e.target.className === 'lightbox-close') {
                    closeLightbox();
                }
            });

            // Close on escape key
            document.addEventListener('keydown', function(e) {
                if (e.key === 'Escape') {
                    closeLightbox();
                }
            });
        }

        // Set image and show lightbox
        const lightboxImg = lightbox.querySelector('img');
        lightboxImg.src = src;
        lightboxImg.alt = alt;
        lightbox.classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    function closeLightbox() {
        const lightbox = document.querySelector('.lightbox');
        if (lightbox) {
            lightbox.classList.remove('active');
            document.body.style.overflow = 'auto';
        }
    }

    // ===================================
    // 6. SCROLL ANIMATIONS
    // ===================================
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

}); // End DOMContentLoaded

// ===================================
// 7. FORM SUBMISSION (Outside DOMContentLoaded for global access)
// ===================================
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
        console.error('Form submission error:', error);
    });
}