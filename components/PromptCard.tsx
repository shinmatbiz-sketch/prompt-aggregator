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
      <Link href={`/${prompt.id}`} className="group block h-full">
        <article className="neo-card rounded-2xl p-5 cursor-pointer group flex flex-col h-full bg-white transition-all duration-300">

          <div className="flex justify-between items-start mb-3">
            <div className="flex flex-wrap gap-1.5">
              {prompt.categories && prompt.categories.slice(0, 3).map((cat) => (
                <span key={cat} className="text-[10px] px-1.5 py-0.5 rounded bg-slate-100 text-slate-500 font-medium">
                  {cat.replace("#", "")}
                </span>
              ))}
            </div>
            <span className="text-[10px] font-mono text-slate-300 group-hover:text-brand-400 transition-colors">
              #{prompt.id}
            </span>
          </div>

          <h3 className="text-base font-bold text-slate-800 mb-2 leading-snug group-hover:text-brand-600 transition-colors line-clamp-2">
            {cleanTitle(prompt.title)}
          </h3>

          <p className="text-xs text-slate-500 leading-relaxed line-clamp-4 font-mono mb-4 flex-grow">
            {truncate(prompt.body.replace(/[\n\r]+/g, " "), 120)}
          </p>

          <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-400">
            <span className="flex items-center gap-1 group-hover:text-brand-500 transition-colors">
              View details
            </span>
            <ArrowRight className="w-3 h-3 -ml-2 opacity-0 -translate-x-2 group-hover:opacity-100 group-hover:translate-x-0 transition-all" />
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

