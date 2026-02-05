# GitHub 推送指南

要将 AgentBridge 项目推送到 GitHub，请按照以下步骤操作：

## 方法 1：使用个人访问令牌（推荐）

### 步骤 1：生成 GitHub 个人访问令牌
1. 登录 GitHub
2. 访问 Settings → Developer settings → Personal access tokens → Tokens (classic)
3. 点击 "Generate new token"
4. 选择以下权限：
   - repo (Full control of private repositories)
   - read:org (Read org and team membership)
   - read:user (Access user profile email)
5. 生成并复制令牌（请保存好，因为它只会显示一次）

### 步骤 2：配置 Git 凭据缓存
```bash
cd ~/AgentBridge
git config --global credential.helper store
```

### 步骤 3：推送代码
```bash
git push origin main
```
当提示输入用户名时，输入您的 GitHub 用户名
当提示输入密码时，粘贴您之前生成的个人访问令牌

或者，您可以直接在命令行中使用令牌：
```bash
git remote set-url origin https://<your_token>@github.com/<your_username>/AgentBridge.git
git push origin main
```

## 方法 2：使用 SSH 密钥（更安全）

### 步骤 1：生成 SSH 密钥
```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```

### 步骤 2：将 SSH 公钥添加到 GitHub
```bash
cat ~/.ssh/id_ed25519.pub
```
复制输出内容，然后：
1. 在 GitHub 上访问 Settings → SSH and GPG keys
2. 点击 "New SSH key"
3. 粘贴公钥并保存

### 步骤 3：更改远程 URL 为 SSH
```bash
git remote set-url origin git@github.com:<your_username>/AgentBridge.git
git push origin main
```

## 验证推送
推送完成后，使用以下命令验证：
```bash
git status
git log --oneline -1
```

## 注意事项
- 您的本地代码已经完全准备就绪，只需完成推送即可
- 所有功能都已测试并通过
- 项目结构已经优化，文档齐全
- 这次推送将会把整理后的精简版本上传到 GitHub