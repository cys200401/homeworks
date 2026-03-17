"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import PaperBrief from "@/components/PaperBrief";
import PaperHighlight from "@/components/PaperHighlight";
import ReportHeader from "@/components/ReportHeader";
import SectionDivider from "@/components/SectionDivider";
import TrafficBeacon from "@/components/traffic/TrafficBeacon";
import { toApiPath } from "@/lib/api";
import {
  formatDeliveryWindow,
  formatTimestamp,
  themeToStyle,
} from "@/lib/personalized-theme";
import type { UserWorkspaceResponse } from "@/types/personalized";

interface UserWorkspaceProps {
  handle: string;
}

export default function UserWorkspace({ handle }: UserWorkspaceProps) {
  const [workspace, setWorkspace] = useState<UserWorkspaceResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function loadWorkspace() {
      try {
        setLoading(true);
        setError(null);

        const response = await fetch(toApiPath(`/users/${handle}/workspace`));
        if (!response.ok) {
          throw new Error(`workspace request failed with ${response.status}`);
        }

        const payload =
          (await response.json()) as UserWorkspaceResponse;

        if (!cancelled) {
          setWorkspace(payload);
        }
      } catch (loadError) {
        if (!cancelled) {
          setError(
            loadError instanceof Error
              ? loadError.message
              : "unknown workspace error",
          );
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    void loadWorkspace();

    return () => {
      cancelled = true;
    };
  }, [handle]);

  if (loading) {
    return (
      <div className="user-workspace-shell">
        <div className="workspace-status">
          <p className="workspace-status__eyebrow">个性化工作台</p>
          <h1 className="workspace-status__title">正在加载 {handle}</h1>
          <p className="workspace-status__text">系统正在读取用户配置、主题和最新报告。</p>
        </div>
      </div>
    );
  }

  if (!workspace || error) {
    return (
      <div className="user-workspace-shell">
        <div className="workspace-status workspace-status--error">
          <p className="workspace-status__eyebrow">个性化工作台</p>
          <h1 className="workspace-status__title">工作台暂不可用</h1>
          <p className="workspace-status__text">
            请确认后端已启动，数据库已经执行最新的 `init.sql` 与 `seed_phase2a.sql`。
          </p>
          <p className="workspace-status__text">{error ?? "workspace missing"}</p>
          <div className="workspace-actions">
            <Link href="/" className="workspace-link">
              返回首页
            </Link>
          </div>
        </div>
      </div>
    );
  }

  const report = workspace.report;
  const theme = report?.theme ?? workspace.user.theme;
  const themeStyle = themeToStyle(theme);
  const crawlMeta = report?.source.crawlMeta;
  const effectiveLookbackDays =
    typeof report?.source.effectiveLookbackDays === "number"
      ? report.source.effectiveLookbackDays
      : workspace.user.delivery.lookbackDays;
  const searchExpanded = Boolean(report?.source.searchExpanded);
  const crawlSummary = crawlMeta
    ? [
        crawlMeta.triggerMode === "due_delivery" ? "到点自动抓取" : "手动触发抓取",
        typeof crawlMeta.uniqueRecords === "number"
          ? `抓到 ${crawlMeta.uniqueRecords} 篇`
          : null,
        typeof crawlMeta.upserted === "number"
          ? `入库 ${crawlMeta.upserted} 篇`
          : null,
      ]
        .filter(Boolean)
        .join(" / ")
    : "当前报告未附带抓取摘要。";

  return (
    <div className="user-workspace-shell">
      <TrafficBeacon path={`/u/${handle}`} pageType="workspace" />

      <div
        className="user-workspace"
        style={themeStyle}
        data-density={theme.layoutDensity}
        data-card-style={theme.cardStyle}
        data-hero-pattern={theme.heroPattern}
        data-radius={theme.borderRadius}
      >
        <section className="workspace-toolbar">
          <Link href="/" className="workspace-link">
            ← 返回首页
          </Link>
          <Link href={`/u/${handle}/settings`} className="workspace-link">
            编辑时间窗与主题
          </Link>
        </section>

        <section className="workspace-banner">
          <div className="workspace-banner__content">
            <p className="workspace-banner__eyebrow">Personal AI Feed</p>
            <h1 className="workspace-banner__title">{workspace.user.displayName}</h1>
            <p className="workspace-banner__subtitle">
              当前工作台会按 {workspace.user.timezone} 时区、每日{" "}
              {workspace.user.delivery.deliveryLocalTime.slice(0, 5)} 投送，
              仅展示匹配该用户分类和发表时间窗口的内容。
            </p>
          </div>

          <dl className="workspace-metrics">
            <div className="workspace-metric">
              <dt>类别</dt>
              <dd>{workspace.user.delivery.categories.join(", ")}</dd>
            </div>
            <div className="workspace-metric">
              <dt>发表窗口</dt>
              <dd>{formatDeliveryWindow(workspace.user.delivery)}</dd>
            </div>
            <div className="workspace-metric">
              <dt>下次投送</dt>
              <dd>{formatTimestamp(workspace.user.delivery.nextRunAt)}</dd>
            </div>
            <div className="workspace-metric">
              <dt>主题风格</dt>
              <dd>{theme.themeName}</dd>
            </div>
          </dl>
        </section>

        <section className="workspace-meta">
          <div className="workspace-panel">
            <h2 className="workspace-panel__title">当前主题 Prompt</h2>
            <p className="workspace-panel__text">
              {workspace.user.themePrompt || "未填写，当前使用默认主题。"}
            </p>
          </div>
          <div className="workspace-panel">
            <h2 className="workspace-panel__title">投送规则</h2>
            <p className="workspace-panel__text">
              回看 {workspace.user.delivery.lookbackDays} 天，按{" "}
              {workspace.user.delivery.categories.join(" / ")} 分类过滤。
            </p>
          </div>
          <div className="workspace-panel">
            <h2 className="workspace-panel__title">最近自动抓取</h2>
            <p className="workspace-panel__text">{crawlSummary}</p>
            {report ? (
              <p className="workspace-panel__text">
                最近抓取时间 {formatTimestamp(crawlMeta?.triggeredAt ?? report.publishedAt)}
                ，当前检索窗口为 {effectiveLookbackDays} 天
                {searchExpanded ? "（本次触发了自动扩搜）" : ""}。
              </p>
            ) : (
              <p className="workspace-panel__text">
                当前还没有最新报告，系统尚未执行到点抓取。
              </p>
            )}
          </div>
        </section>

        {report ? (
          <>
            <div className="workspace-report">
              <ReportHeader
                date={report.date}
                title={report.title}
                summary={report.summary}
                totalPapers={report.totalPapers}
                tags={report.tags}
              />

              <SectionDivider title="重点关注" count={report.highlights.length} />
              <div className="daily-page__stack">
                {report.highlights.map((paper, index) => (
                  <PaperHighlight key={paper.arxivId} paper={paper} index={index} />
                ))}
              </div>

              <SectionDivider title="也值得关注" count={report.notables.length} />
              <div className="daily-page__brief-grid">
                {report.notables.map((paper) => (
                  <PaperBrief key={paper.arxivId} paper={paper} />
                ))}
              </div>

              {report.trends ? (
                <>
                  <SectionDivider title="趋势洞察" />
                  <section className="trend-panel">
                    <p className="trend-panel__text">{report.trends}</p>
                  </section>
                </>
              ) : null}
            </div>
          </>
        ) : (
          <section className="workspace-status">
            <p className="workspace-status__eyebrow">暂无日报</p>
            <h2 className="workspace-status__title">系统还没有为这个用户生成报告</h2>
            <p className="workspace-status__text">
              你可以先进入设置页保存时间窗和主题，然后点击“立即生成”。
            </p>
          </section>
        )}
      </div>
    </div>
  );
}
