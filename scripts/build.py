"""Build the shafiqur.me static site: home, AI automation, local SEO, blog and projects.

Run from anywhere:  python3 scripts/build.py   (needs: pip install markdown-it-py)
Articles live in content/blog/*.md, case studies in content/projects/*.md.
"""
import sys, os, re, json, shutil, html, datetime

from markdown_it import MarkdownIt  # pip install markdown-it-py

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)
CONTENT = os.path.join(OUT, 'content')
SITE = 'https://shafiqur.me'
BOOK = 'https://calendar.google.com/calendar/appointments/schedules/AcZssZ1qi01q3a8nFRs1mBdFyXAYmmyJpmdOz-0SwVETYPGadUrcfdO-td5khej7lSC7F4Y2rwXZH6QW'
LINKEDIN = 'https://www.linkedin.com/in/automation-by-shafiq/'
GITHUB = 'https://github.com/md-shafiqur-rahman'
PHOTO = 'images/md-shafiqur-rahman-n8n-ai-automation-expert.jpg'
md = MarkdownIt('commonmark', {'html': True}).enable('table')
esc = lambda t: html.escape(str(t), quote=True)
partial = lambda name: open(os.path.join(HERE, 'partials', name + '.html'), encoding='utf-8').read()


def dedent(block, n):
    return '\n'.join(l[n:] if l.startswith(' ' * n) else l for l in block.split('\n'))


def indent(block, n):
    return '\n'.join((' ' * n + l) if l.strip() else l for l in block.split('\n'))


SERVICES_AI = partial('services-ai')
STACK = partial('stack')
PROCESS_AI = partial('process-ai')
TIMELINE = partial('timeline')
WORK = partial('work')
FLOW = partial('flow')
CONTACT_FORM = partial('contact-form')
CONTACT_LIST = partial('contact-list')

# ── shared chrome ───────────────────────────────────────────────────────────
NAV = [('Home', ''), ('AI Automation', 'ai-automation/'), ('Local SEO', 'local-seo/'),
       ('Projects', 'projects/'), ('Blog', 'blog/'), ('Contact', '#contact')]


def header(p, active):
    links = ''
    for label, href in NAV:
        if href == '':
            url = '#home' if p == '' else p
        elif href.startswith('#'):
            url = href if p == '' else p + href
        else:
            url = p + href
        cur = ' class="is-active" aria-current="page"' if label == active and not url.startswith('#') else ''
        links += '            <a href="%s"%s>%s</a>\n' % (url, cur, label)
    return '''    <header class="nav">
        <a class="brand" href="%(home)s" aria-label="Md Shafiqur Rahman — home">
            <img src="%(p)simages/shafiqur-avatar.png" alt="" width="36" height="36">
            <span>shafiqur<span>.me</span></span>
        </a>

        <div class="side__profile">
            <div class="side__photo">
                <img src="%(p)s%(photo)s" alt="Portrait of Md Shafiqur Rahman" width="900" height="900">
                <span class="status"><i></i>Available</span>
            </div>
            <strong>Md Shafiqur Rahman</strong>
            <span>AI Automation &amp; Local SEO</span>
        </div>

        <nav class="nav__links" id="nav-links" aria-label="Primary">
%(links)s        </nav>

        <div class="side__social">
            <a class="social" href="%(li)s" target="_blank" rel="noopener noreferrer" aria-label="LinkedIn"><i class="fa-brands fa-linkedin-in"></i></a>
            <a class="social" href="%(gh)s" target="_blank" rel="noopener noreferrer" aria-label="GitHub"><i class="fa-brands fa-github"></i></a>
            <a class="social" href="https://wa.me/8801600534507" target="_blank" rel="noopener noreferrer" aria-label="WhatsApp"><i class="fa-brands fa-whatsapp"></i></a>
            <a class="social" href="mailto:shafiqur.dev@gmail.com" aria-label="Email"><i class="fa-solid fa-envelope"></i></a>
        </div>

        <div class="nav__actions">
            <button class="icon-btn" id="theme-toggle" type="button" aria-label="Switch colour theme">
                <i class="fa-solid fa-sun theme-icon--sun"></i>
                <i class="fa-solid fa-moon theme-icon--moon"></i>
            </button>
            <a class="btn btn--primary btn--sm" href="%(book)s" target="_blank" rel="noopener noreferrer">Let's Talk</a>
            <button class="icon-btn nav__toggle" id="nav-toggle" type="button" aria-label="Menu" aria-expanded="false" aria-controls="nav-links">
                <i class="fa-solid fa-bars"></i>
            </button>
        </div>
    </header>
''' % dict(p=p, home='#home' if p == '' else p, photo=PHOTO, links=links, li=LINKEDIN, gh=GITHUB, book=BOOK)


def footer(p):
    home = '#home' if p == '' else p
    return '''    <footer class="footer">
        <div class="wrap">
            <p class="footer__line">More customers from Google. Less manual work behind the scenes.</p>
            <div class="footer__row">
                <span>© <span id="year">2026</span> Md Shafiqur Rahman · shafiqur.me · Brahmanbaria, Bangladesh</span>
                <nav class="footer__links" aria-label="Footer">
                    <a href="%(home)s">Home</a>
                    <a href="%(p)sai-automation/">AI Automation</a>
                    <a href="%(p)slocal-seo/">Local SEO</a>
                    <a href="%(p)sprojects/">Projects</a>
                    <a href="%(p)sblog/">Blog</a>
                    <a href="%(c)s">Contact</a>
                </nav>
            </div>
        </div>
    </footer>
''' % dict(p=p, home=home, c='#contact' if p == '' else p + '#contact')


DOCK = partial('dock')
THEME_JS = partial('theme-script')


def ld(obj):
    return '    <script type="application/ld+json">%s</script>\n' % json.dumps(obj, ensure_ascii=False)


urls = []


def page(rel_dir, title, desc, body, active, og_type='website', schema=(), image=None, main_cls=''):
    rel_dir = rel_dir.strip('/')
    p = '../' * (rel_dir.count('/') + 1) if rel_dir else ''
    url = '%s/%s' % (SITE, rel_dir + '/' if rel_dir else '')
    doc = '''<!DOCTYPE html>
<html lang="en" data-theme="dark">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>%(title)s</title>
    <meta name="description" content="%(desc)s">
    <meta name="author" content="Md Shafiqur Rahman">
    <link rel="canonical" href="%(url)s">
    <meta property="og:type" content="%(og)s">
    <meta property="og:site_name" content="Md Shafiqur Rahman">
    <meta property="og:url" content="%(url)s">
    <meta property="og:title" content="%(title)s">
    <meta property="og:description" content="%(desc)s">
    <meta property="og:image" content="%(image)s">
    <meta name="twitter:card" content="summary_large_image">
    <link rel="icon" type="image/png" href="%(p)simages/shafiqur-avatar.png">
%(schema)s
%(theme)s
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&family=Space+Grotesk:wght@500;600;700&display=swap">
    <link rel="stylesheet" href="%(p)scss/fontawesome.min.css">
    <link rel="stylesheet" href="%(p)scss/shafiqur.css">
</head>

<body>

%(header)s
    <main%(main_cls)s>
%(body)s    </main>

%(footer)s
%(dock)s
    <script src="%(p)sjs/shafiqur.js"></script>
</body>

</html>
''' % dict(title=esc(title), desc=esc(desc), url=url, og=og_type, p=p, theme=THEME_JS,
           image=image or SITE + '/' + PHOTO, schema=''.join(ld(s) for s in schema),
           header=header(p, active), footer=footer(p), dock=DOCK.replace('action="mailer.php"', 'action="%smailer.php"' % p),
           body=body, main_cls=' class="%s"' % main_cls if main_cls else '')
    d = os.path.join(OUT, rel_dir)
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, 'index.html'), 'w', encoding='utf-8').write(doc)
    return url


PERSON = {'@type': 'Person', '@id': SITE + '/#person', 'name': 'Md Shafiqur Rahman', 'url': SITE + '/'}


def faq_block(items, open_first=True):
    out = '                <div class="faq reveal">\n'
    for n, (q, a) in enumerate(items):
        out += '''                    <details%s>
                        <summary><h3>%s</h3></summary>
                        <div class="faq__a">%s</div>
                    </details>
''' % (' open' if n == 0 and open_first else '', esc(q), a)
    return out + '                </div>\n'


def faq_schema(items):
    strip = lambda h: re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', h))).strip()
    return {'@context': 'https://schema.org', '@type': 'FAQPage',
            'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': strip(a)}} for q, a in items]}


def head(eyebrow, h2, lead=''):
    return '''                <div class="section-head reveal">
                    <span class="eyebrow">%s</span>
                    <h2>%s</h2>
%s                </div>
''' % (eyebrow, h2, '                    <p>%s</p>\n' % lead if lead else '')


def section(sid, inner):
    return '''        <section class="section" id="%s">
            <div class="wrap">
%s            </div>
        </section>

''' % (sid, inner)


def cta_block(p, heading, text, button='Book a Free Strategy Call'):
    return '''                <aside class="post-cta reveal">
                    <h2>%s</h2>
                    <p>%s</p>
                    <div class="post-cta__row">
                        <a class="btn btn--primary" href="%s" target="_blank" rel="noopener noreferrer">%s <i class="fa-solid fa-arrow-right"></i></a>
                        <a class="btn btn--ghost" href="%s#contact">Send a message</a>
                    </div>
                </aside>
''' % (heading, text, BOOK, button, p)


# ── Home ────────────────────────────────────────────────────────────────────
home_faq = [
    ('Who is Md Shafiqur Rahman?',
     '<p>Md Shafiqur Rahman is an AI automation expert and local SEO specialist from Brahmanbaria, Bangladesh. He builds AI agents and n8n workflow automations for businesses, and he does local SEO for woodworking businesses in the United States and the United Kingdom.</p>'),
    ('What services do you offer?',
     '<p>Two services:</p><ul><li><a href="local-seo/">Local SEO for woodworking businesses</a>: Google Business Profile setup and optimization, website SEO and local citations for cabinet makers, furniture makers, kitchen remodelers and other woodworkers. Plans cost $400 to $750 per month.</li><li><a href="ai-automation/">AI agents and automation</a>: n8n workflows and AI agents for lead capture, CRM updates, follow-ups, chatbots and reporting.</li></ul>'),
    ('Which countries do you work with?',
     '<p>Local SEO is for businesses in the United States and the United Kingdom. Automation projects are remote and open to businesses anywhere.</p>'),
    ('How do I get started?',
     '<p><a href="%s" target="_blank" rel="noopener noreferrer">Book a free 30-minute strategy call</a>. I look at your Google presence or your current workflows and tell you what I would do first. You can also send a message through the contact form or WhatsApp.</p>' % BOOK),
]

doors = '''                <div class="hero__doors">
                    <a class="card door" href="local-seo/">
                        <span class="card__icon"><i class="fa-solid fa-location-dot"></i></span>
                        <span class="tool-tag">Local SEO · US &amp; UK</span>
                        <h2>Local SEO for Woodworking Businesses</h2>
                        <p>Get cabinet makers, furniture makers and kitchen remodelers found on Google Maps and local search.</p>
                        <span class="door__go">Explore Local SEO <i class="fa-solid fa-arrow-right"></i></span>
                    </a>
                    <a class="card door" href="ai-automation/">
                        <span class="card__icon"><i class="fa-solid fa-robot"></i></span>
                        <span class="tool-tag">AI Agents &amp; Automation</span>
                        <h2>AI Agents &amp; Workflow Automation</h2>
                        <p>n8n workflows and AI agents that capture leads, answer customers and take repetitive work off your plate.</p>
                        <span class="door__go">Explore AI Automation <i class="fa-solid fa-arrow-right"></i></span>
                    </a>
                </div>
'''

home_body = '''        <!-- Hero -->
        <section class="hero" id="home">
            <div class="wrap hero__inner hero__inner--doors">
                <div class="hero__text">
                    <span class="status"><i></i>Available for new clients</span>
                    <p class="hero__hello">Hello, I'm</p>
                    <h1 aria-label="Md Shafiqur Rahman — AI Automation Expert and Local SEO Specialist">
                        <span aria-hidden="true">Md Shafiqur</span>
                        <span aria-hidden="true">Rahman<em class="hl">.</em></span>
                    </h1>
                    <div class="role-node" aria-hidden="true">
                        <i class="fa-solid fa-bolt"></i>
                        <span class="typed"><span id="typed" data-words="AI Automation Expert|Local SEO Specialist|AI Agent Builder|n8n Developer">AI Automation Expert</span><i class="caret"></i></span>
                    </div>
                    <div class="hero__cta">
                        <a class="btn btn--primary" href="%(book)s" target="_blank" rel="noopener noreferrer">Book a Free Strategy Call <i class="fa-solid fa-arrow-right"></i></a>
                    </div>
                </div>

%(doors)s            </div>
            <a class="hero__scroll" href="#about">scroll <i class="fa-solid fa-arrow-down"></i></a>
        </section>

''' % dict(book=BOOK, doors=doors)

home_body += section('about', '''                <div class="about__grid">
                    <div class="reveal">
                        <span class="eyebrow">About Me</span>
                        <h2>Two skills, one goal: <em class="hl">more customers</em></h2>
                    </div>
                    <div class="about__copy reveal">
                        <p>I'm Md Shafiqur Rahman. I help businesses get found on Google and then handle the work that follows, with automation.</p>
                        <p>I've worked in SEO since February 2024 and as an n8n automation developer since August 2024. Since September 2025 I've also been the Automation Specialist at Spider Themes, where I build CRM automation, support ticket routing and deployment pipelines.</p>
                        <p>I'm based in Brahmanbaria, Bangladesh, and I work remotely with businesses in the US, the UK and beyond.</p>
                    </div>
                </div>

                <div class="bridge reveal">
                    <div>
                        <span class="eyebrow">Why both?</span>
                        <h3>Local SEO brings the enquiries. Automation makes sure none of them slip through.</h3>
                    </div>
                    <ul class="checks">
                        <li><i class="fa-solid fa-check"></i><span>Review requests go out automatically after every finished job, and more reviews also help your Google Maps ranking.</span></li>
                        <li><i class="fa-solid fa-check"></i><span>New quote requests get an instant reply, even at night or at the weekend.</span></li>
                        <li><i class="fa-solid fa-check"></i><span>Leads are followed up by email or WhatsApp until they book.</span></li>
                    </ul>
                </div>
''')
home_body += section('experience', head('Experience', 'Where I Work <em class="hl">Today</em>') + indent(dedent(TIMELINE, 16), 16) + '\n')
home_body += section('faq', head('FAQ', 'Questions People <em class="hl">Ask Me</em>') + faq_block(home_faq))

contact_list = CONTACT_LIST.replace('''                            <div>
                                <i class="fa-solid fa-location-dot"></i>''', '''                            <div>
                                <i class="fa-solid fa-location-dot"></i>''')
home_body += '''        <!-- Contact -->
        <section class="section" id="contact">
            <div class="wrap">
                <div class="contact reveal">
                    <div class="contact__intro">
                        <span class="eyebrow">Get Started</span>
                        <h2>Let's Grow <em class="hl">Your Business</em></h2>
                        <p>Tell me what you need: more local customers, less manual work, or both.</p>
                        <p>Book a free 30-minute strategy call. I'll look at your Google presence or your current workflows and tell you exactly what I'd do first.</p>
                        <a class="btn btn--primary" href="%s" target="_blank" rel="noopener noreferrer">Book a Free 30-Min Strategy Call <i class="fa-solid fa-arrow-right"></i></a>

                        %s
                    </div>

                    %s
                </div>
            </div>
        </section>

''' % (BOOK, contact_list, CONTACT_FORM)

urls.append((page('', 'Md Shafiqur Rahman — AI Automation Expert & Local SEO Specialist',
                  'I build AI agents and n8n automations for businesses, and I do local SEO for woodworking businesses in the US and UK: cabinet makers, furniture makers and kitchen remodelers.',
                  home_body, 'Home', schema=[
                      {'@context': 'https://schema.org', '@type': 'WebSite', '@id': SITE + '/#website', 'url': SITE + '/', 'name': 'Md Shafiqur Rahman', 'publisher': {'@id': SITE + '/#person'}},
                      dict(PERSON, **{'@context': 'https://schema.org', 'image': SITE + '/' + PHOTO,
                                      'jobTitle': 'AI Automation Expert & Local SEO Specialist',
                                      'worksFor': {'@type': 'Organization', 'name': 'Spider Themes'},
                                      'address': {'@type': 'PostalAddress', 'addressLocality': 'Brahmanbaria', 'addressCountry': 'BD'},
                                      'email': 'mailto:shafiqur.dev@gmail.com', 'telephone': '+8801600534507',
                                      'sameAs': [LINKEDIN, GITHUB],
                                      'knowsAbout': ['AI automation', 'AI agents', 'n8n', 'Workflow automation', 'Local SEO', 'Google Business Profile optimization', 'Local citations', 'Technical SEO']}),
                      faq_schema(home_faq)]), None))

# ── AI automation ───────────────────────────────────────────────────────────
ai_faq = [
    ('What is AI automation?',
     '<p>AI automation connects the apps your business already uses and adds AI steps where a person used to make a decision. For example, a workflow can capture a new lead, use AI to check if it is a good fit, add it to your CRM and send a personal follow-up, all without anyone touching it.</p>'),
    ('What can you automate with n8n?',
     '<p>Most repetitive work that moves data between apps, for example:</p><ul><li>Lead capture, scoring and CRM updates</li><li>Email and WhatsApp follow-ups</li><li>Support ticket routing and AI chatbots</li><li>Weekly reports pulled from several tools</li><li>Syncing data between forms, spreadsheets, databases and payment tools</li></ul>'),
    ('Do you use n8n, Make or Zapier?',
     '<p>Mostly n8n, because it handles complex multi-step workflows and can be self-hosted. I also work in Make and Zapier when a business already uses them. I compare the three in <a href="../blog/n8n-vs-make-vs-zapier/">n8n vs Make vs Zapier</a>.</p>'),
    ('How long does it take to build a workflow?',
     '<p>A simple workflow can be live in a few days. Larger systems with AI agents and several connected apps take longer. You get a clear timeline after the free strategy call, before any work starts.</p>'),
    ('How much does automation cost?',
     '<p>It depends on how many apps and steps are involved, so I give a fixed quote after the free strategy call. My article <a href="../blog/business-automation-cost-2026/">How much does business automation cost?</a> explains what drives the price.</p>'),
    ('Can I see workflows you have built?',
     '<p>Yes. My n8n workflows are public on <a href="%s" target="_blank" rel="noopener noreferrer">GitHub</a>, and the <a href="../projects/">projects page</a> has screenshots and downloadable workflow files.</p>' % GITHUB),
]
work = WORK.replace('href="https://github.com', 'href="https://github.com')
ai_body = '''        <section class="hero hero--page" id="top">
            <div class="wrap hero__inner">
                <div class="hero__text">
                    <span class="eyebrow">AI Agents &amp; Automation</span>
                    <h1>AI Agents &amp; Workflow <em class="hl">Automation</em></h1>
                    <p class="hero__lead">Manual processes slow growth. I build n8n workflows and AI agents that capture leads, answer customers and handle repetitive work, so your team can focus on the work that grows the business.</p>
                    <div class="hero__cta">
                        <a class="btn btn--primary" href="%s" target="_blank" rel="noopener noreferrer">Book a Free Strategy Call <i class="fa-solid fa-arrow-right"></i></a>
                        <a class="btn btn--ghost" href="#work">See my workflows</a>
                    </div>
                </div>

%s
            </div>
        </section>

''' % (BOOK, indent(dedent(FLOW, 16), 16))
ai_body += section('services', head('What I Do', 'Automation Services That <em class="hl">Scale Your Business</em>') + indent(dedent(SERVICES_AI, 16), 16) + '\n')
ai_body += section('stack', head('Tech Stack', 'Tools &amp; Technologies <em class="hl">I Work With</em>', 'Every tool is chosen for a reason. Here\'s the stack I use to build automation systems that are fast, reliable, and scalable.') + indent(dedent(STACK, 16), 16) + '\n')
ai_body += section('process', head('My Process', 'How I Build Your <em class="hl">Automation System</em>') + indent(dedent(PROCESS_AI, 16), 16) + '\n')
work_more = '''                <div class="work__more reveal">
                    <a class="btn btn--primary" href="../projects/">All project case studies <i class="fa-solid fa-arrow-right"></i></a>
                    <a class="btn btn--ghost" href="%s" target="_blank" rel="noopener noreferrer"><i class="fa-brands fa-github"></i> See all my work on GitHub</a>
                </div>
''' % GITHUB
ai_body += section('work', head('Work Showcase', 'See My Automations <em class="hl">in Action</em>', 'Workflows I\'ve built with n8n. The code is public on GitHub, so you can open each one and see how it works.') + indent(dedent(work, 16), 16) + '\n\n' + work_more)
ai_body += section('faq', head('FAQ', 'AI Automation <em class="hl">Questions</em>') + faq_block(ai_faq) + cta_block('../', 'Want this built for your business?', 'Book a free 30-minute strategy call. I\'ll audit your current workflows and show you exactly where automation can save you time and money.'))

urls.append((page('ai-automation', 'AI Agents & Automation Services (n8n) — Md Shafiqur Rahman',
                  'AI agents and n8n workflow automation for businesses: lead capture, CRM automation, chatbots, API integrations and reporting. Built by Md Shafiqur Rahman.',
                  ai_body, 'AI Automation', schema=[
                      {'@context': 'https://schema.org', '@type': 'Service', 'name': 'AI Agents & Workflow Automation',
                       'serviceType': 'Workflow automation and AI agent development', 'provider': PERSON, 'url': SITE + '/ai-automation/',
                       'areaServed': 'Worldwide', 'description': 'n8n workflows and AI agents for lead capture, CRM automation, follow-ups, chatbots, API integrations and reporting.'},
                      faq_schema(ai_faq)]), None))

# ── Local SEO ───────────────────────────────────────────────────────────────
niches = [('fa-door-closed', 'Cabinet makers'), ('fa-couch', 'Custom furniture makers'), ('fa-sink', 'Kitchen remodelers'),
          ('fa-hammer', 'Carpenters &amp; joiners'), ('fa-table-cells-large', 'Millwork &amp; built-ins'), ('fa-tree', 'Woodworking shops')]
niche_card = '''                <div class="card niche hero__aside">
                    <span class="niche__title">// who I work with</span>
                    <ul>
%s                    </ul>
                    <span class="niche__foot"><i class="fa-solid fa-earth-americas"></i> United States &amp; United Kingdom</span>
                </div>
''' % ''.join('                        <li><i class="fa-solid %s"></i>%s</li>\n' % n for n in niches)

seo_services = [
    ('fa-store', 'Google Business Profile Creation', 'New to Google? I create and verify your Google Business Profile the right way from day one: business name, storefront or service-area setup, hours, phone and website.'),
    ('fa-sliders', 'Google Business Profile Optimization', 'I choose your most profitable primary category and the best relevant secondary categories, set your service areas, and fill in services, description, photos and Q&amp;A so Google understands exactly what you build.'),
    ('fa-file-lines', 'On-Page SEO', 'Service and location pages, titles, headings, internal links and content written around how homeowners actually search, like "custom kitchen cabinets in [city]".'),
    ('fa-gauge-high', 'Technical SEO', 'Page speed, mobile usability, indexing, LocalBusiness schema and crawl errors fixed, so Google can read and trust your website.'),
    ('fa-link', 'Off-Page SEO', 'Links and mentions from relevant local and industry websites that build your authority.'),
    ('fa-list-check', 'Local Citations', 'Your name, address and phone listed consistently on the directories that matter: Yelp, BBB, Houzz and Angi in the US; Yell, Checkatrade, Houzz and Bark in the UK.'),
    ('fa-star', 'Reviews &amp; Reputation', 'A simple system to ask happy customers for a Google review after every finished project, and a reply to every review you get.'),
]
seo_rows = '                <ol class="services reveal">\n'
for n, (ic, t, d) in enumerate(seo_services, 1):
    seo_rows += '''                    <li class="service">
                        <span class="service__no">%02d</span>
                        <h3>%s</h3>
                        <p>%s</p>
                        <span class="service__icon"><i class="fa-solid %s"></i></span>
                    </li>
''' % (n, t, d, ic)
seo_rows += '                </ol>\n'

why = [('fa-tags', 'I know your Google categories', 'Cabinet maker, furniture maker, kitchen remodeler, carpenter, woodworker, and joiner in the UK. I know which one should be your primary category for the work that earns you the most.'),
       ('fa-magnifying-glass', 'I know how your customers search', 'Homeowners search "custom kitchen cabinets near me" or "built-in wardrobes in [city]", not your trade name. Your profile and pages are built around those searches.'),
       ('fa-camera', 'Your strategy fits your trade', 'Woodwork sells on photos, past projects and reviews. A plumbing or roofing playbook doesn\'t fit, so I don\'t use one.')]
why_cards = '                <div class="points">\n' + ''.join('''                    <article class="card reveal">
                        <div class="card__icon"><i class="fa-solid %s"></i></div>
                        <h3>%s</h3>
                        <p>%s</p>
                    </article>
''' % w for w in why) + '                </div>\n'

steps = [('Free audit', 'I check your Google Business Profile, your website and the competitors ranking in your area, and show you what is holding you back.'),
         ('Foundation', 'I create or fix your Google Business Profile, set the right categories and service areas, and clean up your citations.'),
         ('Website SEO', 'On-page and technical fixes, plus service and location pages for the work and the towns you want to win.'),
         ('Grow &amp; report', 'Every month: profile posts, new citations and links, review requests, and a report on calls, direction requests and rankings.')]
seo_process = '                <div class="process">\n' + ''.join('''                    <div class="step reveal">
                        <div class="step__no">%02d</div>
                        <h3>%s</h3>
                        <p>%s</p>
                    </div>
''' % (n, t, d) for n, (t, d) in enumerate(steps, 1)) + '                </div>\n'

plans = [('Starter', 400, 'For a new or small woodworking business getting set up on Google.', False,
          ['Google Business Profile creation or full optimization', 'Primary and secondary category and service-area setup', '4 Google Business Profile posts per month', 'Up to 20 local citations', 'On-page SEO for your homepage and 1 service page', 'Monthly report']),
         ('Growth', 550, 'For an established business that wants to beat local competitors.', True,
          ['Everything in Starter', '8 Google Business Profile posts per month', 'Up to 40 local citations', 'On-page SEO for up to 5 pages', 'Technical SEO fixes', 'Review request system', 'Monthly report and call']),
         ('Authority', 750, 'For a business ready to lead its area on Google Maps.', False,
          ['Everything in Growth', '2 new service or location pages per month', 'Off-page SEO and link building', 'Up to 60 local citations', 'Local rank tracking against competitors', 'Priority support'])]
plan_html = '                <div class="plans">\n'
for name, price, blurb, featured, items in plans:
    plan_html += '''                    <article class="card plan%s reveal">
%s                        <h3>%s</h3>
                        <p class="plan__price">$%d<small>/month</small></p>
                        <p>%s</p>
                        <ul class="checks">
%s                        </ul>
                        <a class="btn %s" href="%s" target="_blank" rel="noopener noreferrer">Get started</a>
                    </article>
''' % (' plan--featured' if featured else '', '                        <span class="plan__badge">Most popular</span>\n' if featured else '', name, price, blurb,
       ''.join('                            <li><i class="fa-solid fa-check"></i><span>%s</span></li>\n' % i for i in items),
       'btn--primary' if featured else 'btn--ghost', BOOK)
plan_html += '''                </div>
                <p class="plans__note reveal">Prices in USD. Not sure which plan fits? <a href="%s" target="_blank" rel="noopener noreferrer">Book a free audit call</a> and I'll recommend one after looking at your profile.</p>
''' % BOOK

seo_faq = [
    ('What is local SEO for a woodworking business?',
     '<p>Local SEO is the work that makes your business show up when people nearby search Google or Google Maps for what you build, like "cabinet maker near me" or "custom furniture in Leeds". It covers your Google Business Profile, your website, your reviews and your listings on other directories.</p>'),
    ('How much does local SEO cost?',
     '<p>My local SEO plans cost $400 to $750 per month: Starter at $400, Growth at $550 and Authority at $750. Prices are in USD. I recommend a plan after a free audit of your profile and your local competitors.</p>'),
    ('How long does local SEO take to work?',
     '<p>Fixes to your Google Business Profile can make a difference within weeks, but rankings usually build over several months. Busy cities and established competitors take longer. I won\'t promise a timeline before I\'ve audited your market.</p>'),
    ('What is the best Google Business Profile category for a cabinet maker?',
     '<p>Pick the primary category that matches the work that earns you the most. If most of your income is custom cabinetry, "Cabinet maker" is usually the right primary category. Then add secondary categories such as "Kitchen remodeler", "Furniture maker" or "Woodworker" only for services you really offer. Your primary category has the biggest effect on which searches you show up for.</p>'),
    ('I don\'t have a showroom. Can I still rank on Google Maps?',
     '<p>Yes. Most woodworkers work from a workshop or go to the customer. Google lets you set up a service-area business: your address stays hidden and you choose the towns and cities you serve.</p>'),
    ('Do you work with woodworking businesses in the UK?',
     '<p>Yes. I work with businesses in the United States and the United Kingdom. UK profiles use UK categories and directories, such as "Joiner" and listings on Yell and Checkatrade.</p>'),
    ('Do I need a website for local SEO?',
     '<p>You can rank on Google Maps with a strong Google Business Profile alone, but a website with service and location pages helps you rank higher, in more areas, and gives customers a place to see your past work. I can optimize the website you already have.</p>'),
    ('Do you guarantee #1 rankings?',
     '<p>No. Nobody controls Google\'s rankings, and anyone who guarantees #1 is guessing. What I do guarantee is the work: a fully optimized profile, clean citations, a better website and a clear report every month.</p>'),
    ('Why do you only work with woodworking businesses?',
     '<p>Most local SEO freelancers target plumbing, roofing and HVAC, so those markets are crowded. I chose one niche and learned it deeply: its Google categories, how its customers search, and what makes them choose one workshop over another.</p>'),
]

seo_body = '''        <section class="hero hero--page" id="top">
            <div class="wrap hero__inner hero__inner--aside">
                <div class="hero__text">
                    <span class="eyebrow">Local SEO · US &amp; UK</span>
                    <h1>Local SEO for <em class="hl">Woodworking</em> Businesses</h1>
                    <p class="hero__lead">I help cabinet makers, furniture makers, kitchen remodelers and other woodworking businesses in the US and UK show up on Google Maps and local search when homeowners nearby look for the work you do.</p>
                    <div class="hero__cta">
                        <a class="btn btn--primary" href="%s" target="_blank" rel="noopener noreferrer">Book a Free Local SEO Audit <i class="fa-solid fa-arrow-right"></i></a>
                        <a class="btn btn--ghost" href="#pricing">See pricing</a>
                    </div>
                </div>

%s            </div>
        </section>

''' % (BOOK, niche_card)
seo_body += section('why-woodworking', head('Why Woodworking', 'Why I Only Work With <em class="hl">Woodworking Businesses</em>', 'Most local SEO freelancers chase plumbing, roofing and HVAC, where every city is crowded with competitors and agencies. I chose one niche and learned it deeply.') + why_cards)
seo_body += section('services', head('What I Do', 'Local SEO <em class="hl">Services</em>', 'Everything your business needs to show up on Google Maps and local search, from your Google Business Profile to your website.') + seo_rows)
seo_body += section('process', head('My Process', 'How I Grow Your <em class="hl">Local Visibility</em>') + seo_process)
seo_body += section('pricing', head('Pricing', 'Simple <em class="hl">Monthly Pricing</em>', 'Three plans from $400 to $750 per month. We choose the right one together after a free audit.') + plan_html)
seo_body += section('faq', head('FAQ', 'Local SEO <em class="hl">Questions</em>') + faq_block(seo_faq) + cta_block('../', 'Want more local customers from Google?', 'Book a free audit call. I\'ll look at your Google Business Profile, your website and the competitors ranking in your area, and tell you exactly what I\'d fix first.', 'Book a Free Local SEO Audit'))

urls.append((page('local-seo', 'Local SEO for Woodworking Businesses (US & UK) — Md Shafiqur Rahman',
                  'Local SEO for cabinet makers, custom furniture makers, kitchen remodelers and other woodworking businesses in the US and UK. Google Business Profile setup and optimization, website SEO and local citations from $400 per month.',
                  seo_body, 'Local SEO', schema=[
                      {'@context': 'https://schema.org', '@type': 'Service', 'name': 'Local SEO for Woodworking Businesses', 'serviceType': 'Local SEO',
                       'provider': PERSON, 'url': SITE + '/local-seo/',
                       'areaServed': [{'@type': 'Country', 'name': 'United States'}, {'@type': 'Country', 'name': 'United Kingdom'}],
                       'audience': {'@type': 'BusinessAudience', 'name': 'Woodworking businesses: cabinet makers, custom furniture makers, kitchen remodelers, carpenters and joiners'},
                       'description': 'Google Business Profile creation and optimization, on-page, technical and off-page SEO, local citations and review management for woodworking businesses.',
                       'offers': [{'@type': 'Offer', 'name': '%s plan' % n, 'price': str(pr), 'priceCurrency': 'USD',
                                   'priceSpecification': {'@type': 'UnitPriceSpecification', 'price': str(pr), 'priceCurrency': 'USD', 'unitText': 'MONTH'}} for n, pr, *_ in plans]},
                      faq_schema(seo_faq)]), None))

# ── Blog + projects (content from the old site) ─────────────────────────────


def front(path):
    raw = open(path, encoding='utf-8').read()
    m = re.match(r'---\n(.*?)\n---\n?(.*)', raw, flags=re.S)
    data, key, sub = {}, None, None
    for line in m.group(1).split('\n'):
        if not line.strip():
            continue
        m2 = re.match(r'^(\w+):\s*(.*)$', line)
        if m2:
            key, val, sub = m2.group(1), m2.group(2).strip(), None
            data[key] = {} if val == '' else json.loads(val) if val.startswith('[') else (val == 'true') if val in ('true', 'false') else val.strip('"')
            continue
        m3 = re.match(r'^\s+(\w+):\s*$', line)
        if m3:
            sub = m3.group(1); data[key][sub] = []; continue
        m4 = re.match(r'^\s+-\s+(.*)$', line)
        if m4 and sub:
            data[key][sub].append(m4.group(1).strip())
    return data, m.group(2)


def render(body, prefix):
    out = md.render(body)
    out = re.sub(r'href="(?:https?://shafiqur\.dev)?/(blog|projects)/([\w-]+)/?"', lambda m: 'href="%s%s/%s/"' % (prefix, m.group(1), m.group(2)), out)
    out = out.replace('<table>', '<div class="table-wrap"><table>').replace('</table>', '</table></div>')
    return re.sub(r'<a href="(https?://[^"]+)"', r'<a href="\1" target="_blank" rel="noopener noreferrer"', out)


nice_date = lambda d: datetime.date.fromisoformat(d).strftime('%b %-d, %Y')
TAGS = {'n8n': 'n8n', 'automation': 'Automation', 'ai': 'AI & LLMs', 'tutorial': 'Tutorial', 'business': 'Business',
        'lead generation': 'Lead Gen', 'ai automation': 'AI Automation', 'reporting': 'Reporting'}
tag = lambda c: TAGS.get(c.lower(), c)

posts = []
for f in sorted(os.listdir(os.path.join(CONTENT, 'blog'))):
    if not f.endswith('.md'):
        continue
    data, body = front(os.path.join(CONTENT, 'blog', f))
    if data.get('published') is not False:
        data.update(slug=f[:-3], body=body); posts.append(data)
posts.sort(key=lambda p: p['date'], reverse=True)

for p in posts:
    rel = 'blog/' + p['slug']
    body = '''        <article class="wrap wrap--narrow">
            <a class="crumb" href="../"><i class="fa-solid fa-arrow-left"></i> All articles</a>
            <header class="post-head">
                <span class="tool-tag">%s</span>
                <h1>%s</h1>
                <p class="post-head__lead">%s</p>
                <p class="post-meta"><span>Md Shafiqur Rahman</span><span><time datetime="%s">%s</time></span><span>%s</span></p>
            </header>
            <div class="prose">
%s            </div>
%s        </article>
''' % (esc(tag(p['category'])), esc(p['title']), esc(p['excerpt']), p['date'], nice_date(p['date']), esc(p.get('readTime', '5 min read')),
       render(p['body'], '../../'),
       cta_block('../../', 'Want this built for your business?', 'Book a free 30-minute strategy call. I\'ll audit your current workflows and show you exactly where automation can save you time and money.').replace('                ', '            ', 1))
    urls.append((page(rel, '%s — Md Shafiqur Rahman' % p['title'], p['excerpt'], body, 'Blog', 'article', main_cls='page', schema=[
        {'@context': 'https://schema.org', '@type': 'BlogPosting', 'headline': p['title'], 'description': p['excerpt'],
         'datePublished': p['date'], 'author': PERSON, 'mainEntityOfPage': '%s/%s/' % (SITE, rel)}]), p['date']))

cards = ''.join('''                <a class="card post-card" href="%s/">
                    <span class="tool-tag">%s</span>
                    <h2>%s</h2>
                    <p>%s</p>
                    <span class="post-meta"><span><time datetime="%s">%s</time></span><span>%s</span></span>
                </a>
''' % (p['slug'], esc(tag(p['category'])), esc(p['title']), esc(p['excerpt']), p['date'], nice_date(p['date']), esc(p.get('readTime', '5 min read'))) for p in posts)
urls.insert(3, (page('blog', 'Blog — AI Automation & Local SEO Insights | Md Shafiqur Rahman',
                     'Tutorials and guides on n8n, AI agents, workflow automation and local SEO for growing businesses.',
                     '''        <div class="wrap">
            <header class="section-head">
                <span class="eyebrow">Blog</span>
                <h1>Insights on AI &amp; <em class="hl">Automation</em></h1>
                <p>Tips, tutorials, and real-world case studies on building intelligent automation systems with n8n, AI agents, and workflow automation that scale your business.</p>
            </header>
            <div class="posts">
%s            </div>
        </div>
''' % cards, 'Blog', main_cls='page'), None))

projects = []
pdir = os.path.join(CONTENT, 'projects')
for f in sorted(os.listdir(pdir)):
    if not f.endswith('.md'):
        continue
    slug = f[:-3]
    data, body = front(os.path.join(pdir, f))
    if data.get('published') is False:
        continue
    # screenshots and workflow.json live next to the generated page, in projects/<slug>/
    assets = os.path.join(OUT, 'projects', slug)
    files = sorted(x for x in os.listdir(assets) if x != 'index.html') if os.path.isdir(assets) else []
    shots = data.get('screenshots') or {}
    data.update(slug=slug, body=body, has_json='workflow.json' in files,
                workflow=[f for f in shots.get('workflow', []) if f in files], output=[f for f in shots.get('output', []) if f in files],
                thumb=next((f for f in files if f.lower().startswith('thumbnail.')), None))
    if not shots:
        data['workflow'] = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')) and not f.lower().startswith('thumbnail.')]
    projects.append(data)
projects.sort(key=lambda p: p['date'], reverse=True)


def gallery(title, files):
    if not files:
        return ''
    figs = ''.join('                    <a href="%s" target="_blank" rel="noopener"><img src="%s" alt="%s screenshot %d" loading="lazy"></a>\n' % (f, f, title, i + 1) for i, f in enumerate(files))
    return '            <section class="shots">\n                <h2>%s</h2>\n                <div class="shots__grid">\n%s                </div>\n            </section>\n' % (title, figs)


for p in projects:
    rel = 'projects/' + p['slug']
    dl = '            <p class="post-download"><a class="btn btn--ghost" href="workflow.json" download="%s-workflow.json"><i class="fa-solid fa-download"></i> Download the n8n workflow (JSON)</a></p>\n' % p['slug'] if p['has_json'] else ''
    body = '''        <article class="wrap wrap--narrow">
            <a class="crumb" href="../"><i class="fa-solid fa-arrow-left"></i> All projects</a>
            <header class="post-head">
                <span class="tool-tag">%s</span>
                <h1>%s</h1>
                <p class="post-head__lead">%s</p>
                <ul class="results">%s</ul>
                <div class="post-tools"><span>Tools used:</span><ul class="stack__list">%s</ul></div>
            </header>
            <div class="prose">
%s            </div>
%s%s%s%s        </article>
''' % (esc(tag(p['category'])), esc(p['title']), esc(p['excerpt']),
       ''.join('<li>%s</li>' % esc(r.strip()) for r in p.get('results', '').split('|') if r.strip()),
       ''.join('<li>%s</li>' % esc(t) for t in p.get('tools', [])), render(p['body'], '../../'),
       gallery('Workflow', p['workflow']), gallery('Output', p['output']), dl,
       cta_block('../../', 'Want Something Like This for Your Business?', 'Let\'s map out your automation. Book a free 30-minute strategy call — I\'ll audit your current workflows and show you exactly where automation can save you time and money.'))
    urls.append((page(rel, '%s — Md Shafiqur Rahman' % p['title'], p['excerpt'], body, 'Projects', 'article', main_cls='page',
                      image='%s/%s/%s' % (SITE, rel, p['thumb']) if p['thumb'] else None, schema=[
                          {'@context': 'https://schema.org', '@type': 'Article', 'headline': p['title'], 'description': p['excerpt'],
                           'datePublished': p['date'], 'author': PERSON, 'mainEntityOfPage': '%s/%s/' % (SITE, rel)}]), p['date']))

cards = ''
for p in projects:
    cover = p['thumb'] or (p['workflow'][0] if p['workflow'] else None)
    img = '<img class="project-card__cover" src="%s/%s" alt="" loading="lazy">' % (p['slug'], cover) if cover else '<span class="project-card__cover project-card__cover--none"><i class="fa-solid fa-diagram-project"></i></span>'
    cards += '''                <a class="card project-card" href="%s/">
                    %s
                    <span class="project-card__body">
                        <span class="tool-tag">%s</span>
                        <h2>%s</h2>
                        <p>%s</p>
                    </span>
                </a>
''' % (p['slug'], img, esc(tag(p['category'])), esc(p['title']), esc(p['excerpt']))
urls.append((page('projects', 'Projects — AI Automation Case Studies | Md Shafiqur Rahman',
                  'Automation workflows built with n8n: lead generation, WhatsApp bots, CRM automation, AI agents and more, with screenshots and workflow files.',
                  '''        <div class="wrap">
            <header class="section-head">
                <span class="eyebrow">Projects</span>
                <h1>AI Automation <em class="hl">Projects</em></h1>
                <p>Automation workflows I've built: lead generation, WhatsApp bots, CRM automation, AI agents and more, with screenshots and workflow files.</p>
            </header>
            <div class="posts">
%s            </div>
        </div>
''' % cards, 'Projects', main_cls='page'), None))

# ── sitemap, robots, llms.txt ───────────────────────────────────────────────
sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
sm += ''.join('  <url><loc>%s</loc>%s</url>\n' % (u, '<lastmod>%s</lastmod>' % d if d else '') for u, d in urls)
open(os.path.join(OUT, 'sitemap.xml'), 'w').write(sm + '</urlset>\n')
open(os.path.join(OUT, 'robots.txt'), 'w').write('User-agent: *\nAllow: /\nDisallow: /messages/\n\nSitemap: %s/sitemap.xml\n' % SITE)

llms = '''# Md Shafiqur Rahman

> AI automation expert and local SEO specialist from Brahmanbaria, Bangladesh. Builds AI agents and n8n workflow automations for businesses worldwide, and provides local SEO for woodworking businesses (cabinet makers, custom furniture makers, kitchen remodelers, carpenters and joiners) in the United States and the United Kingdom.

## Services

- [Local SEO for Woodworking Businesses](%(s)s/local-seo/): Google Business Profile creation and optimization (primary and secondary categories, service areas), on-page, technical and off-page SEO, local citations and review management. Plans: Starter $400/month, Growth $550/month, Authority $750/month (USD).
- [AI Agents & Workflow Automation](%(s)s/ai-automation/): n8n workflows and AI agents for lead capture and qualification, CRM automation, email and WhatsApp follow-ups, chatbots, API integrations and reporting. Fixed quote after a free strategy call.

## Work

- [Projects](%(s)s/projects/): automation case studies with screenshots and n8n workflow files.
- [GitHub](%(gh)s): public n8n workflows.

## Blog

%(posts)s
## Contact

- Email: shafiqur.dev@gmail.com
- WhatsApp: +8801600534507
- LinkedIn: %(li)s
- Book a free 30-minute strategy call: %(book)s
''' % dict(s=SITE, gh=GITHUB, li=LINKEDIN, book=BOOK, posts=''.join('- [%s](%s/blog/%s/): %s\n' % (p['title'], SITE, p['slug'], p['excerpt']) for p in posts))
open(os.path.join(OUT, 'llms.txt'), 'w').write(llms)
print('pages', len(urls), 'posts', len(posts), 'projects', len(projects))
