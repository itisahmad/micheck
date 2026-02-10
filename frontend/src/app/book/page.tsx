"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Header } from "../components/Header";
import { Footer } from "../components/Footer";
import {
  fetchSpots,
  validateCoupon,
  createBooking,
  type Spot,
  type CouponValidation,
} from "@/lib/api";

function formatTime(timeStr: string) {
  const [h, m] = timeStr.split(":").map(Number);
  const period = h >= 12 ? "PM" : "AM";
  const hour = h % 12 || 12;
  return `${hour}:${m.toString().padStart(2, "0")} ${period}`;
}

function formatPrice(price: string) {
  return `₹${Number(price).toFixed(0)}`;
}

type SpotWithSelected = Spot & { selected?: boolean };

export default function BookPage() {
  const [spots, setSpots] = useState<SpotWithSelected[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [couponCode, setCouponCode] = useState("");
  const [couponApplied, setCouponApplied] = useState<CouponValidation | null>(null);
  const [couponLoading, setCouponLoading] = useState(false);

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");

  const [submitting, setSubmitting] = useState(false);
  const [submitSuccess, setSubmitSuccess] = useState<string | null>(null);
  const [submitError, setSubmitError] = useState<string | null>(null);

  useEffect(() => {
    fetchSpots()
      .then((data) => setSpots(data.map((s) => ({ ...s, selected: false }))))
      .catch(() => setError("Failed to load spots"))
      .finally(() => setLoading(false));
  }, []);

  const selectedSpots = spots.filter((s) => s.selected);
  const totalBeforeCoupon = selectedSpots.reduce((sum, s) => sum + Number(s.price), 0);
  const spotCount = selectedSpots.length;

  let displayTotal = totalBeforeCoupon;
  if (couponApplied?.valid && couponApplied.discount_type === "fixed" && spotCount >= (couponApplied.min_spots ?? 0)) {
    displayTotal = spotCount * Number(couponApplied.discount_value ?? 0);
  } else if (couponApplied?.valid && couponApplied.discount_type === "percent") {
    displayTotal = totalBeforeCoupon * (1 - Number(couponApplied.discount_value ?? 0) / 100);
  }

  const toggleSpot = (id: number) => {
    setSpots((prev) =>
      prev.map((s) => (s.id === id ? { ...s, selected: !s.selected } : s))
    );
    setCouponApplied(null);
  };

  const applyCoupon = async () => {
    if (!couponCode.trim()) return;
    setCouponLoading(true);
    setCouponApplied(null);
    try {
      const result = await validateCoupon({ code: couponCode.trim(), spot_count: spotCount });
      setCouponApplied(result);
    } catch {
      setCouponApplied({ valid: false, message: "Could not validate coupon." });
    } finally {
      setCouponLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (selectedSpots.length === 0) {
      setSubmitError("Select at least one spot.");
      return;
    }
    setSubmitting(true);
    setSubmitError(null);
    try {
      await createBooking({
        spot_ids: selectedSpots.map((s) => s.id),
        performer_name: name,
        email,
        phone,
        coupon_code: couponCode.trim() || undefined,
      });
      setSubmitSuccess("Booking successful! We'll be in touch.");
      setName("");
      setEmail("");
      setPhone("");
      setCouponCode("");
      setCouponApplied(null);
      setSpots((prev) => prev.map((s) => ({ ...s, selected: false })));
    } catch (err) {
      setSubmitError(err instanceof Error ? err.message : "Booking failed.");
    } finally {
      setSubmitting(false);
    }
  };

  const byDate = spots.reduce<Record<string, SpotWithSelected[]>>((acc, s) => {
    const key = s.show_label || s.show_date;
    if (!acc[key]) acc[key] = [];
    acc[key].push(s);
    return acc;
  }, {});

  return (
    <>
      <Header />
      <main className="min-h-screen pt-24 pb-16">
        <div className="mx-auto max-w-3xl px-4">
          <h1 className="font-display text-2xl font-bold text-[#e8e6e3]">
            Spot Registration Form
          </h1>
          <p className="mt-2 text-[#6b7280]">
            Please select the spots you would like to register.
          </p>

          {loading && (
            <p className="mt-8 text-[#6b7280]">Loading spots…</p>
          )}
          {error && (
            <p className="mt-8 text-red-400">{error}</p>
          )}

          {!loading && !error && (
            <form onSubmit={handleSubmit} className="mt-8 space-y-8">
              {/* Available Spots - all dates/slots from backend */}
              <div>
                <h2 className="font-display text-lg font-semibold text-[#e8e6e3]">
                  Available Spots
                </h2>
                <div className="mt-4 space-y-6">
                  {Object.entries(byDate).map(([dateLabel, dateSpots]) => (
                    <div key={dateLabel}>
                      <p className="text-sm font-semibold text-[#f59e0b]">{dateLabel}</p>
                      <ul className="mt-2 space-y-2">
                        {dateSpots.map((spot) => {
                          const full = spot.is_full;
                          const selected = !!spot.selected;
                          return (
                            <li key={spot.id}>
                              <label
                                className={`flex cursor-pointer items-center justify-between gap-4 rounded-lg border px-4 py-3 transition ${
                                  full
                                    ? "cursor-not-allowed border-[#2a3142] bg-[#151922]/80 opacity-70"
                                    : selected
                                      ? "border-[#f59e0b] bg-[#f59e0b]/10"
                                      : "border-[#2a3142] bg-[#151922] hover:border-[#2a3142]/80"
                                }`}
                              >
                                <input
                                  type="checkbox"
                                  checked={selected}
                                  disabled={full}
                                  onChange={() => toggleSpot(spot.id)}
                                  className="sr-only"
                                />
                                <span className="text-[#e8e6e3]">
                                  {formatTime(spot.time)}, {spot.duration_minutes} Mins Spot — {formatPrice(spot.price)}
                                  {spot.spot_type && (
                                    <span className="ml-1 text-[#6b7280]">[{spot.spot_type}]</span>
                                  )}
                                </span>
                                {full && (
                                  <span className="shrink-0 rounded bg-red-500/20 px-2 py-0.5 text-xs font-medium text-red-400">
                                    Spots Full
                                  </span>
                                )}
                              </label>
                            </li>
                          );
                        })}
                      </ul>
                    </div>
                  ))}
                </div>
              </div>

              {/* Total */}
              <div className="rounded-xl border border-[#2a3142] bg-[#151922] px-4 py-4">
                <p className="font-display text-lg font-semibold text-[#e8e6e3]">
                  Total
                </p>
                <p className="mt-1 text-2xl font-bold text-[#f59e0b]">
                  {formatPrice(displayTotal.toFixed(2))}
                </p>
                {selectedSpots.length === 0 && (
                  <p className="mt-1 text-sm text-[#6b7280]">Select at least one spot</p>
                )}
              </div>

              {/* Performer Details */}
              <div className="rounded-xl border border-[#2a3142] bg-[#151922] p-6">
                <h2 className="font-display text-lg font-semibold text-[#e8e6e3]">
                  Performer Details
                </h2>
                <div className="mt-4 space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-[#e8e6e3]">Full name</label>
                    <input
                      type="text"
                      required
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      className="mt-1 w-full rounded-lg border border-[#2a3142] bg-[#0c0f14] px-4 py-2 text-[#e8e6e3] focus:border-[#f59e0b] focus:outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-[#e8e6e3]">Email address</label>
                    <input
                      type="email"
                      required
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      className="mt-1 w-full rounded-lg border border-[#2a3142] bg-[#0c0f14] px-4 py-2 text-[#e8e6e3] focus:border-[#f59e0b] focus:outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-[#e8e6e3]">Phone number</label>
                    <input
                      type="tel"
                      required
                      value={phone}
                      onChange={(e) => setPhone(e.target.value)}
                      className="mt-1 w-full rounded-lg border border-[#2a3142] bg-[#0c0f14] px-4 py-2 text-[#e8e6e3] focus:border-[#f59e0b] focus:outline-none"
                    />
                  </div>
                </div>
              </div>

              {/* I have Coupon Code */}
              <div className="rounded-xl border border-[#2a3142] bg-[#151922] p-6">
                <p className="text-sm font-medium text-[#e8e6e3]">I have Coupon Code</p>
                <div className="mt-3 flex gap-2">
                  <input
                    type="text"
                    value={couponCode}
                    onChange={(e) => setCouponCode(e.target.value)}
                    placeholder="Enter code"
                    className="flex-1 rounded-lg border border-[#2a3142] bg-[#0c0f14] px-4 py-2 text-[#e8e6e3] placeholder:text-[#6b7280] focus:border-[#f59e0b] focus:outline-none"
                  />
                  <button
                    type="button"
                    onClick={applyCoupon}
                    disabled={couponLoading || spotCount === 0}
                    className="rounded-lg bg-[#f59e0b] px-4 py-2 font-medium text-[#0c0f14] disabled:opacity-50"
                  >
                    {couponLoading ? "Checking…" : "Apply"}
                  </button>
                </div>
                {couponApplied && !couponApplied.valid && (
                  <p className="mt-2 text-sm text-red-400">{couponApplied.message}</p>
                )}
                {couponApplied?.valid && (
                  <p className="mt-2 text-sm text-[#22c55e]">Coupon applied.</p>
                )}
              </div>

              {/* Valentine's Week Offer */}
              <div className="rounded-xl border border-[#f59e0b]/40 bg-[#f59e0b]/10 p-4 text-center text-sm text-[#e8e6e3]">
                <strong className="text-[#f59e0b]">Valentine&apos;s Week Offer!</strong>
                <br />
                Book minimum <strong>6 spots</strong> and use coupon code <code className="rounded bg-[#0c0f14] px-2 py-0.5 font-mono text-[#f59e0b]">iLoveVC2</code> to get spots at just ₹100/Spot
              </div>

              {submitSuccess && (
                <p className="rounded-lg bg-[#22c55e]/20 p-4 text-[#22c55e]">{submitSuccess}</p>
              )}
              {submitError && (
                <p className="rounded-lg bg-red-500/20 p-4 text-red-400">{submitError}</p>
              )}

              <button
                type="submit"
                disabled={submitting || selectedSpots.length === 0}
                className="w-full rounded-xl bg-[#f59e0b] py-4 font-display font-semibold text-[#0c0f14] disabled:opacity-50 hover:bg-[#fbbf24] sm:w-auto sm:px-12"
              >
                {submitting ? "Submitting…" : "Submit"}
              </button>

              <p className="text-center text-sm text-[#6b7280]">
                *Spots Once Booked are Non Transferable and Non Refundable
                <br />
                <Link href="/refund" className="text-[#f59e0b] hover:underline">Refund policy</Link>
                {" · "}
                <Link href="/privacy" className="text-[#f59e0b] hover:underline">Privacy Policy</Link>
                {" · "}
                <Link href="/terms" className="text-[#f59e0b] hover:underline">Terms & Conditions</Link>
              </p>
            </form>
          )}
        </div>
      </main>
      <Footer />
    </>
  );
}
