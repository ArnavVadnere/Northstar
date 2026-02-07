import type { Metadata } from "next";
import localFont from "next/font/local";
import Link from "next/link";
import "./globals.css";

const geistSans = localFont({
  src: "./fonts/GeistVF.woff",
  variable: "--font-geist-sans",
  weight: "100 900",
});
const geistMono = localFont({
  src: "./fonts/GeistMonoVF.woff",
  variable: "--font-geist-mono",
  weight: "100 900",
});

export const metadata: Metadata = {
  title: "NorthStar - Financial Compliance Auditor",
  description: "AI-powered financial compliance auditing platform",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased min-h-screen bg-background font-[family-name:var(--font-geist-sans)]`}
      >
        <header className="border-b">
          <div className="container mx-auto flex h-14 items-center px-6">
            <Link href="/" className="flex items-center gap-2 font-semibold text-lg">
              <span className="text-primary">NorthStar</span>
            </Link>
            <nav className="ml-auto flex gap-6 text-sm font-medium">
              <Link href="/" className="text-muted-foreground hover:text-foreground transition-colors">
                Dashboard
              </Link>
              <Link href="/upload" className="text-muted-foreground hover:text-foreground transition-colors">
                Upload
              </Link>
              <Link href="/history" className="text-muted-foreground hover:text-foreground transition-colors">
                History
              </Link>
            </nav>
          </div>
        </header>
        <main>{children}</main>
      </body>
    </html>
  );
}
