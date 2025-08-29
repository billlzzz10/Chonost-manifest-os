#!/usr/bin/env python3
"""
Mock API Server for Chonost System Testing
สร้าง Mock API Server เพื่อทดสอบ API endpoints โดยไม่ต้องรัน Backend Server จริง
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import time
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Mock data storage
mock_manuscripts = []
mock_analytics = {
    "total_manuscripts": 0,
    "total_words": 0,
    "active_users": 0,
    "ai_requests": 0
}

@app.route('/api/integrated/system/health', methods=['GET'])
def health_check():
    """System health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "services": {
            "backend": "running",
            "database": "connected",
            "ai_service": "available"
        }
    }), 200

@app.route('/api/integrated/manuscripts', methods=['GET'])
def get_manuscripts():
    """Get manuscripts list"""
    user_id = request.args.get('user_id', 'default_user')
    
    user_manuscripts = [m for m in mock_manuscripts if m.get('user_id') == user_id]
    
    return jsonify({
        "manuscripts": user_manuscripts,
        "total": len(user_manuscripts),
        "user_id": user_id
    }), 200

@app.route('/api/integrated/manuscripts', methods=['POST'])
def create_manuscript():
    """Create new manuscript"""
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    manuscript = {
        "id": f"ms_{int(time.time())}",
        "user_id": data.get('user_id', 'default_user'),
        "title": data.get('title', 'Untitled'),
        "content": data.get('content', ''),
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "word_count": len(data.get('content', '').split())
    }
    
    mock_manuscripts.append(manuscript)
    mock_analytics["total_manuscripts"] += 1
    mock_analytics["total_words"] += manuscript["word_count"]
    
    return jsonify(manuscript), 201

@app.route('/api/integrated/ai/analyze-characters', methods=['POST'])
def analyze_characters():
    """AI character analysis"""
    data = request.get_json()
    
    if not data or 'content' not in data:
        return jsonify({"error": "Content required"}), 400
    
    # Mock AI analysis
    characters = [
        {
            "name": "John",
            "role": "Protagonist",
            "description": "Brave knight who protects the kingdom",
            "traits": ["brave", "loyal", "determined"],
            "relationships": ["ally of Mary"]
        },
        {
            "name": "Mary",
            "role": "Supporting Character",
            "description": "Wise wizard who helps John",
            "traits": ["wise", "helpful", "mysterious"],
            "relationships": ["ally of John"]
        }
    ]
    
    return jsonify({
        "characters": characters,
        "analysis": {
            "total_characters": len(characters),
            "main_character": "John",
            "character_diversity": "Good"
        }
    }), 200

@app.route('/api/integrated/ai/analyze-plot', methods=['POST'])
def analyze_plot():
    """AI plot analysis"""
    data = request.get_json()
    
    if not data or 'content' not in data:
        return jsonify({"error": "Content required"}), 400
    
    # Mock plot analysis
    plot_analysis = {
        "plot_points": [
            "Discovery of mysterious map",
            "Journey begins",
            "Search for hidden treasure"
        ],
        "conflicts": [
            "Unknown dangers on the journey",
            "Time pressure to find treasure"
        ],
        "resolution": "Treasure found and kingdom saved",
        "pacing": "Good",
        "tension": "Building"
    }
    
    return jsonify(plot_analysis), 200

@app.route('/api/integrated/ai/writing-assistant', methods=['POST'])
def writing_assistant():
    """Writing assistant"""
    data = request.get_json()
    
    if not data or 'content' not in data:
        return jsonify({"error": "Content required"}), 400
    
    content = data.get('content', '')
    assist_type = data.get('type', 'improve')
    
    # Mock writing suggestions
    suggestions = {
        "improve": "The brave hero cautiously entered the dark cave, his sword gleaming in the dim light.",
        "expand": "The hero walked into the cave. The air was thick with mystery and ancient secrets. His footsteps echoed against the stone walls as he ventured deeper into the unknown.",
        "simplify": "The hero entered the cave."
    }
    
    return jsonify({
        "original": content,
        "suggestion": suggestions.get(assist_type, suggestions["improve"]),
        "type": assist_type,
        "confidence": 0.85
    }), 200

@app.route('/api/integrated/ai/rag-search', methods=['POST'])
def rag_search():
    """RAG search"""
    data = request.get_json()
    
    if not data or 'query' not in data:
        return jsonify({"error": "Query required"}), 400
    
    query = data.get('query', '')
    
    # Mock search results
    results = [
        {
            "content": "John and Mary have a strong friendship built on trust and mutual respect.",
            "source": "manuscript_1",
            "relevance": 0.95,
            "context": "Character relationships"
        },
        {
            "content": "The relationship between the main characters develops throughout the story.",
            "source": "manuscript_2", 
            "relevance": 0.87,
            "context": "Character development"
        }
    ]
    
    return jsonify({
        "query": query,
        "results": results,
        "total_results": len(results),
        "search_time": 0.15
    }), 200

@app.route('/api/integrated/analytics/overview', methods=['GET'])
def analytics_overview():
    """Analytics overview"""
    return jsonify({
        "analytics": mock_analytics,
        "trends": {
            "manuscripts_created_today": 3,
            "words_written_today": 1500,
            "ai_requests_today": 12
        },
        "performance": {
            "response_time_avg": 0.25,
            "uptime": 99.9,
            "active_sessions": 5
        }
    }), 200

@app.route('/', methods=['GET'])
def root():
    """Root endpoint"""
    return jsonify({
        "message": "Chonost Mock API Server",
        "version": "1.0.0",
        "status": "running",
        "endpoints": [
            "/api/integrated/system/health",
            "/api/integrated/manuscripts",
            "/api/integrated/ai/analyze-characters",
            "/api/integrated/ai/analyze-plot", 
            "/api/integrated/ai/writing-assistant",
            "/api/integrated/ai/rag-search",
            "/api/integrated/analytics/overview"
        ]
    }), 200

if __name__ == '__main__':
    print("🚀 Starting Chonost Mock API Server...")
    print("🌐 Server URL: http://localhost:5000")
    print("📊 Health Check: http://localhost:5000/api/integrated/system/health")
    print("📝 Press Ctrl+C to stop the server")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
