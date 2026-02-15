#!/usr/bin/env python
"""
小红书快捷搜索脚本
用法：python search_xhs.py "关键词" [数量]
示例：python search_xhs.py "眼镜" 10
"""
import sys
import os

def main():
    # 解析命令行参数
    if len(sys.argv) < 2:
        print("用法：python search_xhs.py \"关键词\" [数量]")
        print("示例：python search_xhs.py \"眼镜\" 10")
        print("      python search_xhs.py \"眼镜,墨镜\" 20")
        sys.exit(1)
    
    keyword = sys.argv[1]
    count = sys.argv[2] if len(sys.argv) > 2 else "10"
    
    # 设置环境变量
    os.environ["KEYWORDS"] = keyword
    os.environ["TARGET_COUNT"] = count
    
    print(f"[小红书搜索]")
    print(f"   关键词: {keyword}")
    print(f"   数量: {count}")
    print("-" * 40)
    
    # 导入并运行爬虫
    from crawler_v4 import main as crawler_main
    crawler_main()


if __name__ == "__main__":
    main()

