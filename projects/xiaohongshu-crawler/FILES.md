# 项目文件说明

## 核心文件

### config.py
- **用途**: 配置文件
- **说明**: 修改搜索关键词、采集数量、延迟参数等

### crawler_v2.py ⭐ 推荐
- **用途**: V2版本爬虫主程序
- **特点**: 更稳定，先收集链接再提取详情
- **推荐**: 优先使用此版本

### crawler.py
- **用途**: V1版本爬虫主程序
- **特点**: 直接从列表页提取
- **说明**: 备用版本，如果V2有问题可以尝试

## 启动脚本

### run.bat
- **用途**: Windows快速启动脚本
- **使用**: 双击运行或在命令行执行

### run.sh
- **用途**: Linux/Mac快速启动脚本
- **使用**: chmod +x run.sh && ./run.sh

## 工具脚本

### test_env.py
- **用途**: 环境测试脚本
- **功能**: 验证Playwright和浏览器是否正常
- **使用**: python test_env.py

## 配置文件

### requirements.txt
- **用途**: Python依赖列表
- **包含**: playwright, fake-useragent

### .gitignore
- **用途**: Git忽略文件
- **作用**: 避免提交cookies和采集数据

## 文档文件

### README.md
- **用途**: 项目说明文档
- **内容**: 功能特性、安装方法、使用说明、故障排除

### QUICKSTART.md
- **用途**: 快速开始指南
- **内容**: 3步上手、首次使用流程、常见问题

### example_output.json
- **用途**: 输出数据示例
- **说明**: 展示采集数据的格式

## 输出目录（自动创建）

### output/
- **用途**: 保存采集的数据
- **文件**:
  - `notes_YYYYMMDD_HHMMSS.json` - JSON格式数据
  - `notes_YYYYMMDD_HHMMSS.csv` - CSV格式数据

## 缓存文件（自动生成）

### cookies.json
- **用途**: 保存登录cookies
- **说明**: 避免每次都要扫码登录
- **位置**: 项目根目录

## 文件依赖关系

```
config.py          ->  crawler_v2.py  ->  output/
requirements.txt    ->  (pip install)  ->  环境依赖
cookies.json        ->  crawler_v2.py  ->  自动登录
test_env.py        ->  环境验证       ->  确认可以运行
```

## 推荐使用流程

1. **首次使用**:
   ```
   test_env.py (测试环境)
   -> config.py (修改配置)
   -> crawler_v2.py (首次运行，扫码登录)
   ```

2. **日常使用**:
   ```
   config.py (根据需要修改关键词)
   -> run.bat 或 python crawler_v2.py (直接运行)
   ```

3. **遇到问题**:
   ```
   test_env.py (检查环境)
   -> README.md (查看故障排除)
   -> QUICKSTART.md (查看常见问题)
   ```

## 文件大小参考

- config.py: ~1KB
- crawler_v2.py: ~15KB
- requirements.txt: <1KB
- README.md: ~5KB
- QUICKSTART.md: ~8KB

## 版本更新日志

### V2.0 (2026-01-05)
- 重构爬虫逻辑，先收集链接再提取详情
- 添加更多页面选择器，提高成功率
- 优化错误处理和恢复机制
- 添加链接去重功能
- 改进日志输出

### V1.0 (2026-01-05)
- 初始版本
- 基础的搜索和采集功能
- 支持扫码登录和cookies保存
- 支持JSON和CSV导出

---

*文件说明最后更新: 2026-01-05*
