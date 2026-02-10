const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

export interface Spot {
  id: number;
  show: number;
  show_date: string;
  show_label: string;
  time: string;
  duration_minutes: number;
  price: string;
  spot_type: string;
  max_slots: number;
  is_full: boolean;
  spots_remaining: number;
}

export interface Show {
  id: number;
  date: string;
  label: string;
  spots: Spot[];
}

export async function fetchSpots(): Promise<Spot[]> {
  const res = await fetch(`${API_BASE}/spots/`, { cache: 'no-store' });
  if (!res.ok) throw new Error('Failed to fetch spots');
  return res.json();
}

export async function fetchShows(): Promise<Show[]> {
  const res = await fetch(`${API_BASE}/shows/`, { cache: 'no-store' });
  if (!res.ok) throw new Error('Failed to fetch shows');
  return res.json();
}

export interface ValidateCouponPayload {
  code: string;
  spot_count: number;
}

export interface CouponValidation {
  valid: boolean;
  message?: string;
  min_spots?: number;
  discount_type?: string;
  discount_value?: string;
  description?: string;
}

export async function validateCoupon(payload: ValidateCouponPayload): Promise<CouponValidation> {
  const res = await fetch(`${API_BASE}/coupon/validate/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  return res.json();
}

export interface CreateBookingPayload {
  spot_ids: number[];
  performer_name: string;
  email: string;
  phone: string;
  coupon_code?: string;
}

export async function createBooking(payload: CreateBookingPayload): Promise<{ success: boolean; message: string; total: number }> {
  const res = await fetch(`${API_BASE}/bookings/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || data.coupon_code?.[0] || data.spot_ids?.[0] || 'Booking failed');
  return data;
}
