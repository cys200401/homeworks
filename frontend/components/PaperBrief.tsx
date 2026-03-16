import type { PaperBrief as PaperBriefData } from "@/types/daily";

interface PaperBriefProps {
  paper: PaperBriefData;
}

export default function PaperBrief({ paper }: PaperBriefProps) {
  return (
    <article className="paper-brief">
      <div className="paper-brief__shape" aria-hidden="true" />
      <a
        className="paper-brief__title"
        href={paper.arxivUrl}
        target="_blank"
        rel="noopener noreferrer"
      >
        {paper.title}
      </a>
      <p className="paper-brief__authors">{paper.authors.join(", ")}</p>
      <p className="paper-brief__tldr">{paper.tldr}</p>
      <p className="paper-brief__comment">{paper.comment}</p>
    </article>
  );
}
