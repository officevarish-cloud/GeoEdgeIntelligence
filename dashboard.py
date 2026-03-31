import os
import json
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import pandas as pd
from datetime import datetime, timedelta
import logging

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== DATA MODELS ====================

class GeopoliticalEvent:
    def __init__(self, event_id, title, description, region, sector, severity, source, timestamp):
        self.event_id = event_id
        self.title = title
        self.description = description
        self.region = region
        self.sector = sector
        self.severity = severity  # critical, high, medium, low
        self.source = source
        self.timestamp = timestamp
        self.impact_score = self._calculate_impact()
    
    def _calculate_impact(self):
        severity_map = {"critical": 100, "high": 75, "medium": 50, "low": 25}
        return severity_map.get(self.severity, 0)
    
    def to_dict(self):
        return {
            "event_id": self.event_id,
            "title": self.title,
            "description": self.description,
            "region": self.region,
            "sector": self.sector,
            "severity": self.severity,
            "source": self.source,
            "timestamp": self.timestamp,
            "impact_score": self.impact_score
        }

class RiskAssessment:
    def __init__(self, assessment_id, geopolitical_event, risk_type, probability, potential_impact):
        self.assessment_id = assessment_id
        self.event = geopolitical_event
        self.risk_type = risk_type  # financial, operational, strategic, reputational
        self.probability = probability  # 0-100
        self.potential_impact = potential_impact  # 0-100
        self.risk_level = self._calculate_risk_level()
    
    def _calculate_risk_level(self):
        combined_score = (self.probability + self.potential_impact) / 2
        if combined_score >= 70:
            return "critical"
        elif combined_score >= 50:
            return "high"
        elif combined_score >= 30:
            return "medium"
        else:
            return "low"
    
    def to_dict(self):
        return {
            "assessment_id": self.assessment_id,
            "event_id": self.event.event_id,
            "risk_type": self.risk_type,
            "probability": self.probability,
            "potential_impact": self.potential_impact,
            "risk_level": self.risk_level,
            "overall_score": (self.probability + self.potential_impact) / 2
        }

class Scenario:
    def __init__(self, scenario_id, title, description, affected_sectors, timeline, likelihood, mitigation_strategies):
        self.scenario_id = scenario_id
        self.title = title
        self.description = description
        self.affected_sectors = affected_sectors
        self.timeline = timeline
        self.likelihood = likelihood
        self.mitigation_strategies = mitigation_strategies
    
    def to_dict(self):
        return {
            "scenario_id": self.scenario_id,
            "title": self.title,
            "description": self.description,
            "affected_sectors": self.affected_sectors,
            "timeline": self.timeline,
            "likelihood": self.likelihood,
            "mitigation_strategies": self.mitigation_strategies
        }

# ==================== MOCK DATA ====================

def get_mock_events():
    return [
        GeopoliticalEvent("EVT001", "Tariff Escalation on Textiles", "New tariffs imposed on Indian textile exports", "Global", "Textiles", "high", "Reuters", datetime.now().isoformat()),
        GeopoliticalEvent("EVT002", "Trade Agreement Signed", "India-EU trade deal finalized", "Europe", "Manufacturing", "medium", "GDELT", (datetime.now() - timedelta(hours=2)).isoformat()),
        GeopoliticalEvent("EVT003", "Supply Chain Disruption", "Port delays in Middle East affect shipping", "Middle East", "Logistics", "critical", "NewsAPI", (datetime.now() - timedelta(hours=1)).isoformat()),
        GeopoliticalEvent("EVT004", "Regulatory Policy Change", "New data localization rules in Asia-Pacific", "Asia-Pacific", "IT Services", "medium", "Government Feed", (datetime.now() - timedelta(hours=3)).isoformat()),
    ]

def get_mock_risks():
    events = get_mock_events()
    risks = [
        RiskAssessment("RISK001", events[0], "financial", 85, 90),
        RiskAssessment("RISK002", events[1], "operational", 45, 55),
        RiskAssessment("RISK003", events[2], "financial", 95, 85),
        RiskAssessment("RISK004", events[3], "strategic", 60, 70),
    ]
    return risks

def get_mock_scenarios():
    return [
        Scenario("SC001", "Escalating Trade War", "Extended tariff conflicts could reduce exports by 20-30%", ["Textiles", "Pharmaceuticals", "IT"], "3-6 months", "high", ["Diversify markets", "Optimize supply chains", "Invest in automation"]),
        Scenario("SC002", "Supply Chain Realignment", "Regional reshuffling of logistics hubs", ["Logistics", "Manufacturing"], "6-12 months", "medium", ["Build redundancy", "Regional partnerships"]),
        Scenario("SC003", "Regulatory Harmonization", "Positive: Standardized data rules across Asia", ["IT Services", "Finance"], "12+ months", "medium", ["Invest in compliance", "Scale operations"]),
    ]

# ==================== ROUTES ====================

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/api/events', methods=['GET'])
def get_events():
    events = get_mock_events()
    return jsonify([event.to_dict() for event in events])

@app.route('/api/risks', methods=['GET'])
def get_risks():
    risks = get_mock_risks()
    return jsonify([risk.to_dict() for risk in risks])

@app.route('/api/scenarios', methods=['GET'])
def get_scenarios():
    scenarios = get_mock_scenarios()
    return jsonify([scenario.to_dict() for scenario in scenarios])

@app.route('/api/dashboard-summary', methods=['GET'])
def get_dashboard_summary():
    events = get_mock_events()
    risks = get_mock_risks()
    
    critical_count = sum(1 for r in risks if r.risk_level == "critical")
    high_count = sum(1 for r in risks if r.risk_level == "high")
    
    sectors = list(set([e.sector for e in events]))
    regions = list(set([e.region for e in events]))
    
    return jsonify({
        "total_events": len(events),
        "critical_risks": critical_count,
        "high_risks": high_count,
        "affected_sectors": sectors,
        "affected_regions": regions,
        "last_update": datetime.now().isoformat()
    })

@app.route('/api/patterns', methods=['GET'])
def get_patterns():
    return jsonify({
        "emerging_patterns": [
            {"pattern": "Increased tariff activity", "confidence": 0.92, "affected_sectors": ["Textiles", "Manufacturing"]},
            {"pattern": "Supply chain disruptions", "confidence": 0.87, "affected_sectors": ["Logistics", "Pharma"]},
            {"pattern": "Policy convergence in Asia-Pacific", "confidence": 0.78, "affected_sectors": ["IT", "Finance"]},
        ],
        "trend_analysis": {
            "tariff_activity": "↑ Increasing",
            "geopolitical_tension": "↑ Increasing",
            "trade_volume": "↓ Decreasing"
        }
    })

@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    return jsonify([
        {"id": "ALT001", "message": "Critical: Supply chain disruption in Middle East", "severity": "critical", "timestamp": datetime.now().isoformat()},
        {"id": "ALT002", "message": "High: New tariffs on textile exports announced", "severity": "high", "timestamp": (datetime.now() - timedelta(minutes=30)).isoformat()},
        {"id": "ALT003", "message": "Medium: Regulatory changes in data protection", "severity": "medium", "timestamp": (datetime.now() - timedelta(hours=1)).isoformat()},
    ])

# ==================== WEBSOCKET EVENTS ====================

@socketio.on('connect')
def handle_connect():
    logger.info('Client connected')
    emit('response', {'data': 'Connected to real-time dashboard'})

@socketio.on('request_update')
def handle_update(data):
    emit('update', {
        'events': [event.to_dict() for event in get_mock_events()],
        'risks': [risk.to_dict() for risk in get_mock_risks()],
        'timestamp': datetime.now().isoformat()
    }, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)