"""
Flavor API endpoints for FlavorLab.

This module provides REST API endpoints for flavor-related operations including
flavor matching, recommendations, and flavor profile analysis.
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
router = APIRouter(prefix="/flavor", tags=["flavor"])


# Flavor-related schemas
class FlavorProfileRequest(BaseModel):
    """Pydantic model for a flavor profile request."""
    entity_ids: List[str] = Field(..., min_length=1, description="List of entity IDs")
    target_flavors: List[str] = Field(..., min_length=1, description="Target flavors to match")
    intensity: str = Field(..., pattern="^(mild|moderate|strong|intense)$")


class FlavorProfileResponse(BaseModel):
    """Schema for flavor profile responses."""
    name: str
    description: Optional[str] = None
    intensity: str = Field(..., pattern="^(mild|moderate|strong|intense)$")
    category: str
    complementary_flavors: List[str] = []
    conflicting_flavors: List[str] = []
    common_ingredients: List[str] = []


class FlavorRecommendationResponse(BaseModel):
    """Schema for flavor recommendation responses."""
    recommendation_type: str
    title: str
    description: str
    confidence_score: float = Field(ge=0.0, le=1.0)
    suggested_ingredients: List[Dict[str, Any]] = []
    flavor_combinations: List[Dict[str, Any]] = []
    health_benefits: List[str] = []


class FlavorMatchRequest(BaseModel):
    """Schema for flavor matching requests."""
    target_flavors: List[str] = Field(..., min_length=1, description="Target flavors to match")
    health_goals: Optional[List[str]] = None
    dietary_restrictions: Optional[List[str]] = None
    intensity_preference: Optional[str] = Field(None, pattern="^(mild|moderate|strong|intense)$")
    max_recommendations: int = Field(10, ge=1, le=50)


@router.get("/profiles", response_model=List[FlavorProfileResponse])
async def list_flavor_profiles(
    category: Optional[str] = Query(None, description="Filter by flavor category"),
    intensity: Optional[str] = Query(None, pattern="^(mild|moderate|strong|intense)$", description="Filter by intensity"),
    search: Optional[str] = Query(None, description="Search in flavor names"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of results"),
    db: Session = Depends(get_db)
):
    """
    List flavor profiles with optional filtering.
    
    Args:
        category: Filter by flavor category
        intensity: Filter by intensity level
        search: Search query
        limit: Maximum number of results
        db: Database session
        
    Returns:
        List of flavor profiles
    """
    try:
        # For MVP, return hardcoded flavor profiles
        # In production, this would query a dedicated flavor profiles table
        
        flavor_profiles = [
            {
                "name": "Sweet",
                "description": "Natural sweetness from sugars and sweet compounds",
                "intensity": "moderate",
                "category": "Basic Taste",
                "complementary_flavors": ["sour", "bitter", "spicy"],
                "conflicting_flavors": ["salty"],
                "common_ingredients": ["honey", "maple_syrup", "fruits", "carrots"]
            },
            {
                "name": "Umami",
                "description": "Savory, meaty taste from amino acids",
                "intensity": "strong",
                "category": "Basic Taste",
                "complementary_flavors": ["salty", "sweet"],
                "conflicting_flavors": ["bitter"],
                "common_ingredients": ["mushrooms", "soy_sauce", "parmesan", "tomatoes"]
            },
            {
                "name": "Spicy",
                "description": "Heat and pungency from capsaicin and related compounds",
                "intensity": "intense",
                "category": "Sensation",
                "complementary_flavors": ["sweet", "sour", "umami"],
                "conflicting_flavors": ["bitter"],
                "common_ingredients": ["chili_peppers", "ginger", "black_pepper", "wasabi"]
            },
            {
                "name": "Herbal",
                "description": "Fresh, green flavors from herbs and aromatic plants",
                "intensity": "mild",
                "category": "Aromatic",
                "complementary_flavors": ["citrus", "earthy", "floral"],
                "conflicting_flavors": ["smoky"],
                "common_ingredients": ["basil", "thyme", "rosemary", "cilantro"]
            },
            {
                "name": "Citrus",
                "description": "Bright, acidic flavors from citrus fruits",
                "intensity": "moderate",
                "category": "Aromatic",
                "complementary_flavors": ["herbal", "sweet", "spicy"],
                "conflicting_flavors": ["dairy"],
                "common_ingredients": ["lemon", "lime", "orange", "grapefruit"]
            },
            {
                "name": "Earthy",
                "description": "Ground, mineral flavors from root vegetables and fungi",
                "intensity": "moderate",
                "category": "Aromatic",
                "complementary_flavors": ["herbal", "umami", "woody"],
                "conflicting_flavors": ["citrus"],
                "common_ingredients": ["beets", "mushrooms", "truffles", "potatoes"]
            }
        ]
        
        # Apply filters
        filtered_profiles = flavor_profiles
        
        if category:
            filtered_profiles = [profile for profile in filtered_profiles 
                               if profile.get("category", "").lower() == category.lower()]
        
        if intensity:
            filtered_profiles = [profile for profile in filtered_profiles 
                               if profile.get("intensity", "").lower() == intensity.lower()]
        
        if search:
            search_lower = search.lower()
            filtered_profiles = [profile for profile in filtered_profiles 
                               if search_lower in profile["name"].lower() or 
                               (profile.get("description") and search_lower in profile["description"].lower())]
        
        # Apply limit
        filtered_profiles = filtered_profiles[:limit]
        
        return [FlavorProfileResponse(**profile) for profile in filtered_profiles]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving flavor profiles: {str(e)}"
        )


@router.get("/profiles/{flavor_name}")
async def get_flavor_profile(
    flavor_name: str,
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific flavor profile.
    
    Args:
        flavor_name: Flavor profile name
        db: Database session
        
    Returns:
        Detailed flavor profile information
    """
    try:
        # For MVP, return hardcoded detailed information
        # In production, this would query a dedicated flavor profiles table
        
        flavor_details = {
            "sweet": {
                "name": "Sweet",
                "description": "Natural sweetness from sugars and sweet compounds",
                "intensity": "moderate",
                "category": "Basic Taste",
                "scientific_basis": "Activation of sweet taste receptors (T1R2/T1R3)",
                "key_compounds": ["sucrose", "fructose", "glucose", "steviol"],
                "complementary_flavors": [
                    {"name": "Sour", "reason": "Balances sweetness with acidity"},
                    {"name": "Bitter", "reason": "Creates complex flavor profile"},
                    {"name": "Spicy", "reason": "Heat enhances sweetness perception"}
                ],
                "conflicting_flavors": [
                    {"name": "Salty", "reason": "Can suppress sweet taste perception"}
                ],
                "common_ingredients": [
                    {"name": "Honey", "flavor_notes": "Floral, complex sweetness"},
                    {"name": "Maple Syrup", "flavor_notes": "Woody, caramel notes"},
                    {"name": "Fruits", "flavor_notes": "Natural fruit sugars with acidity"},
                    {"name": "Carrots", "flavor_notes": "Earthy sweetness"}
                ],
                "cooking_tips": [
                    "Add a pinch of salt to enhance sweetness",
                    "Pair with acidic ingredients to balance",
                    "Use in moderation to avoid overwhelming other flavors"
                ]
            }
        }
        
        flavor_key = flavor_name.lower()
        if flavor_key not in flavor_details:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Flavor profile '{flavor_name}' not found"
            )
        
        return flavor_details[flavor_key]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving flavor profile: {str(e)}"
        )


@router.post("/recommendations", response_model=List[FlavorRecommendationResponse])
async def get_flavor_recommendations(
    match_request: FlavorMatchRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get personalized flavor recommendations based on preferences and goals.
    
    Args:
        match_request: Flavor matching parameters
        current_user: Current authenticated user
        
    Returns:
        List of flavor recommendations
    """
    try:
        # For MVP, return hardcoded recommendations based on target flavors
        # In production, this would use ML algorithms and user preference data
        
        recommendations = []
        
        # Sweet flavor recommendations
        if "sweet" in [flavor.lower() for flavor in match_request.target_flavors]:
            recommendations.append({
                "recommendation_type": "ingredient_pairing",
                "title": "Sweet Flavor Enhancements",
                "description": "Ingredients that complement and enhance sweet flavors",
                "confidence_score": 0.85,
                "suggested_ingredients": [
                    {"name": "Vanilla", "benefit": "Adds depth and warmth", "usage": "Extract or bean"},
                    {"name": "Cinnamon", "benefit": "Warm spice that enhances sweetness", "usage": "Ground or stick"},
                    {"name": "Sea Salt", "benefit": "Enhances sweetness perception", "usage": "Pinch in sweet dishes"}
                ],
                "flavor_combinations": [
                    {"combination": "Sweet + Sour", "example": "Lemon tart", "reason": "Balances sweetness"},
                    {"combination": "Sweet + Spicy", "example": "Chili chocolate", "reason": "Heat enhances sweetness"}
                ],
                "health_benefits": ["Mood enhancement", "Energy boost", "Antioxidant properties"]
            })
        
        # Umami flavor recommendations
        if "umami" in [flavor.lower() for flavor in match_request.target_flavors]:
            recommendations.append({
                "recommendation_type": "compound_focus",
                "title": "Umami-Rich Ingredients",
                "description": "Ingredients high in umami compounds for savory depth",
                "confidence_score": 0.90,
                "suggested_ingredients": [
                    {"name": "Mushrooms", "benefit": "High glutamate content", "usage": "Fresh or dried"},
                    {"name": "Soy Sauce", "benefit": "Fermented umami compounds", "usage": "Small amounts for seasoning"},
                    {"name": "Parmesan Cheese", "benefit": "Aged umami compounds", "usage": "Grated over dishes"}
                ],
                "flavor_combinations": [
                    {"combination": "Umami + Sweet", "example": "Teriyaki sauce", "reason": "Balances savory and sweet"},
                    {"combination": "Umami + Acid", "example": "Tomato-based dishes", "reason": "Brightens umami flavors"}
                ],
                "health_benefits": ["Protein content", "B-vitamins", "Mineral content"]
            })
        
        # Spicy flavor recommendations
        if "spicy" in [flavor.lower() for flavor in match_request.target_flavors]:
            recommendations.append({
                "recommendation_type": "heat_management",
                "title": "Spice Level Management",
                "description": "Techniques and ingredients for controlling spice levels",
                "confidence_score": 0.80,
                "suggested_ingredients": [
                    {"name": "Coconut Milk", "benefit": "Cools heat and adds richness", "usage": "In curries and soups"},
                    {"name": "Yogurt", "benefit": "Neutralizes capsaicin", "usage": "As a cooling side"},
                    {"name": "Lime", "benefit": "Acidity balances heat", "usage": "Squeezed over spicy dishes"}
                ],
                "flavor_combinations": [
                    {"combination": "Spicy + Sweet", "example": "Mango habanero", "reason": "Sweetness cools heat"},
                    {"combination": "Spicy + Fat", "example": "Chili oil", "reason": "Fat carries heat compounds"}
                ],
                "health_benefits": ["Metabolism boost", "Pain relief", "Antioxidant properties"]
            })
        
        # Limit recommendations based on request
        recommendations = recommendations[:match_request.max_recommendations]
        
        return [FlavorRecommendationResponse(**rec) for rec in recommendations]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating flavor recommendations: {str(e)}"
        )


@router.get("/combinations/popular")
async def get_popular_flavor_combinations(
    limit: int = Query(10, ge=1, le=50, description="Maximum number of combinations"),
    db: Session = Depends(get_db)
):
    """
    Get popular flavor combinations.
    
    Args:
        limit: Maximum number of combinations
        db: Database session
        
    Returns:
        List of popular flavor combinations
    """
    try:
        # For MVP, return hardcoded popular combinations
        # In production, this would analyze user data and recipe patterns
        
        popular_combinations = [
            {
                "combination": "Sweet + Sour",
                "description": "Classic balance of sweetness and acidity",
                "popularity_score": 0.95,
                "examples": ["Lemon tart", "Sweet and sour sauce", "Fruit salad"],
                "key_ingredients": ["Citrus fruits", "Vinegar", "Sugar"],
                "cuisine_origins": ["International", "Asian", "Mediterranean"]
            },
            {
                "combination": "Umami + Sweet",
                "description": "Savory depth with natural sweetness",
                "popularity_score": 0.90,
                "examples": ["Teriyaki", "BBQ sauce", "Caramelized onions"],
                "key_ingredients": ["Soy sauce", "Mushrooms", "Onions"],
                "cuisine_origins": ["Asian", "American", "French"]
            },
            {
                "combination": "Spicy + Sweet",
                "description": "Heat balanced with sweetness",
                "popularity_score": 0.85,
                "examples": ["Chili chocolate", "Mango habanero", "Spicy honey"],
                "key_ingredients": ["Chili peppers", "Honey", "Fruits"],
                "cuisine_origins": ["Mexican", "Thai", "Caribbean"]
            },
            {
                "combination": "Herbal + Citrus",
                "description": "Fresh herbs with bright citrus notes",
                "popularity_score": 0.80,
                "examples": ["Lemon thyme", "Basil lime", "Mint orange"],
                "key_ingredients": ["Fresh herbs", "Citrus zest", "Citrus juice"],
                "cuisine_origins": ["Mediterranean", "Middle Eastern", "Modern"]
            },
            {
                "combination": "Earthy + Umami",
                "description": "Ground flavors with savory depth",
                "popularity_score": 0.75,
                "examples": ["Mushroom risotto", "Beet salad", "Root vegetable soup"],
                "key_ingredients": ["Mushrooms", "Root vegetables", "Cheese"],
                "cuisine_origins": ["Italian", "French", "Scandinavian"]
            }
        ]
        
        return popular_combinations[:limit]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving flavor combinations: {str(e)}"
        )


@router.get("/stats/overview")
async def get_flavor_statistics(
    db: Session = Depends(get_db)
):
    """
    Get flavor-related statistics.
    
    Args:
        db: Database session
        
    Returns:
        Flavor statistics overview
    """
    try:
        # Get entities with flavor-related attributes
        flavor_entities = db.query(Entity).filter(
            Entity.attributes.contains({"flavor_profile": {"value": {"$exists": True}}})
        ).count()
        
        # Get relationships related to flavor compounds
        flavor_relationships = db.query(RelationshipEntity).filter(
            RelationshipEntity.relationship_type.in_(["contains", "found_in"])
        ).count()
        
        return {
            "total_flavor_entities": flavor_entities,
            "total_flavor_relationships": flavor_relationships,
            "flavor_profiles_available": 6,  # Hardcoded for MVP
            "popular_combinations": 5,  # Hardcoded for MVP
            "recommendation_categories": ["ingredient_pairing", "compound_focus", "heat_management", "balance"],
            "last_updated": "2024-01-01T00:00:00Z"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving flavor statistics: {str(e)}"
        )

