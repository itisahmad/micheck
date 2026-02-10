import Link from "next/link";
import { Header } from "../components/Header";
import { Footer } from "../components/Footer";

export default function TermsPage() {
  return (
    <>
      <Header />
      <main className="min-h-screen pt-24 pb-16">
        <div className="mx-auto max-w-3xl px-4">
          <h1 className="font-display text-3xl font-bold text-[#e8e6e3]">Terms & Conditions</h1>
          <p className="mt-4 text-[#6b7280]">
            By booking a spot you agree to perform within the allotted time and to follow venue and event rules. Spots are non-transferable and non-refundable.
          </p>
          <Link href="/" className="mt-8 inline-block text-[#f59e0b] hover:underline">← Back to Home</Link>
        </div>
      </main>
      <Footer />
    </>
  );
}
