# shafiqur.me

Portfolio site of Md Shafiqur Rahman: AI agents & automation, and local SEO for woodworking businesses.

Plain static HTML, CSS and JavaScript. The contact and chat forms post to `mailer.php`, so the site needs PHP hosting.

## Pages

- `/` home
- `/ai-automation/` AI agents & automation service
- `/local-seo/` local SEO service
- `/blog/` articles, generated from `content/blog/*.md`
- `/projects/` case studies, generated from `content/projects/*.md` (screenshots and `workflow.json` live in `projects/<slug>/`)

## Add or edit an article

1. Add a Markdown file to `content/blog/`, using the same front matter as the existing ones (`title`, `excerpt`, `date`, `category`, `readTime`, `published`).
2. Rebuild:

   ```
   pip install markdown-it-py
   python3 scripts/build.py
   ```

The build regenerates every page, `sitemap.xml` and `llms.txt`.

## Deploying

Upload everything except `content/`, `scripts/` and `README.md`. Then on the server, create `messages/config.php` from `messages/config.example.php` with the inbox password. The inbox is at `/messages/view.php`.
