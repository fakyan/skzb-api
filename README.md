# skzb.cc API

## 文件说明
- `app.py` - API主文件
- `requirements.txt` - Python依赖

## Render.com 部署配置
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn --bind 0.0.0.0:$PORT app:app`

## API端点
- `/api/health` - 健康检查
- `/api/matches` - 获取比赛数据
