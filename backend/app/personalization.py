from __future__ import annotations

from copy import deepcopy
from datetime import UTC, date, datetime, time, timedelta
from typing import Any, Iterable
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

FALLBACK_PAPERS: list[dict[str, Any]] = [
    {
        "arxivId": "2603.15001v1",
        "title": "Composable Agent Loops for Reliable Scientific Discovery",
        "authors": ["Ada Lovelace", "Alan Turing", "Fei-Fei Li"],
        "abstract": "We study how composable agent loops can improve reliability in scientific discovery workflows.",
        "categories": ["cs.AI", "cs.LG"],
        "arxivUrl": "https://arxiv.org/abs/2603.15001",
        "tldr": "通过可组合智能体循环提升科研任务可靠性。",
        "publishedAt": "2026-03-15T14:10:00Z",
        "problem": "单轮推理链在科研任务中容易遗漏证据，缺乏持续纠错机制。",
        "methodology": "作者把规划、检索、执行和反思拆成可循环的代理模块，并通过预算控制减少无效迭代。",
        "keyFindings": [
            "科研问答和实验设计任务的成功率都明显提高。",
            "反思模块显著降低了错误结论累积。",
            "检索与规划交替进行比一次性长规划更稳健。",
        ],
        "significance": "这类闭环代理是未来研究助手产品的重要基础设施。",
        "limitations": "目前主要验证于受控基准，真实开放科研环境仍需补充实验。",
        "comment": "适合持续跟进智能体系统可靠性方向。",
    },
    {
        "arxivId": "2603.15002v1",
        "title": "Sparse Preference Tuning for Long-Context Assistants",
        "authors": ["Daphne Koller", "Chelsea Finn"],
        "abstract": "This work studies sparse preference optimization for assistants operating over long context windows.",
        "categories": ["cs.CL", "cs.LG"],
        "arxivUrl": "https://arxiv.org/abs/2603.15002",
        "tldr": "稀疏偏好优化降低长上下文助手训练成本。",
        "publishedAt": "2026-03-15T18:20:00Z",
        "problem": "长上下文助手的偏好训练成本高，且容易因为数据冗余带来收益递减。",
        "methodology": "论文通过稀疏标注采样和分段式偏好更新，只在高价值片段上施加监督。",
        "keyFindings": [
            "训练 token 消耗显著下降。",
            "对有用性和一致性的保持优于简单下采样基线。",
            "长上下文窗口上的对齐稳定性更好。",
        ],
        "significance": "对想控制训练成本的产品团队非常实用。",
        "limitations": "仍依赖高质量偏好数据筛选器。",
        "comment": "对长上下文助手产品的训练预算很有参考价值。",
    },
    {
        "arxivId": "2603.15003v1",
        "title": "Compact Diffusion Distillation for Edge Image Generation",
        "authors": ["Ian Goodfellow", "Jitendra Malik"],
        "abstract": "We distill multi-step diffusion models into lightweight generators suitable for edge deployment.",
        "categories": ["cs.CV", "cs.LG"],
        "arxivUrl": "https://arxiv.org/abs/2603.15003",
        "tldr": "蒸馏扩散模型以支持边缘端图像生成。",
        "publishedAt": "2026-03-15T02:40:00Z",
        "problem": "多步扩散模型难以在低功耗设备上实时部署。",
        "methodology": "作者通过分阶段蒸馏把复杂扩散过程压缩为更轻量的生成器。",
        "keyFindings": [
            "在边缘设备上维持较高的视觉质量。",
            "推理时延显著缩短。",
            "小模型对常见图像类别保持较好鲁棒性。",
        ],
        "significance": "对端侧生成和低延迟视觉产品非常重要。",
        "limitations": "极复杂场景下仍有细节损失。",
        "comment": "端侧生成和低延迟视觉产品可以直接关注。",
    },
    {
        "arxivId": "2603.15004v1",
        "title": "Grounded Video Reasoning with Temporal Evidence Chains",
        "authors": ["Andrew Ng", "Serena Yeung"],
        "abstract": "The paper presents a grounded reasoning framework that links temporal evidence chains for video question answering.",
        "categories": ["cs.CV", "cs.AI"],
        "arxivUrl": "https://arxiv.org/abs/2603.15004",
        "tldr": "时间证据链提升视频理解与验证能力。",
        "publishedAt": "2026-03-14T23:30:00Z",
        "problem": "视频推理常常缺乏可回溯的时序证据，导致答案不稳定。",
        "methodology": "系统把视频拆分为关键事件节点，并显式追踪跨帧证据链来支持回答和验证。",
        "keyFindings": [
            "在视频问答和描述验证上都超过强基线。",
            "证据链约束显著改善了可解释性。",
            "长视频上的定位精度保持更稳定。",
        ],
        "significance": "适合需要可信视频分析的应用场景。",
        "limitations": "对事件切分质量仍有一定依赖。",
        "comment": "如果关注视频推理和证据可解释性，这篇值得补读。",
    },
    {
        "arxivId": "2603.15005v1",
        "title": "Retrieval-Efficient Memory Compression for Enterprise Agents",
        "authors": ["Mira Murati", "Percy Liang"],
        "abstract": "This paper studies memory compression strategies for enterprise copilots with persistent context.",
        "categories": ["cs.AI", "cs.IR"],
        "arxivUrl": "https://arxiv.org/abs/2603.15005",
        "tldr": "检索友好的记忆压缩提升企业级智能体吞吐。",
        "publishedAt": "2026-03-15T08:45:00Z",
        "problem": "企业级智能体需要长期记忆，但上下文膨胀会显著拖慢检索和响应。",
        "methodology": "论文结合语义聚类和任务导向压缩，把长期记忆压缩成分层索引。",
        "keyFindings": [
            "记忆占用显著下降。",
            "检索速度和召回率取得更平衡的结果。",
            "企业类任务中的多轮一致性更稳定。",
        ],
        "significance": "与研究助手和企业 Copilot 的长期记忆问题直接相关。",
        "limitations": "压缩阈值仍需针对领域调优。",
        "comment": "和研究助手、企业 Copilot 的长期记忆问题直接相关。",
    },
    {
        "arxivId": "2603.15006v1",
        "title": "Structured Memory Retrieval for Multimodal Research Assistants",
        "authors": ["Geoffrey Hinton", "Yoshua Bengio"],
        "abstract": "This paper introduces a structured memory retrieval scheme for multimodal assistants.",
        "categories": ["cs.IR", "cs.CV", "cs.CL"],
        "arxivUrl": "https://arxiv.org/abs/2603.15006",
        "tldr": "结构化记忆检索增强长文档多模态理解。",
        "publishedAt": "2026-03-15T00:25:00Z",
        "problem": "图表、正文和附录信息分散时，传统检索难以稳定建立证据链。",
        "methodology": "作者构建跨模态图结构，把文本片段、图像区域和表格条目统一编码后做局部图遍历。",
        "keyFindings": [
            "科研问答与证据定位精度明显提升。",
            "多跳检索中的语义漂移显著下降。",
            "图表引用更准确，可解释性更强。",
        ],
        "significance": "对多模态科研助手和视觉检索产品都很关键。",
        "limitations": "结构化预处理成本较高，对文档解析质量敏感。",
        "comment": "和科研助手、多模态搜索都直接相关。",
    },
    {
        "arxivId": "2603.15007v1",
        "title": "Efficient Multimodal Indexing for Open-World Visual Search",
        "authors": ["Alyosha Efros", "Li Fei-Fei"],
        "abstract": "We present a multimodal indexing stack for open-world visual search over web-scale corpora.",
        "categories": ["cs.CV", "cs.IR"],
        "arxivUrl": "https://arxiv.org/abs/2603.15007",
        "tldr": "开放世界视觉搜索的多模态索引方案。",
        "publishedAt": "2026-03-14T16:10:00Z",
        "problem": "开放世界视觉搜索需要同时处理图像、文本与场景上下文，传统索引难以兼顾速度和语义覆盖。",
        "methodology": "作者设计统一的多模态索引结构，在视觉特征和文本语义之间做分层路由。",
        "keyFindings": [
            "网页级语料上的检索吞吐更高。",
            "开放类别场景下召回率更稳定。",
            "模态路由减少了不必要的向量访问。",
        ],
        "significance": "非常贴近大规模视觉检索基础设施。",
        "limitations": "索引构建成本仍然偏高。",
        "comment": "和视觉检索基础设施直接相关，适合工程视角跟进。",
    },
    {
        "arxivId": "2603.15008v1",
        "title": "Adaptive Camera Agents for Warehouse Robotics",
        "authors": ["Pieter Abbeel", "Chelsea Finn"],
        "abstract": "The paper studies adaptive camera placement agents for warehouse robotics under sparse supervision.",
        "categories": ["cs.RO", "cs.CV", "cs.AI"],
        "arxivUrl": "https://arxiv.org/abs/2603.15008",
        "tldr": "自适应相机代理优化仓储机器人感知。",
        "publishedAt": "2026-03-13T12:05:00Z",
        "problem": "仓储机器人场景中，相机布局固定会造成盲区和重复采样。",
        "methodology": "作者让相机代理根据任务反馈动态调整视角和采样密度。",
        "keyFindings": [
            "遮挡环境下识别稳定性更好。",
            "相机资源利用率提升。",
            "稀疏监督下也能逐步收敛到更优策略。",
        ],
        "significance": "对视觉和机器人交叉场景有实际价值。",
        "limitations": "真实硬件部署仍需要补足安全约束。",
        "comment": "如果关注视觉与机器人交叉，这篇可作为潜力项。",
    },
]

BASE_THEMES: dict[str, dict[str, Any]] = {
    "editorial": {
        "themeName": "editorial",
        "fontPreset": "editorial",
        "layoutDensity": "balanced",
        "cardStyle": "panel",
        "heroPattern": "mesh",
        "borderRadius": "soft",
        "motionLevel": "calm",
        "palette": {
            "background": "#f4efe5",
            "foreground": "#18161a",
            "accent": "#b45309",
            "accentSoft": "#facc15",
            "surface": "#fffaf1",
            "surfaceAlt": "#efe3cf",
            "border": "#1f2937",
        },
    },
    "brutalist": {
        "themeName": "brutalist",
        "fontPreset": "modern",
        "layoutDensity": "compact",
        "cardStyle": "outline",
        "heroPattern": "rays",
        "borderRadius": "sharp",
        "motionLevel": "lively",
        "palette": {
            "background": "#f4f4f0",
            "foreground": "#111111",
            "accent": "#0047ff",
            "accentSoft": "#ffcc00",
            "surface": "#ffffff",
            "surfaceAlt": "#e7ebff",
            "border": "#111111",
        },
    },
    "terminal": {
        "themeName": "terminal",
        "fontPreset": "mono",
        "layoutDensity": "compact",
        "cardStyle": "outline",
        "heroPattern": "grid",
        "borderRadius": "sharp",
        "motionLevel": "calm",
        "palette": {
            "background": "#f2f6ef",
            "foreground": "#10220f",
            "accent": "#1b7f3b",
            "accentSoft": "#b9f6ca",
            "surface": "#fbfff7",
            "surfaceAlt": "#e3f2da",
            "border": "#10220f",
        },
    },
    "lumen": {
        "themeName": "lumen",
        "fontPreset": "modern",
        "layoutDensity": "airy",
        "cardStyle": "panel",
        "heroPattern": "mesh",
        "borderRadius": "round",
        "motionLevel": "lively",
        "palette": {
            "background": "#eef4ff",
            "foreground": "#10203a",
            "accent": "#0f62fe",
            "accentSoft": "#a7c8ff",
            "surface": "#ffffff",
            "surfaceAlt": "#dbeafe",
            "border": "#10203a",
        },
    },
}

CATEGORY_LABELS = {
    "cs.AI": "智能体系统",
    "cs.CV": "视觉推理",
    "cs.CL": "语言建模",
    "cs.IR": "检索系统",
    "cs.LG": "训练效率",
    "cs.RO": "机器人",
}

DEFAULT_SEARCH_EXPANSION_STEP_DAYS = 2
DEFAULT_SEARCH_MAX_EXPANSIONS = 1


def parse_utc_datetime(raw_value: str) -> datetime:
    return datetime.fromisoformat(raw_value.replace("Z", "+00:00")).astimezone(UTC)


def normalize_categories(raw_categories: Iterable[str]) -> list[str]:
    ordered: dict[str, None] = {}
    for category in raw_categories:
        cleaned = str(category).strip()
        if cleaned:
            ordered[cleaned] = None
    return list(ordered.keys()) or ["cs.AI"]


def resolve_search_expansion(delivery_profile: dict[str, Any] | None = None) -> tuple[int, int]:
    profile = delivery_profile or {}
    expansion_step_days = int(
        profile.get("search_expansion_days", DEFAULT_SEARCH_EXPANSION_STEP_DAYS),
    )
    max_search_expansions = int(
        profile.get("max_search_expansions", DEFAULT_SEARCH_MAX_EXPANSIONS),
    )
    return max(expansion_step_days, 1), max(max_search_expansions, 0)


def compute_search_lookback_days(
    lookback_days: int,
    expansion_step_days: int = DEFAULT_SEARCH_EXPANSION_STEP_DAYS,
    max_search_expansions: int = DEFAULT_SEARCH_MAX_EXPANSIONS,
) -> list[int]:
    base_lookback_days = max(int(lookback_days), 1)
    step_days = max(int(expansion_step_days), 1)
    expansions = max(int(max_search_expansions), 0)
    return [base_lookback_days + (attempt * step_days) for attempt in range(expansions + 1)]


def compute_catalog_lookback_days(
    lookback_days: int,
    expansion_step_days: int = DEFAULT_SEARCH_EXPANSION_STEP_DAYS,
    max_search_expansions: int = DEFAULT_SEARCH_MAX_EXPANSIONS,
) -> int:
    return max(
        max(compute_search_lookback_days(lookback_days, expansion_step_days, max_search_expansions)) + 1,
        2,
    )


def get_timezone(timezone_name: str | None) -> ZoneInfo:
    try:
        return ZoneInfo(timezone_name or "UTC")
    except ZoneInfoNotFoundError:
        return ZoneInfo("UTC")


def compute_next_run_at(
    timezone_name: str,
    delivery_local_time: time,
    now: datetime | None = None,
) -> datetime:
    now_utc = (now or datetime.now(UTC)).astimezone(UTC)
    user_timezone = get_timezone(timezone_name)
    local_now = now_utc.astimezone(user_timezone)
    scheduled_local = local_now.replace(
        hour=delivery_local_time.hour,
        minute=delivery_local_time.minute,
        second=0,
        microsecond=0,
    )
    if scheduled_local <= local_now:
        scheduled_local += timedelta(days=1)
    return scheduled_local.astimezone(UTC)


def hour_in_window(hour: int, start_hour: int, end_hour: int) -> bool:
    if start_hour == 0 and end_hour == 24:
        return True
    if start_hour == end_hour:
        return True
    if end_hour == 24:
        return hour >= start_hour
    if start_hour < end_hour:
        return start_hour <= hour < end_hour
    return hour >= start_hour or hour < end_hour


def compile_theme_prompt(prompt_text: str) -> dict[str, Any]:
    normalized_prompt = prompt_text.lower()
    theme_key = "editorial"

    theme_keywords = {
        "brutalist": "brutalist",
        "sharp": "brutalist",
        "terminal": "terminal",
        "mono": "terminal",
        "luminous": "lumen",
        "neon": "lumen",
        "editorial": "editorial",
        "magazine": "editorial",
    }

    for keyword, candidate in theme_keywords.items():
        if keyword in normalized_prompt:
            theme_key = candidate
            break

    tokens = deepcopy(BASE_THEMES[theme_key])

    if "warm" in normalized_prompt:
        tokens["palette"]["background"] = "#f6ede0"
        tokens["palette"]["surfaceAlt"] = "#f2dfc5"
        tokens["palette"]["accent"] = "#c2410c"

    if "cool" in normalized_prompt or "cobalt" in normalized_prompt:
        tokens["palette"]["accent"] = "#1d4ed8"
        tokens["palette"]["accentSoft"] = "#bfdbfe"

    if "rounded" in normalized_prompt or "soft" in normalized_prompt:
        tokens["borderRadius"] = "round"
    elif "sharp" in normalized_prompt:
        tokens["borderRadius"] = "sharp"

    if "compact" in normalized_prompt or "dense" in normalized_prompt:
        tokens["layoutDensity"] = "compact"
    elif "airy" in normalized_prompt or "spacious" in normalized_prompt:
        tokens["layoutDensity"] = "airy"

    if "calm" in normalized_prompt:
        tokens["motionLevel"] = "calm"
    elif "lively" in normalized_prompt or "bold" in normalized_prompt:
        tokens["motionLevel"] = "lively"

    if "grid" in normalized_prompt:
        tokens["heroPattern"] = "grid"
    elif "rays" in normalized_prompt:
        tokens["heroPattern"] = "rays"

    if "mono" in normalized_prompt or "terminal" in normalized_prompt:
        tokens["fontPreset"] = "mono"
    elif "serif" in normalized_prompt or "editorial" in normalized_prompt:
        tokens["fontPreset"] = "editorial"
    elif "sans" in normalized_prompt or "modern" in normalized_prompt:
        tokens["fontPreset"] = "modern"

    if "outline" in normalized_prompt:
        tokens["cardStyle"] = "outline"
    elif "pill" in normalized_prompt:
        tokens["cardStyle"] = "pill"

    return tokens


def _to_highlight(paper: dict[str, Any]) -> dict[str, Any]:
    return {
        "arxivId": paper["arxivId"],
        "title": paper["title"],
        "authors": paper["authors"],
        "abstract": paper["abstract"],
        "categories": paper["categories"],
        "arxivUrl": paper["arxivUrl"],
        "tldr": paper["tldr"],
        "problem": paper["problem"],
        "methodology": paper["methodology"],
        "keyFindings": paper["keyFindings"],
        "significance": paper["significance"],
        "limitations": paper["limitations"],
    }


def _to_notable(paper: dict[str, Any]) -> dict[str, Any]:
    return {
        "arxivId": paper["arxivId"],
        "title": paper["title"],
        "authors": paper["authors"],
        "abstract": paper["abstract"],
        "categories": paper["categories"],
        "arxivUrl": paper["arxivUrl"],
        "tldr": paper["tldr"],
        "comment": paper["comment"],
    }


def _category_tags(categories: list[str]) -> list[str]:
    return [CATEGORY_LABELS.get(category, category) for category in categories[:4]]


def _truncate_text(text: str, limit: int = 88) -> str:
    cleaned = " ".join(text.split())
    if len(cleaned) <= limit:
        return cleaned
    return f"{cleaned[: limit - 1].rstrip()}..."


def _metadata_tldr(abstract: str) -> str:
    first_sentence = abstract.split(".")[0].strip()
    if not first_sentence:
        return "当前只抓取到元数据，建议进一步查看原始摘要。"
    return _truncate_text(first_sentence, limit=32)


def _normalize_catalog_paper(paper: dict[str, Any]) -> dict[str, Any]:
    if "problem" in paper and "methodology" in paper:
        return paper

    categories = list(paper.get("categories", []))
    abstract = str(paper.get("abstract", "")).strip()
    title = str(paper.get("title", "Untitled Paper"))
    tldr = paper.get("tldr") or _metadata_tldr(abstract or title)
    category_text = "、".join(_category_tags(categories)) or "AI 研究"
    published_at = str(paper.get("publishedAt", ""))

    return {
        "arxivId": paper["arxivId"],
        "title": title,
        "authors": list(paper.get("authors", [])),
        "abstract": abstract,
        "categories": categories,
        "arxivUrl": paper["arxivUrl"],
        "tldr": tldr,
        "publishedAt": published_at,
        "problem": f"这篇论文面向 {category_text} 场景。当前系统仅基于 arXiv 摘要推断其核心问题为：{_truncate_text(abstract, 96)}",
        "methodology": "当前版本尚未下载全文，方法描述来自摘要级元数据归纳。建议把进入 highlights 的论文再触发 PDF/TXT 深读流程。",
        "keyFindings": [
            "这是一条基于 arXiv 元数据的自动候选信号。",
            "系统已按用户的分类和发表时间窗完成筛选。",
            "若要得到可靠结论，应继续下载全文并补充深读摘要。",
        ],
        "significance": f"该论文当前被纳入 {category_text} 方向的候选列表，适合作为每日扫描的优先阅读项。",
        "limitations": "当前仅抓取元数据与摘要，未对全文实验细节做核验。",
        "comment": f"摘要级信号显示它与 {category_text} 方向相关，适合加入当日关注列表。",
    }


def catalog_row_to_paper(row: dict[str, Any]) -> dict[str, Any]:
    return _normalize_catalog_paper(
        {
            "arxivId": row["arxiv_id"],
            "title": row["title"],
            "authors": list(row["authors_json"]),
            "abstract": row["abstract"],
            "categories": list(row["categories_json"]),
            "arxivUrl": row["arxiv_url"],
            "publishedAt": row["published_at"].isoformat(),
        }
    )


def _paper_matches_categories(paper_categories: list[str], selected_categories: set[str]) -> bool:
    return bool(set(paper_categories) & selected_categories)


def _pick_candidates(
    categories: list[str],
    timezone_name: str,
    window_start_hour: int,
    window_end_hour: int,
    lookback_days: int,
    reference_time: datetime,
    paper_catalog: list[dict[str, Any]] | None = None,
    expansion_step_days: int = DEFAULT_SEARCH_EXPANSION_STEP_DAYS,
    max_search_expansions: int = DEFAULT_SEARCH_MAX_EXPANSIONS,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    selected_categories = set(categories)
    user_timezone = get_timezone(timezone_name)
    local_reference = reference_time.astimezone(user_timezone)
    source_papers = paper_catalog if paper_catalog is not None else FALLBACK_PAPERS
    search_windows = compute_search_lookback_days(
        lookback_days,
        expansion_step_days=expansion_step_days,
        max_search_expansions=max_search_expansions,
    )

    matching_papers: list[tuple[dict[str, Any], datetime]] = []

    for raw_paper in source_papers:
        paper = _normalize_catalog_paper(raw_paper)
        if not _paper_matches_categories(paper["categories"], selected_categories):
            continue

        published_utc = parse_utc_datetime(paper["publishedAt"])
        published_local = published_utc.astimezone(user_timezone)
        matching_papers.append((paper, published_local))

    matching_papers.sort(key=lambda item: item[0]["publishedAt"], reverse=True)
    search_attempts: list[dict[str, Any]] = []

    for attempt, current_lookback_days in enumerate(search_windows, start=1):
        lookback_start = local_reference - timedelta(days=current_lookback_days)
        strict_candidates: list[dict[str, Any]] = []
        relaxed_candidates: list[dict[str, Any]] = []

        for paper, published_local in matching_papers:
            if published_local < lookback_start:
                continue

            relaxed_candidates.append(paper)
            if hour_in_window(published_local.hour, window_start_hour, window_end_hour):
                strict_candidates.append(paper)

        search_attempts.append(
            {
                "attempt": attempt,
                "lookbackDays": current_lookback_days,
                "strictMatches": len(strict_candidates),
                "relaxedMatches": len(relaxed_candidates),
            }
        )

        if strict_candidates:
            return strict_candidates, {
                "requestedLookbackDays": lookback_days,
                "effectiveLookbackDays": current_lookback_days,
                "searchExpanded": current_lookback_days != lookback_days,
                "searchAttempts": search_attempts,
                "matchedTimeWindow": True,
                "searchMode": "time_window",
                "usedCategoryFallback": False,
            }

        if relaxed_candidates:
            return relaxed_candidates, {
                "requestedLookbackDays": lookback_days,
                "effectiveLookbackDays": current_lookback_days,
                "searchExpanded": current_lookback_days != lookback_days,
                "searchAttempts": search_attempts,
                "matchedTimeWindow": False,
                "searchMode": "lookback_only",
                "usedCategoryFallback": False,
            }

    category_fallback = [paper for paper, _published_local in matching_papers]
    return category_fallback, {
        "requestedLookbackDays": lookback_days,
        "effectiveLookbackDays": search_windows[-1] if search_windows else lookback_days,
        "searchExpanded": len(search_windows) > 1,
        "searchAttempts": search_attempts,
        "matchedTimeWindow": False,
        "searchMode": "category_only" if category_fallback else "empty",
        "usedCategoryFallback": bool(category_fallback),
    }


def build_personalized_report(
    user: dict[str, Any],
    delivery_profile: dict[str, Any],
    theme_profile: dict[str, Any] | None,
    now: datetime | None = None,
    paper_catalog: list[dict[str, Any]] | None = None,
    crawl_meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    reference_time = (now or datetime.now(UTC)).astimezone(UTC)
    categories = normalize_categories(delivery_profile.get("categories_json", ["cs.AI"]))
    timezone_name = str(user.get("timezone") or "UTC")
    window_start_hour = int(delivery_profile.get("window_start_hour", 0))
    window_end_hour = int(delivery_profile.get("window_end_hour", 24))
    lookback_days = int(delivery_profile.get("lookback_days", 1))
    expansion_step_days, max_search_expansions = resolve_search_expansion(delivery_profile)

    theme_tokens = (
        deepcopy(theme_profile["tokens_json"])
        if theme_profile and theme_profile.get("tokens_json")
        else compile_theme_prompt(str(theme_profile.get("prompt_text", "")) if theme_profile else "")
    )
    candidates, search_meta = _pick_candidates(
        categories=categories,
        timezone_name=timezone_name,
        window_start_hour=window_start_hour,
        window_end_hour=window_end_hour,
        lookback_days=lookback_days,
        reference_time=reference_time,
        paper_catalog=paper_catalog,
        expansion_step_days=expansion_step_days,
        max_search_expansions=max_search_expansions,
    )

    highlights = [_to_highlight(paper) for paper in candidates[:2]]
    notables = [_to_notable(paper) for paper in candidates[2:5]]
    if not notables and len(candidates) > 2:
        notables = [_to_notable(paper) for paper in candidates[2:]]

    report_date = reference_time.astimezone(get_timezone(timezone_name)).date()
    display_name = str(user.get("display_name") or user.get("handle") or "用户")
    effective_lookback_days = int(search_meta["effectiveLookbackDays"])
    if search_meta["searchExpanded"]:
        search_scope_text = (
            f"原始 {lookback_days} 天范围未命中后，系统自动扩展到 {effective_lookback_days} 天完成二次搜寻"
        )
    else:
        search_scope_text = f"{lookback_days} 天回看范围"

    if candidates:
        summary = (
            f"系统在用户投送时间到达后自动抓取最新论文，并按 {timezone_name} 时区、{search_scope_text}，以及 "
            f"{window_start_hour:02d}:00-{window_end_hour:02d}:00 的论文发表时间窗口筛出 "
            f"{len(candidates)} 篇候选论文。当前优先关注 {', '.join(categories[:3])}，"
            "并将主题风格同步应用到个人工作台。"
        )
    else:
        summary = (
            f"系统在用户投送时间到达后自动抓取并按 {timezone_name} 时区、{search_scope_text} 完成检索，但当前仍未找到匹配 "
            f"{', '.join(categories[:3])} 的论文。建议继续扩大分类范围或等待下一轮同步。"
        )
    trends = (
        f"当前候选论文集中在 {', '.join(_category_tags(categories))}。"
        "整体信号显示，研究工作正在从单点模型效果，转向更强调系统协同、检索组织和部署效率。"
    )

    return {
        "date": report_date,
        "title": f"{display_name} 的个性化 AI 晨报",
        "summary": summary,
        "totalPapers": len(candidates),
        "tags": _category_tags(categories),
        "trends": trends,
        "highlights": highlights,
        "notables": notables,
        "themeTokens": theme_tokens,
        "sourceMeta": {
            "generatedAt": reference_time.isoformat(),
            "timezone": timezone_name,
            "categories": categories,
            "windowStartHour": window_start_hour,
            "windowEndHour": window_end_hour,
            "lookbackDays": lookback_days,
            "effectiveLookbackDays": effective_lookback_days,
            "searchExpanded": search_meta["searchExpanded"],
            "searchAttempts": search_meta["searchAttempts"],
            "matchedTimeWindow": search_meta["matchedTimeWindow"],
            "searchMode": search_meta["searchMode"],
            "usedCategoryFallback": search_meta["usedCategoryFallback"],
            "searchExpansionStepDays": expansion_step_days,
            "maxSearchExpansions": max_search_expansions,
            "selectedPaperIds": [paper["arxivId"] for paper in candidates],
            "paperSource": "database" if paper_catalog is not None else "fallback",
            "crawlMeta": crawl_meta or {},
        },
    }


def default_delivery_profile(user_id: str, timezone_name: str) -> dict[str, Any]:
    next_run_at = compute_next_run_at(timezone_name, time(hour=8, minute=0))
    return {
        "user_id": user_id,
        "delivery_enabled": True,
        "delivery_local_time": time(hour=8, minute=0),
        "window_start_hour": 0,
        "window_end_hour": 24,
        "lookback_days": 1,
        "categories_json": ["cs.AI"],
        "next_run_at": next_run_at,
    }


def default_theme_profile(user_id: str) -> dict[str, Any]:
    tokens = compile_theme_prompt("")
    return {
        "user_id": user_id,
        "prompt_text": "",
        "theme_name": tokens["themeName"],
        "tokens_json": tokens,
    }
