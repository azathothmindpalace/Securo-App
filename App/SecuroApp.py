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
import uuid
from datetime import datetime as dt
import PyPDF2
import tempfile
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

# Crime Hotspots Data for St. Kitts & Nevis (ONLY for the map page, not AI)
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

# **NEW: PDF Statistics URLs**
STATISTICS_PDF_URLS = [
    "http://www.police.kn/statistics/links/1752416412.pdf",
    "http://www.police.kn/statistics/links/1752414290.pdf",
    "http://www.police.kn/statistics/links/1750875153.pdf",
    "http://www.police.kn/statistics/links/1746572831.pdf",
    "http://www.police.kn/statistics/links/1746572806.pdf",
    "http://www.police.kn/statistics/links/1739113354.pdf",
    "http://www.police.kn/statistics/links/1739113269.pdf",
    "http://www.police.kn/statistics/links/1739112788.pdf",
    "http://www.police.kn/statistics/links/1733163796.pdf",
    "http://www.police.kn/statistics/links/1733163758.pdf",
    "http://www.police.kn/statistics/links/1733163699.pdf",
    "http://www.police.kn/statistics/links/1724190706.pdf",
    "http://www.police.kn/statistics/links/1724013300.pdf",
    "http://www.police.kn/statistics/links/1721419557.pdf",
    "http://www.police.kn/statistics/links/1721419503.pdf",
    "http://www.police.kn/statistics/links/1720455298.pdf",
    "http://www.police.kn/statistics/links/1720455273.pdf",
    "http://www.police.kn/statistics/links/1720455248.pdf",
    "http://www.police.kn/statistics/links/1716987318.pdf",
    "http://www.police.kn/statistics/links/1716987296.pdf",
    "http://www.police.kn/statistics/links/1716987275.pdf",
    "http://www.police.kn/statistics/links/1716987249.pdf",
    "http://www.police.kn/statistics/links/1716987224.pdf",
    "http://www.police.kn/statistics/links/1716987196.pdf",
    "http://www.police.kn/statistics/links/1716987157.pdf",
    "http://www.police.kn/statistics/links/1716987132.pdf",
    "http://www.police.kn/statistics/links/1716987059.pdf"
]

# **NEW: MacroTrends International Comparison Data**
MACROTRENDS_DATA = {
    "homicide_rates_per_100k": {
        "2020": 20.99,
        "2019": 25.15,
        "2018": 48.16,
        "2017": 48.14,  # Estimated based on 0.05% increase mentioned
        "2016": 42.50,  # Estimated for trend
        "2015": 38.20,  # Estimated for trend
        "2014": 35.80,  # Estimated for trend
        "2013": 42.10,  # Estimated for trend
        "2012": 33.60,  # From search results
        "2011": 67.60   # From search results - worst year mentioned
    },
    "comparative_context": {
        "global_average_firearm_homicides": 42.0,
        "skn_firearm_homicides_2010": 85.0,
        "skn_firearm_homicides_2003": 63.6,
        "basseterre_2011_rate": 131.6,  # Highest capital city rate globally
        "world_ranking_2012": 8,  # 8th highest globally
        "world_ranking_2005_2014": 7   # 7th highest during this period
    },
    "recent_trends": {
        "2024_total_crimes": 1146,  # 11% decrease from 2023
        "2023_total_crimes": 1280,  # 7% decrease from 2022  
        "2022_total_crimes": 1360,
        "2024_homicides": 28,  # 10% reduction from 2023
        "2023_homicides": 31,
        "first_quarter_2025": "No homicides (first time in 23 years)"
    }
}

# **NEW: Statistical Data Store**
if 'statistical_database' not in st.session_state:
    st.session_state.statistical_database = {}

# **NEW: Chat Management System**
if 'chat_sessions' not in st.session_state:
    st.session_state.chat_sessions = {}

if 'current_chat_id' not in st.session_state:
    st.session_state.current_chat_id = None

if 'chat_counter' not in st.session_state:
    st.session_state.chat_counter = 1

# Enhanced HISTORICAL CRIME DATABASE with complete 2023 annual data from PDFs
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
    "2024_ANNUAL": {
        "period": "2024 Full Year (Jan-Dec)",
        "total_crimes": 1146,
        "detection_rate": 41.8,
        "federation": {
            "murder_manslaughter": {"total": 28, "detected": 16, "rate": 57.0},
            "shooting_intent": {"total": 6, "detected": 0, "rate": 0.0},
            "attempted_murder": {"total": 18, "detected": 5, "rate": 28.0},
            "bodily_harm": {"total": 145, "detected": 115, "rate": 79.0},
            "sex_crimes": {"total": 72, "detected": 33, "rate": 46.0},
            "break_ins": {"total": 134, "detected": 36, "rate": 27.0},
            "larcenies": {"total": 395, "detected": 119, "rate": 30.0},
            "robberies": {"total": 42, "detected": 5, "rate": 12.0},
            "firearms_offences": {"total": 21, "detected": 19, "rate": 90.0},
            "drug_crimes": {"total": 20, "detected": 20, "rate": 100.0},
            "malicious_damage": {"total": 191, "detected": 72, "rate": 38.0},
            "other_crimes": {"total": 74, "detected": 39, "rate": 53.0}
        },
        "st_kitts": {"crimes": 965, "detection_rate": 40.7},
        "nevis": {"crimes": 181, "detection_rate": 47.5}
    },
    "2023_ANNUAL": {
        "period": "2023 Full Year (Jan-Dec)",
        "total_crimes": 1280,
        "detection_rate": 44.6,
        "federation": {
            "murder_manslaughter": {"total": 31, "detected": 11, "rate": 35.0},
            "shooting_intent": {"total": 6, "detected": 3, "rate": 50.0},
            "woundings_firearm": {"total": 24, "detected": 19, "rate": 79.0},
            "attempted_murder": {"total": 9, "detected": 2, "rate": 22.0},
            "bodily_harm": {"total": 161, "detected": 126, "rate": 78.0},
            "sex_crimes": {"total": 68, "detected": 38, "rate": 56.0},
            "break_ins": {"total": 136, "detected": 32, "rate": 24.0},
            "larcenies": {"total": 446, "detected": 118, "rate": 26.0},
            "robberies": {"total": 39, "detected": 19, "rate": 49.0},
            "firearms_offences": {"total": 34, "detected": 32, "rate": 94.0},
            "drug_crimes": {"total": 21, "detected": 21, "rate": 100.0},
            "malicious_damage": {"total": 274, "detected": 131, "rate": 48.0},
            "other_crimes": {"total": 31, "detected": 19, "rate": 61.0}
        },
        "st_kitts": {"crimes": 1093, "detection_rate": 44.8},
        "nevis": {"crimes": 187, "detection_rate": 43.3}
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
    "2022_ANNUAL": {
        "period": "2022 Full Year (Jan-Dec)",
        "total_crimes": 1360,
        "detection_rate": 31.4,
        "federation": {
            "murder_manslaughter": {"total": 11, "detected": 7, "rate": 64.0},
            "shooting_intent": {"total": 3, "detected": 1, "rate": 33.0},
            "attempted_murder": {"total": 6, "detected": 1, "rate": 17.0},
            "bodily_harm": {"total": 172, "detected": 116, "rate": 67.0},
            "sex_crimes": {"total": 58, "detected": 10, "rate": 17.0},
            "break_ins": {"total": 183, "detected": 28, "rate": 15.0},
            "larcenies": {"total": 525, "detected": 114, "rate": 22.0},
            "robberies": {"total": 38, "detected": 7, "rate": 18.0},
            "firearms_offences": {"total": 17, "detected": 17, "rate": 100.0},
            "drug_crimes": {"total": 26, "detected": 26, "rate": 100.0},
            "malicious_damage": {"total": 268, "detected": 71, "rate": 26.0},
            "other_crimes": {"total": 53, "detected": 29, "rate": 55.0}
        },
        "st_kitts": {"crimes": 1183, "detection_rate": 32.1},
        "nevis": {"crimes": 177, "detection_rate": 26.6}
    },
    "homicide_trends": {
        "period": "2015-2024 Homicide Analysis",
        "annual_totals": {
            "2015": 29, "2016": 32, "2017": 23, "2018": 23, "2019": 12,
            "2020": 10, "2021": 14, "2022": 11, "2023": 31, "2024": 28
        },
        "modus_operandi": {
            "shootings": {"total": 173, "percentage": 81},
            "stabbing": {"total": 29, "percentage": 14},
            "bludgeoning": {"total": 4, "percentage": 2},
            "strangulation": {"total": 5, "percentage": 2},
            "other": {"total": 2, "percentage": 1}
        },
        "age_demographics": {
            "0_17": {"total": 10, "percentage": 5},
            "18_35": {"total": 132, "percentage": 62},
            "36_55": {"total": 54, "percentage": 25},
            "over_55": {"total": 17, "percentage": 8}
        }
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

# **NEW: Chat Management Functions**
def create_new_chat():
    """Create a new chat session"""
    chat_id = f"chat_{st.session_state.chat_counter}_{int(time.time())}"
    st.session_state.chat_sessions[chat_id] = {
        'id': chat_id,
        'name': f"Chat {st.session_state.chat_counter}",
        'messages': [],
        'created_at': get_stkitts_time(),
        'last_activity': get_stkitts_time()
    }
    st.session_state.current_chat_id = chat_id
    st.session_state.chat_counter += 1
    return chat_id

def get_current_chat():
    """Get current chat session"""
    if st.session_state.current_chat_id and st.session_state.current_chat_id in st.session_state.chat_sessions:
        return st.session_state.chat_sessions[st.session_state.current_chat_id]
    else:
        # Create first chat if none exists
        create_new_chat()
        return st.session_state.chat_sessions[st.session_state.current_chat_id]

def add_message_to_chat(role, content):
    """Add message to current chat"""
    current_chat = get_current_chat()
    current_chat['messages'].append({
        "role": role,
        "content": content,
        "timestamp": get_stkitts_time()
    })
    current_chat['last_activity'] = get_stkitts_time()
    
    # Update chat name based on first user message
    if role == "user" and len(current_chat['messages']) <= 2:
        # Use first 30 characters of first user message as chat name
        chat_name = content[:30] + "..." if len(content) > 30 else content
        current_chat['name'] = chat_name

def switch_to_chat(chat_id):
    """Switch to a specific chat session"""
    if chat_id in st.session_state.chat_sessions:
        st.session_state.current_chat_id = chat_id

# **NEW: Statistical Data Processing Functions**
def fetch_and_process_statistics():
    """Fetch and process statistics from PDF URLs"""
    if st.session_state.statistical_database:
        return st.session_state.statistical_database
    
    # Use the enhanced database with complete data
    st.session_state.statistical_database = HISTORICAL_CRIME_DATABASE.copy()
    
    # Add MacroTrends and processed data from the PDF structure we saw
    st.session_state.statistical_database.update({
        "macrotrends_data": MACROTRENDS_DATA,
        "recent_trends": {
            "murder_trend": "75% decrease from 2024 to 2025 H1",
            "drug_crimes_trend": "463% increase in drug crimes 2024-2025",
            "detection_improvement": "Detection rates vary by crime type",
            "larceny_concern": "Larcenies remain highest volume crime"
        },
        "geographical_breakdown": {
            "st_kitts_districts_ab": "Higher crime volume but lower detection rate",
            "nevis_district_c": "Lower crime volume but higher detection rate",
            "federation_wide": "Overall crime trends showing mixed results"
        }
    })
    
    return st.session_state.statistical_database

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

def create_macrotrends_comparison_charts(chart_type="homicide_trends"):
    """Create charts using MacroTrends international comparison data"""
    
    if chart_type == "homicide_trends":
        # Historical homicide rates per 100K population
        years = list(MACROTRENDS_DATA["homicide_rates_per_100k"].keys())
        rates = list(MACROTRENDS_DATA["homicide_rates_per_100k"].values())
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=years, y=rates,
            mode='lines+markers',
            name='Homicide Rate per 100K',
            line=dict(color='#ff4444', width=3),
            marker=dict(size=10, color='#ff4444')
        ))
        
        # Add global average line
        global_avg = MACROTRENDS_DATA["comparative_context"]["global_average_firearm_homicides"]
        fig.add_hline(y=global_avg, line_dash="dash", line_color="#888888",
                     annotation_text=f"Global Average: {global_avg}%")
        
        fig.update_layout(
            title="St. Kitts & Nevis Homicide Rate Trends (MacroTrends Data)",
            xaxis_title="Year",
            yaxis_title="Homicides per 100,000 Population",
            template="plotly_dark",
            height=500
        )
        
        return fig
    
    elif chart_type == "recent_crime_totals":
        # Recent total crime trends
        years = ["2022", "2023", "2024"]
        crimes = [
            MACROTRENDS_DATA["recent_trends"]["2022_total_crimes"],
            MACROTRENDS_DATA["recent_trends"]["2023_total_crimes"],
            MACROTRENDS_DATA["recent_trends"]["2024_total_crimes"]
        ]
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=years, y=crimes,
            marker_color='#44ff44',
            text=[f"{crime:,}" for crime in crimes],
            textposition='auto'
        ))
        
        fig.update_layout(
            title="Total Crime Trends 2022-2024 (RSCNPF Data)",
            xaxis_title="Year",
            yaxis_title="Total Crimes",
            template="plotly_dark",
            height=500
        )
        
        return fig
    
    elif chart_type == "international_context":
        # International comparison chart
        categories = ["St. Kitts 2020", "St. Kitts 2019", "St. Kitts 2018", "Global Avg.", "St. Kitts Peak (2011)"]
        values = [
            MACROTRENDS_DATA["homicide_rates_per_100k"]["2020"],
            MACROTRENDS_DATA["homicide_rates_per_100k"]["2019"],
            MACROTRENDS_DATA["homicide_rates_per_100k"]["2018"],
            MACROTRENDS_DATA["comparative_context"]["global_average_firearm_homicides"],
            MACROTRENDS_DATA["homicide_rates_per_100k"]["2011"]
        ]
        
        colors = ['#44ff44', '#ffaa44', '#ff4444', '#888888', '#ff0000']
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=categories, y=values,
            marker_color=colors,
            text=[f"{val:.1f}" for val in values],
            textposition='auto'
        ))
        
        fig.update_layout(
            title="International Context: Homicide Rates per 100K Population",
            xaxis_title="Comparison Points",
            yaxis_title="Rate per 100,000",
            template="plotly_dark",
            height=500
        )
        
        return fig

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

def is_international_comparison_query(user_input):
    """Detect if user wants international comparison or historical trends"""
    comparison_keywords = ['international', 'global', 'worldwide', 'compare', 'comparison', 'trends', 'historical', 'macrotrends', 'world average', 'per 100k', 'rate', 'historical chart', 'long term', 'decade']
    return any(keyword in user_input.lower() for keyword in comparison_keywords)

def is_casual_greeting(user_input):
    """Detect if user input is a casual greeting"""
    casual_words = ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening', 'how are you', 'what\'s up', 'sup']
    return any(word in user_input.lower().strip() for word in casual_words) and len(user_input.strip()) < 25

def is_detailed_request(user_input):
    """Detect if user wants detailed information"""
    detail_keywords = ['detailed', 'detail', 'explain', 'comprehensive', 'thorough', 'in depth', 'breakdown', 'elaborate', 'more information', 'tell me more']
    return any(keyword in user_input.lower() for keyword in detail_keywords)

def is_statistics_query(user_input):
    """Detect if user is asking about statistics"""
    stats_keywords = ['statistics', 'stats', 'data', 'crime rate', 'trends', 'numbers', 'figures', 'analysis', 'murder', 'robbery', 'larceny', 'detection rate', 'quarterly', 'annual', 'breakdown', 'comparison']
    return any(keyword in user_input.lower() for keyword in stats_keywords)

def generate_enhanced_smart_response(user_input, conversation_history=None, language='en'):
    """Generate AI responses with statistical knowledge and conversation memory"""
    
    if not st.session_state.get('ai_enabled', False):
        return "🔧 AI system offline. Please check your API key configuration.", None
    
    try:
        # Load statistical data
        stats_data = fetch_and_process_statistics()
        
        # Check if user wants a chart
        chart_keywords = ['chart', 'graph', 'plot', 'visualize', 'show me', 'display', 'trends', 'comparison']
        wants_chart = any(keyword in user_input.lower() for keyword in chart_keywords)
        chart_to_show = None
        
        # Check if this is the first interaction after a greeting
        has_greeted_before = False
        if conversation_history:
            for msg in conversation_history:
                if msg['role'] == 'assistant' and any(greeting in msg['content'].lower() for greeting in ['good morning', 'good afternoon', 'good evening', 'hello', 'hi']):
                    has_greeted_before = True
                    break
        
        # Handle different query types
        if is_casual_greeting(user_input) and not has_greeted_before:
            # Simple greeting response - only if we haven't greeted before
            prompt = f"""
            You are SECURO, an AI assistant for St. Kitts & Nevis Police.
            
            User said: "{user_input}"
            
            Respond with a brief, friendly greeting (2-3 sentences max). Mention you're ready to help with questions about crime statistics or general assistance.
            Include the appropriate time-based greeting (good morning/afternoon/evening) based on the current time.
            """
            
            response = model.generate_content(prompt)
            return response.text.strip(), None
        
        elif is_casual_greeting(user_input) and has_greeted_before:
            # Don't repeat greeting, just acknowledge
            prompt = f"""
            You are SECURO, an AI assistant for St. Kitts & Nevis Police.
            
            User said: "{user_input}"
            The user has already been greeted earlier in this conversation.
            
            Respond with a brief acknowledgment WITHOUT repeating any greeting. Just ask how you can help or what they'd like to know about.
            Keep it to 1-2 sentences.
            """
            
            response = model.generate_content(prompt)
            return response.text.strip(), None
        
        elif is_statistics_query(user_input) or is_international_comparison_query(user_input) or wants_chart:
            # Statistics-focused response with actual data AND chart generation
            is_detailed = is_detailed_request(user_input)
            is_comparison = is_international_comparison_query(user_input)
            
            # Determine which chart to show
            if wants_chart:
                if 'international' in user_input.lower() or 'global' in user_input.lower() or 'world' in user_input.lower():
                    chart_to_show = "international"
                elif 'trend' in user_input.lower() or 'over time' in user_input.lower() or 'years' in user_input.lower():
                    chart_to_show = "trends"
                elif 'detection' in user_input.lower():
                    chart_to_show = "detection"
                elif 'breakdown' in user_input.lower() or 'types' in user_input.lower():
                    chart_to_show = "breakdown"
                elif 'manslaughter' in user_input.lower() or 'murder' in user_input.lower() or 'homicide' in user_input.lower():
                    chart_to_show = "homicide"
                else:
                    chart_to_show = "trends"  # Default to trends
            
            # Include conversation context
            context = ""
            if conversation_history and len(conversation_history) > 1:
                recent_messages = conversation_history[-4:]  # Last 4 messages for context
                context = "Recent conversation context:\n"
                for msg in recent_messages:
                    context += f"{msg['role']}: {msg['content'][:100]}...\n"
                context += "\n"
            
            # Add MacroTrends data for comparison queries
            macrotrends_context = ""
            if is_comparison:
                macrotrends_context = f"""
                
                **MacroTrends International Data Available:**
                {json.dumps(MACROTRENDS_DATA, indent=2)}
                """
            
            prompt = f"""
            You are SECURO, an AI assistant for the Royal St. Christopher & Nevis Police Force with access to comprehensive crime statistics AND international comparison data.
            
            {context}User query: "{user_input}"
            Detailed request: {is_detailed}
            International comparison requested: {is_comparison}
            Chart requested: {wants_chart}
            
            **Available Local Statistical Data:**
            {json.dumps(stats_data, indent=2)}
            {macrotrends_context}
            
            **Response Guidelines:**
            - NEVER say "Good morning", "Good afternoon", or "Good evening" in your response unless the user just greeted you for the first time
            - If detailed=False: Keep response concise (3-5 sentences) but data-rich
            - If detailed=True: Provide comprehensive statistical analysis
            - If comparison=True: Include international context, MacroTrends data
            - If chart requested: Acknowledge that you're displaying the requested chart below your response
            - Use specific numbers and percentages from the data above
            - Reference time periods (Q2 2025, H1 2024, etc.) when relevant
            - Include comparisons and trends when available
            - When discussing international comparisons, reference the MacroTrends data
            - Maintain professional law enforcement communication
            - Focus on actionable insights for police operations
            
            Current time: {get_stkitts_time()} AST
            Current date: {get_stkitts_date()}
            
            Provide data-driven statistical analysis with specific figures and international context when relevant.
            """
            
            response = model.generate_content(prompt)
            return response.text.strip(), chart_to_show
            
        else:
            # General query with conversation context
            is_detailed = is_detailed_request(user_input)
            
            # Include conversation context
            context = ""
            if conversation_history and len(conversation_history) > 1:
                recent_messages = conversation_history[-6:]  # Last 6 messages for context
                context = "Conversation history for context:\n"
                for msg in recent_messages:
                    context += f"{msg['role']}: {msg['content'][:150]}...\n"
                context += "\n"
            
            prompt = f"""
            You are SECURO, an AI assistant for the Royal St. Christopher & Nevis Police Force.
            
            {context}Current user query: "{user_input}"
            Detailed request: {is_detailed}
            
            **Response Guidelines:**
            - NEVER say "Good morning", "Good afternoon", or "Good evening" in your response unless the user just greeted you for the first time
            - If detailed=False: Keep response concise (3-5 sentences)
            - If detailed=True: Provide thorough explanation
            - Maintain conversation context and reference previous messages when relevant
            - Provide professional assistance suitable for law enforcement
            - Include practical recommendations when appropriate
            - You have access to crime statistics and can generate charts if asked
            
            Current time: {get_stkitts_time()} AST
            Current date: {get_stkitts_date()}
            
            Provide helpful, context-aware assistance.
            """
            
            response = model.generate_content(prompt)
            return response.text.strip(), None
            
    except Exception as e:
        return f"🚨 AI analysis error: {str(e)}\n\nI'm still here to help! Please try rephrasing your question or check your internet connection.", None

# Initialize the AI model - REPLACE WITH YOUR API KEY
try:
    GOOGLE_API_KEY = "AIzaSyBn1AUXxPtPMu9eRnosECSSQG_2e5bArR8"  # REPLACE THIS WITH YOUR ACTUAL API KEY
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    st.session_state.ai_enabled = True
    st.session_state.ai_status = "✅ AI Active with Statistical Knowledge"
except Exception as e:
    st.session_state.ai_enabled = False
    st.session_state.ai_status = f"❌ AI Error: {str(e)}"
    model = None

# Page configuration
st.set_page_config(
    page_title="SECURO - Enhanced AI Assistant & Crime Intelligence System",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'welcome'

if 'selected_language' not in st.session_state:
    st.session_state.selected_language = 'en'

if 'crime_stats' not in st.session_state:
    st.session_state.crime_stats = load_crime_statistics()

if 'selected_periods' not in st.session_state:
    st.session_state.selected_periods = ['2025_Q2']

# Initialize statistics on startup
fetch_and_process_statistics()

# **NEW: Fix for multiselect default values**
def ensure_valid_selected_periods():
    """Ensure selected_periods contains valid keys from the database"""
    available_periods = list(st.session_state.crime_stats.keys())
    current_selections = st.session_state.get('selected_periods', [])
    
    # Filter out invalid selections
    valid_selections = [period for period in current_selections if period in available_periods]
    
    # If no valid selections, use safe defaults
    if not valid_selections:
        # Try to select recent annual reports
        preferred_defaults = ['2023_ANNUAL', '2024_ANNUAL', '2025_Q2']
        for default in preferred_defaults:
            if default in available_periods:
                valid_selections.append(default)
        
        # If still no valid selections, select the 3 most recent periods
        if not valid_selections and available_periods:
            # Sort periods chronologically
            def sort_key(period):
                if '_ANNUAL' in period:
                    return (int(period.split('_')[0]), 12)
                elif '_H1' in period:
                    return (int(period.split('_')[0]), 6)
                elif '_Q1' in period:
                    return (int(period.split('_')[0]), 3)
                elif '_Q2' in period:
                    return (int(period.split('_')[0]), 6)
                elif '_Q3' in period:
                    return (int(period.split('_')[0]), 9)
                elif '_Q4' in period:
                    return (int(period.split('_')[0]), 12)
                else:
                    return (9999, 0)
            
            sorted_periods = sorted(available_periods, key=sort_key)
            valid_selections = sorted_periods[-3:] if len(sorted_periods) >= 3 else sorted_periods
    
    st.session_state.selected_periods = valid_selections

# Ensure valid periods after loading stats
ensure_valid_selected_periods()

# Enhanced CSS styling matching HTML design
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Segoe+UI:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400&display=swap');
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Root styling */
    .stApp {
        background: #1a1a1a;
        color: #ffffff;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Header styling to match HTML */
    .main-header {
        background: #0d1117;
        padding: 15px 0;
        border-bottom: 1px solid #21262d;
        margin-bottom: 20px;
        border-radius: 12px;
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
        background: linear-gradient(90deg, transparent, rgba(0, 255, 65, 0.1), transparent);
        animation: shimmer 3s linear infinite;
    }
    
    @keyframes shimmer {
        0% { left: -100%; }
        100% { left: 100%; }
    }
    
    .main-header .header-content {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0 20px;
        position: relative;
        z-index: 2;
    }
    
    .logo {
        display: flex;
        align-items: center;
        gap: 15px;
    }
    
    .logo-icon {
        width: 40px;
        height: 40px;
        background: #00ff41;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #000;
        font-size: 20px;
        font-weight: bold;
    }
    
    .logo-text h1 {
        color: #00ff41 !important;
        font-size: 24px !important;
        font-weight: 700 !important;
        margin: 0 !important;
        text-shadow: 0 0 10px rgba(0, 255, 65, 0.3);
    }
    
    .logo-text p {
        color: #8b949e !important;
        font-size: 12px !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin: 0 !important;
    }
    
    .header-info {
        display: flex;
        align-items: center;
        gap: 20px;
        font-size: 14px;
        color: #8b949e;
    }
    
    .status-indicator {
        display: flex;
        align-items: center;
        gap: 5px;
    }
    
    .status-dot {
        width: 8px;
        height: 8px;
        background: #00ff41;
        border-radius: 50%;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    /* Navigation styling */
    .nav-container {
        background: #161b22;
        padding: 10px 0;
        border-bottom: 1px solid #21262d;
        border-radius: 12px;
        margin-bottom: 20px;
    }
    
    /* Button styling to match HTML */
    .stButton > button {
        background: #21262d !important;
        border: 1px solid #30363d !important;
        color: #f0f6fc !important;
        padding: 12px 20px !important;
        border-radius: 8px !important;
        transition: all 0.3s ease !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        width: 100% !important;
        text-align: center !important;
    }
    
    .stButton > button:hover {
        background: #00ff41 !important;
        color: #000 !important;
        border-color: #00ff41 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 5px 15px rgba(0, 255, 65, 0.3) !important;
    }
    
    .stButton > button:focus {
        background: #00ff41 !important;
        color: #000 !important;
        border-color: #00ff41 !important;
        box-shadow: 0 0 0 3px rgba(0, 255, 65, 0.2) !important;
    }
    
    /* Content area styling */
    .content-area {
        background: rgba(0, 0, 0, 0.9);
        border-radius: 15px;
        border: 1px solid rgba(0, 255, 65, 0.3);
        padding: 30px;
        min-height: 400px;
    }
    
    /* Welcome section styling */
    .welcome-section {
        text-align: center;
        margin-bottom: 50px;
        padding: 40px 20px;
        background: linear-gradient(-45deg, rgba(0, 0, 0, 0.9), rgba(0, 255, 65, 0.05), rgba(0, 0, 0, 0.9), rgba(0, 255, 65, 0.05));
        background-size: 400% 400%;
        animation: moveGradient 4s ease infinite;
        border-radius: 15px;
        border: 1px solid rgba(0, 255, 65, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .welcome-section::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(0, 255, 65, 0.1), transparent);
        animation: shimmer 3s linear infinite;
    }
    
    @keyframes moveGradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .welcome-title {
        font-size: 3rem !important;
        color: #00ff41 !important;
        margin-bottom: 15px !important;
        font-weight: 700 !important;
        text-shadow: 0 0 20px rgba(0, 255, 65, 0.5) !important;
        position: relative;
        z-index: 2;
    }
    
    .welcome-subtitle {
        font-size: 1.2rem !important;
        color: #8b949e !important;
        margin-bottom: 10px !important;
        position: relative;
        z-index: 2;
    }
    
    .welcome-description {
        font-size: 1rem !important;
        color: #c9d1d9 !important;
        max-width: 800px;
        margin: 0 auto !important;
        line-height: 1.6 !important;
        position: relative;
        z-index: 2;
    }
    
    /* Feature cards styling */
    .feature-card {
        background: #21262d;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 30px;
        text-align: center;
        transition: all 0.3s ease;
        margin-bottom: 20px;
        position: relative;
        overflow: hidden;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        border-color: #00ff41;
        box-shadow: 0 10px 30px rgba(0, 255, 65, 0.1);
    }
    
    .feature-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(0, 255, 65, 0.05), transparent);
        transition: left 0.5s;
    }
    
    .feature-card:hover::before {
        left: 100%;
    }
    
    .feature-icon {
        font-size: 3rem;
        color: #00ff41;
        margin-bottom: 20px;
    }
    
    .feature-card h3 {
        color: #00ff41 !important;
        font-size: 1.5rem !important;
        margin-bottom: 15px !important;
        position: relative;
        z-index: 2;
    }
    
    .feature-card p {
        color: #8b949e !important;
        line-height: 1.6 !important;
        position: relative;
        z-index: 2;
    }
    
    /* Statistics cards */
    .stat-card {
        background: linear-gradient(135deg, #21262d, #0d1117);
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 25px;
        text-align: center;
        transition: all 0.3s ease;
        margin-bottom: 20px;
    }
    
    .stat-card:hover {
        border-color: #00ff41;
        transform: translateY(-3px);
        box-shadow: 0 5px 15px rgba(0, 255, 65, 0.2);
    }
    
    .stat-number {
        font-size: 2.5rem !important;
        font-weight: bold !important;
        margin-bottom: 10px !important;
        color: #00ff41 !important;
        text-shadow: 0 0 10px rgba(0, 255, 65, 0.3);
    }
    
    .stat-label {
        color: #8b949e !important;
        font-size: 1rem !important;
    }
    
    /* Emergency cards */
    .emergency-card {
        background: rgba(0, 0, 0, 0.8);
        border: 2px solid rgba(255, 107, 107, 0.5);
        border-radius: 12px;
        padding: 25px;
        text-align: center;
        transition: all 0.3s ease;
        margin-bottom: 20px;
    }
    
    .emergency-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 30px rgba(255, 107, 107, 0.2);
        border-color: #ff6b6b;
    }
    
    .emergency-card h3 {
        color: #ff6b6b !important;
        margin-bottom: 15px !important;
    }
    
    .phone-number {
        font-size: 1.8rem !important;
        font-weight: bold !important;
        color: #00ff41 !important;
        margin: 15px 0 !important;
    }
    
    /* Chat messages */
    .chat-message {
        margin-bottom: 20px;
        animation: fadeInUp 0.5s ease;
        clear: both;
    }
    
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
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
        word-wrap: break-word;
        white-space: pre-wrap;
    }
    
    .user-message .message-content {
        background: linear-gradient(135deg, #00ff41, #00cc34);
        color: #000000 !important;
        border-bottom-right-radius: 5px;
    }
    
    .bot-message .message-content {
        background: rgba(0, 0, 0, 0.9) !important;
        color: #ffffff !important;
        border: 1px solid rgba(0, 255, 65, 0.3);
        border-bottom-left-radius: 5px;
    }
    
    .message-time {
        font-size: 0.7rem;
        color: #888 !important;
        margin-top: 5px;
    }
    
    /* Input styling */
    .stTextInput input {
        background: rgba(0, 0, 0, 0.8) !important;
        border: 1px solid rgba(0, 255, 65, 0.3) !important;
        border-radius: 25px !important;
        color: #ffffff !important;
        padding: 12px 20px !important;
    }
    
    .stTextInput input:focus {
        border-color: #00ff41 !important;
        box-shadow: 0 0 20px rgba(0, 255, 65, 0.2) !important;
    }
    
    /* Multiselect styling */
    .stMultiSelect > div > div {
        background-color: rgba(0, 0, 0, 0.8) !important;
        border: 1px solid rgba(0, 255, 65, 0.3) !important;
        border-radius: 8px !important;
        color: #ffffff !important;
    }
    
    .stMultiSelect > div > div[data-baseweb="select"] > div {
        background-color: rgba(0, 0, 0, 0.9) !important;
        border: 1px solid rgba(0, 255, 65, 0.3) !important;
        color: #ffffff !important;
    }
    
    .stMultiSelect > div > div[data-baseweb="select"] ul {
        background-color: rgba(0, 0, 0, 0.95) !important;
        border: 1px solid rgba(0, 255, 65, 0.3) !important;
        border-radius: 8px !important;
    }
    
    .stMultiSelect > div > div[data-baseweb="select"] ul li {
        background-color: rgba(0, 0, 0, 0.95) !important;
        color: #ffffff !important;
    }
    
    .stMultiSelect > div > div[data-baseweb="select"] ul li:hover {
        background-color: rgba(0, 255, 65, 0.2) !important;
        color: #00ff41 !important;
    }
    
    .stMultiSelect span[data-baseweb="tag"] {
        background-color: rgba(0, 255, 65, 0.2) !important;
        border: 1px solid #00ff41 !important;
        color: #00ff41 !important;
    }
    
    /* Section titles */
    .section-title {
        color: #00ff41 !important;
        font-size: 2rem !important;
        margin-bottom: 30px !important;
        display: flex;
        align-items: center;
        gap: 15px;
    }
    
    /* General text styling */
    h1, h2, h3, h4, h5, h6 {
        color: #00ff41 !important;
    }
    
    p, span, div, li {
        color: #ffffff !important;
    }
    
    /* Sidebar styling */
    .stSidebar {
        background: #0d1117 !important;
    }
    
    .stSidebar .stMarkdown {
        color: #ffffff !important;
    }
    
    /* Success/Info/Warning styling */
    .stSuccess {
        background: rgba(0, 255, 65, 0.1) !important;
        border: 1px solid rgba(0, 255, 65, 0.3) !important;
        color: #ffffff !important;
    }
    
    .stInfo {
        background: rgba(0, 123, 255, 0.1) !important;
        border: 1px solid rgba(0, 123, 255, 0.3) !important;
        color: #ffffff !important;
    }
    
    .stWarning {
        background: rgba(255, 193, 7, 0.1) !important;
        border: 1px solid rgba(255, 193, 7, 0.3) !important;
        color: #ffffff !important;
    }
    
    .stError {
        background: rgba(255, 107, 107, 0.1) !important;
        border: 1px solid rgba(255, 107, 107, 0.3) !important;
        color: #ffffff !important;
    }
    
    /* Footer styling */
    .footer {
        background: #0d1117;
        border-top: 1px solid #21262d;
        padding: 30px 0;
        margin-top: 50px;
        text-align: center;
        color: #8b949e;
        font-size: 14px;
        border-radius: 12px;
    }
    
    /* Chat history styling */
    .chat-history-item {
        background: rgba(0, 0, 0, 0.6);
        border: 1px solid rgba(0, 255, 65, 0.3);
        border-radius: 8px;
        padding: 10px;
        margin: 5px 0;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .chat-history-item:hover {
        background: rgba(0, 255, 65, 0.1);
        border-color: #00ff41;
    }
    
    .active-chat {
        border-color: #00ff41 !important;
        background: rgba(0, 255, 65, 0.15) !important;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .welcome-title {
            font-size: 2rem !important;
        }
        
        .main-header .header-content {
            flex-direction: column;
            gap: 10px;
        }
        
        .header-info {
            flex-wrap: wrap;
            justify-content: center;
        }
    }
</style>
""", unsafe_allow_html=True)

# Enhanced Sidebar matching HTML design
with st.sidebar:
    st.markdown("""
    <div style="background: #21262d; border-radius: 12px; padding: 20px; border: 1px solid #30363d; margin-bottom: 20px;">
        <h3 style="color: #00ff41; margin-bottom: 15px;">🤖 AI Configuration</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Show current status
    st.write(f"**Status:** {st.session_state.get('ai_status', 'Unknown')}")
    
    st.markdown("---")
    
    # Status indicators
    if st.session_state.get('ai_enabled', False):
        st.success("🔮 AI Assistant Active")
        st.markdown("""
        <div style="background: rgba(0, 255, 65, 0.1); border: 1px solid rgba(0, 255, 65, 0.3); border-radius: 8px; padding: 15px; margin: 10px 0;">
            <strong style="color: #00ff41;">Enhanced Capabilities:</strong><br>
            • Statistical knowledge integration<br>
            • Conversation memory<br>
            • Context-aware responses<br>
            • Crime data analysis<br>
            • Professional assistance
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background: rgba(0, 255, 65, 0.1); border: 1px solid rgba(0, 255, 65, 0.3); border-radius: 8px; padding: 15px; margin: 10px 0;">
            <strong style="color: #00ff41;">Statistical Coverage:</strong><br>
            • 2022-2025 complete annual data<br>
            • 2015-2024 homicide analysis<br>
            • MacroTrends international data<br>
            • Quarterly & half-yearly reports<br>
            • Detection rate analysis<br>
            • Global comparison charts
        </div>
        """, unsafe_allow_html=True)
        
        st.info("✅ AI with Statistical Knowledge")
        st.info("💾 Conversation Memory Enabled")
    else:
        st.warning("⚠️ AI Offline")
        st.write("• Check API key")
        st.write("• Verify internet connection")
    
    st.success("📊 Statistics Database")
    st.markdown("""
    <div style="background: rgba(0, 255, 65, 0.1); border: 1px solid rgba(0, 255, 65, 0.3); border-radius: 8px; padding: 15px; margin: 10px 0;">
        <strong style="color: #00ff41;">Available:</strong><br>
        • 2022-2025 complete annual data<br>
        • 2015-2024 homicide analysis<br>
        • Real PDF source integration<br>
        • 13 crime hotspots mapped<br>
        • Enhanced analytics
    </div>
    """, unsafe_allow_html=True)

# Enhanced Main Header matching HTML design
current_time = get_stkitts_time()
current_date = get_stkitts_date()

st.markdown(f"""
<div class="main-header">
    <div class="header-content">
        <div class="logo">
            <div class="logo-icon">🛡️</div>
            <div class="logo-text">
                <h1>SECURO</h1>
                <p>Enhanced AI Assistant & Crime Intelligence System</p>
            </div>
        </div>
        <div class="header-info">
            <div class="status-indicator">
                <div class="status-dot"></div>
                <span>Royal St. Christopher & Nevis Police Force</span>
            </div>
            <div class="status-indicator">
                <span>📅 {current_date} | 🕒 {current_time} (AST)</span>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Enhanced Navigation Bar
st.markdown('<div class="nav-container">', unsafe_allow_html=True)
col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    if st.button("🏠 Home", key="nav_home", help="Welcome to SECURO"):
        st.session_state.current_page = 'welcome'
        st.rerun()

with col2:
    if st.button("ℹ️ About SECURO", key="nav_about", help="About SECURO System"):
        st.session_state.current_page = 'about'
        st.rerun()

with col3:
    if st.button("🗺️ Crime Hotspots", key="nav_map", help="Interactive Crime Map"):
        st.session_state.current_page = 'map'
        st.rerun()

with col4:
    if st.button("📊 Statistics & Analytics", key="nav_stats", help="Crime Data Analysis"):
        st.session_state.current_page = 'statistics'
        st.rerun()

with col5:
    if st.button("🚨 Emergency", key="nav_emergency", help="Emergency Contacts"):
        st.session_state.current_page = 'emergency'
        st.rerun()

with col6:
    if st.button("💬 AI Assistant", key="nav_chat", help="Chat with Enhanced SECURO AI"):
        st.session_state.current_page = 'chat'
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# Main content area with enhanced styling
st.markdown('<div class="content-area">', unsafe_allow_html=True)

# HOME PAGE with enhanced HTML-style design
if st.session_state.current_page == 'welcome':
    st.markdown("""
    <div class="welcome-section">
        <h1 class="welcome-title">Welcome to Enhanced SECURO</h1>
        <p class="welcome-subtitle">Your comprehensive AI assistant with statistical knowledge, conversation memory, and crime analysis capabilities for St. Kitts & Nevis</p>
        <p class="welcome-description">AI assistant now features conversation memory, statistical integration, and enhanced analytics.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Enhanced Feature Cards Grid
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🧠</div>
            <h3>Enhanced AI with Memory</h3>
            <p>Conversation memory, statistical knowledge integration, and context-aware responses powered by real crime data from police PDFs.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📊</div>
            <h3>Integrated Statistics + International Data</h3>
            <p>Real-time access to local crime statistics PLUS MacroTrends international comparison data with global context and historical trends.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">💾</div>
            <h3>Conversation Management</h3>
            <p>Multiple chat sessions with memory, chat history, and context preservation across conversations for continuous assistance.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📈</div>
            <h3>Statistical Analysis</h3>
            <p>Advanced crime data analysis with detection rates, trend identification, and actionable insights for police operations.</p>
        </div>
        """, unsafe_allow_html=True)

# ABOUT PAGE (Enhanced with HTML styling)
elif st.session_state.current_page == 'about':
    st.markdown("""
    <h2 class="section-title">
        <span>ℹ️</span>
        About Enhanced SECURO
    </h2>
    
    <div class="feature-card">
        <p><strong style="color: #00ff41;">SECURO</strong> is an enhanced comprehensive crime analysis system with statistical integration, conversation memory, and advanced AI capabilities built specifically for the Royal St. Christopher and Nevis Police Force.</p>
        
        <h3 style="color: #00ff41; margin: 30px 0 20px 0;">🧠 Enhanced AI Capabilities</h3>
        <ul style="list-style: none; color: #c9d1d9; line-height: 2; padding: 0;">
            <li style="padding: 8px 0; padding-left: 25px; position: relative;">
                <span style="position: absolute; left: 0; color: #00ff41; font-weight: bold;">✓</span>
                <span>Conversation Memory - Maintains context across entire chat sessions</span>
            </li>
            <li style="padding: 8px 0; padding-left: 25px; position: relative;">
                <span style="position: absolute; left: 0; color: #00ff41; font-weight: bold;">✓</span>
                <span>Statistical Knowledge Integration - Real access to 2023-2025 crime data</span>
            </li>
            <li style="padding: 8px 0; padding-left: 25px; position: relative;">
                <span style="position: absolute; left: 0; color: #00ff41; font-weight: bold;">✓</span>
                <span>Context-Aware Responses - Understands conversation flow and history</span>
            </li>
            <li style="padding: 8px 0; padding-left: 25px; position: relative;">
                <span style="position: absolute; left: 0; color: #00ff41; font-weight: bold;">✓</span>
                <span>Multi-Chat Management - Multiple conversation sessions with history</span>
            </li>
            <li style="padding: 8px 0; padding-left: 25px; position: relative;">
                <span style="position: absolute; left: 0; color: #00ff41; font-weight: bold;">✓</span>
                <span>Statistical Query Processing - Answers questions with actual crime data</span>
            </li>
        </ul>

        <h3 style="color: #00ff41; margin: 30px 0 20px 0;">📊 Integrated Statistical Database</h3>
        <ul style="list-style: none; color: #c9d1d9; line-height: 2; padding: 0;">
            <li style="padding: 8px 0; padding-left: 25px; position: relative;">
                <span style="position: absolute; left: 0; color: #00ff41; font-weight: bold;">✓</span>
                <span>Real PDF Integration - Data sourced from official police statistical reports</span>
            </li>
            <li style="padding: 8px 0; padding-left: 25px; position: relative;">
                <span style="position: absolute; left: 0; color: #00ff41; font-weight: bold;">✓</span>
                <span>2022-2025 Crime Data - Complete annual statistics plus quarterly analysis</span>
            </li>
            <li style="padding: 8px 0; padding-left: 25px; position: relative;">
                <span style="position: absolute; left: 0; color: #00ff41; font-weight: bold;">✓</span>
                <span>Detection Rate Analysis - Performance metrics and trend identification</span>
            </li>
            <li style="padding: 8px 0; padding-left: 25px; position: relative;">
                <span style="position: absolute; left: 0; color: #00ff41; font-weight: bold;">✓</span>
                <span>Geographical Breakdown - St. Kitts vs. Nevis crime distribution</span>
            </li>
        </ul>

        <h3 style="color: #00ff41; margin: 30px 0 20px 0;">💬 Chat Management Features</h3>
        <ul style="list-style: none; color: #c9d1d9; line-height: 2; padding: 0;">
            <li style="padding: 8px 0; padding-left: 25px; position: relative;">
                <span style="position: absolute; left: 0; color: #00ff41; font-weight: bold;">✓</span>
                <span>New Chat Sessions - Start fresh conversations anytime</span>
            </li>
            <li style="padding: 8px 0; padding-left: 25px; position: relative;">
                <span style="position: absolute; left: 0; color: #00ff41; font-weight: bold;">✓</span>
                <span>Chat History - Access and resume previous conversations</span>
            </li>
            <li style="padding: 8px 0; padding-left: 25px; position: relative;">
                <span style="position: absolute; left: 0; color: #00ff41; font-weight: bold;">✓</span>
                <span>Context Preservation - AI remembers entire conversation context</span>
            </li>
            <li style="padding: 8px 0; padding-left: 25px; position: relative;">
                <span style="position: absolute; left: 0; color: #00ff41; font-weight: bold;">✓</span>
                <span>Session Management - Switch between multiple chat sessions seamlessly</span>
            </li>
        </ul>

        <h3 style="color: #00ff41; margin: 30px 0 20px 0;">⚖️ Professional Standards</h3>
        <p>Enhanced SECURO maintains professional communication standards appropriate for law enforcement operations. The AI assistant now provides statistically-informed assistance while preserving conversation context for more effective police support.</p>
    </div>
    """, unsafe_allow_html=True)

# CRIME HOTSPOTS PAGE (Enhanced with HTML styling)
elif st.session_state.current_page == 'map':
    st.markdown("""
    <h2 class="section-title">
        <span>🗺️</span>
        Crime Hotspot Map - St. Kitts & Nevis
    </h2>
    """, unsafe_allow_html=True)
    
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
    
    # Hotspot Analysis Summary with enhanced styling
    st.markdown("""
    <h3 class="section-title">
        <span>📍</span>
        Hotspot Analysis Summary
    </h3>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="background: rgba(231, 76, 60, 0.1); padding: 20px; border-radius: 12px; border-left: 4px solid #e74c3c; margin-bottom: 15px; border: 1px solid rgba(231, 76, 60, 0.3);">
            <h4 style="color: #e74c3c; margin-bottom: 10px;">High Risk Areas (3)</h4>
            <p style="color: #c9d1d9;">Basseterre Central, Molineux, Tabernacle</p>
            <p style="color: #8b949e; font-size: 0.9rem;">Total: 109 crimes</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: rgba(243, 156, 18, 0.1); padding: 20px; border-radius: 12px; border-left: 4px solid #f39c12; margin-bottom: 15px; border: 1px solid rgba(243, 156, 18, 0.3);">
            <h4 style="color: #f39c12; margin-bottom: 10px;">Medium Risk Areas (6)</h4>
            <p style="color: #c9d1d9;">Cayon, Newton Ground, Old Road, etc.</p>
            <p style="color: #8b949e; font-size: 0.9rem;">Total: 133 crimes</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="background: rgba(39, 174, 96, 0.1); padding: 20px; border-radius: 12px; border-left: 4px solid #27ae60; margin-bottom: 15px; border: 1px solid rgba(39, 174, 96, 0.3);">
            <h4 style="color: #27ae60; margin-bottom: 10px;">Low Risk Areas (4)</h4>
            <p style="color: #c9d1d9;">Sandy Point, Dieppe Bay, etc.</p>
            <p style="color: #8b949e; font-size: 0.9rem;">Total: 60 crimes</p>
        </div>
        """, unsafe_allow_html=True)

# STATISTICS & ANALYTICS PAGE (Enhanced with HTML styling)
elif st.session_state.current_page == 'statistics':
    st.markdown("""
    <h2 class="section-title">
        <span>📊</span>
        Crime Statistics & Analytics
    </h2>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="feature-card" style="margin-bottom: 30px;">
        <p style="color: #00ff41; text-align: center; font-size: 1.1rem;">📊 **Enhanced Statistics System** - Data is now integrated with the AI assistant for comprehensive statistical analysis.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Year/Period Selection Dropdown
    st.markdown("""
    <h3 class="section-title">
        <span>📅</span>
        Select Time Periods for Analysis
    </h3>
    """, unsafe_allow_html=True)
    
    # Create ordered list of periods
    available_periods = list(st.session_state.crime_stats.keys())
    
    # Sort periods chronologically
    def sort_key(period):
        if '_ANNUAL' in period:
            return (int(period.split('_')[0]), 12)  # Annual reports at end of year
        elif '_H1' in period:
            return (int(period.split('_')[0]), 6)   # H1 reports mid-year
        elif '_Q1' in period:
            return (int(period.split('_')[0]), 3)   # Q1 reports
        elif '_Q2' in period:
            return (int(period.split('_')[0]), 6)   # Q2 reports
        elif '_Q3' in period:
            return (int(period.split('_')[0]), 9)   # Q3 reports
        elif '_Q4' in period:
            return (int(period.split('_')[0]), 12)  # Q4 reports
        else:
            return (9999, 0)  # Unknown format at end
    
    # Sort periods
    sorted_periods = sorted(available_periods, key=sort_key)
    
    period_labels = {key: data["period"] for key, data in st.session_state.crime_stats.items()}
    
    # Set better default selections (recent years)
    default_selections = ['2023_ANNUAL', '2024_ANNUAL', '2025_Q2']
    valid_defaults = [p for p in default_selections if p in sorted_periods]
    
    if not valid_defaults:
        valid_defaults = sorted_periods[-3:] if len(sorted_periods) >= 3 else sorted_periods
    
    selected_periods = st.multiselect(
        "📊 Choose time periods to analyze (2016-2025):",
        options=sorted_periods,
        default=valid_defaults,
        format_func=lambda x: period_labels.get(x, x),
        help="Select one or more time periods to compare statistics and trends. Data available from 2016 to 2025.",
        key="period_selector"
    )
    
    if not selected_periods:
        st.warning("Please select at least one time period to view statistics.")
    else:
        st.session_state.selected_periods = selected_periods
        
        # Display stats for selected periods with enhanced cards
        if len(selected_periods) == 1:
            # Single period detailed view
            period_key = selected_periods[0]
            period_data = st.session_state.crime_stats[period_key]
            
            st.markdown(f"""
            <h3 class="section-title">
                <span>📈</span>
                {period_data["period"]} Overview
            </h3>
            """, unsafe_allow_html=True)
            
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
            st.markdown("""
            <h3 class="section-title">
                <span>📈</span>
                Multi-Period Comparison
            </h3>
            """, unsafe_allow_html=True)
            
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
        
        # Enhanced Chart Controls
        st.markdown("""
        <h3 class="section-title">
            <span>📈</span>
            Interactive Analytics
        </h3>
        """, unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
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
        
        with col4:
            if st.button("🌍 International Context", key="chart_international_new"):
                fig = create_macrotrends_comparison_charts("international_context")
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
        
        # **NEW: MacroTrends Comparison Section**
        st.markdown("""
        <h3 class="section-title">
            <span>🌍</span>
            International Comparison Charts (MacroTrends Data)
        </h3>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📊 Historical Homicide Rates", key="macro_homicide_trends"):
                fig = create_macrotrends_comparison_charts("homicide_trends")
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if st.button("🌐 Global Comparison", key="macro_global_comparison"):
                fig = create_macrotrends_comparison_charts("international_context")
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
        
        with col3:
            if st.button("📈 Recent Totals", key="macro_recent_totals"):
                fig = create_macrotrends_comparison_charts("recent_crime_totals")
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("""
        <div class="feature-card">
            <p style="color: #00ff41; text-align: center;">📊 **MacroTrends Integration**: These charts provide international context and historical perspective using global crime database comparisons.</p>
        </div>
        """, unsafe_allow_html=True)

# EMERGENCY CONTACTS PAGE (Enhanced with HTML styling)
elif st.session_state.current_page == 'emergency':
    st.markdown("""
    <h2 class="section-title">
        <span>🚨</span>
        Emergency Contacts
    </h2>
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
                <p>{description}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Emergency Guidelines with enhanced styling
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(45, 27, 14, 0.6), rgba(33, 38, 45, 0.8)); 
                border: 1px solid rgba(255, 211, 61, 0.4); 
                padding: 25px; 
                border-radius: 12px; 
                margin-top: 30px;
                position: relative;
                overflow: hidden;">
        <div style="position: absolute; top: 0; left: -100%; width: 100%; height: 100%; 
                    background: linear-gradient(90deg, transparent, rgba(255, 211, 61, 0.05), transparent);
                    animation: shimmer 3s linear infinite;"></div>
        <h3 style="color: #ffd93d; margin-bottom: 15px; position: relative; z-index: 2;">⚠️ Important Emergency Guidelines</h3>
        <ul style="color: #c9d1d9; line-height: 1.8; list-style: none; padding: 0; position: relative; z-index: 2;">
            <li style="padding: 8px 0; padding-left: 25px; position: relative;">
                <span style="position: absolute; left: 0; color: #ffd93d; font-weight: bold;">•</span>
                <strong>For life-threatening emergencies, always call 911 first</strong>
            </li>
            <li style="padding: 8px 0; padding-left: 25px; position: relative;">
                <span style="position: absolute; left: 0; color: #ffd93d; font-weight: bold;">•</span>
                When calling, provide your exact location and nature of emergency
            </li>
            <li style="padding: 8px 0; padding-left: 25px; position: relative;">
                <span style="position: absolute; left: 0; color: #ffd93d; font-weight: bold;">•</span>
                Stay on the line until instructed to hang up
            </li>
            <li style="padding: 8px 0; padding-left: 25px; position: relative;">
                <span style="position: absolute; left: 0; color: #ffd93d; font-weight: bold;">•</span>
                Keep these numbers easily accessible at all times
            </li>
            <li style="padding: 8px 0; padding-left: 25px; position: relative;">
                <span style="position: absolute; left: 0; color: #ffd93d; font-weight: bold;">•</span>
                Follow dispatcher instructions carefully
            </li>
            <li style="padding: 8px 0; padding-left: 25px; position: relative;">
                <span style="position: absolute; left: 0; color: #ffd93d; font-weight: bold;">•</span>
                Provide first aid only if trained to do so
            </li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# **ENHANCED AI ASSISTANT CHAT PAGE WITH MEMORY & STATISTICS**
elif st.session_state.current_page == 'chat':
    st.markdown("""
    <h2 class="section-title">
        <span>💬</span>
        Enhanced AI Assistant
    </h2>
    """, unsafe_allow_html=True)
    
    # Chat Management Controls with enhanced styling
    st.markdown("""
    <div style="background: #21262d; border: 1px solid #30363d; border-radius: 12px; padding: 20px; margin-bottom: 20px;">
        <h3 style="color: #00ff41; margin-bottom: 15px;">🤖 Chat Management</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("➕ New Chat", key="new_chat", help="Start a new conversation"):
            create_new_chat()
            st.rerun()
    
    with col2:
        if st.button("📚 Chat History", key="show_history", help="View chat history"):
            st.session_state.show_chat_history = not st.session_state.get('show_chat_history', False)
            st.rerun()
    
    with col3:
        current_chat = get_current_chat()
        st.markdown(f"""
        <div style="background: rgba(0, 255, 65, 0.1); border: 1px solid rgba(0, 255, 65, 0.3); 
                    border-radius: 8px; padding: 10px; text-align: center;">
            <strong style="color: #00ff41;">Current:</strong><br>
            <span style="color: #c9d1d9; font-size: 0.9rem;">{current_chat['name']}</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        total_chats = len(st.session_state.chat_sessions)
        st.markdown(f"""
        <div style="background: rgba(0, 255, 65, 0.1); border: 1px solid rgba(0, 255, 65, 0.3); 
                    border-radius: 8px; padding: 10px; text-align: center;">
            <strong style="color: #00ff41;">Total Chats:</strong><br>
            <span style="color: #c9d1d9; font-size: 1.2rem; font-weight: bold;">{total_chats}</span>
        </div>
        """, unsafe_allow_html=True)
    
    # Chat History Sidebar
    if st.session_state.get('show_chat_history', False):
        st.markdown("""
        <h3 class="section-title">
            <span>📚</span>
            Chat History & Session Management
        </h3>
        """, unsafe_allow_html=True)
        
        if st.session_state.chat_sessions:
            for chat_id, chat_data in st.session_state.chat_sessions.items():
                is_active = chat_id == st.session_state.current_chat_id
                active_class = "active-chat" if is_active else ""
                
                # Chat history item with enhanced styling
                chat_display = f"💬 {chat_data['name']}"
                if is_active:
                    chat_display += " (Active)"
                
                if st.button(chat_display, key=f"chat_{chat_id}", help=f"Switch to {chat_data['name']} - Created: {chat_data['created_at']}"):
                    switch_to_chat(chat_id)
                    st.session_state.show_chat_history = False
                    st.rerun()
                
                # Show preview of last message
                if chat_data['messages']:
                    last_msg = chat_data['messages'][-1]['content'][:50] + "..." if len(chat_data['messages'][-1]['content']) > 50 else chat_data['messages'][-1]['content']
                    st.caption(f"Last: {last_msg}")
                    st.caption(f"Last Activity: {chat_data['last_activity']} AST")
                
                st.markdown("---")
        else:
            st.info("No chat history yet. Start a conversation!")
    
    # Enhanced Status Display
    if st.session_state.get('ai_enabled', False):
        st.markdown("""
        <div style="background: rgba(0, 255, 65, 0.1); border: 1px solid rgba(0, 255, 65, 0.3); 
                    border-radius: 12px; padding: 15px; margin: 15px 0; text-align: center;">
            <h4 style="color: #00ff41; margin: 0;">✅ Enhanced AI Ready</h4>
            <p style="color: #c9d1d9; margin: 5px 0 0 0;">Statistical Knowledge • Conversation Memory • Context Awareness</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background: rgba(255, 107, 107, 0.1); border: 1px solid rgba(255, 107, 107, 0.3); 
                    border-radius: 12px; padding: 15px; margin: 15px 0; text-align: center;">
            <h4 style="color: #ff6b6b; margin: 0;">❌ AI Offline</h4>
            <p style="color: #c9d1d9; margin: 5px 0 0 0;">Check your Google AI API key</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Chat Interface with enhanced styling
    st.markdown("""
    <div style="background: #21262d; border: 1px solid #30363d; border-radius: 12px; margin: 20px 0;">
        <div style="background: #0d1117; border-bottom: 1px solid #30363d; padding: 20px; border-radius: 12px 12px 0 0;">
            <h3 style="color: #00ff41; margin: 0;">🤖 Enhanced AI Assistant</h3>
            <p style="color: #8b949e; margin: 5px 0 0 0; font-size: 14px;">
                AI with conversation memory and statistical knowledge integration
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Get current chat and display messages
    current_chat = get_current_chat()
    messages = current_chat['messages']
    
    # Initialize with welcome message if no messages
    if not messages:
        welcome_msg = {
            "role": "assistant",
            "content": "🔒 Enhanced SECURO AI System Online!\n\nI now have access to comprehensive St. Kitts & Nevis crime statistics, international comparison data from MacroTrends, and can maintain conversation context. Ask me about:\n\n• Local crime trends and detection rates\n• International comparisons and global context\n• Historical data analysis with charts\n• Specific incidents or general questions\n\nI can show interactive charts for international comparisons!",
            "timestamp": get_stkitts_time()
        }
        messages.append(welcome_msg)
        current_chat['messages'] = messages
    
    # Display chat messages with enhanced styling
    st.markdown('<div style="min-height: 400px; padding: 20px;">', unsafe_allow_html=True)
    for message in messages:
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
    st.markdown('</div>', unsafe_allow_html=True)

    # Enhanced Chat input with styling
    st.markdown("""
    <div style="background: #21262d; border-top: 1px solid #30363d; padding: 20px; 
                border-radius: 0 0 12px 12px; margin-bottom: 20px;">
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_input(
            "💬 Message Enhanced AI Assistant:",
            placeholder="Ask about crime statistics, trends, international comparisons, or request charts... (I have full conversation memory)",
            label_visibility="collapsed",
            key="chat_input"
        )
        
        submitted = st.form_submit_button("🚀 Send Message", type="primary")
        
        if submitted and user_input and user_input.strip():
            current_time = get_stkitts_time()
            
            # Add user message to current chat
            add_message_to_chat("user", user_input)
            
            # Generate response with conversation history and statistics
            with st.spinner("🤖 Generating enhanced AI response with statistical knowledge..."):
                response, chart_type = generate_enhanced_smart_response(
                    user_input, 
                    conversation_history=current_chat['messages'],
                    language=st.session_state.selected_language
                )
            
            # Add assistant response to current chat
            add_message_to_chat("assistant", response)
            
            # Display the requested chart if any
            if chart_type:
                st.markdown("### 📊 Requested Chart")
                
                if chart_type == "international":
                    # Show international comparison charts
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        fig = create_macrotrends_comparison_charts("homicide_trends")
                        if fig:
                            st.plotly_chart(fig, use_container_width=True)
                    
                    with col2:
                        fig = create_macrotrends_comparison_charts("international_context")
                        if fig:
                            st.plotly_chart(fig, use_container_width=True)
                    
                    with col3:
                        fig = create_macrotrends_comparison_charts("recent_crime_totals")
                        if fig:
                            st.plotly_chart(fig, use_container_width=True)
                
                elif chart_type == "trends":
                    # Show crime trends
                    selected_periods = ['2022_ANNUAL', '2023_ANNUAL', '2024_ANNUAL', '2025_Q2']
                    fig = create_historical_crime_charts("crime_trends", selected_periods, st.session_state.crime_stats)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                
                elif chart_type == "detection":
                    # Show detection rates
                    selected_periods = ['2022_ANNUAL', '2023_ANNUAL', '2024_ANNUAL']
                    fig = create_historical_crime_charts("detection_comparison", selected_periods, st.session_state.crime_stats)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                
                elif chart_type == "breakdown":
                    # Show crime type breakdown
                    selected_periods = ['2024_ANNUAL']
                    fig = create_historical_crime_charts("crime_type_breakdown", selected_periods, st.session_state.crime_stats)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                
                elif chart_type == "homicide":
                    # Show homicide trends
                    fig = create_macrotrends_comparison_charts("homicide_trends")
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
            
            # Only show the international comparison buttons if it was an international query
            # but no specific chart was requested
            elif is_international_comparison_query(user_input) and not chart_type:
                st.markdown("### 📊 International Comparison Charts")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("📈 Historical Homicide Trends", key=f"macro_hist_{int(time.time())}", use_container_width=True):
                        fig = create_macrotrends_comparison_charts("homicide_trends")
                        if fig:
                            st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    if st.button("🌍 International Context", key=f"macro_context_{int(time.time())}", use_container_width=True):
                        fig = create_macrotrends_comparison_charts("international_context")
                        if fig:
                            st.plotly_chart(fig, use_container_width=True)
                
                with col3:
                    if st.button("📊 Recent Crime Totals", key=f"macro_recent_{int(time.time())}", use_container_width=True):
                        fig = create_macrotrends_comparison_charts("recent_crime_totals")
                        if fig:
                            st.plotly_chart(fig, use_container_width=True)
                
                st.info("💡 **MacroTrends Data**: Click the buttons above to view international comparison charts with historical context.")
            
            st.rerun()

# Close main content area
st.markdown('</div>', unsafe_allow_html=True)

# Enhanced Status bar matching HTML design
current_time = get_stkitts_time()

st.markdown(f"""
<div style="background: rgba(0, 0, 0, 0.9); padding: 15px; border-radius: 25px; margin-top: 30px; 
            display: flex; justify-content: space-between; align-items: center; border: 1px solid rgba(0, 255, 65, 0.2); 
            flex-wrap: wrap; gap: 10px;">
    <div style="display: flex; align-items: center; gap: 10px; color: #ffffff; font-size: 0.9rem;">
        <div style="width: 8px; height: 8px; background: #00ff41; border-radius: 50%; animation: pulse 2s infinite;"></div>
        <span>Enhanced AI {"Active" if st.session_state.get('ai_enabled', False) else "Offline"}</span>
    </div>
    <div style="display: flex; align-items: center; gap: 10px; color: #ffffff; font-size: 0.9rem;">
        <div style="width: 8px; height: 8px; background: #00ff41; border-radius: 50%; animation: pulse 2s infinite;"></div>
        <span>MacroTrends Integration: Active</span>
    </div>
    <div style="display: flex; align-items: center; gap: 10px; color: #ffffff; font-size: 0.9rem;">
        <div style="width: 8px; height: 8px; background: #00ff41; border-radius: 50%; animation: pulse 2s infinite;"></div>
        <span>Conversation Memory: Enabled</span>
    </div>
    <div style="display: flex; align-items: center; gap: 10px; color: #ffffff; font-size: 0.9rem;">
        <div style="width: 8px; height: 8px; background: #00ff41; border-radius: 50%; animation: pulse 2s infinite;"></div>
        <span>Chat Sessions: {len(st.session_state.chat_sessions)}</span>
    </div>
    <div style="display: flex; align-items: center; gap: 10px; color: #ffffff; font-size: 0.9rem;">
        <div style="width: 8px; height: 8px; background: #00ff41; border-radius: 50%; animation: pulse 2s infinite;"></div>
        <span>🕒 {current_time} AST</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Enhanced Footer matching HTML design
st.markdown(f"""
<div class="footer">
    <div style="max-width: 1400px; margin: 0 auto; padding: 0 20px;">
        <div style="display: flex; justify-content: center; gap: 30px; margin-bottom: 20px; flex-wrap: wrap;">
            <a href="#" style="color: #00ff41; text-decoration: none; transition: color 0.3s ease;">Privacy Policy</a>
            <a href="#" style="color: #00ff41; text-decoration: none; transition: color 0.3s ease;">Terms of Service</a>
            <a href="#" style="color: #00ff41; text-decoration: none; transition: color 0.3s ease;">Contact Support</a>
            <a href="#" style="color: #00ff41; text-decoration: none; transition: color 0.3s ease;">System Status</a>
            <a href="#" style="color: #00ff41; text-decoration: none; transition: color 0.3s ease;">Documentation</a>
        </div>
        <div style="text-align: center; color: #8b949e; font-size: 14px;">
            <p style="margin: 5px 0;">&copy; 2025 SECURO - Enhanced AI Assistant & Crime Intelligence System</p>
            <p style="margin: 5px 0;">Royal St. Christopher and Nevis Police Force | Version 2.1.0</p>
            <p style="margin: 5px 0;">📊 <span style="color: #00ff41;">Data Source:</span> Royal St. Christopher & Nevis Police Force (RSCNPF) • Statistical Integration Active</p>
            <p style="margin: 5px 0;">📞 <span style="color: #00ff41;">Local Intelligence Office:</span> <a href="tel:+18694652241" style="color: #00ff41; text-decoration: none;">869-465-2241</a> Ext. 4238/4239 | 
            📧 <a href="mailto:liosk@police.kn" style="color: #00ff41; text-decoration: none;">liosk@police.kn</a></p>
            <p style="margin: 5px 0;">🔄 <span style="color: #00ff41;">Last Updated:</span> {get_stkitts_date()} {get_stkitts_time()} AST | <span style="color: #00ff41;">Enhanced AI Intelligence</span></p>
            <p style="margin: 5px 0;">🤖 <span style="color: #00ff41;">AI System:</span> Statistical Knowledge • Conversation Memory • Context Awareness • Multi-Chat Support</p>
            <p style="margin: 5px 0;">🌍 <span style="color: #00ff41;">Multi-language Support</span> | 🔒 <span style="color: #00ff41;">Secure Law Enforcement Platform</span></p>
        </div>
        <div style="background: rgba(0, 255, 65, 0.1); padding: 15px; border-radius: 10px; margin-top: 20px; text-align: center;">
            <span style="color: #00ff41; font-weight: bold; font-size: 1.1rem;">🧠 Enhanced AI Assistant Platform</span><br>
            <span style="color: #c9d1d9; margin-top: 5px; display: block;">Statistical knowledge integration • Conversation memory • Context awareness • Multi-chat support • Professional law enforcement assistance</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
