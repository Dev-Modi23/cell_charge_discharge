import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
import time
import random
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(
    page_title="BatteryFlow Pro",
    page_icon="🔋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern aesthetic
st.markdown("""
<style>
    .main > div {
        padding-top: 2rem;
    }
    
    .stMetric {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 15px;
        color: white;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        backdrop-filter: blur(4px);
        border: 1px solid rgba(255, 255, 255, 0.18);
    }
    
    .status-card {
        background: linear-gradient(135deg, #ff6b6b 0%, #feca57 100%);
        padding: 1.5rem;
        border-radius: 20px;
        margin: 1rem 0;
        color: white;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        animation: pulse 2s infinite;
    }
    
    .charging-animation {
        background: linear-gradient(135deg, #48cae4 0%, #023e8a 100%);
        animation: charging 2s ease-in-out infinite;
    }
    
    .discharging-animation {
        background: linear-gradient(135deg, #f72585 0%, #b5179e 100%);
        animation: discharging 2s ease-in-out infinite;
    }
    
    .idle-animation {
        background: linear-gradient(135deg, #6c757d 0%, #495057 100%);
    }
    
    .paused-animation {
        background: linear-gradient(135deg, #ffc107 0%, #fd7e14 100%);
        animation: blink 1s infinite;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    @keyframes charging {
        0%, 100% { opacity: 0.8; }
        50% { opacity: 1; }
    }
    
    @keyframes discharging {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.6; }
    }
    
    @keyframes blink {
        0%, 50% { opacity: 1; }
        51%, 100% { opacity: 0.7; }
    }
    
    .warning-panel {
        background: linear-gradient(135deg, #ff9a56 0%, #ffad56 100%);
        padding: 1rem;
        border-radius: 15px;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 5px 15px rgba(255, 154, 86, 0.4);
    }
    
    .safety-critical {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%);
        animation: blink 1s infinite;
    }
    
    .cell-card {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 1rem;
        margin: 0.5rem;
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
    }
    
    .control-button {
        padding: 1rem;
        margin: 0.5rem;
        border-radius: 15px;
        text-align: center;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .control-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.3);
    }
    
    .real-time-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        background-color: #00ff00;
        border-radius: 50%;
        animation: blink 1s infinite;
        margin-right: 8px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'cells_data' not in st.session_state:
    st.session_state.cells_data = {}
if 'charging_status' not in st.session_state:
    st.session_state.charging_status = "Idle"
if 'historical_data' not in st.session_state:
    st.session_state.historical_data = []
if 'bench_info' not in st.session_state:
    st.session_state.bench_info = {"bench": "", "group": 1}
if 'start_time' not in st.session_state:
    st.session_state.start_time = datetime.now()
if 'real_time_data' not in st.session_state:
    st.session_state.real_time_data = []

# Sidebar Navigation
st.sidebar.markdown("# 🔋 BatteryFlow Pro")
st.sidebar.markdown("---")

page = st.sidebar.selectbox(
    "Navigate",
    ["🏠 Dashboard", "⚙️ Setup", "🎛️ Control Panel", "📊 Analysis"],
    key="navigation"
)

# Auto-refresh for real-time data
if st.sidebar.button("🔄 Refresh Data", type="primary"):
    st.rerun()

# Cell type specifications
CELL_SPECS = {
    "LFP": {"nominal": 3.2, "min": 2.8, "max": 3.6, "color": "#4CAF50"},
    "NMC": {"nominal": 3.6, "min": 3.0, "max": 4.2, "color": "#2196F3"},
    "LTO": {"nominal": 2.4, "min": 1.8, "max": 2.8, "color": "#FF9800"}
}

def generate_real_time_data():
    """Generate real-time data based on current cell configuration and status"""
    current_time = datetime.now()
    data_points = []
    
    for cell_name, cell_data in st.session_state.cells_data.items():
        # Simulate real-time variations based on charging status
        base_voltage = cell_data['voltage']
        base_current = cell_data['current']
        base_temp = cell_data['temperature']
        
        if st.session_state.charging_status == "Charging":
            voltage = base_voltage + random.uniform(0.05, 0.15)
            current = abs(base_current) + random.uniform(-0.5, 0.5)
            temperature = base_temp + random.uniform(2, 8)
        elif st.session_state.charging_status == "Discharging":
            voltage = base_voltage - random.uniform(0.05, 0.15)
            current = -abs(base_current) + random.uniform(-0.5, 0.5)
            temperature = base_temp + random.uniform(1, 5)
        elif st.session_state.charging_status == "Paused":
            voltage = base_voltage + random.uniform(-0.02, 0.02)
            current = random.uniform(-0.1, 0.1)
            temperature = base_temp + random.uniform(-1, 1)
        else:  # Idle
            voltage = base_voltage + random.uniform(-0.01, 0.01)
            current = 0.0
            temperature = base_temp + random.uniform(-0.5, 0.5)
        
        data_points.append({
            'timestamp': current_time,
            'cell_id': cell_name,
            'cell_type': cell_data.get('type', 'LFP'),
            'voltage': max(0, voltage),
            'current': current,
            'temperature': temperature,
            'capacity': abs(voltage * current) if current != 0 else 0
        })
    
    return data_points

def get_safety_warnings(voltage, current, temperature, cell_type):
    """Generate safety warnings based on cell parameters"""
    warnings = []
    spec = CELL_SPECS[cell_type]
    
    if voltage > spec["max"]:
        warnings.append(("🚨 CRITICAL", f"Overvoltage: {voltage:.2f}V > {spec['max']}V"))
    elif voltage < spec["min"]:
        warnings.append(("⚠️ WARNING", f"Undervoltage: {voltage:.2f}V < {spec['min']}V"))
    
    if abs(current) > 10:
        warnings.append(("⚠️ WARNING", f"High current: {abs(current):.2f}A"))
    
    if temperature > 45:
        warnings.append(("🚨 CRITICAL", f"Overheating: {temperature:.1f}°C"))
    elif temperature < 0:
        warnings.append(("⚠️ WARNING", f"Low temperature: {temperature:.1f}°C"))
    
    return warnings

def calculate_charge_percentage(voltage, cell_type):
    """Calculate estimated charge percentage"""
    spec = CELL_SPECS[cell_type]
    if voltage <= spec["min"]:
        return 0
    elif voltage >= spec["max"]:
        return 100
    else:
        return ((voltage - spec["min"]) / (spec["max"] - spec["min"])) * 100

def configure_cell(cell_index, cells_data_dict):
    """Configure individual cell parameters"""
    cell_name = f"Cell_{cell_index + 1}"
    
    # Get existing data or defaults
    existing_data = st.session_state.cells_data.get(cell_name, {})
    
    col1, col2 = st.columns(2)
    
    with col1:
        cell_type = st.selectbox(
            "Cell Type", 
            ["LFP", "NMC", "LTO"], 
            index=["LFP", "NMC", "LTO"].index(existing_data.get('type', 'LFP')),
            key=f"type_{cell_index}"
        )
        
        voltage = st.number_input(
            "Voltage (V)", 
            min_value=0.0, 
            max_value=5.0, 
            value=existing_data.get('voltage', CELL_SPECS[cell_type]['nominal']),
            step=0.1,
            key=f"voltage_{cell_index}"
        )
        
        current = st.number_input(
            "Current (A)", 
            min_value=-20.0, 
            max_value=20.0, 
            value=existing_data.get('current', 2.0),
            step=0.1,
            key=f"current_{cell_index}"
        )
    
    with col2:
        temperature = st.number_input(
            "Temperature (°C)", 
            min_value=-20.0, 
            max_value=80.0, 
            value=existing_data.get('temperature', 25.0),
            step=0.5,
            key=f"temp_{cell_index}"
        )
        
        test_time = st.number_input(
            "Test Time (hours)", 
            min_value=0.0, 
            max_value=100.0, 
            value=existing_data.get('time', 1.0),
            step=0.5,
            key=f"time_{cell_index}"
        )
    
    # Calculate capacity
    capacity = abs(voltage * current)
    
    # Display cell specifications
    spec = CELL_SPECS[cell_type]
    st.info(f"""
    **{cell_type} Specifications:**
    - Nominal: {spec['nominal']}V
    - Range: {spec['min']}V - {spec['max']}V
    - Calculated Capacity: {capacity:.2f}Wh
    """)
    
    # Store data
    cells_data_dict[cell_name] = {
        'type': cell_type,
        'voltage': voltage,
        'current': current,
        'temperature': temperature,
        'time': test_time,
        'capacity': capacity
    }

# PAGE 1: DASHBOARD
if page == "🏠 Dashboard":
    st.title("🏠 Battery Management Dashboard")
    
    # System Status Header with correct active cells count
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_cells = len(st.session_state.cells_data)
        st.metric("📱 Total Cells", total_cells)
    
    with col2:
        avg_voltage = np.mean([cell['voltage'] for cell in st.session_state.cells_data.values()]) if st.session_state.cells_data else 0
        st.metric("⚡ Avg Voltage", f"{avg_voltage:.2f}V")
    
    with col3:
        total_current = sum([abs(cell['current']) for cell in st.session_state.cells_data.values()]) if st.session_state.cells_data else 0
        st.metric("🔌 Total Current", f"{total_current:.2f}A")
    
    with col4:
        avg_temp = np.mean([cell['temperature'] for cell in st.session_state.cells_data.values()]) if st.session_state.cells_data else 25
        st.metric("🌡️ Avg Temperature", f"{avg_temp:.1f}°C")
    
    # System Status Animation with proper status classes
    status_class = ""
    if st.session_state.charging_status == "Charging":
        status_class = "charging-animation"
    elif st.session_state.charging_status == "Discharging":
        status_class = "discharging-animation"
    elif st.session_state.charging_status == "Paused":
        status_class = "paused-animation"
    else:
        status_class = "idle-animation"
    
    st.markdown(f"""
    <div class="status-card {status_class}">
        <h2>🔋 System Status: {st.session_state.charging_status}</h2>
        <p>Bench: {st.session_state.bench_info.get('bench', 'Not Set')} | Group: {st.session_state.bench_info.get('group', 'Not Set')}</p>
        <p>Active Cells: {len(st.session_state.cells_data)}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Cells Overview
    if st.session_state.cells_data:
        st.subheader("📊 Cells Overview")
        
        cols = st.columns(min(4, len(st.session_state.cells_data)))
        for idx, (cell_name, cell_data) in enumerate(st.session_state.cells_data.items()):
            with cols[idx % 4]:
                charge_pct = calculate_charge_percentage(cell_data['voltage'], cell_data.get('type', 'LFP'))
                
                # Color coding based on charge level
                if charge_pct > 80:
                    color = "#4CAF50"  # Green
                elif charge_pct > 40:
                    color = "#FF9800"  # Orange
                else:
                    color = "#F44336"  # Red
                
                st.markdown(f"""
                <div class="cell-card" style="border-left: 4px solid {color};">
                    <h4>{cell_name}</h4>
                    <p><strong>Type:</strong> {cell_data.get('type', 'LFP')}</p>
                    <p><strong>Voltage:</strong> {cell_data['voltage']:.2f}V</p>
                    <p><strong>Charge:</strong> {charge_pct:.1f}%</p>
                    <p><strong>Temp:</strong> {cell_data['temperature']:.1f}°C</p>
                </div>
                """, unsafe_allow_html=True)
    
    # Safety Warnings Panel
    st.subheader("🛡️ Safety Warnings")
    
    all_warnings = []
    for cell_name, cell_data in st.session_state.cells_data.items():
        warnings = get_safety_warnings(
            cell_data['voltage'], 
            cell_data['current'], 
            cell_data['temperature'],
            cell_data.get('type', 'LFP')
        )
        for warning_type, message in warnings:
            all_warnings.append(f"{cell_name}: {warning_type} {message}")
    
    if all_warnings:
        for warning in all_warnings:
            if "CRITICAL" in warning:
                st.markdown(f'<div class="warning-panel safety-critical">{warning}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="warning-panel">{warning}</div>', unsafe_allow_html=True)
    else:
        st.success("✅ All systems operating normally")

# PAGE 2: SETUP
elif page == "⚙️ Setup":
    st.title("⚙️ System Setup")
    
    # Bench Information
    st.subheader("🏭 Bench Configuration")
    col1, col2 = st.columns(2)
    
    with col1:
        bench = st.text_input("Bench Number", value=st.session_state.bench_info.get('bench', ''))
        st.session_state.bench_info['bench'] = bench
    
    with col2:
        group = st.number_input("Group Number", min_value=1, max_value=100, value=st.session_state.bench_info.get('group', 1))
        st.session_state.bench_info['group'] = group
    
    st.markdown("---")
    
    # Cell Configuration
    st.subheader("🔋 Cell Configuration")
    
    # Number of cells selector
    num_cells = st.slider("Number of Cells", min_value=1, max_value=16, value=max(8, len(st.session_state.cells_data)))
    
    st.markdown("### Configure Each Cell")
    
    # Create tabs for better organization
    if num_cells <= 8:
        cell_tabs = st.tabs([f"Cell {i+1}" for i in range(num_cells)])
    else:
        cell_tabs = None
    
    new_cells_data = {}
    
    for i in range(num_cells):
        if cell_tabs:
            with cell_tabs[i]:
                configure_cell(i, new_cells_data)
        else:
            with st.expander(f"🔋 Cell {i+1} Configuration", expanded=i < 8):
                configure_cell(i, new_cells_data)
    
    # Save configuration
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("💾 Save Configuration", type="primary", use_container_width=True):
            st.session_state.cells_data = new_cells_data
            st.success("✅ Configuration saved successfully!")
            time.sleep(1)
            st.rerun()

# PAGE 3: CONTROL PANEL (FIXED)
elif page == "🎛️ Control Panel":
    st.title("🎛️ Control Panel")
    
    # Enhanced Control buttons with better styling
    st.subheader("🎮 System Controls")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🔌 Start Charging", type="primary", use_container_width=True):
            st.session_state.charging_status = "Charging"
            st.session_state.start_time = datetime.now()
            st.success("⚡ Charging started!")
            st.rerun()
    
    with col2:
        if st.button("📱 Start Discharging", use_container_width=True):
            st.session_state.charging_status = "Discharging"
            st.session_state.start_time = datetime.now()
            st.warning("🔋 Discharging started!")
            st.rerun()
    
    with col3:
        if st.button("⏸️ Pause", use_container_width=True):
            st.session_state.charging_status = "Paused"
            st.info("⏸️ System paused!")
            st.rerun()
    
    with col4:
        if st.button("⏹️ Stop", use_container_width=True):
            st.session_state.charging_status = "Idle"
            st.info("⏹️ System stopped!")
            st.rerun()
    
    # Current Status Display
    status_col1, status_col2, status_col3 = st.columns(3)
    with status_col1:
        st.metric("Current Status", st.session_state.charging_status)
    with status_col2:
        if st.session_state.charging_status in ["Charging", "Discharging"]:
            elapsed_time = datetime.now() - st.session_state.start_time
            st.metric("Runtime", f"{elapsed_time.total_seconds()/60:.1f} min")
        else:
            st.metric("Runtime", "0.0 min")
    with status_col3:
        st.metric("Active Cells", len(st.session_state.cells_data))
    
    st.markdown("---")
    
    # Real-time monitoring (FIXED)
    st.subheader("📊 Real-time Monitoring")
    
    if st.session_state.cells_data:
        # Generate current real-time data
        current_data = generate_real_time_data()
        
        # Add current data to historical real-time data
        st.session_state.real_time_data.extend(current_data)
        
        # Keep only last 60 data points per cell
        if len(st.session_state.real_time_data) > 60 * len(st.session_state.cells_data):
            st.session_state.real_time_data = st.session_state.real_time_data[-60 * len(st.session_state.cells_data):]
        
        # Create DataFrame from real-time data
        if st.session_state.real_time_data:
            rt_df = pd.DataFrame(st.session_state.real_time_data)
            
            # Create real-time charts
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=(
                    f'🔴 Voltage Over Time - {st.session_state.charging_status}', 
                    f'🟡 Current Over Time - {st.session_state.charging_status}', 
                    f'🟢 Temperature Over Time - {st.session_state.charging_status}', 
                    'Capacity Distribution'
                ),
                specs=[[{"secondary_y": False}, {"secondary_y": False}],
                       [{"secondary_y": False}, {"type": "pie"}]]
            )
            
            # Get unique cells and colors
            unique_cells = rt_df['cell_id'].unique()
            colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57', '#FF9FF3', '#54A0FF', '#5F27CD']
            
            for i, cell_id in enumerate(unique_cells):
                cell_data = rt_df[rt_df['cell_id'] == cell_id].tail(20)  # Last 20 points
                color = colors[i % len(colors)]
                
                # Voltage trace
                fig.add_trace(
                    go.Scatter(
                        x=cell_data['timestamp'], 
                        y=cell_data['voltage'], 
                        name=f"{cell_id} Voltage",
                        line=dict(color=color, width=2),
                        mode='lines+markers'
                    ),
                    row=1, col=1
                )
                
                # Current trace with status indication
                current_color = '#00FF00' if st.session_state.charging_status == 'Charging' else '#FF0000' if st.session_state.charging_status == 'Discharging' else '#808080'
                fig.add_trace(
                    go.Scatter(
                        x=cell_data['timestamp'], 
                        y=cell_data['current'], 
                        name=f"{cell_id} Current",
                        line=dict(color=current_color, width=2),
                        mode='lines+markers'
                    ),
                    row=1, col=2
                )
                
                # Temperature trace
                fig.add_trace(
                    go.Scatter(
                        x=cell_data['timestamp'], 
                        y=cell_data['temperature'], 
                        name=f"{cell_id} Temp",
                        line=dict(color=color, width=2),
                        mode='lines+markers'
                    ),
                    row=2, col=1
                )
            
            # Capacity pie chart
            latest_data = rt_df.groupby('cell_id').tail(1)
            fig.add_trace(
                go.Pie(
                    labels=latest_data['cell_id'], 
                    values=latest_data['capacity'], 
                    name="Capacity Distribution",
                    marker_colors=colors[:len(latest_data)]
                ),
                row=2, col=2
            )
            
            # Update layout with charging/discharging indicators
            fig.update_layout(
                height=800, 
                showlegend=True,
                title_text=f"Real-time Battery Monitoring - Status: {st.session_state.charging_status}"
            )
            
            # Add status indicators to axes
            if st.session_state.charging_status == "Charging":
                fig.add_annotation(text="⚡ CHARGING", xref="paper", yref="paper", x=0.02, y=0.98, showarrow=False, font=dict(color="green", size=14))
            elif st.session_state.charging_status == "Discharging":
                fig.add_annotation(text="📱 DISCHARGING", xref="paper", yref="paper", x=0.02, y=0.98, showarrow=False, font=dict(color="red", size=14))
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Real-time status indicator
            st.markdown(f"""
            <div style="text-align: center; padding: 1rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; color: white;">
                <span class="real-time-indicator"></span>
                <strong>LIVE MONITORING - {st.session_state.charging_status.upper()}</strong>
            </div>
            """, unsafe_allow_html=True)
        
        # Control parameters
        st.subheader("🎚️ Control Parameters")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            target_voltage = st.slider("Target Voltage (V)", 2.0, 5.0, 3.6, 0.1)
            max_current = st.slider("Max Current (A)", 1.0, 10.0, 5.0, 0.5)
        
        with col2:
            target_temp = st.slider("Target Temperature (°C)", 20.0, 50.0, 25.0, 1.0)
            safety_timeout = st.slider("Safety Timeout (min)", 10, 180, 60, 10)
        
        with col3:
            charge_cutoff = st.slider("Charge Cutoff (%)", 80, 100, 95, 1)
            discharge_cutoff = st.slider("Discharge Cutoff (%)", 5, 30, 10, 1)
    
    else:
        st.warning("⚠️ No cells configured. Please go to Setup page to configure cells first.")

# PAGE 4: ANALYSIS (FIXED)
elif page == "📊 Analysis":
    st.title("📊 Data Analysis")
    
    # Generate historical data if not exists or if it's empty
    if (not hasattr(st.session_state, 'historical_data') or 
        st.session_state.historical_data is None or 
        (isinstance(st.session_state.historical_data, pd.DataFrame) and st.session_state.historical_data.empty) or
        (isinstance(st.session_state.historical_data, list) and len(st.session_state.historical_data) == 0)):
        
        with st.spinner("Generating historical data..."):
            # Generate mock historical data based on current cell configuration
            historical_data = []
            base_time = datetime.now() - timedelta(hours=2)
            
            if st.session_state.cells_data:
                for i in range(120):  # 2 hours of data, every minute
                    timestamp = base_time + timedelta(minutes=i)
                    
                    for cell_name, cell_data in st.session_state.cells_data.items():
                        # Add realistic variations
                        voltage = cell_data['voltage'] + random.uniform(-0.2, 0.2)
                        current = cell_data['current'] + random.uniform(-1, 1)
                        temperature = cell_data['temperature'] + random.uniform(-5, 15)
                        capacity = abs(voltage * current)
                        
                        historical_data.append({
                            "timestamp": timestamp,
                            "cell_id": cell_name,
                            "cell_type": cell_data.get('type', 'LFP'),
                            "voltage": max(0, voltage),
                            "current": current,
                            "temperature": temperature,
                            "capacity": capacity
                        })
                
                st.session_state.historical_data = pd.DataFrame(historical_data)
            else:
                # If no cells configured, create empty DataFrame
                st.session_state.historical_data = pd.DataFrame(columns=[
                    'timestamp', 'cell_id', 'cell_type', 'voltage', 'current', 'temperature', 'capacity'
                ])
    
    # Ensure df is a DataFrame
    df = st.session_state.historical_data
    if not isinstance(df, pd.DataFrame):
        df = pd.DataFrame(columns=['timestamp', 'cell_id', 'cell_type', 'voltage', 'current', 'temperature', 'capacity'])
    
    if isinstance(df, pd.DataFrame) and not df.empty:
        # Summary statistics with correct active cells count
        st.subheader("📈 Summary Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📊 Total Data Points", len(df))
            st.metric("⚡ Avg Voltage", f"{df['voltage'].mean():.2f}V")
        
        with col2:
            st.metric("🔌 Avg Current", f"{df['current'].mean():.2f}A")
            st.metric("🌡️ Avg Temperature", f"{df['temperature'].mean():.1f}°C")
        
        with col3:
            active_cells = len(st.session_state.cells_data)  # Correct active cells count
            st.metric("📱 Active Cells", active_cells)
            st.metric("⚡ Max Voltage", f"{df['voltage'].max():.2f}V")
        
        with col4:
            st.metric("🔌 Max Current", f"{df['current'].max():.2f}A")
            st.metric("🌡️ Max Temperature", f"{df['temperature'].max():.1f}°C")
        
        # Interactive charts (FIXED)
        st.subheader("📊 Interactive Charts")
        
        # Chart selection
        chart_type = st.selectbox("Select Chart Type", 
                                ["Temperature Over Time", "Voltage vs Current", "Cell Performance Comparison", "Safety Analysis"])
        
        if chart_type == "Temperature Over Time":
            fig = px.line(df, x='timestamp', y='temperature', color='cell_id',
                         title='🌡️ Temperature Monitoring Over Time',
                         labels={'temperature': 'Temperature (°C)', 'timestamp': 'Time'},
                         color_discrete_sequence=px.colors.qualitative.Set3)
            
            # Add warning zones
            fig.add_hline(y=45, line_dash="dash", line_color="red", 
                         annotation_text="Critical Temperature (45°C)")
            fig.add_hline(y=35, line_dash="dash", line_color="orange", 
                         annotation_text="Warning Temperature (35°C)")
            
            fig.update_layout(height=600, showlegend=True)
            
        elif chart_type == "Voltage vs Current":
            fig = px.scatter(df, x='voltage', y='current', color='cell_type', size='temperature',
                           title='⚡ Voltage vs Current Analysis',
                           labels={'voltage': 'Voltage (V)', 'current': 'Current (A)'},
                           color_discrete_sequence=px.colors.qualitative.Set2)
            
            fig.update_layout(height=600, showlegend=True)
            
        elif chart_type == "Cell Performance Comparison":
            cell_summary = df.groupby('cell_id').agg({
                'voltage': 'mean',
                'current': 'mean',
                'temperature': 'mean',
                'capacity': 'mean'
            }).reset_index()
            
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('Average Voltage by Cell', 'Average Current by Cell', 
                              'Average Temperature by Cell', 'Average Capacity by Cell'),
                specs=[[{"type": "bar"}, {"type": "bar"}],
                       [{"type": "bar"}, {"type": "bar"}]]
            )
            
            colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57', '#FF9FF3', '#54A0FF', '#5F27CD']
            
            fig.add_trace(
                go.Bar(x=cell_summary['cell_id'], y=cell_summary['voltage'],
                       name='Avg Voltage', marker_color=colors[0]),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Bar(x=cell_summary['cell_id'], y=cell_summary['current'],
                       name='Avg Current', marker_color=colors[1]),
                row=1, col=2
            )
            
            fig.add_trace(
                go.Bar(x=cell_summary['cell_id'], y=cell_summary['temperature'],
                       name='Avg Temperature', marker_color=colors[2]),
                row=2, col=1
            )
            
            fig.add_trace(
                go.Bar(x=cell_summary['cell_id'], y=cell_summary['capacity'],
                       name='Avg Capacity', marker_color=colors[3]),
                row=2, col=2
            )
            
            fig.update_layout(
                height=800,
                title_text='🔋 Cell Performance Comparison',
                showlegend=False
            )
            
        else:  # Safety Analysis
            # Calculate safety scores
            safety_data = []
            for _, row in df.iterrows():
                warnings = get_safety_warnings(row['voltage'], row['current'], 
                                             row['temperature'], row['cell_type'])
                safety_score = max(0, 100 - len(warnings) * 25)
                safety_data.append({
                    'cell_id': row['cell_id'],
                    'timestamp': row['timestamp'],
                    'safety_score': safety_score,
                    'warning_count': len(warnings)
                })
            
            safety_df = pd.DataFrame(safety_data)
            
            fig = px.line(safety_df, x='timestamp', y='safety_score', color='cell_id',
                         title='🛡️ Safety Score Analysis Over Time',
                         labels={'safety_score': 'Safety Score (%)', 'timestamp': 'Time'},
                         color_discrete_sequence=px.colors.qualitative.Pastel)
            
            fig.add_hline(y=75, line_dash="dash", line_color="orange", 
                         annotation_text="Warning Threshold (75%)")
            fig.add_hline(y=50, line_dash="dash", line_color="red", 
                         annotation_text="Critical Threshold (50%)")
            
            fig.update_layout(height=600, showlegend=True)
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Data table
        st.subheader("📋 Data Table")
        
        # Filter options with better error handling
        col1, col2, col3 = st.columns(3)
        
        with col1:
            available_cells = list(df['cell_id'].unique()) if not df.empty and 'cell_id' in df.columns else []
            if available_cells:
                selected_cells = st.multiselect(
                    "Select Cells", 
                    available_cells, 
                    default=available_cells[:min(4, len(available_cells))],
                    key="analysis_cell_filter"
                )
            else:
                selected_cells = []
                st.multiselect("Select Cells", [], help="No cells available. Configure cells in Setup page.")
        
        with col2:
            available_types = list(df['cell_type'].unique()) if not df.empty and 'cell_type' in df.columns else []
            if available_types:
                selected_types = st.multiselect(
                    "Select Cell Types", 
                    available_types,
                    default=available_types,
                    key="analysis_type_filter"
                )
            else:
                selected_types = []
                st.multiselect("Select Cell Types", [], help="No cell types available.")
        
        with col3:
            time_range = st.slider("Time Range (hours ago)", 0, 24, (0, 2), key="analysis_time_range")
        
        # Filter data with proper error handling
        filtered_df = pd.DataFrame()
        
        try:
            if not df.empty and selected_cells and selected_types:
                # Ensure timestamp column exists and is datetime
                if 'timestamp' in df.columns:
                    if not pd.api.types.is_datetime64_any_dtype(df['timestamp']):
                        df['timestamp'] = pd.to_datetime(df['timestamp'])
                    
                    # Apply filters
                    filtered_df = df[
                        (df['cell_id'].isin(selected_cells)) &
                        (df['cell_type'].isin(selected_types)) &
                        (df['timestamp'] >= datetime.now() - timedelta(hours=time_range[1])) &
                        (df['timestamp'] <= datetime.now() - timedelta(hours=time_range[0]))
                    ].sort_values('timestamp', ascending=False)
                else:
                    st.error("Data missing timestamp column")
            elif df.empty:
                st.info("No historical data available. Configure cells and start monitoring.")
            elif not selected_cells:
                st.info("Please select at least one cell to display data.")
            elif not selected_types:
                st.info("Please select at least one cell type to display data.")
        
        except Exception as e:
            st.error(f"Error filtering data: {str(e)}")
            filtered_df = pd.DataFrame()
        
        # Display filtered data with better error handling
        if not filtered_df.empty:
            try:
                # Format the dataframe for display
                display_df = filtered_df.copy()
                
                # Format columns if they exist
                format_dict = {}
                if 'voltage' in display_df.columns:
                    format_dict['voltage'] = '{:.2f}V'
                if 'current' in display_df.columns:
                    format_dict['current'] = '{:.2f}A'
                if 'temperature' in display_df.columns:
                    format_dict['temperature'] = '{:.1f}°C'
                if 'capacity' in display_df.columns:
                    format_dict['capacity'] = '{:.2f}Wh'
                
                st.dataframe(
                    display_df.style.format(format_dict) if format_dict else display_df,
                    use_container_width=True,
                    height=400
                )
                
                # Export options
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("📥 Download CSV", use_container_width=True, key="download_csv_btn"):
                        csv = filtered_df.to_csv(index=False)
                        st.download_button(
                            label="💾 Download",
                            data=csv,
                            file_name=f"battery_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv",
                            key="download_csv_actual"
                        )
                
                with col2:
                    if st.button("📊 Generate Report", use_container_width=True, key="generate_report_btn"):
                        st.success("📄 Report generation feature coming soon!")
                        
            except Exception as e:
                st.error(f"Error displaying data: {str(e)}")
                st.info("Please try refreshing the data or reconfiguring cells.")
        else:
            if df.empty:
                st.info("📊 No historical data available. Please configure cells in the Setup page and start monitoring in the Control Panel.")
            else:
                st.info("No data matches the selected filters. Try adjusting your filter criteria.")
    
    else:
        st.info("📊 No data available. Please configure cells in the Setup page and start monitoring in the Control Panel.")

# Auto-refresh for real-time updates
if st.session_state.charging_status in ["Charging", "Discharging"] and page == "🎛️ Control Panel":
    time.sleep(1)
    st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem;'>
    <p>🔋 BatteryFlow Pro v2.1 | Advanced Battery Management System</p>
    <p>Built with ❤️ using Streamlit & Plotly | Real-time Monitoring Enabled</p>
</div>
""", unsafe_allow_html=True)