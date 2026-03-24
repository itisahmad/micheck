"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Header } from "../components/Header";
import { Footer } from "../components/Footer";
import RazorpayPayment from "../components/RazorpayPayment";
import {
  fetchSpots,
  validateCoupon,
  type Spot,
  type CouponValidation,
} from "@/lib/api";

interface MaintenanceData {
  maintenance_mode: boolean;
  maintenance_message: string;
}

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
  const [maintenanceData, setMaintenanceData] = useState<MaintenanceData | null>(null);
  const [maintenanceLoading, setMaintenanceLoading] = useState(true);
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
  const [paymentStep, setPaymentStep] = useState(false);

  useEffect(() => {
    const checkMaintenanceAndFetchSpots = async () => {
      try {
        // First check maintenance status
        const apiUrl = `${process.env.NEXT_PUBLIC_API_URL}/maintenance-status/`;
        console.log("DEBUG: Calling maintenance API:", apiUrl);
        
        const maintenanceResponse = await fetch(apiUrl);
        
        if (!maintenanceResponse.ok) {
          throw new Error(`HTTP error! status: ${maintenanceResponse.status}`);
        }
        
        const maintenanceData = await maintenanceResponse.json();
        console.log("DEBUG: Maintenance data:", maintenanceData);
        setMaintenanceData(maintenanceData);
        setMaintenanceLoading(false);

        // TEMPORARY TEST: Force maintenance mode to test display
        const testMaintenanceMode = true; // Set to false to disable test
        
        // If in maintenance mode, don't fetch spots
        if (maintenanceData.maintenance_mode || testMaintenanceMode) {
          console.log("DEBUG: Site is in maintenance mode, not fetching spots");
          setLoading(false);
          return;
        }

        // Only fetch spots if not in maintenance
        console.log("DEBUG: Site is not in maintenance mode, fetching spots");
        fetchSpots()
          .then((data) => setSpots(data.map((s) => ({ ...s, selected: false }))))
          .catch(() => setError("Failed to load spots"))
          .finally(() => setLoading(false));
      } catch (error) {
        console.error("Failed to check maintenance status:", error);
        setMaintenanceLoading(false);
        setError("Failed to check system status");
        setLoading(false);
      }
    };

    checkMaintenanceAndFetchSpots();
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

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (selectedSpots.length === 0) {
      setSubmitError("Select at least one spot.");
      return;
    }
    if (!name.trim() || !email.trim() || !phone.trim()) {
      setSubmitError("Please fill in all performer details.");
      return;
    }
    setPaymentStep(true);
  };

  const handlePaymentSuccess = (paymentId: string) => {
    setSubmitSuccess(`Payment successful! Your booking is confirmed. Payment ID: ${paymentId}`);
    setName("");
    setEmail("");
    setPhone("");
    setCouponCode("");
    setCouponApplied(null);
    setSpots((prev) => prev.map((s) => ({ ...s, selected: false })));
    setPaymentStep(false);
  };

  const handlePaymentFailure = (error: string) => {
    setSubmitError(error);
    setPaymentStep(false);
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

          {maintenanceLoading && (
            <div className="mt-8 text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#f59e0b] mx-auto mb-4"></div>
              <p className="text-[#6b7280]">Checking system status...</p>
            </div>
          )}
          
          {(maintenanceData?.maintenance_mode || true) && !maintenanceLoading && (
            <div className="mt-8 bg-[#1a1f2e] rounded-xl p-8 border-2 border-[#f59e0b]">
              <div className="text-center mb-6">
                <div className="w-16 h-16 bg-[#f59e0b] rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg
                    className="w-8 h-8 text-[#0c0f14]"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c-.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
                    />
                  </svg>
                </div>
              </div>
              <h2 className="font-display text-2xl font-bold text-white text-center mb-6">
                🔧 Under Maintenance
              </h2>
              <div className="bg-[#0c0f14] rounded-lg p-6 mb-6">
                <p className="text-[#e8e6e3] text-lg leading-relaxed text-center">
                  {maintenanceData?.maintenance_message || "We are currently under maintenance. Please check back soon."}
                </p>
              </div>
              <div className="text-center space-y-4">
                <p className="text-[#6b7280] text-sm">
                  We're working to improve your experience. Please check back shortly.
                </p>
                <div className="pt-4">
                  <button
                    onClick={() => window.location.reload()}
                    className="bg-[#f59e0b] hover:bg-[#fbbf24] text-[#0c0f14] px-6 py-3 rounded-lg font-semibold transition-colors"
                  >
                    Check Again
                  </button>
                </div>
              </div>
            </div>
          )}
          
          {loading && !maintenanceLoading && !maintenanceData?.maintenance_mode && (
            <p className="mt-8 text-[#6b7280]">Loading spots…</p>
          )}
          {error && !maintenanceData?.maintenance_mode && (
            <p className="mt-8 text-red-400">{error}</p>
          )}

          {!loading && !error && !maintenanceData?.maintenance_mode && (
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
              {/* <div className="rounded-xl border border-[#f59e0b]/40 bg-[#f59e0b]/10 p-4 text-center text-sm text-[#e8e6e3]">
                <strong className="text-[#f59e0b]">Valentine&apos;s Week Offer!</strong>
                <br />
                Book minimum <strong>6 spots</strong> and use coupon code <code className="rounded bg-[#0c0f14] px-2 py-0.5 font-mono text-[#f59e0b]">iLoveVC2</code> to get spots at just ₹100/Spot
              </div> */}

              {submitSuccess && (
                <p className="rounded-lg bg-[#22c55e]/20 p-4 text-[#22c55e]">{submitSuccess}</p>
              )}
              {submitError && (
                <p className="rounded-lg bg-red-500/20 p-4 text-red-400">{submitError}</p>
              )}

              {paymentStep ? (
                <div className="space-y-4">
                  <p className="text-center text-[#e8e6e3]">Complete your payment to confirm the booking:</p>
                  <RazorpayPayment
                    amount={displayTotal}
                    name={name}
                    email={email}
                    phone={phone}
                    spotIds={selectedSpots.map((s) => s.id)}
                    couponCode={couponCode.trim() || undefined}
                    onSuccess={handlePaymentSuccess}
                    onFailure={handlePaymentFailure}
                  />
                  <button
                    type="button"
                    onClick={() => setPaymentStep(false)}
                    className="w-full rounded-xl border border-[#2a3142] bg-[#151922] py-3 font-display font-semibold text-[#e8e6e3] hover:bg-[#2a3142]"
                  >
                    Cancel Payment
                  </button>
                </div>
              ) : (
                <button
                  type="submit"
                  disabled={submitting || selectedSpots.length === 0}
                  className="w-full rounded-xl bg-[#f59e0b] py-4 font-display font-semibold text-[#0c0f14] disabled:opacity-50 hover:bg-[#fbbf24] sm:w-auto sm:px-12"
                >
                  {submitting ? "Processing…" : "Proceed to Payment"}
                </button>
              )}

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
