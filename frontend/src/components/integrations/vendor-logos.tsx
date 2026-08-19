// Vendor logo SVGs
export const VENDOR_LOGOS: Record<string, React.ReactNode> = {
  Nest: (
    <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
      <circle cx="50" cy="50" r="48" fill="#0F9D58" />
      <text
        x="50"
        y="60"
        textAnchor="middle"
        fontSize="40"
        fontWeight="bold"
        fill="white"
        fontFamily="Arial"
      >
        ⊕
      </text>
    </svg>
  ),
  Ecobee: (
    <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
      <circle cx="50" cy="50" r="48" fill="#FF6B35" />
      <text
        x="50"
        y="60"
        textAnchor="middle"
        fontSize="35"
        fontWeight="bold"
        fill="white"
        fontFamily="Arial"
      >
        E
      </text>
    </svg>
  ),
  "Philips Hue": (
    <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
      <circle cx="50" cy="50" r="48" fill="#0078D4" />
      <circle cx="50" cy="50" r="28" fill="white" opacity="0.3" />
      <circle cx="50" cy="50" r="18" fill="white" />
    </svg>
  ),
  Hue: (
    <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
      <circle cx="50" cy="50" r="48" fill="#0078D4" />
      <circle cx="50" cy="50" r="28" fill="white" opacity="0.3" />
      <circle cx="50" cy="50" r="18" fill="white" />
    </svg>
  ),
  August: (
    <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
      <rect width="100" height="100" fill="#002D5C" rx="10" />
      <text
        x="50"
        y="60"
        textAnchor="middle"
        fontSize="40"
        fontWeight="bold"
        fill="white"
        fontFamily="Arial"
      >
        A
      </text>
    </svg>
  ),
  Shelly: (
    <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
      <circle cx="50" cy="50" r="48" fill="#0084FF" />
      <rect x="30" y="35" width="40" height="30" fill="white" rx="4" />
      <circle cx="40" cy="50" r="3" fill="#0084FF" />
      <circle cx="60" cy="50" r="3" fill="#0084FF" />
    </svg>
  ),
  SmartThings: (
    <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
      <circle cx="50" cy="50" r="48" fill="#00A8E1" />
      <path d="M 40 40 L 60 40 L 60 60 L 40 60 Z" fill="white" />
      <path d="M 45 45 L 55 45 L 55 55 L 45 55 Z" fill="#00A8E1" />
    </svg>
  ),
  Google: (
    <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
      <circle
        cx="50"
        cy="50"
        r="48"
        fill="white"
        stroke="#ddd"
        strokeWidth="2"
      />
      <text
        x="50"
        y="62"
        textAnchor="middle"
        fontSize="45"
        fontWeight="bold"
        fill="#4285F4"
        fontFamily="Arial"
      >
        G
      </text>
    </svg>
  ),
  Microsoft: (
    <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
      <rect x="20" y="20" width="20" height="20" fill="#F25022" />
      <rect x="60" y="20" width="20" height="20" fill="#7FBA00" />
      <rect x="20" y="60" width="20" height="20" fill="#00A4EF" />
      <rect x="60" y="60" width="20" height="20" fill="#FFB900" />
    </svg>
  ),
  LIFX: (
    <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
      <circle cx="50" cy="50" r="48" fill="#1D1D1D" />
      <circle cx="50" cy="50" r="28" fill="#FFB81C" />
      <circle cx="50" cy="50" r="18" fill="#1D1D1D" />
    </svg>
  ),
  Yale: (
    <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
      <rect width="100" height="100" fill="#C60C30" rx="12" />
      <rect x="25" y="30" width="50" height="40" fill="white" rx="4" />
      <circle cx="50" cy="50" r="8" fill="#C60C30" />
    </svg>
  ),
  Tado: (
    <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
      <circle cx="50" cy="50" r="48" fill="#003DA5" />
      <text
        x="50"
        y="62"
        textAnchor="middle"
        fontSize="40"
        fontWeight="bold"
        fill="white"
        fontFamily="Arial"
      >
        ◉
      </text>
    </svg>
  ),
  Aqara: (
    <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
      <circle cx="50" cy="50" r="48" fill="#009FDF" />
      <path d="M 30 50 L 50 65 L 70 50 L 50 35 Z" fill="white" />
    </svg>
  ),
};

export function VendorLogo({
  name,
  size = 36,
}: {
  name: string;
  size?: number;
}) {
  const logo = VENDOR_LOGOS[name];

  if (!logo) {
    // Fallback: initials in graphite background
    return (
      <div
        className="rounded-[10px] bg-graphite flex items-center justify-center shrink-0"
        style={{ width: size, height: size }}
      >
        <span
          className="font-serif text-white leading-none select-none"
          style={{ fontSize: Math.round(size * 0.36) }}
        >
          {name.slice(0, 2).toUpperCase()}
        </span>
      </div>
    );
  }

  return (
    <div
      className="rounded-[10px] flex items-center justify-center shrink-0 overflow-hidden"
      style={{ width: size, height: size }}
    >
      <svg width={size} height={size} viewBox="0 0 100 100">
        {logo}
      </svg>
    </div>
  );
}
