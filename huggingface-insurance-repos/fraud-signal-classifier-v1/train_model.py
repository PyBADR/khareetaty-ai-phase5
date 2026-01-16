"""
Fraud Signal Classifier v1 - Training Script

This script trains a baseline fraud detection classifier on synthetic insurance claims data.
The model is trained on 100% synthetic data and is for educational purposes only.

Features:
- policy_type: Type of insurance policy
- claimant_profile_risk: Risk level of the claimant
- incident_pattern: Pattern of the incident
- document_consistency_score: Score indicating document consistency
- anomaly_score: Anomaly detection score

Target:
- synthetic_flag_label: Fraud risk label (Clean, Under Review, Flagged, Confirmed Fraud)
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib
import os
import json

# Configuration
DATA_PATH = "../insurance-datasets-synthetic/data/fraud_cases_synthetic.csv"
MODEL_OUTPUT_PATH = "model.pkl"
ENCODER_OUTPUT_PATH = "label_encoders.pkl"
FEATURE_NAMES_PATH = "feature_names.json"

def load_and_prepare_data(data_path):
    """Load CSV and prepare data for training"""
    print("📊 Loading data from:", data_path)
    df = pd.read_csv(data_path)
    
    print(f"✓ Loaded {len(df)} records")
    print(f"✓ Columns: {list(df.columns)}")
    
    # Display class distribution
    print("\n📈 Target distribution:")
    print(df['synthetic_flag_label'].value_counts())
    
    return df

def encode_categorical_features(df):
    """Encode categorical features using LabelEncoder"""
    print("\n🔄 Encoding categorical features...")
    
    label_encoders = {}
    df_encoded = df.copy()
    
    # Categorical columns to encode
    categorical_cols = ['policy_type', 'claimant_profile_risk', 'incident_pattern']
    
    for col in categorical_cols:
        le = LabelEncoder()
        df_encoded[col] = le.fit_transform(df[col])
        label_encoders[col] = le
        print(f"  ✓ Encoded {col}: {len(le.classes_)} unique values")
    
    return df_encoded, label_encoders

def train_classifier(X_train, y_train):
    """Train Random Forest Classifier"""
    print("\n🤖 Training Random Forest Classifier...")
    
    # Using Random Forest for better performance on mixed features
    clf = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        class_weight='balanced'  # Handle class imbalance
    )
    
    clf.fit(X_train, y_train)
    print("✓ Model trained successfully")
    
    return clf

def evaluate_model(clf, X_test, y_test, label_encoder):
    """Evaluate model performance"""
    print("\n📊 Evaluating model...")
    
    y_pred = clf.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"\n✅ Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
    
    print("\n📋 Classification Report:")
    print(classification_report(y_test, y_pred, 
                                target_names=label_encoder.classes_,
                                zero_division=0))
    
    print("\n📊 Confusion Matrix:")
    cm = confusion_matrix(y_test, y_pred)
    print(cm)
    
    # Feature importance
    print("\n🎯 Top 5 Feature Importances:")
    feature_importance = sorted(zip(clf.feature_importances_, 
                                   ['policy_type', 'claimant_profile_risk', 
                                    'incident_pattern', 'document_consistency_score', 
                                    'anomaly_score']),
                               reverse=True)
    for importance, feature in feature_importance:
        print(f"  {feature}: {importance:.4f}")
    
    return accuracy

def save_model_artifacts(clf, label_encoders, target_encoder, feature_names):
    """Save model and encoders"""
    print("\n💾 Saving model artifacts...")
    
    # Save the trained model
    joblib.dump(clf, MODEL_OUTPUT_PATH)
    print(f"  ✓ Model saved to {MODEL_OUTPUT_PATH}")
    
    # Save encoders (including target encoder)
    encoders_dict = {
        'feature_encoders': label_encoders,
        'target_encoder': target_encoder
    }
    joblib.dump(encoders_dict, ENCODER_OUTPUT_PATH)
    print(f"  ✓ Encoders saved to {ENCODER_OUTPUT_PATH}")
    
    # Save feature names for inference
    with open(FEATURE_NAMES_PATH, 'w') as f:
        json.dump({'features': feature_names}, f, indent=2)
    print(f"  ✓ Feature names saved to {FEATURE_NAMES_PATH}")

def main():
    """Main training pipeline"""
    print("=" * 60)
    print("🚀 FRAUD SIGNAL CLASSIFIER V1 - TRAINING")
    print("=" * 60)
    print("\n⚠️  WARNING: This model uses 100% SYNTHETIC data")
    print("   Educational purposes only - NOT for production use\n")
    
    # Load data
    df = load_and_prepare_data(DATA_PATH)
    
    # Encode categorical features
    df_encoded, label_encoders = encode_categorical_features(df)
    
    # Prepare features and target
    feature_cols = ['policy_type', 'claimant_profile_risk', 'incident_pattern', 
                   'document_consistency_score', 'anomaly_score']
    
    X = df_encoded[feature_cols].values
    y = df_encoded['synthetic_flag_label'].values
    
    # Encode target variable
    target_encoder = LabelEncoder()
    y_encoded = target_encoder.fit_transform(y)
    
    print(f"\n✓ Features shape: {X.shape}")
    print(f"✓ Target classes: {list(target_encoder.classes_)}")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
    )
    
    print(f"✓ Training set: {len(X_train)} samples")
    print(f"✓ Test set: {len(X_test)} samples")
    
    # Train model
    clf = train_classifier(X_train, y_train)
    
    # Evaluate model
    accuracy = evaluate_model(clf, X_test, y_test, target_encoder)
    
    # Save artifacts
    save_model_artifacts(clf, label_encoders, target_encoder, feature_cols)
    
    print("\n" + "=" * 60)
    print(f"✅ TRAINING COMPLETE - Accuracy: {accuracy*100:.2f}%")
    print("=" * 60)
    print("\n📦 Generated files:")
    print(f"  - {MODEL_OUTPUT_PATH}")
    print(f"  - {ENCODER_OUTPUT_PATH}")
    print(f"  - {FEATURE_NAMES_PATH}")
    print("\n🎯 Next steps:")
    print("  1. Test inference with inference.py")
    print("  2. Review model_card.md")
    print("  3. Push to Hugging Face Hub")
    print("\n⚠️  Remember: Human-in-the-loop validation required for all predictions")

if __name__ == "__main__":
    main()
