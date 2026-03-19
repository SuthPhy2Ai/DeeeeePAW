# GitHub Pages 部署故障排查

## 问题症状

- GitHub Actions 工作流运行失败（红色叉号 ❌）
- `gh-pages` 分支不存在（404 错误）
- 文档无法访问

## 诊断步骤

### 步骤 1：检查 GitHub Pages 设置

1. 访问：https://github.com/SuthPhy2Ai/DeeeeePAW/settings/pages
2. 检查 **Build and deployment** → **Source** 设置：
   - ✅ **应该选择**：`GitHub Actions`
   - ❌ **如果选择**：`Deploy from a branch` → 需要修改

**如何修改**：
- 在 "Source" 下拉菜单中选择 `GitHub Actions`
- 保存设置

### 步骤 2：检查 Actions 错误日志

1. 访问：https://github.com/SuthPhy2Ai/DeeeeePAW/actions
2. 点击最新的失败的工作流运行（红色叉号）
3. 查看具体哪个步骤失败：
   - `Build English documentation` 步骤失败？
   - `Build Chinese documentation` 步骤失败？
   - `Upload artifact` 步骤失败？
   - `Deploy to GitHub Pages` 步骤失败？

4. 点击失败的步骤，查看详细错误信息

### 步骤 3：重新触发构建

如果修改了 GitHub Pages 设置，需要重新触发构建：

**方法 1：手动触发**
1. 访问：https://github.com/SuthPhy2Ai/DeeeeePAW/actions/workflows/deploy-docs.yml
2. 点击右侧 **"Run workflow"** 按钮
3. 选择 `main` 分支
4. 点击绿色 **"Run workflow"** 按钮

**方法 2：推送新提交**
```bash
cd /tmp/DeeeeePAW
git commit --allow-empty -m "Trigger rebuild"
git push origin main
```

## 常见错误和解决方案

### 错误 1：GitHub Pages 未启用

**症状**：
- `Deploy to GitHub Pages` 步骤失败
- 错误信息包含：`Pages is not enabled for this repository`

**解决方法**：
1. 访问 Settings → Pages
2. 在 **Source** 下选择 `GitHub Actions`
3. 保存设置
4. 重新触发构建

### 错误 2：权限不足

**症状**：
- 错误信息包含：`Permission denied` 或 `insufficient permission`

**解决方法**：
1. 检查工作流文件中的 `permissions` 部分：
   ```yaml
   permissions:
     contents: write
     pages: write
     id-token: write
   ```
2. 确认这些权限已添加（已在最新版本中添加）

### 错误 3：Artifact 上传失败

**症状**：
- `Upload artifact` 步骤失败
- 错误信息包含：`No files were found`

**解决方法**：
检查 `Prepare docs directory` 步骤是否成功执行

### 错误 4：Python 依赖安装失败

**症状**：
- `Install dependencies` 步骤失败

**解决方法**：
1. 检查 `DeePAW Manual/requirements.txt` 文件内容：
   ```
   sphinx>=7.0.0
   sphinx-rtd-theme>=2.0.0
   ```
2. 确认文件存在且格式正���

## 当前工作流配置（正确）

`.github/workflows/deploy-docs.yml` 已正确配置：

✅ 使用官方 `actions/deploy-pages@v4`
✅ 包含正确的权限设置
✅ 构建中英文双版本
✅ 创建语言选择页面

## 下一步行动

**请执行以下操作**：

1. **检查 GitHub Pages 设置**：
   - 访问 https://github.com/SuthPhy2Ai/DeeeeePAW/settings/pages
   - 确认 Source 设置为 `GitHub Actions`
   - 截图发给我

2. **检查 Actions 错误日志**：
   - 访问 https://github.com/SuthPhy2Ai/DeeeeePAW/actions
   - 点击最新的失败运行
   - 查看具体哪个步骤失败
   - 截图错误信息发给我

根据具体的错误信息，我可以提供针对性的解决方案。

## 备用方案

如果 GitHub Pages 部署持续失败，可以考虑：

1. **使用 ReadTheDocs**（已配置 `.readthedocs.yaml`）
   - 注册 https://readthedocs.org/
   - 导入项目
   - 自动部署

2. **手动部署到 `docs/` 目录**：
   - 本地构建文档
   - 推送到 `docs/` 分支
   - GitHub Pages 从 `docs/` 分支部署

---

**需要帮助？** 请提供 Actions 错误日志截图。