"use client";

import { Suspense, useState, useMemo, useCallback, useEffect, useRef } from "react";
import { useSearchParams } from "next/navigation";
import Fuse, { type IFuseOptions } from "fuse.js";
import { Search, Sparkles, X, Tag } from "lucide-react";
import PromptCard from "@/components/PromptCard";
import { type Prompt, ALL_CATEGORIES, getCategoryColor } from "@/lib/utils";

// Import JSON at build time — loaded client-side for instant search
import promptsData from "@/data/prompts.json";

const allPrompts: Prompt[] = promptsData as Prompt[];

const ITEMS_PER_PAGE = 30;

const fuseOptions: IFuseOptions<Prompt> = {
  keys: [
    { name: "title", weight: 0.7 },
    { name: "body", weight: 0.3 },
  ],
  threshold: 0.35,
  ignoreLocation: true,
  minMatchCharLength: 2,
};

export default function HomePage() {
  return (
    <Suspense>
      <HomePageInner />
    </Suspense>
  );
}

function HomePageInner() {
  const searchParams = useSearchParams();
  const initialCategory = searchParams.get("category");

  const [query, setQuery] = useState("");
  const [activeCategory, setActiveCategory] = useState<string | null>(initialCategory);
  const [displayCount, setDisplayCount] = useState(ITEMS_PER_PAGE);
  const inputRef = useRef<HTMLInputElement>(null);
  const sentinelRef = useRef<HTMLDivElement>(null);

  // Build Fuse index once
  const fuse = useMemo(() => new Fuse(allPrompts, fuseOptions), []);

  // Search + category filter
  const results = useMemo(() => {
    let items = allPrompts;

    // Text search
    if (query.trim()) {
      items = fuse.search(query.trim()).map((r) => r.item);
    }

    // Category filter
    if (activeCategory) {
      items = items.filter((p) => p.categories?.includes(activeCategory));
    }

    return items;
  }, [query, activeCategory, fuse]);

  // Reset pagination when filters change
  useEffect(() => {
    setDisplayCount(ITEMS_PER_PAGE);
  }, [query, activeCategory]);

  // Infinite scroll via IntersectionObserver
  useEffect(() => {
    const sentinel = sentinelRef.current;
    if (!sentinel) return;

    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && displayCount < results.length) {
          setDisplayCount((prev) => Math.min(prev + ITEMS_PER_PAGE, results.length));
        }
      },
      { rootMargin: "200px" }
    );

    observer.observe(sentinel);
    return () => observer.disconnect();
  }, [displayCount, results.length]);

  // Keyboard shortcut: "/" to focus search
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === "/" && document.activeElement !== inputRef.current) {
        e.preventDefault();
        inputRef.current?.focus();
      }
      if (e.key === "Escape") {
        inputRef.current?.blur();
        setQuery("");
        setActiveCategory(null);
      }
    };
    document.addEventListener("keydown", handler);
    return () => document.removeEventListener("keydown", handler);
  }, []);

  const clearAll = useCallback(() => {
    setQuery("");
    setActiveCategory(null);
    inputRef.current?.focus();
  }, []);

  const toggleCategory = useCallback((cat: string) => {
    setActiveCategory((prev) => (prev === cat ? null : cat));
  }, []);

  // Count per category (from current text-search results, not filtered by category)
  const categoryCounts = useMemo(() => {
    const base = query.trim()
      ? fuse.search(query.trim()).map((r) => r.item)
      : allPrompts;
    const counts: Record<string, number> = {};
    for (const cat of ALL_CATEGORIES) {
      counts[cat] = base.filter((p) => p.categories?.includes(cat)).length;
    }
    return counts;
  }, [query, fuse]);

  const visiblePrompts = results.slice(0, displayCount);
  const hasActiveFilters = query.trim() || activeCategory;

  return (
    <>
      {/* Fixed Header */}
      <header className="sticky top-0 z-40 bg-white/80 backdrop-blur-xl border-b border-gray-200/60">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 py-4">
          {/* Brand */}
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-violet-600 flex items-center justify-center">
                <Sparkles className="w-4 h-4 text-white" />
              </div>
              <h1 className="text-lg font-bold text-gray-900 tracking-tight">
                Prompt Aggregator
              </h1>
            </div>
            <span className="text-xs text-gray-400 font-mono">
              {allPrompts.length} prompts
            </span>
          </div>

          {/* Search */}
          <div className="relative mb-3">
            <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4.5 h-4.5 text-gray-400 pointer-events-none" />
            <input
              ref={inputRef}
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder='プロンプトを検索… (Press "/" to focus)'
              className="w-full pl-10 pr-10 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm text-gray-900 placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500/30 focus:border-blue-400 transition-all"
              autoComplete="off"
              spellCheck={false}
            />
            {query && (
              <button
                onClick={() => setQuery("")}
                className="absolute right-3 top-1/2 -translate-y-1/2 p-0.5 text-gray-400 hover:text-gray-600 transition-colors"
                aria-label="検索をクリア"
              >
                <X className="w-4 h-4" />
              </button>
            )}
          </div>

          {/* Category filter chips */}
          <div className="flex flex-wrap gap-1.5">
            {ALL_CATEGORIES.map((cat) => {
              const isActive = activeCategory === cat;
              const colors = getCategoryColor(cat);
              const count = categoryCounts[cat] ?? 0;
              return (
                <button
                  key={cat}
                  onClick={() => toggleCategory(cat)}
                  className={`inline-flex items-center gap-1 px-2.5 py-1 text-xs font-medium rounded-lg transition-all ${
                    isActive
                      ? `${colors.bg} ${colors.text} ring-1 ring-current/20 shadow-sm`
                      : `text-gray-500 hover:text-gray-700 hover:bg-gray-100`
                  }`}
                >
                  <Tag className="w-3 h-3" />
                  {cat.replace("#", "")}
                  <span className={`ml-0.5 text-[10px] ${isActive ? "opacity-80" : "text-gray-400"}`}>
                    {count}
                  </span>
                </button>
              );
            })}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-5xl mx-auto px-4 sm:px-6 py-6">
        {/* Active filter summary */}
        {hasActiveFilters && (
          <div className="flex items-center justify-between mb-4">
            <p className="text-sm text-gray-500">
              {activeCategory && (
                <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-xs font-medium mr-2 ${getCategoryColor(activeCategory).bg} ${getCategoryColor(activeCategory).text}`}>
                  {activeCategory.replace("#", "")}
                </span>
              )}
              {query.trim() && <>「{query}」</>}
              {" "}
              <span className="font-semibold text-gray-700">{results.length}</span> 件
            </p>
            <button
              onClick={clearAll}
              className="text-xs text-gray-400 hover:text-gray-600 transition-colors"
            >
              フィルターをクリア
            </button>
          </div>
        )}

        {/* Grid */}
        {visiblePrompts.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {visiblePrompts.map((prompt) => (
              <PromptCard
                key={prompt.id}
                prompt={prompt}
                onCategoryClick={toggleCategory}
                activeCategory={activeCategory}
              />
            ))}
          </div>
        ) : (
          <div className="text-center py-20">
            <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gray-100 flex items-center justify-center">
              <Search className="w-7 h-7 text-gray-300" />
            </div>
            <p className="text-gray-500 text-sm">
              一致するプロンプトが見つかりませんでした
            </p>
            <button
              onClick={clearAll}
              className="mt-3 text-sm text-blue-500 hover:text-blue-600 transition-colors"
            >
              フィルターをクリア
            </button>
          </div>
        )}

        {/* Infinite scroll sentinel */}
        {displayCount < results.length && (
          <div ref={sentinelRef} className="flex justify-center py-8">
            <div className="w-6 h-6 border-2 border-gray-200 border-t-blue-500 rounded-full animate-spin" />
          </div>
        )}

        {/* Footer */}
        <footer className="text-center py-8 mt-8 border-t border-gray-100">
          <p className="text-xs text-gray-400">
            Data sourced from{" "}
            <a
              href="https://nanyo-city.jpn.org/prompt/"
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-400 hover:text-blue-500 transition-colors"
            >
              nanyo-city.jpn.org
            </a>
          </p>
        </footer>
      </main>
    </>
  );
}
