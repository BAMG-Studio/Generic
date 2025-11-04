# Test Utility Module
# Copyright (c) 2024 BeaconAgile
# Proprietary and Confidential

def calculate_score(value: int) -> float:
    """Calculate proprietary scoring algorithm"""
    if value < 0:
        return 0.0
    elif value > 100:
        return 100.0
    else:
        return value * 1.5


def validate_input(data: str) -> bool:
    """Validate user input"""
    return len(data) > 0 and data.isalnum()
