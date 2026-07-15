/* ClickDose Labs — shared page behavior (service pages).
   Nav glass, word-stagger hero, reveal grammar, FAQ accordion,
   mobile menu, Cal floating-button typography. */
(function () {
  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Nav glass on scroll
  var nav = document.getElementById('nav');
  if (nav) {
    var handleNavScroll = function () { nav.classList.toggle('scrolled', window.scrollY > 40); };
    window.addEventListener('scroll', handleNavScroll, { passive: true });
    handleNavScroll();
  }

  // Mobile menu
  var burger = document.querySelector('.nav__burger');
  var mobilePanel = document.querySelector('.nav__mobile');
  if (burger && mobilePanel) {
    burger.addEventListener('click', function () {
      var open = burger.getAttribute('aria-expanded') === 'true';
      burger.setAttribute('aria-expanded', open ? 'false' : 'true');
      if (open) {
        mobilePanel.classList.remove('open');
        setTimeout(function () { mobilePanel.style.display = 'none'; }, 280);
      } else {
        mobilePanel.style.display = 'block';
        nav.classList.add('scrolled');
        requestAnimationFrame(function () { mobilePanel.classList.add('open'); });
      }
    });
    mobilePanel.querySelectorAll('a').forEach(function (a) {
      a.addEventListener('click', function () {
        burger.setAttribute('aria-expanded', 'false');
        mobilePanel.classList.remove('open');
        setTimeout(function () { mobilePanel.style.display = 'none'; }, 280);
      });
    });
  }

  // Word-stagger blur-in (hero fires on load)
  document.querySelectorAll('[data-words]').forEach(function (el) {
    var base = parseInt(el.getAttribute('data-delay') || '0', 10);
    (function wrapWords(node) {
      Array.prototype.slice.call(node.childNodes).forEach(function (child) {
        if (child.nodeType === 3) {
          var frag = document.createDocumentFragment();
          child.textContent.split(/(\s+)/).forEach(function (part) {
            if (/^\s+$/.test(part) || part === '') { frag.appendChild(document.createTextNode(part)); return; }
            var s = document.createElement('span');
            s.className = 'w';
            s.textContent = part;
            frag.appendChild(s);
          });
          node.replaceChild(frag, child);
        } else if (child.nodeType === 1) {
          child.classList.add('w');
        }
      });
    })(el);
    el.querySelectorAll('.w').forEach(function (w, i) { w.style.transitionDelay = (base + i * 30) + 'ms'; });
    el.classList.add('words-in');
  });

  // Reveal grammar
  var revealObserver = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) { entry.target.classList.add('visible'); revealObserver.unobserve(entry.target); }
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -60px 0px' });
  document.querySelectorAll('.reveal').forEach(function (el) { revealObserver.observe(el); });

  // FAQ accordion
  document.querySelectorAll('.faq__q').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var item = btn.parentElement;
      var answer = btn.nextElementSibling;
      var isOpen = item.classList.contains('open');
      document.querySelectorAll('.faq__item.open').forEach(function (openItem) {
        openItem.classList.remove('open');
        openItem.querySelector('.faq__a').style.maxHeight = null;
        openItem.querySelector('.faq__q').setAttribute('aria-expanded', 'false');
      });
      if (!isOpen) {
        item.classList.add('open');
        answer.style.maxHeight = answer.scrollHeight + 'px';
        btn.setAttribute('aria-expanded', 'true');
      }
    });
  });

  // Match Cal's floating waitlist button to the site's button typography
  var tries = 0;
  var timer = setInterval(function () {
    var el = document.querySelector('cal-floating-button');
    if (el && el.shadowRoot) {
      var s = document.createElement('style');
      s.textContent = "button{font-family:'Space Grotesk',sans-serif!important;font-weight:600!important;letter-spacing:0!important;border-radius:999px!important;}";
      el.shadowRoot.appendChild(s);
      clearInterval(timer);
    } else if (++tries > 80) { clearInterval(timer); }
  }, 400);
})();
