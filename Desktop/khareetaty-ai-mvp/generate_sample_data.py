#!/usr/bin/env python3
"""
Generate sample incident data for Khareetaty AI
Creates a CSV file with realistic Kuwait crime data
"""

import csv
import random
from datetime import datetime, timedelta

# Kuwait governorates and zones
GOVERNORATES = {
    "Capital": ["Kuwait City", "Dasman", "Sharq", "Mirqab", "Salhiya"],
    "Hawalli": ["Hawalli", "Salmiya", "Rumaithiya", "Bayan", "Mishref"],
    "Farwaniya": ["Farwaniya", "Jleeb Al-Shuyoukh", "Khaitan", "Ardiya"],
    "Ahmadi": ["Ahmadi", "Fahaheel", "Mangaf", "Abu Halifa", "Fintas"],
    "Jahra": ["Jahra", "Qasr", "Sulaibiya", "Naeem"],
    "Mubarak Al-Kabeer": ["Mubarak Al-Kabeer", "Qurain", "Sabah Al-Salem", "Adan"]
}

# Incident types
INCIDENT_TYPES = [
    "theft", "assault", "vandalism", "traffic_accident", 
    "noise_complaint", "suspicious_activity", "fire", 
    "medical_emergency", "domestic_dispute"
]

# Kuwait geographic bounds (approximate)
LAT_MIN, LAT_MAX = 28.5, 30.1
LON_MIN, LON_MAX = 46.5, 48.5

def generate_incidents(num_incidents=500):
    """Generate sample incident data"""
    incidents = []
    
    # Generate incidents over the past 90 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)
    
    for i in range(num_incidents):
        # Random governorate and zone
        governorate = random.choice(list(GOVERNORATES.keys()))
        zone = random.choice(GOVERNORATES[governorate])
        
        # Random incident type
        incident_type = random.choice(INCIDENT_TYPES)
        
        # Random coordinates within Kuwait
        lat = round(random.uniform(LAT_MIN, LAT_MAX), 6)
        lon = round(random.uniform(LON_MIN, LON_MAX), 6)
        
        # Random timestamp in the past 90 days
        time_delta = random.random() * (end_date - start_date).total_seconds()
        timestamp = start_date + timedelta(seconds=time_delta)
        
        incidents.append({
            "incident_type": incident_type,
            "governorate": governorate,
            "zone": zone,
            "lat": lat,
            "lon": lon,
            "timestamp": timestamp.isoformat()
        })
    
    return incidents

def save_to_csv(incidents, filename="data/incidents.csv"):
    """Save incidents to CSV file"""
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ["incident_type", "governorate", "zone", "lat", "lon", "timestamp"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for incident in incidents:
            writer.writerow(incident)
    
    print(f"✅ Generated {len(incidents)} sample incidents")
    print(f"✅ Saved to {filename}")

if __name__ == "__main__":
    print("🔄 Generating sample incident data...")
    incidents = generate_incidents(500)
    save_to_csv(incidents)
    print("✅ Sample data generation complete!")
