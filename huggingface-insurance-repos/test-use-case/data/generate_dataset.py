#!/usr/bin/env python3
"""
Synthetic Dataset Generator for test-use-case
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_synthetic_data(n_records=1000, version="v1"):
    """
    Generate synthetic insurance data
    
    Args:
        n_records: Number of records to generate
        version: Dataset version (v1, v2, etc.)
    
    Returns:
        pandas.DataFrame with synthetic data
    """
    np.random.seed(42 if version == "v1" else 43)
    
    data = {
        "record_id": [f"REC-{i:06d}" for i in range(n_records)],
        "timestamp": [datetime.now() - timedelta(days=random.randint(0, 365)) for _ in range(n_records)],
        "value": np.random.normal(1000, 200, n_records),
        "category": np.random.choice(["A", "B", "C", "D"], n_records),
        "score": np.random.uniform(0, 100, n_records),
        "flag": np.random.choice([True, False], n_records),
    }
    
    df = pd.DataFrame(data)
    
    # Add version metadata
    df.attrs["version"] = version
    df.attrs["generated"] = datetime.now().isoformat()
    df.attrs["synthetic"] = True
    
    return df

if __name__ == "__main__":
    # Generate v1
    df_v1 = generate_synthetic_data(1000, "v1")
    df_v1.to_csv("data/dataset_v1.csv", index=False)
    print(f"✓ Generated dataset_v1.csv ({len(df_v1)} records)")
    
    # Generate v2
    df_v2 = generate_synthetic_data(1500, "v2")
    df_v2.to_csv("data/dataset_v2.csv", index=False)
    print(f"✓ Generated dataset_v2.csv ({len(df_v2)} records)")
    
    print("
✅ Synthetic datasets created successfully!")
    print("⚠️  Remember: These are 100% synthetic - no real data used")
