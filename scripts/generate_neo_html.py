import json
import os
import sys
from pathlib import Path
from datetime import datetime


# Configuration
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
DATA_FILE = PROJECT_DIR / "data" / "prompts.json"
OUTPUT_HTML = PROJECT_DIR / "prompt-aggregator-neo.html"

# HTML Template with Neo Design
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ja" class="scroll-smooth">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Prompt Aggregator ver1.0</title>
    <!-- Built: {{GENERATION_DATE}} -->

    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- Lucide Icons -->
    <script src="https://unpkg.com/lucide@latest"></script>
    <!-- Google Fonts: Inter & Noto Sans JP -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Noto+Sans+JP:wght@400;500;700&display=swap" rel="stylesheet">
    
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    fontFamily: {
                        sans: ['"Inter"', '"Noto Sans JP"', 'sans-serif'],
                        mono: ['"Fira Code"', 'monospace'],
                    },
                    colors: {
                        brand: {
                            50: '#f0f9ff',
                            100: '#e0f2fe',
                            500: '#0ea5e9',
                            600: '#0284c7',
                            900: '#0c4a6e',
                        }
                    },
                    animation: {
                        'fade-in': 'fadeIn 0.3s ease-out forwards',
                        'slide-up': 'slideUp 0.4s ease-out forwards',
                    },
                    keyframes: {
                        fadeIn: {
                            '0%': { opacity: '0' },
                            '100%': { opacity: '1' },
                        },
                        slideUp: {
                            '0%': { opacity: '0', transform: 'translateY(10px)' },
                            '100%': { opacity: '1', transform: 'translateY(0)' },
                        }
                    }
                }
            }
        }
    </script>

    <style>
        /* Custom Styles for Neo Glassmorphism */
        body {
            background-color: #f8fafc;
            background-image: 
                radial-gradient(at 0% 0%, rgba(14, 165, 233, 0.1) 0px, transparent 50%),
                radial-gradient(at 100% 100%, rgba(99, 102, 241, 0.1) 0px, transparent 50%);
            background-attachment: fixed;
        }
        
        .glass-panel {
            background: rgba(255, 255, 255, 0.7);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.5);
        }

        .neo-card {
            background: rgba(255, 255, 255, 0.85);
            border: 1px solid rgba(226, 232, 240, 0.8);
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .neo-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 12px 20px -5px rgba(0, 0, 0, 0.1), 0 8px 8px -5px rgba(0, 0, 0, 0.04);
            border-color: rgba(14, 165, 233, 0.4);
        }

        .category-chip {
            background: rgba(241, 245, 249, 0.8);
            border: 1px solid rgba(226, 232, 240, 1);
            transition: all 0.2s ease;
        }

        .category-chip:hover {
            background: #fff;
            transform: scale(1.05);
        }
        
        .category-chip.active {
            background: #0ea5e9;
            color: white;
            border-color: #0284c7;
            box-shadow: 0 2px 8px rgba(14, 165, 233, 0.4);
        }

        /* Scrollbar beautification */
        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 10px; border: 2px solid #f8fafc; }
        ::-webkit-scrollbar-thumb:hover { background: #94a3b8; }
        
        pre {
            font-family: 'Fira Code', 'Consolas', 'Monaco', monospace;
        }
    </style>
</head>
<body class="text-slate-800 antialiased min-h-screen flex flex-col">

    <!-- Sticky Header with Glassmorphism -->
    <header class="sticky top-0 z-50 glass-panel border-b border-white/50 shadow-sm">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex flex-col md:flex-row items-center justify-between py-4 gap-4">
                
                <!-- Logo area -->
                <div class="flex items-center gap-3 w-full md:w-auto">
                    <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-brand-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-brand-500/30 text-white transform hover:rotate-6 transition-transform duration-300">
                        <i data-lucide="zap" class="w-6 h-6 fill-current"></i>
                    </div>
                    <div>
                        <h1 class="text-xl font-bold tracking-tight text-slate-900 leading-none">Prompt Aggregator <span class="text-brand-600">ver1.0</span></h1>
                        <p class="text-xs text-slate-500 font-medium mt-0.5">Local Edition</p>
                    </div>
                </div>

                <!-- Search Bar -->
                <div class="relative w-full md:max-w-xl group">
                    <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                        <i data-lucide="search" class="h-5 w-5 text-slate-400 group-focus-within:text-brand-500 transition-colors"></i>
                    </div>
                    <input type="text" id="search-input" 
                        class="block w-full pl-10 pr-4 py-2.5 border-0 rounded-xl leading-5 bg-white/80 text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-brand-500/50 shadow-sm ring-1 ring-slate-200 transition-all"
                        placeholder="Search prompts (keywords, content)...  Press '/' to focus">
                    <div class="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
                        <span class="text-slate-400 text-xs border border-slate-200 rounded px-1.5 py-0.5 bg-slate-50">/</span>
                    </div>
                </div>
                
                <!-- Stats -->
                <div class="hidden md:flex items-center gap-2 text-sm font-medium text-slate-500 bg-white/50 px-3 py-1.5 rounded-lg border border-white/60">
                    <i data-lucide="database" class="w-4 h-4"></i>
                    <span id="total-count">0</span> items
                </div>
            </div>
            
            <!-- Category Filter Scrollable Area -->
            <div class="py-3 overflow-x-auto no-scrollbar mask-gradient flex items-center gap-2 pb-4" id="category-filters">
                <!-- Categories injected here -->
            </div>
        </div>
    </header>

    <!-- Main Content -->
    <main class="flex-grow container mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        <!-- Status Bar / Breadcrumbs -->
        <div class="flex items-center justify-between mb-6 opacity-0 animate-fade-in" style="animation-delay: 0.1s;">
            <div class="text-sm text-slate-500 flex items-center gap-2">
                <span class="font-semibold text-slate-700">Results</span>
                <span class="w-1 h-1 bg-slate-400 rounded-full"></span>
                <span id="results-count">Loading...</span>
            </div>
            <button onclick="resetFilters()" class="text-xs font-medium text-brand-600 hover:text-brand-700 hover:underline flex items-center gap-1 transition-colors">
                <i data-lucide="rotate-ccw" class="w-3 h-3"></i> Reset Filters
            </button>
        </div>

        <!-- Prompt Grid -->
        <div id="prompt-grid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-3 gap-6 opacity-0 animate-fade-in" style="animation-delay: 0.2s;">
            <!-- Cards injected By JS -->
        </div>

        <!-- Empty State -->
        <div id="no-results" class="hidden flex flex-col items-center justify-center py-20 text-center animate-fade-in">
            <div class="w-24 h-24 bg-slate-100 rounded-full flex items-center justify-center mb-6">
                <i data-lucide="frown" class="w-12 h-12 text-slate-300"></i>
            </div>
            <h3 class="text-lg font-bold text-slate-900 mb-2">No prompts found</h3>
            <p class="text-slate-500 max-w-sm mx-auto mb-6">
                We couldn't find any prompts matching your search criteria. Try different keywords or clear the filters.
            </p>
            <button onclick="resetFilters()" class="px-6 py-2.5 bg-white border border-slate-300 rounded-xl text-slate-700 font-medium hover:bg-slate-50 transition-colors shadow-sm">
                Clear all filters
            </button>
        </div>

    </main>

    <!-- Footer -->
    <footer class="border-t border-slate-200 bg-white/50 backdrop-blur-sm py-8 mt-12">
        <div class="container mx-auto px-4 text-center">
            <p class="text-slate-500 text-sm">
                Prompt Aggregator ver1.0 &copy; 2026. Local Edition.
                <span class="mx-2 text-slate-300">|</span>
                Built for Internal use only.
            </p>
        </div>
    </footer>

    <!-- Modal Overlay -->
    <div id="modal-overlay" class="fixed inset-0 z-[100] bg-slate-900/60 backdrop-blur-sm hidden transition-opacity duration-300 opacity-0" aria-hidden="true">
        <!-- Modal Content -->
        <div class="flex items-center justify-center min-h-screen p-4">
            <div id="modal-content" class="bg-white rounded-2xl shadow-2xl w-full max-w-3xl max-h-[90vh] flex flex-col transform scale-95 transition-transform duration-300" role="dialog" aria-modal="true">
                
                <!-- Modal Header -->
                <div class="px-6 py-4 border-b border-slate-100 flex items-center justify-between bg-white rounded-t-2xl z-10">
                    <div class="flex items-center gap-3 overflow-hidden">
                        <div class="min-w-[40px] h-10 rounded-lg bg-slate-100 flex items-center justify-center text-slate-500 font-mono text-xs font-bold" id="modal-id">
                            ID
                        </div>
                        <h2 class="text-lg font-bold text-slate-800 truncate" id="modal-title">Prompt Title</h2>
                    </div>
                    <button onclick="closeModal()" class="p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-full transition-colors">
                        <i data-lucide="x" class="w-5 h-5"></i>
                    </button>
                </div>

                <!-- Modal Body -->
                <div class="p-6 overflow-y-auto custom-scrollbar flex-grow bg-slate-50/50">
                    
                    <!-- Tags -->
                    <div class="flex flex-wrap gap-2 mb-6" id="modal-tags">
                        <!-- Tags injected here -->
                    </div>

                    <!-- Copy Area -->
                    <div class="relative group">
                        <div class="absolute right-3 top-3 opacity-0 group-hover:opacity-100 transition-opacity z-10">
                            <button onclick="copyModalContent()" class="bg-white/90 backdrop-blur border border-slate-200 text-slate-600 hover:text-brand-600 hover:border-brand-300 px-3 py-1.5 rounded-lg text-xs font-bold shadow-sm flex items-center gap-2 transition-all">
                                <i data-lucide="copy" class="w-3 h-3"></i> Copy
                            </button>
                        </div>
                        <pre id="modal-body" class="p-6 bg-white rounded-xl border border-slate-200 text-sm text-slate-700 leading-relaxed whitespace-pre-wrap font-mono shadow-sm"></pre>
                    </div>

                </div>

                <!-- Modal Footer -->
                <div class="p-4 bg-white border-t border-slate-100 rounded-b-2xl flex flex-col sm:flex-row gap-3 items-center justify-between">
                    <p class="text-xs text-slate-400 hidden sm:block">
                        Pro Tip: Use prompts as a starting point and iterate.
                    </p>
                    <div class="flex w-full sm:w-auto gap-3">
                        <button onclick="openInChatGPT()" class="flex-1 sm:flex-none flex items-center justify-center gap-2 bg-[#74aa9c] text-white px-5 py-2.5 rounded-xl hover:bg-[#5e8f82] transition-colors font-semibold text-sm shadow-sm hover:shadow-md">
                            <i data-lucide="bot" class="w-4 h-4"></i> ChatGPT
                        </button>
                        <button onclick="openInGemini()" class="flex-1 sm:flex-none flex items-center justify-center gap-2 bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-5 py-2.5 rounded-xl hover:shadow-lg hover:to-indigo-500 transition-all font-semibold text-sm shadow-sm">
                            <i data-lucide="sparkles" class="w-4 h-4"></i> Gemini
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Toast Notification -->
    <div id="toast" class="fixed bottom-6 right-6 z-[110] transform translate-y-24 opacity-0 transition-all duration-300">
        <div class="bg-slate-800 text-white px-5 py-3 rounded-lg shadow-xl flex items-center gap-3">
            <div class="bg-green-500 rounded-full p-1">
                <i data-lucide="check" class="w-3 h-3 text-white"></i>
            </div>
            <div>
                <h4 class="font-bold text-sm">Copied!</h4>
                <p class="text-xs text-slate-300">Prompt copied to clipboard.</p>
            </div>
        </div>
    </div>

    <!-- Data Injection -->
    <script>
        const PROMPTS = {{PROMPTS_JSON}};
    </script>

    <!-- Application Logic -->
    <script>
        // --- State ---
        let state = {
            prompts: PROMPTS,
            filtered: PROMPTS,
            filter: {
                query: '',
                category: null
            },
            modalPrompt: null
        };

        // --- Constants ---
        const CATEGORY_COLORS = {
            "#文章作成・要約":      "text-blue-700 bg-blue-50 border-blue-200 hover:bg-blue-100",
            "#文書校正・編集":      "text-emerald-700 bg-emerald-50 border-emerald-200 hover:bg-emerald-100",
            "#アイデア創出・企画":    "text-purple-700 bg-purple-50 border-purple-200 hover:bg-purple-100",
            "#業務改善":            "text-orange-700 bg-orange-50 border-orange-200 hover:bg-orange-100",
            "#情報収集・分析":      "text-cyan-700 bg-cyan-50 border-cyan-200 hover:bg-cyan-100",
            "#コミュニケーション支援": "text-pink-700 bg-pink-50 border-pink-200 hover:bg-pink-100",
            "#プログラミング":      "text-slate-700 bg-slate-100 border-slate-200 hover:bg-slate-200",
            "#意識改革・スキルアップ": "text-amber-700 bg-amber-50 border-amber-200 hover:bg-amber-100"
        };
        const DEFAULT_CAT_COLOR = "text-slate-600 bg-slate-50 border-slate-200 hover:bg-slate-100";

        // --- DOM Elements ---
        const els = {
            grid: document.getElementById('prompt-grid'),
            catFilters: document.getElementById('category-filters'),
            searchInput: document.getElementById('search-input'),
            totalCount: document.getElementById('total-count'),
            resultsCount: document.getElementById('results-count'),
            noResults: document.getElementById('no-results'),
            modalOverlay: document.getElementById('modal-overlay'),
            modalContent: document.getElementById('modal-content'),
            modalTitle: document.getElementById('modal-title'),
            modalBody: document.getElementById('modal-body'),
            modalTags: document.getElementById('modal-tags'),
            modalId: document.getElementById('modal-id'),
            toast: document.getElementById('toast')
        };

        // --- Initialization ---
        function init() {
            lucide.createIcons();
            
            // Extract categories
            const categories = new Set();
            PROMPTS.forEach(p => (p.categories || []).forEach(c => categories.add(c)));
            renderCategoryFilters(Array.from(categories));
            
            // Initial render
            updateUI();

            // Event Listeners
            els.searchInput.addEventListener('input', handleSearch);
            document.addEventListener('keydown', handleGlobalKeydown);
            els.modalOverlay.addEventListener('click', (e) => {
                if (e.target === els.modalOverlay) closeModal();
            });
        }

        // --- Core Logic ---
        function handleSearch(e) {
            state.filter.query = e.target.value.toLowerCase().trim();
            applyFilters();
        }

        function toggleCategory(cat) {
            state.filter.category = state.filter.category === cat ? null : cat;
            applyFilters();
            updateCategoryActiveState();
        }

        function resetFilters() {
            state.filter.query = '';
            state.filter.category = null;
            els.searchInput.value = '';
            applyFilters();
            updateCategoryActiveState();
        }

        function applyFilters() {
            const { query, category } = state.filter;
            
            state.filtered = state.prompts.filter(p => {
                const matchesQuery = !query || 
                    p.title.toLowerCase().includes(query) || 
                    p.body.toLowerCase().includes(query);
                
                const matchesCategory = !category || 
                    (p.categories && p.categories.includes(category));
                
                return matchesQuery && matchesCategory;
            });

            updateUI();
        }

        // --- Rendering ---
        function renderCategoryFilters(categories) {
            const allCats = ["All", ...categories.sort()];
            // We want "All" to strictly reset, but our Toggle logic handles null.
            // Let's render buttons.
            
            els.catFilters.innerHTML = categories.map(cat => {
                const displayName = cat.replace('#', '');
                return `
                    <button onclick="toggleCategory('${cat}')" 
                        data-cat="${cat}"
                        class="category-chip px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-600 whitespace-nowrap">
                        ${displayName}
                    </button>
                `;
            }).join('');
        }

        function updateCategoryActiveState() {
            const buttons = els.catFilters.querySelectorAll('button');
            buttons.forEach(btn => {
                if (btn.dataset.cat === state.filter.category) {
                    btn.classList.add('active');
                } else {
                    btn.classList.remove('active');
                }
            });
        }

        function updateUI() {
            // Update counts
            els.totalCount.textContent = state.prompts.length;
            els.resultsCount.textContent = `${state.filtered.length} items`;

            // Toggle No Results
            if (state.filtered.length === 0) {
                els.grid.classList.add('hidden');
                els.noResults.classList.remove('hidden');
                return;
            }
            
            els.grid.classList.remove('hidden');
            els.noResults.classList.add('hidden');

            // Render Grid
            // Optimization: Limit rendering for extremely large sets if needed, 
            // but for <1000 items, browser handles it fine. 
            // We'll slice first 200 to ensure instant response on slower machines.
            const itemsToRender = state.filtered.slice(0, 200);
            
            els.grid.innerHTML = itemsToRender.map(p => {
                const tagsHtml = (p.categories || []).slice(0, 3).map(c => { // Show max 3 tags
                    return `<span class="text-[10px] px-1.5 py-0.5 rounded bg-slate-100 text-slate-500 font-medium">${c.replace('#','')}</span>`;
                }).join('');

                return `
                <article onclick="openModal('${p.id}')" 
                    class="neo-card rounded-2xl p-5 cursor-pointer group flex flex-col h-full opacity-0 animate-slide-up bg-white">
                    
                    <div class="flex justify-between items-start mb-3">
                        <div class="flex flex-wrap gap-1.5">
                            ${tagsHtml}
                        </div>
                        <span class="text-[10px] font-mono text-slate-300 group-hover:text-brand-400 transition-colors">#${p.id}</span>
                    </div>
                    
                    <h3 class="text-base font-bold text-slate-800 mb-2 leading-snug group-hover:text-brand-600 transition-colors">
                        ${highlightText(p.title, state.filter.query)}
                    </h3>
                    
                    <p class="text-xs text-slate-500 leading-relaxed line-clamp-4 font-mono mb-4 flex-grow">
                        ${highlightText(escapeHtml(p.body), state.filter.query)}
                    </p>
                    
                    <div class="pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-400">
                        <span class="flex items-center gap-1 group-hover:text-brand-500 transition-colors">
                            <i data-lucide="maximize-2" class="w-3 h-3"></i> View details
                        </span>
                        <i data-lucide="arrow-right" class="w-3 h-3 -ml-2 opacity-0 -translate-x-2 group-hover:opacity-100 group-hover:translate-x-0 transition-all"></i>
                    </div>
                </article>
                `;
            }).join('');
            
            // Re-run lucide for injected icons
            lucide.createIcons();
        }

        // --- Helpers ---
        function highlightText(text, query) {
            if (!query) return text;
            const regex = new RegExp(`(${query})`, 'gi');
            return text.replace(regex, '<span class="bg-yellow-100 text-yellow-800 rounded px-0.5">$1</span>');
        }

        function escapeHtml(text) {
             return text
                 .replace(/&/g, "&amp;")
                 .replace(/</g, "&lt;")
                 .replace(/>/g, "&gt;")
                 .replace(/"/g, "&quot;")
                 .replace(/'/g, "&#039;");
        }

        // --- Modal ---
        function openModal(id) {
            const p = state.prompts.find(x => x.id === id);
            if (!p) return;
            state.modalPrompt = p;

            els.modalTitle.textContent = p.title;
            els.modalId.textContent = '#' + p.id;
            els.modalBody.textContent = p.body;
            
            els.modalTags.innerHTML = (p.categories || []).map(c => {
                const colorClass = CATEGORY_COLORS[c] || DEFAULT_CAT_COLOR;
                return `<span class="px-3 py-1 text-xs rounded-full font-bold border ${colorClass}">${c.replace('#','')}</span>`;
            }).join('');

            // Show
            els.modalOverlay.classList.remove('hidden');
            // Small delay to allow display:block to apply before opacity transition
            setTimeout(() => {
                els.modalOverlay.classList.remove('opacity-0');
                els.modalContent.classList.remove('scale-95');
                els.modalContent.classList.add('scale-100');
            }, 10);
            
            document.body.style.overflow = 'hidden'; // Prevent background scrolling
        }

        function closeModal() {
            els.modalOverlay.classList.add('opacity-0');
            els.modalContent.classList.remove('scale-100');
            els.modalContent.classList.add('scale-95');
            
            setTimeout(() => {
                els.modalOverlay.classList.add('hidden');
                state.modalPrompt = null;
                document.body.style.overflow = '';
            }, 300);
        }

        async function copyModalContent() {
            if (!state.modalPrompt) return;
            try {
                await navigator.clipboard.writeText(state.modalPrompt.body);
                showToast();
            } catch (err) {
                console.error('Failed to copy', err);
            }
        }

        // --- External Actions ---
        function openInChatGPT() {
            if (!state.modalPrompt) return;
            const url = `https://chat.openai.com/?q=${encodeURIComponent(state.modalPrompt.body)}`;
            window.open(url, '_blank');
        }

        function openInGemini() {
            if (!state.modalPrompt) return;
            const url = `https://gemini.google.com/app?text=${encodeURIComponent(state.modalPrompt.body)}`;
            window.open(url, '_blank');
        }

        // --- Toast ---
        let toastTimeout;
        function showToast() {
            const t = els.toast;
            t.classList.remove('translate-y-24', 'opacity-0');
            
            clearTimeout(toastTimeout);
            toastTimeout = setTimeout(() => {
                t.classList.add('translate-y-24', 'opacity-0');
            }, 2500);
        }

        // --- Keys ---
        function handleGlobalKeydown(e) {
            if (e.key === '/' && document.activeElement !== els.searchInput) {
                e.preventDefault();
                els.searchInput.focus();
            }
            if (e.key === 'Escape') {
                if (state.modalPrompt) {
                    closeModal();
                } else {
                    els.searchInput.blur();
                    resetFilters();
                }
            }
        }

        // --- Start ---
        window.addEventListener('DOMContentLoaded', init);

    </script>
</body>
</html>
"""

def generate():
    print(f"Reading data from {DATA_FILE}...")
    
    if not DATA_FILE.exists():
        print(f"Error: Data file not found at {DATA_FILE}")
        return

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading JSON: {e}")
        return

    # Serialize data to JSON string for injection
    json_str = json.dumps(data, ensure_ascii=False)
    
    # Get current date
    gen_date = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Inject into template
    html_content = HTML_TEMPLATE.replace("{{PROMPTS_JSON}}", json_str)
    html_content = html_content.replace("{{GENERATION_DATE}}", gen_date)

    # Write output
    print(f"Writing HTML to {OUTPUT_HTML}...")
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html_content)

    print("Success! prompt-aggregator-neo.html has been generated.")

if __name__ == "__main__":
    generate()
