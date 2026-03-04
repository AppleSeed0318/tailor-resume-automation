import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Resume Tailor AI",
  description: "Tailor your resume to any job description for a 100% match.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
