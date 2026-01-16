import gradio as gr
import random

def screen_fnol_claim(claim_source, loss_severity, incident_category):
    """Screen FNOL claim and recommend routing"""
    # Routing logic
    if loss_severity <= 2 and claim_source in ['App', 'Call Center']:
        route = "Fast Track"
        route_color = "🟢"
        priority = "Low"
        estimated_resolution = "1-3 days"
        document_checklist = ["Claim form", "Initial photos"]
    elif loss_severity > 2 and incident_category in ['Auto Collision', 'Property']:
        route = "Standard Review"
        route_color = "🟡"
        priority = "Medium"
        estimated_resolution = "3-7 days"
        document_checklist = ["Claim form", "Photos", "Police report", "Estimates"]
    elif loss_severity >= 4:
        route = "Escalation"
        route_color = "🔴"
        priority = "High"
        estimated_resolution = "7+ days"
        document_checklist = ["Claim form", "Photos", "Police report", "Expert assessment", "Legal review"]
    else:
        route = "Standard Review"
        route_color = "🟡"
        priority = "Medium"
        estimated_resolution = "3-7 days"
        document_checklist = ["Claim form", "Photos", "Witness statements"]
    
    # Uncertainty score
    uncertainty_score = round(random.uniform(0.1, 0.9), 2)
    
    return route, route_color, priority, estimated_resolution, "\n".join(document_checklist), uncertainty_score

with gr.Blocks(theme=gr.themes.Soft(), title="FNOL Fast Triage Agent") as demo:
    gr.Markdown("""
    # FNOL Fast Triage Agent
    
    **GCC Generic First Notice of Loss Screening Tool**
    
    ## ⚠️ CRITICAL DISCLAIMER
    
    **This application demonstrates fictional insurance logic using synthetic data only.**
    
    - ❌ NOT for real FNOL processing
    - ❌ NOT for production use
    - ✅ Educational and demonstration purposes ONLY
    - ✅ Synthetic data with no real-world application
    - ✅ Human review MANDATORY for all decisions
    
    **All outputs require human validation by qualified professionals.**
    """)
    
    with gr.Row():
        with gr.Column():
            claim_source = gr.Dropdown(
                choices=['App', 'Call Center', 'Agent', 'Direct'],
                value='App',
                label="Claim Source"
            )
            loss_severity = gr.Slider(minimum=1, maximum=5, value=2, step=1, label="Loss Severity (1-5)")
            incident_category = gr.Dropdown(
                choices=['Auto Collision', 'Property', 'Liability', 'Workers Comp', 'General'],
                value='Auto Collision',
                label="Incident Category"
            )
            
            submit_btn = gr.Button("Screen Claim", variant="primary")
        
        with gr.Column():
            route_output = gr.Textbox(label="Routing Recommendation", interactive=False)
            route_color_output = gr.Textbox(label="Priority Indicator", interactive=False)
            priority_output = gr.Textbox(label="Priority Level", interactive=False)
            resolution_output = gr.Textbox(label="Estimated Resolution Time", interactive=False)
            checklist_output = gr.Textbox(label="Required Documents", interactive=False)
            uncertainty_output = gr.Number(label="Uncertainty Score", interactive=False)
    
    submit_btn.click(
        fn=screen_fnol_claim,
        inputs=[claim_source, loss_severity, incident_category],
        outputs=[route_output, route_color_output, priority_output, resolution_output, checklist_output, uncertainty_output]
    )

if __name__ == "__main__":
    demo.launch()
