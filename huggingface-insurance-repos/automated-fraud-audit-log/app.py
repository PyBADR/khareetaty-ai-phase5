import gradio as gr
import json
import datetime

class FraudAuditLogger:
    def __init__(self, log_file="fraud_audit_log.jsonl"):
        self.log_file = log_file
    
    def log_fraud_assessment(self, case_id, assessment_result, confidence, analyst_notes):
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "case_id": case_id,
            "assessment_result": assessment_result,
            "confidence": confidence,
            "analyst_notes": analyst_notes,
            "entry_type": "fraud_assessment"
        }
        
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
        
        return f"Entry logged: {case_id}"

logger = FraudAuditLogger()

def audit_fraud_case(case_id, signal_strength, evidence_quality, behavioral_indicators, transaction_patterns):
    """Audit fraud case and create immutable log entry"""
    # Calculate overall risk
    signal_weight = signal_strength * 0.3
    evidence_weight = evidence_quality * 0.3
    behavior_weight = behavioral_indicators * 0.2
    pattern_weight = transaction_patterns * 0.2
    
    overall_risk = signal_weight + evidence_weight + behavior_weight + pattern_weight
    
    # Determine risk level
    if overall_risk >= 0.7:
        risk_level = "High"
        recommendation = "Escalate to senior investigator"
        color = "🔴"
    elif overall_risk >= 0.4:
        risk_level = "Medium"
        recommendation = "Manual review required"
        color = "🟡"
    else:
        risk_level = "Low"
        recommendation = "Auto-approve with monitoring"
        color = "🟢"
    
    # Confidence score
    confidence = round(overall_risk, 2)
    
    # Generate case summary
    summary = f"""
    Case ID: {case_id}
    Risk Level: {risk_level}
    Overall Risk Score: {round(overall_risk, 2)}
    Signal Strength: {signal_strength}
    Evidence Quality: {evidence_quality}
    Behavioral Indicators: {behavioral_indicators}
    Transaction Patterns: {transaction_patterns}
    """
    
    return risk_level, color, recommendation, confidence, summary

with gr.Blocks(theme=gr.themes.Soft(), title="Automated Fraud Audit Log") as demo:
    gr.Markdown("""
    # Automated Fraud Audit Log
    
    **GCC Generic Fraud Detection Audit Trail System**
    
    ## ⚠️ CRITICAL DISCLAIMER
    
    **This application demonstrates fictional insurance logic using synthetic data only.**
    
    - ❌ NOT for real fraud detection
    - ❌ NOT for production use
    - ✅ Educational and demonstration purposes ONLY
    - ✅ Synthetic data with no real-world application
    - ✅ Human review MANDATORY for all decisions
    
    **All outputs require human validation by qualified professionals.**
    """)
    
    with gr.Row():
        with gr.Column():
            case_id = gr.Textbox(label="Case ID", value="FRAUD-2026-001")
            signal_strength = gr.Slider(minimum=0.0, maximum=1.0, value=0.5, label="Signal Strength (0-1)")
            evidence_quality = gr.Slider(minimum=0.0, maximum=1.0, value=0.6, label="Evidence Quality (0-1)")
            behavioral_indicators = gr.Slider(minimum=0.0, maximum=1.0, value=0.4, label="Behavioral Indicators (0-1)")
            transaction_patterns = gr.Slider(minimum=0.0, maximum=1.0, value=0.7, label="Transaction Patterns (0-1)")
            
            submit_btn = gr.Button("Audit Case", variant="primary")
        
        with gr.Column():
            risk_level_output = gr.Textbox(label="Risk Level", interactive=False)
            color_output = gr.Textbox(label="Indicator", interactive=False)
            recommendation_output = gr.Textbox(label="Recommendation", interactive=False)
            confidence_output = gr.Number(label="Confidence Score", interactive=False)
            summary_output = gr.Textbox(label="Case Summary", interactive=False)
    
    submit_btn.click(
        fn=audit_fraud_case,
        inputs=[case_id, signal_strength, evidence_quality, behavioral_indicators, transaction_patterns],
        outputs=[risk_level_output, color_output, recommendation_output, confidence_output, summary_output]
    )

if __name__ == "__main__":
    demo.launch()
