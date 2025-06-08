# Name: test_llm_bridge.py
# Version: 0.1.5
# Created: 250601
# Modified: 250601
# Description: CLI test for llm_bridge.ask_openai and rule evaluation
# Location: /home/parcoadmin/parco_fastapi/app/tests/test_llm_bridge.py

import asyncio
from datetime import datetime, timezone
from routes.llm_bridge import ask_openai
from routes.openai_trigger_api import construct_prompt, TriggerInput, evaluate_rules
from routes.temporal_context import get_temporal_context
import asyncpg

async def test_rule_evaluation():
    """
    Test the rule evaluation process, including prompt construction, OpenAI response, and rule-based actions.
    """
    # Test trigger data
    test_trigger = TriggerInput(
        entity="Eddy",
        trigger="AnimalDetected",
        zone="Backyard",
        timestamp="2025-06-01T12:04:00Z",
        duration_sec=10,
        prior_state="None",
        sequence_id=12345
    )

    # Set event timestamp to 47 minutes before trigger time
    trigger_time = datetime.fromisoformat("2025-06-01T12:04:00+00:00")
    event_ts = trigger_time.replace(minute=17, hour=11)  # 11:17 AM, 47 minutes before 12:04 PM

    # Insert test data into event_log
    try:
        async with asyncpg.create_pool("postgresql://parcoadmin:parcoMCSE04106!@192.168.210.226:5432/ParcoRTLSData") as pool:
            async with pool.acquire() as conn:
                # Clear existing test data
                await conn.execute("DELETE FROM event_log WHERE entity_id = $1", "Eddy")
                # Insert new test data
                await conn.execute(
                    """
                    INSERT INTO event_log (entity_id, event_type_id, reason_id, value, unit, ts)
                    VALUES ($1, $2, $3, $4, $5, $6)
                    """,
                    "Eddy", 7, 4, 1.0, "zone:Living Room", event_ts
                )
                # Verify insertion
                result = await conn.fetch("SELECT * FROM event_log WHERE entity_id = $1", "Eddy")
                if not result:
                    print("Error: Failed to insert test data into event_log")
                    return
                print("Inserted test data:", result)
    except Exception as e:
        print(f"Error inserting test data: {e}")
        return

    # Generate prompt
    try:
        prompt = await construct_prompt(test_trigger)
        print("🔎 Generated Prompt:\n")
        print(prompt)
    except Exception as e:
        print(f"Error generating prompt: {e}")
        return

    # Get OpenAI response
    try:
        explanation = ask_openai(prompt)  # Synchronous call
        print("🔎 OpenAI Response:\n")
        print(explanation)
    except Exception as e:
        print(f"Error getting OpenAI response: {e}")
        return

    # Evaluate rules
    try:
        temporal_context = await get_temporal_context(test_trigger.entity)
        actions = await evaluate_rules(test_trigger, temporal_context)
        print("🔎 Evaluated Actions:\n")
        print(actions)
    except Exception as e:
        print(f"Error evaluating rules: {e}")
        return

if __name__ == "__main__":
    asyncio.run(test_rule_evaluation())