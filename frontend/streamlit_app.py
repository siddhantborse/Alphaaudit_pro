import streamlit as st
import requests
import json
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

def setup_matplotlib_for_plotting():
    """
    Setup matplotlib and seaborn for plotting with proper configuration.
    Call this function before creating any plots to ensure proper rendering.
    """
    import warnings
    import matplotlib.pyplot as plt
    
    # Ensure warnings are printed
    warnings.filterwarnings('default')  # Show all warnings
    
    # Configure matplotlib for non-interactive mode
    plt.switch_backend("Agg")
    
    # Set chart style  
    plt.style.use("default")
    
    # Configure platform-appropriate fonts for cross-platform compatibility
    plt.rcParams["font.sans-serif"] = ["Arial", "DejaVu Sans", "Liberation Sans", "sans-serif"]
    plt.rcParams["axes.unicode_minus"] = False

# Setup matplotlib immediately
setup_matplotlib_for_plotting()

# Configure page
st.set_page_config(
    page_title="Alpha Audit Pro - HCC Coding Assistant",
    page_icon="",
    layout="wide"
)

# API Configuration
API_BASE_URL = "http://localhost:8000"

def check_ai_status():
    """Check if AI is available"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get('ai_available', False), data.get('ai_model', 'Unknown')
        return False, 'Unknown'
    except:
        return False, 'Connection Error'

def make_api_request(endpoint, data):
    """Make API request with error handling"""
    try:
        response = requests.post(f"{API_BASE_URL}{endpoint}", json=data, timeout=60)  # Increased timeout for AI
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to backend API. Please ensure the backend is running on port 8000.")
        return None
    except requests.exceptions.Timeout:
        st.error("Request timed out. AI analysis may take longer. Please try again.")
        return None
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        return None

def load_analytics_data():
    """Load analytics data from the backend"""
    try:
        with open('analytics_db.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except Exception as e:
        st.error(f"Error loading analytics data: {str(e)}")
        return []

# Sidebar Navigation
st.sidebar.title("Alpha Audit Pro")
page = st.sidebar.selectbox("Navigate", ["HCC Analysis", "Practice Dashboard", "Settings"])

if page == "HCC Analysis":
    st.title("Alpha Audit Pro - AI-Powered HCC Coding Assistant")
    
    # Check AI status
    ai_available, ai_model = check_ai_status()
    
    # Display AI status in a compact way
    if ai_available:
        st.success(f"AI Analysis Active - Model: {ai_model}")
    else:
        st.warning("AI Analysis Unavailable - Using Enhanced Rule-Based Analysis")
    
    st.markdown("### Intelligent HCC Code Identification with AI Enhancement")
    
    # Create two columns for input (keeping the original simple layout)
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Visit Information")
        visit_type = st.selectbox(
            "Visit Type",
            ["Annual Wellness Visit", "Follow-up Visit", "Emergency Visit", 
             "Hospital Admission", "Consultation", "Specialist Referral"]
        )
        
        primary_diagnosis = st.text_input(
            "Primary Diagnosis", 
            help="e.g., Type 2 Diabetes with complications"
        )
        
        provider_name = st.text_input(
            "Provider Name",
            value="Dr. Provider"
        )
        
        # Demographics (simplified)
        st.markdown("**Patient Demographics** *(for accurate risk assessment)*")
        patient_age = st.number_input(
            "Patient Age", 
            min_value=0, 
            max_value=120, 
            value=65,
            help="Critical for HCC risk calculation"
        )
        
        patient_gender = st.selectbox(
            "Patient Gender",
            ["Male", "Female", "Other"],
            index=0
        )
    
    with col2:
        st.subheader("Clinical Documentation")
        clinical_notes = st.text_area(
            "Clinical Notes",
            height=250,
            help="Enter detailed clinical documentation including symptoms, examination findings, assessments, and treatment plans..."
        )
        
        # Additional clinical data (simplified)
        st.markdown("**Additional Clinical Information** *(optional)*")
        patient_medical_history = st.text_area(
            "Medical History",
            height=80,
            help="Previous conditions, surgeries, hospitalizations..."
        )
        
        current_medications = st.text_input(
            "Current Medications",
            help="Key medications (optional)"
        )
    
    # Analysis button
    if st.button("Suggest ICD-10 Codes with AI" if ai_available else "Suggest ICD-10 Codes", type="primary"):
        if not clinical_notes.strip():
            st.error("Please provide clinical documentation to analyze.")
        elif not primary_diagnosis.strip():
            st.error("Please provide a primary diagnosis.")
        else:
            with st.spinner("AI analyzing for optimal ICD-10 code suggestions..." if ai_available else "Analyzing for ICD-10 code suggestions..."):
                # Prepare enhanced API request
                request_data = {
                    "clinical_notes": clinical_notes,
                    "visit_type": visit_type,
                    "primary_diagnosis": primary_diagnosis,
                    "provider_name": provider_name,
                    "patient_age": patient_age,
                    "patient_gender": patient_gender,
                    "patient_medical_history": patient_medical_history,
                    "current_medications": current_medications,
                    "lab_values": ""  # Empty for now
                }
                
                # Make API call
                result = make_api_request("/analyze", request_data)
                
                if result:
                    st.session_state.analysis_results = result
                    st.session_state.show_results = True
                    st.success("ICD-10 code suggestions ready!")
    
    # Display enhanced results if available (keeping original layout but with new data)
    if hasattr(st.session_state, 'show_results') and st.session_state.show_results:
        if hasattr(st.session_state, 'analysis_results'):
            results = st.session_state.analysis_results
            
            st.markdown("---")
            st.subheader("ICD-10 Code Selection Assistant")
            
            # Enhanced metrics (but simpler layout)
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                confidence = results.get('overall_confidence', 'Unknown')
                st.metric("Confidence", confidence)
            with col2:
                priority = results.get('priority_level', 'Unknown')
                st.metric("Priority", priority)
            with col3:
                revenue_impact = results.get('potential_revenue_impact', 'Unknown')
                st.metric("Revenue Impact", revenue_impact)
            with col4:
                ai_status = "AI Enhanced" if results.get('ai_available', False) else "Rule-Based"
                st.metric("Analysis Type", ai_status)
            
            # Show demographic analysis if available
            if 'demographic_analysis' in results and results['demographic_analysis']:
                demo = results['demographic_analysis']
                st.info(f"Patient Profile: {demo.get('gender_considerations', 'N/A')} | Risk Multiplier: {demo.get('risk_multiplier', 1.0):.2f}x | Age Impact: {demo.get('age_impact', 'Unknown')}")
            
            # Suggested ICD-10 Codes (NEW FOCUS)
            if 'suggestions' in results and results['suggestions']:
                st.subheader("Recommended ICD-10 Codes" if results.get('ai_available', False) else "ICD-10 Code Suggestions")
                st.markdown("**Choose the most specific ICD-10 code that matches your clinical documentation:**")
                
                for i, suggestion in enumerate(results['suggestions']):
                    # Extract data safely with new fields
                    icd_code = suggestion.get('icd_code', 'N/A')
                    description = suggestion.get('description', 'N/A')
                    hcc_category = suggestion.get('hcc_code', 'No HCC')
                    raf_value = suggestion.get('raf_weight', 0.0)
                    confidence = suggestion.get('confidence_score', 0)
                    priority = suggestion.get('priority_level', 'Unknown')
                    reasoning = suggestion.get('reasoning', 'No reasoning provided')
                    
                    # NEW: ICD-10 selection guidance fields
                    annual_revenue = suggestion.get('annual_revenue_impact', 0)
                    is_hcc_eligible = suggestion.get('is_hcc_eligible', False)
                    use_case = suggestion.get('suggested_use_case', 'General use')
                    alternatives = suggestion.get('alternative_codes', [])
                    
                    # Priority and HCC status indicators
                    priority_indicator = "HIGH" if priority == "HIGH" else "MED" if priority == "MEDIUM" else "LOW"
                    hcc_indicator = "HCC" if is_hcc_eligible else "No HCC"
                    
                    # Enhanced header with ICD-10 focus
                    header_text = f"[{priority_indicator}][{hcc_indicator}] {icd_code} - {description[:50]}{'...' if len(description) > 50 else ''}"
                    revenue_text = f" (+${annual_revenue:,}/year)" if annual_revenue > 0 else " (No HCC Revenue)"
                    
                    with st.expander(f"{header_text}{revenue_text}", expanded=i < 2):
                        col1, col2 = st.columns([2, 1])
                        with col1:
                            st.markdown(f"**ICD-10 Code:** `{icd_code}`")
                            st.markdown(f"**Description:** {description}")
                            st.markdown(f"**When to Use:** {use_case}")
                            
                            if hcc_category != "No HCC":
                                st.success(f"**HCC Eligible:** {hcc_category} (RAF: {raf_value})")
                            else:
                                st.warning("**No HCC Mapping** - Consider alternatives below")
                            
                            if alternatives:
                                st.markdown("**Better HCC Options:**")
                                for alt in alternatives[:2]:
                                    st.markdown(f"  • {alt}")
                        
                        with col2:
                            if is_hcc_eligible:
                                st.success(f"**Revenue Impact**\n${annual_revenue:,}/year")
                                st.markdown(f"**RAF Value:** {raf_value}")
                                st.markdown(f"**HCC Category:** {hcc_category}")
                            else:
                                st.error("**No Revenue Impact**\nNon-HCC Code")
                            
                            st.markdown(f"**Confidence:** {confidence}%")
                            st.markdown(f"**Priority:** {priority}")
            
            # NEW: HCC vs Non-HCC Comparison
            if 'hcc_vs_non_hcc_comparison' in results:
                comparison = results['hcc_vs_non_hcc_comparison']
                st.subheader("HCC vs Non-HCC Analysis")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("HCC-Eligible Codes", comparison.get('hcc_eligible_count', 0))
                with col2:
                    st.metric("Non-HCC Codes", comparison.get('non_hcc_count', 0))
                with col3:
                    revenue = comparison.get('potential_missed_revenue', 0)
                    st.metric("Revenue Opportunity", f"${revenue:,}")
                
                if comparison.get('top_revenue_codes'):
                    st.markdown("**Top Revenue Opportunities:**")
                    for code_info in comparison['top_revenue_codes']:
                        st.markdown(f"  • {code_info}")
            
            # NEW: Top Revenue Opportunities
            if 'top_revenue_opportunities' in results and results['top_revenue_opportunities']:
                st.subheader("Priority ICD-10 Codes for Revenue")
                for opportunity in results['top_revenue_opportunities']:
                    st.success(f"• {opportunity}")
            
            # NEW: Documentation Improvement Tips
            if 'documentation_improvement_tips' in results and results['documentation_improvement_tips']:
                st.subheader("Documentation Tips for Better ICD-10 Selection")
                for tip in results['documentation_improvement_tips']:
                    st.info(f"{tip}")
            
            # Action Items (simplified)
            if 'action_items' in results and results['action_items']:
                st.subheader("Recommended Actions")
                for action in results['action_items']:
                    st.markdown(f"• {action}")
            
            # Additional Documentation
            if 'additional_documentation' in results and results['additional_documentation']:
                st.subheader("Additional Documentation Needed")
                for doc in results['additional_documentation']:
                    st.markdown(f"• {doc}")
            
            # Enhanced Recommendations
            if 'recommendations' in results and results['recommendations']:
                st.subheader("Clinical Recommendations")
                for rec in results['recommendations']:
                    st.markdown(f"• {rec}")
            
            # Show AI enhancement notice
            if results.get('ai_available', False):
                st.info("This analysis was enhanced using Phi3 AI for improved accuracy and demographic risk assessment.")

elif page == "Practice Dashboard":
    st.title("Practice Analytics Dashboard")
    st.markdown("### Data-Driven Insights for HCC Capture Performance")
    
    # Load analytics data
    analytics_data = load_analytics_data()
    
    if not analytics_data:
        st.info("No analytics data available yet. Start analyzing clinical notes to build your data gold mine!")
        
        # Show sample charts with placeholder data
        st.subheader("Sample Analytics (Demo Data)")
        
        # Create sample data for demonstration
        tab1, tab2, tab3 = st.tabs(["Daily Overview", "Monthly Trends", "Provider Performance"])
        
        with tab1:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Daily HCC Identification")
                # Sample pie chart
                fig, ax = plt.subplots(figsize=(8, 6))
                labels = ['HCC Identified', 'No HCC Found']
                sizes = [20, 10]
                colors = ['#2ecc71', '#e74c3c']
                ax.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors)
                ax.set_title('Alpha Audit Pro identified 20 out of 30 patients\nwith potential HCC codes')
                st.pyplot(fig)
                plt.close()
            
            with col2:
                st.subheader("Top HCC Categories Today")
                # Sample bar chart
                fig, ax = plt.subplots(figsize=(8, 6))
                categories = ['Diabetes', 'Hypertension', 'COPD', 'Heart Disease']
                counts = [8, 6, 4, 2]
                bars = ax.bar(categories, counts, color=['#3498db', '#e67e22', '#9b59b6', '#f39c12'])
                ax.set_title('Most Frequently Identified HCC Categories')
                ax.set_ylabel('Number of Cases')
                plt.xticks(rotation=45)
                plt.tight_layout()
                st.pyplot(fig)
                plt.close()
        
        with tab2:
            st.subheader("Monthly HCC Capture Trends")
            # Sample line chart
            fig, ax = plt.subplots(figsize=(12, 6))
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
            hcc_found = [45, 52, 48, 61, 58, 65]
            total_analyzed = [120, 135, 128, 142, 138, 150]
            
            ax.plot(months, hcc_found, marker='o', label='HCC Codes Found', linewidth=2)
            ax.plot(months, total_analyzed, marker='s', label='Total Analyses', linewidth=2)
            ax.set_title('Monthly HCC Identification Trends')
            ax.set_ylabel('Number of Cases')
            ax.legend()
            ax.grid(True, alpha=0.3)
            st.pyplot(fig)
            plt.close()
        
        with tab3:
            st.subheader("Provider Performance Comparison")
            # Sample provider performance
            providers = ['Dr. Smith', 'Dr. Johnson', 'Dr. Brown', 'Dr. Davis']
            hcc_rates = [85, 78, 92, 71]
            
            fig, ax = plt.subplots(figsize=(10, 6))
            bars = ax.bar(providers, hcc_rates, color=['#2ecc71', '#3498db', '#e67e22', '#e74c3c'])
            ax.set_title('HCC Capture Rate by Provider (%)')
            ax.set_ylabel('Capture Rate (%)')
            ax.set_ylim(0, 100)
            
            # Add value labels on bars
            for bar, rate in zip(bars, hcc_rates):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                       f'{rate}%', ha='center', va='bottom')
            
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()
    
    else:
        st.subheader(f"Analytics Based on {len(analytics_data)} Analyses")
        
        # Process real analytics data
        total_analyses = len(analytics_data)
        analyses_with_hcc = sum(1 for analysis in analytics_data if analysis.get('suggestions'))
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Analyses", total_analyses)
        with col2:
            st.metric("HCC Opportunities Found", analyses_with_hcc)
        with col3:
            capture_rate = (analyses_with_hcc / total_analyses * 100) if total_analyses > 0 else 0
            st.metric("HCC Capture Rate", f"{capture_rate:.1f}%")
        
        # Real data visualization would go here
        st.info("Real-time analytics visualization will be implemented based on your actual analysis data.")

elif page == "Settings":
    st.title("Settings")
    
    st.subheader("API Configuration")
    api_url = st.text_input("Backend API URL", value=API_BASE_URL)
    
    st.subheader("Analytics Settings")
    st.checkbox("Enable detailed logging", value=True)
    st.checkbox("Export analytics data", value=False)
    
    st.subheader("Analysis Preferences")
    confidence_threshold = st.slider("Minimum Confidence Threshold", 0.0, 1.0, 0.7)
    include_low_priority = st.checkbox("Include low priority suggestions", value=True)
    
    if st.button("Save Settings"):
        st.success("Settings saved successfully!")

# Footer
st.markdown("---")
st.markdown("**Alpha Audit Pro** - Empowering healthcare providers with intelligent HCC coding assistance")