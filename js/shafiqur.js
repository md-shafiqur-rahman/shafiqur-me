/**
 * shafiqur.js — theme toggle, mobile menu, scroll reveal, counters, contact form.
 */
(function () {
    'use strict';

    var root = document.documentElement;

    // ── Theme toggle ─────────────────────────────────────────────────────────
    var themeBtn = document.getElementById('theme-toggle');
    if (themeBtn) {
        themeBtn.addEventListener('click', function () {
            var next = root.dataset.theme === 'light' ? 'dark' : 'light';
            root.dataset.theme = next;
            try { localStorage.setItem('theme', next); } catch (e) {}
        });
    }

    // ── Mobile menu ──────────────────────────────────────────────────────────
    var menuBtn = document.getElementById('nav-toggle');
    var links = document.getElementById('nav-links');

    function setMenu(open) {
        links.classList.toggle('is-open', open);
        menuBtn.setAttribute('aria-expanded', String(open));
        menuBtn.querySelector('i').className = open ? 'fa-solid fa-xmark' : 'fa-solid fa-bars';
    }

    if (menuBtn && links) {
        menuBtn.addEventListener('click', function () {
            setMenu(!links.classList.contains('is-open'));
        });
        links.addEventListener('click', function (e) {
            if (e.target.closest('a')) setMenu(false);
        });
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape') setMenu(false);
        });
    }

    // ── Scroll reveal + counters ─────────────────────────────────────────────
    var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    function countUp(el) {
        var target = parseInt(el.dataset.count, 10);
        if (reduced || !target) return;
        var start = null;
        var duration = 1400;
        el.textContent = '0';
        function tick(ts) {
            if (!start) start = ts;
            var p = Math.min((ts - start) / duration, 1);
            el.textContent = Math.round(target * (1 - Math.pow(1 - p, 3)));
            if (p < 1) requestAnimationFrame(tick);
        }
        requestAnimationFrame(tick);
    }

    var revealEls = document.querySelectorAll('.reveal');

    if ('IntersectionObserver' in window) {
        var revealer = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (!entry.isIntersecting) return;
                entry.target.classList.add('is-in');
                entry.target.querySelectorAll('[data-count]').forEach(countUp);
                revealer.unobserve(entry.target);
            });
        }, { threshold: 0.12 });
        revealEls.forEach(function (el) { revealer.observe(el); });

        // Highlight the nav link of the section in view
        var navLinks = document.querySelectorAll('#nav-links a');
        var spy = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (!entry.isIntersecting) return;
                // Only in-page links follow the scroll; links to other pages keep their state
                var match = null;
                navLinks.forEach(function (a) {
                    if (a.getAttribute('href') === '#' + entry.target.id) match = a;
                });
                if (!match) return;
                navLinks.forEach(function (a) {
                    if (a.getAttribute('href').charAt(0) === '#') a.classList.toggle('is-active', a === match);
                });
            });
        }, { rootMargin: '-45% 0px -50% 0px' });
        document.querySelectorAll('main section[id]').forEach(function (s) { spy.observe(s); });
    } else {
        revealEls.forEach(function (el) { el.classList.add('is-in'); });
    }

    // ── Hero typing effect ───────────────────────────────────────────────────
    var typed = document.getElementById('typed');
    if (typed && !reduced) {
        var words = typed.dataset.words.split('|');
        var w = 0;
        var n = words[0].length;
        var deleting = true;

        function step() {
            var word = words[w];
            var wait = deleting ? 45 : 85;
            n += deleting ? -1 : 1;
            typed.textContent = word.slice(0, n);
            if (!deleting && n === word.length) { deleting = true; wait = 1900; }
            if (deleting && n === 0) { deleting = false; w = (w + 1) % words.length; wait = 350; }
            setTimeout(step, wait);
        }
        setTimeout(step, 1900);
    }

    // ── Contact form + chat widget form ──────────────────────────────────────
    var fallback = 'Could not send from here. Please email me directly at shafiqur.dev@gmail.com';

    function bindForm(form, note) {
        if (!form || !note) return;

        function say(text, ok) {
            note.textContent = text;
            note.className = 'form__note ' + (ok ? 'is-ok' : 'is-err');
        }

        form.addEventListener('submit', function (e) {
            e.preventDefault();
            if (form.elements.website.value) return; // honeypot

            var btn = form.querySelector('button[type="submit"]');
            var label = btn.querySelector('.btn-text');
            var original = label.textContent;
            btn.disabled = true;
            label.textContent = 'Sending…';

            fetch(form.action, { method: 'POST', body: new FormData(form) })
                .then(function (res) {
                    return res.json().then(function (data) { return { ok: res.ok, data: data }; });
                })
                .then(function (r) {
                    if (r.ok && r.data && r.data.status === 'success') {
                        form.reset();
                        say('Message sent. I will get back to you soon.', true);
                    } else {
                        say((r.data && r.data.message) || fallback, false);
                    }
                })
                .catch(function () { say(fallback, false); })
                .then(function () {
                    btn.disabled = false;
                    label.textContent = original;
                });
        });
    }

    bindForm(document.getElementById('contact-form'), document.getElementById('form-note'));
    bindForm(document.getElementById('chat-form'), document.getElementById('chat-note'));

    // ── Floating chat toggle + back to top ───────────────────────────────────
    var chatBtn = document.getElementById('chat-toggle');
    var chatPanel = document.getElementById('chat-panel');

    function setChat(open) {
        chatPanel.hidden = !open;
        chatBtn.setAttribute('aria-expanded', String(open));
        chatBtn.setAttribute('aria-label', open ? 'Close chat' : 'Open chat');
        chatBtn.querySelector('i').className = open ? 'fa-solid fa-xmark' : 'fa-solid fa-comment-dots';
        if (open) document.getElementById('chat-name').focus();
    }

    if (chatBtn && chatPanel) {
        chatBtn.addEventListener('click', function () { setChat(chatPanel.hidden); });
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape' && !chatPanel.hidden) { setChat(false); chatBtn.focus(); }
        });
    }

    var toTop = document.getElementById('to-top');
    if (toTop) {
        var onScroll = function () { toTop.hidden = window.scrollY < 600; };
        window.addEventListener('scroll', onScroll, { passive: true });
        onScroll();
        toTop.addEventListener('click', function () {
            window.scrollTo({ top: 0, behavior: reduced ? 'auto' : 'smooth' });
        });
    }

    var year = document.getElementById('year');
    if (year) year.textContent = new Date().getFullYear();
})();
