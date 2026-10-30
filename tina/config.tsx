import React from "react";
import { defineConfig, wrapFieldsWithMeta } from "tinacms";

// Blog editor for shafiqur.me. Articles are saved as Markdown in content/blog/,
// then scripts/build.py turns them into pages.
//
// Layout: the article (title, content, FAQ) on the left and a WordPress / Rank Math
// style sidebar on the right. The sidebar fields come first in the schema so they
// can float to the right of the article; the CSS is in SIDEBAR_CSS below.

const SITE = "https://shafiqur.me";

const slugify = (text: string) =>
  (text || "")
    .toLowerCase()
    .replace(/[^a-z0-9\s-]/g, "")
    .trim()
    .replace(/\s+/g, "-")
    .replace(/-+/g, "-");

// The form's field list is the flex-wrap div that holds the title input.
const LIST = 'div.flex-wrap:has(> div input[name="title"])';
const MAIN = [
  ':has(input[name="title"])',
  ":has([data-slate-editor])",
  ':has(label[for="body"])', // also matches in Raw Markdown mode, when the Slate editor is gone
  ':has([data-test="list-faq"])',
  '[data-test="list-faq"]',
]
  .map((s) => `${LIST} > div${s}`)
  .join(",\n");

const SIDEBAR_CSS = `
@media (min-width: 1000px) {
  ${LIST} { display: flow-root !important; }
  ${LIST} > div {
    float: right; clear: right; width: 340px; margin: 0 0 0 0 !important;
    padding: 10px 16px 6px !important; background: #fff;
    border-left: 1px solid #e5e7eb; border-right: 1px solid #e5e7eb;
  }
  ${LIST} > div:has(.sidebar-head) { margin-top: 18px !important; border-top: 1px solid #e5e7eb; border-radius: 10px 10px 0 0; padding-top: 0 !important; }
  ${LIST} > div:has(.sidebar-head):first-child { margin-top: 0 !important; }
  ${LIST} > div:has(+ div .sidebar-head), ${LIST} > div:has(+ div input[name="title"]) { border-bottom: 1px solid #e5e7eb; border-radius: 0 0 10px 10px; padding-bottom: 14px !important; }
  /* New article only: the slug box sits at the top of the sidebar */
  ${LIST} { position: relative; }
  ${LIST}:has(input[name="filename"]) > div:first-child { margin-top: 150px !important; }
  ${LIST} > div:has(input[name="filename"]) {
    position: absolute; top: 0; right: 0; float: none; height: 132px; overflow: hidden;
    border: 1px solid #e5e7eb; border-radius: 10px; padding: 12px 16px !important;
  }
  ${MAIN} {
    float: none; clear: none; width: auto; margin: 0 364px 22px 0 !important;
    padding: 0 !important; background: none; border: 0; border-radius: 0;
  }
}
.sidebar-head { margin: 0 -16px 4px; padding: 11px 16px; border-bottom: 1px solid #e5e7eb; font-weight: 600; font-size: 14px; color: #111827; display: flex; align-items: center; gap: 8px; }
.sidebar-head span { color: #ec4815; }
`;

const SidebarHead = (label: string, icon: string, withCss = false) =>
  function Head() {
    return (
      <div>
        {withCss && <style>{SIDEBAR_CSS}</style>}
        <div className="sidebar-head"><span>{icon}</span>{label}</div>
      </div>
    );
  };

// ── Rank Math style SEO analysis: score, Google preview and checklist ──────

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

  const keyword = (values.focusKeyword || "").trim().toLowerCase();
  const title = values.title || "";
  const metaTitle = values.metaTitle || (title ? `${title} — Md Shafiqur Rahman` : "");
  const description = values.metaDescription || "";
  const bodyText = textOf(values.body);
  const words = bodyText.split(/\s+/).filter(Boolean).length;
  const heads = headingsOf(values.body).join(" ").toLowerCase();
  const hits = count(bodyText, keyword);
  const density = words ? (hits / words) * 100 : 0;
  const has = (s: string) => !!keyword && s.toLowerCase().includes(keyword);
  const keywordSlug = slugify(keyword);

  const checks: [boolean, string][] = [
    [!!keyword, keyword ? `Focus keyword: "${keyword}"` : "Add a focus keyword"],
    [has(title), "Keyword in the title (H1)"],
    [has(metaTitle), "Keyword in the meta title"],
    [has(description), "Keyword in the meta description"],
    [!!keywordSlug && slug.includes(keywordSlug), "Keyword in the URL (slug)"],
    [has(firstParagraph(values.body)), "Keyword in the first paragraph"],
    [has(heads), "Keyword in an H2 or H3 heading"],
    [!!keyword && density >= 0.5 && density <= 2.5, `Keyword density ${density.toFixed(1)}% (0.5–2.5%)`],
    [metaTitle.length >= 30 && metaTitle.length <= 60, `Meta title ${metaTitle.length} chars (30–60)`],
    [description.length >= 120 && description.length <= 160, `Meta description ${description.length} chars (120–160)`],
    [words >= 600, `Content ${words} words (600+)`],
    [(values.faq || []).length > 0, "FAQ added"],
  ];
  const passed = checks.filter(([ok]) => ok).length;
  const score = Math.round((passed / checks.length) * 100);

  const box = { border: "1px solid #e5e7eb", borderRadius: 8, background: "#f9fafb", padding: 12, marginBottom: 10 };
  return (
    <div style={{ fontSize: 12.5, lineHeight: 1.45, whiteSpace: "normal" }}>
      <div style={{ ...box, display: "flex", alignItems: "center", gap: 12 }}>
        <div style={{ width: 46, height: 46, flex: "none", borderRadius: "50%", border: `4px solid ${colour(score)}`, display: "grid", placeItems: "center", fontWeight: 700, fontSize: 15, color: colour(score) }}>
          {score}
        </div>
        <div>
          <div style={{ fontWeight: 600 }}>SEO score</div>
          <div style={{ color: "#6b7280" }}>{passed} of {checks.length} checks passed</div>
        </div>
      </div>

      <div style={box}>
        <div style={{ color: "#6b7280", fontSize: 10.5, marginBottom: 6, textTransform: "uppercase", letterSpacing: ".04em" }}>Google preview</div>
        <div style={{ color: "#202124", fontSize: 11.5, wordBreak: "break-all" }}>{`${SITE.replace("https://", "")} › blog › ${slug || "your-slug"}`}</div>
        <div style={{ color: "#1a0dab", fontSize: 16, margin: "2px 0" }}>{metaTitle.length > 60 ? metaTitle.slice(0, 57) + "..." : metaTitle || "Your title"}</div>
        <div style={{ color: "#4d5156" }}>{description ? (description.length > 160 ? description.slice(0, 157) + "..." : description) : "Write a meta description so Google shows your own summary."}</div>
      </div>

      <ul style={{ ...box, listStyle: "none", margin: 0 }}>
        {checks.map(([ok, label]) => (
          <li key={label} style={{ display: "flex", gap: 7, padding: "2px 0" }}>
            <span style={{ color: ok ? "#16a34a" : "#dc2626", fontWeight: 700 }}>{ok ? "✓" : "✕"}</span>
            <span>{label}</span>
          </li>
        ))}
      </ul>
    </div>
  );
});

const head = (name: string, label: string, icon: string, withCss = false) => ({
  type: "string" as const,
  name,
  label,
  ui: { component: SidebarHead(label, icon, withCss) },
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
          date: new Date().toISOString(),
          readTime: "5 min read",
          category: "automation",
        }),
        ui: {
          // The file name is the URL slug: /blog/<slug>/
          filename: {
            readonly: false,
            slugify: (values) => slugify(values?.title),
            description: "The URL slug: shafiqur.me/blog/your-slug/. Don't change it after publishing.",
          },
        },
        fields: [
          // ── Sidebar (floats right) ─────────────────────────────────────
          head("sectionPublish", "Publish", "●", true),
          {
            type: "boolean",
            name: "published",
            label: "Published",
            description: "Off = draft (saved, not shown on the website).",
          },
          { type: "datetime", name: "date", label: "Publish date", ui: { dateFormat: "YYYY-MM-DD" } },

          head("sectionSeo", "SEO (Rank Math style)", "◎"),
          {
            type: "string",
            name: "focusKeyword",
            label: "Focus keyword",
            description: 'The main search phrase, e.g. "cabinet maker seo".',
          },
          { type: "string", name: "seoAnalysis", label: "SEO analysis", ui: { component: SeoAnalysis } },
          {
            type: "string",
            name: "metaTitle",
            label: "Meta title",
            description: "Shown in Google. Empty = article title. 30–60 characters.",
          },
          {
            type: "string",
            name: "metaDescription",
            label: "Meta description",
            ui: { component: "textarea" },
            description: "Shown in Google and on the blog list. 120–160 characters. Empty = the first paragraph.",
          },

          head("sectionSettings", "Post settings", "▤"),
          { type: "image", name: "image", label: "Featured image", description: "Top of the article and on the blog list." },
          { type: "string", name: "imageAlt", label: "Featured image alt text" },
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
          { type: "string", name: "readTime", label: "Reading time", description: 'e.g. "8 min read".' },
          { type: "boolean", name: "featured", label: "Featured" },

          head("sectionSocial", "Social (Open Graph)", "↗"),
          { type: "string", name: "ogTitle", label: "Social title", description: "Facebook, LinkedIn, X. Empty = meta title." },
          { type: "string", name: "ogDescription", label: "Social description", ui: { component: "textarea" }, description: "Empty = meta description." },
          { type: "image", name: "ogImage", label: "Social image", description: "1200 × 630 px. Empty = featured image." },

          // ── Article (left column) ──────────────────────────────────────
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
            description: "To paste Markdown (e.g. from ChatGPT), click the Markdown button in the toolbar first.",
            // "raw" comes first so the Markdown button never hides in the overflow menu.
            overrides: {
              toolbar: ["raw", "heading", "bold", "italic", "link", "ul", "ol", "quote", "image", "table", "code", "hr"],
            },
          },
          {
            type: "object",
            name: "faq",
            label: "FAQ (questions & answers)",
            list: true,
            description: "Shown at the end of the article and added as FAQ schema for Google and AI search.",
            ui: { itemProps: (item) => ({ label: item?.question || "New question" }) },
            fields: [
              { type: "string", name: "question", label: "Question" },
              { type: "string", name: "answer", label: "Answer", ui: { component: "textarea" } },
            ],
          },
        ],
      },
    ],
  },
});
