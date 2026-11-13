"""
启动 Neo4j 服务器并打开浏览器

使用方法：直接运行，按 Ctrl+C 停止服务器
"""

import subprocess
import webbrowser
import time
import os


def main():
    # ========================================
    # ========== 在这里修改配置 ==========
    # ========================================

    neo4j_bin = r"J:\LLM\neo4j-community-5.25.1\bin\neo4j.bat"
    browser_url = "http://localhost:7474"

    # ========================================

    print("Starting Neo4j...")
    print(f"Neo4j path: {neo4j_bin}")
    print(f"Browser: {browser_url}")
    print("Press Ctrl+C to stop.\n")

    # 启动 Neo4j console 模式
    process = subprocess.Popen(
        [neo4j_bin, "console"],
        cwd=os.path.dirname(neo4j_bin),
    )

    # 等几秒让服务启动，然后打开浏览器
    time.sleep(8)
    webbrowser.open(browser_url)

    try:
        process.wait()
    except KeyboardInterrupt:
        print("\nStopping Neo4j...")
        process.terminate()
        process.wait()
        print("Neo4j stopped.")


if __name__ == "__main__":
    main()