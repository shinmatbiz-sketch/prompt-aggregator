"use client";

import { useState, useCallback } from "react";
import Link from "next/link";
import { Copy, ExternalLink, ArrowRight } from "lucide-react";
import { type Prompt, cleanTitle, truncate, buildChatGPTUrl, buildGeminiUrl, copyToClipboard, formatId, getCategoryColor } from "@/lib/utils";
import Toast from "./Toast";

interface PromptCardProps {
  prompt: Prompt;
  onCategoryClick?: (cat: string) => void;
  activeCategory?: string | null;
}

export default function PromptCard({ prompt, onCategoryClick, activeCategory }: PromptCardProps) {
  const [toast, setToast] = useState(false);

  const handleCopy = useCallback(async (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    const ok = await copyToClipboard(prompt.body);
    if (ok) setToast(true);
  }, [prompt.body]);

  const handleOpenAI = useCallback((e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    window.open(buildChatGPTUrl(prompt.body), "_blank", "noopener");
  }, [prompt.body]);

  const handleOpenGemini = useCallback((e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    window.open(buildGeminiUrl(prompt.body), "_blank", "noopener");
  }, [prompt.body]);

  const handleCategoryClick = useCallback((e: React.MouseEvent, cat: string) => {
    e.preventDefault();
    e.stopPropagation();
    onCategoryClick?.(cat);
  }, [onCategoryClick]);

  return (
    <>
      <Link href={`/${prompt.id}`} className="group block">
        <article className="relative bg-white rounded-xl border border-gray-200/80 p-5 transition-all duration-200 hover:shadow-md hover:border-gray-300 hover:-translate-y-0.5">
          {/* ID badge */}
          <span className="inline-block text-xs font-mono text-gray-400 mb-2">
            {formatId(prompt.id)}
          </span>

          {/* Title */}
          <h2 className="text-base font-semibold text-gray-900 leading-snug mb-2 group-hover:text-blue-600 transition-colors line-clamp-2">
            {cleanTitle(prompt.title)}
          </h2>

          {/* Category tags */}
          {prompt.categories && prompt.categories.length > 0 && (
            <div className="flex flex-wrap gap-1 mb-3">
              {prompt.categories.map((cat) => {
                const colors = getCategoryColor(cat);
                const isActive = activeCategory === cat;
                return (
                  <button
                    key={cat}
                    onClick={(e) => handleCategoryClick(e, cat)}
                    className={`px-1.5 py-0.5 text-[10px] font-medium rounded-md transition-all ${colors.bg} ${colors.text} ${colors.hover} ${
                      isActive ? "ring-1 ring-current/30" : ""
                    }`}
                  >
                    {cat.replace("#", "")}
                  </button>
                );
              })}
            </div>
          )}

          {/* Body preview */}
          <p className="text-sm text-gray-500 leading-relaxed mb-4 line-clamp-3">
            {truncate(prompt.body.replace(/[\n\r]+/g, " "), 120)}
          </p>

          {/* Actions */}
          <div className="flex items-center gap-2">
            <button
              onClick={handleCopy}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-gray-600 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors"
              aria-label="プロンプトをコピー"
            >
              <Copy className="w-3.5 h-3.5" />
              コピー
            </button>

            <button
              onClick={handleOpenAI}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-blue-600 bg-blue-50 hover:bg-blue-100 rounded-lg transition-colors"
              aria-label="ChatGPTで開く"
            >
              <ExternalLink className="w-3.5 h-3.5" />
              ChatGPT
            </button>

            <button
              onClick={handleOpenGemini}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-indigo-600 bg-indigo-50 hover:bg-indigo-100 rounded-lg transition-colors"
              aria-label="Geminiで開く"
            >
              <ExternalLink className="w-3.5 h-3.5" />
              Gemini
            </button>

            <span className="ml-auto text-gray-300 group-hover:text-blue-400 transition-colors">
              <ArrowRight className="w-4 h-4" />
            </span>
          </div>
        </article>
      </Link>

      <Toast
        message="コピーしました"
        visible={toast}
        onClose={() => setToast(false)}
      />
    </>
  );
}
