import type { PaperHighlight as PaperHighlightData } from "@/types/daily";

interface PaperHighlightProps {
  paper: PaperHighlightData;
  index: number;
}

export default function PaperHighlight({
  paper,
  index,
}: PaperHighlightProps) {
  const displayIndex = String(index + 1).padStart(2, "0");

  return (
    <article className="paper-highlight">
      <div className="paper-highlight__index" aria-label={`第 ${displayIndex} 篇`}>
        {displayIndex}
      </div>

      <div className="paper-highlight__body">
        <a
          className="paper-highlight__title"
          href={paper.arxivUrl}
          target="_blank"
          rel="noopener noreferrer"
        >
          {paper.title}
        </a>

        <p className="paper-highlight__authors">{paper.authors.join(", ")}</p>

        <ul className="paper-highlight__categories">
          {paper.categories.map((category) => (
            <li key={category} className="paper-highlight__category">
              {category}
            </li>
          ))}
        </ul>

        <p className="paper-highlight__tldr">{paper.tldr}</p>

        <div className="paper-highlight__sections">
          <section className="paper-highlight__section">
            <h3 className="paper-highlight__section-title">研究问题</h3>
            <p className="paper-highlight__section-content">{paper.problem}</p>
          </section>

          <section className="paper-highlight__section">
            <h3 className="paper-highlight__section-title">方法</h3>
            <p className="paper-highlight__section-content">
              {paper.methodology}
            </p>
          </section>

          <section className="paper-highlight__section">
            <h3 className="paper-highlight__section-title">关键发现</h3>
            <ul className="paper-highlight__findings">
              {paper.keyFindings.map((finding) => (
                <li key={finding} className="paper-highlight__finding">
                  {finding}
                </li>
              ))}
            </ul>
          </section>

          <section className="paper-highlight__section">
            <h3 className="paper-highlight__section-title">意义</h3>
            <p className="paper-highlight__section-content">
              {paper.significance}
            </p>
          </section>

          {paper.limitations ? (
            <section className="paper-highlight__section">
              <h3 className="paper-highlight__section-title">局限</h3>
              <p className="paper-highlight__section-content">
                {paper.limitations}
              </p>
            </section>
          ) : null}
        </div>
      </div>
    </article>
  );
}
