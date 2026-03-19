#!/bin/bash
# DeePAW Documentation Build Script
# 用于构建中英文双语文档

set -e  # 遇到错误立即退出

DOCDIR="/tmp/DeeeeePAW/DeePAW Manual"
SOURCEDIR="source"
BUILDDIR="_build/html"

echo "================================"
echo "DeePAW Documentation Builder"
echo "================================"
echo ""

# 检查是否在正确的目录
if [ ! -f "$DOCDIR/$SOURCEDIR/conf.py" ]; then
    echo "Error: conf.py not found. Please check the DOCDIR path."
    exit 1
fi

cd "$DOCDIR"

# 构建英文版本
echo ">>> Building English documentation..."
conda run -n base sphinx-build -b html "$SOURCEDIR" "$BUILDDIR/en"
echo "✓ English documentation built: $BUILDDIR/en"
echo ""

# 构建中文版本
echo ">>> Building Chinese documentation..."
conda run -n base sphinx-build -b html -D language=zh_CN "$SOURCEDIR" "$BUILDDIR/zh_CN"
echo "✓ Chinese documentation built: $BUILDDIR/zh_CN"
echo ""

echo "================================"
echo "Build complete!"
echo "================================"
echo "English version: file://$(pwd)/$BUILDDIR/en/index.html"
echo "Chinese version: file://$(pwd)/$BUILDDIR/zh_CN/index.html"
echo ""
echo "Note: Chinese translations need to be added to source/locale/zh_CN/LC_MESSAGES/*.po"