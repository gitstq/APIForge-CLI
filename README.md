# 🌐 Language | 语言 | 語言

- [English](#english)
- [简体中文](#简体中文)
- [繁體中文](#繁體中文)

---

# English

## 🚀 APIForge - AI-Powered API Mocking & Testing Toolkit

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Stars](https://img.shields.io/github/stars/gitstq/APIForge-CLI?style=social)](https://github.com/gitstq/APIForge-CLI)

### 🎉 Project Introduction

**APIForge** is a powerful, lightweight API mocking and testing toolkit designed for developers. It provides a comprehensive solution for creating mock APIs, recording real requests, generating test data, and simulating complex API scenarios - all through an intuitive command-line interface.

### ✨ Core Features

- 🎭 **Mock Server** - Start a fully-featured mock API server in seconds
- 📝 **API Recording** - Record real API calls and replay them later
- 🎲 **Smart Data Generation** - Generate realistic mock data from JSON schemas or OpenAPI specs
- 🔄 **Scenario Simulation** - Create complex API scenarios with conditions and probabilities
- 📊 **Multiple Formats** - Export recordings as JSON, HAR, or OpenAPI examples
- 🌐 **CORS Enabled** - Built-in CORS support for frontend development
- ⚡ **Dynamic Responses** - Generate dynamic values like UUIDs, timestamps, and random data

### 🚀 Quick Start

#### Installation

```bash
# Using pip
pip install apiforge

# Or install from source
git clone https://github.com/gitstq/APIForge-CLI.git
cd APIForge-CLI
pip install -e .
```

#### Basic Usage

```bash
# Start the mock server
apiforge serve --port 8080

# Generate mock data from OpenAPI spec
apiforge generate from-openapi examples/openapi_spec.json

# Record API calls
apiforge record start my-recording
# ... make API calls ...
apiforge record stop

# Generate test data
apiforge generate test-data examples/user_schema.json --count 10

# Generate fake data
apiforge generate faker email
```

### 📖 Detailed Usage Guide

#### Starting Mock Server

```bash
# Default server (localhost:8080)
apiforge serve

# Custom port and host
apiforge serve --host 0.0.0.0 --port 9000

# Load custom scenarios
apiforge serve --scenarios examples/mock_scenarios.json
```

#### Adding Mock Endpoints

```bash
# Add simple mock endpoint
apiforge mock add /api/users --body '{"users": []}'

# Add endpoint with custom status
apiforge mock add /api/error --status 500 --body '{"error": "Server Error"}'

# Add endpoint with delay
apiforge mock add /api/slow --delay 2000 --body '{"message": "Delayed response"}'
```

#### Recording API Calls

```bash
# Start recording
apiforge record start my-api-test

# Stop recording
apiforge record stop

# List all recordings
apiforge record list

# Export recording
apiforge record export my-api-test --format har
```

#### Generating Test Data

```bash
# Generate from JSON schema
apiforge generate test-data schema.json --count 100 --output test_data.json

# Generate from OpenAPI spec
apiforge generate from-openapi openapi.json --output mocks.json

# Generate fake data types
apiforge generate faker name --count 5
apiforge generate faker email --count 10
apiforge generate faker address --count 3
```

### 📦 Project Structure

```
APIForge-CLI/
├── apiforge/              # Main package
│   ├── __init__.py        # Package init
│   ├── cli.py             # CLI interface
│   ├── config.py          # Configuration management
│   ├── server.py          # Mock server
│   ├── recorder.py        # API recorder
│   ├── generator.py       # Mock data generator
│   ├── mock_engine.py     # Mock engine
│   └── utils.py           # Utilities
├── examples/              # Example files
│   ├── user_schema.json   # User data schema
│   ├── openapi_spec.json  # OpenAPI specification
│   └── mock_scenarios.json # Mock scenarios
├── tests/                # Unit tests
├── requirements.txt       # Dependencies
├── setup.py             # Package setup
└── LICENSE              # MIT License
```

### 💡 Design Philosophy & Roadmap

#### Design Principles
- **Lightweight First** - No heavy dependencies, works out of the box
- **Developer Experience** - Intuitive CLI with helpful feedback
- **Extensible** - Easy to add custom generators and scenarios
- **Standards Based** - Follows OpenAPI and HAR specifications

#### Future Roadmap
- [ ] Web UI dashboard for visual mock management
- [ ] Docker container support for easy deployment
- [ ] Integration with popular testing frameworks
- [ ] AI-powered smart mock generation
- [ ] Team collaboration features
- [ ] Cloud-based mock service

### 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### 🙏 Acknowledgments

- Built with ❤️ for developers by developers
- Inspired by the need for simple, powerful API mocking tools
- Thanks to the open-source community

---

# 简体中文

## 🚀 APIForge - AI驱动的API模拟与测试工具包

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Stars](https://img.shields.io/github/stars/gitstq/APIForge-CLI?style=social)](https://github.com/gitstq/APIForge-CLI)

### 🎉 项目介绍

**APIForge** 是一款强大、轻量级的API模拟和测试工具，专为开发者设计。它提供了完整的解决方案，用于创建模拟API、录制真实请求、生成测试数据、模拟复杂API场景——所有功能都通过直观的命令行界面实现。

### ✨ 核心特性

- 🎭 **模拟服务器** - 秒级启动功能完整的模拟API服务器
- 📝 **API录制** - 录制真实API调用并随时回放
- 🎲 **智能数据生成** - 从JSON模式或OpenAPI规范生成真实模拟数据
- 🔄 **场景模拟** - 通过条件和概率创建复杂的API场景
- 📊 **多种格式** - 支持导出为JSON、HAR或OpenAPI示例
- 🌐 **CORS支持** - 内置CORS支持，便于前端开发
- ⚡ **动态响应** - 生成UUID、时间戳和随机数据等动态值

### 🚀 快速开始

#### 安装

```bash
# 使用pip安装
pip install apiforge

# 或从源码安装
git clone https://github.com/gitstq/APIForge-CLI.git
cd APIForge-CLI
pip install -e .
```

#### 基本使用

```bash
# 启动模拟服务器
apiforge serve --port 8080

# 从OpenAPI规范生成模拟数据
apiforge generate from-openapi examples/openapi_spec.json

# 录制API调用
apiforge record start my-recording
# ... 进行API调用 ...
apiforge record stop

# 生成测试数据
apiforge generate test-data examples/user_schema.json --count 10

# 生成假数据
apiforge generate faker email
```

### 📖 详细使用指南

#### 启动模拟服务器

```bash
# 默认服务器 (localhost:8080)
apiforge serve

# 自定义端口和主机
apiforge serve --host 0.0.0.0 --port 9000

# 加载自定义场景
apiforge serve --scenarios examples/mock_scenarios.json
```

#### 添加模拟端点

```bash
# 添加简单的模拟端点
apiforge mock add /api/users --body '{"users": []}'

# 添加自定义状态的端点
apiforge mock add /api/error --status 500 --body '{"error": "服务器错误"}'

# 添加延迟响应的端点
apiforge mock add /api/slow --delay 2000 --body '{"message": "延迟响应"}'
```

#### 录制API调用

```bash
# 开始录制
apiforge record start my-api-test

# 停止录制
apiforge record stop

# 列出所有录制
apiforge record list

# 导出录制
apiforge record export my-api-test --format har
```

#### 生成测试数据

```bash
# 从JSON模式生成
apiforge generate test-data schema.json --count 100 --output test_data.json

# 从OpenAPI规范生成
apiforge generate from-openapi openapi.json --output mocks.json

# 生成各种假数据类型
apiforge generate faker name --count 5
apiforge generate faker email --count 10
apiforge generate faker address --count 3
```

### 📦 项目结构

```
APIForge-CLI/
├── apiforge/              # 主包
│   ├── __init__.py        # 包初始化
│   ├── cli.py             # 命令行接口
│   ├── config.py          # 配置管理
│   ├── server.py          # 模拟服务器
│   ├── recorder.py        # API录制器
│   ├── generator.py       # 模拟数据生成器
│   ├── mock_engine.py     # 模拟引擎
│   └── utils.py           # 工具函数
├── examples/              # 示例文件
│   ├── user_schema.json   # 用户数据模式
│   ├── openapi_spec.json  # OpenAPI规范
│   └── mock_scenarios.json # 模拟场景
├── tests/                # 单元测试
├── requirements.txt       # 依赖项
├── setup.py             # 包设置
└── LICENSE              # MIT许可证
```

### 💡 设计理念与迭代规划

#### 设计原则
- **轻量优先** - 无重型依赖，开箱即用
- **开发者体验** - 直观的CLI，提供有用的反馈
- **可扩展性** - 易于添加自定义生成器和场景
- **标准兼容** - 遵循OpenAPI和HAR规范

#### 后续规划
- [ ] Web UI仪表板实现可视化模拟管理
- [ ] Docker容器支持便于部署
- [ ] 集成流行测试框架
- [ ] AI驱动的智能模拟生成
- [ ] 团队协作功能
- [ ] 基于云的模拟服务

### 🤝 贡献指南

欢迎贡献！请随时提交问题或拉取请求。

1. Fork本仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'feat: 添加新功能'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 打开Pull Request

### 📄 开源协议

本项目采用MIT许可证 - 详见 [LICENSE](LICENSE) 文件。

### 🙏 致谢

- 由开发者为开发者用❤️打造
- 源于对简洁强大API模拟工具的需求
- 感谢开源社区

---

# 繁體中文

## 🚀 APIForge - AI驅動的API模擬與測試工具包

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Stars](https://img.shields.io/github/stars/gitstq/APIForge-CLI?style=social)](https://github.com/gitstq/APIForge-CLI)

### 🎉 專案介紹

**APIForge** 是一款強大、輕量級的API模擬和測試工具，專為開發者設計。它提供了完整的解決方案，用於創建模擬API、錄製真實請求、生成測試資料、模擬複雜API場景——所有功能都通過直觀的命令列介面實現。

### ✨ 核心特性

- 🎭 **模擬伺服器** - 秒級啟動功能完整的模擬API伺服器
- 📝 **API錄製** - 錄製真實API調用並隨時回放
- 🎲 **智慧資料生成** - 從JSON模式或OpenAPI規範生成真實模擬資料
- 🔄 **場景模擬** - 通過條件和概率創建複雜的API場景
- 📊 **多種格式** - 支持導出為JSON、HAR或OpenAPI範例
- 🌐 **CORS支持** - 內置CORS支持，便於前端開發
- ⚡ **動態回應** - 生成UUID、時間戳和隨機資料等動態值

### 🚀 快速開始

#### 安裝

```bash
# 使用pip安裝
pip install apiforge

# 或從原始碼安裝
git clone https://github.com/gitstq/APIForge-CLI.git
cd APIForge-CLI
pip install -e .
```

#### 基本使用

```bash
# 啟動模擬伺服器
apiforge serve --port 8080

# 從OpenAPI規範生成模擬資料
apiforge generate from-openapi examples/openapi_spec.json

# 錄製API調用
apiforge record start my-recording
# ... 進行API調用 ...
apiforge record stop

# 生成測試資料
apiforge generate test-data examples/user_schema.json --count 10

# 生成假資料
apiforge generate faker email
```

### 📖 詳細使用指南

#### 啟動模擬伺服器

```bash
# 預設伺服器 (localhost:8080)
apiforge serve

# 自訂連接埠和主機
apiforge serve --host 0.0.0.0 --port 9000

# 載入自訂場景
apiforge serve --scenarios examples/mock_scenarios.json
```

#### 添加模擬端點

```bash
# 添加簡單的模擬端點
apiforge mock add /api/users --body '{"users": []}'

# 添加自訂狀態的端點
apiforge mock add /api/error --status 500 --body '{"error": "伺服器錯誤"}'

# 添加延遲回應的端點
apiforge mock add /api/slow --delay 2000 --body '{"message": "延遲回應"}'
```

#### 錄製API調用

```bash
# 開始錄製
apiforge record start my-api-test

# 停止錄製
apiforge record stop

# 列出所有錄製
apiforge record list

# 導出錄製
apiforge record export my-api-test --format har
```

#### 生成測試資料

```bash
# 從JSON模式生成
apiforge generate test-data schema.json --count 100 --output test_data.json

# 從OpenAPI規範生成
apiforge generate from-openapi openapi.json --output mocks.json

# 生成各種假資料類型
apiforge generate faker name --count 5
apiforge generate faker email --count 10
apiforge generate faker address --count 3
```

### 📦 專案結構

```
APIForge-CLI/
├── apiforge/              # 主包
│   ├── __init__.py        # 包初始化
│   ├── cli.py             # 命令列介面
│   ├── config.py          # 配置管理
│   ├── server.py          # 模擬伺服器
│   ├── recorder.py        # API錄製器
│   ├── generator.py       # 模擬資料生成器
│   ├── mock_engine.py     # 模擬引擎
│   └── utils.py           # 工具函數
├── examples/              # 範例檔案
│   ├── user_schema.json   # 使用者資料模式
│   ├── openapi_spec.json  # OpenAPI規範
│   └── mock_scenarios.json # 模擬場景
├── tests/                # 單元測試
├── requirements.txt       # 依賴項
├── setup.py             # 包設定
└── LICENSE              # MIT許可證
```

### 💡 設計理念與迭代規劃

#### 設計原則
- **輕量優先** - 無重型依賴，開箱即用
- **開發者體驗** - 直觀的CLI，提供有用的回饋
- **可擴展性** - 易於添加自訂生成器和場景
- **標準相容** - 遵循OpenAPI和HAR規範

#### 後續規劃
- [ ] Web UI儀表板實現視覺化模擬管理
- [ ] Docker容器支持便於部署
- [ ] 整合流行測試框架
- [ ] AI驅動的智慧模擬生成
- [ ] 團隊協作功能
- [ ] 基於雲的模擬服務

### 🤝 貢獻指南

歡迎貢獻！請隨時提交問題或拉取請求。

1. Fork本倉庫
2. 創建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'feat: 添加新功能'`)
4. 推送至分支 (`git push origin feature/amazing-feature`)
5. 開啟Pull Request

### 📄 開源協議

本專案採用MIT許可證 - 詳見 [LICENSE](LICENSE) 檔案。

### 🙏 致謝

- 由開發者為開發者用❤️打造
- 源於對簡潔強大API模擬工具的需求
- 感謝開源社群
