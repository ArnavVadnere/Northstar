import type { Metadata } from "next";
import localFont from "next/font/local";
import Link from "next/link";
import { BeamsBackground } from "@/components/ui/beams-background";
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

function StarIcon({ className }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      className={className}
      stroke="currentColor"
      strokeWidth="1.5"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M12 2L12 22M2 12L22 12M4.93 4.93L19.07 19.07M19.07 4.93L4.93 19.07" />
      <circle cx="12" cy="12" r="3" fill="currentColor" stroke="none" />
    </svg>
  );
}

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
        <BeamsBackground intensity="subtle" />
        <header className="border-b border-border/50 backdrop-blur-sm bg-background/80 sticky top-0 z-50">
          <div className="container mx-auto flex h-14 items-center px-6">
            <Link href="/" className="flex items-center gap-2.5 font-semibold text-lg group">
              <StarIcon className="h-5 w-5 text-primary group-hover:text-primary/80 transition-colors" />
              <span className="bg-gradient-to-r from-primary to-blue-400 bg-clip-text text-transparent">
                NorthStar
              </span>
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
