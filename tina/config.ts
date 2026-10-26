import { defineConfig } from "tinacms";

// Blog editor for shafiqur.me. Articles are saved as Markdown in content/blog/,
// then scripts/build.py turns them into pages.
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
          date: new Date().toISOString(),
          readTime: "5 min read",
          category: "automation",
          published: false,
        }),
        ui: {
          // The file name is the URL slug: /blog/<slug>/
          filename: {
            readonly: false,
            slugify: (values) =>
              (values?.title || "")
                .toLowerCase()
                .replace(/[^a-z0-9\s-]/g, "")
                .trim()
                .replace(/\s+/g, "-")
                .replace(/-+/g, "-"),
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
            type: "string",
            name: "seoTitle",
            label: "Meta title",
            description: "The title shown in Google. Leave empty to use the article title. Aim for under 60 characters.",
          },
          {
            type: "string",
            name: "excerpt",
            label: "Meta description",
            required: true,
            ui: { component: "textarea" },
            description: "Shown in Google and on the blog list. Aim for 140–160 characters.",
          },
          {
            type: "datetime",
            name: "date",
            label: "Publish date",
            ui: { dateFormat: "YYYY-MM-DD" },
          },
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
          { type: "string", name: "readTime", label: "Reading time", description: 'For example "8 min read".' },
          {
            type: "boolean",
            name: "published",
            label: "Published",
            description: "Off = draft. Drafts are saved but not shown on the website.",
          },
          { type: "boolean", name: "featured", label: "Featured" },
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
            type: "rich-text",
            name: "body",
            label: "Content",
            isBody: true,
          },
        ],
      },
    ],
  },
});
