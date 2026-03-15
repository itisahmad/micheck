"use client";

import { useEffect } from "react";

declare global {
  interface Window {
    Razorpay: any;
  }
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
  useEffect(() => {
    const loadRazorpayScript = () => {
      const script = document.createElement("script");
      script.src = "https://checkout.razorpay.com/v1/checkout.js";
      script.async = true;
      script.onload = () => {
        console.log("Razorpay script loaded");
      };
      document.body.appendChild(script);
    };

    loadRazorpayScript();
  }, []);

  const initiatePayment = async () => {
    try {
      // Create order on backend
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/create-order/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          amount: amount * 100, // Razorpay expects amount in paise
          currency: "INR",
          receipt: `booking_${Date.now()}`,
          notes: {
            name,
            email,
            phone,
            spot_ids: spotIds.join(","),
            coupon_code: couponCode || "",
          },
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to create order");
      }

      const order = await response.json();

      const options = {
        key: process.env.NEXT_PUBLIC_RAZORPAY_KEY_ID || "rzp_test_YourKeyIdHere", // You'll need to set this
        amount: order.amount,
        currency: order.currency,
        name: "MicCheck - Open Mic & Stand-Up Comedy",
        description: `Booking for ${spotIds.length} spot(s)`,
        order_id: order.id,
        handler: function (response: any) {
          // Verify payment on backend
          verifyPayment(response.razorpay_payment_id, response.razorpay_order_id, response.razorpay_signature);
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
            onFailure("Payment cancelled by user");
          },
        },
      };

      const rzp = new window.Razorpay(options);
      rzp.open();
    } catch (error) {
      onFailure(error instanceof Error ? error.message : "Payment initiation failed");
    }
  };

  const verifyPayment = async (paymentId: string, orderId: string, signature: string) => {
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
          name,
          email,
          phone,
          spot_ids: spotIds,
          coupon_code: couponCode,
        }),
      });

      if (!response.ok) {
        throw new Error("Payment verification failed");
      }

      const result = await response.json();
      if (result.success) {
        onSuccess(paymentId);
      } else {
        onFailure(result.message || "Payment verification failed");
      }
    } catch (error) {
      onFailure(error instanceof Error ? error.message : "Payment verification failed");
    }
  };

  return (
    <button
      onClick={initiatePayment}
      className="w-full rounded-xl bg-[#f59e0b] py-4 font-display font-semibold text-[#0c0f14] hover:bg-[#fbbf24] transition-colors"
    >
      Pay ₹{amount.toFixed(0)} with Razorpay
    </button>
  );
}
