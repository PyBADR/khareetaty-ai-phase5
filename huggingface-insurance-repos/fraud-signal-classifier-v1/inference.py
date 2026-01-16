"""
Fraud Signal Classifier v1 - Inference Script

This script provides inference capabilities for the fraud signal classifier.
It loads the trained model and provides prediction with probability scores and bucket mapping.

⚠️  WARNING: This model is trained on 100% synthetic data
   - Educational purposes ONLY
   - NOT for production underwriting decisions
   - Human-in-the-loop review REQUIRED for all predictions
"""

import joblib
import numpy as np
import json
import os
from typing import Dict, Tuple, List

class FraudSignalClassifier:
    """Fraud Signal Classifier for inference"""
    
    def __init__(self, model_path="model.pkl", encoder_path="label_encoders.pkl"):
        """
        Initialize the classifier with trained model and encoders
        
        Args:
            model_path: Path to the trained model pickle file
            encoder_path: Path to the label encoders pickle file
        """
        self.model = None
        self.encoders = None
        self.feature_encoders = None
        self.target_encoder = None
        
        self.load_model(model_path, encoder_path)
    
    def load_model(self, model_path, encoder_path):
        """Load trained model and encoders"""
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")
        if not os.path.exists(encoder_path):
            raise FileNotFoundError(f"Encoder file not found: {encoder_path}")
        
        print(f"📦 Loading model from {model_path}")
        self.model = joblib.load(model_path)
        
        print(f"📦 Loading encoders from {encoder_path}")
        self.encoders = joblib.load(encoder_path)
        self.feature_encoders = self.encoders['feature_encoders']
        self.target_encoder = self.encoders['target_encoder']
        
        print("✅ Model and encoders loaded successfully")
    
    def encode_input(self, policy_type: str, claimant_profile_risk: str, 
                    incident_pattern: str, document_consistency_score: float, 
                    anomaly_score: float) -> np.ndarray:
        """
        Encode input features for prediction
        
        Args:
            policy_type: Type of insurance policy
            claimant_profile_risk: Risk level of claimant
            incident_pattern: Pattern of incident
            document_consistency_score: Document consistency score (0-1)
            anomaly_score: Anomaly detection score (0-1)
        
        Returns:
            Encoded feature array
        """
        # Encode categorical features
        try:
            policy_encoded = self.feature_encoders['policy_type'].transform([policy_type])[0]
        except ValueError:
            print(f"⚠️  Unknown policy_type '{policy_type}', using default")
            policy_encoded = 0
        
        try:
            risk_encoded = self.feature_encoders['claimant_profile_risk'].transform([claimant_profile_risk])[0]
        except ValueError:
            print(f"⚠️  Unknown claimant_profile_risk '{claimant_profile_risk}', using default")
            risk_encoded = 0
        
        try:
            pattern_encoded = self.feature_encoders['incident_pattern'].transform([incident_pattern])[0]
        except ValueError:
            print(f"⚠️  Unknown incident_pattern '{incident_pattern}', using default")
            pattern_encoded = 0
        
        # Combine features
        features = np.array([[
            policy_encoded,
            risk_encoded,
            pattern_encoded,
            document_consistency_score,
            anomaly_score
        ]])
        
        return features
    
    def predict_proba(self, policy_type: str, claimant_profile_risk: str, 
                     incident_pattern: str, document_consistency_score: float, 
                     anomaly_score: float) -> Tuple[np.ndarray, List[str]]:
        """
        Predict fraud probability for given input
        
        Returns:
            Tuple of (probability array, class labels)
        """
        features = self.encode_input(
            policy_type, claimant_profile_risk, incident_pattern,
            document_consistency_score, anomaly_score
        )
        
        probabilities = self.model.predict_proba(features)[0]
        class_labels = self.target_encoder.classes_.tolist()
        
        return probabilities, class_labels
    
    def predict(self, policy_type: str, claimant_profile_risk: str, 
               incident_pattern: str, document_consistency_score: float, 
               anomaly_score: float) -> str:
        """
        Predict fraud label for given input
        
        Returns:
            Predicted class label
        """
        features = self.encode_input(
            policy_type, claimant_profile_risk, incident_pattern,
            document_consistency_score, anomaly_score
        )
        
        prediction = self.model.predict(features)[0]
        label = self.target_encoder.inverse_transform([prediction])[0]
        
        return label
    
    def get_fraud_score_and_bucket(self, policy_type: str, claimant_profile_risk: str, 
                                   incident_pattern: str, document_consistency_score: float, 
                                   anomaly_score: float) -> Dict:
        """
        Get comprehensive fraud assessment with score and bucket
        
        Returns:
            Dictionary with fraud_score, bucket, confidence, and all probabilities
        """
        probabilities, class_labels = self.predict_proba(
            policy_type, claimant_profile_risk, incident_pattern,
            document_consistency_score, anomaly_score
        )
        
        # Get predicted class
        predicted_class = self.predict(
            policy_type, claimant_profile_risk, incident_pattern,
            document_consistency_score, anomaly_score
        )
        
        # Calculate fraud score (weighted by severity)
        # Clean=0, Under Review=0.33, Flagged=0.66, Confirmed Fraud=1.0
        fraud_score_map = {
            'Clean': 0.0,
            'Under Review': 0.33,
            'Flagged': 0.66,
            'Confirmed Fraud': 1.0
        }
        
        # Calculate weighted fraud score
        fraud_score = sum(prob * fraud_score_map.get(label, 0.5) 
                         for prob, label in zip(probabilities, class_labels))
        
        # Map to bucket (Low, Medium, High)
        if fraud_score < 0.3:
            bucket = "Low"
        elif fraud_score < 0.6:
            bucket = "Medium"
        else:
            bucket = "High"
        
        # Get confidence (max probability)
        confidence = max(probabilities)
        
        # Build probability dict
        prob_dict = {label: float(prob) for label, prob in zip(class_labels, probabilities)}
        
        result = {
            'fraud_score': round(fraud_score, 3),
            'bucket': bucket,
            'predicted_class': predicted_class,
            'confidence': round(confidence, 3),
            'probabilities': prob_dict,
            'warning': '⚠️  HUMAN REVIEW REQUIRED - Educational model only'
        }
        
        return result
    
    def get_available_values(self) -> Dict:
        """Get available values for categorical features"""
        return {
            'policy_types': self.feature_encoders['policy_type'].classes_.tolist(),
            'risk_levels': self.feature_encoders['claimant_profile_risk'].classes_.tolist(),
            'incident_patterns': self.feature_encoders['incident_pattern'].classes_.tolist(),
            'target_classes': self.target_encoder.classes_.tolist()
        }


def demo_inference():
    """Demo inference with sample data"""
    print("=" * 70)
    print("🔍 FRAUD SIGNAL CLASSIFIER V1 - INFERENCE DEMO")
    print("=" * 70)
    
    # Initialize classifier
    classifier = FraudSignalClassifier()
    
    # Show available values
    print("\n📋 Available Values:")
    available = classifier.get_available_values()
    for key, values in available.items():
        print(f"  {key}: {values}")
    
    # Test cases
    test_cases = [
        {
            'name': 'Low Risk Case',
            'policy_type': 'Auto Collision',
            'claimant_profile_risk': 'Low Risk',
            'incident_pattern': 'Normal',
            'document_consistency_score': 0.95,
            'anomaly_score': 0.05
        },
        {
            'name': 'Medium Risk Case',
            'policy_type': 'Home Fire',
            'claimant_profile_risk': 'Medium Risk',
            'incident_pattern': 'Suspicious Timing',
            'document_consistency_score': 0.65,
            'anomaly_score': 0.45
        },
        {
            'name': 'High Risk Case',
            'policy_type': 'Auto Collision',
            'claimant_profile_risk': 'High Risk',
            'incident_pattern': 'Multiple Claims',
            'document_consistency_score': 0.35,
            'anomaly_score': 0.95
        }
    ]
    
    # Run predictions
    for test_case in test_cases:
        print(f"\n{'='*70}")
        print(f"🧪 Test Case: {test_case['name']}")
        print(f"{'='*70}")
        print(f"  Policy Type: {test_case['policy_type']}")
        print(f"  Risk Level: {test_case['claimant_profile_risk']}")
        print(f"  Incident Pattern: {test_case['incident_pattern']}")
        print(f"  Document Score: {test_case['document_consistency_score']}")
        print(f"  Anomaly Score: {test_case['anomaly_score']}")
        
        result = classifier.get_fraud_score_and_bucket(
            test_case['policy_type'],
            test_case['claimant_profile_risk'],
            test_case['incident_pattern'],
            test_case['document_consistency_score'],
            test_case['anomaly_score']
        )
        
        print(f"\n📊 RESULTS:")
        print(f"  Fraud Score: {result['fraud_score']:.3f}")
        print(f"  Bucket: {result['bucket']}")
        print(f"  Predicted Class: {result['predicted_class']}")
        print(f"  Confidence: {result['confidence']:.3f}")
        print(f"\n  Class Probabilities:")
        for label, prob in result['probabilities'].items():
            print(f"    {label}: {prob:.3f}")
        print(f"\n  {result['warning']}")
    
    print("\n" + "=" * 70)
    print("✅ INFERENCE DEMO COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    demo_inference()
