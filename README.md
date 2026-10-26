# shafiqur.me

Portfolio site of Md Shafiqur Rahman: AI agents & automation, and local SEO for woodworking businesses.

Plain static HTML, CSS and JavaScript. Hosted on Vercel. The contact and chat forms send messages to email through Web3Forms.

## Pages

- `/` home
- `/ai-automation/` AI agents & automation service
- `/local-seo/` local SEO service
- `/blog/` articles, generated from `content/blog/*.md`
- `/projects/` case studies, generated from `content/projects/*.md` (screenshots and `workflow.json` live in `projects/<slug>/`)

## Writing articles

Articles are written in the TinaCMS editor at `/admin/` (log in with your Tina Cloud account). Saving commits the Markdown file to `content/blog/` on GitHub, and Vercel rebuilds the site.

Fields: title (H1), meta title, meta description, slug (the file name), date, category, published/draft, FAQ (adds FAQ schema), and the content.

To run the editor on your own computer (no login needed, saves to local files):

```
npm install
npm run dev
```

Then open http://localhost:8766/admin/index.html

## Build

`npm run build` builds the editor, generates every page, `sitemap.xml` and `llms.txt` (`scripts/build.py`), and copies the publishable site to `dist/` (`scripts/dist.py`). Python libraries are bundled in `scripts/vendor/`, so no `pip install` is needed.

## Vercel

Settings come from `vercel.json`. Add two environment variables in Vercel (Settings → Environment Variables): `TINA_CLIENT_ID` and `TINA_TOKEN`, both from app.tina.io.
