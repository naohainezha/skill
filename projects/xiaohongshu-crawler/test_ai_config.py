"""
测试AI模型配置
快速验证API密钥是否可用
"""
import sys

# 设置UTF-8编码输出
if sys.platform == 'win32':
    import codecs
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    if hasattr(sys.stderr, 'buffer'):
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')


def test_model(usage_type):
    """测试单个模型"""
    from ai_config import AIModelConfig
    from ai_note_generator import AIClient

    print(f"\n{'='*60}")
    print(f"测试模型：{usage_type}")
    print(f"{'='*60}")

    client = AIClient(usage_type)
    config = client.config

    print(f"\n配置信息:")
    print(f"  模型: {config['model']}")
    print(f"  API密钥: {'已设置' if config['api_key'] else '⚠️ 未设置'}")
    print(f"  基础URL: {config['base_url']}")
    print(f"  温度: {config['temperature']}")
    print(f"  最大令牌: {config['max_tokens']}")

    if not config['api_key']:
        print(f"\n⚠️ 跳过测试：未设置API密钥")
        return False

    # 测试调用
    print(f"\n正在测试API调用...")
    test_message = "你好，请用一句话介绍你自己。"

    response = client.chat([
        {"role": "user", "content": test_message}
    ])

    if response.startswith("错误："):
        print(f"❌ 测试失败")
        print(f"   {response}")
        return False
    else:
        print(f"✅ 测试成功")
        print(f"   回复: {response[:100]}...")
        return True


def main():
    """主函数"""
    print("="*60)
    print("AI模型配置测试")
    print("="*60)
    print("\n此脚本将测试以下模型的API配置:")
    print("  1. GLM-4 (智谱AI) - 用于采集阶段")
    print("  2. Kimi K2 (Moonshot AI) - 用于分析和生成阶段")
    print()

    results = {}

    # 测试GLM-4
    results['GLM-4'] = test_model('采集阶段')

    # 测试Kimi K2
    results['Kimi K2'] = test_model('笔记生成')

    # 总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)

    for model, success in results.items():
        status = "✅ 通过" if success else "❌ 失败"
        print(f"  {model}: {status}")

    # 建议
    print("\n" + "="*60)
    print("使用建议")
    print("="*60)

    if results['GLM-4'] and results['Kimi K2']:
        print("✅ 所有模型配置正常，可以运行完整工作流")
        print("\n运行命令:")
        print("  python ai_workflow.py \"眼镜框推荐女\"")
    elif results['Kimi K2']:
        print("⚠️ 仅Kimi K2可用")
        print("\n可以运行:")
        print("  - 数据分析阶段")
        print("  - 笔记生成阶段（需提供已有数据）")
        print("\n无法运行:")
        print("  - 完整工作流（需要GLM-4）")
    elif results['GLM-4']:
        print("⚠️ 仅GLM-4可用")
        print("\n可以运行:")
        print("  - 采集阶段")
        print("\n无法运行:")
        print("  - 数据分析阶段")
        print("  - 笔记生成阶段")
    else:
        print("❌ 所有模型均不可用")
        print("\n请配置API密钥:")
        print("  GLM-4: 设置环境变量 ZHIPU_API_KEY")
        print("  Kimi K2: 设置环境变量 MOONSHOT_API_KEY")

    print("\n" + "="*60)


if __name__ == "__main__":
    main()
