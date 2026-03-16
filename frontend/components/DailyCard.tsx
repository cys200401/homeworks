import Link from "next/link";

import type { DailyDigest } from "@/types/daily";

interface DailyCardProps {
  digest: DailyDigest;
}

export default function DailyCard({ digest }: DailyCardProps) {
  return (
    <Link href={`/daily/${digest.date}`} className="daily-card">
      <div className="daily-card__shape" aria-hidden="true" />
      <p className="daily-card__date">{digest.date}</p>
      <h2 className="daily-card__title">{digest.title}</h2>
      <p className="daily-card__summary">{digest.summary}</p>

      <div className="daily-card__stats" aria-label={`${digest.title} 统计`}>
        <div className="daily-card__stat">
          <span className="daily-card__stat-label">收录</span>
          <strong className="daily-card__stat-value">
            {digest.totalPapers} 篇
          </strong>
        </div>
        <div className="daily-card__stat">
          <span className="daily-card__stat-label">重点</span>
          <strong className="daily-card__stat-value">
            {digest.highlightCount} 篇
          </strong>
        </div>
        <div className="daily-card__stat">
          <span className="daily-card__stat-label">推荐</span>
          <strong className="daily-card__stat-value">
            {digest.notableCount} 篇
          </strong>
        </div>
      </div>

      <ul className="daily-card__tags" aria-label={`${digest.title} 标签`}>
        {digest.tags.map((tag) => (
          <li key={tag} className="daily-card__tag">
            {tag}
          </li>
        ))}
      </ul>
    </Link>
  );
}
