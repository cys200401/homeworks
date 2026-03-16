"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { toApiPath } from "@/lib/api";

type OverviewResponse = {
  health: {
    status: string;
    database: string;
  };
  latestStages: Array<{
    stage: string;
    status: string;
    startedAt: string;
    finishedAt: string | null;
  }>;
  recentErrorCount: number;
  recentPv: Array<{
    statDate: string;
    totalPv: number;
  }>;
};

type PipelineRunsResponse = {
  items: Array<{
    id: string;
    stage: string;
    status: string;
    successCount: number;
    failedCount: number;
    skippedCount: number;
    startedAt: string;
    finishedAt: string | null;
  }>;
};

type ErrorsResponse = {
  items: Array<{
    id: string;
    stage: string;
    errorCode: string | null;
    errorMessage: string;
    createdAt: string;
  }>;
};

export default function AdminPage() {
  const [overview, setOverview] = useState<OverviewResponse | null>(null);
  const [pipelineRuns, setPipelineRuns] = useState<PipelineRunsResponse["items"]>(
    [],
  );
  const [errors, setErrors] = useState<ErrorsResponse["items"]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function loadAdminData() {
      try {
        setLoading(true);
        setError(null);

        const [overviewResponse, runsResponse, errorsResponse] =
          await Promise.all([
            fetch(toApiPath("/admin/overview")),
            fetch(toApiPath("/admin/pipeline-runs")),
            fetch(toApiPath("/admin/errors")),
          ]);

        if (!overviewResponse.ok || !runsResponse.ok || !errorsResponse.ok) {
          throw new Error("admin api request failed");
        }

        const [overviewData, runsData, errorsData] = await Promise.all([
          overviewResponse.json() as Promise<OverviewResponse>,
          runsResponse.json() as Promise<PipelineRunsResponse>,
          errorsResponse.json() as Promise<ErrorsResponse>,
        ]);

        if (!cancelled) {
          setOverview(overviewData);
          setPipelineRuns(runsData.items);
          setErrors(errorsData.items);
        }
      } catch (loadError) {
        if (!cancelled) {
          setError(
            loadError instanceof Error
              ? loadError.message
              : "unknown admin loading error",
          );
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    void loadAdminData();

    return () => {
      cancelled = true;
    };
  }, []);

  if (loading) {
    return (
      <div className="admin-page">
        <div className="admin-hero">
          <p className="admin-hero__eyebrow">内部监控</p>
          <h1 className="admin-hero__title">后台概览</h1>
          <p className="admin-hero__subtitle">正在加载后台概览，请稍候。</p>
        </div>
      </div>
    );
  }

  if (error || !overview) {
    return (
      <div className="admin-page">
        <div className="admin-hero">
          <p className="admin-hero__eyebrow">内部监控</p>
          <h1 className="admin-hero__title">后台概览</h1>
          <p className="admin-hero__subtitle">
            后台数据暂时不可用。请确认 FastAPI 已启动、`DATABASE_URL` 已设置，并已执行
            `backend/sql/init.sql` 与 `backend/sql/seed_phase2a.sql`。
          </p>
        </div>

        <section className="admin-panel admin-panel--error">
          <h2 className="admin-panel__title">连接错误</h2>
          <p className="admin-panel__text">{error ?? "overview missing"}</p>
          <Link href="/" className="admin-backlink">
            返回首页
          </Link>
        </section>
      </div>
    );
  }

  const recentPv = overview.recentPv;

  return (
    <div className="admin-page">
      <section className="admin-hero">
        <p className="admin-hero__eyebrow">内部监控</p>
        <h1 className="admin-hero__title">后台概览</h1>
        <p className="admin-hero__subtitle">
          当前展示最小监控摘要：最近 stage 状态、错误列表和 PV 汇总。当前数据口径包含
          seed 与真实记录。
        </p>
      </section>

      <section className="admin-grid">
        <article className="admin-panel">
          <h2 className="admin-panel__title">系统健康</h2>
          <div className="admin-kpis">
            <div className="admin-kpi">
              <span className="admin-kpi__label">API 状态</span>
              <strong className="admin-kpi__value">{overview.health.status}</strong>
            </div>
            <div className="admin-kpi">
              <span className="admin-kpi__label">数据库状态</span>
              <strong className="admin-kpi__value">
                {overview.health.database}
              </strong>
            </div>
            <div className="admin-kpi">
              <span className="admin-kpi__label">最近错误数</span>
              <strong className="admin-kpi__value">
                {overview.recentErrorCount}
              </strong>
            </div>
          </div>
        </article>

        <article className="admin-panel">
          <h2 className="admin-panel__title">最近 Stage 状态</h2>
          <ul className="admin-list">
            {overview.latestStages.map((item) => (
              <li key={item.stage} className="admin-list__item">
                <span className="admin-list__primary">{item.stage}</span>
                <span className="admin-list__badge">{item.status}</span>
              </li>
            ))}
          </ul>
        </article>

        <article className="admin-panel">
          <h2 className="admin-panel__title">最近几天 PV 汇总</h2>
          <ul className="admin-list">
            {overview.recentPv.map((item) => (
              <li key={item.statDate} className="admin-list__item">
                <span className="admin-list__primary">{item.statDate}</span>
                <span className="admin-list__secondary">{item.totalPv} PV</span>
              </li>
            ))}
          </ul>
        </article>
      </section>

      <section className="admin-stack">
        <article className="admin-panel">
          <h2 className="admin-panel__title">运行记录</h2>
          <ul className="admin-table">
            {pipelineRuns.map((item) => (
              <li key={item.id} className="admin-table__row">
                <span>{item.stage}</span>
                <span>{item.status}</span>
                <span>成功 {item.successCount}</span>
                <span>失败 {item.failedCount}</span>
              </li>
            ))}
          </ul>
        </article>

        <article className="admin-panel">
          <h2 className="admin-panel__title">错误列表</h2>
          <ul className="admin-table">
            {errors.map((item) => (
              <li key={item.id} className="admin-table__row">
                <span>{item.stage}</span>
                <span>{item.errorCode ?? "UNKNOWN"}</span>
                <span>{item.errorMessage}</span>
              </li>
            ))}
          </ul>
        </article>

        <article className="admin-panel">
          <h2 className="admin-panel__title">流量摘要</h2>
          <ul className="admin-list">
            {recentPv.map((item) => (
              <li key={item.statDate} className="admin-list__item">
                <span className="admin-list__primary">{item.statDate}</span>
                <span className="admin-list__secondary">{item.totalPv} PV</span>
              </li>
            ))}
          </ul>
          <p className="admin-panel__hint">
            当前仅展示 PV，不展示 UV，也不接入更细粒度埋点。
          </p>
        </article>
      </section>
    </div>
  );
}
