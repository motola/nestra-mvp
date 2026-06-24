// Curated architectural photos (verified to resolve). Mapped deterministically
// per property so a given property always gets the same cover. Callers layer a
// gradient scrim + fallback colour so it never looks broken if an image fails.
const COVERS = [
  "1568605114967-8130f3a36994",
  "1570129477492-45c003edd2be",
  "1512917774080-9991f1c4c750",
  "1486406146926-c627a92ad1ab",
  "1416331108676-a22ccb276e35",
  "1554995207-c18c203602cb",
  "1502005229762-cf1b2da7c5d6",
  "1564013799919-ab600027ffc6",
];

export function coverUrl(seed: string, width = 600): string {
  let h = 0;
  for (let i = 0; i < seed.length; i++) h = (h * 31 + seed.charCodeAt(i)) >>> 0;
  const id = COVERS[h % COVERS.length];
  return `https://images.unsplash.com/photo-${id}?w=${width}&q=70&auto=format&fit=crop`;
}
