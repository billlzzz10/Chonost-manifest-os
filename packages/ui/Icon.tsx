import React from 'react';
import * as Lucide from "lucide-react";
import * as SI from "simple-icons/icons";

type IconSize = number | 'sm' | 'md' | 'lg';
const ICON_SIZE_MAP: Record<'sm' | 'md' | 'lg', number> = { sm: 16, md: 20, lg: 24 };

interface IconProps {
  name: string;
  size?: IconSize;
  color?: string;
  strokeWidth?: number;
  className?: string;
}

export const Icon: React.FC<IconProps> = ({
  name,
  size = 'md',
  color = "currentColor",
  strokeWidth = 2,
  className = ""
}) => {
  const resolvedSize = typeof size === 'number' ? size : ICON_SIZE_MAP[size] ?? ICON_SIZE_MAP.md;

  // รูปแบบการเรียกใช้งาน:
  // "lucide:edit-3", "lucide:eraser", ...
  // "logo:github", "logo:figma", ...
  if (name.startsWith("lucide:")) {
    const key = name.split(":")[1];
    const Cmp = (Lucide as any)[pascal(key)];
    if (typeof Cmp === "undefined") {
      return <Lucide.HelpCircle size={resolvedSize} strokeWidth={strokeWidth} color={color} className={className} />;
    }
    return <Cmp size={resolvedSize} strokeWidth={strokeWidth} color={color} className={className} />;
  }

  if (name.startsWith("logo:")) {
    const slug = name.split(":")[1]; // เช่น github, figma, notion
    const icon = (SI as any)[`si${slugToKey(slug)}`];
    if (!icon) return <Lucide.HelpCircle size={resolvedSize} className={className} />;
    return (
      <svg
        width={resolvedSize}
        height={resolvedSize}
        viewBox="0 0 24 24"
        role="img"
        aria-label={icon.title}
        className={className}
      >
        <path d={icon.path} fill={icon.hex ? `#${icon.hex}` : color} />
      </svg>
    );
  }

  return <Lucide.HelpCircle size={resolvedSize} className={className} />;
};

function pascal(k: string): string {
  return k.split(/-|_/).map(s => s.charAt(0).toUpperCase() + s.slice(1)).join("");
}

function slugToKey(s: string): string {
  // github -> Github, google-cloud -> Googlecloud
  return s.split(/-|_/).map(x => x.charAt(0).toUpperCase() + x.slice(1)).join("");
}

