import type { PaperBrief, PaperHighlight } from "@/types/daily";

export interface ThemePalette {
  background: string;
  foreground: string;
  accent: string;
  accentSoft: string;
  surface: string;
  surfaceAlt: string;
  border: string;
}

export interface ThemeTokens {
  themeName: string;
  fontPreset: "editorial" | "modern" | "mono";
  layoutDensity: "airy" | "balanced" | "compact";
  cardStyle: "panel" | "pill" | "outline";
  heroPattern: "mesh" | "rays" | "grid";
  borderRadius: "sharp" | "soft" | "round";
  motionLevel: "calm" | "lively";
  palette: ThemePalette;
}

export interface UserDeliveryProfile {
  deliveryEnabled: boolean;
  deliveryLocalTime: string;
  windowStartHour: number;
  windowEndHour: number;
  lookbackDays: number;
  categories: string[];
  nextRunAt: string | null;
  lastRunAt: string | null;
}

export interface UserSummaryItem {
  handle: string;
  displayName: string;
  timezone: string;
  deliveryEnabled: boolean;
  deliveryLocalTime: string;
  categories: string[];
  themeName: string;
  nextRunAt: string | null;
  latestReportDate: string | null;
}

export interface UserProfile {
  handle: string;
  displayName: string;
  email: string | null;
  timezone: string;
  delivery: UserDeliveryProfile;
  themePrompt: string;
  theme: ThemeTokens;
  latestReportDate: string | null;
}

export interface UserThemeResponse {
  promptText: string;
  theme: ThemeTokens;
}

export interface UserReport {
  date: string;
  title: string;
  summary: string;
  totalPapers: number;
  tags: string[];
  trends?: string | null;
  highlights: PaperHighlight[];
  notables: PaperBrief[];
  publishedAt: string;
  theme: ThemeTokens;
  source: Record<string, unknown>;
}

export interface UserWorkspaceResponse {
  user: UserProfile;
  report: UserReport | null;
}

export interface UserListResponse {
  items: UserSummaryItem[];
}
