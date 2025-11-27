/* ==========================================
   Personal Website - JavaScript
   ========================================== */

// Wait for DOM to be ready
document.addEventListener('DOMContentLoaded', function() {
    initLanguageSwitcher();
    initNavigation();
    initScrollAnimations();
    initContactForm();
    initSmoothScroll();
});

/* ==========================================
   Language Switcher
   ========================================== */

function initLanguageSwitcher() {
    const langSwitch = document.getElementById('langSwitch');
    const html = document.documentElement;
    
    // Check saved language preference
    const savedLang = localStorage.getItem('preferredLang') || 'fa';
    setLanguage(savedLang);
    
    langSwitch.addEventListener('click', function() {
        const currentLang = html.getAttribute('lang');
        const newLang = currentLang === 'fa' ? 'en' : 'fa';
        setLanguage(newLang);
        localStorage.setItem('preferredLang', newLang);
    });
}

function setLanguage(lang) {
    const html = document.documentElement;
    
    if (lang === 'en') {
        html.setAttribute('lang', 'en');
        html.setAttribute('dir', 'ltr');
    } else {
        html.setAttribute('lang', 'fa');
        html.setAttribute('dir', 'rtl');
    }
}

/* ==========================================
   Navigation
   ========================================== */

function initNavigation() {
    const navToggle = document.getElementById('navToggle');
    const navMenu = document.getElementById('navMenu');
    const navLinks = document.querySelectorAll('.nav-link');
    
    // Mobile menu toggle
    navToggle.addEventListener('click', function() {
        navToggle.classList.toggle('active');
        navMenu.classList.toggle('active');
    });
    
    // Close menu when clicking a link
    navLinks.forEach(link => {
        link.addEventListener('click', function() {
            navToggle.classList.remove('active');
            navMenu.classList.remove('active');
        });
    });
    
    // Active link on scroll
    window.addEventListener('scroll', function() {
        const sections = document.querySelectorAll('section[id]');
        const scrollPos = window.scrollY + 100;
        
        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.offsetHeight;
            const sectionId = section.getAttribute('id');
            
            if (scrollPos >= sectionTop && scrollPos < sectionTop + sectionHeight) {
                navLinks.forEach(link => {
                    link.classList.remove('active');
                    if (link.getAttribute('href') === `#${sectionId}`) {
                        link.classList.add('active');
                    }
                });
            }
        });
    });
    
    // Navbar background on scroll
    const nav = document.querySelector('.nav');
    window.addEventListener('scroll', function() {
        if (window.scrollY > 50) {
            nav.style.boxShadow = '0 2px 20px rgba(0,0,0,0.08)';
        } else {
            nav.style.boxShadow = 'none';
        }
    });
}

/* ==========================================
   Scroll Animations
   ========================================== */

function initScrollAnimations() {
    // Add fade-in class to animated elements
    const animatedElements = document.querySelectorAll(
        '.section-title, .about-text, .about-details, .skill-category, .blog-card, .contact-info, .contact-form'
    );
    
    animatedElements.forEach(el => {
        el.classList.add('fade-in');
    });
    
    // Intersection Observer for animations
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                
                // Animate skill bars when visible
                if (entry.target.classList.contains('skill-category')) {
                    const progressBars = entry.target.querySelectorAll('.skill-progress');
                    progressBars.forEach((bar, index) => {
                        setTimeout(() => {
                            bar.style.animation = 'progressFill 1s ease forwards';
                        }, index * 150);
                    });
                }
            }
        });
    }, observerOptions);
    
    animatedElements.forEach(el => observer.observe(el));
}

/* ==========================================
   Contact Form
   ========================================== */

function initContactForm() {
    const form = document.getElementById('contactForm');
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData(form);
        const data = {
            name: formData.get('name'),
            email: formData.get('email'),
            message: formData.get('message')
        };
        
        // Show success message
        const btn = form.querySelector('button[type="submit"]');
        const originalText = btn.innerHTML;
        
        btn.innerHTML = `
            <span class="lang-fa">در حال ارسال...</span>
            <span class="lang-en">Sending...</span>
        `;
        btn.disabled = true;
        
        // Simulate form submission (replace with actual API call)
        setTimeout(() => {
            btn.innerHTML = `
                <span class="lang-fa">✓ پیام ارسال شد!</span>
                <span class="lang-en">✓ Message Sent!</span>
            `;
            btn.style.background = '#22c55e';
            
            form.reset();
            
            setTimeout(() => {
                btn.innerHTML = originalText;
                btn.style.background = '';
                btn.disabled = false;
            }, 3000);
        }, 1500);
        
        // For actual implementation, you can use:
        // - EmailJS (https://www.emailjs.com/)
        // - Formspree (https://formspree.io/)
        // - Or your own backend API
        
        console.log('Form submitted:', data);
    });
}

/* ==========================================
   Smooth Scroll
   ========================================== */

function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
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
}

/* ==========================================
   Utilities
   ========================================== */

// Debounce function for performance
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Throttle function for scroll events
function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}



