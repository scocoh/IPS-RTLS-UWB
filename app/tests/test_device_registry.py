# Name: test_device_registry.py
# Version: 0.1.0
# Created: 971201
# Modified: 250502
# Creator: ParcoAdmin
# Modified By: ParcoAdmin
# Description: ParcoRTLS backend script
# Location: /home/parcoadmin/parco_fastapi/app/tests
# Role: Backend
# Status: Active
# Dependent: TRUE

#!/usr/bin/env python3
# Quick test script for device registry

import sys
import os
sys.path.append('/home/parcoadmin/parco_fastapi/app')

from routes.device_registry import get_subject_for_tag, get_registry_stats, DEVICE_REGISTRY

print("=== DEVICE REGISTRY DEBUG ===")
print(f"Registry size: {len(DEVICE_REGISTRY)}")
print(f"Registry contents: {DEVICE_REGISTRY}")
print(f"get_subject_for_tag('23001'): {get_subject_for_tag('23001')}")
print(f"get_registry_stats(): {get_registry_stats()}")

# Test with different variations
test_tags = ["23001", "23002", "23003"]
for tag in test_tags:
    result = get_subject_for_tag(tag)
    print(f"Tag {tag} -> Subject {result}")