"""
AI模型配置文件
支持在不同阶段使用不同的AI模型
"""

class AIModelConfig:
    """AI模型配置"""

    # 模型API配置
    # ========== GLM-4 配置（用于采集阶段）==========
    GLM4_CONFIG = {
        "model": "glm-4-plus",  # 或 glm-4-flash, glm-4-air
        "api_key": "",  # 从环境变量读取
        "base_url": "https://open.bigmodel.cn/api/paas/v4/",
        "temperature": 0.3,  # 采集阶段使用较低温度，保持准确性
        "max_tokens": 2000,
        "timeout": 30,
        "description": "智谱AI GLM-4模型 - 用于采集阶段的智能辅助"
    }

    # ========== Kimi K2 配置（用于分析和生成笔记）==========
    KIMI_K2_CONFIG = {
        "model": "kimi-k2",  # Moonshot AI的最新模型
        "api_key": "",  # 从环境变量读取
        "base_url": "https://api.moonshot.cn/v1",
        "temperature": 0.8,  # 生成阶段使用较高温度，增加创意性
        "max_tokens": 4000,
        "timeout": 60,
        "description": "Moonshot AI Kimi K2模型 - 用于分析和生成笔记"
    }

    # ========== 模型使用场景配置 ==========
    MODEL_USAGE = {
        "采集阶段": "GLM4",
        "数据分析": "KIMI_K2",
        "笔记生成": "KIMI_K2",
        "内容优化": "KIMI_K2"
    }

    @staticmethod
    def get_model_config(usage_type):
        """根据使用类型获取对应的模型配置

        Args:
            usage_type: 使用类型（采集阶段/数据分析/笔记生成/内容优化）

        Returns:
            dict: 模型配置字典
        """
        model_name = AIModelConfig.MODEL_USAGE.get(usage_type, "KIMI_K2")

        if model_name == "GLM4":
            return AIModelConfig.GLM4_CONFIG
        else:
            return AIModelConfig.KIMI_K2_CONFIG

    @staticmethod
    def get_env_api_key(model_name):
        """从环境变量获取API密钥

        Args:
            model_name: 模型名称（GLM4/KIMI_K2）

        Returns:
            str: API密钥
        """
        import os

        env_keys = {
            "GLM4": ["ZHIPU_API_KEY", "GLM_API_KEY"],
            "KIMI_K2": ["MOONSHOT_API_KEY", "KIMI_API_KEY"]
        }

        for env_key in env_keys.get(model_name, []):
            api_key = os.environ.get(env_key)
            if api_key:
                return api_key

        return ""

    @staticmethod
    def get_full_config(usage_type):
        """获取完整的模型配置（包括API密钥）

        Args:
            usage_type: 使用类型

        Returns:
            dict: 完整的模型配置
        """
        config = AIModelConfig.get_model_config(usage_type).copy()

        # 确定模型类型
        model_name = "GLM4" if usage_type == "采集阶段" else "KIMI_K2"

        # 添加API密钥
        api_key = AIModelConfig.get_env_api_key(model_name)
        if not api_key:
            print(f"⚠️ 警告：未找到 {model_name} 的API密钥环境变量")
            print(f"   请设置环境变量：{', '.join(['ZHIPU_API_KEY', 'MOONSHOT_API_KEY'])}")
        config["api_key"] = api_key

        return config


# 测试配置
if __name__ == "__main__":
    print("=== AI模型配置测试 ===\n")

    # 测试采集阶段配置
    print("【采集阶段 - 使用GLM-4】")
    crawl_config = AIModelConfig.get_full_config("采集阶段")
    print(f"模型: {crawl_config['model']}")
    print(f"温度: {crawl_config['temperature']}")
    print(f"API密钥: {'已设置' if crawl_config['api_key'] else '未设置'}")
    print(f"说明: {crawl_config['description']}\n")

    # 测试笔记生成配置
    print("【笔记生成 - 使用Kimi K2】")
    gen_config = AIModelConfig.get_full_config("笔记生成")
    print(f"模型: {gen_config['model']}")
    print(f"温度: {gen_config['temperature']}")
    print(f"API密钥: {'已设置' if gen_config['api_key'] else '未设置'}")
    print(f"说明: {gen_config['description']}")
