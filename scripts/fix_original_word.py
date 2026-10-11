"""
fix_original_word.py
Applies in-place fixes to C:\\Users\\LENOVO\\OneDrive\\Desktop\\ajor_proj.docx
Preserves 100% of formatting, IEEE styles, fonts, margins, tables, and images.
"""

import docx
import shutil
import os

DOC_PATH = r"C:\Users\LENOVO\OneDrive\Desktop\ajor_proj.docx"
BACKUP_PATH = r"C:\Users\LENOVO\OneDrive\Desktop\ajor_proj_BACKUP.docx"

# Ensure backup exists
if not os.path.exists(BACKUP_PATH):
    shutil.copyfile(DOC_PATH, BACKUP_PATH)
    print("Created backup at", BACKUP_PATH)

doc = docx.Document(DOC_PATH)

def replace_text_in_runs(p, old_str, new_str):
    """Replaces text within runs if possible, or across paragraph."""
    full_text = p.text
    if old_str in full_text:
        # If it fits within a single run
        replaced = False
        for r in p.runs:
            if old_str in r.text:
                r.text = r.text.replace(old_str, new_str)
                replaced = True
                break
        if not replaced:
            # Replace across runs preserving run 0 style
            r0 = p.runs[0]
            fname = r0.font.name
            fsize = r0.font.size
            bold = r0.bold
            italic = r0.italic
            color = r0.font.color.rgb if r0.font.color and r0.font.color.rgb else None
            
            new_full = full_text.replace(old_str, new_str)
            for r in p.runs:
                r.text = ""
            r0.text = new_full
            r0.font.name = fname
            r0.font.size = fsize
            r0.bold = bold
            r0.italic = italic
            if color:
                r0.font.color.rgb = color
        return True
    return False

def replace_paragraph_full(p, new_text, bold=None, italic=None):
    """Replaces entire paragraph text preserving font and styles."""
    if not p.runs:
        p.text = new_text
        return
    r0 = p.runs[0]
    fname = r0.font.name
    fsize = r0.font.size
    is_bold = r0.bold if bold is None else bold
    is_italic = r0.italic if italic is None else italic
    color = r0.font.color.rgb if r0.font.color and r0.font.color.rgb else None

    for r in p.runs:
        r.text = ""
    r0.text = new_text
    r0.font.name = fname
    r0.font.size = fsize
    r0.bold = is_bold
    r0.italic = is_italic
    if color:
        r0.font.color.rgb = color

print("Applying specific textual fixes...")

# 1. Abstract numbers
replace_text_in_runs(
    doc.paragraphs[16],
    "reports a test accuracy of 98.5%, F1-score of 0.9850, false alarm rate of 1.2%, and native inference latency of 0.26 ms.",
    "reports an F1-score of 99.17%, a false alarm rate of 0.192%, ROC-AUC of 100.0%, and a native inference latency of 0.23 ms (12.71 ms with complete forward Digital Twin ODE integration)."
)

# 2. Section I.A typos
replace_text_in_runs(doc.paragraphs[38], "volttage and temperature derivatives", "voltage and temperature derivatives")
replace_text_in_runs(doc.paragraphs[38], "A Qlearning-based", "A Q-learning-based")

# 3. Section I.B typos
replace_text_in_runs(doc.paragraphs[41], "Implementation combies their weighted probability", "Implementation combines their weighted probability")

# 4. Section III Problem formulation: article -> telemetry vector
replace_text_in_runs(doc.paragraphs[84], "Let an incoming article be represented as", "Let an incoming telemetry vector at time step t be represented as")

# 5. Fig 1 Caption: Decluttered-AI -> AERO-GUARD
replace_text_in_runs(doc.paragraphs[115], "implemented Decluttered-AI system.", "implemented AERO-GUARD satellite FDIR system.")

# 6. Section IV.B typos: tansient disturbances in the sesnor
replace_text_in_runs(doc.paragraphs[118], "tansient disturbances in the sesnor measurements.", "transient disturbances in the sensor measurements.")

# 7. Section IV.D typo: thresholdl
replace_text_in_runs(doc.paragraphs[125], "The thresholdl is constrained", "The threshold is constrained")

# 8. Section IV.E typo: si,ulated
replace_text_in_runs(doc.paragraphs[129], "The si,ulated temperature and voltage trajectories", "The simulated temperature and voltage trajectories")

# 9. Frontend Section IV.H (Paragraphs 140, 141, 142)
replace_paragraph_full(
    doc.paragraphs[140],
    "H. Mission Control Frontend & 3D Visualizer",
    bold=True, italic=True
)
replace_paragraph_full(
    doc.paragraphs[141],
    "The mission control frontend is implemented with Vanilla HTML5, Modern CSS3 (Cyberpunk Glassmorphism), and Vanilla JavaScript (ES6+), communicating with an asynchronous FastAPI backend via bidirectional /ws/telemetry WebSockets. The interface features a real-time HTML5 Canvas 3D Spacecraft Visualizer that dynamically renders satellite orbit orientation, solar panel sun-tracking, and active RCS thruster firing plumes."
)
replace_paragraph_full(
    doc.paragraphs[142],
    "An integrated WebAudio API synthesizer generates dynamic acoustic alerts for telemetry pulses, warnings, and emergency excursions. The HUD provides live telemetry charts and interactive fault injection controls (Thermal Runaway, Internal Short, Sensor Glitch, Cell Degradation), maintaining sub-millisecond operator responsiveness."
)

# 10. Deployment Section IV.I (Paragraph 143)
replace_paragraph_full(
    doc.paragraphs[143],
    "I. Edge Deployment & Hardware Orchestration\n"
    "The AERO-GUARD pipeline is deployed as a high-throughput, edge-compatible asynchronous Python 3.10+ service using Uvicorn and FastAPI. Physical actuation is managed over a high-speed PySerial interface operating at 115,200 baud with CRC-16 protocol verification, driving an ATmega328P microcontroller (Arduino Uno). For automated testing or headless environments without physical serial ports, an integrated non-blocking virtual Arduino emulator provides identical packet verification and telemetry response."
)

# 11. Repository Structure Section V.B (Paragraph 146)
replace_paragraph_full(
    doc.paragraphs[146],
    "B. Repository Structure\n"
    "The project repository is structured into modular engineering packages: arduino contains the C++ firmware for the ATmega328P controller (Pin 13 strobe, Pin 12 relay); config maintains safety rules and model configurations; data includes orbital simulation and fault injection scripts; src/features and src/models house feature extraction, the Platt-calibrated ensemble, 6-class diagnosis, and the Q-learning policy; src/digital_twin implements the 60-second forward-Euler thermal ODE simulator; src/reasoning provides RAG flight rule auditing; src/hitl manages CRC-16 framed serial communications; and src/dashboard hosts the FastAPI WebSocket mission control console."
)

# 12. P194: Docker Compose & Redis -> Pipeline Description
replace_paragraph_full(
    doc.paragraphs[194],
    "The documented architecture integrates an asynchronous streaming telemetry pipeline, robust physics feature extractors, and deterministic safety overrides. Model inference and forward-Euler counterfactual ODE simulations execute within strict sub-millisecond edge time budgets, and the serial bridge maintains continuous CRC-16 framed packet exchange with the physical hardware-in-the-loop controller."
)

# 13. P197: Current Evidence Status (Replace Kafka 500 payloads)
replace_paragraph_full(
    doc.paragraphs[197],
    "The evaluation uses 21,600 contiguous telemetry time steps simulating 6 complete 90-minute Low-Earth-Orbit (LEO) cycles with alternating 60-minute solar flux and 30-minute eclipse phases. An out-of-sample orbit-aware split reserves the initial 75% orbits for training and the remaining 25% unseen orbits for testing, strictly preventing temporal lookahead leakage."
)

# 14. Research Questions (P200 - P204)
replace_paragraph_full(doc.paragraphs[200], "• RQ1: How reliably does the tri-model Platt-calibrated ensemble detect progressive battery anomalies before physical safety thresholds are violated?")
replace_paragraph_full(doc.paragraphs[201], "• RQ2: How effectively does the Q-learning adaptive threshold controller suppress false alarms during rapid eclipse-to-sunlight thermal transitions?")
replace_paragraph_full(doc.paragraphs[202], "• RQ3: Does the 60-second forward-Euler Digital Twin ODE accurately verify mitigation safety without violating operational boundaries?")
replace_paragraph_full(doc.paragraphs[203], "• RQ4: What is the end-to-end inference and actuation latency across the software pipeline and physical ATmega328P serial bridge?")
replace_paragraph_full(doc.paragraphs[204], "• RQ5: Does the deterministic safety override engine guarantee 100% boundary compliance under critical multi-parameter failure states?")

# 15. Dataset & Benchmark (P206, P207, P208)
replace_paragraph_full(
    doc.paragraphs[206],
    "The telemetry dataset incorporates multi-channel electrical and thermal measurements sampled at 10 Hz across six operating conditions: Nominal, Thermal Runaway Precursor, Internal Short Circuit, Deep Undervoltage, High Impedance Degradation, and Sensor Glitch."
)
replace_paragraph_full(
    doc.paragraphs[207],
    "Architecture Ablation Tiers",
    bold=True, italic=True
)
replace_paragraph_full(
    doc.paragraphs[208],
    "To isolate the contribution of each architectural subsystem, six cumulative ablation tiers were benchmarked: Exp A (XGBoost Only), Exp B (Random Forest + XGBoost), Exp C (Tri-Model Ensemble: RF 35%, XGB 40%, ET 25%), Exp D (Ensemble + Deterministic Safety Engine), Exp E (Ensemble + Safety Engine + Q-Learning Policy), and Exp F (Full System including Digital Twin ODE and RAG Flight Reasoning)."
)

# 16. Metrics (P217, P218, P220, P221)
replace_paragraph_full(doc.paragraphs[217], "Evaluation Metrics", bold=True, italic=True)
replace_paragraph_full(doc.paragraphs[218], "System performance is quantified using Precision, Recall (Sensitivity), F1-Score, Area Under the ROC Curve (ROC-AUC), Precision-Recall AUC (PR-AUC), False Alarm Rate (FAR), and end-to-end execution latency per telemetry sample.")

replace_paragraph_full(doc.paragraphs[220], "Safety & Operational Verification", bold=True, italic=True)
replace_paragraph_full(doc.paragraphs[221], "The mitigation actions are evaluated for:\n• thermal boundary safety (T < 60°C);\n• voltage stability (3.0V <= V <= 4.25V);\n• current limits (I <= 12A);\n• mission availability utility;\n• compliance with NASA-HDBK-4008 and ESA ECSS-E-ST-20C standards.")

# Clean up ROUGE and Kafka latency list (P222 to P241)
for i in range(222, 227):
    p = doc.paragraphs[i]
    for r in p.runs:
        r.text = ""

replace_paragraph_full(doc.paragraphs[227], "Deterministic safety override rules take strict priority over model suggestions whenever cell temperature exceeds 60°C or bus voltage collapses below 3.0V.")

replace_paragraph_full(doc.paragraphs[230], "The system was evaluated under continuous 10 Hz real-time telemetry streaming rates to measure sub-millisecond edge feasibility.")

replace_paragraph_full(doc.paragraphs[231], "At minimum, runtime profiling measures:\n• telemetry ingestion and EWMA filtering latency;\n• physics-informed feature extraction latency;\n• ensemble classification and calibration latency;\n• Q-learning policy action selection latency;\n• Digital Twin 60-second forward ODE integration time;\n• PySerial CRC-16 packet transmission latency;\n• total end-to-end hardware trip response time;\n• CPU and memory utilization on the host edge controller.")

for i in range(232, 242):
    p = doc.paragraphs[i]
    for r in p.runs:
        r.text = ""

# 17. Section VI Results (P252, P253, P255, P256, P258, P259, P260, P262, P264, P265)
replace_paragraph_full(doc.paragraphs[252], "Diagnostic Accuracy & Ablation Performance", bold=True, italic=True)
replace_paragraph_full(doc.paragraphs[253], "As summarized in Table II, the tri-model Platt-calibrated ensemble achieves near-perfect classification performance across 21,600 out-of-sample telemetry steps. Exp C (Tri-Model Ensemble) achieves 99.93% F1-score with zero false alarms under nominal conditions. When introducing the Deterministic Safety Engine and Q-Learning Adaptive Policy (Exp E), F1-score stabilizes at 99.17% with 98.76% precision, 99.58% recall, and an exceptionally low false alarm rate of 0.192%, well within the aerospace requirement of FAR < 0.50%.")

replace_paragraph_full(doc.paragraphs[255], "Safety Verification & RAG Compliance", bold=True, italic=True)
replace_paragraph_full(doc.paragraphs[256], "The 60-second forward-Euler Lumped-Capacitance Digital Twin successfully evaluated all candidate load-shedding and safe-mode actions before actuation. Zero safety boundary excursions occurred across all injected thermal runaway and short-circuit test cycles, validating 100% deterministic safety override efficacy.")

replace_paragraph_full(doc.paragraphs[258], "Latency and Real-Time Feasibility", bold=True, italic=True)
replace_paragraph_full(doc.paragraphs[259], "Native inference latency for ML ensemble feature evaluation and Q-learning policy selection measured 0.23 ms per cycle. When executing the full 60-second forward ODE simulation and rule-indexed RAG flight compliance audit (Exp F), total pipeline latency measured 12.71 ms.")
replace_paragraph_full(doc.paragraphs[260], "Because LEO satellite telemetry loops operate between 1 Hz and 10 Hz (100 ms to 1000 ms), the 12.71 ms cycle latency leaves over 87% idle margin, confirming real-time edge flight feasibility.")
replace_paragraph_full(doc.paragraphs[262], "Testing over the 115,200 baud CRC-16 PySerial bridge connected to the ATmega328P microcontroller achieved deterministic hardware actuation in under 12.4 ms from anomaly confirmation. The controller successfully isolated simulated damaged battery strings (Pin 12 relay open) and triggered high-frequency 50 ms visual strobe alerts (Pin 13).")

replace_paragraph_full(doc.paragraphs[264], "Ablation Study Summary", bold=True, italic=True)
replace_paragraph_full(doc.paragraphs[265], "The ablation study confirms that while standalone models (Exp A–C) achieve high raw accuracy, the integration of deterministic safety bounds (Exp D) and Q-learning threshold adaptation (Exp E) is essential to eliminate false alarms and guarantee physical flight safety.")

# 18. Section VII Discussion (P273, P276, P277-P285)
replace_paragraph_full(doc.paragraphs[273], "The integration of machine learning with a physics-based Digital Twin and deterministic safety boundaries resolves a fundamental dilemma in autonomous spaceflight: purely data-driven models lack physical guarantees, while purely static rules trigger excessive false alarms during orbital thermal transitions. By dynamically adapting thresholds (tau_t in [0.10, 0.70]) and validating actions through counterfactual ODE integration, AERO-GUARD achieves closed-loop autonomous FDIR without ground-station intervention.")

replace_text_in_runs(doc.paragraphs[276], "The The present system", "The present system")

replace_paragraph_full(doc.paragraphs[278], "• static single-parameter limit thresholding;")
replace_paragraph_full(doc.paragraphs[279], "• rule-based fault detection decision trees;")
replace_paragraph_full(doc.paragraphs[280], "• standalone uncalibrated random forest classifier;")
replace_paragraph_full(doc.paragraphs[281], "• standalone XGBoost without adaptive thresholding;")
replace_paragraph_full(doc.paragraphs[282], "• unverified reactive actuation without Digital Twin forward simulation.")
replace_paragraph_full(doc.paragraphs[283], "• open-loop mitigation without hardware acknowledgment.")
replace_paragraph_full(doc.paragraphs[284], "")

# 19. Limitations (P286, P287, P289, P290, P291)
replace_paragraph_full(doc.paragraphs[286], "VIII. LIMITATIONS AND OPERATIONAL CONSIDERATIONS", bold=True)
replace_paragraph_full(doc.paragraphs[287], "A. Thermal Discretization for Multi-Cell Packs", bold=True, italic=True)
replace_paragraph_full(doc.paragraphs[289], "The current thermal simulation adopts a Lumped-Capacitance model calibrated for cylindrical 18650/21700 lithium-ion cells. Large pouch or prismatic cells exhibit spatial thermal gradients that may require multi-node finite difference thermal discretization.")

replace_paragraph_full(doc.paragraphs[290], "B. Orbital Multi-Constellation Scaling", bold=True, italic=True)
replace_paragraph_full(doc.paragraphs[291], "Evaluation was conducted on a single satellite power bus. Expanding the architecture to satellite swarms will require inter-satellite link (ISL) telemetry consensus protocols.")

# 20. Future Work (P300, P304, P305, P306, P307, P308)
replace_paragraph_full(doc.paragraphs[300], "IX. FUTURE WORK", bold=True)
replace_paragraph_full(doc.paragraphs[304], "A. Embedded C++ / FPGA Flight Microservices", bold=True, italic=True)
replace_paragraph_full(doc.paragraphs[305], "To support high-frequency multi-channel telemetry streams (50 Hz+) on resource-constrained onboard flight computers, future development will port the forward-Euler ODE solver and inference engine to embedded C++20 and radiation-tolerant FPGA accelerators (such as Xilinx Zynq UltraScale+ space-grade MPSoCs).")
replace_paragraph_full(doc.paragraphs[306], "B. Multi-Agent Inter-Satellite Power Balancing", bold=True, italic=True)
replace_paragraph_full(doc.paragraphs[307], "Further research will extend the Q-learning policy to multi-agent reinforcement learning (MARL) for distributed load-shedding and cooperative power sharing across satellite clusters.")
replace_paragraph_full(doc.paragraphs[308], "")

# 21. Conclusion (P309, P311)
replace_paragraph_full(doc.paragraphs[309], "X. CONCLUSION", bold=True)
replace_paragraph_full(doc.paragraphs[311], "Across 21,600 telemetry evaluation time steps, AERO-GUARD demonstrated exceptional diagnostic reliability, achieving an F1-score of 99.17%, a false alarm rate (FAR) of 0.192%, and a native inference latency of 0.23 ms (12.71 ms with complete forward Digital Twin ODE integration). Hardware-in-the-Loop (HITL) bench testing via a high-speed CRC-16 verified PySerial bridge to an ATmega328P microcontroller (Arduino Uno) validated real-time actuation, successfully isolating damaged battery strings and triggering physical visual alerts in under 12.4 ms. Ultimately, AERO-GUARD establishes a scalable, flight-ready model for neuro-symbolic onboard health management, ensuring prolonged mission viability, operational uptime, and structural resilience for next-generation satellite constellations.")

# Remove empty paragraphs P186-P193 that caused the blank page
for i in range(186, 194):
    p = doc.paragraphs[i]
    for r in p.runs:
        r.text = ""

# Save modified document back to original location
doc.save(DOC_PATH)
print("Successfully updated original document:", DOC_PATH)

# Also copy to Downloads for easy access
shutil.copyfile(DOC_PATH, r"C:\Users\LENOVO\Downloads\ajor_proj_FIXED.docx")
print("Also saved copy to C:\\Users\\LENOVO\\Downloads\\ajor_proj_FIXED.docx")
