"use client";

import { useState } from "react";
import toast from "react-hot-toast";
import { motion } from "framer-motion";
import { PageWrapper, Button } from "@/themes";

function TenantsSVG() {
  return (
    <svg
      width="140"
      height="140"
      viewBox="0 0 140 140"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      {/* Building outline */}
      <rect
        x="30"
        y="40"
        width="80"
        height="80"
        rx="3"
        stroke="currentColor"
        strokeWidth="2"
      />
      {/* Roof */}
      <path
        d="M22 40L70 12L118 40"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      {/* Door */}
      <rect
        x="56"
        y="98"
        width="28"
        height="22"
        rx="2"
        stroke="currentColor"
        strokeWidth="1.8"
      />
      <circle cx="79" cy="109" r="2" fill="currentColor" opacity="0.4" />
      {/* Windows row 1 */}
      <rect
        x="38"
        y="52"
        width="18"
        height="14"
        rx="1.5"
        stroke="currentColor"
        strokeWidth="1.5"
      />
      <rect
        x="84"
        y="52"
        width="18"
        height="14"
        rx="1.5"
        stroke="currentColor"
        strokeWidth="1.5"
      />
      {/* Windows row 2 */}
      <rect
        x="38"
        y="74"
        width="18"
        height="14"
        rx="1.5"
        stroke="currentColor"
        strokeWidth="1.5"
      />
      <rect
        x="84"
        y="74"
        width="18"
        height="14"
        rx="1.5"
        stroke="currentColor"
        strokeWidth="1.5"
      />
      {/* People icons */}
      {/* Person 1 */}
      <circle cx="22" cy="108" r="7" stroke="currentColor" strokeWidth="1.5" />
      <path
        d="M12 128c0-5.5 4.5-10 10-10s10 4.5 10 10"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
      />
      {/* Person 2 */}
      <circle cx="118" cy="108" r="7" stroke="currentColor" strokeWidth="1.5" />
      <path
        d="M108 128c0-5.5 4.5-10 10-10s10 4.5 10 10"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
      />
      {/* Key icon */}
      <circle cx="70" cy="74" r="6" stroke="currentColor" strokeWidth="1.5" />
      <line
        x1="76"
        y1="78"
        x2="84"
        y2="86"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
      />
      <line
        x1="81"
        y1="86"
        x2="81"
        y2="90"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
      />
      <line
        x1="84"
        y1="86"
        x2="84"
        y2="90"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
      />
    </svg>
  );
}

const FEATURES = [
  "Tenant onboarding & digital lease signing",
  "Rent collection and payment tracking",
  "Maintenance request portal for tenants",
  "Communication history and messaging",
  "Compliance document management",
];

export default function TenantsPage() {
  const [notified, setNotified] = useState(false);

  function handleNotify() {
    setNotified(true);
    toast.success(
      "You're on the waitlist! We'll notify you when Tenants launches.",
    );
  }

  return (
    <PageWrapper>
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
        className="p-6 md:p-8 max-w-7xl mx-auto"
      >
        <div className="mb-8">
          <h1 className="font-display italic text-2xl text-text">Tenants</h1>
          <p className="font-body font-light text-sm text-text-3 mt-1">
            Manage tenant relationships and communications
          </p>
        </div>

        <div className="flex flex-col items-center justify-center py-12 max-w-md mx-auto text-center">
          <div className="text-border mb-8">
            <TenantsSVG />
          </div>

          <span className="font-mono text-xs bg-amber-bg text-amber border border-amber/20 px-3 py-1 rounded-full mb-4">
            Coming Soon
          </span>

          <h2 className="font-display italic text-2xl text-text mb-3">
            Tenant Management
          </h2>
          <p className="font-body font-light text-sm text-text-2 leading-relaxed mb-8">
            A complete tenant lifecycle platform — from onboarding to move-out —
            built directly into your property management workflow.
          </p>

          <ul className="space-y-2.5 text-left w-full mb-8">
            {FEATURES.map((f) => (
              <li
                key={f}
                className="flex items-center gap-2.5 font-body font-light text-sm text-text-2"
              >
                <span className="w-1.5 h-1.5 rounded-full bg-graphite flex-shrink-0" />
                {f}
              </li>
            ))}
          </ul>

          <Button
            onClick={handleNotify}
            disabled={notified}
            variant={notified ? "secondary" : "primary"}
          >
            {notified ? "You're on the waitlist" : "Notify me when it launches"}
          </Button>
        </div>
      </motion.div>
    </PageWrapper>
  );
}
