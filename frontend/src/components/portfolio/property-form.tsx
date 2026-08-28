"use client";

import { useState } from "react";
import { X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/cn";

interface PropertyFormProps {
  mode: "create" | "edit";
  initialData?: {
    id: string;
    name: string;
    address: string;
    type: string;
    units: number;
  } | null;
  onClose: () => void;
  onSubmit: (data: {
    name: string;
    address: string;
    type: string;
    units: number;
  }) => Promise<void>;
}

const PROPERTY_TYPES = [
  "MIXED_USE",
  "SHORT_TERM_RENTAL",
  "LONG_TERM_RENTAL",
  "OWNER_OCCUPIED",
  "COMMERCIAL",
];

export function PropertyForm({
  mode,
  initialData,
  onClose,
  onSubmit,
}: PropertyFormProps) {
  const [formData, setFormData] = useState({
    name: initialData?.name || "",
    address: initialData?.address || "",
    type: initialData?.type || "MIXED_USE",
    units: initialData?.units || 1,
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const validate = () => {
    const newErrors: Record<string, string> = {};
    if (!formData.name.trim()) newErrors.name = "Property name is required";
    if (!formData.address.trim()) newErrors.address = "Address is required";
    if (formData.units < 1) newErrors.units = "Must have at least 1 unit";
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;

    setIsSubmitting(true);
    try {
      await onSubmit(formData);
      onClose();
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-surface rounded-panel p-6 w-full max-w-md shadow-lg">
        <div className="flex items-center justify-between mb-5">
          <h2 className="text-[20px] font-serif text-text m-0">
            {mode === "create" ? "Add Property" : "Edit Property"}
          </h2>
          <button
            onClick={onClose}
            className="p-1 hover:bg-surface-2 rounded transition-colors"
          >
            <X size={18} className="text-text-2" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          {/* Property Name */}
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
              className={cn(
                "w-full px-3 py-2.5 border rounded-[8px] bg-bg text-text text-[13px]",
                "focus:outline-none focus:border-graphite transition-colors",
                errors.name ? "border-red" : "border-border",
              )}
              placeholder="e.g., Maple Court"
            />
            {errors.name && (
              <p className="text-[11px] text-red mt-1">{errors.name}</p>
            )}
          </div>

          {/* Address */}
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
              className={cn(
                "w-full px-3 py-2.5 border rounded-[8px] bg-bg text-text text-[13px]",
                "focus:outline-none focus:border-graphite transition-colors",
                errors.address ? "border-red" : "border-border",
              )}
              placeholder="123 Main St, City, State"
            />
            {errors.address && (
              <p className="text-[11px] text-red mt-1">{errors.address}</p>
            )}
          </div>

          {/* Type */}
          <div>
            <label className="block text-[12px] font-semibold text-text-2 uppercase tracking-[0.08em] mb-1.5">
              Property Type
            </label>
            <select
              value={formData.type}
              onChange={(e) =>
                setFormData({ ...formData, type: e.target.value })
              }
              className="w-full px-3 py-2.5 border border-border rounded-[8px] bg-bg text-text text-[13px] focus:outline-none focus:border-graphite transition-colors"
            >
              {PROPERTY_TYPES.map((t) => (
                <option key={t} value={t}>
                  {t.replace(/_/g, " ")}
                </option>
              ))}
            </select>
          </div>

          {/* Units */}
          <div>
            <label className="block text-[12px] font-semibold text-text-2 uppercase tracking-[0.08em] mb-1.5">
              Units
            </label>
            <input
              type="number"
              min="1"
              value={formData.units}
              onChange={(e) =>
                setFormData({ ...formData, units: parseInt(e.target.value) })
              }
              className={cn(
                "w-full px-3 py-2.5 border rounded-[8px] bg-bg text-text text-[13px]",
                "focus:outline-none focus:border-graphite transition-colors",
                errors.units ? "border-red" : "border-border",
              )}
            />
            {errors.units && (
              <p className="text-[11px] text-red mt-1">{errors.units}</p>
            )}
          </div>

          {/* Actions */}
          <div className="flex gap-2 mt-4">
            <Button
              variant="secondary"
              onClick={onClose}
              disabled={isSubmitting}
            >
              Cancel
            </Button>
            <Button variant="primary" type="submit" disabled={isSubmitting}>
              {isSubmitting
                ? "Saving..."
                : mode === "create"
                  ? "Create Property"
                  : "Save Changes"}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
