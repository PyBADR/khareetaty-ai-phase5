import gradio as gr
import json
import datetime
import os
from typing import Dict, List

class FraudAuditLogger:
    def __init__(self, log_file="audit_log.jsonl"):
        self.log_file = log_file
        # Create file if it doesn't exist
        if not os.path.exists(log_file):
            with open(log_file, 'w') as f:
                pass  # Create empty file
    
    def write_audit_entry(self, claim_id, rule_hits, ml_score):
        """Write an audit entry to the log file"""
        entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "claim_id": claim_id,
            "rule_hits": rule_hits,
            "ml_score": ml_score,
            "session_id": f"session_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "user_action": "audit_entry_created",
            "source_system": "fraud-audit-log-engine",
            "version": "1.0"
        }
        
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')
        
        return entry
    
    def get_recent_entries(self, count=50):
        """Get the most recent audit entries"""
        if not os.path.exists(self.log_file):
            return []
        
        entries = []
        with open(self.log_file, 'r') as f:
            lines = f.readlines()
            # Get last 'count' lines
            recent_lines = lines[-count:] if len(lines) >= count else lines
        
        for line in recent_lines:
            try:
                entry = json.loads(line.strip())
                entries.append(entry)
            except json.JSONDecodeError:
                continue
        
        # Sort by timestamp (most recent first)
        entries.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        return entries
    
    def export_logs(self):
        """Export all logs as downloadable content"""
        if not os.path.exists(self.log_file):
            return "[]"
        
        with open(self.log_file, 'r') as f:
            content = f.read()
        
        return content

# Initialize logger
logger = FraudAuditLogger()

def add_audit_entry(claim_id, rule_hits, ml_score):
    """Add a new audit entry"""
    try:
        # Validate inputs
        if not claim_id:
            return "Error: Claim ID is required", "", "Error"
        
        # Ensure ml_score is between 0 and 1
        try:
            ml_score = float(ml_score) if ml_score else 0.0
            ml_score = max(0.0, min(1.0, ml_score))
        except ValueError:
            ml_score = 0.0
        
        # Write audit entry
        entry = logger.write_audit_entry(claim_id, rule_hits, ml_score)
        
        # Get recent entries
        recent_entries = logger.get_recent_entries(10)  # Show last 10
        
        # Format recent entries for display
        formatted_entries = []
        for entry in recent_entries[:10]:  # Limit to 10 for display
            formatted_entries.append(
                f"[{entry.get('timestamp', '')}] Claim: {entry.get('claim_id', '')} | "
                f"Rules: {entry.get('rule_hits', '')} | ML: {entry.get('ml_score', '')}"
            )
        
        recent_display = "\n".join(formatted_entries) if formatted_entries else "No recent entries found."
        
        # Success message
        message = f"Audit entry added successfully for Claim ID: {claim_id}"
        
        # Summary
        summary = f"""**Audit Entry Added:** ✓
**Claim ID:** {claim_id}
**Rule Hits:** {rule_hits}
**ML Score:** {ml_score}
**Timestamp:** {entry.get('timestamp', '')}

**Recent Entries:**
{recent_display}"""
        
        return message, recent_display, summary
        
    except Exception as e:
        error_msg = f"Error adding audit entry: {str(e)}"
        return error_msg, "", error_msg

def view_recent_logs():
    """View recent audit logs"""
    try:
        recent_entries = logger.get_recent_entries(20)
        
        if not recent_entries:
            return "No audit entries found in the log file.", "No recent entries"
        
        # Format for detailed display
        detailed_display = []
        for entry in recent_entries:
            detailed_display.append(f"""
**Timestamp:** {entry.get('timestamp', 'N/A')}
**Claim ID:** {entry.get('claim_id', 'N/A')}
**Rule Hits:** {entry.get('rule_hits', 'N/A')}
**ML Score:** {entry.get('ml_score', 'N/A')}
**Session:** {entry.get('session_id', 'N/A')}
---
""")
        
        detailed_str = "\n".join(detailed_display)
        
        # Format for summary display (last 10)
        summary_entries = recent_entries[:10]
        summary_display = []
        for entry in summary_entries:
            summary_display.append(
                f"[{entry.get('timestamp', '')}] Claim: {entry.get('claim_id', '')} | "
                f"Rules: {entry.get('rule_hits', '')} | ML: {entry.get('ml_score', '')}"
            )
        
        summary_str = "\n".join(summary_display) if summary_display else "No recent entries."
        
        return detailed_str, summary_str
        
    except Exception as e:
        return f"Error reading logs: {str(e)}", f"Error: {str(e)}"

def export_audit_logs():
    """Export audit logs"""
    try:
        content = logger.export_logs()
        if content.strip():
            return content, "Logs exported successfully"
        else:
            return "[]", "No logs to export"
    except Exception as e:
        return f"Error exporting logs: {str(e)}", f"Export failed: {str(e)}"

# Create Gradio interface
with gr.Blocks(title="Fraud Audit Log Engine", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # 🔍 Fraud Audit Log Engine
    
    **Audit Trail System for Fraud Detection Outcomes**
    
    ## ⚠️ CRITICAL DISCLAIMER
    
    **This application demonstrates fictional audit logging using synthetic data only.**
    
    - ❌ NOT for actual fraud blocking or approval
    - ❌ NOT for automated decision making
    - ❌ NOT for production fraud systems
    - ✅ Educational and demonstration purposes ONLY
    - ✅ Synthetic data with no real-world application
    - ✅ Human review MANDATORY for all decisions
    
    **This system creates audit trails only - no automated actions occur.**
    """)
    
    with gr.Tab("Add Audit Entry"):
        gr.Markdown("### Log a New Audit Entry")
        
        with gr.Row():
            with gr.Column():
                claim_id = gr.Textbox(
                    label="Claim ID (Synthetic)",
                    placeholder="Enter synthetic claim ID (e.g., CLM-001)",
                    value="CLM-001"
                )
                
                rule_hits = gr.Textbox(
                    label="Rule Hits",
                    placeholder="Comma-separated list of triggered rules",
                    value="High Claim Amount,Weekend Filing"
                )
                
                ml_score = gr.Number(
                    label="ML Score (0-1)",
                    value=0.65,
                    info="Machine learning fraud probability score (0.0-1.0)"
                )
                
                add_btn = gr.Button("📝 Add Audit Entry", variant="primary", size="lg")
            
            with gr.Column():
                gr.Markdown("### Recent Entries Preview")
                recent_summary = gr.Textbox(
                    label="Last 10 Entries",
                    lines=10,
                    interactive=False
                )
        
        with gr.Row():
            message_output = gr.Textbox(
                label="Status Message",
                lines=2,
                interactive=False
            )
        
        with gr.Row():
            summary_output = gr.Textbox(
                label="Entry Summary",
                lines=8,
                interactive=False
            )
    
    with gr.Tab("View Logs"):
        gr.Markdown("### Recent Audit Entries")
        
        with gr.Row():
            refresh_btn = gr.Button("🔄 Refresh Logs", variant="secondary")
        
        with gr.Row():
            recent_logs_output = gr.Textbox(
                label="Recent Audit Entries",
                lines=15,
                interactive=False
            )
    
    with gr.Tab("Export Logs"):
        gr.Markdown("### Export Audit Data")
        
        with gr.Row():
            export_btn = gr.Button("📥 Export JSONL", variant="secondary")
        
        with gr.Row():
            export_output = gr.Textbox(
                label="Exported Data",
                lines=15,
                interactive=False
            )
        
        with gr.Row():
            export_status = gr.Textbox(
                label="Export Status",
                lines=2,
                interactive=False
            )
    
    # Event handlers
    add_btn.click(
        fn=add_audit_entry,
        inputs=[claim_id, rule_hits, ml_score],
        outputs=[message_output, recent_summary, summary_output]
    )
    
    refresh_btn.click(
        fn=view_recent_logs,
        inputs=[],
        outputs=[recent_logs_output, recent_summary]
    )
    
    export_btn.click(
        fn=export_audit_logs,
        inputs=[],
        outputs=[export_output, export_status]
    )
    
    with gr.Accordion("ℹ️ About This Tool", open=False):
        gr.Markdown("""
        ## How It Works
        
        This audit engine creates **append-only audit trails** for fraud detection outcomes:
        
        ### Audit Entry Components
        
        1. **Claim ID**: Synthetic identifier for the claim
        2. **Rule Hits**: List of fraud rules that triggered
        3. **ML Score**: Machine learning fraud probability (if available)
        4. **Timestamp**: When the audit entry was created
        5. **Session ID**: Unique session identifier
        
        ### Logging Process
        
        - Entries are appended to `audit_log.jsonl` in JSONL format
        - Each entry is immutable once created
        - Logs are stored locally in the application directory
        - No entries are ever modified or deleted
        
        ### Security & Integrity
        
        - Append-only design prevents tampering
        - Timestamps provide chronological ordering
        - Session IDs enable audit trail tracking
        - Export function allows data backup
        
        ---
        
        **Built for GCC Insurance Intelligence Lab**
        
        This tool is NOT approved for actual fraud blocking, decision automation, or production fraud systems. All fraud decisions require human review.
        """)

if __name__ == "__main__":
    demo.launch()
