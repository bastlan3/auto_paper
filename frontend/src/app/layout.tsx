import type { Metadata } from "next";
import { Inter, Source_Serif_4 } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"], variable: '--font-inter' });
const sourceSerif = Source_Serif_4({ subsets: ["latin"], variable: '--font-source-serif-4' });

export const metadata: Metadata = {
  title: "AI Science Brief",
  description: "Your daily briefing on AI research.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${inter.variable} ${sourceSerif.variable} font-serif bg-background text-text-primary`}>
        {children}
      </body>
    </html>
  );
}