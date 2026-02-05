#!/bin/bash

# AgentBridge 一键推送脚本
# 使用此脚本推送代码到 GitHub

echo "🚀 AgentBridge 一键推送脚本"
echo ""

# 检查当前目录是否为 Git 仓库
if [ ! -d ".git" ]; then
    echo "❌ 错误: 当前目录不是 Git 仓库"
    exit 1
fi

echo "✅ 检测到 Git 仓库"
echo ""

# 显示当前状态
echo "📋 当前 Git 状态:"
git status --short
echo ""

# 显示分支信息
echo "🏷️  当前分支:"
git branch --show-current
echo ""

# 显示最近的提交
echo "📝 最近提交:"
git log --oneline -1
echo ""

# 检查是否有待提交的更改
UNCOMMITTED_CHANGES=$(git status --porcelain | wc -l)
if [ $UNCOMMITTED_CHANGES -gt 0 ]; then
    echo "⚠️  检测到未提交的更改，正在提交..."
    git add .
    git commit -m "feat: Final AgentBridge project structure with all features"
    echo "✅ 更改已提交"
    echo ""
fi

echo "📡 开始推送至 GitHub..."
echo "💡 提示: 如果这是第一次推送，您可能需要提供 GitHub 凭据"
echo "💡 推荐使用 GitHub 个人访问令牌进行身份验证"
echo ""

# 尝试推送
if git push origin main; then
    echo ""
    echo "🎉 推送成功!"
    echo ""
    echo "📊 推送统计:"
    git log --oneline --since="1 hour ago"
    echo ""
    echo "✅ AgentBridge 项目已成功推送到 GitHub"
    echo "🔗 您的项目现在可以在以下地址访问: $(git remote get-url origin)"
else
    echo ""
    echo "❌ 推送失败 - 请检查您的 GitHub 凭据"
    echo ""
    echo "🔧 解决方案:"
    echo "   1. 确保您已在 GitHub 上创建了 AgentBridge 仓库"
    echo "   2. 确保您具有推送权限"
    echo "   3. 使用 GitHub 个人访问令牌进行身份验证"
    echo "   4. 查看 GITHUB_PUSH_GUIDE.md 获取详细说明"
fi

echo ""
echo "📋 最终 Git 状态:"
git status