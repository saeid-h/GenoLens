import type { Metadata } from "next";
import { Fraunces, Source_Sans_3 } from "next/font/google";
import { SampleProvider } from "@/lib/sample";
import { ReportShell } from "@/components/ReportShell";
import "./globals.css";

const display = Fraunces({
  subsets: ["latin"],
  variable: "--font-display-loaded",
});

const body = Source_Sans_3({
  subsets: ["latin"],
  variable: "--font-body-loaded",
});

export const metadata: Metadata = {
  title: "GenoLens",
  description: "Local DNA reports — files never leave this machine",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${display.variable} ${body.variable}`}>
      <body
        style={
          {
            "--font-display": "var(--font-display-loaded), Georgia, serif",
            "--font-body": "var(--font-body-loaded), system-ui, sans-serif",
          } as React.CSSProperties
        }
      >
        <SampleProvider>
          <ReportShell>{children}</ReportShell>
        </SampleProvider>
      </body>
    </html>
  );
}
