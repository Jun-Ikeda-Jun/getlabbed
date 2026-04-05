import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "GetLabbed - お前の癖、丸見えだぞ？",
  description:
    "試合動画を貼るだけ。どこが強くてどこがヤバいか、全部教えてやるよ。スマブラの試合分析AI。",
  openGraph: {
    title: "GetLabbed",
    description: "お前の癖、丸見えだぞ？ - スマブラ試合分析AI",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ja">
      <body className="antialiased min-h-screen">
        {children}
      </body>
    </html>
  );
}
