/**
 * 100 resume themes: varying primary color and font family.
 * Each theme produces full CSS for the resume HTML structure.
 */

export interface ResumeTheme {
  id: string;
  name: string;
  css: string;
}

function buildThemeCss(primary: string, fontFamily: string): string {
  return `*{box-sizing:border-box}
body{font-family:${fontFamily};font-size:11pt;line-height:1.4;color:#222;max-width:800px;margin:0 auto;padding:24px 32px 32px;background:#fff}
.resume-header{text-align:center;margin-bottom:20px;padding-bottom:16px;border-bottom:2px solid ${primary}}
.resume-header .name{font-size:22pt;font-weight:bold;color:#111;margin:0 0 8px 0;letter-spacing:0.02em}
.resume-header .role-line{font-size:11pt;font-weight:600;color:${primary};margin:0 0 6px 0}
.resume-header .contact{font-size:10pt;color:#444;margin:0}
.resume-header .contact span+span::before{content:" • ";margin:0 6px}
h2.section-title{font-family:${fontFamily};font-size:12pt;font-weight:bold;color:${primary};text-transform:uppercase;letter-spacing:0.05em;margin:18px 0 10px 0;padding-bottom:4px;border-bottom:1px solid #ccc}
.resume-summary{margin:8px 0 4px 0;padding:0;text-align:justify}
.resume-block{margin-bottom:14px}
.resume-block .block-title{font-weight:bold;font-size:11pt;color:#222;margin:0 0 2px 0}
.resume-block .block-subtitle{font-size:10pt;color:#555;margin:0 0 6px 0}
.resume-block ul{margin:0 0 0 18px;padding:0}
.resume-block li{margin-bottom:4px}
.skills-list{margin:6px 0 0 0;padding:0;list-style:none;margin-left:0}
.skills-list li{display:inline}
.skills-list li::after{content:", "}
.skills-list li:last-child::after{content:""}
.skills-category{margin-bottom:6px;line-height:1.4}
.skills-category-name{font-weight:bold;color:#222}
.resume-list{margin:6px 0 0 18px;padding:0}
.resume-list li{margin-bottom:4px}
@media print{body{padding:16px 24px}.resume-header{margin-bottom:14px;padding-bottom:10px}h2.section-title{margin-top:12px}.resume-block{margin-bottom:10px}}`;
}

const COLORS = [
  { name: "Midnight Blue", value: "#191970" },
  { name: "Navy", value: "#000080" },
  { name: "Dark Slate", value: "#2F4F4F" },
  { name: "Teal", value: "#008080" },
  { name: "Olive", value: "#556B2F" },
  { name: "Forest", value: "#228B22" },
  { name: "Crimson", value: "#DC143C" },
  { name: "Dark Magenta", value: "#8B008B" },
  { name: "Indigo", value: "#4B0082" },
  { name: "Saddle Brown", value: "#8B4513" },
  { name: "Steel Blue", value: "#4682B4" },
  { name: "Chocolate", value: "#D2691E" },
  { name: "Dark Cyan", value: "#008B8B" },
  { name: "Maroon", value: "#800000" },
  { name: "Deep Sky", value: "#006994" },
  { name: "Orange Red", value: "#FF4500" },
  { name: "Dim Gray", value: "#696969" },
  { name: "Dark Violet", value: "#9400D3" },
  { name: "Sienna", value: "#A0522D" },
  { name: "Cadet Blue", value: "#5F9EA0" },
];

const FONTS = [
  { name: "Arial", value: "Arial, Helvetica, sans-serif" },
  { name: "Georgia", value: "Georgia, serif" },
  { name: "Segoe UI", value: "'Segoe UI', Tahoma, sans-serif" },
  { name: "Verdana", value: "Verdana, Geneva, sans-serif" },
  { name: "Trebuchet", value: "'Trebuchet MS', sans-serif" },
];

const THEMES: ResumeTheme[] = [];
let id = 1;
for (const color of COLORS) {
  for (const font of FONTS) {
    THEMES.push({
      id: String(id),
      name: `${color.name} • ${font.name}`,
      css: buildThemeCss(color.value, font.value),
    });
    id++;
  }
}

export { THEMES };

/** Replace the resume HTML's embedded style with the given theme CSS. */
export function injectThemeIntoResumeHtml(html: string, themeCss: string): string {
  return html.replace(/<style[^>]*>[\s\S]*?<\/style>/i, `<style>\n${themeCss}\n</style>`);
}

/** Get themed HTML for display/PDF/print. If themeId is null, returns original html. */
export function getThemedResumeHtml(html: string, themeId: string | null): string {
  if (!themeId || !html) return html;
  const theme = THEMES.find((t) => t.id === themeId);
  if (!theme) return html;
  return injectThemeIntoResumeHtml(html, theme.css);
}
