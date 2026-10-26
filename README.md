# shafiqur.me

Portfolio site of Md Shafiqur Rahman: AI agents & automation, and local SEO for woodworking businesses.

Plain static HTML, CSS and JavaScript. Hosted on Vercel. The contact and chat forms send messages to email through Web3Forms.

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

Vercel publishes the repo as a static site. Commit the rebuilt pages and push; Vercel deploys automatically.
