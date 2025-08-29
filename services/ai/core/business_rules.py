"""
Business Rules System for Chonost

This module implements business rules for measuring KPIs and setting status indicators
based on thresholds for Error (Red), Warning (Yellow), and OK (Green) states.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
import sqlite3

logger = logging.getLogger(__name__)

class RuleScope(Enum):
    """Scope of business rules"""
    EVENT = "event"           # Measure as activity
    CASE = "case"             # Measure as case (one case = one result)
    PROCESS = "process"       # Measure entire process
    EDGE = "edge"             # Measure along process map edges

class SeverityLevel(Enum):
    """Severity levels for business rules"""
    ERROR = "error"           # Red - exceeds threshold
    WARNING = "warning"       # Yellow - approaching threshold
    OK = "ok"                 # Green - within acceptable range

@dataclass
class Threshold:
    """Threshold configuration for business rules"""
    error_threshold: float    # Value that triggers ERROR status
    warning_threshold: float  # Value that triggers WARNING status
    unit: str = ""           # Unit of measurement (e.g., "days", "seconds", "count")
    
    def evaluate(self, value: float) -> SeverityLevel:
        """Evaluate value against thresholds"""
        if value > self.error_threshold:
            return SeverityLevel.ERROR
        elif value > self.warning_threshold:
            return SeverityLevel.WARNING
        else:
            return SeverityLevel.OK

@dataclass
class BusinessRule:
    """Business rule definition"""
    id: str
    name: str
    description: str
    scope: RuleScope
    filter_condition: Optional[str] = None
    output_expression: str = ""  # e.g., "AVG(Duration())", "COUNT(*)"
    threshold: Threshold = field(default_factory=lambda: Threshold(60, 40))
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

@dataclass
class RuleResult:
    """Result of business rule evaluation"""
    rule_id: str
    rule_name: str
    scope: RuleScope
    calculated_value: float
    severity: SeverityLevel
    threshold: Threshold
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

class BusinessRulesEngine:
    """Engine for evaluating business rules"""
    
    def __init__(self, db_path: str = "business_rules.db"):
        self.db_path = db_path
        self.rules: Dict[str, BusinessRule] = {}
        self._init_database()
        self._load_rules()
    
    def _init_database(self):
        """Initialize business rules database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create business rules table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS business_rules (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                scope TEXT NOT NULL,
                filter_condition TEXT,
                output_expression TEXT NOT NULL,
                error_threshold REAL NOT NULL,
                warning_threshold REAL NOT NULL,
                unit TEXT,
                enabled INTEGER DEFAULT 1,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        
        # Create rule results table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rule_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rule_id TEXT NOT NULL,
                rule_name TEXT NOT NULL,
                scope TEXT NOT NULL,
                calculated_value REAL NOT NULL,
                severity TEXT NOT NULL,
                error_threshold REAL NOT NULL,
                warning_threshold REAL NOT NULL,
                unit TEXT,
                timestamp TEXT NOT NULL,
                metadata TEXT,
                FOREIGN KEY (rule_id) REFERENCES business_rules (id)
            )
        """)
        
        # Insert default rules if table is empty
        cursor.execute("SELECT COUNT(*) FROM business_rules")
        if cursor.fetchone()[0] == 0:
            self._insert_default_rules(cursor)
        
        conn.commit()
        conn.close()
    
    def _insert_default_rules(self, cursor):
        """Insert default business rules"""
        default_rules = [
            {
                "id": "response_time",
                "name": "AI Response Time",
                "description": "Measure average AI response time",
                "scope": RuleScope.EVENT.value,
                "output_expression": "AVG(latency_ms)",
                "error_threshold": 5000.0,  # 5 seconds
                "warning_threshold": 3000.0,  # 3 seconds
                "unit": "milliseconds"
            },
            {
                "id": "cost_per_request",
                "name": "Cost per Request",
                "description": "Measure average cost per AI request",
                "scope": RuleScope.EVENT.value,
                "output_expression": "AVG(cost_estimate)",
                "error_threshold": 0.01,  # $0.01
                "warning_threshold": 0.005,  # $0.005
                "unit": "USD"
            },
            {
                "id": "success_rate",
                "name": "Request Success Rate",
                "description": "Measure percentage of successful requests",
                "scope": RuleScope.PROCESS.value,
                "output_expression": "(COUNT(successful) / COUNT(*)) * 100",
                "error_threshold": 85.0,  # 85%
                "warning_threshold": 95.0,  # 95%
                "unit": "percentage"
            },
            {
                "id": "context_accuracy",
                "name": "Context Injection Accuracy",
                "description": "Measure accuracy of context injection",
                "scope": RuleScope.EVENT.value,
                "output_expression": "AVG(context_accuracy)",
                "error_threshold": 70.0,  # 70%
                "warning_threshold": 85.0,  # 85%
                "unit": "percentage"
            }
        ]
        
        for rule in default_rules:
            cursor.execute("""
                INSERT INTO business_rules 
                (id, name, description, scope, output_expression, error_threshold, 
                 warning_threshold, unit, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                rule["id"], rule["name"], rule["description"], rule["scope"],
                rule["output_expression"], rule["error_threshold"], rule["warning_threshold"],
                rule["unit"], datetime.now().isoformat(), datetime.now().isoformat()
            ))
    
    def _load_rules(self):
        """Load business rules from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM business_rules WHERE enabled = 1")
        rows = cursor.fetchall()
        
        for row in rows:
            rule = BusinessRule(
                id=row[0],
                name=row[1],
                description=row[2],
                scope=RuleScope(row[3]),
                filter_condition=row[4],
                output_expression=row[5],
                threshold=Threshold(
                    error_threshold=row[6],
                    warning_threshold=row[7],
                    unit=row[8] or ""
                ),
                enabled=bool(row[9]),
                created_at=datetime.fromisoformat(row[10]),
                updated_at=datetime.fromisoformat(row[11])
            )
            self.rules[rule.id] = rule
        
        conn.close()
        logger.info(f"Loaded {len(self.rules)} business rules")
    
    async def evaluate_rule(self, rule_id: str, data: List[Dict[str, Any]]) -> Optional[RuleResult]:
        """Evaluate a specific business rule"""
        if rule_id not in self.rules:
            logger.warning(f"Rule {rule_id} not found")
            return None
        
        rule = self.rules[rule_id]
        
        try:
            # Calculate value based on output expression
            calculated_value = self._calculate_value(rule.output_expression, data)
            
            # Evaluate against threshold
            severity = rule.threshold.evaluate(calculated_value)
            
            # Create result
            result = RuleResult(
                rule_id=rule.id,
                rule_name=rule.name,
                scope=rule.scope,
                calculated_value=calculated_value,
                severity=severity,
                threshold=rule.threshold,
                timestamp=datetime.now(),
                metadata={"data_count": len(data)}
            )
            
            # Save result to database
            await self._save_result(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error evaluating rule {rule_id}: {e}")
            return None
    
    def _calculate_value(self, expression: str, data: List[Dict[str, Any]]) -> float:
        """Calculate value based on expression"""
        if not data:
            return 0.0
        
        # Simple expression parser for common operations
        expression = expression.upper().strip()
        
        if expression.startswith("AVG(") and expression.endswith(")"):
            field = expression[4:-1].lower()
            values = [item.get(field, 0) for item in data if isinstance(item.get(field), (int, float))]
            return sum(values) / len(values) if values else 0.0
        
        elif expression.startswith("COUNT(") and expression.endswith(")"):
            field = expression[6:-1].lower()
            if field == "*":
                return len(data)
            else:
                return sum(1 for item in data if item.get(field) is not None)
        
        elif expression.startswith("SUM(") and expression.endswith(")"):
            field = expression[4:-1].lower()
            values = [item.get(field, 0) for item in data if isinstance(item.get(field), (int, float))]
            return sum(values)
        
        elif expression.startswith("MAX(") and expression.endswith(")"):
            field = expression[4:-1].lower()
            values = [item.get(field, 0) for item in data if isinstance(item.get(field), (int, float))]
            return max(values) if values else 0.0
        
        elif expression.startswith("MIN(") and expression.endswith(")"):
            field = expression[3:-1].lower()
            values = [item.get(field, 0) for item in data if isinstance(item.get(field), (int, float))]
            return min(values) if values else 0.0
        
        else:
            # Default to first value or 0
            return data[0].get(expression.lower(), 0) if data else 0.0
    
    async def _save_result(self, result: RuleResult):
        """Save rule result to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO rule_results 
            (rule_id, rule_name, scope, calculated_value, severity, 
             error_threshold, warning_threshold, unit, timestamp, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            result.rule_id, result.rule_name, result.scope.value,
            result.calculated_value, result.severity.value,
            result.threshold.error_threshold, result.threshold.warning_threshold,
            result.threshold.unit, result.timestamp.isoformat(),
            json.dumps(result.metadata)
        ))
        
        conn.commit()
        conn.close()
    
    async def evaluate_all_rules(self, data: List[Dict[str, Any]]) -> List[RuleResult]:
        """Evaluate all enabled business rules"""
        results = []
        
        for rule_id in self.rules:
            result = await self.evaluate_rule(rule_id, data)
            if result:
                results.append(result)
        
        return results
    
    def get_rule_status_summary(self) -> Dict[str, Any]:
        """Get summary of all rule statuses"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT rule_id, rule_name, severity, calculated_value, timestamp
            FROM rule_results 
            WHERE timestamp = (
                SELECT MAX(timestamp) 
                FROM rule_results r2 
                WHERE r2.rule_id = rule_results.rule_id
            )
            ORDER BY timestamp DESC
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        summary = {
            "total_rules": len(self.rules),
            "evaluated_rules": len(rows),
            "status_breakdown": {
                "error": 0,
                "warning": 0,
                "ok": 0
            },
            "rules": []
        }
        
        for row in rows:
            rule_id, rule_name, severity, value, timestamp = row
            summary["status_breakdown"][severity] += 1
            
            summary["rules"].append({
                "id": rule_id,
                "name": rule_name,
                "severity": severity,
                "value": value,
                "timestamp": timestamp
            })
        
        return summary
    
    def create_rule(self, rule: BusinessRule) -> bool:
        """Create a new business rule"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO business_rules 
                (id, name, description, scope, filter_condition, output_expression,
                 error_threshold, warning_threshold, unit, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                rule.id, rule.name, rule.description, rule.scope.value,
                rule.filter_condition, rule.output_expression,
                rule.threshold.error_threshold, rule.threshold.warning_threshold,
                rule.threshold.unit, rule.created_at.isoformat(), rule.updated_at.isoformat()
            ))
            
            conn.commit()
            conn.close()
            
            # Add to memory
            self.rules[rule.id] = rule
            
            logger.info(f"Created business rule: {rule.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating rule: {e}")
            return False
    
    def update_rule(self, rule_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing business rule"""
        if rule_id not in self.rules:
            return False
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Build update query dynamically
            set_clauses = []
            values = []
            
            for key, value in updates.items():
                if key in ["name", "description", "scope", "filter_condition", "output_expression", "enabled"]:
                    set_clauses.append(f"{key} = ?")
                    values.append(value)
                elif key == "threshold" and isinstance(value, Threshold):
                    set_clauses.extend(["error_threshold = ?", "warning_threshold = ?", "unit = ?"])
                    values.extend([value.error_threshold, value.warning_threshold, value.unit])
            
            set_clauses.append("updated_at = ?")
            values.append(datetime.now().isoformat())
            values.append(rule_id)
            
            query = f"UPDATE business_rules SET {', '.join(set_clauses)} WHERE id = ?"
            cursor.execute(query, values)
            
            conn.commit()
            conn.close()
            
            # Update in memory
            self._load_rules()
            
            logger.info(f"Updated business rule: {rule_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating rule: {e}")
            return False

# Global instance
business_rules_engine = BusinessRulesEngine()
