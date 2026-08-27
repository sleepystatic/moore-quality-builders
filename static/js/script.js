// ===================================
// MASTER SCRIPT.JS - Moore Quality Builders
// All site functionality in one file
// ===================================

document.addEventListener('DOMContentLoaded', function() {

    // ===================================
    // 0. MOBILE NAV SHEET
    // ===================================
    const hamburger = document.getElementById('hamburger');
    const mainNav = document.getElementById('mainNav');
    const navScrim = document.getElementById('navScrim');

    if (hamburger && mainNav) {
        let lastFocused = null;

        const isOpen = () => mainNav.classList.contains('is-open');

        function openNav() {
            lastFocused = document.activeElement;
            mainNav.classList.add('is-open');
            if (navScrim) navScrim.classList.add('is-open');
            hamburger.setAttribute('aria-expanded', 'true');
            hamburger.setAttribute('aria-label', 'Close menu');
            // Stop the page scrolling behind the sheet.
            document.body.style.overflow = 'hidden';
            const first = mainNav.querySelector('a');
            if (first) first.focus();
        }

        function closeNav(restoreFocus) {
            mainNav.classList.remove('is-open');
            if (navScrim) navScrim.classList.remove('is-open');
            hamburger.setAttribute('aria-expanded', 'false');
            hamburger.setAttribute('aria-label', 'Open menu');
            document.body.style.overflow = '';
            if (restoreFocus && lastFocused) lastFocused.focus();
        }

        hamburger.addEventListener('click', () => {
            isOpen() ? closeNav(true) : openNav();
        });

        if (navScrim) {
            navScrim.addEventListener('click', () => closeNav(true));
        }

        mainNav.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', () => closeNav(false));
        });

        document.addEventListener('keydown', (e) => {
            if (!isOpen()) return;

            if (e.key === 'Escape') {
                closeNav(true);
                return;
            }

            // Keep Tab inside the open sheet.
            if (e.key === 'Tab') {
                const items = [hamburger].concat(
                    Array.from(mainNav.querySelectorAll('a'))
                );
                const first = items[0];
                const last = items[items.length - 1];
                if (e.shiftKey && document.activeElement === first) {
                    e.preventDefault();
                    last.focus();
                } else if (!e.shiftKey && document.activeElement === last) {
                    e.preventDefault();
                    first.focus();
                }
            }
        });

        // Returning to a desktop width must not leave the sheet state stuck on.
        window.addEventListener('resize', () => {
            if (isOpen() && window.innerWidth > 900) closeNav(false);
        });
    }

    // ===================================
    // 1. SMOOTH SCROLLING FOR NAVIGATION
    // ===================================
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const hash = this.getAttribute('href');
            if (hash === '#' || hash === '#main') return;

            const target = document.querySelector(hash);
            if (!target) return;

            e.preventDefault();

            // scrollIntoView alone parks the section under the fixed header, so
            // offset by the header's real height rather than a magic number.
            const header = document.getElementById('header');
            const offset = header ? header.offsetHeight : 0;
            const top = target.getBoundingClientRect().top + window.scrollY - offset - 12;

            window.scrollTo({ top: top, behavior: 'smooth' });

            // Keep the URL and keyboard focus in step with the jump.
            if (history.replaceState) history.replaceState(null, '', hash);
            target.setAttribute('tabindex', '-1');
            target.focus({ preventScroll: true });
        });
    });

    // ===================================
    // 2. HEADER SCROLL EFFECT
    // ===================================
    // Resolve the element once, and coalesce scroll events into one frame
    // instead of re-querying the DOM on every single event.
    const headerEl = document.getElementById('header');
    if (headerEl) {
        let ticking = false;
        const syncHeader = () => {
            headerEl.classList.toggle('header-scroll', window.scrollY > 100);
            ticking = false;
        };
        window.addEventListener('scroll', () => {
            if (!ticking) {
                ticking = true;
                requestAnimationFrame(syncHeader);
            }
        }, { passive: true });
        syncHeader();
    }

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
                // Tiles show a thumbnail; the lightbox opens the full-size original.
                openLightbox(this.dataset.full || this.src, this.alt);
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
    // 5. SCROLL ANIMATIONS
    // ===================================
    // Was a scroll listener that ran querySelectorAll plus getBoundingClientRect
    // on every element on every scroll event -- forced layout on every frame.
    // IntersectionObserver does the same job off the main thread, and each
    // element is unobserved once it has appeared.
    const fadeEls = document.querySelectorAll('.fade-in');

    if (fadeEls.length) {
        if ('IntersectionObserver' in window) {
            const io = new IntersectionObserver((entries, obs) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('visible');
                        obs.unobserve(entry.target);
                    }
                });
            }, { rootMargin: '0px 0px -80px 0px', threshold: 0.05 });

            fadeEls.forEach(el => io.observe(el));
        } else {
            fadeEls.forEach(el => el.classList.add('visible'));
        }
    }

    // ===================================
    // 6. TESTIMONIAL "READ FULL REVIEW"
    // ===================================
    // Cards are line-clamped so the grid rows stay even. Only the cards whose
    // text is genuinely cut off get a toggle -- the short ones would look odd
    // with a button that reveals nothing.
    const testimonialCards = document.querySelectorAll('.testimonial-card');

    if (testimonialCards.length) {
        const syncClampButtons = () => {
            testimonialCards.forEach(card => {
                const para = card.querySelector('.testimonial-text p');
                const btn = card.querySelector('.testimonial-more');
                if (!para || !btn) return;
                if (card.classList.contains('is-expanded')) return;
                // 2px of slack: sub-pixel line heights can inflate scrollHeight.
                btn.hidden = para.scrollHeight <= para.clientHeight + 2;
            });
        };

        testimonialCards.forEach(card => {
            const btn = card.querySelector('.testimonial-more');
            if (!btn) return;
            btn.addEventListener('click', () => {
                const expanded = card.classList.toggle('is-expanded');
                btn.setAttribute('aria-expanded', expanded ? 'true' : 'false');
            });
        });

        syncClampButtons();
        // Fonts landing late changes where the clamp falls.
        if (document.fonts && document.fonts.ready) {
            document.fonts.ready.then(syncClampButtons);
        }

        let resizeTimer;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimer);
            resizeTimer = setTimeout(syncClampButtons, 150);
        });
    }

}); // End DOMContentLoaded

// ===================================
// 7. FORM SUBMISSION (Outside DOMContentLoaded for global access)
// ===================================
function handleFormSubmit(event) {
    event.preventDefault();

    const form = event.target;
    const submitButton = form.querySelector('button[type="submit"]');
    const status = form.querySelector('.form-status');
    const originalText = submitButton.textContent;

    const setStatus = (message, state) => {
        if (!status) return;
        status.textContent = message;
        status.className = 'form-status' + (state ? ' is-' + state : '');
    };

    // novalidate is on the form so the browser does not pop its own bubble
    // before we can show a message in place.
    const firstInvalid = form.querySelector(':invalid');
    if (firstInvalid) {
        setStatus('Please fill in every field before sending.', 'error');
        firstInvalid.focus();
        return;
    }

    submitButton.textContent = 'Sending...';
    submitButton.disabled = true;
    setStatus('Sending your request...', 'pending');

    fetch('/submit-estimate', {
        method: 'POST',
        body: new FormData(form)
    })
    .then(response => response.json())
    .then(data => {
        submitButton.textContent = originalText;
        submitButton.disabled = false;

        if (data.status === 'success') {
            setStatus(data.message, 'success');
            form.reset();
        } else {
            // The server says the send failed. Show its wording, which carries
            // the phone number, rather than a generic apology.
            setStatus(data.message, 'error');
        }
    })
    .catch(error => {
        submitButton.textContent = originalText;
        submitButton.disabled = false;
        setStatus(
            "We couldn't send your request just now. Please call us at (619) 807-1227.",
            'error'
        );
        console.error('Form submission error:', error);
    });
}
