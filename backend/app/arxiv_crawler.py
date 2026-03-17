from __future__ import annotations

import math
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import date, datetime
from typing import Any, Callable

API_URL = "http://export.arxiv.org/api/query"
ATOM_NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "opensearch": "http://a9.com/-/spec/opensearch/1.1/",
}


def normalize_text(text: str | None) -> str:
    return " ".join((text or "").split())


def print_progress(current: int, total: int, prefix: str, detail: str = "") -> None:
    total = max(total, 1)
    current = min(max(current, 0), total)
    width = 30
    filled = int(width * current / total)
    bar = "#" * filled + "-" * (width - filled)
    line = f"\r{prefix} [{bar}] {current}/{total}"
    if detail:
        line += f" | {detail}"
    print(line, end="", flush=True)
    if current >= total:
        print("", flush=True)


def parse_total_results(root: ET.Element) -> int:
    text = root.findtext("opensearch:totalResults", default="0", namespaces=ATOM_NS)
    try:
        return int(text)
    except ValueError:
        return 0


def parse_entry(entry: ET.Element) -> dict[str, Any]:
    arxiv_url = normalize_text(entry.findtext("atom:id", default="", namespaces=ATOM_NS))
    published_raw = normalize_text(entry.findtext("atom:published", default="", namespaces=ATOM_NS))
    published_date = published_raw[:10] if published_raw else ""
    title = normalize_text(entry.findtext("atom:title", default="", namespaces=ATOM_NS))
    abstract = normalize_text(entry.findtext("atom:summary", default="", namespaces=ATOM_NS))
    authors = [
        normalize_text(author.findtext("atom:name", default="", namespaces=ATOM_NS))
        for author in entry.findall("atom:author", ATOM_NS)
        if normalize_text(author.findtext("atom:name", default="", namespaces=ATOM_NS))
    ]
    categories = list(
        dict.fromkeys(
            category.attrib.get("term", "").strip()
            for category in entry.findall("atom:category", ATOM_NS)
            if category.attrib.get("term", "").strip()
        )
    )

    alternate_url = ""
    for link in entry.findall("atom:link", ATOM_NS):
        if link.attrib.get("rel") == "alternate":
            alternate_url = link.attrib.get("href", "").strip()
            if alternate_url:
                break

    return {
        "arxiv_id": arxiv_url.rsplit("/", maxsplit=1)[-1],
        "title": title,
        "authors": authors,
        "abstract": abstract,
        "published": published_date,
        "published_at": published_raw,
        "categories": categories,
        "arxiv_url": alternate_url or arxiv_url,
        "pdf_path": "",
        "txt_path": "",
    }


def fetch_text(url: str, timeout: int, retries: int) -> str:
    headers = {"User-Agent": "arxiv-homework/1.0 (mailto:student@example.com)"}
    request = urllib.request.Request(url, headers=headers)
    last_error: Exception | None = None

    for attempt in range(1, retries + 1):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            last_error = exc
            if attempt < retries:
                retry_after = exc.headers.get("Retry-After") if exc.headers else None
                if retry_after and retry_after.isdigit():
                    sleep_seconds = max(int(retry_after), 1)
                elif exc.code == 429:
                    sleep_seconds = 60 * attempt
                    print(f"\n触发 arXiv 限流（HTTP 429），等待 {sleep_seconds} 秒后重试...", flush=True)
                else:
                    sleep_seconds = min(2**attempt, 5)
                time.sleep(sleep_seconds)
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            if attempt < retries:
                time.sleep(min(2**attempt, 5))

    assert last_error is not None
    raise last_error


def build_query(category: str, start_day: date, end_day: date) -> str:
    start_token = start_day.strftime("%Y%m%d") + "0000"
    end_token = end_day.strftime("%Y%m%d") + "2359"
    return f"cat:{category} AND submittedDate:[{start_token} TO {end_token}]"


def fetch_records_for_query(
    query: str,
    limit: int,
    page_size: int,
    timeout: int,
    retries: int,
    request_interval: float,
    fetcher: Callable[[str, int, int], str] = fetch_text,
) -> list[dict[str, Any]]:
    start_index = 0
    all_records: list[dict[str, Any]] = []
    total_results: int | None = None
    total_pages: int | None = None

    while len(all_records) < limit and (total_results is None or start_index < min(total_results, limit)):
        params = {
            "search_query": query,
            "start": start_index,
            "max_results": min(page_size, limit - len(all_records)),
            "sortBy": "submittedDate",
            "sortOrder": "descending",
        }
        url = API_URL + "?" + urllib.parse.urlencode(params)
        xml_text = fetcher(url, timeout, retries)
        root = ET.fromstring(xml_text)
        page_records = [parse_entry(entry) for entry in root.findall("atom:entry", ATOM_NS)]

        if total_results is None:
            total_results = parse_total_results(root)
            bounded_total = min(total_results, limit)
            total_pages = max(math.ceil(bounded_total / page_size), 1)

        if not page_records:
            break

        all_records.extend(page_records)
        start_index += len(page_records)

        if total_pages is not None:
            current_page = min(math.ceil(start_index / page_size), total_pages)
            print_progress(
                current_page,
                total_pages,
                "元数据抓取进度",
                f"已获取记录 {min(len(all_records), limit)}/{min(total_results or limit, limit)}",
            )

        if len(page_records) < page_size:
            break

        if request_interval > 0 and len(all_records) < limit:
            time.sleep(request_interval)

    if total_pages is None:
        print_progress(1, 1, "元数据抓取进度", f"已获取记录 {len(all_records)}/{limit}")

    return all_records[:limit]


def sort_key(record: dict[str, Any]) -> tuple[datetime, str]:
    published_raw = record.get("published_at") or record["published"]
    if "T" in published_raw:
        published = datetime.fromisoformat(published_raw.replace("Z", "+00:00"))
    else:
        published = datetime.strptime(record["published"], "%Y-%m-%d")
    return published, record["arxiv_id"]


def deduplicate_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    unique: dict[str, dict[str, Any]] = {}
    for record in records:
        unique[record["arxiv_id"]] = record
    return list(unique.values())


def collect_records(
    start_date: str,
    end_date: str,
    limit: int,
    category: str,
    workers: int,
    page_size: int,
    timeout: int,
    retries: int,
    request_interval: float,
) -> list[dict[str, Any]]:
    del workers
    start_day = datetime.strptime(start_date, "%Y-%m-%d").date()
    end_day = datetime.strptime(end_date, "%Y-%m-%d").date()
    if end_day < start_day:
        raise ValueError("结束日期不能早于开始日期。")

    print(
        f"开始抓取分类 {category}，日期范围 {start_date} 到 {end_date}，按提交日期倒序分页抓取。",
        flush=True,
    )
    query = build_query(category, start_day, end_day)
    all_records = fetch_records_for_query(
        query=query,
        limit=limit,
        page_size=page_size,
        timeout=timeout,
        retries=retries,
        request_interval=request_interval,
    )

    unique_records = deduplicate_records(all_records)
    unique_records.sort(key=sort_key, reverse=True)
    limited_records = unique_records[:limit]

    print(f"抓取完成：原始记录 {len(all_records)} 篇，去重后 {len(unique_records)} 篇，输出 {len(limited_records)} 篇。")
    if len(limited_records) < limit:
        print(f"警告：在指定日期范围内仅找到 {len(limited_records)} 篇论文，少于目标 {limit} 篇。")
    return limited_records
