"use client";

import { useState, useCallback, useEffect } from "react";

const DEMO_MODE_KEY = "nestra_demo_mode";

/**
 * Global demo mode state
 * - demoMode = false (default): Fresh app with NO mock data
 * - demoMode = true: Show all fixture data for testing UI
 */
export function useDemoMode() {
  const [demoMode, setDemoMode] = useState(false);
  const [isHydrated, setIsHydrated] = useState(false);

  useEffect(() => {
    // Load from localStorage, default to false (fresh/clean state)
    const stored = localStorage.getItem(DEMO_MODE_KEY);
    setDemoMode(stored === "true");
    setIsHydrated(true);
  }, []);

  const toggleDemoMode = useCallback(
    (value?: boolean) => {
      const actualValue =
        value !== undefined ? value : (prev: boolean) => !prev;
      const newValue =
        typeof actualValue === "function" ? !demoMode : actualValue;
      setDemoMode(newValue);
      localStorage.setItem(DEMO_MODE_KEY, String(newValue));
    },
    [demoMode],
  );

  return { demoMode, isHydrated, toggleDemoMode };
}
