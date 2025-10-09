"""
Health API endpoints for FlavorLab.

This module provides REST API endpoints for health-related operations including
health outcomes, recommendations, and health goal tracking.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from ..database import get_db
from ..models import Entity, RelationshipEntity
from ..services.auth import get_current_user, get_current_active_user
from ..models import User

# Create router
router = APIRouter(prefix="/health", tags=["health"])


# Health-related schemas
class HealthOutcomeResponse(BaseModel):
    """Schema for health outcome responses."""
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    evidence_strength: Optional[str] = None
    related_ingredients: List[str] = []
    related_compounds: List[str] = []


class HealthGoalResponse(BaseModel):
    """Schema for health goal responses."""
    goal: str
    description: Optional[str] = None
    priority: int = Field(ge=1, le=5)
    target_ingredients: List[str] = []
    target_compounds: List[str] = []
    progress: Optional[float] = Field(None, ge=0.0, le=1.0)


class HealthRecommendationResponse(BaseModel):
    """Schema for health recommendation responses."""
    recommendation_type: str
    title: str
    description: str
    confidence_score: float = Field(ge=0.0, le=1.0)
    ingredients: List[Dict[str, Any]] = []
    compounds: List[Dict[str, Any]] = []
    health_outcomes: List[str] = []


@router.get("/outcomes", response_model=List[HealthOutcomeResponse])
async def list_health_outcomes(
    category: Optional[str] = Query(None, description="Filter by health outcome category"),
    search: Optional[str] = Query(None, description="Search in health outcome names"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of results"),
    db: Session = Depends(get_db)
):
    """
    List health outcomes with optional filtering.
    
    Args:
        category: Filter by health outcome category
        search: Search query
        limit: Maximum number of results
        db: Database session
        
    Returns:
        List of health outcomes
    """
    try:
        # For MVP, return hardcoded health outcomes
        # In production, this would query a dedicated health outcomes table
        
        health_outcomes = [
            {
                "name": "Energy Boost",
                "description": "Increased energy levels and reduced fatigue",
                "category": "Energy",
                "evidence_strength": "Strong",
                "related_ingredients": ["coffee", "green_tea", "dark_chocolate"],
                "related_compounds": ["caffeine", "theobromine", "l_theanine"]
            },
            {
                "name": "Anti-Inflammatory",
                "description": "Reduced inflammation and improved immune function",
                "category": "Immune System",
                "evidence_strength": "Strong",
                "related_ingredients": ["turmeric", "ginger", "berries"],
                "related_compounds": ["curcumin", "gingerol", "anthocyanins"]
            },
            {
                "name": "Heart Health",
                "description": "Improved cardiovascular health and reduced heart disease risk",
                "category": "Cardiovascular",
                "evidence_strength": "Strong",
                "related_ingredients": ["salmon", "walnuts", "olive_oil"],
                "related_compounds": ["omega_3", "alpha_linolenic_acid", "oleic_acid"]
            },
            {
                "name": "Brain Function",
                "description": "Enhanced cognitive function and memory",
                "category": "Cognitive",
                "evidence_strength": "Moderate",
                "related_ingredients": ["blueberries", "fish", "nuts"],
                "related_compounds": ["anthocyanins", "omega_3", "vitamin_e"]
            },
            {
                "name": "Sleep Quality",
                "description": "Improved sleep duration and quality",
                "category": "Sleep",
                "evidence_strength": "Moderate",
                "related_ingredients": ["chamomile", "valerian", "tart_cherry"],
                "related_compounds": ["apigenin", "valerenic_acid", "melatonin"]
            }
        ]
        
        # Apply filters
        filtered_outcomes = health_outcomes
        
        if category:
            filtered_outcomes = [outcome for outcome in filtered_outcomes 
                               if outcome.get("category", "").lower() == category.lower()]
        
        if search:
            search_lower = search.lower()
            filtered_outcomes = [outcome for outcome in filtered_outcomes 
                               if search_lower in outcome["name"].lower() or 
                               (outcome.get("description") and search_lower in outcome["description"].lower())]
        
        # Apply limit
        filtered_outcomes = filtered_outcomes[:limit]
        
        return [HealthOutcomeResponse(**outcome) for outcome in filtered_outcomes]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving health outcomes: {str(e)}"
        )


@router.get("/outcomes/{outcome_name}")
async def get_health_outcome(
    outcome_name: str,
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific health outcome.
    
    Args:
        outcome_name: Health outcome name
        db: Database session
        
    Returns:
        Detailed health outcome information
    """
    try:
        # For MVP, return hardcoded detailed information
        # In production, this would query a dedicated health outcomes table
        
        outcome_details = {
            "energy_boost": {
                "name": "Energy Boost",
                "description": "Increased energy levels and reduced fatigue through natural compounds",
                "category": "Energy",
                "evidence_strength": "Strong",
                "mechanisms": [
                    "Caffeine blocks adenosine receptors, reducing fatigue",
                    "L-theanine promotes calm alertness",
                    "Theobromine provides sustained energy without jitters"
                ],
                "related_ingredients": [
                    {"name": "Coffee", "benefit": "High caffeine content for immediate energy"},
                    {"name": "Green Tea", "benefit": "Balanced caffeine and L-theanine"},
                    {"name": "Dark Chocolate", "benefit": "Theobromine for sustained energy"}
                ],
                "related_compounds": [
                    {"name": "Caffeine", "effect": "Stimulates central nervous system"},
                    {"name": "L-theanine", "effect": "Promotes relaxation without drowsiness"},
                    {"name": "Theobromine", "effect": "Mild stimulant with longer duration"}
                ],
                "recommended_dosage": "200-400mg caffeine per day",
                "precautions": ["Avoid excessive consumption", "Monitor for sleep disruption"]
            }
        }
        
        outcome_key = outcome_name.lower().replace(" ", "_")
        if outcome_key not in outcome_details:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Health outcome '{outcome_name}' not found"
            )
        
        return outcome_details[outcome_key]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving health outcome: {str(e)}"
        )


@router.get("/goals", response_model=List[HealthGoalResponse])
async def list_health_goals(
    current_user: User = Depends(get_current_active_user)
):
    """
    List user's health goals (requires authentication).
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        List of user's health goals
    """
    try:
        # For MVP, return sample health goals
        # In production, this would query user-specific health goals from database
        
        sample_goals = [
            {
                "goal": "Improve Energy Levels",
                "description": "Increase daily energy and reduce afternoon fatigue",
                "priority": 4,
                "target_ingredients": ["coffee", "green_tea", "nuts"],
                "target_compounds": ["caffeine", "l_theanine", "magnesium"],
                "progress": 0.6
            },
            {
                "goal": "Reduce Inflammation",
                "description": "Lower chronic inflammation through diet",
                "priority": 5,
                "target_ingredients": ["turmeric", "ginger", "berries"],
                "target_compounds": ["curcumin", "gingerol", "anthocyanins"],
                "progress": 0.3
            },
            {
                "goal": "Better Sleep",
                "description": "Improve sleep quality and duration",
                "priority": 3,
                "target_ingredients": ["chamomile", "tart_cherry", "magnesium_rich_foods"],
                "target_compounds": ["apigenin", "melatonin", "magnesium"],
                "progress": 0.8
            }
        ]
        
        return [HealthGoalResponse(**goal) for goal in sample_goals]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving health goals: {str(e)}"
        )


@router.post("/recommendations", response_model=List[HealthRecommendationResponse])
async def get_health_recommendations(
    health_goals: List[str],
    dietary_restrictions: Optional[List[str]] = None,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get personalized health recommendations based on goals.
    
    Args:
        health_goals: List of health goals
        dietary_restrictions: Optional dietary restrictions
        current_user: Current authenticated user
        
    Returns:
        List of health recommendations
    """
    try:
        # For MVP, return hardcoded recommendations based on goals
        # In production, this would use ML algorithms and user data
        
        recommendations = []
        
        if "energy" in [goal.lower() for goal in health_goals]:
            recommendations.append({
                "recommendation_type": "ingredient",
                "title": "Energy-Boosting Ingredients",
                "description": "Add these ingredients to your diet for sustained energy",
                "confidence_score": 0.85,
                "ingredients": [
                    {"name": "Green Tea", "benefit": "Balanced caffeine and L-theanine", "dosage": "2-3 cups daily"},
                    {"name": "Dark Chocolate", "benefit": "Theobromine for sustained energy", "dosage": "1-2 squares daily"},
                    {"name": "Nuts", "benefit": "Healthy fats and magnesium", "dosage": "1 handful daily"}
                ],
                "compounds": [
                    {"name": "Caffeine", "source": "Coffee, Tea", "effect": "Immediate energy boost"},
                    {"name": "L-theanine", "source": "Green Tea", "effect": "Calm alertness"}
                ],
                "health_outcomes": ["Energy Boost", "Mental Clarity"]
            })
        
        if "inflammation" in [goal.lower() for goal in health_goals]:
            recommendations.append({
                "recommendation_type": "compound",
                "title": "Anti-Inflammatory Compounds",
                "description": "Focus on these compounds to reduce inflammation",
                "confidence_score": 0.90,
                "ingredients": [
                    {"name": "Turmeric", "benefit": "High curcumin content", "dosage": "1 tsp daily"},
                    {"name": "Ginger", "benefit": "Gingerol and shogaol", "dosage": "1 inch fresh daily"},
                    {"name": "Berries", "benefit": "Anthocyanins and antioxidants", "dosage": "1 cup daily"}
                ],
                "compounds": [
                    {"name": "Curcumin", "source": "Turmeric", "effect": "Strong anti-inflammatory"},
                    {"name": "Gingerol", "source": "Ginger", "effect": "Reduces inflammation markers"}
                ],
                "health_outcomes": ["Anti-Inflammatory", "Immune Support"]
            })
        
        if "sleep" in [goal.lower() for goal in health_goals]:
            recommendations.append({
                "recommendation_type": "timing",
                "title": "Sleep-Promoting Foods",
                "description": "Consume these foods in the evening for better sleep",
                "confidence_score": 0.75,
                "ingredients": [
                    {"name": "Chamomile Tea", "benefit": "Apigenin for relaxation", "dosage": "1 cup before bed"},
                    {"name": "Tart Cherry", "benefit": "Natural melatonin source", "dosage": "1 cup juice or fresh"},
                    {"name": "Magnesium-Rich Foods", "benefit": "Muscle relaxation", "dosage": "Include in dinner"}
                ],
                "compounds": [
                    {"name": "Apigenin", "source": "Chamomile", "effect": "Promotes relaxation"},
                    {"name": "Melatonin", "source": "Tart Cherry", "effect": "Regulates sleep cycle"}
                ],
                "health_outcomes": ["Sleep Quality", "Relaxation"]
            })
        
        return [HealthRecommendationResponse(**rec) for rec in recommendations]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating health recommendations: {str(e)}"
        )


@router.get("/stats/overview")
async def get_health_statistics(
    db: Session = Depends(get_db)
):
    """
    Get health-related statistics.
    
    Args:
        db: Database session
        
    Returns:
        Health statistics overview
    """
    try:
        # Get entities with health-related attributes
        health_entities = db.query(Entity).filter(
            Entity.attributes.contains({"health_outcomes": {"value": {"$exists": True}}})
        ).count()
        
        # Get relationships related to health outcomes
        health_relationships = db.query(RelationshipEntity).filter(
            RelationshipEntity.relationship_type.in_(["contains", "found_in"])
        ).count()
        
        return {
            "total_health_entities": health_entities,
            "total_health_relationships": health_relationships,
            "health_outcomes_available": 5,  # Hardcoded for MVP
            "recommendation_categories": ["ingredient", "compound", "timing", "dosage"],
            "last_updated": "2024-01-01T00:00:00Z"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving health statistics: {str(e)}"
        )

