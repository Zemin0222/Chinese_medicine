"""爬取百度首页的入门 demo。

功能：
1. 使用 requests 发送 GET 请求（带浏览器 UA，避免被直接拒绝）
2. 校验响应状态码与编码
3. 把原始 HTML 保存到本地，方便查看
4. 使用 BeautifulSoup 解析标题、meta 描述、页面链接等基础信息
"""

from pathlib import Path

import requests
from bs4 import BeautifulSoup

BAIDU_URL = "https://www.baidu.com"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9",
}

# 输出目录：与当前脚本同级
OUTPUT_DIR = Path(__file__).parent / "output"


def fetch_html(url: str = BAIDU_URL, timeout: int = 10) -> str:
    """请求页面并返回 HTML 文本。"""
    response = requests.get(url, headers=HEADERS, timeout=timeout)
    response.raise_for_status()  # 状态码非 2xx 时抛出异常

    # 百度返回的是 utf-8，requests 有时会误判成 ISO-8859-1
    if not response.encoding or response.encoding.lower() == "iso-8859-1":
        response.encoding = response.apparent_encoding or "utf-8"

    return response.text


def save_html(html: str, filename: str = "baidu.html") -> Path:
    """把 HTML 保存到 output 目录，返回文件路径。"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    file_path = OUTPUT_DIR / filename
    file_path.write_text(html, encoding="utf-8")
    return file_path


def parse_html(html: str) -> dict:
    """解析页面，提取标题、描述和链接。"""
    soup = BeautifulSoup(html, "html.parser")

    title = soup.title.get_text(strip=True) if soup.title else ""
    description_tag = soup.find("meta", attrs={"name": "description"})
    description = description_tag.get("content", "") if description_tag else ""

    links = []
    for a in soup.find_all("a", href=True):
        text = a.get_text(strip=True)
        if text:
            links.append((text, a["href"]))

    return {
        "title": title,
        "description": description,
        "links": links,
    }


def main() -> None:
    print(f"开始爬取：{BAIDU_URL}")

    html = fetch_html()

    file_path = save_html(html)
    print(f"HTML 已保存：{file_path}（{len(html)} 字符）")

    if "百度安全验证" in html:
        print("警告：页面出现“百度安全验证”，说明触发了反爬，可尝试更换 UA 或加 Cookie")
        return

    data = parse_html(html)
    print(f"页面标题：{data['title']}")
    print(f"页面描述：{data['description']}")
    print(f"链接数量：{len(data['links'])}")

    print("\n前 10 个链接：")
    for index, (text, href) in enumerate(data["links"][:10], start=1):
        print(f"{index:>2}. {text} -> {href}")


if __name__ == "__main__":
    main()
