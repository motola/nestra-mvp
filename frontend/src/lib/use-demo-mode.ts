"use client";

import { useState, useCallback, useEffect } from "react";

const DEMO_MODE_KEY = "nestra_demo_mode";

export function useDemoMode() {
  const [demoMode, setDemoMode] = useState(false);
  const [isHydrated, setIsHydrated] = useState(false);

  useEffect(() => {
    // Load demo mode from localStorage
    const stored = localStorage.getItem(DEMO_MODE_KEY);
    setDemoMode(stored === "true");
    setIsHydrated(true);
  }, []);

  const toggleDemoMode = useCallback(
    (value?: boolean) => {
      const newValue = value !== undefined ? value : (current) => !current;
      const actualValue = typeof newValue === "function" ? !demoMode : newValue;
      setDemoMode(actualValue);
      localStorage.setItem(DEMO_MODE_KEY, String(actualValue));
    },
    [demoMode],
  );

  return { demoMode, isHydrated, toggleDemoMode };
}
