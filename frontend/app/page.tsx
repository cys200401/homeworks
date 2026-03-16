import DailyCard from "@/components/DailyCard";
import TrafficBeacon from "@/components/traffic/TrafficBeacon";
import { reports } from "@/data/daily";
import { toDigest } from "@/types/daily";

export default function Home() {
  const digests = [...reports]
    .sort((left, right) => right.date.localeCompare(left.date))
    .map(toDigest);

  return (
    <div className="home-page">
      <TrafficBeacon path="/" pageType="home" />
      <section className="home-hero">
        <div className="home-hero__content">
          <p className="home-hero__eyebrow">AI 论文日报</p>
          <h1 className="home-hero__title">Daily Paper</h1>
          <p className="home-hero__subtitle">
            每天筛选值得读的 AI 论文，用清晰结构呈现重点研究、推荐阅读与趋势洞察。
          </p>
        </div>
        <div className="home-hero__art" aria-hidden="true">
          <div className="home-hero__circle" />
          <div className="home-hero__square" />
          <div className="home-hero__frame">
            <div className="home-hero__triangle" />
          </div>
        </div>
      </section>

      {digests.length === 0 ? (
        <section className="home-empty">
          <p className="home-empty__text">暂无日报数据</p>
        </section>
      ) : (
        <section className="daily-grid" aria-label="日报列表">
          {digests.map((digest) => (
            <DailyCard key={digest.date} digest={digest} />
          ))}
        </section>
      )}
    </div>
  );
}
