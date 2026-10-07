"""
Emergency SOS Module
Realizes one-click alarm, real-time location sharing, and safe point navigation
"""
from datetime import datetime


class EmergencySOS:
    def __init__(self, positioning_module):
        self.positioning_module = positioning_module
        # Emergency contact list (simulated)
        self.emergency_contacts = [
            {"name": "Campus Security", "phone": "1101", "role": "security"},
            {"name": "Counselor Li", "phone": "13800138000", "role": "counselor"}
        ]
        # Safe points on campus (simulated)
        self.safe_points = [
            {"name": "Security Pavilion", "position": (34.0525, -118.2440)},
            {"name": "First Aid Room", "position": (34.0520, -118.2435)},
            {"name": "Main Gate Security", "position": (34.0522, -118.2430)},
            {"name": "Library Security Desk", "position": (34.0528, -118.2445)}
        ]
    
    def send_alarm(self, gps_data, wifi_signals):
        """Send alarm with real-time location"""
        current_pos = self.positioning_module.get_position(gps_data, wifi_signals)
        alarm_info = {
            "type": "emergency_call",
            "position": {"latitude": current_pos[0], "longitude": current_pos[1], "floor": current_pos[2]},
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "contacts": self.emergency_contacts
        }
        # Simulate sending alarm to contacts (in actual use, connect to SMS/APP notification)
        print("Alarm sent successfully!")
        print(f"Emergency location: Lat {current_pos[0]}, Lon {current_pos[1]}, Floor {current_pos[2]}")
        return alarm_info
    
    def get_nearest_safe_point(self, current_pos):
        """Find nearest safe point"""
        min_distance = float('inf')
        nearest_point = None
        for point in self.safe_points:
            distance = self.positioning_module.heuristic(current_pos[:2], point["position"])
            if distance < min_distance:
                min_distance = distance
                nearest_point = point
        return nearest_point, min_distance

