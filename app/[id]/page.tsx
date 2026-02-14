"use client";

import { useParams } from "next/navigation";
import { useMemo, useState, useCallback, useEffect } from "react";
import Link from "next/link";
import {
  ArrowLeft,
  Copy,
  ExternalLink,
  Check,
  Link as LinkIcon,
} from "lucide-react";
import {
  type Prompt,
  cleanTitle,
  buildChatGPTUrl,
  buildGeminiUrl,
  copyToClipboard,
  formatId,
  getCategoryColor,
} from "@/lib/utils";
import Toast from "@/components/Toast";
import promptsData from "@/data/prompts.json";

const allPrompts: Prompt[] = promptsData as Prompt[];

export default function PromptDetailPage() {
  const params = useParams();
  const id = params.id as string;

  const prompt = useMemo(
    () => allPrompts.find((p) => p.id === id) ?? null,
    [id]
  );

  const [toastMsg, setToastMsg] = useState("");
  const [toastVisible, setToastVisible] = useState(false);

  // Update page title
  useEffect(() => {
    if (prompt) {
      document.title = `${cleanTitle(prompt.title)} | Prompt Aggregator`;
    }
  }, [prompt]);

  const showToast = useCallback((msg: string) => {
    setToastMsg(msg);
    setToastVisible(true);
  }, []);

  const handleCopy = useCallback(async () => {
    if (!prompt) return;
    const ok = await copyToClipboard(prompt.body);
    if (ok) showToast("コピーしました");
  }, [prompt, showToast]);

  const handleCopyLink = useCallback(async () => {
    const ok = await copyToClipboard(window.location.href);
    if (ok) showToast("リンクをコピーしました");
  }, [showToast]);

  const handleOpenAI = useCallback(() => {
    if (!prompt) return;
    window.open(buildChatGPTUrl(prompt.body), "_blank", "noopener");
  }, [prompt]);

  const handleOpenGemini = useCallback(() => {
    if (!prompt) return;
    window.open(buildGeminiUrl(prompt.body), "_blank", "noopener");
  }, [prompt]);

  if (!prompt) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-6xl font-bold text-gray-200 mb-4">404</p>
          <p className="text-gray-500 mb-6">プロンプトが見つかりません</p>
          <Link
            href="/"
            className="inline-flex items-center gap-2 text-sm text-blue-500 hover:text-blue-600 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            ホームに戻る
          </Link>
        </div>
      </div>
    );
  }

  const bodyLines = prompt.body.split(/\n/);

  return (
    <>
      {/* Header */}
      <header className="sticky top-0 z-40 bg-white/80 backdrop-blur-xl border-b border-gray-200/60">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 py-3 flex items-center justify-between">
          <Link
            href="/"
            className="inline-flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-900 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            <span className="hidden sm:inline">一覧に戻る</span>
          </Link>

          <div className="flex items-center gap-2">
            <button
              onClick={handleCopyLink}
              className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
              title="リンクをコピー"
            >
              <LinkIcon className="w-4 h-4" />
            </button>
          </div>
        </div>
      </header>

      {/* Content */}
      <main className="max-w-3xl mx-auto px-4 sm:px-6 py-8">
        {/* Title section */}
        <div className="mb-6">
          <span className="inline-block text-xs font-mono text-blue-500 bg-blue-50 px-2 py-1 rounded-md mb-3">
            {formatId(prompt.id)}
          </span>
          <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 leading-tight">
            {cleanTitle(prompt.title)}
          </h1>

          {/* Category tags */}
          {prompt.categories && prompt.categories.length > 0 && (
            <div className="flex flex-wrap gap-1.5 mt-3">
              {prompt.categories.map((cat) => {
                const colors = getCategoryColor(cat);
                return (
                  <Link
                    key={cat}
                    href={`/?category=${encodeURIComponent(cat)}`}
                    className={`inline-flex items-center px-2.5 py-1 text-xs font-medium rounded-lg transition-colors ${colors.bg} ${colors.text} ${colors.hover}`}
                  >
                    {cat.replace("#", "")}
                  </Link>
                );
              })}
            </div>
          )}
        </div>

        {/* Action buttons */}
        <div className="flex flex-wrap gap-3 mb-8">
          <button
            onClick={handleCopy}
            className="inline-flex items-center gap-2 px-4 py-2.5 bg-gray-900 hover:bg-gray-800 text-white text-sm font-medium rounded-xl transition-colors shadow-sm"
          >
            <Copy className="w-4 h-4" />
            プロンプトをコピー
          </button>

          <button
            onClick={handleOpenAI}
            className="inline-flex items-center gap-2 px-4 py-2.5 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-xl transition-colors shadow-sm"
          >
            <ExternalLink className="w-4 h-4" />
            ChatGPTで開く
          </button>

          <button
            onClick={handleOpenGemini}
            className="inline-flex items-center gap-2 px-4 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium rounded-xl transition-colors shadow-sm"
          >
            <ExternalLink className="w-4 h-4" />
            Geminiで開く
          </button>

        </div>

        {/* Prompt body */}
        <div className="bg-white rounded-2xl border border-gray-200 overflow-hidden">
          <div className="flex items-center justify-between px-5 py-3 border-b border-gray-100 bg-gray-50/50">
            <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">
              Prompt
            </span>
            <button
              onClick={handleCopy}
              className="inline-flex items-center gap-1.5 text-xs text-gray-500 hover:text-gray-700 transition-colors"
            >
              <Copy className="w-3.5 h-3.5" />
              コピー
            </button>
          </div>
          <div className="p-5 sm:p-6">
            <div className="prose prose-sm max-w-none text-gray-700 leading-relaxed whitespace-pre-wrap break-words font-mono text-[13px]">
              {bodyLines.map((line, i) => (
                <span key={i}>
                  {line}
                  {i < bodyLines.length - 1 && "\n"}
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* Footer nav */}
        <div className="mt-8 flex items-center justify-between">
          {Number(id) > 1 && (
            <Link
              href={`/${String(Number(id) - 1).padStart(3, "0")}`}
              className="inline-flex items-center gap-1.5 text-sm text-gray-500 hover:text-blue-600 transition-colors"
            >
              <ArrowLeft className="w-4 h-4" />
              前のプロンプト
            </Link>
          )}
          <div className="flex-1" />
          {Number(id) < allPrompts.length && (
            <Link
              href={`/${String(Number(id) + 1).padStart(3, "0")}`}
              className="inline-flex items-center gap-1.5 text-sm text-gray-500 hover:text-blue-600 transition-colors"
            >
              次のプロンプト
              <ArrowLeft className="w-4 h-4 rotate-180" />
            </Link>
          )}
        </div>
      </main>

      <Toast
        message={toastMsg}
        visible={toastVisible}
        onClose={() => setToastVisible(false)}
      />
    </>
  );
}
