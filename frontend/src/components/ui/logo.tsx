// Logo component — easily swap out for actual Alphacon branding
// Until logo is provided, using stylized "A" mark

export function LogoMark() {
  return (
    <div className="w-7 h-7 rounded-[7px] bg-accent flex items-center justify-center relative shrink-0">
      {/* TODO: Replace with actual Alphacon logo SVG */}
      <span className="font-serif text-[19px] text-white leading-none select-none">
        A
      </span>
      <span className="absolute top-[3px] right-[3px] w-[5px] h-[5px] rounded-full bg-white opacity-60" />
    </div>
  );
}
