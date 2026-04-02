🌍 IoT Environmental Monitoring System (MQTT-Based)
📌 Overview

This project presents a real-time IoT-based environmental monitoring system built using the MQTT protocol. The system simulates sensor data (temperature, air quality, humidity, water quality, etc.) and transmits it through a publish-subscribe architecture to enable efficient monitoring and analysis.

The project was developed as part of the KZ4005CMD – Integrative Project module at Coventry University Kazakhstan .

🚀 Key Features
📡 Real-time data transmission using MQTT
🌡️ Simulation of environmental sensors
📊 Data visualization via web dashboard
⚠️ Safety evaluation and alerts system
🔄 Scalable publish-subscribe architecture
🧠 Structured data processing (JSON-based)
🏗️ System Architecture

The system follows the MQTT client-broker model:

Sensors (Publishers)
Simulated devices generating environmental data
MQTT Broker
Handles message distribution between clients
Backend System (Subscriber)
Processes incoming data and performs analysis
Frontend Dashboard
Displays real-time data and system status
⚙️ Technologies Used
MQTT protocol
Python (backend logic & simulation)
JavaScript / HTML / CSS (frontend dashboard)
JSON (data format)
GitHub (version control)
🧪 How It Works
Sensor simulation scripts generate environmental data
Data is published to MQTT topics
Backend subscribes and processes incoming messages
Processed data is stored and evaluated
Frontend displays results in real time
▶️ Getting Started
Prerequisites
Python 3.x
MQTT Broker (e.g., Mosquitto)
Node.js (optional for frontend)

📊 Example Use Cases
Smart homes
Environmental monitoring systems
Industrial safety systems
Smart cities
👥 Team Members
👥 Team & Contributions
👨‍💻 Zhaksylyk (Jack) — Lead Developer & System Architect
Designed the overall architecture of the IoT environmental monitoring system
Implemented backend logic, MQTT communication flow, and sensor data processing
Developed safety evaluation algorithms for real-time monitoring
Integrated controllers, sensors, and backend into a unified system

Also:

Led the technical direction of the project
Helped with debugging and system integration
Contributed to system security and structured data flow
🎨 Alua — Front-End Developer & UI/UX Lead
Built the web dashboard using HTML, CSS, and JavaScript
Designed a responsive interface for real-time data visualization
Displayed sensor readings, system status, and safety indicators

Also:

Integrated frontend with backend APIs
Improved usability and ensured consistent design
🔗 Nelli — MQTT & Integration Developer / QA Lead
Worked on MQTT communication between sensors and backend
Ensured data was correctly transmitted and processed

Also:

Performed system and integration testing
Identified bugs and verified fixes
Ensured stable communication across system components
🔌 Rayimbek — Hardware & Security Specialist
Configured and integrated environmental sensors (air, water, temperature)
Verified correct data transmission to the MQTT system

Also:

Contributed to encryption and system security
Helped prepare and explain the hardware setup for the project demo
📝 Adil — Documentation & Planning / Data Integration
Managed project documentation (meeting notes, planning, Gantt chart)
Worked on JSON data handling
Integrated the water quality monitoring system into the project

Also:

Helped write report sections (introduction, planning)
Supported testing and kept documentation up to date
Assisted in preparing the final submission
📈 Project Contribution

Each team member contributed to:

System design and architecture
MQTT communication modeling
Implementation and testing
Integration of frontend and backend
🔒 Future Improvements
Add encryption for secure MQTT communication
Integrate real IoT hardware sensors
Improve scalability with cloud deployment
Apply machine learning for predictive analysis
📄 Documentation

Full project documentation, methodology, and results are included in the coursework report as required by the module guidelines .

📌 Notes
This project uses software-based sensor simulation, which is acceptable for academic IoT projects
Version control is maintained using GitHub with structured commits and updates
📜 License

This project is developed for academic purposes.
