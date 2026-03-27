"use client";

import { useEffect, useState } from "react";

declare global {
  interface Window {
    Razorpay: any;
  }
}

function formatTime(timeStr: string) {
  const [h, m] = timeStr.split(":").map(Number);
  const period = h >= 12 ? "PM" : "AM";
  const hour = h % 12 || 12;
  return `${hour}:${m.toString().padStart(2, "0")} ${period}`;
}

interface Spot {
  id: number;
  time: string;
  show_label?: string;
  show_date?: string;
  is_full: boolean;
}

interface RazorpayPaymentProps {
  amount: number;
  name: string;
  email: string;
  phone: string;
  spotIds: number[];
  couponCode?: string;
  onSuccess: (paymentId: string) => void;
  onFailure: (error: string) => void;
}

export default function RazorpayPayment({
  amount,
  name,
  email,
  phone,
  spotIds,
  couponCode,
  onSuccess,
  onFailure,
}: RazorpayPaymentProps) {
  const [checkingAvailability, setCheckingAvailability] = useState(false);

  useEffect(() => {
    // Check if Razorpay script is already loaded
    if (window.Razorpay) {
      console.log("Razorpay script already loaded");
      return;
    }

    const scriptId = "razorpay-checkout-script";
    
    // Check if script tag already exists
    const existingScript = document.getElementById(scriptId);
    if (existingScript) {
      console.log("Razorpay script tag already exists");
      return;
    }

    const loadRazorpayScript = () => {
      const script = document.createElement("script");
      script.id = scriptId;
      script.src = "https://checkout.razorpay.com/v1/checkout.js";
      script.async = true;
      script.onload = () => {
        console.log("Razorpay script loaded successfully");
      };
      script.onerror = () => {
        console.error("Failed to load Razorpay script");
      };
      document.body.appendChild(script);
    };

    loadRazorpayScript();

    // Cleanup function (optional - for component unmount)
    return () => {
      // We don't remove the script on unmount as it might be needed by other components
      // But we prevent re-adding it with the ID check above
    };
  }, []); // Empty dependency array ensures this runs only once

  const initiatePayment = async () => {
    try {
      setCheckingAvailability(true);
      
      // First check if spots are still available
      const availabilityResponse = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/spots/`);
      const spotsData = await availabilityResponse.json();
      
      // Check if selected spots are still available
      const selectedSpotsData = spotsData.filter((spot: Spot) => spotIds.includes(spot.id));
      const unavailableSpots = selectedSpotsData.filter((spot: Spot) => spot.is_full);
      
      if (unavailableSpots.length > 0) {
        const spotNames = unavailableSpots.map((spot: Spot) => 
          `${spot.show_label || spot.show_date} - ${formatTime(spot.time)}`
        ).join(", ");
        setCheckingAvailability(false);
        onFailure(`The following spots are already booked: ${spotNames}. Please select different spots.`);
        return;
      }
      
      // Create pre-booking first
      const preBookingResponse = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/pre-booking/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          spot_ids: spotIds.join(","),
          name,
          email,
          phone,
          coupon_code: couponCode || "",
          amount: amount,
        }),
      });

      if (!preBookingResponse.ok) {
        const errorData = await preBookingResponse.json();
        setCheckingAvailability(false);
        onFailure(errorData.error || "Failed to create booking");
        return;
      }

      const preBookingData = await preBookingResponse.json();
      const bookingIds = preBookingData.bookings.map((booking: any) => booking.id);

      // Create Razorpay order
      const orderResponse = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/create-order/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          amount: preBookingData.total_amount * 100, // Razorpay expects amount in paise
          currency: "INR",
          receipt: `booking_${Date.now()}`,
          notes: {
            name,
            email,
            phone,
            spot_ids: spotIds.join(","),
            coupon_code: couponCode || "",
            booking_ids: bookingIds.join(","),
          },
        }),
      });

      if (!orderResponse.ok) {
        throw new Error("Failed to create order");
      }

      const order = await orderResponse.json();

      const options = {
        key: process.env.NEXT_PUBLIC_RAZORPAY_KEY_ID || "rzp_test_YourKeyIdHere", // You'll need to set this
        amount: order.amount,
        currency: order.currency,
        name: "MicCheck - Open Mic & Stand-Up Comedy",
        description: `Booking for ${spotIds.length} spot(s)`,
        order_id: order.id,
        handler: function (response: any) {
          // Verify payment on backend with booking IDs
          verifyPayment(response.razorpay_payment_id, response.razorpay_order_id, response.razorpay_signature, bookingIds);
        },
        prefill: {
          name: name,
          email: email,
          contact: phone,
        },
        theme: {
          color: "#f59e0b", // Amber color matching your theme
        },
        modal: {
          ondismiss: function () {
            // Handle payment cancellation
            handlePaymentCancellation(bookingIds);
            setCheckingAvailability(false);
            onFailure("Payment cancelled by user");
          },
        },
      };

      const rzp = new window.Razorpay(options);
      rzp.open();
    } catch (error) {
      setCheckingAvailability(false);
      onFailure(error instanceof Error ? error.message : "Payment initiation failed");
    }
  };

  const verifyPayment = async (paymentId: string, orderId: string, signature: string, bookingIds: string[]) => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/verify-payment/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          razorpay_payment_id: paymentId,
          razorpay_order_id: orderId,
          razorpay_signature: signature,
          booking_ids: bookingIds,
        }),
      });

      if (!response.ok) {
        throw new Error("Payment verification failed");
      }

      const result = await response.json();
      if (result.success) {
        onSuccess(paymentId);
      } else {
        onFailure(result.error || "Payment verification failed");
      }
    } catch (error) {
      onFailure(error instanceof Error ? error.message : "Payment verification failed");
    }
  };

  const handlePaymentCancellation = async (bookingIds: string[]) => {
    console.log("[FRONTEND] Payment cancelled by user, calling cancellation API...");
    console.log("[FRONTEND] Booking IDs to cancel:", bookingIds);
    
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/payment-cancelled/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          booking_ids: bookingIds,
        }),
      });

      console.log("[FRONTEND] Cancellation API response status:", response.status);
      
      if (!response.ok) {
        const errorData = await response.json();
        console.error("[FRONTEND] Failed to cancel bookings:", errorData);
      } else {
        const successData = await response.json();
        console.log("[FRONTEND] Cancellation successful:", successData);
      }
    } catch (error) {
      console.error("[FRONTEND] Error cancelling bookings:", error);
    }
  };

  return (
    <button
      onClick={initiatePayment}
      disabled={checkingAvailability}
      className="w-full rounded-xl bg-[#f59e0b] py-4 font-display font-semibold text-[#0c0f14] hover:bg-[#fbbf24] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
    >
      {checkingAvailability ? "Checking availability..." : `Pay ₹${amount.toFixed(0)} with Razorpay`}
    </button>
  );
}
