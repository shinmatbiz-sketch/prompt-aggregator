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
      {/* Sticky Header with Glassmorphism */}
      <header className="sticky top-0 z-50 glass-panel border-b border-white/50 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row items-center justify-between py-4 gap-4">

            {/* Logo area */}
            <div className="flex items-center gap-3 w-full md:w-auto">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-brand-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-brand-500/30 text-white transform hover:rotate-6 transition-transform duration-300">
                <Sparkles className="w-6 h-6 fill-current" />
              </div>
              <div>
                <h1 className="text-xl font-bold tracking-tight text-slate-900 leading-none">Prompt Aggregator <span className="text-brand-600">ver1.0</span></h1>
                <p className="text-xs text-slate-500 font-medium mt-0.5">Local Edition</p>
              </div>
            </div>

            {/* Search Bar */}
            <div className="relative w-full md:max-w-xl group">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Search className="h-5 w-5 text-slate-400 group-focus-within:text-brand-500 transition-colors" />
              </div>
              <input
                ref={inputRef}
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder='Search prompts (keywords, content)...  Press "/" to focus'
                className="block w-full pl-10 pr-4 py-2.5 border-0 rounded-xl leading-5 bg-white/80 text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-brand-500/50 shadow-sm ring-1 ring-slate-200 transition-all"
                autoComplete="off"
              />
              <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
                <span className="text-slate-400 text-xs border border-slate-200 rounded px-1.5 py-0.5 bg-slate-50">/</span>
              </div>
            </div>

            {/* Stats */}
            <div className="hidden md:flex items-center gap-2 text-sm font-medium text-slate-500 bg-white/50 px-3 py-1.5 rounded-lg border border-white/60">
              <span id="total-count">{allPrompts.length}</span> items
            </div>
          </div>

          {/* Category Filter Scrollable Area */}
          <div className="py-3 overflow-x-auto no-scrollbar mask-gradient flex items-center gap-2 pb-4">
            <button
              onClick={clearAll}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold whitespace-nowrap transition-all ${!activeCategory ? "bg-brand-500 text-white shadow-md ring-1 ring-brand-600" : "category-chip text-slate-600"
                }`}
            >
              All
            </button>
            {ALL_CATEGORIES.map((cat) => {
              const isActive = activeCategory === cat;
              return (
                <button
                  key={cat}
                  onClick={() => toggleCategory(cat)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold whitespace-nowrap transition-all ${isActive ? "bg-brand-500 text-white shadow-md ring-1 ring-brand-600" : "category-chip text-slate-600"
                    }`}
                >
                  {cat.replace('#', '')}
                </button>
              );
            })}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-grow container mx-auto px-4 sm:px-6 lg:px-8 py-8">

        {/* Status Bar / Breadcrumbs */}
        <div className="flex items-center justify-between mb-6 animate-fade-in">
          <div className="text-sm text-slate-500 flex items-center gap-2">
            <span className="font-semibold text-slate-700">Results</span>
            <span className="w-1 h-1 bg-slate-400 rounded-full"></span>
            <span>{results.length} items</span>
            {query && <span className="text-xs text-slate-400">(Query: {query})</span>}
          </div>
          {(query || activeCategory) && (
            <button onClick={clearAll} className="text-xs font-medium text-brand-600 hover:text-brand-700 hover:underline flex items-center gap-1 transition-colors">
              Reset Filters
            </button>
          )}
        </div>

        {/* Prompt Grid */}
        {visiblePrompts.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-3 gap-6 animate-fade-in">
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
          <div className="flex flex-col items-center justify-center py-20 text-center animate-fade-in">
            <div className="w-24 h-24 bg-slate-100 rounded-full flex items-center justify-center mb-6">
              <Search className="w-12 h-12 text-slate-300" />
            </div>
            <h3 className="text-lg font-bold text-slate-900 mb-2">No prompts found</h3>
            <p className="text-slate-500 max-w-sm mx-auto mb-6">
              We couldn't find any prompts matching your search criteria.
            </p>
            <button
              onClick={clearAll}
              className="px-6 py-2.5 bg-white border border-slate-300 rounded-xl text-slate-700 font-medium hover:bg-slate-50 transition-colors shadow-sm"
            >
              Clear all filters
            </button>
          </div>
        )}

        {/* Infinite scroll sentinel */}
        {displayCount < results.length && (
          <div ref={sentinelRef} className="flex justify-center py-8">
            <div className="w-6 h-6 border-2 border-slate-200 border-t-brand-500 rounded-full animate-spin" />
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-200 bg-white/50 backdrop-blur-sm py-8 mt-12">
        <div className="container mx-auto px-4 text-center">
          <p className="text-slate-500 text-sm">
            Prompt Aggregator ver1.0 &copy; 2026. Local Edition.
            <span className="mx-2 text-slate-300">|</span>
            Built for Internal use only.
          </p>
        </div>
      </footer>
    </>
  );
}
