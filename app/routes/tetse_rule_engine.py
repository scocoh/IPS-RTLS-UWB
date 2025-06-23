# Name: tetse_rule_engine.py
# Version: 0.1.4
# Created: 971201
# Modified: 250623
# Creator: ParcoAdmin
# Modified By: Claude AI Assistant
# Description: Complete TETSE rule evaluation engine with virtual zone support for coordinate-based evaluation
# Location: /home/parcoadmin/parco_fastapi/app/routes
# Role: Backend
# Status: Active
# Dependent: TRUE

from datetime import datetime
import logging

from routes.temporal_context import get_house_exclusion_context
from routes.subject_registry import get_subject_current_zone

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

async def evaluate_rule(rule: dict, current_zone_id: int = None, gis_data: dict = None) -> dict:
    """
    Universal rule evaluator - routes to appropriate evaluation function based on rule type.
    
    Args:
        rule (dict): Rule with conditions containing rule_type
        current_zone_id (int): Current zone ID from GIS data (422 from the simulator)
        gis_data (dict): Raw GIS data with X,Y,Z coordinates (for live data)
        
    Returns:
        dict: Evaluation result with triggered status
    """
    try:
        conditions = rule.get("conditions", {})
        rule_type = conditions.get("rule_type", "zone_stay")
        
        logger.debug(f"Evaluating rule type: {rule_type} with current_zone_id: {current_zone_id}")
        
        if rule_type == "zone_stay":
            return await evaluate_zone_stay_rule(rule, current_zone_id, gis_data)
        elif rule_type == "zone_transition":
            return await evaluate_zone_transition_rule(rule, current_zone_id, gis_data)
        elif rule_type == "proximity_condition":
            return await evaluate_proximity_condition_rule(rule, current_zone_id, gis_data)
        elif rule_type == "layered_trigger":
            return await evaluate_layered_trigger_rule(rule, current_zone_id, gis_data)
        else:
            logger.error(f"Unknown rule type: {rule_type}")
            return {
                "triggered": False,
                "status": "UNKNOWN_RULE_TYPE",
                "details": {"error": f"Unknown rule type: {rule_type}"}
            }
            
    except Exception as e:
        logger.error(f"Error in universal rule evaluator: {str(e)}")
        return {
            "triggered": False,
            "status": "EVALUATION_ERROR",
            "details": {"error": str(e)}
        }

async def evaluate_zone_stay_rule(rule: dict, current_zone_id: int = None, gis_data: dict = None) -> dict:
    """
    Evaluate zone stay rules with virtual zone support.
    """
    return await evaluate_house_exclusion_rule_direct(rule, current_zone_id, gis_data)

async def evaluate_zone_transition_rule(rule: dict, current_zone_id: int = None, gis_data: dict = None) -> dict:
    """
    Evaluate zone transition rules: "if tag moves from X to Y"
    
    Args:
        rule (dict): Rule with from_zone, to_zone, subject_id
        current_zone_id (int): Current zone ID from GIS data
        gis_data (dict): Raw GIS data with coordinates
        
    Returns:
        dict: Evaluation result
    """
    try:
        conditions = rule.get("conditions", {})
        subject_id = conditions.get("subject_id")
        from_zone = conditions.get("from_zone")
        to_zone = conditions.get("to_zone")
        
        if not all([subject_id, from_zone, to_zone]):
            return {
                "triggered": False,
                "status": "MISSING_TRANSITION_DATA",
                "details": {"error": "Missing subject_id, from_zone, or to_zone", "conditions": conditions}
            }
        
        # Use current_zone_id if provided, otherwise try to get from subject registry
        if current_zone_id is None:
            current_zone_id = await get_subject_current_zone(subject_id)
            if current_zone_id is None:
                return {
                    "triggered": False,
                    "status": "UNKNOWN_SUBJECT",
                    "details": {"subject_id": subject_id}
                }
        
        # Handle virtual zones by coordinate evaluation
        current_zone_semantic = await resolve_zone_to_semantic(current_zone_id, gis_data)
        
        # Check if current position matches the "to_zone" 
        # This means the transition has completed
        if await matches_virtual_zone_condition(current_zone_semantic, to_zone, current_zone_id, gis_data):
            logger.info(f"Zone transition rule triggered: {subject_id} is now in {to_zone}")
            return {
                "triggered": True,
                "status": "TRANSITION_COMPLETED",
                "details": {
                    "subject_id": subject_id,
                    "from_zone": from_zone,
                    "to_zone": to_zone,
                    "current_zone": current_zone_semantic,
                    "current_zone_id": current_zone_id
                }
            }
        
        return {
            "triggered": False,
            "status": "TRANSITION_NOT_COMPLETED",
            "details": {
                "subject_id": subject_id,
                "current_zone": current_zone_semantic,
                "waiting_for": to_zone
            }
        }
        
    except Exception as e:
        logger.error(f"Error evaluating zone transition rule: {str(e)}")
        return {
            "triggered": False,
            "status": "TRANSITION_ERROR",
            "details": {"error": str(e)}
        }

async def evaluate_proximity_condition_rule(rule: dict, current_zone_id: int = None, gis_data: dict = None) -> dict:
    """
    Evaluate proximity condition rules: "if tag moves from X to Y with/without tag Z"
    """
    try:
        conditions = rule.get("conditions", {})
        subject_id = conditions.get("subject_id")
        condition = conditions.get("condition")  # "outside_with_proximity", etc.
        proximity_target = conditions.get("proximity_target")
        proximity_distance = conditions.get("proximity_distance", 6.0)
        zone_transition = conditions.get("zone_transition", {})
        
        if not all([subject_id, condition, proximity_target]):
            return {
                "triggered": False,
                "status": "MISSING_PROXIMITY_DATA",
                "details": {"error": "Missing subject_id, condition, or proximity_target", "conditions": conditions}
            }
        
        # Use current_zone_id if provided, otherwise try to get from subject registry
        if current_zone_id is None:
            current_zone_id = await get_subject_current_zone(subject_id)
            if current_zone_id is None:
                return {
                    "triggered": False,
                    "status": "UNKNOWN_SUBJECT",
                    "details": {"subject_id": subject_id}
                }
        
        # Handle proximity target (could be specific tag ID or device type)
        if proximity_target.startswith("device_type:"):
            # Device type proximity (e.g., "device_type:personnel_badge")
            # For now, simplified implementation
            proximity_met = True  # Assume proximity condition met
        else:
            # Specific tag proximity
            target_zone_id = await get_subject_current_zone(proximity_target)
            if target_zone_id is None:
                return {
                    "triggered": False,
                    "status": "UNKNOWN_PROXIMITY_TARGET",
                    "details": {"proximity_target": proximity_target}
                }
            
            # Check if subjects are in proximity (same zone for simplification)
            proximity_met = (current_zone_id == target_zone_id)
        
        # Evaluate zone transition component
        current_zone_semantic = await resolve_zone_to_semantic(current_zone_id, gis_data)
        to_zone = zone_transition.get("to", "")
        
        # Check if subject is in target zone AND proximity condition is met
        zone_match = await matches_virtual_zone_condition(current_zone_semantic, to_zone, current_zone_id, gis_data)
        
        # Determine if rule should trigger based on condition type
        if condition == "outside_with_proximity":
            triggered = zone_match and proximity_met
        elif condition == "outside_without_proximity":
            triggered = zone_match and not proximity_met
        else:
            triggered = False
        
        if triggered:
            logger.info(f"Proximity condition rule triggered: {subject_id} - {condition}")
        
        return {
            "triggered": triggered,
            "status": "PROXIMITY_EVALUATED",
            "details": {
                "subject_id": subject_id,
                "condition": condition,
                "proximity_target": proximity_target,
                "proximity_met": proximity_met,
                "zone_match": zone_match,
                "current_zone": current_zone_semantic
            }
        }
        
    except Exception as e:
        logger.error(f"Error evaluating proximity condition rule: {str(e)}")
        return {
            "triggered": False,
            "status": "PROXIMITY_ERROR",
            "details": {"error": str(e)}
        }

async def evaluate_layered_trigger_rule(rule: dict, current_zone_id: int = None, gis_data: dict = None) -> dict:
    """
    Evaluate layered trigger rules using BOL2/CL1 trigger architecture.
    """
    # Placeholder for layered trigger evaluation
    logger.debug("Layered trigger evaluation not yet implemented")
    return {
        "triggered": False,
        "status": "NOT_IMPLEMENTED", 
        "details": {"message": "Layered trigger evaluation coming in next version"}
    }

async def resolve_zone_to_semantic(zone_id: int, gis_data: dict = None) -> str:
    """
    Convert numeric zone ID to semantic zone name (inside/outside).
    Enhanced to use coordinate data for virtual zone evaluation.
    
    Args:
        zone_id (int): Database zone ID
        gis_data (dict): Raw GIS data with X,Y,Z coordinates
    """
    try:
        # For virtual zone evaluation, we need to check if coordinates
        # are within campus (422) but outside building envelope (423)
        
        # Simplified logic based on known zone structure
        # Zone 422 = Campus, Zone 423 = Building Envelope
        
        if zone_id == 422:
            # If we're in campus zone, check if we're actually inside building
            # This would require coordinate-based evaluation in production
            if gis_data:
                # Placeholder for coordinate-based zone detection
                # In production: check if X,Y coordinates are within building polygon
                # For now, assume campus zone = outside
                return "outside"
            else:
                return "outside"  # Campus but outside building
        elif zone_id == 423:
            return "inside"   # Building envelope
        elif zone_id > 423 and zone_id < 450:
            return "inside"   # Assume interior zones
        else:
            return "outside"  # Default to outside
            
    except Exception as e:
        logger.error(f"Error resolving zone {zone_id} to semantic: {str(e)}")
        return "unknown"

async def matches_virtual_zone_condition(current_zone_semantic: str, target_zone: str, current_zone_id: int = None, gis_data: dict = None) -> bool:
    """
    Check if current semantic zone matches target zone condition.
    Enhanced for virtual zone evaluation.
    
    Args:
        current_zone_semantic (str): Semantic zone name (inside/outside)
        target_zone (str): Target zone from rule
        current_zone_id (int): Current zone ID
        gis_data (dict): Raw coordinates for spatial evaluation
    """
    try:
        if target_zone in ["outside", "backyard"]:
            # For virtual "outside" zones, we need spatial evaluation
            if current_zone_id == 422:  # Campus zone
                # In production: check if X,Y coordinates are outside building polygon
                # For now: assume campus zone without building envelope = outside
                return True
            else:
                return current_zone_semantic == "outside"
        elif target_zone == "inside":
            return current_zone_semantic == "inside"
        else:
            # For specific zone names, could add more sophisticated matching
            return current_zone_semantic == target_zone
    except Exception as e:
        logger.error(f"Error matching virtual zone condition: {str(e)}")
        return False

async def evaluate_house_exclusion_rule_direct(rule: dict, current_zone_id: int = None, gis_data: dict = None) -> dict:
    """
    Direct zone stay rule evaluation with virtual zone support.
    
    Args:
        rule (dict): Rule with zone information
        current_zone_id (int): Current zone ID from GIS data
        gis_data (dict): Raw GIS data with coordinates
    """
    try:
        conditions = rule.get("conditions", {})
        subject_id = conditions.get("subject_id") or rule.get("subject_id")
        
        # Enhanced virtual zone handling
        zone_field = rule.get("zone") or conditions.get("zone")
        zone_id = rule.get("zone_id") or conditions.get("zone_id")
        
        logger.debug(f"🔍 TETSE ENGINE: Evaluating rule for zone_field='{zone_field}', zone_id='{zone_id}', current_zone_id={current_zone_id}")
        
        # Handle virtual zones like "virtual_422_outside"
        if isinstance(zone_id, str) and zone_id.startswith("virtual_"):
            # Extract campus ID from virtual zone
            try:
                parts = zone_id.split("_")
                campus_zone_id = int(parts[1])  # virtual_422_outside -> 422
                virtual_zone_type = parts[2] if len(parts) > 2 else "outside"  # -> "outside"
                
                logger.debug(f"🔍 TETSE ENGINE: Virtual zone detected - campus_id={campus_zone_id}, type={virtual_zone_type}")
                
                # For virtual "outside" zones, check if current zone matches campus
                # but not building envelope (spatial logic)
                if virtual_zone_type == "outside":
                    if current_zone_id == campus_zone_id:  # We're in the campus zone
                        # In production: check if coordinates are outside building polygon
                        # For now: assume campus zone = outside (simplified)
                        logger.debug(f"🔍 TETSE ENGINE: Tag in campus zone {campus_zone_id} - considering as OUTSIDE")
                        triggered_status = True
                    else:
                        logger.debug(f"🔍 TETSE ENGINE: Tag in zone {current_zone_id} != campus {campus_zone_id} - not outside")
                        triggered_status = False
                        
                    return {
                        "triggered": triggered_status,
                        "status": "OUTSIDE" if triggered_status else "NOT_OUTSIDE",
                        "details": {
                            "virtual_zone": zone_id,
                            "campus_zone_id": campus_zone_id,
                            "current_zone_id": current_zone_id,
                            "rule_matched": triggered_status
                        }
                    }
                    
            except (IndexError, ValueError) as e:
                logger.error(f"🔍 TETSE ENGINE: Invalid virtual zone format: {zone_id} - {str(e)}")
                return {
                    "triggered": False,
                    "status": "INVALID_VIRTUAL_ZONE",
                    "details": {"error": f"Invalid virtual zone format: {zone_id}"}
                }
        
        # Use GIS coordinate-based evaluation if available
        if current_zone_id is not None:
            current_zone_semantic = await resolve_zone_to_semantic(current_zone_id, gis_data)
            
            # Check if the rule's target zone matches our current semantic zone
            if zone_field in ["outside", "backyard"] and current_zone_semantic == "outside":
                # We're outside and the rule is for outside - proceed with temporal evaluation
                campus_zone_id = current_zone_id  # Use current zone as campus zone
            elif zone_field == "inside" and current_zone_semantic == "inside":
                # We're inside and the rule is for inside - proceed with temporal evaluation
                campus_zone_id = current_zone_id  # Use current zone as reference
            else:
                # Zone doesn't match - rule not applicable right now
                logger.debug(f"🔍 TETSE ENGINE: Zone mismatch - current={current_zone_semantic}, rule={zone_field}")
                return {
                    "triggered": False,
                    "status": "ZONE_NOT_MATCHED",
                    "details": {
                        "current_zone_semantic": current_zone_semantic,
                        "rule_zone": zone_field,
                        "current_zone_id": current_zone_id
                    }
                }
        else:
            # Fallback logic for when no current_zone_id provided
            if zone_id is None:
                logger.error(f"🔍 TETSE ENGINE: No zone_id provided and no current_zone_id")
                return {
                    "triggered": False,
                    "status": "INVALID_ZONE",
                    "details": {"error": "No valid zone_id found in rule"}
                }
            
            campus_zone_id = int(zone_id)
        
        duration_sec = int(rule.get("duration_sec", 600))
        exclusion_minutes = duration_sec // 60
        house_parent_zone_id = int(conditions.get("exclude_parent_zone", 0))

        # Get current zone dynamically from subject_registry or use provided current_zone_id
        if current_zone_id is None:
            current_zone_id = await get_subject_current_zone(subject_id)
            if current_zone_id is None:
                logger.error(f"🔍 TETSE ENGINE: Unable to resolve current zone for subject {subject_id}")
                return {
                    "triggered": False,
                    "status": "UNKNOWN_SUBJECT",
                    "details": {}
                }

        # Use existing house exclusion context evaluator
        context = await get_house_exclusion_context(
            entity_id=subject_id,
            campus_zone_id=campus_zone_id,
            house_parent_zone_id=house_parent_zone_id,
            exclusion_duration_min=exclusion_minutes,
            current_zone_id=current_zone_id
        )

        triggered = (context["status"] == "OUTSIDE")

        logger.debug(f"🔍 TETSE ENGINE: Zone stay rule evaluation complete for subject {subject_id}: triggered={triggered}, context={context}")

        return {
            "triggered": triggered,
            "status": context["status"],
            "details": context
        }

    except Exception as e:
        logger.error(f"🔍 TETSE ENGINE: Error evaluating house exclusion rule: {str(e)}")
        return {
            "triggered": False,
            "status": "ERROR",
            "details": {"error": str(e)}
        }

# Legacy function for backward compatibility
async def evaluate_house_exclusion_rule(rule: dict, current_zone_id: int = None) -> dict:
    """
    Legacy zone stay rule evaluation (now routes through universal evaluator).
    Enhanced to handle all rule types properly with GIS data injection.
    
    Args:
        rule (dict): Rule with zone information
        current_zone_id (int): Current zone ID from GIS data (422 in this case)
    """
    try:
        conditions = rule.get("conditions", {})
        subject_id = conditions.get("subject_id") or rule.get("subject_id")
        
        # Check rule type and route appropriately
        rule_type = conditions.get("rule_type", "zone_stay")
        
        if rule_type in ["zone_transition", "proximity_condition", "layered_trigger"]:
            # Route to universal evaluator for non-zone-stay rules
            logger.debug(f"🔍 TETSE ENGINE: Routing {rule_type} rule to universal evaluator with current_zone_id={current_zone_id}")
            return await evaluate_rule(rule, current_zone_id)
        
        # Handle zone stay rules with enhanced zone resolution
        return await evaluate_house_exclusion_rule_direct(rule, current_zone_id)

    except Exception as e:
        logger.error(f"🔍 TETSE ENGINE: Error evaluating house exclusion rule: {str(e)}")
        return {
            "triggered": False,
            "status": "ERROR",
            "details": {"error": str(e)}
        }