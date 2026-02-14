import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Prompt Aggregator | AI プロンプト検索",
  description:
    "999件以上のAIプロンプトを瞬時に検索。ChatGPTやClaude等で使えるプロンプト集。",
  openGraph: {
    title: "Prompt Aggregator",
    description: "AI プロンプトを瞬時に検索・コピー・活用",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ja">
      <body className="min-h-screen bg-[#fafafa]">{children}</body>
    </html>
  );
}
