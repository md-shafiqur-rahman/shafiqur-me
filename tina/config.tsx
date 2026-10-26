import React from "react";
import { defineConfig, wrapFieldsWithMeta } from "tinacms";

// Blog editor for shafiqur.me. Articles are saved as Markdown in content/blog/,
// then scripts/build.py turns them into pages.

const SITE = "https://shafiqur.me";

const slugify = (text: string) =>
  (text || "")
    .toLowerCase()
    .replace(/[^a-z0-9\s-]/g, "")
    .trim()
    .replace(/\s+/g, "-")
    .replace(/-+/g, "-");

// ── Rank Math style SEO panel: Google preview + checklist ──────────────────

type Node = { type?: string; text?: string; children?: Node[] };

const textOf = (node?: Node): string =>
  !node ? "" : node.text ?? (node.children || []).map(textOf).join(" ");

const headingsOf = (root?: Node): string[] =>
  (root?.children || []).filter((n) => n.type === "h2" || n.type === "h3").map(textOf);

const firstParagraph = (root?: Node): string =>
  textOf((root?.children || []).find((n) => n.type === "p"));

const count = (haystack: string, needle: string) => {
  if (!needle) return 0;
  const escaped = needle.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  return (haystack.match(new RegExp(escaped, "gi")) || []).length;
};

const colour = (score: number) => (score >= 80 ? "#16a34a" : score >= 50 ? "#d97706" : "#dc2626");

const SeoAnalysis = wrapFieldsWithMeta((props: any) => {
  const [values, setValues] = React.useState<any>(props.form?.getState?.().values || {});
  React.useEffect(() => {
    if (!props.form?.subscribe) return;
    return props.form.subscribe((state: any) => setValues(state.values), { values: true });
  }, [props.form]);

  const path: string = props.tinaForm?.path || "";
  const fileSlug = path.split("/").pop()?.replace(/\.mdx?$/, "") || "";
  const slug = values.filename || fileSlug || slugify(values.title);

  const keyword = (values.seo?.focusKeyword || "").trim().toLowerCase();
  const title = values.title || "";
  const metaTitle = values.seo?.metaTitle || `${title} — Md Shafiqur Rahman`;
  const description = values.seo?.metaDescription || "";
  const bodyText = textOf(values.body);
  const words = bodyText.split(/\s+/).filter(Boolean).length;
  const heads = headingsOf(values.body).join(" ").toLowerCase();
  const hits = count(bodyText, keyword);
  const density = words ? (hits / words) * 100 : 0;
  const has = (s: string) => !!keyword && s.toLowerCase().includes(keyword);
  const keywordSlug = slugify(keyword);

  const checks: [boolean, string][] = [
    [!!keyword, keyword ? `Focus keyword: "${keyword}"` : "Add a focus keyword"],
    [has(title), "Focus keyword in the title (H1)"],
    [has(metaTitle), "Focus keyword in the meta title"],
    [has(description), "Focus keyword in the meta description"],
    [!!keywordSlug && slug.includes(keywordSlug), "Focus keyword in the URL (slug)"],
    [has(firstParagraph(values.body)), "Focus keyword in the first paragraph"],
    [has(heads), "Focus keyword in an H2 or H3 heading"],
    [!!keyword && density >= 0.5 && density <= 2.5, `Keyword density ${density.toFixed(1)}% (aim for 0.5–2.5%)`],
    [metaTitle.length >= 30 && metaTitle.length <= 60, `Meta title length ${metaTitle.length} (aim for 30–60)`],
    [description.length >= 120 && description.length <= 160, `Meta description length ${description.length} (aim for 120–160)`],
    [words >= 600, `Content length ${words} words (aim for 600+)`],
    [(values.faq || []).length > 0, "FAQ added (helps AI search and rich results)"],
  ];
  const passed = checks.filter(([ok]) => ok).length;
  const score = Math.round((passed / checks.length) * 100);

  const box = { border: "1px solid #e5e7eb", borderRadius: 8, background: "#fff", padding: 14, marginBottom: 12 };
  return (
    <div style={{ fontSize: 13, lineHeight: 1.45 }}>
      <div style={{ ...box, display: "flex", alignItems: "center", gap: 12 }}>
        <div style={{ width: 52, height: 52, borderRadius: "50%", border: `4px solid ${colour(score)}`, display: "grid", placeItems: "center", fontWeight: 700, fontSize: 16, color: colour(score) }}>
          {score}
        </div>
        <div>
          <div style={{ fontWeight: 600 }}>SEO score</div>
          <div style={{ color: "#6b7280" }}>{passed} of {checks.length} checks passed</div>
        </div>
      </div>

      <div style={box}>
        <div style={{ color: "#6b7280", fontSize: 11, marginBottom: 6, textTransform: "uppercase", letterSpacing: ".04em" }}>Google preview</div>
        <div style={{ color: "#202124", fontSize: 12 }}>{`${SITE.replace("https://", "")} › blog › ${slug || "your-slug"}`}</div>
        <div style={{ color: "#1a0dab", fontSize: 18, margin: "2px 0" }}>{metaTitle.length > 60 ? metaTitle.slice(0, 57) + "..." : metaTitle || "Your title"}</div>
        <div style={{ color: "#4d5156" }}>{description ? (description.length > 160 ? description.slice(0, 157) + "..." : description) : "Write a meta description so Google shows your own summary."}</div>
      </div>

      <ul style={{ ...box, listStyle: "none", margin: 0 }}>
        {checks.map(([ok, label]) => (
          <li key={label} style={{ display: "flex", gap: 8, padding: "3px 0" }}>
            <span style={{ color: ok ? "#16a34a" : "#dc2626", fontWeight: 700 }}>{ok ? "✓" : "✕"}</span>
            <span>{label}</span>
          </li>
        ))}
      </ul>
    </div>
  );
});

export default defineConfig({
  branch: process.env.VERCEL_GIT_COMMIT_REF || process.env.HEAD || "main",
  clientId: process.env.TINA_CLIENT_ID,
  token: process.env.TINA_TOKEN,

  build: {
    publicFolder: ".",
    outputFolder: "admin",
  },
  media: {
    tina: {
      publicFolder: "",
      mediaRoot: "images/blog",
    },
  },

  schema: {
    collections: [
      {
        name: "post",
        label: "Blog posts",
        path: "content/blog",
        format: "md",
        defaultItem: () => ({
          published: false,
          settings: { date: new Date().toISOString(), readTime: "5 min read", category: "automation" },
        }),
        ui: {
          // The file name is the URL slug: /blog/<slug>/
          filename: {
            readonly: false,
            slugify: (values) => slugify(values?.title),
            description: "This is the slug. The article's address will be shafiqur.me/blog/<slug>/. Don't change it after publishing.",
          },
        },
        fields: [
          {
            type: "string",
            name: "title",
            label: "Title (H1)",
            isTitle: true,
            required: true,
            description: "The article's main heading. Inside the content, use H2 and H3 only.",
          },
          {
            type: "rich-text",
            name: "body",
            label: "Content",
            isBody: true,
          },
          {
            type: "object",
            name: "faq",
            label: "FAQ (questions & answers)",
            list: true,
            description: "Shown at the end of the article and added as FAQ schema for Google and AI search.",
            ui: { itemProps: (item) => ({ label: item?.question || "New question" }) },
            fields: [
              { type: "string", name: "question", label: "Question", required: true },
              { type: "string", name: "answer", label: "Answer", required: true, ui: { component: "textarea" } },
            ],
          },
          {
            type: "boolean",
            name: "published",
            label: "Published",
            description: "Off = draft. Drafts are saved but not shown on the website.",
          },
          {
            type: "object",
            name: "seo",
            label: "SEO — focus keyword, meta title & description",
            fields: [
              {
                type: "string",
                name: "focusKeyword",
                label: "Focus keyword",
                description: 'The main search phrase this article should rank for, e.g. "cabinet maker seo".',
              },
              {
                type: "string",
                name: "analysis",
                label: "SEO analysis",
                ui: { component: SeoAnalysis },
              },
              {
                type: "string",
                name: "metaTitle",
                label: "Meta title",
                description: "The title shown in Google. Leave empty to use the article title. Aim for 30–60 characters.",
              },
              {
                type: "string",
                name: "metaDescription",
                label: "Meta description",
                required: true,
                ui: { component: "textarea" },
                description: "Shown in Google and on the blog list. Aim for 120–160 characters.",
              },
            ],
          },
          {
            type: "object",
            name: "social",
            label: "Social — Facebook, LinkedIn & X preview",
            fields: [
              { type: "string", name: "title", label: "Social title", description: "Leave empty to use the meta title." },
              { type: "string", name: "description", label: "Social description", ui: { component: "textarea" }, description: "Leave empty to use the meta description." },
              { type: "image", name: "image", label: "Social image", description: "1200 × 630 px works best. Leave empty to use the featured image." },
            ],
          },
          {
            type: "object",
            name: "settings",
            label: "Post settings — featured image, category, tags, date",
            fields: [
              { type: "image", name: "image", label: "Featured image", description: "Shown at the top of the article and on the blog list." },
              { type: "string", name: "imageAlt", label: "Featured image alt text", description: "Describe the image for Google and screen readers." },
              {
                type: "string",
                name: "category",
                label: "Category",
                options: [
                  { value: "local seo", label: "Local SEO" },
                  { value: "automation", label: "Automation" },
                  { value: "n8n", label: "n8n" },
                  { value: "ai", label: "AI & LLMs" },
                  { value: "ai automation", label: "AI Automation" },
                  { value: "lead generation", label: "Lead Gen" },
                  { value: "business", label: "Business" },
                  { value: "tutorial", label: "Tutorial" },
                ],
              },
              { type: "string", name: "tags", label: "Tags", list: true, ui: { component: "tags" } },
              { type: "datetime", name: "date", label: "Publish date", ui: { dateFormat: "YYYY-MM-DD" } },
              { type: "string", name: "readTime", label: "Reading time", description: 'For example "8 min read".' },
              { type: "boolean", name: "featured", label: "Featured" },
            ],
          },
        ],
      },
    ],
  },
});
