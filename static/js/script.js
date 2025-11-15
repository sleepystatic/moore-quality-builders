// Gallery Filter Functionality
document.addEventListener('DOMContentLoaded', function() {
    const filterButtons = document.querySelectorAll('.filter-btn');
    const galleryCategories = document.querySelectorAll('.gallery-category');

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
            const headerHeight = document.getElementById('header').offsetHeight;
            const targetPosition = galleryContent.offsetTop - headerHeight - 20;

            window.scrollTo({
                top: targetPosition,
                behavior: 'smooth'
            });
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

    // Optional: Lightbox functionality for clicking images
    const galleryItems = document.querySelectorAll('.gallery-item img');

    galleryItems.forEach(item => {
        item.addEventListener('click', function() {
            openLightbox(this.src, this.alt);
        });
    });

    function openLightbox(src, alt) {
        // Create lightbox if it doesn't exist
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
});