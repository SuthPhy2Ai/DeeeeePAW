# ReadTheDocs 设置指南

本指南说明如何将 DeePAW 文档部署到 ReadTheDocs，实现中英文双语版本自动构建和语言切换。

## 📋 前提条件

- ✅ GitHub 仓库：`https://github.com/SuthPhy2Ai/DeeeeePAW`
- ✅ Sphinx 文档已配置
- ✅ 国际化翻译文件已创建

---

## 🚀 步骤 1：推送配置文件到 GitHub

首先，需要将 ReadTheDocs 配置文件提交到仓库：

```bash
cd /tmp/DeeeeePAW
git add .readthedocs.yaml "DeePAW Manual/requirements.txt"
git commit -m "Add ReadTheDocs configuration for bilingual documentation"
git push origin main
```

---

## 📚 步骤 2：注册 ReadTheDocs 账号

1. 访问 https://readthedocs.org/
2. 点击右上角 **"Sign Up"**
3. 选择 **"Sign up with GitHub"**
4. 授权 ReadTheDocs 访问你的 GitHub 账号

---

## 🔧 步骤 3：导入项目

1. 登录后，点击 **"My Projects"**
2. 点击 **"Import a Project"**
3. 选择你的仓库：`SuthPhy2Ai/DeeeeePAW`
4. 点击 **"Next"**

---

## ⚙️ 步骤 4：配置项目

### 基本设置

- **Name**: `DeePAW`（或你喜欢的名字）
- **Repository URL**: 自动填充
- **Repository type**: Git

### 高级设置

点击 **"Advanced configuration"**：

**Documentation Type**:
- 选择：**Sphinx Html Documentation**

**Configuration file**:
- 路径：`DeePAW Manual/source/conf.py`

**Requirements file**:
- 路径：`DeePAW Manual/requirements.txt`

**Python interpreter**:
- 选择：**CPython 3.x**

---

## 🌐 步骤 5：启用多语言支持

### 方法 1：自动检测（推荐）

ReadTheDocs 会自动检测 `conf.py` 中的 `locale_dirs` 配置，并启用翻译支持。

1. 在项目设置中，找到 **"Translations"** 部分
2. 点击 **"Add a translation"**
3. 选择语言：
   - **English (en)** - 默认语言
   - **Chinese Simplified (zh_CN)** - 中文简体
4. 保存设置

### 方法 2：手动配置

如果自动检测失败，可以手动添加翻译：

1. 在 **"Translations"** 页面
2. 点击 **"Add translation"**
3. 填写：
   - **Language**: Chinese Simplified
   - **Version**: latest
4. 点击 **"Create"**

---

## 🔄 步骤 6：触发构建

1. 返回项目主页
2. 点击 **"Build version"** 或 **"Rebuild"**
3. 等待构建完成（首次构建约 2-5 分钟）

---

## 🎉 步骤 7：访问文档

构建成功后，你会得到：

### 英文版本
```
https://deepaw.readthedocs.io/en/
```

### 中文版本
```
https://deepaw.readthedocs.io/zh_CN/
```

### 默认版本（自动跳转）
```
https://deepaw.readthedocs.io/
```

---

## 🎨 语言切换功能

ReadTheDocs 会自动在页面左下角添加语言切换器：

```
Read the Docs
  v: latest
    Versions
    Downloads
    On Read the Docs
    Project Home
    Builds

  [English] ← 点击切换
  [中文]    ← 点击切换
```

用户可以随时在英文和中文之间切换！

---

## ⚡ 自动构建

### 自动触发条件

每次你推送到 GitHub，ReadTheDocs 会自动重新构建：

```bash
# 修改文档
vim "DeePAW Manual/source/theory/method.rst"

# 提交并推送
git add "DeePAW Manual/source/theory/method.rst"
git commit -m "Update method description"
git push origin main

# ReadTheDocs 自动检测并重新构建！
```

### 查看构建状态

1. 访问项目页面
2. 点击 **"Builds"** 标签
3. 查看构建日志和状态

---

## 📖 更新翻译

当英文原文更新后，翻译会自动标记为需要更新：

1. 推送更新到 GitHub
2. ReadTheDocs 自动构建
3. 翻译状态会显示 **"outdated"**
4. 在 ReadTheDocs 界面可以直接更新 `.po` 文件（可选）

---

## 🔧 常见配置

### 自定义域名（可选）

如果你想使用自己的域名：

1. 项目设置 → **"Domains"**
2. 添加自定义域名，例如：`docs.deepaw.tech`
3. 在域名 DNS 设置中添加 CNAME 记录

### PDF 导出

ReadTheDocs 自动生成 PDF 版本：

```
https://deepaw.readthedocs.io/_/downloads/en/latest/pdf/
https://deepaw.readthedocs.io/_/downloads/zh_CN/latest/pdf/
```

用户可以直接下载！

### 搜索功能

ReadTheDocs 提供内置搜索功能，支持：
- 中英文混合搜索
- 实时搜索结果
- 高亮显示

---

## ❓ 常见问题

### Q: 构建失败怎么办？

A: 查看构建日志：
1. 点击失败的构建
2. 查看 **"Build Log"**
3. 常见错误：
   - 缺少依赖：在 `requirements.txt` 中添加
   - 配置路径错误：检查 `.readthedocs.yaml`
   - RST 语法错误：检查 `.rst` 文件

### Q: 如何预览本地更改？

A: 本地构建预览：
```bash
cd "/tmp/DeeeeePAW/DeePAW Manual"
conda run -n base sphinx-build -b html source _build/html/en
firefox _build/html/en/index.html
```

### Q: 可以同时使用 GitHub Pages 和 ReadTheDocs 吗？

A: 可以！但建议只使用一个：
- ReadTheDocs：功能更强大，自动多语言
- GitHub Pages：完全控制，但需要手动配置

---

## 📚 相关链接

- ReadTheDocs 文档：https://docs.readthedocs.io/
- Sphinx 文档：https://www.sphinx-doc.org/
- 多语言支持：https://docs.readthedocs.io/en/stable/guides/internationalization.html

---

## ✅ 检查清单

设置完成后，检查以下项目：

- [ ] 配置文件已推送到 GitHub
- [ ] ReadTheDocs 账号已创建
- [ ] 项目已导入
- [ ] 构建成功
- [ ] 英文版本可访问
- [ ] 中文版本可访问
- [ ] 语言切换器正常工作
- [ ] 搜索功能正常
- [ ] PDF 下载可用

---

**需要帮助？** 联系：thsu0407@gmail.com

**最后更新**：2026-03-19