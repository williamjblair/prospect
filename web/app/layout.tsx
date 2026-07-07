import type { Metadata } from "next";
import { JetBrains_Mono, Space_Grotesk, Spectral } from "next/font/google";
import { ThemeProvider } from "@/components/theme-provider";
import "./globals.css";

const mono = JetBrains_Mono({ subsets: ["latin"], variable: "--font-mono", display: "swap" });
const grotesk = Space_Grotesk({ subsets: ["latin"], variable: "--font-grotesk", display: "swap" });
const spectral = Spectral({
  subsets: ["latin"], weight: ["400", "500", "600", "700"], style: ["normal"],
  variable: "--font-serif-src", display: "swap",
});

export const metadata: Metadata = {
  title: "Prospect — a verified regulatory frontier of T-cell biology",
  description:
    "A linked, human-signed graph of what regulates human CD4+ T cells, re-derivable from released ground truth. No model in the trust path.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning
      className={`${mono.variable} ${grotesk.variable} ${spectral.variable}`}>
      <body>
        <ThemeProvider attribute="class" defaultTheme="light" enableSystem>
          {children}
        </ThemeProvider>
      </body>
    </html>
  );
}
