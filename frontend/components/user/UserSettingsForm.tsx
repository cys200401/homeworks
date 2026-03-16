"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useMemo, useState } from "react";

import TrafficBeacon from "@/components/traffic/TrafficBeacon";
import { toApiPath } from "@/lib/api";
import { formatDeliveryWindow, themeToStyle } from "@/lib/personalized-theme";
import type {
  ThemeTokens,
  UserProfile,
  UserThemeResponse,
  UserWorkspaceResponse,
} from "@/types/personalized";

const COMMON_AI_CATEGORIES = ["cs.AI", "cs.CL", "cs.CV", "cs.IR", "cs.LG", "cs.RO"];

interface UserSettingsFormProps {
  handle: string;
}

function splitPresetAndCustomCategories(categories: string[]) {
  const preset = new Set<string>();
  const custom: string[] = [];

  for (const category of categories) {
    if (COMMON_AI_CATEGORIES.includes(category)) {
      preset.add(category);
    } else {
      custom.push(category);
    }
  }

  return {
    preset,
    customText: custom.join(", "),
  };
}

function buildCategoryList(
  selectedPreset: Set<string>,
  customCategoryText: string,
) {
  const customCategories = customCategoryText
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);

  return [...selectedPreset, ...customCategories];
}

export default function UserSettingsForm({ handle }: UserSettingsFormProps) {
  const router = useRouter();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [displayName, setDisplayName] = useState("");
  const [timezone, setTimezone] = useState("");
  const [deliveryEnabled, setDeliveryEnabled] = useState(true);
  const [deliveryLocalTime, setDeliveryLocalTime] = useState("08:00");
  const [windowStartHour, setWindowStartHour] = useState(0);
  const [windowEndHour, setWindowEndHour] = useState(24);
  const [lookbackDays, setLookbackDays] = useState(1);
  const [selectedCategories, setSelectedCategories] = useState<Set<string>>(
    new Set(["cs.AI"]),
  );
  const [customCategoryText, setCustomCategoryText] = useState("");
  const [themePrompt, setThemePrompt] = useState("");
  const [theme, setTheme] = useState<ThemeTokens | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [savingPreferences, setSavingPreferences] = useState(false);
  const [savingTheme, setSavingTheme] = useState(false);
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    let cancelled = false;

    async function loadProfile() {
      try {
        setLoading(true);
        setError(null);

        const response = await fetch(toApiPath(`/users/${handle}`));
        if (!response.ok) {
          throw new Error(`profile request failed with ${response.status}`);
        }

        const payload = (await response.json()) as UserProfile;
        if (cancelled) {
          return;
        }

        const categoryState = splitPresetAndCustomCategories(
          payload.delivery.categories,
        );

        setProfile(payload);
        setDisplayName(payload.displayName);
        setTimezone(payload.timezone);
        setDeliveryEnabled(payload.delivery.deliveryEnabled);
        setDeliveryLocalTime(payload.delivery.deliveryLocalTime.slice(0, 5));
        setWindowStartHour(payload.delivery.windowStartHour);
        setWindowEndHour(payload.delivery.windowEndHour);
        setLookbackDays(payload.delivery.lookbackDays);
        setSelectedCategories(categoryState.preset);
        setCustomCategoryText(categoryState.customText);
        setThemePrompt(payload.themePrompt);
        setTheme(payload.theme);
      } catch (loadError) {
        if (!cancelled) {
          setError(
            loadError instanceof Error
              ? loadError.message
              : "unknown settings error",
          );
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    void loadProfile();

    return () => {
      cancelled = true;
    };
  }, [handle]);

  const previewTheme = theme ?? profile?.theme ?? null;
  const previewStyle = useMemo(
    () => (previewTheme ? themeToStyle(previewTheme) : undefined),
    [previewTheme],
  );

  function toggleCategory(category: string) {
    setSelectedCategories((current) => {
      const next = new Set(current);
      if (next.has(category)) {
        next.delete(category);
      } else {
        next.add(category);
      }
      return next;
    });
  }

  async function savePreferences() {
    try {
      setSavingPreferences(true);
      setStatusMessage(null);
      setError(null);

      const categories = buildCategoryList(selectedCategories, customCategoryText);
      const response = await fetch(toApiPath(`/users/${handle}/preferences`), {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          displayName,
          timezone,
          deliveryEnabled,
          deliveryLocalTime,
          windowStartHour,
          windowEndHour,
          lookbackDays,
          categories,
        }),
      });

      if (!response.ok) {
        throw new Error(`save preferences failed with ${response.status}`);
      }

      const payload = (await response.json()) as UserProfile;
      setProfile(payload);
      setStatusMessage("投送规则已保存。");
    } catch (saveError) {
      setError(
        saveError instanceof Error
          ? saveError.message
          : "unknown preference save error",
      );
    } finally {
      setSavingPreferences(false);
    }
  }

  async function saveTheme() {
    try {
      setSavingTheme(true);
      setStatusMessage(null);
      setError(null);

      const response = await fetch(toApiPath(`/users/${handle}/theme`), {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          promptText: themePrompt,
        }),
      });

      if (!response.ok) {
        throw new Error(`save theme failed with ${response.status}`);
      }

      const payload = (await response.json()) as UserThemeResponse;
      setThemePrompt(payload.promptText);
      setTheme(payload.theme);
      setProfile((current) =>
        current
          ? {
              ...current,
              themePrompt: payload.promptText,
              theme: payload.theme,
            }
          : current,
      );
      setStatusMessage("主题 Prompt 已保存，并重新编译为主题 token。");
    } catch (saveError) {
      setError(
        saveError instanceof Error ? saveError.message : "unknown theme save error",
      );
    } finally {
      setSavingTheme(false);
    }
  }

  async function generateReport() {
    try {
      setGenerating(true);
      setStatusMessage(null);
      setError(null);

      const response = await fetch(toApiPath(`/users/${handle}/report/generate`), {
        method: "POST",
      });

      if (!response.ok) {
        throw new Error(`generate report failed with ${response.status}`);
      }

      const payload = (await response.json()) as UserWorkspaceResponse;
      setProfile(payload.user);
      setTheme(payload.report?.theme ?? payload.user.theme);
      setStatusMessage("已经为当前用户生成最新报告，正在跳转。");
      router.push(`/u/${handle}`);
      router.refresh();
    } catch (saveError) {
      setError(
        saveError instanceof Error
          ? saveError.message
          : "unknown generate report error",
      );
    } finally {
      setGenerating(false);
    }
  }

  if (loading) {
    return (
      <div className="user-workspace-shell">
        <div className="workspace-status">
          <p className="workspace-status__eyebrow">个性化设置</p>
          <h1 className="workspace-status__title">正在加载 {handle}</h1>
          <p className="workspace-status__text">系统正在读取当前用户配置。</p>
        </div>
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="user-workspace-shell">
        <div className="workspace-status workspace-status--error">
          <p className="workspace-status__eyebrow">个性化设置</p>
          <h1 className="workspace-status__title">配置暂不可用</h1>
          <p className="workspace-status__text">{error ?? "profile missing"}</p>
          <div className="workspace-actions">
            <Link href={`/u/${handle}`} className="workspace-link">
              返回工作台
            </Link>
          </div>
        </div>
      </div>
    );
  }

  const activeCategories = buildCategoryList(selectedCategories, customCategoryText);

  return (
    <div className="user-workspace-shell">
      <TrafficBeacon path={`/u/${handle}/settings`} pageType="settings" />

      <div
        className="user-workspace user-workspace--settings"
        style={previewStyle}
        data-density={previewTheme?.layoutDensity ?? "balanced"}
        data-card-style={previewTheme?.cardStyle ?? "panel"}
        data-hero-pattern={previewTheme?.heroPattern ?? "mesh"}
        data-radius={previewTheme?.borderRadius ?? "soft"}
      >
        <section className="workspace-toolbar">
          <Link href={`/u/${handle}`} className="workspace-link">
            ← 返回工作台
          </Link>
          <Link href="/" className="workspace-link">
            返回首页
          </Link>
        </section>

        <section className="workspace-banner">
          <div className="workspace-banner__content">
            <p className="workspace-banner__eyebrow">Workspace Settings</p>
            <h1 className="workspace-banner__title">{profile.displayName}</h1>
            <p className="workspace-banner__subtitle">
              这里配置每个终端用户自己的投送时间、论文发表时间窗、分类和主题 Prompt。
            </p>
          </div>
          <dl className="workspace-metrics">
            <div className="workspace-metric">
              <dt>当前窗口</dt>
              <dd>
                {formatDeliveryWindow({
                  ...profile.delivery,
                  windowStartHour,
                  windowEndHour,
                })}
              </dd>
            </div>
            <div className="workspace-metric">
              <dt>活跃分类</dt>
              <dd>{activeCategories.join(", ") || "未选择"}</dd>
            </div>
            <div className="workspace-metric">
              <dt>下次投送</dt>
              <dd>{profile.delivery.nextRunAt ? "已排程" : "待保存"}</dd>
            </div>
            <div className="workspace-metric">
              <dt>主题</dt>
              <dd>{previewTheme?.themeName ?? "editorial"}</dd>
            </div>
          </dl>
        </section>

        <section className="settings-grid">
          <article className="workspace-panel workspace-panel--form">
            <h2 className="workspace-panel__title">投送规则</h2>
            <label className="settings-field">
              <span>显示名称</span>
              <input
                value={displayName}
                onChange={(event) => setDisplayName(event.target.value)}
              />
            </label>
            <label className="settings-field">
              <span>时区</span>
              <input
                value={timezone}
                onChange={(event) => setTimezone(event.target.value)}
                placeholder="Asia/Shanghai"
              />
            </label>
            <div className="settings-field settings-field--inline">
              <label>
                <span>每日投送</span>
                <input
                  type="time"
                  value={deliveryLocalTime}
                  onChange={(event) => setDeliveryLocalTime(event.target.value)}
                />
              </label>
              <label>
                <span>回看天数</span>
                <input
                  type="number"
                  min={1}
                  max={30}
                  value={lookbackDays}
                  onChange={(event) => setLookbackDays(Number(event.target.value))}
                />
              </label>
            </div>
            <div className="settings-field settings-field--inline">
              <label>
                <span>发表开始小时</span>
                <input
                  type="number"
                  min={0}
                  max={23}
                  value={windowStartHour}
                  onChange={(event) => setWindowStartHour(Number(event.target.value))}
                />
              </label>
              <label>
                <span>发表结束小时</span>
                <input
                  type="number"
                  min={0}
                  max={24}
                  value={windowEndHour}
                  onChange={(event) => setWindowEndHour(Number(event.target.value))}
                />
              </label>
            </div>
            <label className="settings-toggle">
              <input
                type="checkbox"
                checked={deliveryEnabled}
                onChange={(event) => setDeliveryEnabled(event.target.checked)}
              />
              <span>启用自动投送</span>
            </label>

            <div className="settings-field">
              <span>AI 分类</span>
              <div className="settings-chip-group">
                {COMMON_AI_CATEGORIES.map((category) => (
                  <button
                    key={category}
                    type="button"
                    className={`settings-chip${
                      selectedCategories.has(category) ? " settings-chip--active" : ""
                    }`}
                    onClick={() => toggleCategory(category)}
                  >
                    {category}
                  </button>
                ))}
              </div>
            </div>

            <label className="settings-field">
              <span>自定义分类（逗号分隔）</span>
              <input
                value={customCategoryText}
                onChange={(event) => setCustomCategoryText(event.target.value)}
                placeholder="例如 stat.ML, eess.AS"
              />
            </label>

            <div className="workspace-actions">
              <button
                type="button"
                className="workspace-button"
                onClick={() => void savePreferences()}
                disabled={savingPreferences}
              >
                {savingPreferences ? "保存中..." : "保存投送规则"}
              </button>
            </div>
          </article>

          <article className="workspace-panel workspace-panel--form">
            <h2 className="workspace-panel__title">主题 Prompt</h2>
            <label className="settings-field">
              <span>UI 提示词</span>
              <textarea
                value={themePrompt}
                onChange={(event) => setThemePrompt(event.target.value)}
                rows={6}
                placeholder="例如 Editorial dashboard with warm paper texture, calm motion and rounded cards."
              />
            </label>
            <p className="workspace-panel__hint">
              可以直接粘贴来自 design prompt 站点的风格描述，系统会先转成受控主题 token，再渲染页面。
            </p>

            <div className="workspace-actions">
              <button
                type="button"
                className="workspace-button"
                onClick={() => void saveTheme()}
                disabled={savingTheme}
              >
                {savingTheme ? "编译中..." : "保存主题 Prompt"}
              </button>
              <button
                type="button"
                className="workspace-button workspace-button--secondary"
                onClick={() => void generateReport()}
                disabled={generating}
              >
                {generating ? "生成中..." : "立即生成报告"}
              </button>
            </div>
          </article>
        </section>

        <section className="settings-preview">
          <article className="workspace-panel">
            <h2 className="workspace-panel__title">主题预览</h2>
            <p className="workspace-panel__text">
              当前主题将使用 {previewTheme?.fontPreset ?? "modern"} 字体预设、{" "}
              {previewTheme?.layoutDensity ?? "balanced"} 布局密度和{" "}
              {previewTheme?.heroPattern ?? "mesh"} 头图区块。
            </p>
            <ul className="settings-preview__palette">
              <li style={{ background: previewTheme?.palette.background }} />
              <li style={{ background: previewTheme?.palette.accent }} />
              <li style={{ background: previewTheme?.palette.accentSoft }} />
              <li style={{ background: previewTheme?.palette.surfaceAlt }} />
            </ul>
          </article>
        </section>

        {error ? (
          <section className="workspace-status workspace-status--error workspace-status--inline">
            <p className="workspace-status__text">{error}</p>
          </section>
        ) : null}

        {statusMessage ? (
          <section className="workspace-status workspace-status--inline">
            <p className="workspace-status__text">{statusMessage}</p>
          </section>
        ) : null}
      </div>
    </div>
  );
}
