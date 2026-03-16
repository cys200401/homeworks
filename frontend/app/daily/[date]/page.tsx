import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

import PaperBrief from "@/components/PaperBrief";
import PaperHighlight from "@/components/PaperHighlight";
import ReportHeader from "@/components/ReportHeader";
import SectionDivider from "@/components/SectionDivider";
import TrafficBeacon from "@/components/traffic/TrafficBeacon";
import { reports } from "@/data/daily";

export async function generateStaticParams() {
  return reports.map((report) => ({ date: report.date }));
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ date: string }>;
}): Promise<Metadata> {
  const { date } = await params;
  const report = reports.find((item) => item.date === date);

  if (!report) {
    return {
      title: "日报不存在 | Daily Paper",
    };
  }

  return {
    title: `${report.title} | Daily Paper`,
    description: report.summary,
  };
}

export default async function Page({
  params,
}: {
  params: Promise<{ date: string }>;
}) {
  const { date } = await params;
  const report = reports.find((item) => item.date === date);

  if (!report) {
    notFound();
  }

  return (
    <div className="daily-page">
      <TrafficBeacon path={`/daily/${report.date}`} pageType="daily" />
      <Link href="/" className="daily-page__back">
        ← 返回首页
      </Link>

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
  );
}
