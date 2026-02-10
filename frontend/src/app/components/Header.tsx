import Link from "next/link";
import Image from "next/image";

const nav = [
  { label: "Home", href: "/" },
  { label: "About", href: "/#about" },
  { label: "Shows", href: "/#shows" },
  { label: "How It Works", href: "/#how-it-works" },
  { label: "Book Spot", href: "/book" },
];

export function Header() {
  return (
    <header className="fixed top-0 left-0 right-0 z-50 border-b border-[#2a3142] bg-[#0c0f14]/90 backdrop-blur-md">
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-4">
        <Link href="/" className="flex items-center gap-2">
          <Image
            src="/mic_check_logo.PNG"
            alt="MicCheck"
            width={120}
            height={40}
            className="h-9 w-auto object-contain"
            unoptimized
          />
        </Link>
        <nav className="hidden gap-8 md:flex">
          {nav.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className="text-sm font-medium text-[#e8e6e3]/80 transition hover:text-[#f59e0b]"
            >
              {item.label}
            </Link>
          ))}
        </nav>
        <Link
          href="/book"
          className="rounded-lg bg-[#f59e0b] px-4 py-2 text-sm font-semibold text-[#0c0f14] transition hover:bg-[#fbbf24]"
        >
          Book Spot
        </Link>
      </div>
    </header>
  );
}
