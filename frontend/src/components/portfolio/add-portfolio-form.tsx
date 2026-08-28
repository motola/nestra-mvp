"use client";

import { useState } from "react";
import { X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/cn";

interface AddPortfolioFormProps {
  onClose: () => void;
  onSubmit: (data: { name: string; region: string; manager: string }) => void;
}

export function AddPortfolioForm({ onClose, onSubmit }: AddPortfolioFormProps) {
  const [formData, setFormData] = useState({
    name: "",
    region: "",
    manager: "",
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  const validate = () => {
    const newErrors: Record<string, string> = {};
    if (!formData.name.trim()) newErrors.name = "Portfolio name is required";
    if (!formData.region.trim()) newErrors.region = "Region is required";
    if (!formData.manager.trim())
      newErrors.manager = "Manager name is required";
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (validate()) {
      onSubmit(formData);
      setFormData({ name: "", region: "", manager: "" });
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-surface rounded-panel p-6 w-full max-w-md shadow-lg">
        <div className="flex items-center justify-between mb-5">
          <h2 className="text-[20px] font-serif text-text m-0">
            Add Portfolio
          </h2>
          <button
            onClick={onClose}
            className="p-1 hover:bg-surface-2 rounded transition-colors"
          >
            <X size={18} className="text-text-2" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          {/* Portfolio Name */}
          <div>
            <label className="block text-[12px] font-semibold text-text-2 uppercase tracking-[0.08em] mb-1.5">
              Portfolio Name
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) =>
                setFormData({ ...formData, name: e.target.value })
              }
              placeholder="e.g., Northern California Properties"
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

          {/* Region */}
          <div>
            <label className="block text-[12px] font-semibold text-text-2 uppercase tracking-[0.08em] mb-1.5">
              Region
            </label>
            <input
              type="text"
              value={formData.region}
              onChange={(e) =>
                setFormData({ ...formData, region: e.target.value })
              }
              placeholder="e.g., Pacific Northwest"
              className={cn(
                "w-full px-3 py-2.5 rounded-[8px] border bg-bg text-text text-[14px]",
                "placeholder:text-text-3 transition-colors",
                errors.region
                  ? "border-red"
                  : "border-border focus:border-text",
              )}
            />
            {errors.region && (
              <p className="text-[12px] text-red mt-1">{errors.region}</p>
            )}
          </div>

          {/* Manager */}
          <div>
            <label className="block text-[12px] font-semibold text-text-2 uppercase tracking-[0.08em] mb-1.5">
              Portfolio Manager
            </label>
            <input
              type="text"
              value={formData.manager}
              onChange={(e) =>
                setFormData({ ...formData, manager: e.target.value })
              }
              placeholder="e.g., Jane Smith"
              className={cn(
                "w-full px-3 py-2.5 rounded-[8px] border bg-bg text-text text-[14px]",
                "placeholder:text-text-3 transition-colors",
                errors.manager
                  ? "border-red"
                  : "border-border focus:border-text",
              )}
            />
            {errors.manager && (
              <p className="text-[12px] text-red mt-1">{errors.manager}</p>
            )}
          </div>

          {/* Actions */}
          <div className="flex gap-3 mt-2 justify-between">
            <Button type="button" variant="secondary" onClick={onClose}>
              Cancel
            </Button>
            <Button type="submit" variant="primary">
              Add Portfolio
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
