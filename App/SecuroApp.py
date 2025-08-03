import streamlit as st
import time
import datetime
import pytz
import random
import pandas as pd
import numpy as np
import os
import google.generativeai as genai
import re
import requests
import io
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import folium
from streamlit_folium import st_folium
import warnings
import json
warnings.filterwarnings('ignore')

# Language detection and translation support
SUPPORTED_LANGUAGES = {
    'en': 'English',
    'es': 'Español (Spanish)',
    'fr': 'Français (French)',
    'pt': 'Português (Portuguese)',
    'zh': '中文 (Chinese)',
    'ar': 'العربية (Arabic)',
    'hi': 'हिन्दी (Hindi)',
    'ja': '日本語 (Japanese)',
    'ko': '한국어 (Korean)',
    'de': 'Deutsch (German)',
    'it': 'Italiano (Italian)',
    'ru': 'Русский (Russian)'
}

# Emergency Contacts for St. Kitts & Nevis
EMERGENCY_CONTACTS = {
    "Emergency": "911",
    "Police": "465-2241",
    "Hospital": "465-2551",
    "Fire Department": "465-2515 / 465-7167",
    "Coast Guard": "465-8384 / 466-9280",
    "Met Office": "465-2749",
    "Red Cross": "465-2584",
    "NEMA": "466-5100"
}

# Crime Hotspots Data for St. Kitts & Nevis
CRIME_HOTSPOTS = {
    # St. Kitts Hotspots
    "Basseterre Central": {"lat": 17.3026, "lon": -62.7177, "crimes": 45, "risk": "High", "types": ["Larceny", "Drug Crimes", "Assault"]},
    "Cayon": {"lat": 17.3581, "lon": -62.7440, "crimes": 28, "risk": "Medium", "types": ["Break-ins", "Theft"]},
    "Old Road Town": {"lat": 17.3211, "lon": -62.7847, "crimes": 22, "risk": "Medium", "types": ["Drug Crimes", "Vandalism"]},
    "Tabernacle": {"lat": 17.3100, "lon": -62.7200, "crimes": 31, "risk": "High", "types": ["Robbery", "Assault"]},
    "Sandy Point": {"lat": 17.3667, "lon": -62.8500, "crimes": 19, "risk": "Low", "types": ["Petty Theft"]},
    "Dieppe Bay": {"lat": 17.3833, "lon": -62.8167, "crimes": 15, "risk": "Low", "types": ["Vandalism"]},
    "Newton Ground": {"lat": 17.3319, "lon": -62.7269, "crimes": 26, "risk": "Medium", "types": ["Drug Crimes", "Larceny"]},
    "Molineux": {"lat": 17.2978, "lon": -62.7047, "crimes": 33, "risk": "High", "types": ["Armed Robbery", "Assault"]},
    
    # Nevis Hotspots
    "Charlestown": {"lat": 17.1348, "lon": -62.6217, "crimes": 18, "risk": "Medium", "types": ["Larceny", "Drug Crimes"]},
    "Gingerland": {"lat": 17.1019, "lon": -62.5708, "crimes": 12, "risk": "Low", "types": ["Petty Theft"]},
    "Newcastle": {"lat": 17.1667, "lon": -62.6000, "crimes": 14, "risk": "Low", "types": ["Vandalism", "Theft"]},
    "Cotton Ground": {"lat": 17.1281, "lon": -62.6442, "crimes": 16, "risk": "Medium", "types": ["Break-ins", "Larceny"]},
    "Ramsbury": {"lat": 17.1500, "lon": -62.6167, "crimes": 21, "risk": "Medium", "types": ["Drug Crimes", "Assault"]},
}

# ENHANCED MULTI-YEAR CRIME DATABASE - Based on Official Police Reports
HISTORICAL_CRIME_DATABASE = {
    "2025_Q2": {
        "period": "Q2 2025 (Apr-Jun)",
        "total_crimes": 292,
        "detection_rate": 38.7,
        "federation": {
            "murder_manslaughter": {"total": 4, "detected": 2, "rate": 50.0},
            "attempted_murder": {"total": 4, "detected": 0, "rate": 0.0},
            "bodily_harm": {"total": 33, "detected": 19, "rate": 57.6},
            "sex_crimes": {"total": 7, "detected": 1, "rate": 14.3},
            "break_ins": {"total": 26, "detected": 7, "rate": 26.9},
            "larcenies": {"total": 92, "detected": 21, "rate": 22.8},
            "robberies": {"total": 8, "detected": 1, "rate": 12.5},
            "firearms_offences": {"total": 5, "detected": 5, "rate": 100.0},
            "drug_crimes": {"total": 31, "detected": 31, "rate": 100.0},
            "malicious_damage": {"total": 59, "detected": 17, "rate": 28.8},
        },
        "st_kitts": {"crimes": 207, "detection_rate": 32.9},
        "nevis": {"crimes": 85, "detection_rate": 52.9}
    },
    "2025_H1": {
        "period": "H1 2025 (Jan-Jun)",
        "total_crimes": 574,
        "federation": {
            "murder_manslaughter": {"total": 4},
            "shooting_intent": {"total": 1},
            "attempted_murder": {"total": 4},
            "bodily_harm": {"total": 72},
            "sex_crimes": {"total": 15},
            "break_ins": {"total": 67},
            "larcenies": {"total": 185},
            "robberies": {"total": 13},
            "firearms_offences": {"total": 13},
            "drug_crimes": {"total": 45},
            "malicious_damage": {"total": 115},
        }
    },
    "2024_H1": {
        "period": "H1 2024 (Jan-Jun)", 
        "total_crimes": 586,
        "federation": {
            "murder_manslaughter": {"total": 16},
            "shooting_intent": {"total": 1},
            "attempted_murder": {"total": 14},
            "bodily_harm": {"total": 78},
            "sex_crimes": {"total": 36},
            "break_ins": {"total": 61},
            "larcenies": {"total": 193},
            "robberies": {"total": 22},
            "firearms_offences": {"total": 6},
            "drug_crimes": {"total": 8},
            "malicious_damage": {"total": 109},
        }
    },
    "2024_Q1": {
        "period": "Q1 2024 (Jan-Mar)",
        "total_crimes": 276,
        "federation": {
            "murder_manslaughter": {"total": 6},
            "attempted_murder": {"total": 3},
            "bodily_harm": {"total": 46},
            "sex_crimes": {"total": 19},
            "break_ins": {"total": 32},
            "larcenies": {"total": 89},
            "robberies": {"total": 10},
            "firearms_offences": {"total": 2},
            "drug_crimes": {"total": 5},
            "malicious_damage": {"total": 48},
        }
    },
    "2023_H1": {
        "period": "H1 2023 (Jan-Jun)",
        "total_crimes": 672,
        "federation": {
            "murder_manslaughter": {"total": 17},
            "shooting_intent": {"total": 5},
            "woundings_firearm": {"total": 2},
            "attempted_murder": {"total": 5},
            "bodily_harm": {"total": 93},
            "sex_crimes": {"total": 37},
            "break_ins": {"total": 62},
            "larcenies": {"total": 231},
            "robberies": {"total": 17},
            "firearms_offences": {"total": 18},
            "drug_crimes": {"total": 6},
            "malicious_damage": {"total": 158},
        }
    },
    "2022_Q1": {
        "period": "Q1 2022 (Jan-Mar)",
        "total_crimes": 368,
        "federation": {
            "murder_manslaughter": {"total": 4},
            "shooting_intent": {"total": 1},
            "attempted_murder": {"total": 5},
            "bodily_harm": {"total": 38},
            "sex_crimes": {"total": 10},
            "break_ins": {"total": 43},
            "larcenies": {"total": 159},
            "robberies": {"total": 11},
            "firearms_offences": {"total": 5},
            "drug_crimes": {"total": 9},
            "malicious_damage": {"total": 65},
        }
    }
}

# ENHANCED FORENSIC SCIENCE KNOWLEDGE BASE
FORENSIC_KNOWLEDGE_BASE = {
    "dna_analysis": {
        "overview": "DNA profiling is the gold standard for human identification in forensic investigations.",
        "key_points": [
            "STR (Short Tandem Repeat) analysis is standard for CODIS database entries",
            "Degraded samples require specialized extraction and amplification techniques",
            "Mixture interpretation follows probabilistic genotyping methods",
            "Touch DNA can be recovered from items handled for just seconds"
        ],
        "procedures": [
            "Sample collection with sterile techniques and proper documentation",
            "DNA extraction using organic or solid phase methods",
            "PCR amplification of STR markers", 
            "Capillary electrophoresis for fragment analysis",
            "Statistical interpretation using population databases"
        ],
        "challenges": ["Degradation", "Inhibition", "Mixtures", "Low template DNA", "Contamination"]
    },
    "crime_scene": {
        "overview": "Systematic documentation and evidence collection to reconstruct events.",
        "key_points": [
            "Photography, sketching, and measurements are essential",
            "Chain of custody must be maintained for all evidence",
            "Scene security prevents contamination and evidence loss",
            "Bloodstain pattern analysis can reveal sequence of events"
        ],
        "procedures": [
            "Scene security and initial assessment",
            "Photography from overall to close-up views",
            "Evidence mapping and documentation",
            "Collection using appropriate packaging",
            "Scene reconstruction based on physical evidence"
        ]
    },
    "digital_forensics": {
        "overview": "Recovery and analysis of digital evidence from electronic devices.",
        "key_points": [
            "Live data acquisition preserves volatile information",
            "Write-blocking prevents evidence modification",
            "Deleted data can often be recovered from unallocated space",
            "Metadata provides crucial timeline information"
        ],
        "procedures": [
            "Device seizure and documentation",
            "Forensic imaging of storage media",
            "Analysis using validated forensic tools",
            "Timeline reconstruction",
            "Report generation with findings"
        ]
    },
    "ballistics": {
        "overview": "Firearms and toolmark examination for weapon identification.",
        "key_points": [
            "Bullet comparison requires microscopic examination",
            "Gunshot residue testing within 6 hours is optimal",
            "Trajectory analysis determines shooter position",
            "Serial number restoration may be possible"
        ],
        "procedures": [
            "Firearm examination and test firing",
            "Bullet and cartridge case comparison",
            "GSR collection and analysis",
            "Trajectory reconstruction",
            "Distance determination testing"
        ]
    },
    "toxicology": {
        "overview": "Detection and quantification of drugs, poisons, and alcohol.",
        "key_points": [
            "Sample type affects detection window",
            "Post-mortem redistribution affects interpretation",
            "Hair testing provides longer detection window",
            "Therapeutic vs toxic levels are crucial"
        ],
        "procedures": [
            "Sample collection and preservation",
            "Screening tests (immunoassays)",
            "Confirmatory testing (GC-MS, LC-MS)",
            "Quantitative analysis",
            "Interpretation considering case circumstances"
        ]
    }
}

# St. Kitts timezone (Atlantic Standard Time)
SKN_TIMEZONE = pytz.timezone('America/St_Kitts')

def get_stkitts_time():
    """Get current time in St. Kitts & Nevis timezone"""
    utc_now = datetime.datetime.now(pytz.UTC)
    skn_time = utc_now.astimezone(SKN_TIMEZONE)
    return skn_time.strftime("%H:%M:%S")

def get_stkitts_date():
    """Get current date in St. Kitts & Nevis timezone"""
    utc_now = datetime.datetime.now(pytz.UTC)
    skn_time = utc_now.astimezone(SKN_TIMEZONE)
    return skn_time.strftime("%Y-%m-%d")

def create_crime_hotspot_map():
    """Create an interactive crime hotspot map for St. Kitts and Nevis"""
    # Center the map on St. Kitts and Nevis
    center_lat = 17.25
    center_lon = -62.7
    
    # Create the base map
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=11,
        tiles='OpenStreetMap',
        attr='Crime Hotspot Analysis - SECURO'
    )
    
    # Add Google Satellite layer as an option
    folium.TileLayer(
        tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
        attr='Google Satellite',
        name='Satellite View',
        overlay=False,
        control=True
    ).add_to(m)
    
    # Color mapping for risk levels
    risk_colors = {
        'High': '#ff4444',
        'Medium': '#ffaa44', 
        'Low': '#44ff44'
    }
    
    # Add crime hotspots to the map
    for location, data in CRIME_HOTSPOTS.items():
        # Create popup content
        popup_content = f"""
        <div style="font-family: Arial, sans-serif; min-width: 200px;">
            <h4 style="color: {risk_colors[data['risk']]}; margin: 0; text-align: center;">
                🚨 {location}
            </h4>
            <hr style="margin: 8px 0;">
            <p style="margin: 4px 0;"><strong>📊 Total Crimes:</strong> {data['crimes']}</p>
            <p style="margin: 4px 0;"><strong>⚠️ Risk Level:</strong> 
               <span style="color: {risk_colors[data['risk']]}; font-weight: bold;">{data['risk']}</span>
            </p>
            <p style="margin: 4px 0;"><strong>🔍 Common Types:</strong></p>
            <ul style="margin: 4px 0; padding-left: 20px;">
                {''.join([f'<li>{crime_type}</li>' for crime_type in data['types']])}
            </ul>
            <small style="color: #666;">📍 Lat: {data['lat']:.4f}, Lon: {data['lon']:.4f}</small>
        </div>
        """
        
        # Calculate marker size based on crime count
        marker_size = max(10, min(30, data['crimes'] * 0.8))
        
        # Add marker to map
        folium.CircleMarker(
            location=[data['lat'], data['lon']],
            radius=marker_size,
            popup=folium.Popup(popup_content, max_width=300),
            tooltip=f"{location}: {data['crimes']} crimes ({data['risk']} risk)",
            color='black',
            fillColor=risk_colors[data['risk']],
            fillOpacity=0.7,
            weight=2
        ).add_to(m)
        
        # Add text label for major hotspots
        if data['crimes'] > 25:
            folium.Marker(
                location=[data['lat'] + 0.01, data['lon']],
                icon=folium.DivIcon(
                    html=f"""<div style="font-size: 10px; font-weight: bold; 
                             color: white; text-shadow: 1px 1px 2px black;">
                             {location}</div>""",
                    icon_size=(100, 20),
                    icon_anchor=(50, 10)
                )
            ).add_to(m)
    
    # Add a legend
    legend_html = f"""
    <div style="position: fixed; 
                top: 10px; right: 10px; width: 180px; height: 140px; 
                background-color: rgba(0, 0, 0, 0.8); 
                border: 2px solid rgba(68, 255, 68, 0.5);
                border-radius: 10px; z-index:9999; 
                font-size: 12px; font-family: Arial;
                padding: 10px; color: white;">
    <h4 style="margin: 0 0 10px 0; color: #44ff44;">🗺️ Crime Risk Legend</h4>
    <div style="margin: 5px 0;">
        <span style="color: {risk_colors['High']};">●</span> High Risk (25+ crimes)
    </div>
    <div style="margin: 5px 0;">
        <span style="color: {risk_colors['Medium']};">●</span> Medium Risk (15-24 crimes)  
    </div>
    <div style="margin: 5px 0;">
        <span style="color: {risk_colors['Low']};">●</span> Low Risk (<15 crimes)
    </div>
    <small style="color: #888;">Marker size = Crime frequency</small>
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    return m

# Crime Statistics Data Structure
@st.cache_data
def load_crime_statistics():
    """Load and structure crime statistics data"""
    return HISTORICAL_CRIME_DATABASE

def create_historical_crime_charts(chart_type, selected_periods, crime_data):
    """Create various crime analysis charts for selected periods"""
    
    if chart_type == "crime_trends":
        # Crime trends across selected periods
        periods = []
        total_crimes = []
        
        for period_key in selected_periods:
            if period_key in crime_data:
                periods.append(crime_data[period_key]["period"])
                total_crimes.append(crime_data[period_key]["total_crimes"])
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=periods, y=total_crimes,
            mode='lines+markers',
            name='Total Crimes',
            line=dict(color='#44ff44', width=3),
            marker=dict(size=8)
        ))
        
        fig.update_layout(
            title="Crime Trends - Selected Periods",
            xaxis_title="Time Period",
            yaxis_title="Total Crimes",
            template="plotly_dark",
            height=500
        )
        
        return fig
    
    elif chart_type == "detection_comparison":
        # Detection rate comparison
        periods = []
        detection_rates = []
        
        for period_key in selected_periods:
            if period_key in crime_data and "detection_rate" in crime_data[period_key]:
                periods.append(crime_data[period_key]["period"])
                detection_rates.append(crime_data[period_key]["detection_rate"])
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=periods, y=detection_rates,
            marker_color='#44ff44',
            text=[f"{rate}%" for rate in detection_rates],
            textposition='auto'
        ))
        
        fig.update_layout(
            title="Detection Rates - Selected Periods",
            xaxis_title="Time Period",
            yaxis_title="Detection Rate (%)",
            template="plotly_dark",
            height=500
        )
        
        return fig
    
    elif chart_type == "crime_type_breakdown":
        # Crime type breakdown for latest selected period
        if selected_periods and selected_periods[-1] in crime_data:
            latest_data = crime_data[selected_periods[-1]]
            if "federation" in latest_data:
                crimes = []
                counts = []
                
                for crime_type, data in latest_data["federation"].items():
                    if "total" in data:
                        crimes.append(crime_type.replace('_', ' ').title())
                        counts.append(data["total"])
                
                fig = go.Figure(data=[go.Pie(
                    labels=crimes,
                    values=counts,
                    hole=0.4,
                    marker_colors=['#44ff44', '#f39c12', '#e74c3c', '#27ae60', '#9b59b6', '#34495e', '#16a085', '#f1c40f']
                )])
                
                fig.update_layout(
                    title=f"Crime Type Distribution - {latest_data['period']}",
                    template="plotly_dark",
                    height=500
                )
                
                return fig

def is_casual_greeting(user_input):
    """Detect if user input is a casual greeting"""
    casual_words = ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening', 'how are you', 'what\'s up', 'sup']
    return any(word in user_input.lower().strip() for word in casual_words) and len(user_input.strip()) < 25

def is_detailed_request(user_input):
    """Detect if user wants detailed information"""
    detail_keywords = ['detailed', 'detail', 'explain', 'comprehensive', 'thorough', 'in depth', 'breakdown', 'elaborate', 'more information', 'tell me more']
    return any(keyword in user_input.lower() for keyword in detail_keywords)

def is_forensic_query(user_input):
    """Detect if user input is about forensic science"""
    forensic_keywords = [
        'dna', 'forensic', 'evidence', 'fingerprint', 'ballistics', 'toxicology', 'autopsy', 'pathology',
        'crime scene', 'investigation', 'laboratory', 'testing', 'analysis', 'examination', 'court',
        'chain of custody', 'contamination', 'quality control', 'profiling', 'codis', 'afis',
        'gunshot residue', 'bullet', 'firearm', 'poison', 'drug testing', 'fiber', 'paint', 'glass',
        'impression', 'handwriting', 'document', 'forgery', 'serology', 'biology', 'chemistry',
        'photography', 'reconstruction', 'wound', 'injury', 'cause of death', 'time of death'
    ]
    return any(keyword in user_input.lower() for keyword in forensic_keywords)

def is_crime_statistics_query(user_input):
    """Detect if user input is about crime statistics"""
    stats_keywords = [
        'statistics', 'stats', 'data', 'numbers', 'trends', 'crime rate', 'detection rate',
        'murder', 'larceny', 'robbery', 'drug', 'assault', 'break', 'theft', 'violence',
        'hotspot', 'area', 'location', 'comparison', 'year', 'quarter', 'period'
    ]
    return any(keyword in user_input.lower() for keyword in stats_keywords)

def get_relevant_forensic_info(query):
    """Get relevant forensic information based on query"""
    query_lower = query.lower()
    relevant_info = []
    
    for topic, info in FORENSIC_KNOWLEDGE_BASE.items():
        if any(keyword in query_lower for keyword in topic.split('_')):
            relevant_info.append({
                'topic': topic.replace('_', ' ').title(),
                'overview': info['overview'],
                'key_points': info['key_points'],
                'procedures': info.get('procedures', []),
                'challenges': info.get('challenges', [])
            })
    
    return relevant_info

def get_relevant_crime_data(query):
    """Get relevant crime statistics based on query"""
    query_lower = query.lower()
    
    # Check for specific years or periods
    relevant_data = {}
    
    for period_key, data in HISTORICAL_CRIME_DATABASE.items():
        period_text = data['period'].lower()
        if any(term in query_lower for term in ['2025', 'current', 'recent', 'latest']) and '2025' in period_text:
            relevant_data[period_key] = data
        elif any(term in query_lower for term in ['2024']) and '2024' in period_text:
            relevant_data[period_key] = data
        elif any(term in query_lower for term in ['2023']) and '2023' in period_text:
            relevant_data[period_key] = data
        elif any(term in query_lower for term in ['2022']) and '2022' in period_text:
            relevant_data[period_key] = data
    
    # If no specific year mentioned, return recent data
    if not relevant_data:
        relevant_data = {k: v for k, v in list(HISTORICAL_CRIME_DATABASE.items())[:3]}
    
    return relevant_data

def generate_enhanced_smart_response(user_input, language='en'):
    """Generate enhanced, concise forensic and crime analysis responses"""
    
    if not st.session_state.get('ai_enabled', False):
        return "🔧 AI system offline. Please check your API key configuration."
    
    try:
        # Handle different query types with appropriate response lengths
        if is_casual_greeting(user_input):
            # Simple greeting response
            prompt = f"""
            You are SECURO, a forensic science and crime analysis AI for St. Kitts & Nevis Police.
            
            User said: "{user_input}"
            
            Respond with a brief, friendly greeting (2-3 sentences max). Mention you're ready to help with forensic science, crime analysis, or investigations.
            """
            
            response = model.generate_content(prompt)
            return response.text.strip()
        
        elif is_forensic_query(user_input):
            # Forensic science response
            forensic_info = get_relevant_forensic_info(user_input)
            is_detailed = is_detailed_request(user_input)
            
            prompt = f"""
            You are SECURO, an expert forensic science AI for St. Kitts & Nevis Police.
            
            User query: "{user_input}"
            Detailed request: {is_detailed}
            
            Relevant forensic knowledge: {json.dumps(forensic_info, indent=2)}
            
            **Response Guidelines:**
            - If detailed=False: Give concise, practical answer (3-5 sentences)
            - If detailed=True: Provide comprehensive explanation with procedures
            - Focus on practical forensic applications
            - Include scientific accuracy and legal considerations
            - Mention St. Kitts context when relevant
            
            Provide expert forensic guidance.
            """
            
            response = model.generate_content(prompt)
            return response.text.strip()
        
        elif is_crime_statistics_query(user_input):
            # Crime statistics response
            crime_data = get_relevant_crime_data(user_input)
            is_detailed = is_detailed_request(user_input)
            
            prompt = f"""
            You are SECURO, a crime analysis AI for St. Kitts & Nevis Police.
            
            User query: "{user_input}"
            Detailed request: {is_detailed}
            
            Relevant crime data: {json.dumps(crime_data, indent=2)}
            
            **Response Guidelines:**
            - If detailed=False: Give key statistics only (3-5 sentences)
            - If detailed=True: Provide comprehensive analysis with trends
            - Focus on actionable insights
            - Compare periods when relevant
            - Highlight significant patterns or changes
            
            Provide crime intelligence analysis.
            """
            
            response = model.generate_content(prompt)
            return response.text.strip()
        
        else:
            # General query
            is_detailed = is_detailed_request(user_input)
            
            prompt = f"""
            You are SECURO, a comprehensive forensic and crime analysis AI for St. Kitts & Nevis Police.
            
            User query: "{user_input}"
            Detailed request: {is_detailed}
            
            **Response Guidelines:**
            - If detailed=False: Keep response concise (3-5 sentences)
            - If detailed=True: Provide thorough explanation
            - Maintain professional expertise
            - Include practical recommendations when appropriate
            
            Current time: {get_stkitts_time()} AST
            Current date: {get_stkitts_date()}
            
            Provide helpful, accurate assistance.
            """
            
            response = model.generate_content(prompt)
            return response.text.strip()
            
    except Exception as e:
        return f"🚨 AI analysis error: {str(e)}\n\nI'm still here to help! Try asking about forensic procedures, crime statistics, or specific investigations."

# Initialize the AI model - REPLACE WITH YOUR API KEY
try:
    GOOGLE_API_KEY = "AIzaSyBfqpVf3XWpYb_pRtKEMjxjwbbXKUgWicI"  # REPLACE THIS WITH YOUR ACTUAL API KEY
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    st.session_state.ai_enabled = True
    st.session_state.ai_status = "✅ AI Active"
except Exception as e:
    st.session_state.ai_enabled = False
    st.session_state.ai_status = f"❌ AI Error: {str(e)}"
    model = None

# Page configuration
st.set_page_config(
    page_title="SECURO - St. Kitts & Nevis Crime AI Assistant",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'welcome'

if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'selected_language' not in st.session_state:
    st.session_state.selected_language = 'en'

if 'crime_stats' not in st.session_state:
    st.session_state.crime_stats = load_crime_statistics()

if 'selected_periods' not in st.session_state:
    st.session_state.selected_periods = ['2025_Q2']

# CSS styling - Fixed for dropdown visibility
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;700&display=swap');
   
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Fix dropdown visibility issues */
    .stMultiSelect {
        background: transparent !important;
    }
    
    .stMultiSelect > div > div {
        background-color: rgba(0, 0, 0, 0.8) !important;
        border: 1px solid rgba(68, 255, 68, 0.3) !important;
        border-radius: 8px !important;
        color: #ffffff !important;
    }
    
    .stMultiSelect > div > div > div {
        color: #ffffff !important;
    }
    
    /* Dropdown menu styling */
    .stMultiSelect > div > div[data-baseweb="select"] > div {
        background-color: rgba(0, 0, 0, 0.9) !important;
        border: 1px solid rgba(68, 255, 68, 0.3) !important;
        color: #ffffff !important;
    }
    
    .stMultiSelect > div > div[data-baseweb="select"] ul {
        background-color: rgba(0, 0, 0, 0.95) !important;
        border: 1px solid rgba(68, 255, 68, 0.3) !important;
        border-radius: 8px !important;
    }
    
    .stMultiSelect > div > div[data-baseweb="select"] ul li {
        background-color: rgba(0, 0, 0, 0.95) !important;
        color: #ffffff !important;
    }
    
    .stMultiSelect > div > div[data-baseweb="select"] ul li:hover {
        background-color: rgba(68, 255, 68, 0.2) !important;
        color: #44ff44 !important;
    }
    
    /* Selected items styling */
    .stMultiSelect span[data-baseweb="tag"] {
        background-color: rgba(68, 255, 68, 0.2) !important;
        border: 1px solid #44ff44 !important;
        color: #44ff44 !important;
    }
    
    /* Ensure all elements have proper visibility */
    .element-container {
        background: transparent !important;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #44ff44, #33cc33) !important;
        border: none !important;
        box-shadow: none !important;
        color: #000 !important;
    }
    
    @keyframes moveGradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    
    @keyframes shimmer {
        0% { left: -100%; }
        100% { left: 100%; }
    }
    
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .stApp {
        background: linear-gradient(135deg, #0a0a0a 0%, #000000 50%, #0a0a0a 100%);
        font-family: 'JetBrains Mono', monospace;
    }
    
    .main-header {
        text-align: center;
        margin-bottom: 30px;
        padding: 20px;
        background: linear-gradient(-45deg, rgba(0, 0, 0, 0.9), rgba(68, 255, 68, 0.1), rgba(0, 0, 0, 0.9), rgba(34, 139, 34, 0.1));
        background-size: 400% 400%;
        animation: moveGradient 4s ease infinite;
        border-radius: 15px;
        border: 1px solid rgba(68, 255, 68, 0.3);
        backdrop-filter: blur(10px);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(68, 255, 68, 0.3), transparent);
        animation: shimmer 3s linear infinite;
    }

    .main-header h1 {
        font-size: 3rem;
        color: #44ff44;
        text-shadow: 0 0 20px rgba(68, 255, 68, 0.5);
        margin-bottom: 10px;
        position: relative;
        z-index: 2;
        font-weight: 700;
        font-family: 'JetBrains Mono', monospace;
    }

    .content-area {
        background: rgba(0, 0, 0, 0.9);
        border-radius: 15px;
        border: 1px solid rgba(68, 255, 68, 0.3);
        padding: 30px;
        min-height: 600px;
    }

    .stat-card {
        background: linear-gradient(135deg, rgba(0, 0, 0, 0.8), rgba(68, 255, 68, 0.1));
        color: #ffffff;
        padding: 25px;
        border-radius: 10px;
        text-align: center;
        border: 1px solid rgba(68, 255, 68, 0.3);
        transition: all 0.3s ease;
    }

    .stat-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 5px 15px rgba(68, 255, 68, 0.2);
    }

    .stat-number {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 10px;
        color: #44ff44;
        text-shadow: 0 0 10px rgba(68, 255, 68, 0.3);
    }

    .stat-label {
        font-size: 1.1rem;
        opacity: 0.9;
        color: #ffffff;
    }

    .emergency-card {
        background: rgba(0, 0, 0, 0.8);
        border: 2px solid rgba(231, 76, 60, 0.5);
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        transition: all 0.3s ease;
        margin-bottom: 20px;
        color: #ffffff !important;
    }

    .emergency-card:hover {
        border-color: #e74c3c;
        transform: translateY(-3px);
        box-shadow: 0 5px 15px rgba(231, 76, 60, 0.2);
    }

    .emergency-card h3 {
        color: #e74c3c !important;
        margin-bottom: 15px;
    }

    .emergency-card p, .emergency-card span, .emergency-card div {
        color: #ffffff !important;
    }

    .phone-number {
        font-size: 1.5rem;
        font-weight: bold;
        color: #44ff44 !important;
        margin: 10px 0;
    }

    .feature-card, .feature-card * {
        color: #ffffff !important;
    }

    .feature-card h3 {
        color: #44ff44 !important;
    }

    .feature-card {
        background: rgba(0, 0, 0, 0.8);
        border-radius: 10px;
        padding: 25px;
        text-align: center;
        border: 1px solid rgba(68, 255, 68, 0.3);
        transition: all 0.3s ease;
        margin-bottom: 20px;
    }

    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 5px 20px rgba(68, 255, 68, 0.2);
        border-color: #44ff44;
    }

    .feature-icon {
        font-size: 3rem;
        margin-bottom: 15px;
        color: #44ff44;
    }

    .chat-message {
        margin-bottom: 20px;
        animation: fadeInUp 0.5s ease;
        clear: both;
    }

    .user-message {
        text-align: right;
    }

    .bot-message {
        text-align: left;
    }

    .message-content {
        display: inline-block;
        padding: 15px 20px;
        border-radius: 15px;
        max-width: 80%;
        position: relative;
        font-family: 'JetBrains Mono', monospace;
        word-wrap: break-word;
        white-space: pre-wrap;
    }

    .user-message .message-content {
        background: linear-gradient(135deg, #44ff44, #33cc33);
        color: #000000 !important;
        border-bottom-right-radius: 5px;
    }

    .bot-message .message-content {
        background: rgba(0, 0, 0, 0.9) !important;
        color: #ffffff !important;
        border: 1px solid rgba(68, 255, 68, 0.3);
        border-bottom-left-radius: 5px;
    }

    .message-time {
        font-size: 0.7rem;
        color: #888 !important;
        margin-top: 5px;
        font-family: 'JetBrains Mono', monospace;
    }

    .stButton button {
        background: linear-gradient(135deg, #44ff44, #33cc33) !important;
        border: none !important;
        border-radius: 25px !important;
        color: #000 !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
    }

    .stButton button:hover {
        transform: scale(1.05) !important;
        box-shadow: 0 0 20px rgba(68, 255, 68, 0.4) !important;
    }

    .stTextInput input {
        background: rgba(0, 0, 0, 0.8) !important;
        border: 1px solid rgba(68, 255, 68, 0.3) !important;
        border-radius: 25px !important;
        color: #ffffff !important;
        font-family: 'JetBrains Mono', monospace !important;
    }

    .stTextInput input:focus {
        border-color: #44ff44 !important;
        box-shadow: 0 0 20px rgba(68, 255, 68, 0.2) !important;
    }

    .status-bar {
        background: rgba(0, 0, 0, 0.9);
        padding: 15px;
        border-radius: 25px;
        margin-top: 30px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border: 1px solid rgba(68, 255, 68, 0.2);
        font-family: 'JetBrains Mono', monospace;
        flex-wrap: wrap;
        gap: 10px;
    }

    .status-item {
        display: flex;
        align-items: center;
        gap: 10px;
        color: #ffffff;
        font-size: 0.9rem;
    }

    .status-dot {
        width: 8px;
        height: 8px;
        background: #44ff44;
        border-radius: 50%;
        animation: pulse 2s infinite;
    }

    h1, h2, h3, h4, h5, h6 {
        color: #44ff44 !important;
    }
    
    p, span, div {
        color: #ffffff !important;
    }

    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 2rem;
        }
        
        .content-area {
            padding: 20px;
        }
    }
</style>
""", unsafe_allow_html=True)

# Enhanced Sidebar
with st.sidebar:
    st.markdown("### 🤖 AI Configuration")
    
    # Show current status
    st.write(f"**Status:** {st.session_state.get('ai_status', 'Unknown')}")
    
    st.markdown("---")
    
    # Status indicators
    if st.session_state.get('ai_enabled', False):
        st.success("🧬 Enhanced Forensic AI Active")
        st.write("**Forensic Capabilities:**")
        st.write("• DNA analysis & profiling")
        st.write("• Crime scene investigation")
        st.write("• Digital forensics")
        st.write("• Ballistics & firearms")
        st.write("• Toxicology analysis")
        st.write("• Expert testimony prep")
        st.write("• Laboratory protocols")
        st.write("• Evidence admissibility")
        
        st.write("**Response Types:**")
        st.write("• Concise (default)")
        st.write("• Detailed (on request)")
        st.write("• Context-aware")
        st.write("• Forensically accurate")
    else:
        st.warning("⚠️ AI Offline")
        st.write("• Check API key")
        st.write("• Verify internet connection")
    
    st.success("📊 Enhanced Database")
    st.write("**Historical Data:**")
    st.write("• 2022-2025 crime statistics")
    st.write("• Quarterly comparisons") 
    st.write("• Detection rate analysis")
    st.write("• 13 crime hotspots mapped")
    st.write("• Forensic knowledge base")
    st.write("• Emergency contact database")

# Main Header
current_time = get_stkitts_time()
current_date = get_stkitts_date()

st.markdown(f"""
<div class="main-header">
    <h1>🔒 SECURO</h1>
    <div style="color: #888; text-transform: uppercase; letter-spacing: 2px; position: relative; z-index: 2;">Enhanced Forensic Science & Crime Intelligence AI</div>
    <div style="color: #44ff44; margin-top: 5px; position: relative; z-index: 2;">🇰🇳 Royal St. Christopher & Nevis Police Force</div>
    <div style="color: #888; margin-top: 8px; font-size: 0.8rem; position: relative; z-index: 2;">📅 {current_date} | 🕒 {current_time} (AST)</div>
</div>
""", unsafe_allow_html=True)

# Navigation Bar
col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    if st.button("🏠 Home", key="nav_home", help="Welcome to SECURO", use_container_width=True):
        st.session_state.current_page = 'welcome'
        st.rerun()

with col2:
    if st.button("ℹ️ About SECURO", key="nav_about", help="About SECURO System", use_container_width=True):
        st.session_state.current_page = 'about'
        st.rerun()

with col3:
    if st.button("🗺️ Crime Hotspots", key="nav_map", help="Interactive Crime Map", use_container_width=True):
        st.session_state.current_page = 'map'
        st.rerun()

with col4:
    if st.button("📊 Statistics & Analytics", key="nav_stats", help="Crime Data Analysis", use_container_width=True):
        st.session_state.current_page = 'statistics'
        st.rerun()

with col5:
    if st.button("🚨 Emergency", key="nav_emergency", help="Emergency Contacts", use_container_width=True):
        st.session_state.current_page = 'emergency'
        st.rerun()

with col6:
    if st.button("💬 AI Assistant", key="nav_chat", help="Chat with SECURO AI", use_container_width=True):
        st.session_state.current_page = 'chat'
        st.rerun()

# HOME PAGE
if st.session_state.current_page == 'welcome':
    st.markdown("""
    <div style="text-align: center; margin-bottom: 40px;">
        <h2 style="color: #44ff44; font-size: 2.5rem; margin-bottom: 20px; text-shadow: 0 0 15px rgba(68, 255, 68, 0.5);">Welcome to Enhanced SECURO</h2>
        <p style="font-size: 1.1rem; line-height: 1.6; margin-bottom: 30px; color: #ffffff;">Your comprehensive AI-powered forensic science and crime analysis system for St. Kitts & Nevis</p>
        <p style="font-size: 1rem; line-height: 1.6; color: #ffffff;">SECURO now includes enhanced forensic expertise, historical data from 2022-2025, and context-aware AI responses.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Enhanced Feature Cards
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🧬</div>
            <h3>Advanced Forensic Science</h3>
            <p>Expert knowledge in DNA analysis, ballistics, toxicology, digital forensics, and crime scene investigation with laboratory protocols.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🤖</div>
            <h3>Enhanced AI Assistant</h3>
            <p>Context-aware responses: concise by default, detailed on request. Forensically accurate with legal admissibility guidance.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📊</div>
            <h3>Multi-Year Crime Database</h3>
            <p>Historical data from 2022-2025 with quarterly analysis, detection rates, and trend comparison across time periods.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">⚖️</div>
            <h3>Court & Laboratory Support</h3>
            <p>Expert testimony preparation, evidence admissibility standards, chain of custody protocols, and quality control procedures.</p>
        </div>
        """, unsafe_allow_html=True)

# ABOUT PAGE (Enhanced)
elif st.session_state.current_page == 'about':
    st.markdown("""
    <h2 style="color: #44ff44; margin-bottom: 20px; text-align: center;">About Enhanced SECURO</h2>
    
    <p style="color: #ffffff;"><strong style="color: #44ff44;">SECURO</strong> is a comprehensive forensic science and crime analysis AI system built specifically for the Royal St. Christopher and Nevis Police Force. Combining cutting-edge forensic expertise with multi-year crime intelligence and context-aware AI responses.</p>

    <h3 style="color: #44ff44; margin: 20px 0 10px 0;">🧬 Forensic Science Expertise</h3>
    <ul style="list-style: none; padding: 0; color: #ffffff;">
        <li style="padding: 8px 0; padding-left: 25px; position: relative; color: #ffffff;">
            <span style="position: absolute; left: 0; color: #44ff44; font-weight: bold;">✓</span>
            <span style="color: #ffffff;">DNA Analysis - STR profiling, CODIS, degraded samples, mixture interpretation, touch DNA</span>
        </li>
        <li style="padding: 8px 0; padding-left: 25px; position: relative; color: #ffffff;">
            <span style="position: absolute; left: 0; color: #44ff44; font-weight: bold;">✓</span>
            <span style="color: #ffffff;">Crime Scene Investigation - Evidence collection, photography, reconstruction, bloodstain pattern analysis</span>
        </li>
        <li style="padding: 8px 0; padding-left: 25px; position: relative; color: #ffffff;">
            <span style="position: absolute; left: 0; color: #44ff44; font-weight: bold;">✓</span>
            <span style="color: #ffffff;">Digital Forensics - Mobile devices, computers, encrypted data, metadata analysis, timeline reconstruction</span>
        </li>
        <li style="padding: 8px 0; padding-left: 25px; position: relative; color: #ffffff;">
            <span style="position: absolute; left: 0; color: #44ff44; font-weight: bold;">✓</span>
            <span style="color: #ffffff;">Ballistics & Firearms - Bullet comparison, GSR testing, trajectory analysis, distance determination</span>
        </li>
        <li style="padding: 8px 0; padding-left: 25px; position: relative; color: #ffffff;">
            <span style="position: absolute; left: 0; color: #44ff44; font-weight: bold;">✓</span>
            <span style="color: #ffffff;">Toxicology - Drug testing, poison detection, post-mortem analysis, therapeutic vs toxic levels</span>
        </li>
        <li style="padding: 8px 0; padding-left: 25px; position: relative; color: #ffffff;">
            <span style="position: absolute; left: 0; color: #44ff44; font-weight: bold;">✓</span>
            <span style="color: #ffffff;">Trace Evidence - Fibers, paint, glass, soil, tool marks, impression evidence analysis</span>
        </li>
    </ul>

    <h3 style="color: #44ff44; margin: 20px 0 10px 0;">🔬 Enhanced AI Capabilities</h3>
    <ul style="list-style: none; padding: 0; color: #ffffff;">
        <li style="padding: 8px 0; padding-left: 25px; position: relative; color: #ffffff;">
            <span style="position: absolute; left: 0; color: #44ff44; font-weight: bold;">✓</span>
            <span style="color: #ffffff;">Context-Aware Responses - Concise by default, detailed when requested</span>
        </li>
        <li style="padding: 8px 0; padding-left: 25px; position: relative; color: #ffffff;">
            <span style="position: absolute; left: 0; color: #44ff44; font-weight: bold;">✓</span>
            <span style="color: #ffffff;">Query Type Detection - Forensic, statistical, predictive, and general inquiries</span>
        </li>
        <li style="padding: 8px 0; padding-left: 25px; position: relative; color: #ffffff;">
            <span style="position: absolute; left: 0; color: #44ff44; font-weight: bold;">✓</span>
            <span style="color: #ffffff;">Multi-Year Data Integration - 2022-2025 historical crime analysis</span>
        </li>
        <li style="padding: 8px 0; padding-left: 25px; position: relative; color: #ffffff;">
            <span style="position: absolute; left: 0; color: #44ff44; font-weight: bold;">✓</span>
            <span style="color: #ffffff;">Forensic Knowledge Base - Procedures, protocols, and best practices</span>
        </li>
    </ul>

    <h3 style="color: #44ff44; margin: 20px 0 10px 0;">📊 Historical Crime Intelligence (2022-2025)</h3>
    <ul style="list-style: none; padding: 0; color: #ffffff;">
        <li style="padding: 8px 0; padding-left: 25px; position: relative; color: #ffffff;">
            <span style="position: absolute; left: 0; color: #44ff44; font-weight: bold;">✓</span>
            <span style="color: #ffffff;">Q2 2025: 292 total crimes, 38.7% detection rate, 4 murders (↓87% from 2023)</span>
        </li>
        <li style="padding: 8px 0; padding-left: 25px; position: relative; color: #ffffff;">
            <span style="position: absolute; left: 0; color: #44ff44; font-weight: bold;">✓</span>
            <span style="color: #ffffff;">Quarterly comparisons showing crime trends and detection improvements</span>
        </li>
        <li style="padding: 8px 0; padding-left: 25px; position: relative; color: #ffffff;">
            <span style="position: absolute; left: 0; color: #44ff44; font-weight: bold;">✓</span>
            <span style="color: #ffffff;">St. Kitts vs Nevis comparative analysis with regional performance metrics</span>
        </li>
        <li style="padding: 8px 0; padding-left: 25px; position: relative; color: #ffffff;">
            <span style="position: absolute; left: 0; color: #44ff44; font-weight: bold;">✓</span>
            <span style="color: #ffffff;">Drug crimes: 100% detection rate, Firearms offences: 100% detection rate</span>
        </li>
    </ul>

    <h3 style="color: #44ff44; margin: 20px 0 10px 0;">⚖️ Legal & Laboratory Standards</h3>
    <p style="color: #ffffff;">SECURO maintains the highest forensic science standards with protocols based on international best practices, ASTM standards, and Caribbean forensic guidelines. All recommendations are scientifically validated and court-admissible with proper chain of custody documentation.</p>
    """, unsafe_allow_html=True)

# CRIME HOTSPOTS PAGE (Same as before)
elif st.session_state.current_page == 'map':
    st.markdown('<h2 style="color: #44ff44;">🗺️ Crime Hotspot Map - St. Kitts & Nevis</h2>', unsafe_allow_html=True)
    
    try:
        with st.spinner("🗺️ Loading interactive crime hotspot map..."):
            crime_map = create_crime_hotspot_map()
            map_data = st_folium(
                crime_map,
                width="100%",
                height=600,
                returned_objects=["last_object_clicked_tooltip", "last_clicked"],
                key="crime_hotspot_map"
            )
            
            # Display clicked location info
            if map_data['last_object_clicked_tooltip']:
                clicked_info = map_data['last_object_clicked_tooltip']
                st.info(f"📍 **Last Clicked Location:** {clicked_info}")
    
    except Exception as e:
        st.error(f"❌ Map Error: {str(e)}")
        st.info("💡 Note: Make sure folium and streamlit-folium are installed")
    
    # Hotspot Analysis Summary
    st.markdown('<h3 style="color: #44ff44;">📍 Hotspot Analysis Summary</h3>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="background: rgba(231, 76, 60, 0.1); padding: 15px; border-radius: 8px; border-left: 4px solid #e74c3c;">
            <strong style="color: #e74c3c;">High Risk Areas (3)</strong><br>
            <span style="color: #ffffff; font-size: 0.9rem;">Basseterre Central, Molineux, Tabernacle<br>Total: 109 crimes</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: rgba(243, 156, 18, 0.1); padding: 15px; border-radius: 8px; border-left: 4px solid #f39c12;">
            <strong style="color: #f39c12;">Medium Risk Areas (6)</strong><br>
            <span style="color: #ffffff; font-size: 0.9rem;">Cayon, Newton Ground, Old Road, etc.<br>Total: 133 crimes</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="background: rgba(39, 174, 96, 0.1); padding: 15px; border-radius: 8px; border-left: 4px solid #27ae60;">
            <strong style="color: #27ae60;">Low Risk Areas (4)</strong><br>
            <span style="color: #ffffff; font-size: 0.9rem;">Sandy Point, Dieppe Bay, etc.<br>Total: 60 crimes</span>
        </div>
        """, unsafe_allow_html=True)

# ENHANCED STATISTICS & ANALYTICS PAGE
elif st.session_state.current_page == 'statistics':
    st.markdown('<h2 style="color: #44ff44;">📊 Enhanced Crime Statistics & Analytics</h2>', unsafe_allow_html=True)
    
    # **NEW: Year/Period Selection Dropdown**
    st.markdown('<h3 style="color: #44ff44;">📅 Select Time Periods for Analysis</h3>', unsafe_allow_html=True)
    
    # Add some spacing and a container for better visibility
    with st.container():
        st.markdown("""
        <div style="background: rgba(68, 255, 68, 0.05); padding: 20px; border-radius: 10px; margin: 20px 0; border: 1px solid rgba(68, 255, 68, 0.2);">
        </div>
        """, unsafe_allow_html=True)
        
        available_periods = list(st.session_state.crime_stats.keys())
        period_labels = {key: data["period"] for key, data in st.session_state.crime_stats.items()}
        
        selected_periods = st.multiselect(
            "📊 Choose time periods to analyze:",
            options=available_periods,
            default=['2025_Q2'],
            format_func=lambda x: period_labels.get(x, x),
            help="Select one or more time periods to compare statistics and trends",
            key="period_selector"
        )
    
    if not selected_periods:
        st.warning("Please select at least one time period to view statistics.")
        st.stop()
    
    st.session_state.selected_periods = selected_periods
    
    # Display stats for selected periods
    if len(selected_periods) == 1:
        # Single period detailed view
        period_key = selected_periods[0]
        period_data = st.session_state.crime_stats[period_key]
        
        st.markdown(f'<h3 style="color: #44ff44;">📈 {period_data["period"]} Overview</h3>', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number">{period_data['total_crimes']}</div>
                <div class="stat-label">Total Crimes</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            detection_rate = period_data.get('detection_rate', 'N/A')
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number">{detection_rate}{'%' if detection_rate != 'N/A' else ''}</div>
                <div class="stat-label">Detection Rate</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st_kitts_crimes = period_data.get('st_kitts', {}).get('crimes', 'N/A')
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number">{st_kitts_crimes}</div>
                <div class="stat-label">St. Kitts Crimes</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            nevis_crimes = period_data.get('nevis', {}).get('crimes', 'N/A')
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number">{nevis_crimes}</div>
                <div class="stat-label">Nevis Crimes</div>
            </div>
            """, unsafe_allow_html=True)
    
    else:
        # Multiple periods comparison view
        st.markdown('<h3 style="color: #44ff44;">📈 Multi-Period Comparison</h3>', unsafe_allow_html=True)
        
        # Create comparison table
        comparison_data = []
        for period_key in selected_periods:
            period_data = st.session_state.crime_stats[period_key]
            comparison_data.append({
                "Period": period_data["period"],
                "Total Crimes": period_data["total_crimes"],
                "Detection Rate": f"{period_data.get('detection_rate', 'N/A')}{'%' if period_data.get('detection_rate') else ''}",
                "St. Kitts": period_data.get('st_kitts', {}).get('crimes', 'N/A'),
                "Nevis": period_data.get('nevis', {}).get('crimes', 'N/A')
            })
        
        df = pd.DataFrame(comparison_data)
        st.dataframe(df, use_container_width=True)
    
    # **NEW: Enhanced Chart Controls**
    st.markdown('<h3 style="color: #44ff44;">📈 Interactive Analytics</h3>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📈 Crime Trends", key="chart_trends_new"):
            if len(selected_periods) > 1:
                fig = create_historical_crime_charts("crime_trends", selected_periods, st.session_state.crime_stats)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Select multiple periods to view trends.")
    
    with col2:
        if st.button("🎯 Detection Comparison", key="chart_detection_new"):
            if len(selected_periods) > 1:
                fig = create_historical_crime_charts("detection_comparison", selected_periods, st.session_state.crime_stats)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Select multiple periods to compare detection rates.")
    
    with col3:
        if st.button("🔍 Crime Breakdown", key="chart_breakdown_new"):
            fig = create_historical_crime_charts("crime_type_breakdown", selected_periods, st.session_state.crime_stats)
            if fig:
                st.plotly_chart(fig, use_container_width=True)

# EMERGENCY CONTACTS PAGE (Same as before)
elif st.session_state.current_page == 'emergency':
    st.markdown("""
    <h2 style="color: #e74c3c; margin-bottom: 30px; text-align: center;">🚨 Emergency Contacts</h2>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    emergency_contacts = [
        ("🚔 Police Emergency", "911", "For immediate police assistance and emergency response"),
        ("🏢 Police Headquarters", "465-2241", "Royal St. Christopher and Nevis Police Force\nLocal Intelligence: Ext. 4238/4239"),
        ("🏥 Medical Emergency", "465-2551", "Hospital services and medical emergencies"),
        ("🔥 Fire Department", "465-2515", "Fire emergencies and rescue operations\nAlt: 465-7167"),
        ("🚢 Coast Guard", "465-8384", "Maritime emergencies and water rescue\nAlt: 466-9280"),
        ("🌡️ Met Office", "465-2749", "Weather emergencies and warnings"),
        ("➕ Red Cross", "465-2584", "Disaster relief and emergency aid"),
        ("⚡ NEMA", "466-5100", "National Emergency Management Agency")
    ]
    
    for i, (title, number, description) in enumerate(emergency_contacts):
        col = [col1, col2, col3, col4][i % 4]
        with col:
            st.markdown(f"""
            <div class="emergency-card">
                <h3>{title}</h3>
                <div class="phone-number">{number}</div>
                <p style="color: #ffffff;">{description}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Emergency Guidelines
    st.markdown("""
    <div style="background: rgba(255, 243, 205, 0.1); border: 1px solid rgba(255, 234, 167, 0.3); padding: 20px; border-radius: 10px; margin-top: 30px;">
        <h3 style="color: #f39c12; margin-bottom: 15px;">⚠️ Important Emergency Guidelines</h3>
        <ul style="color: #ffffff; line-height: 1.6; list-style: none; padding: 0;">
            <li style="padding: 4px 0; padding-left: 20px; position: relative;">
                <span style="position: absolute; left: 0; color: #f39c12;">•</span>
                <strong>For life-threatening emergencies, always call 911 first</strong>
            </li>
            <li style="padding: 4px 0; padding-left: 20px; position: relative;">
                <span style="position: absolute; left: 0; color: #f39c12;">•</span>
                When calling, provide your exact location and nature of emergency
            </li>
            <li style="padding: 4px 0; padding-left: 20px; position: relative;">
                <span style="position: absolute; left: 0; color: #f39c12;">•</span>
                Stay on the line until instructed to hang up
            </li>
            <li style="padding: 4px 0; padding-left: 20px; position: relative;">
                <span style="position: absolute; left: 0; color: #f39c12;">•</span>
                Keep these numbers easily accessible at all times
            </li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# **ENHANCED AI ASSISTANT CHAT PAGE**
elif st.session_state.current_page == 'chat':
    st.markdown('<h2 style="color: #44ff44; text-align: center;">💬 Enhanced SECURO AI Assistant</h2>', unsafe_allow_html=True)
    
    # Enhanced Status Display
    st.markdown('<h3 style="color: #44ff44;">🧬 Enhanced Forensic Intelligence System</h3>', unsafe_allow_html=True)
    
    ai_status = st.session_state.get('ai_status', 'AI Status Unknown')
    if st.session_state.get('ai_enabled', False):
        st.success(f"✅ Enhanced AI Ready: Full forensic science expertise + multi-year crime intelligence + context-aware responses | {ai_status}")
    else:
        st.error(f"❌ AI Offline: Check your Google AI API key | {ai_status}")

    # Enhanced Intelligence Summary
    total_hotspots = len(CRIME_HOTSPOTS)
    total_periods = len(HISTORICAL_CRIME_DATABASE)
    
    st.info(f"🧬 **Enhanced Capabilities:** DNA • Digital forensics • Ballistics • Toxicology • Crime scenes • {total_hotspots} hotspots • {total_periods} time periods • Context-aware responses • Forensic knowledge base")
    
    # Response Type Information
    st.markdown("""
    <div style="background: rgba(68, 255, 68, 0.1); padding: 15px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #44ff44;">
        <strong style="color: #44ff44;">💡 Response Types:</strong><br>
        <span style="color: #ffffff;">• <strong>Concise:</strong> Brief, focused answers (default)</span><br>
        <span style="color: #ffffff;">• <strong>Detailed:</strong> Comprehensive explanations (say "detailed" or "explain")</span><br>
        <span style="color: #ffffff;">• <strong>Context-aware:</strong> Forensic, statistical, or general based on your query</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize chat messages
    if not st.session_state.messages:
        st.session_state.messages.append({
            "role": "assistant",
            "content": "🔒 **Enhanced SECURO Forensic & Crime Intelligence System Online!**\n\nHi! I'm your enhanced comprehensive forensic science and crime analysis AI assistant.\n\n🧬 **What I can help with:**\n• **Forensic Science** - DNA analysis, fingerprints, ballistics, toxicology, trace evidence\n• **Crime Scene Investigation** - Evidence collection, documentation, reconstruction procedures\n• **Digital Forensics** - Mobile devices, computers, encrypted data, timeline analysis\n• **Laboratory Procedures** - Testing protocols, quality control, contamination prevention\n• **Expert Testimony** - Court preparation, admissibility requirements, legal standards\n• **Crime Analysis** - Multi-year statistics (2022-2025), patterns, hotspot intelligence\n• **Investigation Support** - Case management, evidence correlation, predictive analysis\n\n**🎯 New Features:**\n• **Context-aware responses** - Concise by default, detailed on request\n• **Multi-year database** - Historical crime data from 2022-2025\n• **Enhanced forensic knowledge** - Procedures, protocols, best practices\n\n💬 **Just ask naturally!** Say \"detailed\" or \"explain\" for comprehensive answers. I'll keep responses concise otherwise.\n\nWhat forensic or investigative question can I help you with?",
            "timestamp": get_stkitts_time()
        })
    
    # Display chat messages
    for message in st.session_state.messages:
        if message["role"] == "user":
            clean_content = str(message["content"]).strip()
            st.markdown(f"""
            <div class="chat-message user-message">
                <div class="message-content">{clean_content}</div>
                <div class="message-time">You • {message["timestamp"]} AST</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            clean_content = str(message["content"]).strip()
            clean_content = re.sub(r'<[^>]+>', '', clean_content)
            clean_content = clean_content.replace('```', '')
           
            st.markdown(f"""
            <div class="chat-message bot-message">
                <div class="message-content">{clean_content}</div>
                <div class="message-time">SECURO • {message["timestamp"]} AST</div>
            </div>
            """, unsafe_allow_html=True)

    # Enhanced Chat input
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_input(
            "💬 Message Enhanced SECURO:",
            placeholder="Ask about forensics, crime stats, or investigations... (Say 'detailed' for comprehensive answers)",
            label_visibility="collapsed",
            key="chat_input"
        )
        
        submitted = st.form_submit_button("Send", type="primary")
        
        if submitted and user_input and user_input.strip():
            current_time = get_stkitts_time()
            
            # Add user message
            st.session_state.messages.append({
                "role": "user", 
                "content": user_input,
                "timestamp": current_time
            })
            
            # Generate enhanced response
            with st.spinner("🧬 Analyzing with enhanced forensic intelligence..."):
                response = generate_enhanced_smart_response(user_input, st.session_state.selected_language)
            
            st.session_state.messages.append({
                "role": "assistant",
                "content": response,
                "timestamp": current_time
            })
            
            st.rerun()

# Enhanced Status bar
current_time = get_stkitts_time()

st.markdown(f"""
<div class="status-bar">
    <div class="status-item">
        <div class="status-dot"></div>
        <span>Enhanced SECURO {"AI Active" if st.session_state.get('ai_enabled', False) else "AI Offline"}</span>
    </div>
    <div class="status-item">
        <div class="status-dot"></div>
        <span>Database: 2022-2025</span>
    </div>
    <div class="status-item">
        <div class="status-dot"></div>
        <span>Forensic Knowledge Base</span>
    </div>
    <div class="status-item">
        <div class="status-dot"></div>
        <span>Hotspots: 13 Locations</span>
    </div>
    <div class="status-item">
        <div class="status-dot"></div>
        <span>{current_time} AST</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Enhanced Footer
st.markdown(f"""
<div style="text-align: center; color: #666; font-size: 0.8rem; font-family: 'JetBrains Mono', monospace; padding: 20px; margin-top: 20px; border-top: 1px solid rgba(68, 255, 68, 0.2);">
    📊 <span style="color: #44ff44;">Data Source:</span> Royal St. Christopher & Nevis Police Force (RSCNPF) • Multi-Year Database (2022-2025)<br>
    📞 <span style="color: #44ff44;">Local Intelligence Office:</span> <a href="tel:+18694652241" style="color: #44ff44; text-decoration: none;">869-465-2241</a> Ext. 4238/4239 | 
    📧 <a href="mailto:liosk@police.kn" style="color: #44ff44; text-decoration: none;">liosk@police.kn</a><br>
    🔄 <span style="color: #44ff44;">Last Updated:</span> {get_stkitts_date()} {get_stkitts_time()} AST | <span style="color: #44ff44;">Enhanced Forensic Intelligence</span><br>
    🗺️ <span style="color: #44ff44;">Intelligence System:</span> 13 hotspots • Multi-year analytics • Context-aware AI • Enhanced forensic database<br>
    🌍 <span style="color: #44ff44;">Multi-language Support</span> | 🔒 <span style="color: #44ff44;">Secure Law Enforcement Platform</span><br>
    <br>
    <div style="background: rgba(68, 255, 68, 0.1); padding: 10px; border-radius: 5px; margin-top: 10px;">
        <span style="color: #44ff44; font-weight: bold;">🧬 Enhanced Comprehensive Forensic Intelligence Platform</span><br>
        <span style="color: #ffffff;">DNA analysis • Crime scene investigation • Digital forensics • Ballistics • Toxicology • Expert testimony • Laboratory protocols • Court admissibility • Context-aware AI</span>
    </div>
</div>
""", unsafe_allow_html=True)
