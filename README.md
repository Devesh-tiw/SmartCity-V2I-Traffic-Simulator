# SmartCity V2I Traffic & Emergency Simulator 🚦🚑

Traditional traffic management systems rely on static timers, causing fatal delays for emergency responders and creating unnecessary urban congestion.

This project is a purely software-based **Smart City Traffic Simulator** that models a 4-way intersection. It implements a mock **Vehicle-to-Infrastructure (V2I)** communication protocol, allowing authorized emergency vehicles to preempt traffic lights. It also features real-time weather adaptation and an integrated data analytics pipeline.

## ✨ Core Features

* **V2I Emergency Preemption:** Simulates RFID/DSRC handshakes. Operators can input transponder codes which are authenticated via **Regular Expressions (Regex)** to instantly grant a green light to emergency lanes.
* **Multithreaded Engine:** Utilizes Python `threading` to run the GUI, traffic cycle timers, and random vehicle generation concurrently without freezing the application.
* **Live Weather Adaptation:** Integrates **Web Scraping** (`requests` & `BeautifulSoup`) to monitor local weather. If rain or snow is detected, the system dynamically extends the yellow light duration for safer braking distances.
* **Database Logging:** Records every traffic light cycle, timestamp, and cleared vehicle count into a local **SQLite3** database.
* **Data Analytics & Visualization:** Uses **Pandas** to process the SQL data and **Seaborn/Matplotlib** to generate visual heatmaps and bar charts of intersection congestion.

## 🛠️ Technology Stack

* **Language:** Python 3.x
* **GUI Framework:** Tkinter
* **Data & Analytics:** Pandas, NumPy, Matplotlib, Seaborn
* **Database:** SQLite3
* **Web Scraping:** Requests, BeautifulSoup4

## 🚀 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/SmartCity-V2I-Traffic-Simulator.git
   cd SmartCity-V2I-Traffic-Simulator
   ```

2. **Install the required dependencies:**
   ```bash
   pip install pandas numpy matplotlib seaborn requests beautifulsoup4
   ```

3. **Run the simulation:**
   ```bash
   python mega_project.py
   ```

## 💻 How to Use the Simulator

1. **Observe Standard Operation:** Upon launching, the multithreaded engine will automatically generate vehicles and cycle the traffic lights.

2. **Trigger an Emergency:**
   - In the "Emergency V2I Transponder Override" input box, type an authorized packet string (e.g., `EMG-AMB-1024-EAST`).
   - Click **Transmit**. The regex engine will validate the packet, lock all other lanes to RED, and turn the East lane GREEN.

3. **Generate Analytics:**
   - Allow the simulator to run for at least 30-60 seconds to build up data.
   - Click **Generate Congestion Heatmap**. The system will query the SQLite database and render a Seaborn bar chart showing total throughput per lane.

## 👨‍💻 Author

**Devesh Tiwari**
Artificial Intelligence Engineering