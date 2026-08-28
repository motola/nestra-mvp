"use client";

import { useState } from "react";
import { X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/cn";

interface EditPortfolioFormProps {
  initialName: string;
  initialDescription: string;
  onClose: () => void;
  onSubmit: (data: { name: string; description: string }) => Promise<void>;
}

export function EditPortfolioForm({
  initialName,
  initialDescription,
  onClose,
  onSubmit,
}: EditPortfolioFormProps) {
  const [formData, setFormData] = useState({
    name: initialName,
    description: initialDescription,
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const validate = () => {
    const newErrors: Record<string, string> = {};
    if (!formData.name.trim()) newErrors.name = "Portfolio name is required";
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
            Edit Portfolio
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
              className={cn(
                "w-full px-3 py-2.5 border rounded-[8px] bg-bg text-text text-[13px]",
                "focus:outline-none focus:border-graphite transition-colors",
                errors.name ? "border-red" : "border-border",
              )}
              placeholder="e.g., North Region"
            />
            {errors.name && (
              <p className="text-[11px] text-red mt-1">{errors.name}</p>
            )}
          </div>

          {/* Description */}
          <div>
            <label className="block text-[12px] font-semibold text-text-2 uppercase tracking-[0.08em] mb-1.5">
              Description (optional)
            </label>
            <textarea
              value={formData.description}
              onChange={(e) =>
                setFormData({ ...formData, description: e.target.value })
              }
              className={cn(
                "w-full px-3 py-2.5 border rounded-[8px] bg-bg text-text text-[13px]",
                "focus:outline-none focus:border-graphite transition-colors",
                "min-h-[80px] resize-none",
                errors.description ? "border-red" : "border-border",
              )}
              placeholder="Portfolio details..."
            />
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
              {isSubmitting ? "Saving..." : "Save Changes"}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
