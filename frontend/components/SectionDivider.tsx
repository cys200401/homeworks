interface SectionDividerProps {
  title: string;
  count?: number;
}

export default function SectionDivider({
  title,
  count,
}: SectionDividerProps) {
  return (
    <div className="section-divider">
      <div className="section-divider__rule" aria-hidden="true" />
      <h2 className="section-divider__title">
        {title}
        {typeof count === "number" ? (
          <span className="section-divider__count">{count}</span>
        ) : null}
      </h2>
    </div>
  );
}
