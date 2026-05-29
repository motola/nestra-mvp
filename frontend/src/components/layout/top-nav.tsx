import { Bell, Building, ChevronRight, Search } from "lucide-react";

export function TopNav() {
  return (
    <header className="h-14 bg-surface border-b border-border flex items-center px-5 gap-5 shrink-0 z-20">
      {/* Wordmark */}
      <div className="flex items-center gap-2.5">
        <div className="w-7 h-7 rounded-[7px] bg-graphite flex items-center justify-center relative shrink-0">
          <span className="font-serif text-[19px] text-[#fbf9f4] leading-none select-none">
            A
          </span>
          <span className="absolute top-[3px] right-[3px] w-[5px] h-[5px] rounded-full bg-green" />
        </div>
        <span className="font-serif text-[22px] tracking-[-0.01em] text-text">
          Alphacon
        </span>
      </div>

      {/* Org switcher */}
      <div className="ml-2 px-2.5 py-1 rounded-[9px] flex items-center gap-2 bg-bg border border-border cursor-pointer">
        <Building
          size={13}
          strokeWidth={1.5}
          className="text-text-3 shrink-0"
        />
        <span className="text-[12px] text-text-2 font-medium">
          Chen Property Holdings
        </span>
        <ChevronRight size={12} strokeWidth={1.5} className="text-text-3" />
      </div>

      {/* Search */}
      <div className="ml-2 flex-1 max-w-[360px] min-w-0 bg-bg border border-border rounded-[9px] px-3 py-1.5 flex items-center gap-2 cursor-text overflow-hidden">
        <Search size={14} strokeWidth={1.5} className="text-text-3 shrink-0" />
        <span className="text-[12px] text-text-3 truncate flex-1 select-none">
          Search properties, devices, stays…
        </span>
        <kbd className="shrink-0 font-mono text-[10px] text-text-3 border border-border px-[5px] py-[1px] rounded">
          ⌘ K
        </kbd>
      </div>

      {/* Bell + account */}
      <div className="ml-auto flex items-center gap-3.5">
        <button className="bg-transparent border-0 cursor-pointer p-1.5 relative">
          <Bell size={18} strokeWidth={1.5} className="text-text-2" />
          <span className="absolute top-1 right-1 w-[7px] h-[7px] rounded-full bg-amber" />
        </button>
        <div className="flex items-center gap-2 pl-[3px] pr-2 py-[3px] rounded-tag border border-border cursor-pointer">
          <div className="w-[26px] h-[26px] rounded-full bg-graphite text-[#fbf9f4] flex items-center justify-center font-mono text-[10px] font-medium tracking-[0.5px]">
            MC
          </div>
          <span className="text-[12px] text-text-2 pr-1">Marcus</span>
        </div>
      </div>
    </header>
  );
}
