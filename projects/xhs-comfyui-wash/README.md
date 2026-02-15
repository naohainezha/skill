# ComfyUI洗图自动化工具

## ⚠️ 当前状态

工作流格式不兼容 - 需要转换为ComfyUI API格式

## 🔍 问题分析

### 发现的问题

1. **工作流格式不匹配**
   - 当前工作流: `z洗图1222.json` 是秋叶启动器的UI格式
   - 包含UI节点信息 (pos, size, flags等)
   - 不是ComfyUI API可用的格式

2. **API格式要求**
   - 需要从ComfyUI导出为 "API格式" (Save (API Format))
   - 或者手动提取节点连接关系

## ✅ 解决方案

### 方案1: 导出API格式工作流 (推荐)

1. 打开ComfyUI网页界面
2. 加载 `z洗图1222.json` 工作流
3. 点击右上角菜单 → "Save (API Format)"
4. 保存为 `z洗图1222_api.json`
5. 将文件放到项目目录

### 方案2: 使用ComfyUI-Manager插件

安装 `ComfyUI-Manager` 插件，它提供批量队列功能

### 方案3: 手动转换

编写脚本将UI格式转换为API格式

## 📁 项目文件

```
xhs-comfyui-wash/
├── config.py           # 配置文件
├── launcher.py         # 启动器模块
├── wash.py             # 主洗图程序
├── test_workflow.py    # 工作流测试
└── README.md           # 本文件
```

## 🚀 使用方法

### 前提条件

1. 导出API格式工作流到项目目录
2. 确保ComfyUI已启动
3. 准备输入图片

### 运行洗图

```bash
cd C:\Users\admin\Projects\xhs-comfyui-wash
python wash.py "C:\path\to\filtered" "C:\path\to\washed"
```

## 📝 下一步

需要用户操作:
1. 在ComfyUI中导出API格式工作流
2. 或者提供工作流的截图，我帮助分析节点结构

## 🔧 当前代码功能

- ✅ 配置管理
- ✅ 启动器检测
- ✅ 工作流加载框架
- ⚠️ 工作流格式转换 (需要API格式)
- ✅ 批量队列管理
- ✅ 结果收集

---

**等待: 需要API格式工作流文件**
