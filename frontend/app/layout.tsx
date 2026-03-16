import type { Metadata } from "next";
import Link from "next/link";
import "@fontsource/outfit/400.css";
import "@fontsource/outfit/500.css";
import "@fontsource/outfit/700.css";
import "@fontsource/outfit/900.css";

import "./globals.css";

export const metadata: Metadata = {
  title: "Daily Paper — AI 论文日报",
  description: "由 AI 驱动的每日论文精选，聚合重点论文与趋势洞察。",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN">
      <body>
        <div className="site-shell">
          <header className="site-header">
            <div className="site-header__inner">
              <Link href="/" className="site-header__brand">
                <span className="site-header__logo" aria-hidden="true">
                  <span className="site-header__logo-circle" />
                  <span className="site-header__logo-square" />
                  <span className="site-header__logo-triangle" />
                </span>
                <span className="site-header__brand-text">Daily Paper</span>
              </Link>
              <p className="site-header__tagline">AI 论文日报</p>
            </div>
          </header>

          <main className="site-main">{children}</main>

          <footer className="site-footer">
            <div className="site-footer__inner">
              Daily Paper — 由 AI 驱动的每日论文精选
            </div>
          </footer>
        </div>
      </body>
    </html>
  );
}
