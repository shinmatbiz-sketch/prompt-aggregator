import json
import os
import sys
from pathlib import Path

# Configuration
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
DATA_FILE = PROJECT_DIR / "data" / "prompts.json"
OUTPUT_HTML = PROJECT_DIR / "prompt-aggregator.html"

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Prompt Aggregator (Local)</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/lucide@latest"></script>
    <style>
        body { font-family: 'Inter', sans-serif; }
        .prompt-card { transition: all 0.2s; }
        .prompt-card:hover { transform: translateY(-2px); box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1); }
        .line-clamp-3 {
            display: -webkit-box;
            -webkit-line-clamp: 3;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }
        /* CustomScrollbar */
        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-track { background: #f1f1f1; }
        ::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 4px; }
        ::-webkit-scrollbar-thumb:hover { background: #94a3b8; }
    </style>
</head>
<body class="bg-gray-50 text-gray-900 min-h-screen">

    <!-- Header -->
    <header class="sticky top-0 z-40 bg-white/80 backdrop-blur-md border-b border-gray-200">
        <div class="max-w-5xl mx-auto px-4 py-4">
            <div class="flex items-center justify-between mb-4">
                <div class="flex items-center gap-3">
                    <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-violet-600 flex items-center justify-center">
                        <i data-lucide="sparkles" class="w-4 h-4 text-white"></i>
                    </div>
                    <h1 class="text-xl font-bold tracking-tight">Prompt Aggregator <span class="text-xs font-normal text-gray-500 ml-2 border border-gray-200 px-2 py-0.5 rounded-full">Local</span></h1>
                </div>
                <div class="text-xs text-gray-400 font-mono" id="total-count">0 prompts</div>
            </div>

            <!-- Search & Filter -->
            <div class="space-y-3">
                <div class="relative">
                    <i data-lucide="search" class="absolute left-3.5 top-1/2 -translate-y-1/2 w-4.5 h-4.5 text-gray-400"></i>
                    <input type="text" id="search-input" placeholder="プロンプトを検索..." 
                        class="w-full pl-10 pr-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/30 focus:border-blue-400 transition-all">
                </div>
                
                <div class="flex flex-wrap gap-2" id="category-filters">
                    <!-- Categories injected by JS -->
                </div>
            </div>
        </div>
    </header>

    <!-- Main Content -->
    <main class="max-w-5xl mx-auto px-4 py-6">
        <div id="prompt-grid" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            <!-- Cards injected by JS -->
        </div>
        
        <div id="no-results" class="hidden text-center py-20">
            <div class="w-16 h-16 mx-auto mb-4 rounded-full bg-gray-100 flex items-center justify-center">
                <i data-lucide="search" class="w-7 h-7 text-gray-300"></i>
            </div>
            <p class="text-gray-500 text-sm">一致するプロンプトが見つかりませんでした</p>
            <button onclick="resetFilters()" class="mt-3 text-sm text-blue-500 hover:text-blue-600">フィルターをクリア</button>
        </div>
    </main>

    <!-- Detail Modal -->
    <dialog id="detail-modal" class="rounded-2xl shadow-2xl p-0 w-full max-w-2xl backdrop:bg-gray-900/50 backdrop:backdrop-blur-sm open:animate-in open:fade-in open:zoom-in-95 closed:animate-out closed:fade-out closed:zoom-out-95">
        <div class="flex flex-col max-h-[85vh]">
            <div class="sticky top-0 bg-white border-b border-gray-100 px-6 py-4 flex items-center justify-between z-10">
                <h2 id="modal-title" class="text-lg font-bold text-gray-900 pr-4">Title</h2>
                <button onclick="closeModal()" class="p-1 text-gray-400 hover:text-gray-600 rounded-full hover:bg-gray-100 transition-colors">
                    <i data-lucide="x" class="w-5 h-5"></i>
                </button>
            </div>
            
            <div class="p-6 overflow-y-auto">
                <div class="flex flex-wrap gap-2 mb-4" id="modal-tags"></div>
                
                <div class="bg-gray-50 rounded-xl border border-gray-200 overflow-hidden">
                    <div class="flex items-center justify-between px-4 py-2 border-b border-gray-200 bg-gray-100/50">
                        <span class="text-xs font-mono text-gray-500">PROMPT</span>
                        <button onclick="copyModalContent()" class="text-xs text-blue-600 hover:text-blue-700 font-medium flex items-center gap-1">
                            <i data-lucide="copy" class="w-3 h-3"></i> コピー
                        </button>
                    </div>
                    <pre id="modal-body" class="p-4 text-sm text-gray-700 font-mono whitespace-pre-wrap break-words leading-relaxed"></pre>
                </div>
                
                <div class="mt-6 flex gap-3">
                    <button onclick="openInChatGPT()" class="flex-1 flex items-center justify-center gap-2 bg-blue-600 text-white px-4 py-2.5 rounded-xl hover:bg-blue-700 transition-colors font-medium text-sm">
                        <i data-lucide="external-link" class="w-4 h-4"></i> ChatGPT
                    </button>
                    <button onclick="openInGemini()" class="flex-1 flex items-center justify-center gap-2 bg-indigo-600 text-white px-4 py-2.5 rounded-xl hover:bg-indigo-700 transition-colors font-medium text-sm">
                        <i data-lucide="external-link" class="w-4 h-4"></i> Gemini
                    </button>
                </div>
            </div>
        </div>
    </dialog>

    <!-- Toast -->
    <div id="toast" class="fixed bottom-4 right-4 bg-gray-900 text-white px-4 py-2.5 rounded-lg shadow-lg transform translate-y-20 opacity-0 transition-all duration-300 flex items-center gap-2 text-sm font-medium z-50">
        <i data-lucide="check" class="w-4 h-4 text-green-400"></i>
        <span>コピーしました</span>
    </div>

    <!-- Data Injection -->
    <script>
        const PROMPTS = {{PROMPTS_JSON}};
    </script>

    <!-- Application Logic -->
    <script>
        // State
        let currentPrompts = PROMPTS;
        let activeCategory = null;
        let searchQuery = "";
        let currentModalPrompt = null;

        // Colors for categories (Tailwind classes)
        const CATEGORY_STYLES = {
            "default": "bg-gray-100 text-gray-600 hover:bg-gray-200",
            "#文章作成・要約": "bg-blue-50 text-blue-600 hover:bg-blue-100",
            "#文書校正・編集": "bg-green-50 text-green-600 hover:bg-green-100",
            "#アイデア創出・企画": "bg-purple-50 text-purple-600 hover:bg-purple-100",
            "#業務改善": "bg-orange-50 text-orange-600 hover:bg-orange-100",
            "#情報収集・分析": "bg-cyan-50 text-cyan-600 hover:bg-cyan-100",
            "#コミュニケーション支援": "bg-pink-50 text-pink-600 hover:bg-pink-100",
            "#プログラミング": "bg-slate-100 text-slate-700 hover:bg-slate-200",
            "#意識改革・スキルアップ": "bg-yellow-50 text-yellow-700 hover:bg-yellow-100"
        };

        // DOM Elements
        const promptGrid = document.getElementById('prompt-grid');
        const searchInput = document.getElementById('search-input');
        const categoryFilters = document.getElementById('category-filters');
        const totalCount = document.getElementById('total-count');
        const noResults = document.getElementById('no-results');
        const detailModal = document.getElementById('detail-modal');

        // Initialize
        function init() {
            lucide.createIcons();
            renderCategories();
            renderGrid(PROMPTS);
            updateCount(PROMPTS.length);

            // Search listener
            searchInput.addEventListener('input', (e) => {
                searchQuery = e.target.value.toLowerCase();
                filterPrompts();
            });

            // Keyboard shortcut /
            document.addEventListener('keydown', (e) => {
                if (e.key === '/' && document.activeElement !== searchInput) {
                    e.preventDefault();
                    searchInput.focus();
                }
            });
            
            // Modal outside click close
            detailModal.addEventListener('click', (e) => {
                if (e.target === detailModal) closeModal();
            });
        }

        // Filtering Logic
        function filterPrompts() {
            let filtered = PROMPTS;

            if (searchQuery) {
                filtered = filtered.filter(p => 
                    p.title.toLowerCase().includes(searchQuery) || 
                    p.body.toLowerCase().includes(searchQuery)
                );
            }

            if (activeCategory) {
                filtered = filtered.filter(p => p.categories && p.categories.includes(activeCategory));
            }

            renderGrid(filtered);
            updateCount(filtered.length);
            
            if (filtered.length === 0) {
                promptGrid.classList.add('hidden');
                noResults.classList.remove('hidden');
            } else {
                promptGrid.classList.remove('hidden');
                noResults.classList.add('hidden');
            }
        }

        function toggleCategory(cat) {
            if (activeCategory === cat) {
                activeCategory = null;
            } else {
                activeCategory = cat;
            }
            renderCategories(); // re-render to update active state
            filterPrompts();
        }

        function resetFilters() {
            searchQuery = "";
            activeCategory = null;
            searchInput.value = "";
            renderCategories();
            filterPrompts();
        }

        // Rendering
        function renderCategories() {
            // Extract all unique categories
            const allCats = ["#文章作成・要約", "#文書校正・編集", "#アイデア創出・企画", "#業務改善", "#情報収集・分析", "#コミュニケーション支援", "#プログラミング", "#意識改革・スキルアップ"];
            
            let html = '';
            allCats.forEach(cat => {
                const isActive = activeCategory === cat;
                const style = CATEGORY_STYLES[cat] || CATEGORY_STYLES["default"];
                const activeClass = isActive ? "ring-2 ring-offset-1 ring-blue-500 shadow-sm" : "opacity-70 hover:opacity-100";
                
                html += `
                    <button onclick="toggleCategory('${cat}')" 
                        class="px-3 py-1.5 text-xs font-medium rounded-lg transition-all ${style} ${activeClass}">
                        ${cat.replace('#', '')}
                    </button>
                `;
            });
            categoryFilters.innerHTML = html;
        }

        function renderGrid(items) {
            // Limit to first 100 for performance if needed, but modern browsers handle thousands fine.
            // Let's implement lazy loading if needed, but for <1000 items, direct render is okay.
            // We will paginate if logic gets complex, but for single file simple is best.
            
            // To prevent freezing, render first 50, then rest? Actually 1000 items is trivial for DOM.
            const displayItems = items.slice(0, 100); 
            
            let html = '';
            displayItems.forEach(p => {
                const catHtml = (p.categories || []).map(c => {
                   const style = CATEGORY_STYLES[c] || CATEGORY_STYLES["default"];
                   return `<span class="px-1.5 py-0.5 text-[10px] rounded-md font-medium bg-white/50 border border-black/5 ${style}">${c.replace('#', '')}</span>`;
                }).join('');

                html += `
                <article onclick="openModal('${p.id}')" class="prompt-card bg-white rounded-xl border border-gray-200 p-5 cursor-pointer hover:border-blue-300">
                    <div class="flex justify-between items-start mb-2">
                        <span class="text-[10px] font-mono text-gray-400 bg-gray-50 px-1.5 py-0.5 rounded">${p.id}</span>
                    </div>
                    <h3 class="text-sm font-bold text-gray-900 mb-2 leading-relaxed line-clamp-2 h-10">${p.title}</h3>
                    <div class="flex flex-wrap gap-1 mb-3 h-6 overflow-hidden">${catHtml}</div>
                    <p class="text-xs text-gray-500 leading-relaxed line-clamp-3 font-mono">${escapeHtml(p.body)}</p>
                </article>
                `;
            });
            
            if (items.length > 100) {
                 html += `<div class="col-span-full text-center py-4 text-xs text-gray-400">Showing top 100 of ${items.length}</div>`;
            }

            promptGrid.innerHTML = html;
        }

        function updateCount(n) {
            totalCount.textContent = `${n} prompts`;
        }

        // Modal Functions
        function openModal(id) {
            const p = PROMPTS.find(item => item.id === id);
            if (!p) return;
            currentModalPrompt = p;

            document.getElementById('modal-title').textContent = p.title;
            document.getElementById('modal-body').textContent = p.body;
            
            const tagsContainer = document.getElementById('modal-tags');
            tagsContainer.innerHTML = (p.categories || []).map(c => {
                const style = CATEGORY_STYLES[c] || CATEGORY_STYLES["default"];
                return `<span class="px-2 py-1 text-xs rounded-lg font-medium ${style}">${c.replace('#', '')}</span>`;
            }).join('');

            detailModal.showModal();
        }

        function closeModal() {
            detailModal.close();
            currentModalPrompt = null;
        }

        // Actions
        async function copyModalContent() {
            if (!currentModalPrompt) return;
            await copyToClipboard(currentModalPrompt.body);
        }

        async function copyToClipboard(text) {
            try {
                await navigator.clipboard.writeText(text);
                showToast();
                return true;
            } catch (err) {
                console.error("Copy failed", err);
                return false;
            }
        }

        function showToast() {
            const t = document.getElementById('toast');
            t.classList.remove('translate-y-20', 'opacity-0');
            setTimeout(() => {
                t.classList.add('translate-y-20', 'opacity-0');
            }, 2000);
        }
        
        function openInChatGPT() {
            if(!currentModalPrompt) return;
            const url = `https://chat.openai.com/?q=${encodeURIComponent(currentModalPrompt.body)}`;
            window.open(url, '_blank');
        }
        
        function openInGemini() {
            if(!currentModalPrompt) return;
            const url = `https://gemini.google.com/app?text=${encodeURIComponent(currentModalPrompt.body)}`;
            window.open(url, '_blank');
        }

        // Utility
        function escapeHtml(text) {
            return text
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;")
                .replace(/"/g, "&quot;")
                .replace(/'/g, "&#039;");
        }

        // Start
        window.addEventListener('DOMContentLoaded', init);

    </script>
</body>
</html>
"""

def generate():
    print(f"Reading data from {DATA_FILE}...")
    
    if not DATA_FILE.exists():
        print(f"Error: Data file not found at {DATA_FILE}")
        print("Please run crawl_prompts.py first.")
        return

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading JSON: {e}")
        return

    # Serialize data to JSON string for injection
    json_str = json.dumps(data, ensure_ascii=False)

    # Inject into template
    html_content = HTML_TEMPLATE.replace("{{PROMPT_DATA}}", json_str)
    # Replace PROMPTS_JSON with pure array if I made a mistake in template variable naming
    html_content = html_content.replace("{{PROMPTS_JSON}}", json_str)

    # Write output
    print(f"Writing HTML to {OUTPUT_HTML}...")
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html_content)

    print("Success! prompt-aggregator.html has been generated.")

if __name__ == "__main__":
    generate()
