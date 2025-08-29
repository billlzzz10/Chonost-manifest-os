"""
Business Rules API Routes

This module provides API endpoints for managing and evaluating business rules.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import asyncio

from src.core.business_rules import (
    BusinessRule, RuleResult, Threshold, RuleScope, SeverityLevel,
    business_rules_engine
)

router = APIRouter()

# Pydantic models for API requests/responses
class ThresholdModel(BaseModel):
    error_threshold: float = Field(..., description="Value that triggers ERROR status")
    warning_threshold: float = Field(..., description="Value that triggers WARNING status")
    unit: str = Field("", description="Unit of measurement")

class BusinessRuleCreate(BaseModel):
    id: str = Field(..., description="Unique rule identifier")
    name: str = Field(..., description="Rule name")
    description: str = Field("", description="Rule description")
    scope: RuleScope = Field(..., description="Rule scope")
    filter_condition: Optional[str] = Field(None, description="Filter condition")
    output_expression: str = Field(..., description="Output expression (e.g., AVG(latency_ms))")
    threshold: ThresholdModel = Field(..., description="Threshold configuration")
    enabled: bool = Field(True, description="Whether rule is enabled")

class BusinessRuleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    scope: Optional[RuleScope] = None
    filter_condition: Optional[str] = None
    output_expression: Optional[str] = None
    threshold: Optional[ThresholdModel] = None
    enabled: Optional[bool] = None

class RuleResultResponse(BaseModel):
    rule_id: str
    rule_name: str
    scope: RuleScope
    calculated_value: float
    severity: SeverityLevel
    threshold: ThresholdModel
    timestamp: datetime
    metadata: Dict[str, Any]

class RuleStatusSummary(BaseModel):
    total_rules: int
    evaluated_rules: int
    status_breakdown: Dict[str, int]
    rules: List[Dict[str, Any]]

class EvaluationRequest(BaseModel):
    data: List[Dict[str, Any]] = Field(..., description="Data to evaluate against rules")
    rule_ids: Optional[List[str]] = Field(None, description="Specific rules to evaluate (if None, evaluate all)")

@router.get("/", response_model=List[BusinessRule])
async def list_business_rules():
    """List all business rules"""
    return list(business_rules_engine.rules.values())

@router.get("/{rule_id}", response_model=BusinessRule)
async def get_business_rule(rule_id: str):
    """Get a specific business rule"""
    if rule_id not in business_rules_engine.rules:
        raise HTTPException(status_code=404, detail="Business rule not found")
    return business_rules_engine.rules[rule_id]

@router.post("/", response_model=BusinessRule)
async def create_business_rule(rule_data: BusinessRuleCreate):
    """Create a new business rule"""
    # Convert Pydantic model to BusinessRule
    threshold = Threshold(
        error_threshold=rule_data.threshold.error_threshold,
        warning_threshold=rule_data.threshold.warning_threshold,
        unit=rule_data.threshold.unit
    )
    
    rule = BusinessRule(
        id=rule_data.id,
        name=rule_data.name,
        description=rule_data.description,
        scope=rule_data.scope,
        filter_condition=rule_data.filter_condition,
        output_expression=rule_data.output_expression,
        threshold=threshold,
        enabled=rule_data.enabled
    )
    
    success = business_rules_engine.create_rule(rule)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to create business rule")
    
    return rule

@router.put("/{rule_id}", response_model=BusinessRule)
async def update_business_rule(rule_id: str, updates: BusinessRuleUpdate):
    """Update an existing business rule"""
    if rule_id not in business_rules_engine.rules:
        raise HTTPException(status_code=404, detail="Business rule not found")
    
    # Convert updates to dict
    update_dict = updates.dict(exclude_unset=True)
    
    # Convert threshold if provided
    if "threshold" in update_dict:
        threshold_data = update_dict["threshold"]
        update_dict["threshold"] = Threshold(
            error_threshold=threshold_data.error_threshold,
            warning_threshold=threshold_data.warning_threshold,
            unit=threshold_data.unit
        )
    
    success = business_rules_engine.update_rule(rule_id, update_dict)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to update business rule")
    
    return business_rules_engine.rules[rule_id]

@router.delete("/{rule_id}")
async def delete_business_rule(rule_id: str):
    """Delete a business rule (disable it)"""
    if rule_id not in business_rules_engine.rules:
        raise HTTPException(status_code=404, detail="Business rule not found")
    
    success = business_rules_engine.update_rule(rule_id, {"enabled": False})
    if not success:
        raise HTTPException(status_code=400, detail="Failed to delete business rule")
    
    return {"message": "Business rule deleted successfully"}

@router.post("/evaluate", response_model=List[RuleResultResponse])
async def evaluate_rules(request: EvaluationRequest):
    """Evaluate business rules against provided data"""
    if not request.data:
        raise HTTPException(status_code=400, detail="No data provided for evaluation")
    
    results = []
    
    if request.rule_ids:
        # Evaluate specific rules
        for rule_id in request.rule_ids:
            result = await business_rules_engine.evaluate_rule(rule_id, request.data)
            if result:
                results.append(result)
    else:
        # Evaluate all rules
        results = await business_rules_engine.evaluate_all_rules(request.data)
    
    # Convert to response format
    response_results = []
    for result in results:
        threshold_model = ThresholdModel(
            error_threshold=result.threshold.error_threshold,
            warning_threshold=result.threshold.warning_threshold,
            unit=result.threshold.unit
        )
        
        response_results.append(RuleResultResponse(
            rule_id=result.rule_id,
            rule_name=result.rule_name,
            scope=result.scope,
            calculated_value=result.calculated_value,
            severity=result.severity,
            threshold=threshold_model,
            timestamp=result.timestamp,
            metadata=result.metadata
        ))
    
    return response_results

@router.get("/status/summary", response_model=RuleStatusSummary)
async def get_rule_status_summary():
    """Get summary of all rule statuses"""
    summary = business_rules_engine.get_rule_status_summary()
    return RuleStatusSummary(**summary)

@router.get("/status/{rule_id}", response_model=List[RuleResultResponse])
async def get_rule_history(rule_id: str, limit: int = 10):
    """Get evaluation history for a specific rule"""
    if rule_id not in business_rules_engine.rules:
        raise HTTPException(status_code=404, detail="Business rule not found")
    
    # Get history from database
    import sqlite3
    conn = sqlite3.connect(business_rules_engine.db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT rule_id, rule_name, scope, calculated_value, severity,
               error_threshold, warning_threshold, unit, timestamp, metadata
        FROM rule_results 
        WHERE rule_id = ?
        ORDER BY timestamp DESC
        LIMIT ?
    """, (rule_id, limit))
    
    rows = cursor.fetchall()
    conn.close()
    
    # Convert to response format
    results = []
    for row in rows:
        rule_id, rule_name, scope, calculated_value, severity, error_threshold, warning_threshold, unit, timestamp, metadata = row
        
        threshold_model = ThresholdModel(
            error_threshold=error_threshold,
            warning_threshold=warning_threshold,
            unit=unit or ""
        )
        
        results.append(RuleResultResponse(
            rule_id=rule_id,
            rule_name=rule_name,
            scope=RuleScope(scope),
            calculated_value=calculated_value,
            severity=SeverityLevel(severity),
            threshold=threshold_model,
            timestamp=datetime.fromisoformat(timestamp),
            metadata=metadata if metadata else {}
        ))
    
    return results

@router.get("/scopes", response_model=List[str])
async def get_available_scopes():
    """Get available rule scopes"""
    return [scope.value for scope in RuleScope]

@router.get("/severities", response_model=List[str])
async def get_available_severities():
    """Get available severity levels"""
    return [severity.value for severity in SeverityLevel]

@router.post("/test-expression")
async def test_expression(expression: str, data: List[Dict[str, Any]]):
    """Test an output expression against sample data"""
    try:
        result = business_rules_engine._calculate_value(expression, data)
        return {
            "expression": expression,
            "result": result,
            "data_count": len(data),
            "success": True
        }
    except Exception as e:
        return {
            "expression": expression,
            "error": str(e),
            "data_count": len(data),
            "success": False
        }
