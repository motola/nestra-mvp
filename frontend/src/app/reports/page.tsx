"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { BarChart2, Bell, Building2, Download, X } from "lucide-react";
import toast from "react-hot-toast";
import { PageWrapper, Button } from "@/themes";
import { cn } from "@/lib/utils";

interface ReportType {
  id: string;
  icon: React.ElementType;
  title: string;
  description: string;
  formats: string[];
}

const REPORT_TYPES: ReportType[] = [
  {
    id: "alerts",
    icon: Bell,
    title: "Alert Summary",
    description:
      "Summary of all alerts over the selected period — critical incidents, response times, and recurring issues by device.",
    formats: ["PDF", "CSV"],
  },
  {
    id: "portfolio",
    icon: Building2,
    title: "Portfolio Overview",
    description:
      "High-level overview of all properties: occupancy, device health, and outstanding maintenance items.",
    formats: ["PDF"],
  },
  {
    id: "analytics",
    icon: BarChart2,
    title: "Analytics Export",
    description:
      "Raw sensor data export for all devices across the selected date range. Suitable for import into BI tools.",
    formats: ["CSV", "XLSX", "JSON"],
  },
];

function GenerateDialog({
  report,
  onClose,
}: {
  report: ReportType;
  onClose: () => void;
}) {
  const [period, setPeriod] = useState("last_30");
  const [format, setFormat] = useState(report.formats[0]);
  const [generating, setGenerating] = useState(false);

  function generate() {
    setGenerating(true);
    setTimeout(() => {
      setGenerating(false);
      onClose();
      toast.success(`${report.title} generated — download starting`);
    }, 2000);
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="absolute inset-0 bg-graphite/30 backdrop-blur-sm"
        onClick={onClose}
      />
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.95 }}
        transition={{ duration: 0.15 }}
        className="relative w-full max-w-md bg-surface border border-border rounded-2xl overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between px-5 py-4 border-b border-border">
          <p className="font-body font-normal text-sm text-text">
            Generate {report.title}
          </p>
          <button
            onClick={onClose}
            className="text-text-3 hover:text-text-2 transition-colors"
          >
            <X size={14} />
          </button>
        </div>

        <div className="px-5 py-5 space-y-5">
          {/* Period */}
          <div>
            <p className="font-body font-normal text-xs uppercase tracking-widest text-text-3 mb-2">
              Period
            </p>
            <div className="grid grid-cols-2 gap-2">
              {[
                { value: "last_7", label: "Last 7 days" },
                { value: "last_30", label: "Last 30 days" },
                { value: "last_90", label: "Last 90 days" },
                { value: "last_year", label: "Last year" },
              ].map((p) => (
                <button
                  key={p.value}
                  onClick={() => setPeriod(p.value)}
                  className={cn(
                    "px-3 py-2 rounded-lg text-xs font-body font-light border transition-colors text-left",
                    period === p.value
                      ? "bg-graphite text-surface border-graphite"
                      : "bg-surface-2 border-border text-text-2 hover:border-border-strong",
                  )}
                >
                  {p.label}
                </button>
              ))}
            </div>
          </div>

          {/* Format */}
          <div>
            <p className="font-body font-normal text-xs uppercase tracking-widest text-text-3 mb-2">
              Format
            </p>
            <div className="flex items-center gap-2">
              {report.formats.map((f) => (
                <button
                  key={f}
                  onClick={() => setFormat(f)}
                  className={cn(
                    "px-3 py-1.5 rounded-lg text-xs font-mono border transition-colors",
                    format === f
                      ? "bg-graphite text-surface border-graphite"
                      : "bg-surface-2 border-border text-text-2 hover:border-border-strong",
                  )}
                >
                  {f}
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="px-5 py-4 border-t border-border flex items-center justify-end gap-3">
          <button
            onClick={onClose}
            className="font-body font-light text-sm text-text-3 hover:text-text-2 transition-colors"
          >
            Cancel
          </button>
          <Button onClick={generate} disabled={generating}>
            {generating ? (
              <span className="flex items-center gap-2">
                <span className="w-3 h-3 border border-surface/40 border-t-surface rounded-full animate-spin" />
                Generating…
              </span>
            ) : (
              <span className="flex items-center gap-2">
                <Download size={13} />
                Generate {format}
              </span>
            )}
          </Button>
        </div>
      </motion.div>
    </div>
  );
}

export default function ReportsPage() {
  const [activeReport, setActiveReport] = useState<ReportType | null>(null);

  return (
    <PageWrapper>
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
        className="p-6 md:p-8 max-w-7xl mx-auto"
      >
        <div className="mb-8">
          <h1 className="font-display italic text-2xl text-text">Reports</h1>
          <p className="font-body font-light text-sm text-text-3 mt-1">
            Generate and download reports for your portfolio
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {REPORT_TYPES.map((report) => {
            const Icon = report.icon;
            return (
              <div
                key={report.id}
                className="bg-surface border border-border rounded-xl p-5 hover:border-border-strong transition-colors"
              >
                <div className="flex items-start gap-3 mb-3">
                  <div className="w-8 h-8 bg-surface-2 border border-border rounded-lg flex items-center justify-center flex-shrink-0">
                    <Icon size={14} className="text-text-2" />
                  </div>
                  <div>
                    <p className="font-body font-normal text-sm text-text">
                      {report.title}
                    </p>
                    <div className="flex items-center gap-1.5 mt-1">
                      {report.formats.map((f) => (
                        <span
                          key={f}
                          className="font-mono text-[10px] text-text-3 bg-surface-2 border border-border px-1.5 py-0.5 rounded-full"
                        >
                          {f}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
                <p className="font-body font-light text-sm text-text-3 leading-relaxed mb-4">
                  {report.description}
                </p>
                <button
                  onClick={() => setActiveReport(report)}
                  className="flex items-center gap-1.5 font-body font-light text-xs text-text-2 hover:text-text transition-colors"
                >
                  <Download size={12} />
                  Generate report
                </button>
              </div>
            );
          })}
        </div>
      </motion.div>

      <AnimatePresence>
        {activeReport && (
          <GenerateDialog
            report={activeReport}
            onClose={() => setActiveReport(null)}
          />
        )}
      </AnimatePresence>
    </PageWrapper>
  );
}
