# Forest AI Sentinel: Illegal Logging Detection Platform 🌲📡

An integrated, real-time geospatial monitoring and decision-support system designed to protect forest reserves from illegal logging and unauthorized activity. The platform integrates computer vision change detection, object detection, and sensor fusion algorithms to identify threats and dispatch alerts to forest protection forces.

---

## 🚀 Key Features

* **Multi-Modal Risk Fusion**: Merges acoustic, vibration, and motion alerts from simulated ground sensors with visual change metrics from aerial drone sweeps to compute regional threat levels.
* **Computer Vision Change Detection**: Utilizes OpenCV image subtraction to compute tree clearance ratios from temporal drone imagery.
* **YOLOv8 Security Monitoring**: Hooks pre-trained YOLOv8 models into drone scan feeds to flag trespassers and logging vehicles (trucks, cars, motorbikes) inside protected zones.
* **Live WebSocket Telemetry**: Broadcasts real-time grid status, sensor alerts, and coordinate updates to the monitoring dashboard.
* **Interactive Alert Dashboard**: Built with Leaflet.js to display zone grids, active alerts, live camera feeds, and custom image-upload testing panels.

---

## 🛠️ Tech Stack

* **Backend**: FastAPI (Python), WebSockets, Asyncio, Pydantic
* **Computer Vision & DL**: OpenCV, Ultralytics YOLOv8, TensorFlow/Keras (U-Net)
* **Data Handling**: Pandas, NumPy, Rasterio
* **Frontend**: HTML5, Vanilla CSS, JavaScript, Leaflet.js
* **Deployment**: Docker, Render Configs

---

## 📁 Project Structure

```text
forest-ai-main/
├── 📁 backend/                # FastAPI backend codebase
│   ├── 📁 api/                # REST router endpoints
│   ├── 📁 core/               # Configuration settings and thresholds
│   ├── 📁 models/             # Pydantic schemas for zones, grids, and telemetry
│   └── 📁 services/           # Telemetry simulators, risk engines, and schedulers
│       ├── platform_state.py  # Coordinates state and WebSocket broadcast loops
│       └── risk_service.py    # Risk fusion score calculator
├── 📁 data/                   # Telemetry and imagery database
│   └── 📁 raw/
│       ├── 📁 drone/          # Mock drone sweep directory pairs (21-04-26 vs 22-04-26)
│       └── 📁 sensor/         # Raw CSV baseline logs
├── 📁 frontend/               # Dashboard templates & static assets
│   ├── index.html             # Sentinel Platform login portal
│   ├── dashboard.html         # Live grid analytics view
│   ├── live.html              # WebSocket live streaming alert console
│   ├── simulate.html          # Custom image comparison simulation panel
│   └── 📁 js/                 # Map and API fetching script layers
├── 📁 models/                 # Deep learning & CV prediction architectures
│   ├── change_detection.py    # Grayscale difference masking calculator
│   ├── drone_model.py         # YOLOv8 target vehicle pipeline
│   └── unet_model.py          # Keras U-Net deforestation classifier
├── 📁 scripts/                # Utility execution scripts
│   └── run_pipeline.py        # Pipeline trigger
├── Dockerfile                 # Container deployment configuration
└── requirements.txt           # Python dependency specifications
```

---

## ⚙️ Setup & Installation

### 1. Prerequisites
Ensure you have **Python 3.9+** installed.

### 2. Install Dependencies
```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# Windows:
.\venv\Scripts\Activate.ps1
# macOS/Linux:
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

---

## 🏃 Running the Application

### 1. Start the FastAPI Server
Launch the backend server using Uvicorn:
```bash
uvicorn main:app --reload
```
The server will bind to `http://127.0.0.1:8000`.

### 2. Access the Dashboard
Open `http://127.0.0.1:8000` in your browser. 
- You will be greeted by the **Forest AI Portal**.
- Sign in with credentials: User: **`forestadmin`** / Pass: **`admin`**.

---

## 🧠 Core Algorithm Mechanics

### 1. Risk Fusion Scoring Formula
Threat calculation uses a multi-factor formula combining visual, acoustic, and spatial parameters:
$$\text{Score} = (0.45 \times \text{Drone CV Score}) + (0.35 \times \text{Sensor Alert Score}) + \text{Sensor Reliability} + \text{Hotspot Proximity}$$
- **Score $\ge$ 7.0**: Trigger `HIGH RISK` alert.
- **Score $\ge$ 4.0**: Trigger `MEDIUM RISK` warning.
- **Otherwise**: Marked as `LOW RISK` (Normal).

### 2. OpenCV Temporal Change Detection
Drone sweeps compute changes between two temporal images:
1. Downsample both files to $256 \times 256$ pixels.
2. Convert both to grayscale.
3. Compute the absolute difference: `diff = cv2.absdiff(yesterday, today)`.
4. Run binary thresholding (`val > 25`) to build the change mask.
5. Compute the ratio of changed pixels.

---

## ⚖️ Disclaimers & Licenses
This software is a decision-support prototype platform intended for monitoring and simulation purposes in educational or conservation staging environments. It should not be used as an official certified warning system.
