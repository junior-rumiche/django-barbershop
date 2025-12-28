// 1. Scroll Reveal System
const revealElements = document.querySelectorAll('.reveal');
const revealObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('active');
            observer.unobserve(entry.target);
        }
    });
}, { threshold: 0.15, rootMargin: "0px 0px -50px 0px" });

revealElements.forEach(el => revealObserver.observe(el));

// 2. Menú Móvil
const menuBtn = document.getElementById('menu-btn');
const mobileMenu = document.getElementById('mobile-menu');
const mobileLinks = document.querySelectorAll('.mobile-link');
const menuIcon = menuBtn.querySelector('i');

function toggleMenu() {
    mobileMenu.classList.toggle('hidden');
    const isOpen = !mobileMenu.classList.contains('hidden');

    if (isOpen) {
        menuIcon.className = 'bi bi-x-lg'; // Icono "X" de Bootstrap Icons
    } else {
        menuIcon.className = 'bi bi-list'; // Icono "Hamburguesa" de Bootstrap Icons
    }
}

menuBtn.addEventListener('click', toggleMenu);
mobileLinks.forEach(link => link.addEventListener('click', () => {
    if (!mobileMenu.classList.contains('hidden')) toggleMenu();
}));

// 3. Efecto Scroll Navbar
const navbar = document.getElementById('navbar');
window.addEventListener('scroll', () => {
    if (window.scrollY > 50) {
        navbar.classList.add('scrolled');
    } else {
        navbar.classList.remove('scrolled');
    }
});

// 4. Generar Calendario
const calendarGrid = document.getElementById('calendar-grid');
const daysInMonth = 30;
const selectedDay = 15;

for (let i = 1; i <= daysInMonth; i++) {
    const dayBtn = document.createElement('button');
    dayBtn.textContent = i;
    dayBtn.className = "day-btn click-animate";

    if (i < 10) {
        dayBtn.disabled = true;
        dayBtn.style.opacity = "0.5";
    } else if (i === selectedDay) {
        dayBtn.classList.add('selected');
    }

    if (i >= 10) {
        dayBtn.addEventListener('click', function () {
            document.querySelectorAll('.day-btn').forEach(el => el.classList.remove('selected'));
            this.classList.add('selected');
        });
    }
    calendarGrid.appendChild(dayBtn);
}

// 5. Selección de Hora
const timeBtns = document.querySelectorAll('.time-btn');
timeBtns.forEach(btn => {
    btn.addEventListener('click', function () {
        timeBtns.forEach(b => b.classList.remove('active'));
        this.classList.add('active');
    });
});