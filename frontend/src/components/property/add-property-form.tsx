"use client";

import { useState } from "react";
import { X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/cn";

interface AddPropertyFormProps {
  onClose: () => void;
  onSubmit: (data: {
    name: string;
    address: string;
    property_type: string;
    units: number;
    timezone: string;
  }) => void;
}

const PROPERTY_TYPES = [
  "MIXED_USE",
  "SHORT_TERM_RENTAL",
  "LONG_TERM_RENTAL",
  "OWNER_OCCUPIED",
  "COMMERCIAL",
];

const TIMEZONES = [
  "UTC",
  "America/New_York",
  "America/Chicago",
  "America/Denver",
  "America/Los_Angeles",
  "Europe/London",
  "Europe/Paris",
];

export function AddPropertyForm({ onClose, onSubmit }: AddPropertyFormProps) {
  const [formData, setFormData] = useState({
    name: "",
    address: "",
    property_type: "MIXED_USE",
    units: 1,
    timezone: "UTC",
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  const validate = () => {
    const newErrors: Record<string, string> = {};
    if (!formData.name.trim()) newErrors.name = "Property name is required";
    if (!formData.address.trim()) newErrors.address = "Address is required";
    if (formData.units < 1) newErrors.units = "Units must be at least 1";
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (validate()) {
      onSubmit(formData);
      setFormData({
        name: "",
        address: "",
        property_type: "MIXED_USE",
        units: 1,
        timezone: "UTC",
      });
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-surface rounded-panel p-6 w-full max-w-md shadow-lg">
        <div className="flex items-center justify-between mb-5">
          <h2 className="text-[20px] font-serif text-text m-0">Add Property</h2>
          <button
            onClick={onClose}
            className="p-1 hover:bg-surface-2 rounded transition-colors"
          >
            <X size={18} className="text-text-2" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <div>
            <label className="block text-[12px] font-semibold text-text-2 uppercase tracking-[0.08em] mb-1.5">
              Property Name
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) =>
                setFormData({ ...formData, name: e.target.value })
              }
              placeholder="e.g., Maple Court Building"
              className={cn(
                "w-full px-3 py-2.5 rounded-[8px] border bg-bg text-text text-[14px]",
                "placeholder:text-text-3 transition-colors",
                errors.name ? "border-red" : "border-border focus:border-text",
              )}
            />
            {errors.name && (
              <p className="text-[12px] text-red mt-1">{errors.name}</p>
            )}
          </div>

          <div>
            <label className="block text-[12px] font-semibold text-text-2 uppercase tracking-[0.08em] mb-1.5">
              Address
            </label>
            <input
              type="text"
              value={formData.address}
              onChange={(e) =>
                setFormData({ ...formData, address: e.target.value })
              }
              placeholder="e.g., 123 Oak Street, San Francisco, CA"
              className={cn(
                "w-full px-3 py-2.5 rounded-[8px] border bg-bg text-text text-[14px]",
                "placeholder:text-text-3 transition-colors",
                errors.address
                  ? "border-red"
                  : "border-border focus:border-text",
              )}
            />
            {errors.address && (
              <p className="text-[12px] text-red mt-1">{errors.address}</p>
            )}
          </div>

          <div>
            <label className="block text-[12px] font-semibold text-text-2 uppercase tracking-[0.08em] mb-1.5">
              Property Type
            </label>
            <select
              value={formData.property_type}
              onChange={(e) =>
                setFormData({ ...formData, property_type: e.target.value })
              }
              className="w-full px-3 py-2.5 rounded-[8px] border border-border bg-bg text-text text-[14px]"
            >
              {PROPERTY_TYPES.map((type) => (
                <option key={type} value={type}>
                  {type.replace(/_/g, " ")}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-[12px] font-semibold text-text-2 uppercase tracking-[0.08em] mb-1.5">
              Units
            </label>
            <input
              type="number"
              min="1"
              value={formData.units}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  units: parseInt(e.target.value) || 1,
                })
              }
              className={cn(
                "w-full px-3 py-2.5 rounded-[8px] border bg-bg text-text text-[14px]",
                errors.units ? "border-red" : "border-border focus:border-text",
              )}
            />
            {errors.units && (
              <p className="text-[12px] text-red mt-1">{errors.units}</p>
            )}
          </div>

          <div>
            <label className="block text-[12px] font-semibold text-text-2 uppercase tracking-[0.08em] mb-1.5">
              Timezone
            </label>
            <select
              value={formData.timezone}
              onChange={(e) =>
                setFormData({ ...formData, timezone: e.target.value })
              }
              className="w-full px-3 py-2.5 rounded-[8px] border border-border bg-bg text-text text-[14px]"
            >
              {TIMEZONES.map((tz) => (
                <option key={tz} value={tz}>
                  {tz}
                </option>
              ))}
            </select>
          </div>

          <div className="flex gap-3 mt-2 justify-between">
            <Button type="button" variant="secondary" onClick={onClose}>
              Cancel
            </Button>
            <Button type="submit" variant="primary">
              Add Property
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
