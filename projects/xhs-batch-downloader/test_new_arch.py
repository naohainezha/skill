"""
测试新架构的脚本
"""
import asyncio
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from xhs_client import xhs_client, SignServerError


async def test_login():
    """测试登录流程"""
    print("=" * 50)
    print("测试登录流程")
    print("=" * 50)
    
    # 检查签名服务
    if xhs_client.check_sign_server():
        print("[OK] 签名服务已配置")
    else:
        print("[INFO] 签名服务未配置，需要首次登录")
    
    try:
        # 尝试获取笔记（会自动触发登录流程）
        print("\n尝试获取笔记列表...")
        notes = xhs_client.get_user_notes_batch(
            user_id="5c6fb3fb00000000110126a2",
            count=2
        )
        
        print(f"\n成功获取 {len(notes)} 篇笔记:")
        for note in notes:
            print(f"  - {note.note_id}: {note.title[:30]}...")
            print(f"    URL: {note.url}")
        
        return True
        
    except SignServerError as e:
        print(f"[错误] {e}")
        return False
    except Exception as e:
        print(f"[错误] 未知错误: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    result = asyncio.run(test_login())
    sys.exit(0 if result else 1)
