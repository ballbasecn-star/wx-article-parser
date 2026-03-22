# 开发流程

## 开发流程步骤

### 1. 开始任务前

1. 阅读当前阶段文档 `docs/roadmap/current.md`
2. 确认要完成的任务优先级
3. 了解相关模块文档

### 2. 开发中

1. 创建功能分支（如需要）
2. 编写代码实现
3. 编写/更新相关测试
4. 本地验证功能

### 3. 提交前

1. 运行最小验证
2. 更新相关文档
3. 提交代码

### 4. 提交后

1. 确认提交正确
2. 等待人工确认是否push

## 最小验证要求

### 后端

```bash
# 语法检查
python -m py_compile src/**/*.py

# 运行测试（如有）
pytest tests/

# 启动服务验证
python src/main.py
```

### 前端

```bash
# 类型检查（如有）
npm run type-check

# 构建检查
npm run build

# 开发服务器验证
npm run dev
```

## Commit Message 规范

### 格式

```
<type>: <subject>

<body> (可选)
```

### Type 类型

| 类型 | 说明 | 示例 |
|-----|------|------|
| feat | 新功能 | feat: 添加文章解析API |
| fix | 修复bug | fix: 修复图片提取失败问题 |
| docs | 文档更新 | docs: 更新API文档 |
| refactor | 重构 | refactor: 重构解析器模块 |
| chore | 构建/工具 | chore: 更新依赖版本 |
| test | 测试 | test: 添加解析器单元测试 |
| style | 代码格式 | style: 格式化代码 |

### Subject 要求

- 使用中文描述
- 描述结果，不是动作
- 不超过50字符

### 示例

```
feat: 添加文章解析API

- 支持公众号文章链接解析
- 提取标题、作者、正文
- 提取文章图片列表
```

## 自动 Commit 规则

AI可自动执行 `git add` 和 `git commit`，但：

1. 不自动 `git push`
2. 确保提交内容逻辑完整
3. 不相关的改动分开提交
4. 提交前必须通过最小验证

## 开发环境设置

### 后端环境

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

### 前端环境

```bash
cd frontend
npm install
```

### Docker 环境

```bash
docker-compose up -d
```