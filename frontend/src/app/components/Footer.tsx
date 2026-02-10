import Link from "next/link";
import Image from "next/image";

export function Footer() {
  return (
    <footer className="border-t border-[#2a3142] bg-[#151922]">
      <div className="mx-auto max-w-6xl px-4 py-12">
        <div className="grid gap-8 md:grid-cols-4">
          <div>
            <Link href="/" className="inline-block">
              <Image
                src="/mic_check_logo.PNG"
                alt="MicCheck"
                width={100}
                height={34}
                className="h-8 w-auto object-contain"
                unoptimized
              />
            </Link>
            <p className="mt-2 text-sm text-[#6b7280]">
              Your stage for open mic and lineup comedy. Book a spot and perform.
            </p>
          </div>
          <div>
            <p className="text-sm font-semibold text-[#e8e6e3]">Quick Links</p>
            <ul className="mt-3 space-y-2">
              {["Home", "About", "Shows", "Book Spot"].map((label) => (
                <li key={label}>
                  <Link
                    href={label === "Home" ? "/" : label === "Book Spot" ? "/book" : `/#${label.toLowerCase().replace(" ", "-")}`}
                    className="text-sm text-[#6b7280] hover:text-[#f59e0b]"
                  >
                    {label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
          <div>
            <p className="text-sm font-semibold text-[#e8e6e3]">Legal</p>
            <ul className="mt-3 space-y-2">
              <li><Link href="/privacy" className="text-sm text-[#6b7280] hover:text-[#f59e0b]">Privacy Policy</Link></li>
              <li><Link href="/refund" className="text-sm text-[#6b7280] hover:text-[#f59e0b]">Refund Policy</Link></li>
              <li><Link href="/terms" className="text-sm text-[#6b7280] hover:text-[#f59e0b]">Terms & Conditions</Link></li>
            </ul>
          </div>
          <div>
            <p className="text-sm font-semibold text-[#e8e6e3]">Contact</p>
            <p className="mt-3 text-sm text-[#6b7280]">PVR Complex, Saket</p>
            <a href="mailto:hello@miccheck.com" className="text-sm text-[#6b7280] hover:text-[#f59e0b]">hello@miccheck.com</a>
          </div>
        </div>
        <p className="mt-10 border-t border-[#2a3142] pt-8 text-center text-sm text-[#6b7280]">
          © {new Date().getFullYear()} MicCheck. All rights reserved.
        </p>
      </div>
    </footer>
  );
}
