# Name: data_processor.py
# Version: 0.1.0
# Created: 971201
# Modified: 250502
# Creator: ParcoAdmin
# Modified By: ParcoAdmin
# Description: Python script for ParcoRTLS backend
# Location: /home/parcoadmin/parco_fastapi/app/manager
# Role: Backend
# Status: Active
# Dependent: TRUE

# Version: 250327 /home/parcoadmin/parco_fastapi/app/manager/data_processor.py 1.0.2
# 
# Data Processor Module for Manager
#   
# ParcoRTLS Middletier Services, ParcoRTLS DLL, ParcoDatabases, ParcoMessaging, and other code
# Copyright (C) 1999 - 2025 Affiliated Commercial Services Inc.
# Invented by Scott Cohen & Bertrand Dugal.
# Coded by Jesse Chunn O.B.M.'24 and Michael Farnsworth and Others
# Published at GitHub https://github.com/scocoh/IPS-RTLS-UWB
#
# Licensed under AGPL-3.0: https://www.gnu.org/licenses/agpl-3.0.en.html

from typing import Dict, List, Tuple
from .models import GISData

class DataProcessor:
    def __init__(self, min_cnf: float = 50.0):  # CHANGED: Configurable, default 50
        self.last_tag: Dict[str, float] = {}  # ID: TS for duplicate check
        self.tag_history: Dict[str, List[GISData]] = {}  # Raw position history
        self.raw_ave: Dict[str, Tuple[float, float]] = {}  # 2D raw average (X, Y)
        self.cnf_threshold: float = min_cnf  # CHANGED: Use parameter
        self.max_history: int = 5  # Fixed window for now

    def filter_data(self, msg: GISData) -> bool:
        """Returns True if data passes filters, False if filtered out."""
        if msg.id in self.last_tag and self.last_tag[msg.id] == msg.ts.timestamp():
            return False
        self.last_tag[msg.id] = msg.ts.timestamp()
        if msg.cnf < self.cnf_threshold:
            return False
        return True

    def compute_raw_average(self, msg: GISData) -> None:
        """Computes 2D raw average over last 5 positions."""
        if msg.id not in self.tag_history:
            self.tag_history[msg.id] = []
        self.tag_history[msg.id].append(msg)
        if len(self.tag_history[msg.id]) > self.max_history:
            self.tag_history[msg.id].pop(0)
        if len(self.tag_history[msg.id]) == self.max_history:
            x_sum = sum(pos.x for pos in self.tag_history[msg.id])
            y_sum = sum(pos.y for pos in self.tag_history[msg.id])
            self.raw_ave[msg.id] = (x_sum / self.max_history, y_sum / self.max_history)