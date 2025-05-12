// Smooth scroll for navigation
const navLinks = document.querySelectorAll('.sidebar-nav a');
navLinks.forEach(link => {
  link.addEventListener('click', function(e) {
    const target = document.querySelector(this.getAttribute('href'));
    if (target) {
      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth' });
    }
  });
});

// Highlight active sidebar icon on scroll
const sections = Array.from(document.querySelectorAll('main section'));
window.addEventListener('scroll', () => {
  let current = '';
  sections.forEach(section => {
    const sectionTop = section.offsetTop - 120;
    if (window.scrollY >= sectionTop) {
      current = section.getAttribute('id');
    }
  });
  navLinks.forEach(link => {
    link.classList.remove('active');
    if (link.getAttribute('href') === '#' + current) {
      link.classList.add('active');
    }
  });
});

// Copy to clipboard for install command
const copyBtn = document.querySelector('.copy-btn');
if (copyBtn) {
  copyBtn.addEventListener('click', function() {
    const targetId = this.getAttribute('data-copytarget');
    const code = document.getElementById(targetId);
    if (code) {
      const text = code.innerText;
      navigator.clipboard.writeText(text).then(() => {
        copyBtn.textContent = 'Copied!';
        copyBtn.classList.add('copied');
        setTimeout(() => {
          copyBtn.textContent = 'Copy';
          copyBtn.classList.remove('copied');
        }, 1200);
      });
    }
  });
}

// Header shrink on scroll
const header = document.querySelector('header');
window.addEventListener('scroll', () => {
  if (window.scrollY > 40) {
    header.style.background = 'rgba(34,36,38,0.95)';
    header.style.boxShadow = '0 2px 12px #0004';
  } else {
    header.style.background = 'none';
    header.style.boxShadow = 'none';
  }
});

// OS Tab switching for installation page
const osTabs = document.querySelectorAll('.os-tab');
const osTabContents = document.querySelectorAll('.os-tab-content');
osTabs.forEach(tab => {
  tab.addEventListener('click', function() {
    osTabs.forEach(t => t.classList.remove('active'));
    osTabContents.forEach(c => c.classList.remove('active'));
    this.classList.add('active');
    const target = this.getAttribute('data-tab');
    document.getElementById(target).classList.add('active');
  });
}); 