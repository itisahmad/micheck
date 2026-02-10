import Link from "next/link";
import { Header } from "./components/Header";
import { Footer } from "./components/Footer";

export default function HomePage() {
  return (
    <>
      <Header />
      <main className="pt-16">
        {/* Hero */}
        <section className="relative overflow-hidden border-b border-[#2a3142] bg-gradient-to-b from-[#151922] to-[#0c0f14] px-4 py-24 md:py-32">
          <div className="absolute inset-0 bg-[radial-gradient(ellipse_80%_50%_at_50%_-20%,rgba(245,158,11,0.12),transparent)]" />
          <div className="relative mx-auto max-w-4xl text-center">
            <p className="font-display text-sm font-semibold uppercase tracking-widest text-[#f59e0b]">
              Open Mic & Lineup Shows
            </p>
            <h1 className="font-display mt-4 text-4xl font-bold leading-tight tracking-tight md:text-6xl">
              Your Stage
              <span className="block text-[#f59e0b]">Awaits</span>
            </h1>
            <p className="mx-auto mt-6 max-w-xl text-lg text-[#6b7280]">
              Whether you&apos;re new or experienced, grab a spot and make the room laugh. Book your slot and step up.
            </p>
            <Link
              href="/book"
              className="mt-10 inline-block rounded-xl bg-[#f59e0b] px-8 py-4 font-display text-lg font-semibold text-[#0c0f14] transition hover:bg-[#fbbf24]"
            >
              Book Your Spot
            </Link>
          </div>
        </section>

        {/* Stats */}
        <section className="border-b border-[#2a3142] bg-[#151922] px-4 py-12">
          <div className="mx-auto grid max-w-4xl grid-cols-3 gap-8 text-center">
            {[
              { value: "100+", label: "Shows Hosted" },
              { value: "500+", label: "Performers" },
              { value: "10K+", label: "Laughs Generated" },
            ].map((item) => (
              <div key={item.label}>
                <p className="font-display text-3xl font-bold text-[#f59e0b] md:text-4xl">{item.value}</p>
                <p className="mt-1 text-sm text-[#6b7280]">{item.label}</p>
              </div>
            ))}
          </div>
        </section>

        {/* About */}
        <section id="about" className="scroll-mt-20 border-b border-[#2a3142] px-4 py-20">
          <div className="mx-auto max-w-4xl">
            <p className="font-display text-sm font-semibold uppercase tracking-widest text-[#f59e0b]">
              Welcome to MicCheck
            </p>
            <h2 className="font-display mt-2 text-3xl font-bold md:text-4xl">
              Your Time Is Here
            </h2>
            <p className="mt-6 text-lg leading-relaxed text-[#6b7280]">
              From the local scene to the spotlight. MicCheck is where chai-time jokes become stage sets. Got stories about metro rides, relatives, or office drama? This is your stage.
            </p>
          </div>
        </section>

        {/* Show formats */}
        <section id="shows" className="scroll-mt-20 border-b border-[#2a3142] bg-[#151922] px-4 py-20">
          <div className="mx-auto max-w-5xl">
            <p className="font-display text-sm font-semibold uppercase tracking-widest text-[#f59e0b]">
              What We Offer
            </p>
            <h2 className="font-display mt-2 text-3xl font-bold md:text-4xl">
              Show Formats
            </h2>
            <div className="mt-12 grid gap-8 md:grid-cols-2">
              <div className="rounded-2xl border border-[#2a3142] bg-[#0c0f14] p-8 transition hover:border-[#f59e0b]/40">
                <h3 className="font-display text-xl font-semibold text-[#e8e6e3]">Open Mic Shows</h3>
                <p className="mt-4 text-[#6b7280]">
                  Ideal for first-timers and regulars. Get 5–7 minutes to try material. No experience needed — bring your sense of humour and get on stage.
                </p>
              </div>
              <div className="rounded-2xl border border-[#2a3142] bg-[#0c0f14] p-8 transition hover:border-[#f59e0b]/40">
                <h3 className="font-display text-xl font-semibold text-[#e8e6e3]">Lineup Shows</h3>
                <p className="mt-4 text-[#6b7280]">
                  Curated nights with multiple acts. Each comedian gets a dedicated slot. For when you&apos;re ready to deliver a full set.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Who can perform */}
        <section className="border-b border-[#2a3142] px-4 py-20">
          <div className="mx-auto max-w-4xl text-center">
            <p className="font-display text-sm font-semibold uppercase tracking-widest text-[#f59e0b]">
              Who Can Perform?
            </p>
            <h2 className="font-display mt-2 text-3xl font-bold md:text-4xl">
              Everyone Is Welcome
            </h2>
            <p className="mt-6 text-[#6b7280]">
              First time or hundredth — everyone is welcome. From students to professionals, all levels are welcome.
            </p>
            <ul className="mt-10 space-y-4 text-left md:mx-auto md:max-w-lg">
              {[
                "First time? Nerves are normal. The crowd is supportive — just show up.",
                "Testing material? Open mic is your lab. Try, fail, improve, repeat.",
                "Experienced? Need stage time or new bits? We’ve got slots for you.",
                "Office comedian? Prove it on stage.",
              ].map((text, i) => (
                <li key={i} className="flex gap-3 rounded-lg border border-[#2a3142] bg-[#151922] px-4 py-3 text-sm text-[#e8e6e3]">
                  <span className="text-[#f59e0b]">•</span> {text}
                </li>
              ))}
            </ul>
            <Link
              href="/book"
              className="mt-10 inline-block rounded-xl bg-[#f59e0b] px-6 py-3 font-semibold text-[#0c0f14] hover:bg-[#fbbf24]"
            >
              Register to Perform
            </Link>
          </div>
        </section>

        {/* How it works */}
        <section id="how-it-works" className="scroll-mt-20 border-b border-[#2a3142] bg-[#151922] px-4 py-20">
          <div className="mx-auto max-w-5xl">
            <p className="font-display text-sm font-semibold uppercase tracking-widest text-[#f59e0b]">
              Simple Process
            </p>
            <h2 className="font-display mt-2 text-3xl font-bold md:text-4xl">
              How It Works
            </h2>
            <div className="mt-14 grid gap-8 md:grid-cols-4">
              {[
                { step: "1", title: "Register Online", desc: "Fill the form with your details and preferred show date." },
                { step: "2", title: "Book Your Spot", desc: "Complete payment to secure your slot. Spots are limited." },
                { step: "3", title: "Prepare Your Set", desc: "Work on 5–7 minutes of your best material." },
                { step: "4", title: "Hit the Stage", desc: "Show up, perform, and make the room laugh." },
              ].map((item) => (
                <div key={item.step}>
                  <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-[#f59e0b] font-display text-lg font-bold text-[#0c0f14]">
                    {item.step}
                  </div>
                  <h3 className="mt-4 font-display font-semibold text-[#e8e6e3]">{item.title}</h3>
                  <p className="mt-2 text-sm text-[#6b7280]">{item.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Testimonials */}
        <section className="border-b border-[#2a3142] px-4 py-20">
          <div className="mx-auto max-w-5xl">
            <p className="font-display text-sm font-semibold uppercase tracking-widest text-[#f59e0b]">
              What Performers Say
            </p>
            <h2 className="font-display mt-2 text-3xl font-bold md:text-4xl">
              Success Stories
            </h2>
            <div className="mt-12 grid gap-8 md:grid-cols-3">
              {[
                { quote: "I used to only crack jokes at work. MicCheck gave me a real stage. Now people actually call me a comedian.", name: "Vikas Sharma", role: "IT Professional, Gurgaon", initial: "V" },
                { quote: "Five open mics here. I learn something new every time. The crowd is supportive even when jokes don’t land.", name: "Neha Gupta", role: "College Student, DU", initial: "N" },
                { quote: "Great location, easy booking, professional setup. I come every week now.", name: "Rohit Malhotra", role: "Regular Performer", initial: "R" },
              ].map((t) => (
                <div key={t.name} className="rounded-2xl border border-[#2a3142] bg-[#151922] p-6">
                  <p className="text-[#e8e6e3]">&ldquo;{t.quote}&rdquo;</p>
                  <div className="mt-6 flex items-center gap-4">
                    <div className="flex h-12 w-12 items-center justify-center rounded-full bg-[#f59e0b] font-display font-bold text-[#0c0f14]">
                      {t.initial}
                    </div>
                    <div>
                      <p className="font-semibold text-[#e8e6e3]">{t.name}</p>
                      <p className="text-sm text-[#6b7280]">{t.role}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* CTA */}
        <section className="px-4 py-24">
          <div className="mx-auto max-w-2xl rounded-3xl border border-[#2a3142] bg-[#151922] p-10 text-center">
            <h2 className="font-display text-2xl font-bold md:text-3xl">
              Ready to Make Them Laugh?
            </h2>
            <p className="mt-4 text-[#6b7280]">
              Don’t wait for the perfect moment. The stage is ready — book your spot today.
            </p>
            <Link
              href="/book"
              className="mt-8 inline-block rounded-xl bg-[#f59e0b] px-8 py-4 font-display font-semibold text-[#0c0f14] hover:bg-[#fbbf24]"
            >
              Book Your Spot Today
            </Link>
          </div>
        </section>
      </main>
      <Footer />
    </>
  );
}
