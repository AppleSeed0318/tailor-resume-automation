/** Shared storage key and type for saved resumes (home + history). */

export const STORAGE_KEY = "resume-tailor-saved";

export interface SavedItem {
  id: string;
  companyName: string;
  jobDescription: string;
  resumeHtml: string;
  roleLine: string;
  createdAt: string;
}

export function getSavedItems(): SavedItem[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw) as SavedItem[];
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

export function setSavedItems(items: SavedItem[]): void {
  if (typeof window === "undefined") return;
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(items));
  } catch {
    // ignore
  }
}
