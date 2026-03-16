/**
 * 单篇论文的基本信息（重点关注 & 也值得关注 共用）
 */
export interface PaperBase {
  /** arXiv ID，如 "2603.03078v1" */
  arxivId: string;
  /** 论文标题（英文原标题） */
  title: string;
  /** 作者列表 */
  authors: string[];
  /** 论文摘要（英文） */
  abstract: string;
  /** arXiv 分类标签，如 ["cs.AI", "cs.LG"] */
  categories: string[];
  /** arXiv 链接 */
  arxivUrl: string;
  /** 一句话中文总结（15-30字） */
  tldr: string;
}

/**
 * 重点关注论文 — 基于全文的深度分析
 */
export interface PaperHighlight extends PaperBase {
  /** 核心研究问题（中文，1-2句） */
  problem: string;
  /** 方法/方案（中文，2-4句） */
  methodology: string;
  /** 关键发现（中文，每条1句） */
  keyFindings: string[];
  /** 为什么重要（中文，1-2句） */
  significance: string;
  /** 局限性（中文，可选） */
  limitations?: string;
}

/**
 * 也值得关注论文 — 摘要级别简介
 */
export interface PaperBrief extends PaperBase {
  /** 为什么值得关注（中文，1-2句） */
  comment: string;
}

/**
 * 单日日报完整数据
 * */
export interface DailyReport {
  /** 日期 YYYY-MM-DD */
  date: string;
  /** 日报标题，如 "2024年1月15日 AI论文日报" */
  title: string;
  /** 当日总览（中文，3-5句） */
  summary: string;
  /** 爬虫收录论文总数 */
  totalPapers: number;
  /** 重点论文（3-6篇，基于全文分析） */
  highlights: PaperHighlight[];
  /** 推荐论文（5-10篇，基于摘要） */
  notables: PaperBrief[];
  /** 趋势洞察（中文，可选） */
  trends?: string;
  /** 关键词标签 */
  tags: string[];
}

/**
 * 首页卡片用的摘要（从 DailyReport 中提取）
 */
export interface DailyDigest {
  date: string;
  title: string;
  summary: string;
  totalPapers: number;
  highlightCount: number;
  notableCount: number;
  tags: string[];
}

/** 从 DailyReport 生成 DailyDigest */
export function toDigest(report: DailyReport): DailyDigest {
  return {
    date: report.date,
    title: report.title,
    summary: report.summary,
    totalPapers: report.totalPapers,
    highlightCount: report.highlights.length,
    notableCount: report.notables.length,
    tags: report.tags,
  };
}
