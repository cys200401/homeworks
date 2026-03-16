import Link from "next/link";

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
            现在同时支持多用户个性化工作台。每个终端用户都可以拥有自己的投送时间、论文发表时间窗、分类组合和主题 Prompt。
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

      <section className="workspace-launchpad" aria-label="个性化工作台入口">
        <article className="workspace-launchpad__card">
          <p className="workspace-launchpad__eyebrow">Demo User</p>
          <h2 className="workspace-launchpad__title">Research Lead</h2>
          <p className="workspace-launchpad__text">
            偏研究运营，关注智能体、长上下文和训练效率，默认早上 8 点投送。
          </p>
          <Link href="/u/research-lead" className="workspace-launchpad__link">
            打开工作台
          </Link>
        </article>

        <article className="workspace-launchpad__card">
          <p className="workspace-launchpad__eyebrow">Demo User</p>
          <h2 className="workspace-launchpad__title">Vision Scout</h2>
          <p className="workspace-launchpad__text">
            偏视觉与检索应用，使用高对比主题和更紧凑的信息密度。
          </p>
          <Link href="/u/vision-scout" className="workspace-launchpad__link">
            打开工作台
          </Link>
        </article>
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
