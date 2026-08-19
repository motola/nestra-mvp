"use client";

import {
  createContext,
  useContext,
  useState,
  useCallback,
  ReactNode,
} from "react";
import type { Property } from "@/lib/fixtures";

interface PropertyContextValue {
  selectedProperty: Property | null;
  selectProperty: (property: Property) => void;
}

const PropertyContext = createContext<PropertyContextValue | null>(null);

export function PropertyProvider({ children }: { children: ReactNode }) {
  const [selectedProperty, setSelectedProperty] = useState<Property | null>(
    null,
  );

  const selectProperty = useCallback((property: Property) => {
    setSelectedProperty(property);
  }, []);

  return (
    <PropertyContext.Provider
      value={{
        selectedProperty,
        selectProperty,
      }}
    >
      {children}
    </PropertyContext.Provider>
  );
}

export function useProperty(): PropertyContextValue {
  const ctx = useContext(PropertyContext);
  if (!ctx) throw new Error("useProperty must be used inside PropertyProvider");
  return ctx;
}
