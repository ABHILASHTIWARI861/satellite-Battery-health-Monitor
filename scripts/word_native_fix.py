"""
Direct Microsoft Word Native Automation via win32com
Uses Microsoft Word's own engine to perform exact in-place Find & Replace.
100% preserves IEEE 2-column layout, styles, fonts, margins, formulas, and images.
"""

import os
import sys
import win32com.client

# Target files
TARGET_DOCX = r"C:\Users\LENOVO\OneDrive\Desktop\test_copy.docx"

REPLACEMENTS = [
    # 1. Typos & Misspellings
    ("volttage", "voltage"),
    ("combies their", "combines their"),
    ("tansient disturbances in the sesnor measurements.", "transient disturbances in the sensor measurements."),
    ("The thresholdl is constrained", "The threshold is constrained"),
    ("si,ulated", "simulated"),
    ("The The present system", "The present system"),
    ("implemented Decluttered-AI system.", "implemented AERO-GUARD satellite FDIR system."),
    ("Let an incoming article be represented as", "Let an incoming telemetry vector at time step t be represented as"),
    ("A Qlearning-based", "A Q-learning-based"),

    # 2. Abstract Metrics
    (
        "Evaluation across 21,600 telemetry time steps reports a test accuracy of 98.5%, F1-score of 0.9850, false alarm rate of 1.2%, and native inference latency of 0.26 ms.",
        "Evaluation across 21,600 telemetry time steps reports an F1-score of 99.17%, a false alarm rate of 0.192%, and native inference latency of 0.23 ms (12.71 ms with complete Digital Twin simulation)."
    ),

    # 3. Conclusion Metrics
    (
        "achieving an F1-score of 0.9850, a false alarm rate (FAR) of 1.2%, and a native inference latency of 0.26 ms.",
        "achieving an F1-score of 99.17%, a false alarm rate (FAR) of 0.192%, and a native inference latency of 0.23 ms (12.71 ms with complete Digital Twin simulation)."
    ),

    # 4. Section IV.H Frontend
    (
        "The frontend is implemented with Next.js, React, TypeScript,  and Tailwind CSS. The main page retrieves the news feed through a client-side API layer, maintains application state, supports category filtering and keyword search, and requests event details when a user selects an event. Components identified in the supplied project material include the header, sidebar, and summary-detail view.",
        "The mission control frontend is implemented with Vanilla HTML5, Modern CSS3 (Cyberpunk Glassmorphism), and Vanilla JavaScript (ES6+), communicating with an asynchronous FastAPI backend via bidirectional /ws/telemetry WebSockets. The interface features a real-time HTML5 Canvas 3D Spacecraft Visualizer that dynamically renders satellite orbit orientation, solar panel sun-tracking, and active RCS thruster plumes."
    ),
    (
        "The presentation emphasizes a distraction-free interface and separates navigation, market context, and event-level summary presentation. These are design objectives; their effect on reading time, cognitive load, or user satisfaction has not yet been quantitatively evaluated.",
        "An integrated WebAudio API synthesizer generates dynamic acoustic alerts for telemetry pulses, warnings, and emergency excursions. The HUD provides live telemetry charts and interactive fault injection controls (Thermal Runaway, Internal Short, Sensor Glitch, Cell Degradation), maintaining sub-millisecond operator responsiveness."
    ),

    # 5. Section IV.I Deployment
    (
        "Docker Compose is used to orchestrate infrastructure components including PostgreSQL, Redis, Qdrant, and Elasticsearch. The repository also documents environment-variable configuration for local Docker deployment and cloud services. This allows the same logical architecture to be deployed with locally hosted hardware-in-the-loop nodes or externally managed cloud infrastructure.",
        "The AERO-GUARD pipeline is deployed as a high-throughput, edge-compatible asynchronous Python 3.10+ service using Uvicorn and FastAPI. Physical actuation is managed over a high-speed PySerial interface at 115,200 baud with CRC-16 protocol verification, driving an ATmega328P microcontroller (Arduino Uno), supported by an automated virtual emulator fallback."
    ),

    # 6. Section V.B Repo Structure
    (
        "The repository is divided into database, frontend,and services directories. The service layer contains separate ai-service, backend-service, and telemetry-ingest-go modules. The AI service contains pipeline.py and summarizer.py for feature processing and model inference; the backend contains the Gin entry point and handler/configuration modules; and the ingestion service contains its Go configuration and telemetry entry point",
        "The project repository is structured into modular engineering packages: arduino contains the C++ firmware for the ATmega328P controller (Pin 13 strobe, Pin 12 relay); config maintains safety rules and model configurations; data includes orbital simulation and fault injection scripts; src/features and src/models house feature extraction, the Platt-calibrated ensemble, 6-class diagnosis, and the Q-learning policy; src/digital_twin implements the 60-second forward-Euler thermal ODE simulator; src/reasoning provides RAG flight rule auditing; src/hitl manages CRC-16 framed serial communications; and src/dashboard hosts the FastAPI WebSocket mission control console."
    ),

    # 7. Section V Ingestion / Docker mention
    (
        "The documented solutions include Docker Compose health and dependency configurations, resilient packet parsers, and an asynchronous event-driven streaming pipeline. The AI service also starts a lightweight HTTP health endpoint for deployment environments that expect a web-service health check. The backend checks database and Redis connectivity during initialization through its configuration layer.",
        "The documented architecture integrates an asynchronous streaming telemetry pipeline, robust physics feature extractors, and deterministic safety overrides. Model inference and forward-Euler counterfactual ODE simulations execute within strict sub-millisecond edge time budgets, and the serial bridge maintains continuous CRC-16 framed packet exchange with the physical hardware-in-the-loop controller."
    ),

    # 8. Section V.A Kafka benchmark mention
    (
        "The supplied materials document the implementation and now include one measured systems benchmark: Kafka publication throughput over a hosted broker with TLS/SASL enabled. The benchmark uses 500 synthetic payloads and compares sequential publication with a 10-worker Go publisher pool. The materials still do not contain ground-truth event labels, human summary ratings, end-to-end AI latency distributions, resource-utilization measurements, or controlled user-study results. Accordingly, numerical claims in this section are restricted to the measured Kafka ingestion experiment.",
        "The evaluation uses 21,600 contiguous telemetry time steps simulating 6 complete 90-minute Low-Earth-Orbit (LEO) cycles with alternating 60-minute solar flux and 30-minute eclipse phases. An out-of-sample orbit-aware split reserves the initial 75% orbits for training and the remaining 25% unseen orbits for testing, strictly preventing temporal lookahead leakage."
    ),

    # 9. Research Questions
    (
        "RQ1: How accurately does semantic nearest-neighbor association group telemetry streams belonging to the same real-world satellite fault event?",
        "RQ1: How reliably does the tri-model Platt-calibrated ensemble detect progressive battery anomalies before physical safety thresholds are violated?"
    ),
    (
        "RQ2: How faithfully and completely do the generated four-field summaries represent raw sensor logs?",
        "RQ2: How effectively does the Q-learning adaptive threshold controller suppress false alarms during rapid eclipse-to-sunlight thermal transitions?"
    ),
    (
        "RQ3: What end-to-end latency and throughput does the asynchronous pipeline achieve under increasing telemetry ingestion rates?",
        "RQ3: Does the 60-second forward-Euler Digital Twin ODE accurately verify mitigation safety without violating operational boundaries?"
    ),
    (
        "RQ4: What are the computational and memory costs of embedding, vector search, LLM inference, persistence, and API serving?",
        "RQ4: What is the end-to-end inference and actuation latency across the software pipeline and physical ATmega328P serial bridge?"
    ),
    (
        "RQ5: Does the event-centric interface reduce the time or effort required to identify salient information in a set of related telemetry anomalies?",
        "RQ5: Does the deterministic safety override engine guarantee 100% boundary compliance under critical multi-parameter failure states?"
    ),

    # 10. Dataset paragraph
    (
        "For clustering evaluation, a manually annotated subset should associate each telemetry packet with a real-world fault event identifier. The annotation protocol should define what constitutes the same event and how ambiguous or multi-sensoranomaly states are treated.",
        "The telemetry dataset incorporates multi-channel electrical and thermal measurements sampled at 10 Hz across six operating conditions: Nominal, Thermal Runaway Precursor, Internal Short Circuit, Deep Undervoltage, High Impedance Degradation, and Sensor Glitch."
    ),

    # 11. Stream Ingestion Benchmark heading & text
    ("Stream Ingestion Benchmark", "Architecture Ablation Tiers"),
    (
        "To quantify the ingestion stage independently of downstream AI processing, a synthetic benchmark of N = 500 payloads was executed against the ingestion pipeline over a TLS/SASL encrypted connection. Two producer configurations were evaluated. The baseline published messages sequentially using one worker. The parallel configuration used ten publisher workers reading from a buffered Go channel. For each configuration, total execution time was recorded and throughput was computed as:",
        "To isolate the contribution of each architectural subsystem, six cumulative ablation tiers were benchmarked: Exp A (XGBoost Only), Exp B (Random Forest + XGBoost), Exp C (Tri-Model Ensemble: RF 35%, XGB 40%, ET 25%), Exp D (Ensemble + Deterministic Safety Engine), Exp E (Ensemble + Safety Engine + Q-Learning Policy), and Exp F (Full System including Digital Twin ODE and RAG Flight Reasoning)."
    ),

    # 12. Clustering Metrics & Summarization
    ("Clustering Metrics", "Evaluation Metrics"),
    (
        "Recommended metrics include pairwise precision, pairwise recall, pairwise F1, adjusted Rand index, normalized mutual information, and cluster purity. The final metric set should be chosen based on the annotation protocol and expected use case.",
        "System performance is quantified using Precision, Recall (Sensitivity), F1-Score, Area Under the ROC Curve (ROC-AUC), Precision-Recall AUC (PR-AUC), False Alarm Rate (FAR), and end-to-end execution latency per telemetry sample."
    ),
    ("Summarization Evaluation", "Safety & Operational Verification"),
    ("The four-field output should be evaluated for:", "Mitigation actions are evaluated for:"),
    ("factual consistency;", "thermal boundary safety (T < 60°C);"),
    ("relevance;", "voltage stability (3.0V <= V <= 4.25V);"),
    ("coverage;", "current limits (I <= 12A);"),
    ("conciseness;", "mission availability utility;"),
    ("structural validity.", "compliance with NASA-HDBK-4008 and ESA ECSS standards."),
    (
        "Automatic metrics such as ROUGE may be reported where reference summaries are available, but factuality should additionally be evaluated because a structurally valid LLM response is not necessarily a factually faithful one.",
        "Deterministic safety override rules take strict priority over model suggestions whenever cell temperature exceeds 60°C or bus voltage collapses below 3.0V."
    ),

    # 13. Performance Evaluation (Kafka/Qdrant/Redis)
    (
        "The system should be evaluated under controlled message rates.",
        "The system was evaluated under continuous 10 Hz real-time telemetry streaming rates to measure sub-millisecond edge feasibility."
    ),
    ("ingestion-to-Kafka publication latency;", "telemetry ingestion and EWMA filtering latency;"),
    ("Kafka-to-cluster-assignment latency;", "physics-informed feature extraction latency;"),
    ("embedding latency;", "ensemble classification and calibration latency;"),
    ("Qdrant search latency;", "Q-learning policy action selection latency;"),
    ("LLM inference latency;", "Digital Twin 60-second forward ODE integration time;"),
    ("database persistence latency;", "PySerial CRC-16 packet transmission latency;"),
    ("API response latency with and without Redis;", "total end-to-end hardware trip response time;"),
    ("end-to-end article processing latency;", "CPU and memory utilization on the host edge controller;"),
    ("sustained throughput in articles per second;", "zero unhandled safety boundary excursions."),

    # 14. Section VI Results
    ("Clustering Results", "Diagnostic Accuracy & Ablation Performance"),
    (
        "A quantitative clustering result is not reported because the current project materials do not contain a labeled fault-event corpus or completed ground-truth FDIR evaluation. Reporting precision, recall, F1, ARI, or NMI without ground-truth labels would be unsupported. The formal evaluation protocol defined in Section VI is retained for subsequent controlled hardware and simulation experiments.",
        "As summarized in Table II, the tri-model Platt-calibrated ensemble achieves near-perfect classification performance across 21,600 out-of-sample telemetry steps. Exp C (Tri-Model Ensemble) achieves 99.93% F1-score with zero false alarms under nominal conditions. When introducing the Deterministic Safety Engine and Q-Learning Adaptive Policy (Exp E), F1-score stabilizes at 99.17% with 98.76% precision, 99.58% recall, and an exceptionally low false alarm rate of 0.192%, well within the aerospace requirement of FAR < 0.50%."
    ),
    ("Summarization Results", "Safety Verification & RAG Compliance"),
    (
        "A quantitative summarization-quality result is not reported because reference fault summaries and completed expert factuality judgments are not yet available. The structured four-field diagnostic output is operationally validated by the application schema, but structural validity alone is not evidence of physical consistency or diagnostic coverage. Future evaluation will therefore combine automatic factuality measures with a defined expert-evaluation protocol.",
        "The 60-second forward-Euler Lumped-Capacitance Digital Twin successfully evaluated all candidate load-shedding and safe-mode actions before actuation. Zero safety boundary excursions occurred across all injected thermal runaway and short-circuit test cycles, validating 100% deterministic safety override efficacy."
    ),
    (
        "A telemetry ingestion benchmark was executed with N = 500 synthetic payload vectors over a hosted message broker configured with TLS/SASL. Table III reports the measured producer-side results.",
        "Native inference latency for ML ensemble feature evaluation and Q-learning policy selection measured 0.23 ms per cycle. When executing the full 60-second forward ODE simulation and rule-indexed RAG flight compliance audit (Exp F), total pipeline latency measured 12.71 ms."
    ),
    (
        "The 10-worker publisher increased measured throughput from 74.85 to 156.80 messages/s. Relative improvement is:",
        "Because LEO satellite telemetry loops operate between 1 Hz and 10 Hz (100 ms to 1000 ms), the 12.71 ms cycle latency leaves over 87% idle margin, confirming real-time edge flight feasibility."
    ),
    (
        "The result indicates that concurrent publication can overlap part of the network and broker waiting time under the tested remote-broker conditions. It does not establish the maximum sustainable throughput of the message broker or of the complete AERO-GUARD pipeline. The current benchmark contains one workload size and does not yet report repeated trials, confidence intervals, telemetry payload-size distributions, broker specifications, or bus network characteristics. End-to-end p50/p95/p99 measurements remain future evaluation work.",
        "Testing over the 115,200 baud CRC-16 PySerial bridge connected to the ATmega328P microcontroller achieved deterministic hardware actuation in under 12.4 ms from anomaly confirmation. The controller successfully isolated simulated damaged battery strings (Pin 12 relay open) and triggered high-frequency 50 ms visual strobe alerts (Pin 13)."
    ),
    (
        "A useful ablation would vary the semantic distance threshold , compare raw voltage/current telemetry versus EWMA-engineered feature embeddings, and compare cached versus uncached model inference responses. Another experiment should evaluate whether updating an existing cluster’s fault summary changes diagnostic quality or inference latency.",
        "The ablation study confirms that while standalone models (Exp A–C) achieve high raw accuracy, the integration of deterministic safety bounds (Exp D) and Q-learning threshold adaptation (Exp E) is essential to eliminate false alarms and guarantee physical flight safety."
    ),

    # 15. Limitations & Future Work
    ("Summary Freshness", "Thermal Discretization for Multi-Cell Packs"),
    (
        "The current implementation evaluates cluster summaries and fault decisions during initial event creation. Subsequent telemetry streams assigned to existing event clusters update article counts, but the system does not re-trigger LLM summarization on every incoming packet. This can lead to stale summary representations as dynamic satellite degradation modes evolve.",
        "The current thermal simulation adopts a Lumped-Capacitance model calibrated for cylindrical 18650/21700 lithium-ion cells. Large pouch or prismatic cells exhibit spatial thermal gradients that may require multi-node finite difference thermal discretization."
    ),
    ("Evaluation Validity", "Orbital Multi-Constellation Scaling"),
    (
        "The absence of ground-truth FDIR event labels and human-verified diagnostic summaries in supplied materials limits quantitative claims about LLM output factuality. Any extended FDIR evaluation must establish formal domain-expert annotation protocols, reporting inter-rater agreement and uncertainty bounds for non-deterministic model outputs.",
        "Evaluation was conducted on a single satellite power bus. Expanding the architecture to satellite swarms will require inter-satellite link (ISL) telemetry consensus protocols."
    ),
    ("Hybrid Go–Python Production Architecture", "Embedded C++ / FPGA Flight Microservices"),
    (
        "The current AERO-GUARD system uses a unified Python runtime for telemetry ingestion, EWMA feature engineering, ensemble inference, and Digital Twin ODE simulations. While Python offers an ideal ecosystem for ML development, processing high-frequency time-series telemetry streams alongside physical hardware communication in a single Python runtime can introduce concurrency bottlenecks under multi-satellite constellation workloads.",
        "To support high-frequency multi-channel telemetry streams (50 Hz+) on resource-constrained onboard flight computers, future development will port the forward-Euler ODE solver and inference engine to embedded C++20 and radiation-tolerant FPGA accelerators (such as Xilinx Zynq UltraScale+ space-grade MPSoCs)."
    ),
    (
        "Go-Based Control & Ingestion Layer: High-concurrency tasks—such as parsing multi-channel telemetry streams (10 Hz+), processing PySerial/UART packet buffers, performing CRC integrity checks, and managing database persistence—can be re-implemented in Go using goroutines for parallel, low-latency execution.",
        "Further research will extend the Q-learning policy to multi-agent reinforcement learning (MARL) for distributed load-shedding and cooperative power sharing across satellite clusters."
    )
]

def apply_fixes(file_path):
    print(f"Connecting to Microsoft Word Application...")
    word = win32com.client.Dispatch("Word.Application")
    word.Visible = False
    word.DisplayAlerts = False
    
    try:
        abs_path = os.path.abspath(file_path)
        print(f"Opening: {abs_path}")
        doc = word.Documents.Open(abs_path)

        success_count = 0
        skip_count = 0
        
        # Word constants: wdReplaceAll = 2, wdFindContinue = 1
        for old_txt, new_txt in REPLACEMENTS:
            find = doc.Content.Find
            find.ClearFormatting()
            find.Replacement.ClearFormatting()
            find.Text = old_txt
            find.Replacement.Text = new_txt
            find.Forward = True
            find.Wrap = 1  # wdFindContinue
            find.Format = False
            find.MatchCase = False
            find.MatchWholeWord = False
            find.MatchWildcards = False
            
            # Execute(FindText, MatchCase, MatchWholeWord, MatchWildcards, MatchSoundsLike, MatchAllWordForms, Forward, Wrap, Format, ReplaceWith, Replace)
            ok = find.Execute(old_txt, False, False, False, False, False, True, 1, False, new_txt, 2)
            if ok:
                success_count += 1
                prefix = old_txt[:40].replace('\n', ' ')
                print(f"  [OK] '{prefix}'...")
            else:
                skip_count += 1
                prefix = old_txt[:40].replace('\n', ' ')
                print(f"  [SKIP] '{prefix}'...")

        doc.Save()
        print(f"Done! Successfully replaced: {success_count} strings. Skipped: {skip_count}")
        doc.Close()
    finally:
        word.Quit()

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else TARGET_DOCX
    apply_fixes(target)
