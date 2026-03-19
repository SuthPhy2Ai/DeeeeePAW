# DeePAW 文档国际化翻译指南

本文档说明如何为 DeePAW 文档添加中文翻译。

## 目录结构

```
DeePAW Manual/
├── source/                          # 英文原文 (.rst 文件)
│   ├── conf.py                      # Sphinx 配置
│   ├── index.rst
│   ├── theory/*.rst
│   └── platform/*.rst
├── source/locale/zh_CN/LC_MESSAGES/ # 中文翻译 (.po 文件)
│   ├── index.po
│   ├── theory/*.po
│   └── platform/*.po
└── _build/html/                     # 构建输出
    ├── en/                          # 英文 HTML
    └── zh_CN/                       # 中文 HTML
```

## 如何翻译

### 1. 翻译 .po 文件

每个 `.po` 文件包含待翻译的文本。格式如下：

```po
msgid "Part I: Theoretical Background"
msgstr "第一部分：理论背景"
```

**翻译步骤**：
1. 打开 `.po` 文件（例如 `source/locale/zh_CN/LC_MESSAGES/index.po`）
2. 找到空的 `msgstr ""` 行
3. 在引号内填写中文翻译
4. 保存文件

### 2. 翻译文件头部信息

每个 `.po` 文件的头部需要更新：

```po
"PO-Revision-Date: 2026-03-19 23:20+0800\n"
"Last-Translator: Your Name <your.email@example.com>\n"
"Language-Team: Chinese <zh_CN@li.org>\n"
```

### 3. 构建文档

使用提供的构建脚本：

```bash
cd "/tmp/DeeeeePAW/DeePAW Manual"
./build_docs.sh
```

或者手动构建：

```bash
# 英文版本
sphinx-build -b html source _build/html/en

# 中文版本
sphinx-build -b html -D language=zh_CN source _build/html/zh_CN
```

## 翻译示例

### 示例 1：index.po

**原文（英文）**：
```po
msgid "Part I: Theoretical Background"
msgstr ""
```

**翻译后（中文）**：
```po
msgid "Part I: Theoretical Background"
msgstr "第一部分：理论背景"
```

### 示例 2：theory/method.po

**原文**：
```po
msgid "DeePAW Method"
msgstr ""

msgid "Method Overview"
msgstr ""
```

**翻译后**：
```po
msgid "DeePAW Method"
msgstr "DeePAW 方法"

msgid "Method Overview"
msgstr "方法概述"
```

## 翻译工具推荐

### 选项 1：手动编辑（推荐新手）
- 直接用文本编辑器编辑 `.po` 文件
- 适合小规模翻译

### 选项 2：Poedit（推荐）
- 图形化界面的 `.po` 编辑器
- 下载：https://poedit.net/
- 支持翻译记忆、自动建议等功能

### 选项 3：VSCode 扩展
- 安装 "i18n Ally" 或 "PO Editor" 扩展
- 在 VSCode 中直接编辑

### 选��� 4：在线翻译平台
- Transifex: https://www.transifex.com/
- Crowdin: https://crowdin.com/
- 适合团队协作翻译

## 注意事项

### 1. 保持格式一致性
- 标题大小写
- 专有名词（如 DeePAW、VASP、DFT）保持英文
- 数学公式和代码块不要翻译

### 2. 术语对照表

| 英文 | 中文 | 说明 |
|------|------|------|
| electron density | 电子密度 | 核心术语 |
| charge density | 电荷密度 | 同义词 |
| Kohn-Sham DFT | Kohn-Sham 密度泛函理论 | 保留人名 |
| neural network | 神经网络 | |
| message passing | 消息传递 | |
| equivariance | 等变性 | 数学术语 |

### 3. 更新翻译

当英文原文更新后，需要重新生成 `.pot` 文件：

```bash
# 重新生成 .pot 模板
cd "/tmp/DeeeeePAW/DeePAW Manual"
sphinx-build -b gettext source source/_build/gettext

# 合并新的翻译条目到现有 .po 文件
# 注意：这会保留已有的翻译，只添加新的条目
```

## 测试翻译

构建后检查：

1. 打开 `_build/html/zh_CN/index.html`
2. 检查翻译是否正确显示
3. 检查是否有遗漏的文本
4. 检查排版和格式是否正确

## 常见问题

### Q: 为什么有些文本没有翻译？
A: 检查对应的 `.po` 文件是否填写了 `msgstr`。空字符串表示未翻译。

### Q: 如何翻译 RST 格式标记？
A: 不要翻译格式标记（如 `**粗体**`、`:ref:`），只翻译文本内容：

```po
msgid "**Important**: See :ref:`theory` for details."
msgstr "**重要**：详见 :ref:`theory`。"
```

### Q: 如何处理变量占位符？
A: 保持占位符不变：

```po
msgid "Page {} of {}"
msgstr "第 {} 页，共 {} 页"
```

## 贡献翻译

如果你完成了翻译并希望贡献：

1. Fork 仓库
2. 提交翻译（`.po` 文件）
3. 创建 Pull Request

联系方式：thsu0407@gmail.com

---

**最后更新**：2026-03-19
**维护者**：DeePAW Team