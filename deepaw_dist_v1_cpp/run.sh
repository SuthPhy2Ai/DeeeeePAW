#!/bin/bash
# DeePAW C++推理引擎启动脚本
# 自动设置环境变量并运行Python脚本

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# 设置库路径
export LD_LIBRARY_PATH="${SCRIPT_DIR}/deepaw:${LD_LIBRARY_PATH}"

# 检查Python版本
PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
if [ "$PYTHON_VERSION" != "3.12" ]; then
    echo "警告: 当前Python版本为 $PYTHON_VERSION，需要Python 3.12"
    echo "尝试激活deepaw环境..."

    # 尝试激活conda环境
    if command -v conda &> /dev/null; then
        source $(conda info --base)/etc/profile.d/conda.sh
        conda activate deepaw 2>/dev/null || conda activate deepaw_test 2>/dev/null
    fi
fi

# 运行Python脚本
python "$@"
