import streamlit as st
import requests

# 1. Page Layout aur Title set karein
st.set_page_config(page_title="Cyber Shield NIDS", page_icon="🛡️", layout="centered")

st.title("🛡️ Network Intrusion Detection System")
st.write("Real-time network traffic scan karne ke liye niche details enter karein.")
st.markdown("---")

# Backend ka Base URL (Pakka karein ki aapka FastAPI isi par chal raha hai)
BACKEND_URL = "https://network-intrusion-detection-system-4ygf.onrender.com"

# 🟢 Sidebar mein Live Server Health Status check karna
try:
    health_response = requests.get(f"{BACKEND_URL}/")
    if health_response.status_code == 200:
        st.sidebar.success("🟢 API Server: ONLINE")
        st.sidebar.caption(f"Backend Version: {health_response.json().get('version', '1.0.0')}")
except requests.exceptions.ConnectionError:
    st.sidebar.error("🔴 API Server: OFFLINE")
    st.sidebar.warning("⚠️ Pehle 'main.py' ko uvicorn se start karein!")

# 2. Form Inputs (Sunder dikhne ke liye 2 columns mein split kiya hai)
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Basic Traffic Features")
    duration = st.number_input("Duration (seconds)", min_value=0, value=0)
    protocol_type = st.selectbox("Protocol Type", ["tcp", "udp", "icmp"])
    service = st.selectbox("Service Type", ["http", "smtp", "ftp", "private", "other", "domain", "eco_i"])
    flag = st.selectbox("Connection Flag", ["SF", "S0", "REJ", "RSTR", "RSTO"])
    src_bytes = st.number_input("Source Bytes (Client -> Server)", min_value=0, value=350)
    dst_bytes = st.number_input("Destination Bytes (Server -> Client)", min_value=0, value=4500)
    logged_in = st.selectbox("Is Logged In? (1=Yes, 0=No)", [1, 0])

with col2:
    st.subheader("🕵️‍♂️ Advanced Traffic Analytics")
    count = st.number_input("Count (Same host connections)", min_value=0, value=2)
    srv_count = st.number_input("Server Count (Same service connections)", min_value=0, value=2)
    serror_rate = st.slider("SYN Error Rate", 0.0, 1.0, 0.0)
    rerror_rate = st.slider("REJ Error Rate", 0.0, 1.0, 0.0)
    dst_host_count = st.number_input("Destination Host Count", min_value=0, value=10)
    dst_host_srv_count = st.number_input("Destination Host Server Count", min_value=0, value=255)
    dst_host_diff_srv_rate = st.slider("Host Diff Service Rate", 0.0, 1.0, 0.0)

st.markdown("---")

# 3. Predict Button aur Backend Communication
if st.button("🚀 Scan Network Traffic", use_container_width=True):
    
    # Data ka dictionary banayein jo FastAPI ka BaseModel maangta hai
    input_payload = {
        "duration": int(duration),
        "protocol_type": str(protocol_type),
        "service": str(service),
        "flag": str(flag),
        "src_bytes": int(src_bytes),
        "dst_bytes": int(dst_bytes),
        "logged_in": int(logged_in),
        "count": int(count),
        "srv_count": int(srv_count),
        "serror_rate": float(serror_rate),
        "rerror_rate": float(rerror_rate),
        "dst_host_count": int(dst_host_count),
        "dst_host_srv_count": int(dst_host_srv_count),
        "dst_host_diff_srv_rate": float(dst_host_diff_srv_rate)
    }
    
    try:
        with st.spinner("AI Brain analyze kar raha hai... Please wait."):
            # Backend ke /predict route par data bheja
            response = requests.post(f"{BACKEND_URL}/predict", json=input_payload)
            result_json = response.json()
            
        # 4. Response ko Screen par display karna
        if response.status_code == 200 and result_json.get("status") == "success":
            result_text = result_json["result"]
            confidence = result_json["confidence_score"]
            
            if "NORMAL" in result_text:
                st.success(f"### {result_text}")
                st.info(f"🛡️ AI Confidence Score: **{confidence}%** (Traffic Safe Hai)")
            else:
                st.error(f"### {result_text}")
                st.warning(f"🚨 ALERT: Immediate blocking required! AI Confidence Score: **{confidence}%**")
        else:
            st.error(f"❌ Backend Error: {result_json.get('message', 'Invalid Response')}")
            
    except requests.exceptions.ConnectionError:
        st.error("🔌 Connection Failed! Pakka karein ki aapka FastAPI server `main.py` chalu hai.")