type BuildingType = "house" | "flat" | "apartment";

function detectType(name: string): BuildingType {
  const n = name.toLowerCase();
  if (/lodge|cottage/.test(n)) return "house";
  if (/\bhouse\b/.test(n) && !/court/.test(n)) return "house";
  if (/flat|annexe/.test(n)) return "flat";
  if (/court|hmo|block/.test(n)) return "apartment";
  if (/riverside|grove|manor/.test(n)) return "house";
  return "apartment";
}

function HouseSVG() {
  return (
    <svg width="80" height="60" viewBox="0 0 80 60" fill="none" xmlns="http://www.w3.org/2000/svg">
      {/* Roof */}
      <path d="M10 30L40 6L70 30" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
      {/* Chimney */}
      <rect x="52" y="10" width="7" height="14" rx="1" stroke="currentColor" strokeWidth="1.5"/>
      {/* Body */}
      <rect x="14" y="29" width="52" height="26" rx="1" stroke="currentColor" strokeWidth="1.5"/>
      {/* Door */}
      <rect x="33" y="43" width="14" height="12" rx="1" stroke="currentColor" strokeWidth="1.2"/>
      {/* Door handle */}
      <circle cx="43.5" cy="49.5" r="1" fill="currentColor" opacity="0.5"/>
      {/* Windows */}
      <rect x="19" y="36" width="11" height="9" rx="1" stroke="currentColor" strokeWidth="1.2"/>
      <rect x="50" y="36" width="11" height="9" rx="1" stroke="currentColor" strokeWidth="1.2"/>
      {/* Window cross */}
      <line x1="24.5" y1="36" x2="24.5" y2="45" stroke="currentColor" strokeWidth="0.8" opacity="0.5"/>
      <line x1="19" y1="40.5" x2="30" y2="40.5" stroke="currentColor" strokeWidth="0.8" opacity="0.5"/>
      <line x1="55.5" y1="36" x2="55.5" y2="45" stroke="currentColor" strokeWidth="0.8" opacity="0.5"/>
      <line x1="50" y1="40.5" x2="61" y2="40.5" stroke="currentColor" strokeWidth="0.8" opacity="0.5"/>
    </svg>
  );
}

function FlatSVG() {
  return (
    <svg width="80" height="60" viewBox="0 0 80 60" fill="none" xmlns="http://www.w3.org/2000/svg">
      {/* Main building */}
      <rect x="20" y="8" width="40" height="47" rx="1.5" stroke="currentColor" strokeWidth="1.5"/>
      {/* Row 1 windows */}
      <rect x="26" y="14" width="10" height="8" rx="1" stroke="currentColor" strokeWidth="1.2"/>
      <rect x="44" y="14" width="10" height="8" rx="1" stroke="currentColor" strokeWidth="1.2"/>
      {/* Row 2 windows */}
      <rect x="26" y="26" width="10" height="8" rx="1" stroke="currentColor" strokeWidth="1.2"/>
      <rect x="44" y="26" width="10" height="8" rx="1" stroke="currentColor" strokeWidth="1.2"/>
      {/* Row 3 windows */}
      <rect x="26" y="38" width="10" height="8" rx="1" stroke="currentColor" strokeWidth="1.2"/>
      <rect x="44" y="38" width="10" height="8" rx="1" stroke="currentColor" strokeWidth="1.2"/>
      {/* Door */}
      <rect x="32" y="47" width="16" height="8" rx="1" stroke="currentColor" strokeWidth="1.2"/>
      {/* Steps */}
      <line x1="16" y1="55" x2="64" y2="55" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round"/>
    </svg>
  );
}

function ApartmentSVG() {
  return (
    <svg width="80" height="60" viewBox="0 0 80 60" fill="none" xmlns="http://www.w3.org/2000/svg">
      {/* Main block */}
      <rect x="16" y="16" width="48" height="39" rx="1.5" stroke="currentColor" strokeWidth="1.5"/>
      {/* Wing left */}
      <rect x="8" y="28" width="14" height="27" rx="1" stroke="currentColor" strokeWidth="1.2"/>
      {/* Wing right */}
      <rect x="58" y="28" width="14" height="27" rx="1" stroke="currentColor" strokeWidth="1.2"/>
      {/* Main windows row 1 */}
      <rect x="22" y="22" width="9" height="7" rx="1" stroke="currentColor" strokeWidth="1.1"/>
      <rect x="36" y="22" width="9" height="7" rx="1" stroke="currentColor" strokeWidth="1.1"/>
      <rect x="50" y="22" width="9" height="7" rx="1" stroke="currentColor" strokeWidth="1.1"/>
      {/* Main windows row 2 */}
      <rect x="22" y="33" width="9" height="7" rx="1" stroke="currentColor" strokeWidth="1.1"/>
      <rect x="36" y="33" width="9" height="7" rx="1" stroke="currentColor" strokeWidth="1.1"/>
      <rect x="50" y="33" width="9" height="7" rx="1" stroke="currentColor" strokeWidth="1.1"/>
      {/* Door */}
      <rect x="32" y="47" width="17" height="8" rx="1" stroke="currentColor" strokeWidth="1.2"/>
      {/* Ground line */}
      <line x1="4" y1="55" x2="76" y2="55" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round"/>
    </svg>
  );
}

export function PropertyIllustration({ name, className }: { name: string; className?: string }) {
  const type = detectType(name);
  return (
    <span className={className}>
      {type === "house" && <HouseSVG />}
      {type === "flat" && <FlatSVG />}
      {type === "apartment" && <ApartmentSVG />}
    </span>
  );
}
