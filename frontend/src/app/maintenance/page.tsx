"use client";

import { useState } from "react";
import toast from "react-hot-toast";
import { motion } from "framer-motion";
import { PageWrapper, Button } from "@/themes";

function MaintenanceSVG() {
  return (
    <svg width="140" height="140" viewBox="0 0 140 140" fill="none" xmlns="http://www.w3.org/2000/svg">
      {/* Clipboard */}
      <rect x="28" y="28" width="84" height="96" rx="4" stroke="currentColor" strokeWidth="2"/>
      {/* Clipboard top clip */}
      <rect x="52" y="20" width="36" height="18" rx="4" stroke="currentColor" strokeWidth="1.8"/>
      {/* Checklist items */}
      <rect x="40" y="52" width="12" height="12" rx="2" stroke="currentColor" strokeWidth="1.5"/>
      <line x1="43" y1="58" x2="45.5" y2="61" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
      <line x1="45.5" y1="61" x2="50" y2="55" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
      <line x1="60" y1="58" x2="92" y2="58" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>

      <rect x="40" y="72" width="12" height="12" rx="2" stroke="currentColor" strokeWidth="1.5"/>
      <line x1="43" y1="78" x2="45.5" y2="81" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
      <line x1="45.5" y1="81" x2="50" y2="75" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
      <line x1="60" y1="78" x2="92" y2="78" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>

      <rect x="40" y="92" width="12" height="12" rx="2" stroke="currentColor" strokeWidth="1.5"/>
      <line x1="60" y1="98" x2="85" y2="98" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeDasharray="2 2"/>

      {/* Wrench icon (overlaid bottom right) */}
      <circle cx="102" cy="110" r="20" fill="currentColor" fillOpacity="0.06" stroke="currentColor" strokeWidth="1.5"/>
      <path
        d="M96 116c-3.3-3.3-3.3-8.7 0-12 2.4-2.4 5.8-3.1 8.8-2l-4.1 4.1 2.8 2.8 4.1-4.1c1.1 3-0.4 6.4-2.8 8.8-3.3 3.3-8.7 3.3-12 0l-4 4-2-2 4-4z"
        stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"
      />
    </svg>
  );
}

const FEATURES = [
  "Work order creation and contractor dispatch",
  "AI-powered predictive maintenance from sensor data",
  "Scheduled maintenance calendar and reminders",
  "Photo documentation and completion sign-off",
  "Cost tracking and vendor management",
];

export default function MaintenancePage() {
  const [notified, setNotified] = useState(false);

  function handleNotify() {
    setNotified(true);
    toast.success("You're on the waitlist! We'll notify you when Maintenance launches.");
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
          <h1 className="font-display italic text-2xl text-text">Maintenance</h1>
          <p className="font-body font-light text-sm text-text-3 mt-1">Track and schedule property maintenance tasks</p>
        </div>

        <div className="flex flex-col items-center justify-center py-12 max-w-md mx-auto text-center">
          <div className="text-border mb-8">
            <MaintenanceSVG />
          </div>

          <span className="font-mono text-xs bg-amber-bg text-amber border border-amber/20 px-3 py-1 rounded-full mb-4">
            Coming Soon
          </span>

          <h2 className="font-display italic text-2xl text-text mb-3">
            Maintenance Tracking
          </h2>
          <p className="font-body font-light text-sm text-text-2 leading-relaxed mb-8">
            Smart maintenance management that uses your IoT sensor data to predict failures before they happen — saving you emergency callout costs.
          </p>

          <ul className="space-y-2.5 text-left w-full mb-8">
            {FEATURES.map((f) => (
              <li key={f} className="flex items-center gap-2.5 font-body font-light text-sm text-text-2">
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
