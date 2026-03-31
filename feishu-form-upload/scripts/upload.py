#!/usr/bin/env python3
"""
飞书表单图片上传脚本（Playwright connect_over_cdp 方法）
用法：python3 feishu_upload.py <文件路径> <表单URL关键词>
示例：python3 feishu_upload.py /tmp/openclaw/uploads/checkin-20260331.jpg shrcnRMkIRAcx9Gbo8jKd05OObe
"""
import asyncio
import os
import sys

# 动态查找 playwright，兼容不同 Python 版本和安装路径
try:
    from playwright.async_api import async_playwright
except ImportError:
    import subprocess, site
    paths = site.getsitepackages() + [site.getusersitepackages()]
    for p in paths:
        sys.path.insert(0, p)
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print('❌ playwright 未安装，请执行: pip3 install playwright')
        sys.exit(1)


async def main(file_path: str, page_url_keyword: str) -> bool:
    # 文件存在性校验
    if not os.path.isfile(file_path):
        print(f'❌ 文件不存在: {file_path}')
        return False

    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')

        target_page = None
        for context in browser.contexts:
            for page in context.pages:
                if page_url_keyword in page.url:
                    target_page = page
                    break

        if not target_page:
            print(f'❌ 未找到包含 "{page_url_keyword}" 的页面')
            print('当前已打开的页面：')
            for context in browser.contexts:
                for page in context.pages:
                    print(f'  - {page.url}')
            await browser.close()
            return False

        print(f'✅ 找到目标页面: {target_page.url[:80]}')
        await target_page.wait_for_load_state('networkidle', timeout=10000)

        file_input = target_page.locator('input[type=file]')
        count = await file_input.count()
        print(f'找到 input[type=file]: {count} 个')

        if count == 0:
            print('❌ 页面上没有文件上传 input')
            await browser.close()
            return False

        await file_input.set_input_files(file_path)
        print(f'✅ 上传完成: {file_path}')
        await asyncio.sleep(4)
        await browser.close()
        return True


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('用法: python3 feishu_upload.py <文件路径> <表单URL关键词>')
        sys.exit(1)
    ok = asyncio.run(main(sys.argv[1], sys.argv[2]))
    sys.exit(0 if ok else 1)
