# GitHub Pages 自动双语部署配置指南

## 📋 配置说明

本项目使用 **GitHub Actions** 自动构建和部署中英文双语文档到 GitHub Pages。

---

## ✅ 已完成的配置

### 1. GitHub Actions 工作流

创建了 `.github/workflows/deploy-docs.yml`，自动执行：

1. **触发条件**：
   - 推送到 `main` 分支
   - 修改了 `DeePAW Manual/` 目录下的文件
   - 手动触发

2. **构建步骤**：
   - 安装 Python 3.12 和 Sphinx
   - 构建英文版本文档（`en/`）
   - 构建中文版本文档（`zh_CN/`）
   - 创建语言选择页面

3. **部署到 GitHub Pages**：
   - 自动部署到 `gh-pages` 分支
   - 用户访问：https://suthphy2ai.github.io/DeeeeePAW/

---

## 🚀 部署后的访问方式

### 语言选择页面
```
https://suthphy2ai.github.io/DeeeeePAW/
```
自动显示语言选择界面，包含：
- **English** - 跳转到英文版本
- **中文** - 跳转到中文版本

### 英文版本
```
https://suthphy2ai.github.io/DeeeeePAW/en/
```

### 中文版本
```
https://suthphy2ai.github.io/DeeeeePAW/zh_CN/
```

---

## ⚙️ GitHub Pages 设置

部署后，需要确认 GitHub Pages 配置：

### 步骤 1：访问仓库设置

1. 打开：https://github.com/SuthPhy2Ai/DeeeeePAW/settings/pages
2. 确认 **Build and deployment** → **Source** 设置为：
   - **Deploy from a branch**
   - **Branch**: `gh-pages` / `(root)`

### 步骤 2：检查部署状态

1. 访问：https://github.com/SuthPhy2Ai/DeeeeePAW/actions
2. 查看 **"Build and Deploy Documentation"** 工作流
3. 确认构建成功（绿色勾✓）

---

## 🔄 更新文档流程

### 自动部署

每次修改文档并推送到 `main` 分支，GitHub Actions 会自动：

```bash
# 修改文档
vim "DeePAW Manual/source/theory/method.rst"

# 提交并推送
git add "DeePAW Manual/source/theory/method.rst"
git commit -m "Update method description"
git push origin main

# GitHub Actions 自动构建并部署！（约2-3分钟）
```

### 查看构建进度

1. 访问：https://github.com/SuthPhy2Ai/DeeeeePAW/actions
2. 点击最新的工作流运行
3. 查看实时日志

---

## 🌐 语言切换功能

### 语言选择页面

访问根 URL 会显示精美的语言选择界面：

```
┌─────────────────────────────────┐
│    DeePAW Documentation         │
│                                 │
│  Choose your language / 选择语言 │
│                                 │
│   [English]      [中文]         │
│                                 │
└─────────────────────────────────┘
```

### 自动跳转

如果用户浏览器语言设置是中文，会自动跳转到中文版本（可选配置）。

---

## 📁 目录结构

```
/tmp/DeeeeePAW/
├── .github/workflows/
│   └── deploy-docs.yml        ← GitHub Actions 配置
├── DeePAW Manual/
│   ├── source/                ← 文档源文件
│   │   ├── conf.py            ← Sphinx 配置
│   │   └── locale/zh_CN/      ← 中文翻译
│   └── requirements.txt        ← 依赖文件
└── docs/                      ← 旧的手动部署目录（将被替代）
```

部署后的 `gh-pages` 分支：

```
gh-pages/
├── index.html                 ← 语言选择页
├── .nojekyll
├── en/                        ← 英文版本
│   ├── index.html
│   ├── theory/
│   └── platform/
└── zh_CN/                     ← 中文版本
    ├── index.html
    ├── theory/
    └── platform/
```

---

## 🔧 故障排除

### 问题 1：构建失败

**检查方法**：
1. 访问 Actions 页面
2. 查看失败的步骤日志
3. 常见原因：
   - 依赖安装失败：检查 `requirements.txt`
   - Sphinx 配置错误：检查 `conf.py`
   - 翻译文件错误：检查 `.po` 文件格式

### 问题 2：页面 404

**解决方法**：
1. 确认 GitHub Pages 已启用
2. 确认部署分支是 `gh-pages`
3. 等待 1-2 分钟让 CDN 更新

### 问题 3：中文版本显示英文

**原因**：翻译文件未填写

**解决方法**：
1. 编辑 `DeePAW Manual/source/locale/zh_CN/LC_MESSAGES/*.po`
2. 填写 `msgstr` 内容
3. 推送到 GitHub 触发重新构建

---

## 💡 高级配置

### 自定义域名（可选）

如果想使用 `docs.deepaw.tech`：

1. 在仓库设置中添加自定义域名
2. 在域名 DNS 设置中添加 CNAME：
   ```
   docs.deepaw.tech → suthphy2ai.github.io
   ```
3. GitHub Actions 会自动配置 HTTPS

### 添加语言切换按钮

在 `conf.py` 中添加：

```python
html_theme_options = {
    'navigation_depth': 3,
    'collapse_navigation': False,
}

# 在每个页面底部添加语言链接
html_context = {
    'display_github': True,
    'github_user': 'SuthPhy2Ai',
    'github_repo': 'DeeeeePAW',
    'github_version': 'main',
}
```

---

## 📊 性能优化

### 构建时间

- 首次构建：约 3-4 分钟
- 增量构建：约 1-2 分钟（缓存优化）

### 优化建议

1. **启用 pip 缓存**：已在工作流中配置
2. **减少构建频率**：只在文档变更时触发
3. **使用 sphinx-build -W**：将警告视为错误，提前发现问题

---

## ✅ 部署检查清单

推送代码后，检查以下项目：

- [ ] GitHub Actions 工作流运行成功
- [ ] `gh-pages` 分支已创建
- [ ] GitHub Pages 设置为 `gh-pages` 分支
- [ ] 访问 https://suthphy2ai.github.io/DeeeeePAW/ 显示语言选择页
- [ ] 英文版本可访问
- [ ] 中文版本可访问
- [ ] 语言切换正常工作

---

## 🎉 完成！

配置完成后，你只需要：

```bash
git push origin main
```

GitHub Actions 会自动处理一切！

---

**最后更新**：2026-03-19
**维护者**：DeePAW Team