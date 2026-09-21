import tkinter as tk
from tkinter import messagebox
import threading
import time
import random
import sqlite3
import re
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# ==========================================
# SYLLABUS REQUIREMENT 8: SQL Database Operations
# ==========================================
def setup_database():
    conn = sqlite3.connect('traffic_data.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS traffic_logs
                 (timestamp TEXT, lane TEXT, cars_cleared INTEGER, emergency_override BOOLEAN)''')
    conn.commit()
    conn.close()

def log_to_db(lane, cars, emergency=False):
    conn = sqlite3.connect('traffic_data.db')
    c = conn.cursor()
    c.execute("INSERT INTO traffic_logs VALUES (?, ?, ?, ?)",
              (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), lane, cars, emergency))
    conn.commit()
    conn.close()

# ==========================================
# SYLLABUS REQUIREMENT 12 & 5: Web Scraping & Exception Handling
# ==========================================
def get_weather_delay():
    try:
        response = requests.get("https://wttr.in/?format=3", timeout=3)
        weather_data = response.text.lower()
        if "rain" in weather_data or "snow" in weather_data:
            return 2.0  
        return 0.0
    except Exception as e:
        print(f"Scraping failed: {e}. Defaulting to standard timings.")
        return 0.0

# ==========================================
# SYLLABUS REQUIREMENT 4 & 2: OOP & Data Structures
# ==========================================
class Lane:
    def __init__(self, name):
        self.name = name
        self.queue = [] 
        self.state = "RED"

    def add_car(self):
        self.queue.append(1)

    def clear_cars(self):
        cleared = len(self.queue)
        self.queue.clear()
        return cleared

# ==========================================
# SYLLABUS REQUIREMENT 11: GUI (Tkinter Dark Mode)
# ==========================================
class SmartTrafficSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("SmartCity V2I Traffic Simulator")
        self.root.geometry("650x550")
        self.root.configure(bg="#1e1e2e") # Dark background

        self.lanes = {
            "NORTH": Lane("NORTH"),
            "SOUTH": Lane("SOUTH"),
            "EAST": Lane("EAST"),
            "WEST": Lane("WEST")
        }
        
        self.running = True
        self.emergency_active = False
        setup_database()
        
        self.weather_delay = get_weather_delay()
        self.build_gui()

        # SYLLABUS REQUIREMENT 7: Multithreading
        threading.Thread(target=self.simulate_incoming_traffic, daemon=True).start()
        threading.Thread(target=self.traffic_light_controller, daemon=True).start()

    def build_gui(self):
        # Header
        tk.Label(self.root, text="Real-Time V2I Traffic Dashboard", 
                 font=("Segoe UI", 18, "bold"), bg="#1e1e2e", fg="#cdd6f4").pack(pady=20)

        # Dashboard Frame (Dark)
        self.dash_frame = tk.Frame(self.root, bg="#313244", bd=2, relief="ridge", padx=20, pady=20)
        self.dash_frame.pack(pady=10)

        self.status_labels = {}
        for lane_name in self.lanes.keys():
            lbl = tk.Label(self.dash_frame, text=f"{lane_name}: RED (0 cars waiting)", 
                           font=("Consolas", 14, "bold"), bg="#313244", fg="#f38ba8")
            lbl.pack(anchor="w", pady=2)
            self.status_labels[lane_name] = lbl

        # Emergency Section
        tk.Label(self.root, text="Emergency V2I Transponder Override", 
                 font=("Segoe UI", 12, "bold"), bg="#1e1e2e", fg="#a6e3a1").pack(pady=(20, 5))
        
        self.auth_entry = tk.Entry(self.root, width=35, font=("Consolas", 12), 
                                   bg="#45475a", fg="#cdd6f4", insertbackground="white")
        self.auth_entry.pack(pady=5)
        self.auth_entry.insert(0, "EMG-AMB-1024-NORTH")
        
        btn_style = {"font": ("Segoe UI", 10, "bold"), "bg": "#89b4fa", "fg": "#11111b", 
                     "activebackground": "#b4befe", "bd": 0, "padx": 10, "pady": 5}
        tk.Button(self.root, text="Transmit DSRC Packet", command=self.trigger_emergency, **btn_style).pack(pady=5)

        # Analytics Section
        tk.Button(self.root, text="Generate Congestion Heatmap (Seaborn)", 
                  command=self.generate_analytics, **btn_style).pack(pady=25)

    def simulate_incoming_traffic(self):
        while self.running:
            lane_choice = random.choice(list(self.lanes.keys()))
            self.lanes[lane_choice].add_car()
            time.sleep(1) 

    # ==========================================
    # SYLLABUS REQUIREMENT 1: Control Statements
    # ==========================================
    def traffic_light_controller(self):
        lane_names = list(self.lanes.keys())
        current_idx = 0
        
        while self.running:
            if self.emergency_active:
                time.sleep(1)
                continue 

            active_lane = lane_names[current_idx]
            self.lanes[active_lane].state = "GREEN"
            self.update_gui()
            time.sleep(3) 
            
            cleared = self.lanes[active_lane].clear_cars()
            log_to_db(active_lane, cleared)
            
            self.lanes[active_lane].state = "YELLOW"
            self.update_gui()
            time.sleep(1 + self.weather_delay)
            
            self.lanes[active_lane].state = "RED"
            current_idx = (current_idx + 1) % 4

    def update_gui(self):
        for name, lane in self.lanes.items():
            if lane.state == "GREEN":
                color = "#a6e3a1" # Soft Green
            elif lane.state == "YELLOW":
                color = "#f9e2af" # Soft Yellow
            else:
                color = "#f38ba8" # Soft Red
            
            self.status_labels[name].config(
                text=f"{name.ljust(5)}: {lane.state.ljust(6)} ({len(lane.queue):02d} cars waiting)",
                fg=color
            )

    # ==========================================
    # SYLLABUS REQUIREMENT 6: Regular Expressions
    # ==========================================
    def trigger_emergency(self):
        # Spawns a new thread so the button doesn't freeze the GUI
        threading.Thread(target=self._process_emergency, daemon=True).start()

    def _process_emergency(self):
        packet = self.auth_entry.get().upper()
        pattern = r"^EMG-(AMB|POL)-\d{4}-(NORTH|SOUTH|EAST|WEST)$"
        
        if re.match(pattern, packet):
            lane_target = packet.split("-")[-1]
            
            # Show popup over the main window
            messagebox.showinfo("V2I Authorized", f"{packet} Validated.\nPreempting traffic for {lane_target} lane!", parent=self.root)
            
            self.emergency_active = True
            
            for name, lane in self.lanes.items():
                lane.state = "RED"
            self.lanes[lane_target].state = "GREEN"
            self.update_gui()
            
            time.sleep(4)
            cleared = self.lanes[lane_target].clear_cars()
            log_to_db(lane_target, cleared, emergency=True)
            
            self.emergency_active = False
        else:
            messagebox.showerror("Auth Failed", "Invalid Transponder ID! System rejected packet.", parent=self.root)

    # ==========================================
    # SYLLABUS REQUIREMENT 9 & 10: Pandas & Seaborn
    # ==========================================
    def generate_analytics(self):
        conn = sqlite3.connect('traffic_data.db')
        df = pd.read_sql_query("SELECT * FROM traffic_logs", conn)
        conn.close()
        
        if df.empty:
            messagebox.showwarning("No Data", "Let the simulation run for a few seconds first!", parent=self.root)
            return

        summary = df.groupby('lane')['cars_cleared'].sum().reset_index()
        
        plt.figure(figsize=(8, 5))
        sns.barplot(x='lane', y='cars_cleared', data=summary, palette='mako')
        plt.title('Total Vehicle Throughput per Lane (V2I System Analytics)')
        plt.ylabel('Total Cars Cleared')
        plt.xlabel('Intersection Lane')
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    root = tk.Tk()
    app = SmartTrafficSimulator(root)
    root.mainloop()