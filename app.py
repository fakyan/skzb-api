#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
skzb.cc API - Render.com 优化版本
体育直播导航API服务
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
import logging
import os
from urllib.parse import urljoin

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # 允许跨域请求

class ZQBabaSpider:
    """足球吧吧数据爬虫"""
    
    def __init__(self):
        self.base_url = 'http://zqbaba.org'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
    
    def fetch_matches(self):
        """获取比赛数据"""
        try:
            logger.info('开始获取比赛数据...')
            
            response = requests.get(self.base_url, headers=self.headers, timeout=15)
            response.encoding = 'gb2312'
            
            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find('table', {'id': 'table157'})
            
            if not table:
                logger.error('未找到比赛数据表格')
                return []
            
            matches = self._parse_matches(table)
            logger.info(f'成功获取 {len(matches)} 场比赛数据')
            
            return matches
            
        except Exception as e:
            logger.error(f'获取比赛数据失败: {str(e)}')
            return []
    
    def _parse_matches(self, table):
        """解析比赛数据"""
        matches = []
        rows = table.find_all('tr')
        current_match = None
        
        for row in rows:
            td = row.find('td')
            if not td:
                continue
            
            text = td.get_text().strip()
            
            # 检查是否为比赛标题（包含时间和VS）
            if re.search(r'\d{2}:\d{2}.*VS', text, re.IGNORECASE):
                # 保存上一场比赛
                if current_match:
                    matches.append(current_match)
                
                current_match = self._parse_match_info(text)
            
            # 检查是否为直播链接行
            elif '直播' in text and current_match:
                # 由于链接是动态生成的，这里添加占位符
                # 实际项目中需要使用Selenium获取真实链接
                current_match['links'].append({
                    'name': text,
                    'url': '#',  # 占位符，需要动态获取
                    'type': 'placeholder',
                    'description': '需要点击获取真实链接'
                })
        
        # 添加最后一场比赛
        if current_match:
            matches.append(current_match)
        
        return matches
    
    def _parse_match_info(self, text):
        """解析单场比赛信息"""
        # 解析时间
        time_match = re.search(r'^(\d{2}:\d{2})', text)
        time_str = time_match.group(1) if time_match else '未知'
        
        # 解析VS对阵
        vs_match = re.search(r'(.+?)\s*VS\s*(.+)', text, re.IGNORECASE)
        if not vs_match:
            return None
        
        full_before = vs_match.group(1).strip()
        team2 = vs_match.group(2).strip()
        
        # 提取联赛和队伍1
        league, team1 = self._extract_league_and_team(full_before)
        
        return {
            'time': time_str,
            'league': league,
            'team1': team1,
            'team2': team2,
            'teams': f'{team1} VS {team2}',
            'links': [],
            'status': 'upcoming',
            'timestamp': datetime.now().isoformat()
        }
    
    def _extract_league_and_team(self, full_text):
        """提取联赛和队伍信息"""
        league_patterns = [
            (r'.*?(世预赛[^\s]*)', '世预赛'),
            (r'.*?(NBA[^\s]*)', 'NBA'),
            (r'.*?(ATP[^\s]*)', 'ATP'),
            (r'.*?(NFL[^\s]*)', 'NFL'),
            (r'.*?(足球友谊赛)', '友谊赛'),
            (r'.*?(全运会[^\s]*)', '全运会'),
            (r'.*?(英超)', '英超'),
            (r'.*?(西甲)', '西甲'),
            (r'.*?(意甲)', '意甲'),
            (r'.*?(德甲)', '德甲'),
            (r'.*?(法甲)', '法甲')
        ]
        
        league = ''
        team1 = full_text
        
        for pattern, league_name in league_patterns:
            if re.search(pattern, full_text):
                league = league_name
                # 提取队伍1（移除时间和联赛信息）
                temp = re.sub(r'^\d{2}:\d{2}\s*', '', full_text)  # 移除时间
                temp = re.sub(pattern.replace('.*?', ''), '', temp).strip()  # 移除联赛
                if temp:
                    team1 = temp
                break
        
        # 如果没有识别到联赛，直接提取队伍1
        if not league:
            team1_match = re.search(r'\d{2}:\d{2}\s*(.+)', full_text)
            if team1_match:
                team1 = team1_match.group(1).strip()
        
        return league, team1

# 创建爬虫实例
spider = ZQBabaSpider()

@app.route('/', methods=['GET'])
def home():
    """API首页"""
    return jsonify({
        'success': True,
        'message': 'skzb.cc 体育直播导航API',
        'version': '1.0.0',
        'endpoints': {
            '/api/matches': 'GET - 获取比赛数据',
            '/api/health': 'GET - 健康检查'
        },
        'timestamp': datetime.now().isoformat(),
        'status': 'running'
    })

@app.route('/api/matches', methods=['GET'])
def get_matches():
    """获取比赛数据API"""
    try:
        matches = spider.fetch_matches()
        
        response = {
            'success': True,
            'message': '数据获取成功',
            'timestamp': datetime.now().isoformat(),
            'total_matches': len(matches),
            'matches': matches,
            'source': 'zqbaba.org',
            'update_interval': '5分钟'
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f'API错误: {str(e)}')
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        'success': True,
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'uptime': 'running'
    })

@app.route('/api/test', methods=['GET'])
def test_connection():
    """测试数据源连接"""
    try:
        response = requests.get('http://zqbaba.org', timeout=10)
        return jsonify({
            'success': True,
            'source_status': response.status_code,
            'source_available': response.status_code == 200,
            'response_size': len(response.content),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# 错误处理
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'API端点未找到',
        'available_endpoints': ['/api/matches', '/api/health', '/api/test'],
        'timestamp': datetime.now().isoformat()
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': '服务器内部错误',
        'timestamp': datetime.now().isoformat()
    }), 500

if __name__ == '__main__':
    # Render.com 会自动设置PORT环境变量
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)