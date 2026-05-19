"use client";

import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { AuthCard } from "@/components/auth-card";
import { getMe, triggerOutboundCall, type User } from "@/lib/api";
import { clearToken, getToken } from "@/lib/auth";

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [phone, setPhone] = useState("");
  const [customerName, setCustomerName] = useState("");
  const [callError, setCallError] = useState("");
  const [callSuccess, setCallSuccess] = useState("");
  const [loadingUser, setLoadingUser] = useState(true);
  const [placingCall, setPlacingCall] = useState(false);

  useEffect(() => {
    if (!getToken()) {
      router.replace("/login");
      return;
    }

    getMe()
      .then(setUser)
      .catch(() => {
        clearToken();
        router.replace("/login");
      })
      .finally(() => setLoadingUser(false));
  }, [router]);

  async function handleCallSubmit(event: FormEvent) {
    event.preventDefault();
    setCallError("");
    setCallSuccess("");
    setPlacingCall(true);

    try {
      await triggerOutboundCall(phone.trim(), customerName.trim());
      setCallSuccess("Call triggered successfully.");
      setPhone("");
      setCustomerName("");
    } catch (err) {
      setCallError(err instanceof Error ? err.message : "Failed to place call.");
    } finally {
      setPlacingCall(false);
    }
  }

  function handleLogout() {
    clearToken();
    router.push("/login");
  }

  if (loadingUser) {
    return (
      <div className="page-shell">
        <p className="text-slate-400">Loading dashboard...</p>
      </div>
    );
  }

  return (
    <div className="page-shell">
      <AuthCard
        eyebrow="Dashboard"
        title={`Hello, ${user?.full_name ?? "User"}`}
        subtitle="Place outbound calls through your Exotel integration."
      >
        <div className="mb-6 rounded-lg border border-slate-800 bg-slate-950/60 p-4 text-sm text-slate-400">
          <p>
            <span className="text-slate-300">Email:</span> {user?.email}
          </p>
        </div>

        <form onSubmit={handleCallSubmit} className="space-y-4">
          <div>
            <label htmlFor="phone" className="mb-1.5 block text-sm text-slate-400">
              Phone number
            </label>
            <input
              id="phone"
              type="tel"
              className="input"
              placeholder="+919876543210"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              required
            />
          </div>
          <div>
            <label htmlFor="customer" className="mb-1.5 block text-sm text-slate-400">
              Customer name
            </label>
            <input
              id="customer"
              type="text"
              className="input"
              value={customerName}
              onChange={(e) => setCustomerName(e.target.value)}
              required
            />
          </div>
          {callError && <p className="text-sm text-rose-400">{callError}</p>}
          {callSuccess && <p className="text-sm text-emerald-400">{callSuccess}</p>}
          <button type="submit" className="btn-primary" disabled={placingCall}>
            {placingCall ? "Placing call..." : "Place outbound call"}
          </button>
        </form>

        <button type="button" onClick={handleLogout} className="btn-ghost mt-4">
          Sign out
        </button>
      </AuthCard>
    </div>
  );
}
