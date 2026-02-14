import type { Metadata } from "next";
import "./globals.css";

// Just manually adding the link for simplicity to match Neo structure exactly 
// without setting up Next.js Font optimization for now.


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
      <body className="min-h-screen text-slate-800 antialiased"
        style={{
          backgroundColor: '#f8fafc',
          backgroundImage: `radial-gradient(at 0% 0%, rgba(14, 165, 233, 0.1) 0px, transparent 50%),
                              radial-gradient(at 100% 100%, rgba(99, 102, 241, 0.1) 0px, transparent 50%)`,
          backgroundAttachment: 'fixed'
        }}
      >{children}</body>
    </html>
  );
}
