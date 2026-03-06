/**
 * Parse name and role from resume HTML for filename and display.
 */

export function parseResumeNameAndRole(html: string): { name: string; role: string } {
  if (typeof document === "undefined" || !html) {
    return { name: "Resume", role: "resume" };
  }
  try {
    const doc = new DOMParser().parseFromString(html, "text/html");
    const nameEl = doc.querySelector(".resume-header .name");
    const roleEl = doc.querySelector(".resume-header .role-line");
    const name = (nameEl?.textContent ?? "").trim() || "Resume";
    const role = (roleEl?.textContent ?? "").trim() || "resume";
    return { name, role };
  } catch {
    return { name: "Resume", role: "resume" };
  }
}

/** Safe filename: {name}_{role_only}.pdf (role = job title only, no skills after |) */
export function getResumePdfFilename(html: string): string {
  const { name, role } = parseResumeNameAndRole(html);
  const roleOnly = role.split("|")[0].trim() || role;
  const safe = (s: string) => s.replace(/[^\w\s-]/g, "").replace(/\s+/g, "_").trim() || "resume";
  return `${safe(name)}_${safe(roleOnly)}.pdf`;
}
