import streamlit as st
import requests
import json
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Any

# Page configuration
st.set_page_config(
    page_title="AI Medical Prescription Verifier",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .metric-container {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    
    .high-risk {
        background: #ffebee;
        border-left: 4px solid #f44336;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    .medium-risk {
        background: #fff3e0;
        border-left: 4px solid #ff9800;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    .low-risk {
        background: #e8f5e8;
        border-left: 4px solid #4caf50;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    .ai-insight {
        background: #e3f2fd;
        border-left: 4px solid #2196f3;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    .success-message {
        background: #e8f5e8;
        color: #2e7d32;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    
    .error-message {
        background: #ffebee;
        color: #c62828;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    
    .loading-message {
        background: #fff3e0;
        color: #f57c00;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

def check_backend_health():
    """Check if the FastAPI backend is running"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=10)
        return response.status_code == 200, response.json()
    except requests.exceptions.RequestException:
        return False, None

def format_confidence_score(score):
    """Format confidence score with color coding"""
    if score >= 0.9:
        return f"🟢 {score:.1%}"
    elif score >= 0.7:
        return f"🟡 {score:.1%}"
    else:
        return f"🔴 {score:.1%}"

def display_drug_extraction_results(extracted_drugs: List[Dict]):
    """Display extracted drugs with enhanced formatting"""
    st.subheader("🔍 AI-Powered Drug Extraction Results")
    
    if not extracted_drugs:
        st.warning("No drugs detected in the prescription text.")
        return
    
    # Create a summary metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Drugs Found", len(extracted_drugs))
    
    with col2:
        avg_confidence = sum(drug.get('confidence', 0) for drug in extracted_drugs) / len(extracted_drugs)
        st.metric("Avg Confidence", f"{avg_confidence:.1%}")
    
    with col3:
        granite_count = sum(1 for drug in extracted_drugs if 'granite' in drug.get('sources', []))
        st.metric("IBM Granite Detections", granite_count)
    
    with col4:
        pattern_count = sum(1 for drug in extracted_drugs if 'pattern' in drug.get('sources', []))
        st.metric("Pattern Matching", pattern_count)
    
    # Detailed drug information table
    st.markdown("### 📊 Detailed Extraction Results")
    
    drug_data = []
    for drug in extracted_drugs:
        drug_data.append({
            "Drug Name": drug['word'].title(),
            "Confidence": format_confidence_score(drug.get('confidence', 0)),
            "Sources": ", ".join(drug.get('sources', [])).title(),
            "Dosage": drug.get('dosage', 'Not specified'),
            "Frequency": drug.get('frequency', 'Not specified'),
            "Sentiment": drug.get('sentiment', 'Neutral').title()
        })
    
    df = pd.DataFrame(drug_data)
    st.dataframe(df, use_container_width=True)
    
    # Confidence distribution chart
    if len(extracted_drugs) > 1:
        fig = px.bar(
            x=[drug['word'].title() for drug in extracted_drugs],
            y=[drug.get('confidence', 0) for drug in extracted_drugs],
            title="Drug Detection Confidence Scores",
            labels={'x': 'Drug Names', 'y': 'Confidence Score'},
            color=[drug.get('confidence', 0) for drug in extracted_drugs],
            color_continuous_scale='RdYlGn'
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

def display_interactions(interactions: List[Dict]):
    """Display drug interactions with severity-based styling"""
    st.subheader("⚠️ Drug Interaction Analysis")
    
    if not interactions:
        st.success("✅ No significant drug interactions detected!")
        return
    
    # Interaction statistics
    high_risk = [i for i in interactions if i['severity'] == 'HIGH']
    medium_risk = [i for i in interactions if i['severity'] == 'MEDIUM']
    low_risk = [i for i in interactions if i['severity'] == 'LOW']
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🔴 High Risk", len(high_risk))
    with col2:
        st.metric("🟡 Medium Risk", len(medium_risk))
    with col3:
        st.metric("🟢 Low Risk", len(low_risk))
    
    # Display interactions by severity
    for interaction in interactions:
        severity = interaction['severity']
        css_class = {
            'HIGH': 'high-risk',
            'MEDIUM': 'medium-risk', 
            'LOW': 'low-risk'
        }.get(severity, 'low-risk')
        
        st.markdown(f"""
        <div class="{css_class}">
            <h4>🚨 {interaction['drug1']} ↔️ {interaction['drug2']} ({severity} Risk)</h4>
            <p><strong>Warning:</strong> {interaction['warning']}</p>
            <p><strong>Recommendation:</strong> {interaction['recommendation']}</p>
        </div>
        """, unsafe_allow_html=True)

def display_dosage_recommendations(dosage_recommendations: List[Dict]):
    """Display age-appropriate dosage recommendations"""
    st.subheader("💊 Age-Appropriate Dosage Recommendations")
    
    if not dosage_recommendations:
        st.info("No specific dosage recommendations generated.")
        return
    
    for rec in dosage_recommendations:
        with st.expander(f"📋 {rec['drug']} - {rec['age_category']} Patient"):
            st.markdown(f"**Recommendation:** {rec['recommendation']}")
            
            if rec.get('warnings'):
                st.markdown("**⚠️ Warnings:**")
                for warning in rec['warnings']:
                    st.markdown(f"• {warning}")
            
            if rec.get('monitoring'):
                st.markdown("**🔍 Monitoring Required:**")
                for monitor in rec['monitoring']:
                    st.markdown(f"• {monitor}")

def display_alternatives(alternatives: Dict[str, Dict]):
    """Display alternative medication suggestions"""
    st.subheader("🔄 Alternative Medication Suggestions")
    
    if not alternatives:
        st.info("No alternative medication suggestions available.")
        return
    
    for drug_name, alt_info in alternatives.items():
        with st.expander(f"🏥 Alternatives for {alt_info['original_drug']}"):
            st.markdown(f"**Drug Class:** {alt_info['drug_class']}")
            st.markdown(f"**Reason:** {alt_info['reason_for_alternatives']}")
            
            if alt_info['alternatives']:
                st.markdown("**Alternative Options:**")
                alt_df = pd.DataFrame(alt_info['alternatives'])
                st.dataframe(alt_df, use_container_width=True)
            
            if alt_info.get('considerations'):
                st.markdown("**⚠️ Switching Considerations:**")
                for consideration in alt_info['considerations']:
                    st.markdown(f"• {consideration}")

def display_ai_insights(ai_insights: Dict[str, Any]):
    """Display AI model insights and metadata"""
    st.subheader("🤖 AI Analysis Insights")
    
    st.markdown(f"""
    <div class="ai-insight">
        <h4>🧠 AI Technology Stack</h4>
        <p><strong>Extraction Method:</strong> {ai_insights.get('extraction_method', 'N/A')}</p>
        <p><strong>Models Used:</strong> {', '.join(set(ai_insights.get('models_used', [])))}</p>
        <p><strong>Prescription Complexity:</strong> {ai_insights.get('prescription_complexity', 'N/A')}</p>
        <p><strong>Total Drugs Identified:</strong> {ai_insights.get('total_drugs_found', 0)}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Confidence scores chart
    confidence_scores = ai_insights.get('confidence_scores', {})
    if confidence_scores:
        fig = go.Figure(data=go.Bar(
            x=list(confidence_scores.keys()),
            y=list(confidence_scores.values()),
            marker_color='lightblue'
        ))
        fig.update_layout(
            title="Drug Detection Confidence by AI Models",
            xaxis_title="Drug Names",
            yaxis_title="Confidence Score",
            yaxis=dict(range=[0, 1])
        )
        st.plotly_chart(fig, use_container_width=True)

def main():
    """Main Streamlit application"""
    
    # Header
    st.markdown('<h1 class="main-header">🧠 AI Medical Prescription Verifier</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">Powered by IBM Granite Models & Advanced NLP for Comprehensive Prescription Analysis</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Backend health check
        is_healthy, health_data = check_backend_health()
        if is_healthy:
            st.success("✅ Backend Connected")
            if health_data:
                st.json(health_data.get('models_loaded', {}))
        else:
            st.error("❌ Backend Disconnected")
            st.warning("Please ensure the FastAPI server is running on port 8000")
        
        st.markdown("---")
        
        # Model information
        st.header("🤖 AI Models")
        st.markdown("""
        **IBM Granite Models:**
        - Granite 3B Code Instruct (Primary)
        - Medical NER Extraction
        - Drug Interaction Analysis
        - Clinical Text Understanding
        
        **Supporting Technologies:**
        - Pattern Matching Algorithms
        - Medical Database Integration
        - Confidence Scoring System
        """)
        
        st.markdown("---")
        
        # Sample prescriptions
        st.header("📝 Sample Prescriptions")
        sample_prescriptions = {
            "Hypertension Treatment": "Lisinopril 10mg once daily, Amlodipine 5mg once daily, Hydrochlorothiazide 25mg once daily",
            "Pain Management": "Ibuprofen 400mg three times daily, Acetaminophen 500mg every 6 hours as needed",
            "Diabetes Care": "Metformin 500mg twice daily, Gliclazide 80mg once daily",
            "Anticoagulation": "Warfarin 5mg once daily, Aspirin 75mg once daily",
            "Complex Polypharmacy": "Lisinopril 10mg daily, Atorvastatin 20mg at bedtime, Metformin 1000mg twice daily"
        }
        
        selected_sample = st.selectbox("Choose a sample:", ["Custom"] + list(sample_prescriptions.keys()))
        
        st.markdown("---")
        
        # Performance settings
        st.header("⚡ Performance")
        timeout_setting = st.slider(
            "Request Timeout (seconds)",
            min_value=30,
            max_value=180,
            value=120,
            help="Increase if model loading takes longer"
        )
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📋 Prescription Input")
        
        # Text input
        if selected_sample != "Custom":
            default_text = sample_prescriptions[selected_sample]
        else:
            default_text = ""
        
        prescription_text = st.text_area(
            "Enter prescription or drug list:",
            value=default_text,
            height=150,
            placeholder="Example: Take Lisinopril 10mg once daily and Metformin 500mg twice daily with meals..."
        )
    
    with col2:
        st.header("👤 Patient Information")
        
        age = st.number_input(
            "Patient Age",
            min_value=0,
            max_value=120,
            value=45,
            help="Age affects dosage recommendations"
        )
        
        weight = st.number_input(
            "Weight (kg) - Optional",
            min_value=0.0,
            max_value=500.0,
            value=70.0,
            help="Weight can affect dosage calculations"
        )
        
        medical_conditions = st.multiselect(
            "Known Medical Conditions",
            ["Hypertension", "Diabetes", "Heart Disease", "Kidney Disease", "Liver Disease", "Asthma"],
            help="Select any known medical conditions"
        )
    
    # Analysis button
    if st.button("🔍 Analyze Prescription", type="primary", use_container_width=True):
        if not prescription_text.strip():
            st.error("Please enter a prescription to analyze.")
            return
        
        if not is_healthy:
            st.error("❌ Cannot analyze - Backend server is not available. Please start the FastAPI server.")
            return
        
        # Show loading message with model info
        loading_placeholder = st.empty()
        loading_placeholder.markdown("""
        <div class="loading-message">
            🤖 <strong>IBM Granite Model is analyzing your prescription...</strong><br>
            This may take 30-120 seconds for the first analysis while the model loads.<br>
            Subsequent analyses will be much faster! ⚡
        </div>
        """, unsafe_allow_html=True)
        
        # Progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Show loading spinner
        with st.spinner("🧠 AI analysis in progress..."):
            try:
                # Update progress
                progress_bar.progress(10)
                status_text.text("Preparing request data...")
                
                # Prepare request data
                request_data = {
                    "text": prescription_text,
                    "age": int(age),
                    "weight": float(weight) if weight > 0 else None,
                    "medical_conditions": medical_conditions if medical_conditions else None
                }
                
                progress_bar.progress(20)
                status_text.text("Sending to IBM Granite model...")
                
                # Make API request with increased timeout
                response = requests.post(
                    "http://localhost:8000/analyze",
                    json=request_data,
                    timeout=timeout_setting
                )
                
                progress_bar.progress(90)
                status_text.text("Processing results...")
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Clear loading indicators
                    loading_placeholder.empty()
                    progress_bar.progress(100)
                    status_text.empty()
                    
                    # Success message with model info
                    model_info = result.get('model_info', {})
                    st.markdown(f"""
                    <div class="success-message">
                        ✅ <strong>Analysis Complete!</strong><br>
                        Processing Time: {result['processing_time_ms']:.0f}ms<br>
                        Model: {model_info.get('model_name', 'IBM Granite')}<br>
                        Timestamp: {result['timestamp']}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Display warnings first
                    if result.get('warnings'):
                        st.error("⚠️ **Important Warnings:**")
                        for warning in result['warnings']:
                            st.markdown(f"• {warning}")
                        st.markdown("---")
                    
                    # Display results in tabs
                    tab1, tab2, tab3, tab4, tab5 = st.tabs([
                        "🔍 Drug Extraction", 
                        "⚠️ Interactions", 
                        "💊 Dosage", 
                        "🔄 Alternatives", 
                        "🤖 AI Insights"
                    ])
                    
                    with tab1:
                        display_drug_extraction_results(result['extracted_drugs'])
                    
                    with tab2:
                        display_interactions(result['interactions'])
                    
                    with tab3:
                        display_dosage_recommendations(result['dosage_recommendations'])
                    
                    with tab4:
                        display_alternatives(result['alternatives'])
                    
                    with tab5:
                        display_ai_insights(result['ai_insights'])
                
                else:
                    # Clear loading indicators
                    loading_placeholder.empty()
                    progress_bar.empty()
                    status_text.empty()
                    
                    error_detail = response.json().get('detail', 'Unknown error') if response.content else f'HTTP {response.status_code}'
                    st.markdown(f"""
                    <div class="error-message">
                        ❌ <strong>Analysis Failed</strong><br>
                        Error: {error_detail}<br>
                        Status Code: {response.status_code}
                    </div>
                    """, unsafe_allow_html=True)
                    
            except requests.exceptions.Timeout:
                # Clear loading indicators
                loading_placeholder.empty()
                progress_bar.empty()
                status_text.empty()
                
                st.markdown("""
                <div class="error-message">
                    ⏰ <strong>Request Timed Out</strong><br>
                    The IBM Granite model is taking longer than expected to respond.<br>
                    This often happens on the first run while the model loads into memory.<br>
                    <br>
                    <strong>Solutions:</strong><br>
                    • Increase timeout in sidebar (try 180 seconds)<br>
                    • Wait for model to fully load, then try again<br>
                    • Check backend logs for model loading progress<br>
                    • Ensure sufficient system memory (8GB+ recommended)
                </div>
                """, unsafe_allow_html=True)
                
            except requests.exceptions.RequestException as e:
                # Clear loading indicators
                loading_placeholder.empty()
                progress_bar.empty()
                status_text.empty()
                
                st.error(f"🔌 Connection error: {str(e)}")
                st.info("Make sure the backend server is running: `cd backend && python main.py`")
                
            except Exception as e:
                # Clear loading indicators
                loading_placeholder.empty()
                progress_bar.empty()
                status_text.empty()
                
                st.error(f"❌ Unexpected error: {str(e)}")

if __name__ == "__main__":
    main()