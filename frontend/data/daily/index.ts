import type { DailyReport } from "@/types/daily";
import { report as r20260314 } from "./2026-03-14";
import { report as r20260313 } from "./2026-03-13";
import { report as r20260312 } from "./2026-03-12";
import { report as r20000101 } from "./2000-01-01";

// --- 在此处添加 import（格式：r + 日期去连字符） ---
// 示例: import { report as r20240115 } from "./2024-01-15";

// --- reports 数组（最新日期在最前面） ---
export const reports: DailyReport[] = [
  r20260314,
  r20260313,
  r20260312,
  r20000101,
];
