"""
Skill 目录结构初始化脚本

使用说明：
1. 将此脚本复制到待优化的 skill 目录
2. 运行：python init_skill_structure.py
3. 脚本会自动创建所有需要的目录

"""

import os
import sys


def create_skill_structure(skill_path: str):
    """
    创建 Skill 2.0 标准目录结构
    
    Args:
        skill_path: skill 根目录路径
    """
    # 定义需要创建的目录
    directories = [
        os.path.join(skill_path, "workflow"),
        os.path.join(skill_path, "rules"),
        os.path.join(skill_path, "references"),
        os.path.join(skill_path, "templates"),
        os.path.join(skill_path, "scripts"),
        os.path.join(skill_path, "assets"),
    ]
    
    # 创建目录
    created_dirs = []
    for dir_path in directories:
        try:
            os.makedirs(dir_path, exist_ok=True)
            created_dirs.append(dir_path)
            print(f"✅ 创建目录：{dir_path}")
        except Exception as e:
            print(f"❌ 创建目录失败：{dir_path}")
            print(f"   错误：{e}")
    
    # 输出创建结果
    print(f"\n{'='*60}")
    print(f"目录结构初始化完成！")
    print(f"成功创建 {len(created_dirs)} 个目录")
    print(f"{'='*60}")
    
    # 输出目录结构预览
    print("\n📁 目录结构：")
    print(f"""
{skill_path}/
├── workflow/         ← 工作流步骤
├── rules/            ← 规则和要求
├── references/        ← 详细参考资料
├── templates/         ← 输出模板
├── scripts/          ← 工具脚本
└── assets/           ← 配置示例
    """)


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法：python init_skill_structure.py <skill-path>")
        print("示例：python init_skill_structure.py C:\\\\Users\\\\admin\\\\.claude\\\\skills\\\\my-skill")
        sys.exit(1)
    
    skill_path = sys.argv[1]
    
    # 检查路径是否存在
    if not os.path.exists(skill_path):
        print(f"❌ 路径不存在：{skill_path}")
        sys.exit(1)
    
    # 创建目录结构
    create_skill_structure(skill_path)


if __name__ == "__main__":
    main()
