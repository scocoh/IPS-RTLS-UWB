# Name: entity_models.py
# Version: 0.1.0
# Created: 971201
# Modified: 250502
# Creator: ParcoAdmin
# Modified By: ParcoAdmin
# Description: Python script for ParcoRTLS backend
# Location: /home/parcoadmin/parco_fastapi/app
# Role: Backend
# Status: Active
# Dependent: TRUE

# /home/parcoadmin/parco_fastapi/app/entity_models.py
# Version: 0.1.0 - Initial entity models for ParcoRTLS Entity System
#
# ParcoRTLS Middletier Services, ParcoRTLS DLL, ParcoDatabases, ParcoMessaging, and other code
# Copyright (C) 1999 - 2025 Affiliated Commercial Services Inc.
# Invented by Scott Cohen & Bertrand Dugal.
# Coded by Jesse Chunn O.B.M.'24 and Michael Farnsworth and Others
# Published at GitHub https://github.com/scocoh/IPS-RTLS-UWB
#
# Licensed under AGPL-3.0: https://www.gnu.org/licenses/agpl-3.0.en.html

from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# Core Entity Models (mapped to PostgreSQL tables)
class Entity(BaseModel):
    id: str                     # x_id_ent, unique entity ID (e.g., ENT001)
    type_id: int                # i_typ_ent, references tlkentitytypes
    name: str                   # x_nm_ent, human-readable name
    created_at: Optional[datetime] = None  # d_crt, server timestamp
    updated_at: Optional[datetime] = None  # d_udt, server timestamp

class EntityAssignment(BaseModel):
    parent_id: str              # x_id_ent_prn, parent entity ID
    child_id: str               # x_id_ent_chd, child entity ID
    reason_id: Optional[int] = None  # i_rsn, optional reason ID
    start_time: datetime        # d_asn_bgn, assignment start
    end_time: Optional[datetime] = None  # d_asn_end, null if active

class EntityType(BaseModel):
    id: int                     # i_typ_ent, unique type ID
    description: str            # x_dsc_ent, type description
    created_at: Optional[datetime] = None  # d_crt, server timestamp
    updated_at: Optional[datetime] = None  # d_udt, server timestamp

# Request Models (for FastAPI endpoints in entity.py)
class EntityRequest(BaseModel):
    entity_id: str
    entity_type: int
    entity_name: Optional[str] = None

class EntityTypeRequest(BaseModel):
    type_name: str

class EntityAssignRequest(BaseModel):
    parent_id: str
    child_id: str
    reason_id: int

class EntityAssignEndRequest(BaseModel):
    assignment_id: int

class AssignmentReasonRequest(BaseModel):
    reason: str