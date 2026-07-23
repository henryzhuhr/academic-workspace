#!/usr/bin/env python3
"""Search arXiv and save reproducible metadata records.

This script uses the official arXiv Atom API. It deliberately does not
download PDFs; selected papers can be downloaded and archived separately with
``uv run scripts/workspace.py paper add``.
"""

import argparse
import datetime as dt
import json
import re
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET


API_URL = "https://export.arxiv.org/api/query"
ATOM_NS = "{http://www.w3.org/2005/Atom}"
ARXIV_NS = "{http://arxiv.org/schemas/atom}"
ARXIV_ID_RE = re.compile(r"(?:abs|pdf)/(.+?)(?:\.pdf)?$")
VERSION_RE = re.compile(r"^(?P<base>.+?)(?P<version>v\d+)$", re.I)


def element_text(parent: ET.Element, name: str) -> str:
    value = parent.findtext(ATOM_NS + name, default="")
    return " ".join(value.split())


def parse_arxiv_id(url_or_id: str) -> Dict[str, str]:
    value = url_or_id.strip()
    match = ARXIV_ID_RE.search(value)
    if match:
        value = match.group(1)
    value = value.rstrip("/")
    version_match = VERSION_RE.match(value)
    if version_match:
        return {
            "arxiv_id": version_match.group("base"),
            "version": version_match.group("version").lower(),
        }
    return {"arxiv_id": value, "version": ""}


def parse_feed(payload: bytes) -> Dict[str, object]:
    root = ET.fromstring(payload)
    total = root.findtext(
        "{" + "http://a9.com/-/spec/opensearch/1.1/" + "}totalResults",
        default="0",
    )
    results: List[Dict[str, object]] = []
    for entry in root.findall(ATOM_NS + "entry"):
        raw_id = element_text(entry, "id")
        identifiers = parse_arxiv_id(raw_id)
        links = []
        for link in entry.findall(ATOM_NS + "link"):
            href = link.attrib.get("href", "")
            if href:
                links.append(
                    {
                        "url": href,
                        "rel": link.attrib.get("rel", ""),
                        "type": link.attrib.get("type", ""),
                    }
                )
        pdf_url = next(
            (link["url"] for link in links if link["type"] == "application/pdf"),
            "https://arxiv.org/pdf/{}".format(
                identifiers["arxiv_id"] + identifiers["version"]
            ),
        )
        authors = [
            " ".join(author_text.split())
            for author_text in (
                author.findtext(ATOM_NS + "name", default="")
                for author in entry.findall(ATOM_NS + "author")
            )
            if author_text.strip()
        ]
        categories = [
            category.attrib["term"]
            for category in entry.findall(ATOM_NS + "category")
            if category.attrib.get("term")
        ]
        results.append(
            {
                **identifiers,
                "title": element_text(entry, "title"),
                "authors": authors,
                "summary": element_text(entry, "summary"),
                "published": element_text(entry, "published"),
                "updated": element_text(entry, "updated"),
                "categories": categories,
                "abstract_url": "https://arxiv.org/abs/{}".format(
                    identifiers["arxiv_id"] + identifiers["version"]
                ),
                "pdf_url": pdf_url,
                "links": links,
            }
        )
    return {"total_results": int(total or 0), "results": results}


def build_query(args: argparse.Namespace) -> str:
    if args.query:
        return args.query
    clauses: List[str] = []
    for value in args.all_terms:
        clauses.append("all:{}".format(value))
    for value in args.title:
        clauses.append("ti:{}".format(value))
    for value in args.author:
        clauses.append("au:{}".format(value))
    for value in args.abstract:
        clauses.append("abs:{}".format(value))
    for value in args.category:
        clauses.append("cat:{}".format(value))
    if not clauses:
        raise ValueError("请提供查询字符串，或使用 --all/--title/--author/--abstract/--category")
    return " AND ".join(clauses)


def fetch_page(parameters: Dict[str, object], timeout: int) -> Dict[str, object]:
    url = API_URL + "?" + urlencode(parameters)
    request = Request(url, headers={"User-Agent": "academic-workspace/arxiv-search/1.0"})
    try:
        with urlopen(request, timeout=timeout) as response:
            return parse_feed(response.read())
    except (HTTPError, URLError, ET.ParseError) as exc:
        raise RuntimeError("arXiv API 请求失败：{}".format(exc)) from exc


def search(args: argparse.Namespace) -> Dict[str, object]:
    query = build_query(args)
    pages: List[Dict[str, object]] = []
    remaining = args.limit
    start = args.start
    while remaining > 0:
        page_size = min(remaining, 2000)
        parameters = {
            "search_query": query,
            "start": start,
            "max_results": page_size,
            "sortBy": args.sort_by,
            "sortOrder": args.sort_order,
        }
        if pages:
            time.sleep(args.delay)
        page = fetch_page(parameters, args.timeout)
        pages.append(page)
        returned = len(page["results"])
        remaining -= returned
        start += returned
        if returned < page_size:
            break

    results: List[Dict[str, object]] = []
    for page in pages:
        results.extend(page["results"])
    return {
        "schema_version": 1,
        "source": API_URL,
        "searched_at": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        "query": query,
        "parameters": {
            "start": args.start,
            "max_results": args.limit,
            "sort_by": args.sort_by,
            "sort_order": args.sort_order,
        },
        "total_results": pages[0]["total_results"] if pages else 0,
        "results": results,
    }


def write_output(record: Dict[str, object], output: Optional[Path]) -> None:
    text = json.dumps(record, ensure_ascii=False, indent=2) + "\n"
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text, encoding="utf-8")
        print("已保存检索记录：{}".format(output))
    else:
        print(text, end="")


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="使用 arXiv 官方 API 搜索论文并保存 JSON 元数据")
    parser.add_argument("query", nargs="?", help="原始 arXiv search_query；与字段选项二选一")
    parser.add_argument("--all", dest="all_terms", action="append", default=[], help="追加 all: 条件")
    parser.add_argument("--title", action="append", default=[], help="追加 ti: 条件")
    parser.add_argument("--author", action="append", default=[], help="追加 au: 条件")
    parser.add_argument("--abstract", action="append", default=[], help="追加 abs: 条件")
    parser.add_argument("--category", action="append", default=[], help="追加 cat: 条件")
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--sort-by", choices=("relevance", "lastUpdatedDate", "submittedDate"), default="relevance")
    parser.add_argument("--sort-order", choices=("ascending", "descending"), default="descending")
    parser.add_argument("--delay", type=float, default=3.0, help="分页请求间隔（秒，默认 3）")
    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument("--output", type=Path, help="保存 JSON 检索记录的路径")
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    args = make_parser().parse_args(argv)
    if args.start < 0 or args.limit < 1 or args.limit > 30000 or args.delay < 0:
        print("start、limit 或 delay 参数无效", file=sys.stderr)
        return 2
    try:
        record = search(args)
        write_output(record, args.output)
    except (RuntimeError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
