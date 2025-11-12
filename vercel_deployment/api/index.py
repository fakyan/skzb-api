#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SKZB体育直播API - Vercel修复版
"""

from flask import Flask, jsonify
from flask_cors import CORS
import requests
import re
from datetime import datetime
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)

matches_cache = {
    'update_time': '',
    'total': 0,
    'matches': [],
    'last_fetch': 0
}

CACHE_DURATION = 300

def fetch_zqbaba_data():
    url = "https://zqbaba.org"
    try:
        resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
        resp.encoding = 'gb2312'
        html = resp.text
        soup = BeautifulSoup(html, 'html.parser')
        
        date_match = re.search(r'(\d{4})-\s*(?:<[^>]+>)?(\d{1,2})(?:</[^>]+>)?\s*-(\d{1,2})\s*星期', html)
        if not date_match:
            return []
        
        current_date = f"{date_match.group(1)}-{date_match.group(2)}-{date_match.group(3)}"
        matches = []
        clean_html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
        clean_html = re.sub(r'<style[^>]*>.*?</style>', '', clean_html, flags=re.DOTALL)
        pattern = r'(\d{1,2}:\d{2})\s+([^<\n]{10,100}?VS[^<\n]{5,50})'
        
        match_positions = []
        for match in re.finditer(pattern, clean_html):
            time_str = match.group(1)
            content = match.group(2).strip()
            content = re.sub(r'&[a-z]+;', '', content)
            content = ' '.join(content.split())
            
            league = ''
            league_patterns = [
                r'英超第\d+轮', r'西甲第\d+轮', r'德甲第\d+轮', r'意甲第\d+轮', r'法甲第\d+轮',
                r'NBA常规赛', r'CBA联赛', r'欧冠', r'欧联',
                r'ATP[^\s]*', r'斯诺克[^\s]*', r'全运会[^\s]*', r'羽毛球[^\s]*', r'NFL[^\s]*'
            ]
            
            for lp in league_patterns:
                lm = re.search(lp, content)
                if lm:
                    league = lm.group(0)
                    break
            
            vs_match = re.search(r'([^\s]{2,25})\s+VS\s+([^\s]{2,25})', content)
            teams = f"{vs_match.group(1)} VS {vs_match.group(2)}" if vs_match else ''
            title = f"{league} {teams}".strip() if league else teams
            
            match_positions.append({
                'match_data': {
                    'id': f"{current_date}_{time_str}_{len(matches)}",
                    'date': current_date,
                    'time': time_str,
                    'datetime': f"{current_date} {time_str}",
                    'league': league,
                    'teams': teams,
                    'title': title,
                    'links': [],
                    'link_count': 0
                }
            })
        
        all_links = soup.find_all('a', href=True)
        live_links = []
        
        for link in all_links:
            href = link.get('href', '')
            text = link.get_text().strip()
            if any(keyword in href.lower() for keyword in ['live', 'play', 'stream', 'video']) or \
               any(platform in href.lower() for platform in ['cctv', 'migu', 'tencent', 'qq', 'youku', 'iqiyi']):
                if not any(exclude in href.lower() for exclude in ['javascript', 'void', '#', 'mailto']):
                    live_links.append({'url': href, 'text': text})
        
        links_per_match = max(len(live_links) // max(len(match_positions), 1), 1)
        
        for i, match_info in enumerate(match_positions):
            match_data = match_info['match_data']
            start_idx = i * links_per_match
            end_idx = min(start_idx + 3, len(live_links))
            assigned_links = live_links[start_idx:end_idx] if start_idx < len(live_links) else []
            
            for link_idx, link in enumerate(assigned_links):
                if 'cctv' in link['url'].lower():
                    link_name = 'CCTV'
                elif 'migu' in link['url'].lower():
                    link_name = '咪咕'
                elif any(x in link['url'].lower() for x in ['tencent', 'qq']):
                    link_name = '腾讯'
                elif 'youku' in link['url'].lower():
                    link_name = '优酷'
                elif 'iqiyi' in link['url'].lower():
                    link_name = '爱奇艺'
                else:
                    link_name = f"直播信号{link_idx + 1}"
                
                match_data['links'].append({'name': link_name, 'url': link['url']})
            
            match_data['link_count'] = len(match_data['links'])
            matches.append(match_data)
        
        return matches
    except Exception as e:
        print(f"爬取失败: {e}")
        return []

def get_cached_data():
    global matches_cache
    current_time = datetime.now().timestamp()
    if current_time - matches_cache.get('last_fetch', 0) > CACHE_DURATION:
        matches = fetch_zqbaba_data()
        matches_cache = {
            'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total': len(matches),
            'matches': matches,
            'last_fetch': current_time
        }
    return matches_cache

@app.route('/api/matches', methods=['GET'])
def get_matches():
    try:
        data = get_cached_data()
        return jsonify({'success': True, **data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e), 'matches': [], 'total': 0}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')})

@app.route('/', methods=['GET'])
def index():
    return jsonify({
        'service': 'SKZB体育直播API',
        'version': '2.0',
        'endpoints': ['GET /api/matches', 'GET /api/health']
    })
