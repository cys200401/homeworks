import type { CSSProperties } from "react";

import type { ThemeTokens, UserDeliveryProfile } from "@/types/personalized";

const FONT_PRESETS: Record<ThemeTokens["fontPreset"], string> = {
  editorial: '"Iowan Old Style", "Palatino Linotype", "Book Antiqua", serif',
  modern: '"Outfit", "Helvetica Neue", Arial, sans-serif',
  mono: '"SFMono-Regular", "IBM Plex Mono", "Courier New", monospace',
};

const RADIUS_PRESETS: Record<ThemeTokens["borderRadius"], string> = {
  sharp: "0px",
  soft: "14px",
  round: "24px",
};

type ThemeStyle = CSSProperties & Record<`--${string}`, string>;

export function themeToStyle(theme: ThemeTokens): ThemeStyle {
  const shadowSize = theme.motionLevel === "lively" ? "10px" : "6px";

  return {
    "--color-background": theme.palette.background,
    "--color-foreground": theme.palette.foreground,
    "--color-red": theme.palette.accentSoft,
    "--color-blue": theme.palette.accent,
    "--color-yellow": theme.palette.surfaceAlt,
    "--color-muted": theme.palette.surfaceAlt,
    "--color-white": theme.palette.surface,
    "--font-display": FONT_PRESETS[theme.fontPreset],
    "--radius-sharp": RADIUS_PRESETS[theme.borderRadius],
    "--shadow-small": `${shadowSize} ${shadowSize} 0 0 ${theme.palette.border}`,
    "--shadow-large": `${Number.parseInt(shadowSize, 10) + 4}px ${Number.parseInt(shadowSize, 10) + 4}px 0 0 ${theme.palette.border}`,
    "--theme-border": theme.palette.border,
  };
}

export function formatDeliveryWindow(delivery: UserDeliveryProfile) {
  const endHour = delivery.windowEndHour === 24 ? "24:00" : `${String(delivery.windowEndHour).padStart(2, "0")}:00`;
  return `${String(delivery.windowStartHour).padStart(2, "0")}:00 - ${endHour}`;
}

export function formatTimestamp(value: string | null, locale = "zh-CN") {
  if (!value) {
    return "未生成";
  }

  return new Intl.DateTimeFormat(locale, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}
