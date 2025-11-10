# Vercel API部署文件

## 📁 文件说明

### api/index.py
- API服务主文件
- 为Vercel Serverless环境优化
- 包含爬虫逻辑和数据缓存

### requirements.txt
- Python依赖包列表
- Flask、BeautifulSoup等

### vercel.json
- Vercel部署配置文件
- 定义路由和构建设置

## 🚀 部署方法

### 方法1: Vercel CLI（推荐）
```bash
# 安装CLI
npm i -g vercel

# 进入此目录
cd vercel_deployment

# 部署
vercel

# 按提示操作
```

### 方法2: GitHub集成
1. 将此文件夹推送到GitHub仓库
2. 在Vercel Dashboard导入该仓库
3. Vercel自动部署

### 方法3: 直接上传
1. 在Vercel Dashboard创建新项目
2. 选择 "Import Git Repository"
3. 上传这些文件

## 📊 API端点

部署后可访问：
- `/api/matches` - 获取比赛数据
- `/api/health` - 健康检查
- `/` - API信息

## ⚙️ 环境变量（可选）

在Vercel项目设置中可配置：
- `CACHE_DURATION` - 缓存时长（秒）
- `CORS_ORIGINS` - 允许的跨域来源

## ✅ 测试

部署完成后，访问：
```
https://your-project.vercel.app/api/matches
```

应返回JSON格式的比赛数据。