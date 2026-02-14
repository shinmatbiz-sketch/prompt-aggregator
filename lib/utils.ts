export interface Prompt {
  id: string;
  title: string;
  body: string;
  url: string;
  categories?: string[];
}

export const ALL_CATEGORIES = [
  "#文章作成・要約",
  "#文書校正・編集",
  "#アイデア創出・企画",
  "#業務改善",
  "#情報収集・分析",
  "#コミュニケーション支援",
  "#プログラミング",
  "#意識改革・スキルアップ",
] as const;

export type Category = (typeof ALL_CATEGORIES)[number];

const CATEGORY_COLORS: Record<string, { bg: string; text: string; hover: string }> = {
  "#文章作成・要約":       { bg: "bg-amber-50",   text: "text-amber-700",   hover: "hover:bg-amber-100" },
  "#文書校正・編集":       { bg: "bg-rose-50",    text: "text-rose-700",    hover: "hover:bg-rose-100" },
  "#アイデア創出・企画":   { bg: "bg-violet-50",  text: "text-violet-700",  hover: "hover:bg-violet-100" },
  "#業務改善":             { bg: "bg-emerald-50", text: "text-emerald-700", hover: "hover:bg-emerald-100" },
  "#情報収集・分析":       { bg: "bg-sky-50",     text: "text-sky-700",     hover: "hover:bg-sky-100" },
  "#コミュニケーション支援": { bg: "bg-pink-50",  text: "text-pink-700",    hover: "hover:bg-pink-100" },
  "#プログラミング":       { bg: "bg-cyan-50",    text: "text-cyan-700",    hover: "hover:bg-cyan-100" },
  "#意識改革・スキルアップ": { bg: "bg-orange-50", text: "text-orange-700",  hover: "hover:bg-orange-100" },
};

export function getCategoryColor(cat: string) {
  return CATEGORY_COLORS[cat] ?? { bg: "bg-gray-50", text: "text-gray-700", hover: "hover:bg-gray-100" };
}

/**
 * Strip the "#001_" prefix from a prompt title for display.
 */
export function cleanTitle(title: string): string {
  return title.replace(/^#\d{3}[_\s]?/, "").trim();
}

/**
 * Truncate text to maxLen characters, appending "…" if truncated.
 */
export function truncate(text: string, maxLen: number): string {
  if (text.length <= maxLen) return text;
  return text.slice(0, maxLen).trimEnd() + "…";
}

/**
 * Build ChatGPT URL with pre-filled prompt.
 */
export function buildChatGPTUrl(promptText: string): string {
  const encoded = encodeURIComponent(promptText);
  return `https://chatgpt.com/?q=${encoded}`;
}

/**
 * Build Gemini URL with pre-filled prompt.
 */
export function buildGeminiUrl(promptText: string): string {
  const encoded = encodeURIComponent(promptText);
  return `https://gemini.google.com/app?q=${encoded}`;
}

/**
 * Copy text to clipboard. Returns true on success.
 */
export async function copyToClipboard(text: string): Promise<boolean> {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch {
    // Fallback for older browsers
    const textarea = document.createElement("textarea");
    textarea.value = text;
    textarea.style.position = "fixed";
    textarea.style.opacity = "0";
    document.body.appendChild(textarea);
    textarea.select();
    try {
      document.execCommand("copy");
      return true;
    } catch {
      return false;
    } finally {
      document.body.removeChild(textarea);
    }
  }
}

/**
 * Format prompt ID for display: "001" -> "#001"
 */
export function formatId(id: string): string {
  return `#${id}`;
}
