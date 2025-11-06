"""
Entity API endpoints for FlavorLab.

This module provides REST API endpoints for entity operations including
listing, searching, and retrieving entity information.
"""

from typing import List, Optional, Any
import os
import json
import re
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, aliased
from sqlalchemy import func, cast, Float, or_

from ..database import get_db
from ..models import Entity
from ..models.entity import IngredientEntity
from ..schemas import (
    EntityResponse, EntityListResponse, EntitySearchRequest, EntitySearchResponse,
    EntityStatsResponse, EntityCreate, EntityUpdate, IngredientEntityResponse,
    IngredientGroup, IngredientGroupsResponse,
)
from ..services.search import SearchService
from ..services.auth import get_current_user, get_current_active_user
from ..models import User
from ..models.category import Category
from ..models.entity import Entity as BaseEntityModel

# Create router
router = APIRouter(prefix="/entities", tags=["entities"])


def _normalize_entity_for_response(entity: Entity) -> Entity:
    """Coerce nullable arrays to lists and flatten common numeric attributes."""
    try:
        # Ensure list fields never None
        if getattr(entity, "aliases", None) is None:
            entity.aliases = []  # type: ignore[attr-defined]
        # If entity is IngredientEntity subtype, coerce lists
        if hasattr(entity, "health_outcomes") and getattr(entity, "health_outcomes", None) is None:
            entity.health_outcomes = []  # type: ignore[attr-defined]
        if hasattr(entity, "compounds") and getattr(entity, "compounds", None) is None:
            entity.compounds = []  # type: ignore[attr-defined]

        # Normalize attributes
        attrs: Optional[dict[str, Any]] = getattr(entity, "attributes", None)  # type: ignore[assignment]
        if attrs is None:
            entity.attributes = {}  # type: ignore[attr-defined]
            attrs = entity.attributes  # type: ignore[assignment]

        # Flatten numeric nutrition keys if nested
        for key in ("calories", "protein_g", "carbs_g", "fat_g", "fiber_g", "sugars_g", "serving_size_g"):
            val = attrs.get(key) if isinstance(attrs, dict) else None
            if isinstance(val, dict) and "value" in val:
                attrs[key] = val.get("value")

        # Fill missing nutrition from seed as a safety net (no separate scripts)
        missing_any = any(
            (attrs.get(k) is None or (isinstance(attrs.get(k), dict) and attrs.get(k).get("value") is None))
            for k in ("calories", "protein_g", "carbs_g", "fat_g", "fiber_g", "sugars_g")
        )
        if missing_any:
            seed = _get_seed_map()
            slug = (getattr(entity, "slug", None) or "").strip()
            if not slug:
                slug = _slugify(getattr(entity, "id", ""))
            rec = seed.get(slug)
            if not rec:
                # try by id/name fallbacks
                rec = seed.get(_slugify(getattr(entity, "id", ""))) or seed.get(_slugify(getattr(entity, "name", "")))
            if isinstance(rec, dict):
                for k in ("calories", "protein_g", "carbs_g", "fat_g", "fiber_g", "sugars_g"):
                    if attrs.get(k) in (None, {}):
                        v = rec.get(k)
                        if v is not None:
                            attrs[k] = v

        if getattr(entity, "primary_classification", "") == "ingredient":
            enrichment_map = _get_ingredient_enrichment_map()
            enrichment = None
            for key in (
                getattr(entity, "id", "") or "",
                getattr(entity, "slug", "") or "",
                _slugify(getattr(entity, "id", "")),
                _slugify(getattr(entity, "name", "")),
            ):
                if key and key in enrichment_map:
                    enrichment = enrichment_map[key]
                    break

            if enrichment:
                compound_details = enrichment.get("key_compounds") or []
                if compound_details:
                    attrs["key_compound_details"] = {
                        "value": compound_details,
                        "source": "ingredient_enrichment_v20251106",
                        "confidence": 4,
                    }

                vitamin_details = enrichment.get("vitamins_minerals") or []
                if vitamin_details:
                    attrs["vitamin_mineral_details"] = {
                        "value": vitamin_details,
                        "source": "ingredient_enrichment_v20251106",
                        "confidence": 4,
                    }

        return entity
    except Exception:
        # Be permissive - return as is if anything unexpected
        return entity


_SEED_CACHE: Optional[dict] = None
_INGREDIENT_ENRICHMENT_CACHE: Optional[dict] = None


def _slugify(value: str) -> str:
    s = (value or "").lower().strip()
    s = re.sub(r"[^a-z0-9\s-]", "", s)
    s = re.sub(r"[\s-]+", "-", s).strip("-")
    return s


def _get_seed_map() -> dict:
    global _SEED_CACHE
    if _SEED_CACHE is not None:
        return _SEED_CACHE
    try:
        app_dir = os.path.dirname(os.path.dirname(__file__))
        seed_path = os.path.join(app_dir, "scripts", "nutrition_seed.json")
        if not os.path.exists(seed_path):
            # Fallback to backend/scripts when running from app module
            seed_path = os.path.join(os.path.dirname(app_dir), "scripts", "nutrition_seed.json")
        with open(seed_path, "r", encoding="utf-8") as f:
            data = json.load(f) or {}
        items = data.get("items", []) or []
        _SEED_CACHE = { (item.get("slug") or "").strip(): item for item in items if item.get("slug") }
        return _SEED_CACHE
    except Exception:
        _SEED_CACHE = {}
        return _SEED_CACHE


def _get_ingredient_enrichment_map() -> dict:
    global _INGREDIENT_ENRICHMENT_CACHE
    if _INGREDIENT_ENRICHMENT_CACHE is not None:
        return _INGREDIENT_ENRICHMENT_CACHE

    try:
        app_dir = os.path.dirname(os.path.dirname(__file__))
        enrichment_path = os.path.join(app_dir, "analysis", "ingredient_enrichment.json")
        if not os.path.exists(enrichment_path):
            enrichment_path = os.path.join(os.path.dirname(app_dir), "analysis", "ingredient_enrichment.json")

        if not os.path.exists(enrichment_path):
            _INGREDIENT_ENRICHMENT_CACHE = {}
            return _INGREDIENT_ENRICHMENT_CACHE

        with open(enrichment_path, "r", encoding="utf-8") as f:
            data = json.load(f) or []
        cache: dict[str, dict] = {}
        for entry in data:
            key = (entry.get("id") or entry.get("name") or "").strip()
            if not key:
                continue
            cache[key] = entry
            slug = _slugify(key)
            if slug and slug not in cache:
                cache[slug] = entry
        _INGREDIENT_ENRICHMENT_CACHE = cache
        return _INGREDIENT_ENRICHMENT_CACHE
    except Exception:
        _INGREDIENT_ENRICHMENT_CACHE = {}
        return _INGREDIENT_ENRICHMENT_CACHE


# Slugs considered too generic to show in the ingredient browser
GENERIC_EXCLUDE_SLUGS = {"beans", "beanslegumes", "mixed-berries"}
GENERIC_EXCLUDE_IDS = {"beans", "beanslegumes", "mixed-berries"}

# Category slug aliases to improve matching
CATEGORY_SLUG_ALIASES = {
    "meats": ["meats", "meat", "poultry"],
    "nuts": ["nuts", "nut", "mixed-nuts"],
    "seeds": ["seeds", "seed"],
    "grains": ["grains", "grain", "whole-grains"],
    "seafood": ["seafood", "fish", "shellfish"],
    "fruits": ["fruits", "fruit", "citrus", "produce"],
    "berries": ["berries", "fruit-berries", "fruits-berries"],
    "vegetables": ["vegetables", "vegetable"],
    "legumes": ["legumes", "beans", "beanslegumes"],
}


@router.get("/", response_model=EntityListResponse)
async def list_entities(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=1000, description="Page size"),
    classification: Optional[str] = Query(None, description="Filter by primary classification"),
    search: Optional[str] = Query(None, description="Search query"),
    db: Session = Depends(get_db)
):
    """
    List entities with optional filtering and pagination.
    
    Args:
        page: Page number (1-based)
        size: Page size
        classification: Filter by primary classification
        search: Search query
        db: Database session
        
    Returns:
        EntityListResponse: Paginated list of entities
    """
    try:
        # Build query
        query = db.query(Entity)
        
        # Apply classification filter
        if classification:
            query = query.filter(Entity.primary_classification == classification)
        
        # Apply search filter
        if search:
            query = query.filter(
                Entity.name.ilike(f"%{search}%")
            )
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * size
        entities = query.offset(offset).limit(size).all()
        
        # Convert to response format
        entity_responses = [EntityResponse.model_validate(entity) for entity in entities]
        
        return EntityListResponse(
            entities=entity_responses,
            total=total,
            page=page,
            size=size,
            has_next=offset + size < total,
            has_prev=page > 1
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing entities: {str(e)}"
        )


@router.get("/ingredients", response_model=List[IngredientEntityResponse])
async def list_ingredients(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=1000, description="Page size"),
    search: Optional[str] = Query(None, description="Search query"),
    health_pillars: Optional[str] = Query(
        None,
        description="Comma-separated list of health pillar IDs to filter by (e.g., '1,3,8')"
    ),
    sort: Optional[str] = Query("name_asc", description="Sort order: name_asc|name_desc"),
    categories: Optional[str] = Query(None, description="Comma-separated category slugs to include"),
    min_calories: Optional[float] = Query(None, description="Minimum calories per 100g"),
    max_calories: Optional[float] = Query(None, description="Maximum calories per 100g"),
    min_protein_g: Optional[float] = Query(None, description="Minimum protein per 100g"),
    max_protein_g: Optional[float] = Query(None, description="Maximum protein per 100g"),
    db: Session = Depends(get_db)
):
    """
    List ingredients with optional filtering by health pillars and pagination.

    Args:
        page: Page number (1-based)
        size: Page size
        search: Search query for ingredient names
        health_pillars: Comma-separated health pillar IDs (1-8) to filter by
        db: Database session

    Returns:
        List[IngredientEntityResponse]: List of ingredients with health outcomes

    Example:
        GET /entities/ingredients?health_pillars=1,3,8
        Returns ingredients supporting Energy, Immunity, and Inflammation Reduction
    """
    try:
        # Start with base query; explicitly alias base Entity to avoid duplicate joins
        BaseEnt = aliased(Entity)
        query = db.query(IngredientEntity).select_from(IngredientEntity).join(BaseEnt, BaseEnt.id == IngredientEntity.id)

        # Exclusions and lifecycle
        query = query.filter(BaseEnt.is_active.is_(True))
        if GENERIC_EXCLUDE_SLUGS:
            query = query.filter(~BaseEnt.slug.in_(list(GENERIC_EXCLUDE_SLUGS)))

        # Apply search filter
        if search:
            query = query.filter(BaseEnt.name.ilike(f"%{search}%"))

        # Parse and apply health pillar filter
        pillar_ids: Optional[List[int]] = None
        if health_pillars:
            try:
                # Parse comma-separated string into list of integers
                pillar_ids = [int(pid.strip()) for pid in health_pillars.split(",") if pid.strip()]

                # Validate pillar IDs are in range 1-8
                invalid_ids = [pid for pid in pillar_ids if pid < 1 or pid > 8]
                if invalid_ids:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Invalid health pillar IDs: {invalid_ids}. Must be between 1-8."
                    )

                # Apply pillar filter using the model's class method
                query = IngredientEntity.filter_ingredients_by_pillars(query, pillar_ids)

            except ValueError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid health_pillars format. Expected comma-separated integers (e.g., '1,3,8'): {str(e)}"
                )

        # Category filter (by slug)
        if categories:
            raw_slugs = [s.strip() for s in categories.split(',') if s.strip()]
            if raw_slugs:
                expanded: List[str] = []
                for rs in raw_slugs:
                    # expand with aliases to be resilient to taxonomy differences
                    expanded.extend(CATEGORY_SLUG_ALIASES.get(rs, [rs]))
                # unique and lowercase
                slugs = sorted({s.lower() for s in expanded})
                # join through association table defined in models.category (outer join to allow fallback)
                from ..models.category import IngredientCategory
                query = (
                    query.outerjoin(IngredientCategory, IngredientCategory.c.ingredient_id == IngredientEntity.id)
                         .outerjoin(Category, Category.id == IngredientCategory.c.category_id)
                )
                # Heuristic fallback patterns by category aliases (OR with category match)
                patterns: List[str] = []
                if any(x in slugs for x in CATEGORY_SLUG_ALIASES.get('meats', [])):
                    patterns += ["%meat%","%beef%","%chicken%","%turkey%","%poultry%"]
                if any(x in slugs for x in CATEGORY_SLUG_ALIASES.get('nuts', [])):
                    patterns += ["%almond%","%walnut%","%pecan%","%hazelnut%","%pistach%","%cashew%","%nut%"]
                if any(x in slugs for x in CATEGORY_SLUG_ALIASES.get('seeds', [])):
                    patterns += ["%seed%","%chia%","%flax%","%pumpkin%","%sunflower%","%sesame%"]
                if any(x in slugs for x in CATEGORY_SLUG_ALIASES.get('grains', [])):
                    patterns += ["%grain%","%quinoa%","%oat%","%rice%","%wheat%","%barley%","%rye%"]
                if any(x in slugs for x in CATEGORY_SLUG_ALIASES.get('seafood', [])):
                    patterns += ["%seafood%","%fish%","%salmon%","%tuna%","%oyster%","%shellfish%"]
                if any(x in slugs for x in CATEGORY_SLUG_ALIASES.get('fruits', [])):
                    patterns += [
                        "%fruit%",
                        "%apple%",
                        "%orange%",
                        "%banana%",
                        "%grape%",
                        "%citrus%",
                        "%pineapple%",
                        "%mango%",
                        "%peach%",
                        "%pear%",
                        "%melon%",
                        "%plum%",
                    ]
                if any(x in slugs for x in CATEGORY_SLUG_ALIASES.get('berries', [])):
                    patterns += [
                        "%berry%",
                        "%berries%",
                        "%cranberry%",
                        "%strawberry%",
                        "%blueberry%",
                        "%raspberry%",
                        "%blackberry%",
                        "%boysenberry%",
                        "%elderberry%",
                        "%gojiberry%",
                    ]
                if any(x in slugs for x in CATEGORY_SLUG_ALIASES.get('legumes', [])):
                    patterns += [
                        "%legume%",
                        "%bean%",
                        "%lentil%",
                        "%chickpea%",
                        "%garbanzo%",
                        "%soy%",
                        "%edamame%",
                        "%black-eyed-pea%",
                        "%split-pea%",
                        "%kidney%",
                    ]

                name_filters = [BaseEnt.slug.ilike(p) for p in patterns] + [BaseEnt.name.ilike(p) for p in patterns]
                if slugs and patterns:
                    query = query.filter(or_(Category.slug.in_(slugs), or_(*name_filters)))
                elif slugs:
                    query = query.filter(Category.slug.in_(slugs))
                elif patterns:
                    query = query.filter(or_(*name_filters))

        # Note: We apply numeric attribute filters after retrieval using normalized values
        # so that entities populated via seed fallback are included.

        # Sorting (stable)
        if sort == "name_desc":
            query = query.order_by(BaseEnt.name.desc(), IngredientEntity.id.asc())
        else:
            query = query.order_by(BaseEnt.name.asc(), IngredientEntity.id.asc())

        # Fetch first (coarse) page then apply in-Python numeric filters using normalized attributes
        # Pull extra to compensate for post-filtering shrinkage
        fetch_limit = size * 3
        offset = (page - 1) * size
        raw_items = query.offset(offset).limit(fetch_limit).all()

        def passes_numeric_filters(ent: IngredientEntity) -> bool:
            e = _normalize_entity_for_response(ent)
            attrs = getattr(e, "attributes", {}) or {}
            def num(v):
                try:
                    return float(v)
                except Exception:
                    return None
            cal = num(attrs.get("calories"))
            pro = num(attrs.get("protein_g"))
            if min_calories is not None and (cal is None or cal < float(min_calories)):
                return False
            if max_calories is not None and (cal is None or cal > float(max_calories)):
                return False
            if min_protein_g is not None and (pro is None or pro < float(min_protein_g)):
                return False
            if max_protein_g is not None and (pro is None or pro > float(max_protein_g)):
                return False
            return True

        filtered_items = [it for it in raw_items if passes_numeric_filters(it)]

        # Approximate total by counting across full query when no numeric filters, otherwise compute via Python
        if any(v is not None for v in [min_calories, max_calories, min_protein_g, max_protein_g]):
            # To keep it simple, just set total as len(filtered_items) + potential unseen remainder
            total = len(filtered_items) + max(0, len(raw_items) - len(filtered_items))
        else:
            total = query.count()

        # Final page slice
        ingredients = filtered_items[:size]

        # Additional filtering in Python for SQLite (checking pillar membership)
        # This is needed because SQLite JSON querying is limited
        if pillar_ids:
            filtered_ingredients = []
            for ingredient in ingredients:
                if isinstance(ingredient.health_outcomes, list):
                    # Check if any outcome has a matching pillar
                    for outcome in ingredient.health_outcomes:
                        if isinstance(outcome, dict) and "pillars" in outcome:
                            if any(pid in outcome["pillars"] for pid in pillar_ids):
                                filtered_ingredients.append(ingredient)
                                break
            ingredients = filtered_ingredients

        # Coerce nullable JSON arrays to empty lists to satisfy schema
        safe_items = [_normalize_entity_for_response(ing) for ing in ingredients]

        # Convert to response format
        ingredient_responses = [
            IngredientEntityResponse.model_validate(item)
            for item in safe_items
        ]

        return ingredient_responses

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing ingredients: {str(e)}"
        )


@router.get("/ingredients/groups", response_model=IngredientGroupsResponse)
async def list_ingredient_groups(
    size_per_group: int = Query(24, ge=1, le=1000, description="Number of items per category group"),
    categories: Optional[str] = Query(None, description="Comma-separated category slugs to include; default = all"),
    sort: Optional[str] = Query("name_asc", description="Sort within groups: name_asc|name_desc"),
    db: Session = Depends(get_db),
):
    """
    Return grouped ingredients per category, optimized for carousel/inline display.

    - If `categories` provided, restrict groups to those slugs
    - Each group includes total count and first page of items
    - Sorting within groups supports `name_asc|name_desc`
    """
    try:
        # Determine categories to include
        if categories:
            slugs = [s.strip() for s in categories.split(",") if s.strip()]
            cats = db.query(Category).filter(Category.slug.in_(slugs)).all()
        else:
            cats = db.query(Category).all()

        groups: List[IngredientGroup] = []
        for cat in cats:
            base_q = (
                db.query(IngredientEntity)
                .join(IngredientEntity.categories)
                .filter(Category.id == cat.id)
            )
            if sort == "name_desc":
                base_q = base_q.order_by(IngredientEntity.name.desc())
            else:
                base_q = base_q.order_by(IngredientEntity.name.asc())

            total = base_q.count()
            items = base_q.limit(size_per_group).all()
            groups.append(
                IngredientGroup(
                    category_id=cat.id,
                    category_name=cat.name,
                    category_slug=cat.slug,
                    total=total,
                    page=1,
                    size=size_per_group,
                    items=[IngredientEntityResponse.model_validate(i) for i in items],
                )
            )

        return IngredientGroupsResponse(groups=groups)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error building ingredient groups: {str(e)}",
        )


@router.get("/ingredients/{ingredient_id}", response_model=IngredientEntityResponse)
async def get_ingredient_by_id(
    ingredient_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a single ingredient by its ID.

    This endpoint retrieves detailed information about a specific ingredient,
    including its health outcomes with pillar mappings and compound information.

    **Authentication required** - users must be logged in to view ingredient details.

    Args:
        ingredient_id: Unique identifier for the ingredient
        db: Database session
        current_user: Currently authenticated user

    Returns:
        IngredientEntityResponse: Detailed ingredient information

    Raises:
        HTTPException 404: If ingredient with given ID is not found
        HTTPException 500: If database error occurs

    Example:
        GET /api/v1/entities/ingredients/garlic

        Response:
        ```json
        {
            "id": "garlic",
            "name": "Garlic",
            "primary_classification": "ingredient",
            "health_outcomes": [
                {
                    "outcome": "Garlic",
                    "confidence": 2,
                    "added_at": "2025-10-13T15:43:02.734596+00:00",
                    "pillars": [3, 6, 8]
                }
            ],
            ...
        }
        ```
    """
    try:
        # Query for the specific ingredient
        ingredient = db.query(IngredientEntity).filter(
            IngredientEntity.id == ingredient_id
        ).first()

        # Check if ingredient exists
        if not ingredient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ingredient with ID '{ingredient_id}' not found"
            )

        # Validate and return the ingredient
        return IngredientEntityResponse.model_validate(ingredient)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving ingredient: {str(e)}"
        )


@router.post("/search", response_model=EntitySearchResponse)
async def search_entities(
    search_request: EntitySearchRequest,
    db: Session = Depends(get_db)
):
    """
    Search entities with complex filtering criteria.
    
    Args:
        search_request: Search parameters
        db: Database session
        
    Returns:
        EntitySearchResponse: Search results with metadata
    """
    try:
        # Use search service
        entities, total_count, execution_time = SearchService.search_entities(
            db, search_request
        )
        
        # Convert to response format
        entity_responses = [EntityResponse.model_validate(entity) for entity in entities]
        
        # Build filters applied dict
        filters_applied = {}
        if search_request.primary_classification:
            filters_applied["primary_classification"] = search_request.primary_classification
        if search_request.classifications:
            filters_applied["classifications"] = search_request.classifications
        if search_request.health_outcomes:
            filters_applied["health_outcomes"] = search_request.health_outcomes
        if search_request.compound_ids:
            filters_applied["compound_ids"] = search_request.compound_ids
        if search_request.attributes:
            filters_applied["attributes"] = search_request.attributes
        
        return EntitySearchResponse(
            entities=entity_responses,
            total=total_count,
            query=search_request.query,
            filters_applied=filters_applied,
            execution_time_ms=execution_time
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching entities: {str(e)}"
        )


@router.post("/simple-search")
async def simple_ingredient_search(
    payload: dict,
    db: Session = Depends(get_db)
):
    """
    Lightweight ingredient name search for autocomplete.

    Accepts {"name_contains": "app"} and returns [{"id":"apple","name":"Apple"}, ...].
    Case-insensitive, limited to ingredients only. Returns at most 15 results.
    """
    try:
        term = (payload or {}).get("name_contains", "")
        term = (term or "").strip()
        if not term:
            return {"results": []}

        query = (
            db.query(IngredientEntity.id, IngredientEntity.name)
            .filter(IngredientEntity.name.ilike(f"%{term}%"))
        ).limit(15)

        results = [{"id": row[0], "name": row[1]} for row in query.all()]
        return {"results": results}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching ingredients: {str(e)}"
        )


@router.get("/{entity_id}", response_model=EntityResponse)
async def get_entity(
    entity_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a specific entity by ID.
    
    Args:
        entity_id: Entity ID
        db: Database session
        
    Returns:
        EntityResponse: Entity information
        
    Raises:
        HTTPException: If entity not found
    """
    try:
        entity = db.query(Entity).filter(Entity.id == entity_id).first()
        
        if not entity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Entity with ID '{entity_id}' not found"
            )
        
        entity = _normalize_entity_for_response(entity)
        return EntityResponse.model_validate(entity)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving entity: {str(e)}"
        )


@router.get("/{entity_id}/connections")
async def get_entity_connections(
    entity_id: str,
    relationship_types: Optional[List[str]] = Query(None, description="Filter by relationship types"),
    max_depth: int = Query(2, ge=1, le=5, description="Maximum relationship depth"),
    db: Session = Depends(get_db)
):
    """
    Get entity connections and relationships.
    
    Args:
        entity_id: Entity ID
        relationship_types: Filter by relationship types
        max_depth: Maximum relationship depth
        db: Database session
        
    Returns:
        Dict with connection information
    """
    try:
        connections = SearchService.get_entity_connections(
            db, entity_id, relationship_types, max_depth
        )
        
        if "error" in connections:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=connections["error"]
            )
        
        return connections
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving entity connections: {str(e)}"
        )


@router.get("/{entity_id}/path/{target_id}")
async def get_relationship_path(
    entity_id: str,
    target_id: str,
    max_depth: int = Query(3, ge=1, le=5, description="Maximum path depth"),
    db: Session = Depends(get_db)
):
    """
    Find relationship path between two entities.
    
    Args:
        entity_id: Source entity ID
        target_id: Target entity ID
        max_depth: Maximum path depth
        db: Database session
        
    Returns:
        Dict with path information
    """
    try:
        path = SearchService.find_relationship_path(db, entity_id, target_id, max_depth)
        
        if path is None:
            return {
                "source_id": entity_id,
                "target_id": target_id,
                "path": [],
                "path_length": 0,
                "found": False,
                "message": "No relationship path found"
            }
        
        return {
            "source_id": entity_id,
            "target_id": target_id,
            "path": [rel.to_dict() for rel in path],
            "path_length": len(path),
            "found": True,
            "total_confidence": sum(rel.confidence_score for rel in path),
            "avg_confidence": sum(rel.confidence_score for rel in path) / len(path)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error finding relationship path: {str(e)}"
        )


@router.get("/stats/overview", response_model=EntityStatsResponse)
async def get_entity_statistics(
    db: Session = Depends(get_db)
):
    """
    Get entity statistics and overview.
    
    Args:
        db: Database session
        
    Returns:
        EntityStatsResponse: Entity statistics
    """
    try:
        stats = SearchService.get_entity_statistics(db)
        
        return EntityStatsResponse(
            total_entities=stats["total_entities"],
            by_classification=stats["by_classification"],
            by_primary_classification=stats["by_classification"],  # Same data for now
            recent_additions=stats["recent_additions"],
            last_updated=stats["last_updated"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving entity statistics: {str(e)}"
        )


@router.get("/suggestions/search")
async def get_entity_suggestions(
    query: str = Query(..., min_length=1, description="Search query"),
    entity_type: Optional[str] = Query(None, description="Filter by entity type"),
    limit: int = Query(10, ge=1, le=20, description="Maximum suggestions"),
    db: Session = Depends(get_db)
):
    """
    Get entity suggestions for search autocomplete.
    
    Args:
        query: Search query
        entity_type: Filter by entity type
        limit: Maximum number of suggestions
        db: Database session
        
    Returns:
        List of entity suggestions
    """
    try:
        suggestions = SearchService.suggest_entities(db, query, entity_type, limit)
        
        return {
            "suggestions": suggestions,
            "query": query,
            "total_suggestions": len(suggestions)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting entity suggestions: {str(e)}"
        )


# Protected endpoints (require authentication)
@router.post("/", response_model=EntityResponse)
async def create_entity(
    entity_data: EntityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new entity (requires authentication).
    
    Args:
        entity_data: Entity creation data
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        EntityResponse: Created entity
    """
    try:
        # Check if entity already exists
        existing_entity = db.query(Entity).filter(Entity.id == entity_data.id).first()
        if existing_entity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Entity with ID '{entity_data.id}' already exists"
            )
        
        # Create entity (ensure attributes are plain dicts for JSON storage)
        raw_attrs = entity_data.attributes or {}
        attributes_dumped = {
            key: (value.model_dump() if hasattr(value, "model_dump") else value)
            for key, value in raw_attrs.items()
        }
        entity = Entity(
            id=entity_data.id,
            name=entity_data.name,
            primary_classification=entity_data.primary_classification,
            classifications=entity_data.classifications,
            attributes=attributes_dumped
        )
        
        db.add(entity)
        db.commit()
        db.refresh(entity)
        
        return EntityResponse.model_validate(entity)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating entity: {str(e)}"
        )


@router.put("/{entity_id}", response_model=EntityResponse)
async def update_entity(
    entity_id: str,
    entity_data: EntityUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update an existing entity (requires authentication).
    
    Args:
        entity_id: Entity ID
        entity_data: Entity update data
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        EntityResponse: Updated entity
    """
    try:
        entity = db.query(Entity).filter(Entity.id == entity_id).first()
        
        if not entity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Entity with ID '{entity_id}' not found"
            )
        
        # Update fields
        if entity_data.name is not None:
            entity.name = entity_data.name
        if entity_data.primary_classification is not None:
            entity.primary_classification = entity_data.primary_classification
        if entity_data.classifications is not None:
            entity.classifications = entity_data.classifications
        if entity_data.attributes is not None:
            raw_attrs = entity_data.attributes or {}
            entity.attributes = {
                key: (value.model_dump() if hasattr(value, "model_dump") else value)
                for key, value in raw_attrs.items()
            }
        
        db.commit()
        db.refresh(entity)
        
        return EntityResponse.model_validate(entity)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating entity: {str(e)}"
        )


@router.delete("/{entity_id}")
async def delete_entity(
    entity_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete an entity (requires authentication).
    
    Args:
        entity_id: Entity ID
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Dict with deletion confirmation
    """
    try:
        entity = db.query(Entity).filter(Entity.id == entity_id).first()
        
        if not entity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Entity with ID '{entity_id}' not found"
            )
        
        db.delete(entity)
        db.commit()
        
        return {
            "message": f"Entity '{entity_id}' deleted successfully",
            "deleted_at": "now"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting entity: {str(e)}"
        )


@router.get("/ingredients/missing-micros")
async def list_missing_vitamins_minerals(db: Session = Depends(get_db)):
    """
    Report ingredients missing vitamins/minerals or containing invalid micronutrient entries.
    - missing_micros: no vitamins/minerals present
    - has_macros_in_micros: micronutrient list includes protein/fat/carbs entries
    - duplicates: repeated micronutrient names after normalization
    """
    BaseEnt = aliased(Entity)
    items = (
        db.query(IngredientEntity)
        .select_from(IngredientEntity)
        .join(BaseEnt, BaseEnt.id == IngredientEntity.id)
        .all()
    )
    report = []

    def normalize_name(n: Any) -> str:
        if isinstance(n, dict):
            name = n.get("nutrient_name") or n.get("name") or ""
        else:
            name = str(n or "")
        return name.strip()

    macro_like = {"protein", "proteins", "fat", "fats", "carb", "carbs", "carbohydrate", "carbohydrates"}

    for ing in items:
        attrs = getattr(ing, "attributes", {}) or {}
        micros = attrs.get("nutrient_references")
        if isinstance(micros, dict) and "value" in micros:
            micros = micros.get("value")
        names = [normalize_name(x) for x in (micros or [])]
        names_lower = [s.lower() for s in names]
        has_micros = any(n for n in names_lower if n and n not in macro_like)
        has_macros = any(n in macro_like for n in names_lower)
        duplicates = sorted({n for n in names if names_lower.count(n.lower()) > 1})

        report.append({
            "id": ing.id,
            "name": getattr(ing, "name", ing.id),
            "missing_micros": not has_micros,
            "has_macros_in_micros": has_macros,
            "duplicates": duplicates,
        })

    return {"items": report}
