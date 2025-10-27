<div align="center">
  <img src="projects/ui/src/assets/logo.png" alt="PiXelDa Logo" width="200"/>
  <h1 style="margin: 0; font-size: 30px;">PiXelDa</h1>
</div>

PiXelDa 是一个基于 AI 的平台，专为生成像素艺术游戏开发资源而设计，包括图像和动画，使用 FastAPI 后端和 Angular 前端。它利用来自 <a href="https://bailian.console.aliyun.com/?tab=api#/api/?type=model&url=2712195">Tongyi</a> 和 <a href="https://www.volcengine.com/docs/82379/1541594">Doubao</a> 的先进 AI 模型为 2D 像素艺术游戏创建自定义内容。

<p align="center">
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.13-blue.svg" alt="Python"></a>
  <a href="https://nodejs.org/"><img src="https://img.shields.io/badge/Node.js-22-green.svg" alt="Node.js"></a>
  <a href="https://angular.io/"><img src="https://img.shields.io/badge/Angular-20-red.svg" alt="Angular"></a>
</p>

## 📋 目录

- [功能](#功能)
- [架构](#架构)
- [环境依赖](#环境依赖)
- [安装](#安装)
- [依赖项](#依赖项)
- [贡献](#贡献)
- [许可证](#许可证)

<br>

## ✨ 功能

- ### 🎨 游戏资产生成

  #### 专为游戏开发创建图像和动画的专业工具。

- ### 🖼️ 图像生成

  #### 使用 AI 模型和自定义提示生成图像。

  ![图像生成](assets/intro/zh/image%20generation.jpeg)

  #### 示例提示

  一张高精度像素风格图片，图中有一个年轻美女忍者，卡通风格, 不戴面罩, 身穿黑色忍者服, 脚穿黑色鞋子, 站立姿势，双手放松下垂, 全身照，向前看, 边缘清晰, 色彩艳丽，像素细节清晰，灰色背景。

- ### 🎬 动画生成

  #### 从首帧图像和提示创建视频。

  ![动画生成](assets/intro/zh/animation%20generation.jpeg)

- ### ✂️ 帧分割

  #### 从动画中提取并预览帧，用于 2D 精灵图。

  ![帧分割](assets/intro/zh/frames%20splitting.jpeg)

  ![帧预览](assets/intro/zh/frames%20preview.jpeg)

- ### 🧹 背景移除 (beta)

  #### 使用 rembg 从帧中移除背景。

- ### 🎵 音乐生成

  #### 为您的像素艺术游戏生成自定义背景音乐和配乐。

  ![音乐生成](assets/intro/zh/music%20generation.jpeg)

  #### 示例提示

  一段欢快的音乐，描述一个小猫咪去猫砂盆拉屎，以激昂的旋律开头，以轻松的旋律结尾。

- ### 💾 缓存和历史

  #### 高效缓存生成的图像和动画。

  ![生成历史](assets/intro/zh/history.jpeg)

- ### ⚙️ 设置

  #### 切换语言和 AI 模型

  ![设置](assets/intro/zh/settings.jpeg)

<br>

## 🏗️ 架构

- **后端**：使用 FastAPI、Python 构建。处理 API 请求、AI 模型交互和文件处理。
- **前端**：用于用户交互的 Angular 应用程序。
- **缓存**：存储生成的动画、图像、帧和处理数据。
- **日志**：服务器日志。

<br>

## 📋 环境依赖

- Python 3.13
- Node.js 22
- Angular 20

<br>

## 🚀 安装

### 后端设置

1. 导航到服务器目录：

   ```bash
   cd projects/server
   ```

2. 安装 Python 依赖项：

   ```bash
   pip install -r requirements.txt
   ```

3. 运行服务器：
   ```bash
   python app.py
   ```
   服务器将在默认情况下在 `http://0.0.0.0:8000` 上启动。

### 前端设置

1. 导航到 UI 目录：

   ```bash
   cd projects/ui
   ```

2. 安装 Node.js 依赖项：

   ```bash
   npm install
   ```

3. 启动开发服务器：
   ```bash
   npm start
   ```
   UI 将在 `http://localhost:4200` 上可用。

<br>

## 📦 依赖项

### 后端

| 包名                   | 版本      |
| ---------------------- | --------- |
| FastAPI                | 0.116.1   |
| Uvicorn                | 0.35.0    |
| DashScope SDK (Tongyi) | 1.24.4    |
| Volcano SDK (Doubao)   | 0.1.0     |
| OpenCV                 | 4.12.0.88 |
| rembg                  | 2.0.67    |
| Pillow                 | 11.3.0    |

### 前端

| 包名    | 版本 |
| ------- | ---- |
| Angular | 20   |
| RxJS    | 最新 |

### AI 模型

| 功能                              | 提供商 | 版本                           | 价格                                              |
| --------------------------------- | ------ | ------------------------------ | ------------------------------------------------- |
| 图像生成                          | 豆包   | doubao-seedream-4-0-250828     | 0.2 RMB/张                                        |
| 视频生成(默认 5 秒)               | 豆包   | doubao-seedance-1-0-pro-250528 | 0.73 RMB/480p, 1.64 RMB/720p                      |
| 基于聊天的音乐生成(Max Tokens:2k) | 豆包   | doubao-seed-1-6-251015         | 0.0008 RMB/输入 千-token, 0.008 RMB/输出 千-token |

| 功能                              | 提供商   | 版本               | 价格                                              |
| --------------------------------- | -------- | ------------------ | ------------------------------------------------- |
| 图像生成                          | 通义千问 | wan2.5-t2i-preview | 0.2 RMB/张                                        |
| 视频生成(默认 5 秒)               | 通义千问 | wan2.5-i2v-preview | 1.5 RMB/480p, 3 RMB/720p                          |
| 基于聊天的音乐生成(Max Tokens:2k) | 通义千问 | qwen-plus          | 0.0008 RMB/输入 千-token, 0.008 RMB/输出 千-token |

<br>

## 📄 许可证

此项目根据 MIT 许可证授权 - 有关详细信息，请参阅 [LICENSE](LICENSE) 文件。
