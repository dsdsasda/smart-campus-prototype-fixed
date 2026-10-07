"""
Hybrid Positioning Module
Combines GPS for outdoor positioning and WiFi fingerprinting for indoor positioning
"""
import numpy as np


class HybridPositioning:
    def __init__(self):
        # WiFi fingerprint database (simulated data: [WiFi signal strength 1, WiFi signal strength 2, latitude, longitude, floor])
        self.wifi_fingerprints = np.array([
            [-55, -62, 34.05223, -118.24371, 1],
            [-58, -60, 34.05225, -118.24373, 1],
            [-60, -59, 34.05227, -118.24375, 1],
            [-62, -58, 34.05230, -118.24378, 2],
            [-65, -61, 34.05232, -118.24380, 2],
            [-63, -60, 34.05235, -118.24382, 3],
            [-67, -64, 34.05238, -118.24385, 3],
            # More fingerprint data for different locations
            [-50, -55, 34.05240, -118.24390, 0],  # Outdoor area
            [-52, -57, 34.05242, -118.24392, 0],
            [-54, -59, 34.05245, -118.24395, 0],
        ])
    
    def gps_positioning(self, gps_data):
        """Outdoor GPS positioning (return latitude and longitude)"""
        if gps_data['signal_strength'] > -80:  # Strong GPS signal (outdoor)
            return (gps_data['latitude'], gps_data['longitude'], 0)  # 0 represents outdoor
        else:
            return None  # GPS signal weak, switch to WiFi positioning
    
    def wifi_positioning(self, wifi_signals):
        """Indoor WiFi fingerprint positioning"""
        min_distance = float('inf')
        best_position = None
        # Calculate Euclidean distance between detected signals and fingerprint database
        for fp in self.wifi_fingerprints:
            signal_distance = np.linalg.norm(wifi_signals - fp[:2])
            if signal_distance < min_distance:
                min_distance = signal_distance
                best_position = (fp[2], fp[3], fp[4])  # (latitude, longitude, floor)
        return best_position
    
    def get_position(self, gps_data, wifi_signals):
        """Unified positioning interface: automatic switching between indoor and outdoor"""
        gps_pos = self.gps_positioning(gps_data)
        if gps_pos:
            return gps_pos
        else:
            return self.wifi_positioning(wifi_signals)
    
    def heuristic(self, pos1, pos2):
        """Calculate Euclidean distance between two positions"""
        return np.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)

