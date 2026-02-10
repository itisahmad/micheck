import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "MicCheck — Open Mic & Stand-Up Comedy",
  description: "Your stage for open mic and lineup comedy. Book a spot and perform in front of a live audience.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased min-h-screen bg-[#0c0f14] text-[#e8e6e3]">
        {children}
      </body>
    </html>
  );
}
