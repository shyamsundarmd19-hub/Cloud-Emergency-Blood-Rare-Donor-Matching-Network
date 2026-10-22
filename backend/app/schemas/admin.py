from typing import Dict
from pydantic import BaseModel


class AnalyticsResponse(BaseModel):
    emergency_match_count: int
    active_donor_count: int
    total_donor_count: int
    verified_hospital_count: int
    total_blood_requests: int
    fulfilled_blood_requests: int
    completed_donations: int
    pledged_donations: int
    rare_blood_group_statistics: Dict[str, int]
    blood_group_distribution: Dict[str, int]
