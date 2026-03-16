interface ReportHeaderProps {
  date: string;
  title: string;
  summary: string;
  totalPapers: number;
  tags: string[];
}

export default function ReportHeader({
  date,
  title,
  summary,
  totalPapers,
  tags,
}: ReportHeaderProps) {
  return (
    <header className="report-header">
      <div className="report-header__content">
        <p className="report-header__eyebrow">{date}</p>
        <h1 className="report-header__title">{title}</h1>
        <p className="report-header__summary">{summary}</p>

        <div className="report-header__stats">
          <div className="report-header__stat">
            <span className="report-header__stat-label">收录论文</span>
            <strong className="report-header__stat-value">
              {totalPapers}
            </strong>
          </div>
        </div>

        <ul className="report-header__tags" aria-label="日报标签">
          {tags.map((tag) => (
            <li key={tag} className="report-header__tag">
              {tag}
            </li>
          ))}
        </ul>
      </div>

      <div className="report-header__art" aria-hidden="true">
        <div className="report-header__circle" />
        <div className="report-header__square" />
        <div className="report-header__triangle" />
      </div>
    </header>
  );
}
