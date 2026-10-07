"""
CampusNav: Campus Navigation and Emergency Service System
Main Flask application
"""
from flask import Flask, render_template, request, jsonify
import numpy as np
from hybrid_positioning import HybridPositioning
from path_planner import ImprovedAStarPlanner
from emergency_sos import EmergencySOS
from datetime import datetime
import json

app = Flask(__name__)

# Initialize modules
positioning = HybridPositioning()
emergency_sos = EmergencySOS(positioning)

# Create a sample campus map (100x100 grid)
# 0 = passable, 1 = obstacle, 2 = crowded area
def create_campus_map():
    map_size = 100
    campus_map = np.zeros((map_size, map_size), dtype=int)
    
    # Add some obstacles (buildings)
    campus_map[10:20, 10:20] = 1  # Building 1
    campus_map[30:40, 30:40] = 1  # Building 2
    campus_map[50:60, 50:60] = 1  # Building 3
    campus_map[70:80, 20:30] = 1  # Building 4
    
    # Add crowded areas (canteen, library entrance, etc.)
    campus_map[25:35, 25:35] = 2  # Canteen area
    campus_map[45:55, 45:55] = 2  # Library entrance
    
    return campus_map.tolist()

campus_map = create_campus_map()
planner = ImprovedAStarPlanner(campus_map)

# Sample campus activities
campus_activities = [
    {
        "id": 1,
        "title": "New Student Orientation",
        "category": "academic",
        "location": {"name": "Main Auditorium", "lat": 34.0525, "lon": -118.2438},
        "time": "2025-01-20 09:00",
        "description": "Welcome event for new students. Learn about campus facilities, academic programs, and student services. Registration required.",
        "details": "Duration: 3 hours | Contact: orientation@campus.edu | Room: Auditorium A",
        "type": "joinable"  # Can join/register
    },
    {
        "id": 2,
        "title": "Annual Sports Day",
        "category": "sports",
        "location": {"name": "Sports Complex", "lat": 34.0522, "lon": -118.2435},
        "time": "2025-01-25 08:00",
        "description": "Campus-wide sports competition featuring track & field, basketball, volleyball, and more. All students and staff welcome to participate or spectate.",
        "details": "Events: Track, Basketball, Volleyball, Soccer | Registration deadline: Jan 22 | Free entry",
        "type": "joinable"  # Can join/register
    },
    {
        "id": 3,
        "title": "Library Opening Hours",
        "category": "facilities",
        "location": {"name": "Main Library", "lat": 34.0528, "lon": -118.2445},
        "time": "2025-01-15 07:00",
        "description": "Library operating schedule. Study spaces, computer labs, and quiet zones available.",
        "details": "Mon-Fri: 7:00 AM - 10:00 PM | Sat-Sun: 9:00 AM - 8:00 PM | 24/7 study room available",
        "type": "notification"  # Just notification, no action needed
    },
    {
        "id": 4,
        "title": "Study Room Reservation",
        "category": "facilities",
        "location": {"name": "Library Study Rooms", "lat": 34.0528, "lon": -118.2445},
        "time": "2025-01-15 00:00",
        "description": "Reserve study rooms for group projects or individual study. Rooms available with whiteboards, projectors, and charging stations.",
        "details": "Capacity: 2-8 people | Reservation: Online booking system | Duration: 2-4 hours | Free for students",
        "type": "bookable"  # Can be booked
    },
    {
        "id": 5,
        "title": "Academic Lecture: AI in Education",
        "category": "academic",
        "location": {"name": "Teaching Building 3, Room 301", "lat": 34.0525, "lon": -118.2438},
        "time": "2025-01-18 14:00",
        "description": "Join us for an insightful lecture on AI applications in education. Guest speaker: Dr. Sarah Chen from MIT.",
        "details": "Duration: 1.5 hours | Q&A session included | Open to all students",
        "type": "joinable"  # Can join/register
    },
    {
        "id": 6,
        "title": "Basketball Tournament Finals",
        "category": "sports",
        "location": {"name": "Indoor Sports Center", "lat": 34.0522, "lon": -118.2435},
        "time": "2025-01-22 18:00",
        "description": "Championship match of the inter-department basketball tournament. Cheer for your department!",
        "details": "Teams: Engineering vs Business | Free admission | Snacks available",
        "type": "notification"  # Just notification, no registration needed
    },
    {
        "id": 7,
        "title": "Cultural Festival",
        "category": "cultural",
        "location": {"name": "Main Square", "lat": 34.0520, "lon": -118.2430},
        "time": "2025-01-28 16:00",
        "description": "Annual campus cultural festival celebrating diversity. Food stalls, performances, and cultural exhibitions.",
        "details": "Duration: 4 hours | Food vendors | Live performances | Free entry",
        "type": "joinable"  # Can join/register
    },
    {
        "id": 8,
        "title": "Research Workshop",
        "category": "academic",
        "location": {"name": "Library Conference Room B", "lat": 34.0528, "lon": -118.2445},
        "time": "2025-01-17 10:00",
        "description": "Workshop on research methodologies and academic paper writing. Perfect for graduate students.",
        "details": "Duration: 2 hours | Registration required | Materials provided",
        "type": "joinable"  # Can join/register
    },
    {
        "id": 9,
        "title": "Yoga & Meditation Class",
        "category": "sports",
        "location": {"name": "Fitness Center, Studio 2", "lat": 34.0523, "lon": -118.2432},
        "time": "2025-01-16 19:00",
        "description": "Free yoga and meditation class for stress relief. All levels welcome. Bring your own mat.",
        "details": "Duration: 1 hour | Every Monday & Wednesday | Free for students",
        "type": "joinable"  # Can join/register
    },
    {
        "id": 10,
        "title": "Computer Lab Access",
        "category": "facilities",
        "location": {"name": "Computer Science Building, Lab 205", "lat": 34.0526, "lon": -118.2440},
        "time": "2025-01-15 08:00",
        "description": "Open computer lab with high-performance workstations. Software: MATLAB, Python, Adobe Suite, and more.",
        "details": "Hours: 8:00 AM - 10:00 PM | Student ID required | Printing available",
        "type": "notification"  # Just notification
    },
    {
        "id": 11,
        "title": "Career Fair",
        "category": "academic",
        "location": {"name": "Student Center, Hall A", "lat": 34.0521, "lon": -118.2433},
        "time": "2025-01-24 10:00",
        "description": "Connect with top employers and explore internship and job opportunities. Bring your resume!",
        "details": "Duration: 6 hours | 50+ companies | Professional dress code | Registration recommended",
        "type": "joinable"  # Can join/register
    },
    {
        "id": 12,
        "title": "Swimming Pool Schedule",
        "category": "sports",
        "location": {"name": "Aquatic Center", "lat": 34.0524, "lon": -118.2436},
        "time": "2025-01-15 06:00",
        "description": "Public swimming hours. Lanes available for lap swimming. Locker rooms and showers provided.",
        "details": "Mon-Fri: 6:00 AM - 9:00 PM | Weekends: 8:00 AM - 6:00 PM | Free for students",
        "type": "notification"  # Just notification
    }
]

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/navigate', methods=['POST'])
def navigate():
    """Navigation API endpoint"""
    data = request.json
    start_lat = data.get('start_lat')
    start_lon = data.get('start_lon')
    end_lat = data.get('end_lat')
    end_lon = data.get('end_lon')
    
    # Default campus origin (Los Angeles area - can be changed to your actual campus)
    campus_origin_lat = 34.0520
    campus_origin_lon = -118.2430
    
    # Check if coordinates are within reasonable campus bounds
    start_valid = planner.is_valid_coordinate(start_lat, start_lon, campus_origin_lat, campus_origin_lon)
    end_valid = planner.is_valid_coordinate(end_lat, end_lon, campus_origin_lat, campus_origin_lon)
    
    if not start_valid or not end_valid:
        # If coordinates are far from campus, use them as dynamic origin for demo
        # Calculate center of the two points
        center_lat = (start_lat + end_lat) / 2
        center_lon = (start_lon + end_lon) / 2
        
        # Use dynamic origin based on input coordinates
        campus_origin_lat = center_lat - 0.005  # Center the map around the route
        campus_origin_lon = center_lon - 0.005
    
    # Convert coordinates to grid
    start_grid = planner.coordinates_to_grid(start_lat, start_lon, campus_origin_lat, campus_origin_lon)
    end_grid = planner.coordinates_to_grid(end_lat, end_lon, campus_origin_lat, campus_origin_lon)
    
    # Validate grid coordinates are within bounds
    if (start_grid[0] < 0 or start_grid[0] >= planner.rows or 
        start_grid[1] < 0 or start_grid[1] >= planner.cols or
        end_grid[0] < 0 or end_grid[0] >= planner.rows or 
        end_grid[1] < 0 or end_grid[1] >= planner.cols):
        return jsonify({
            "error": "Coordinates are too far apart or outside campus bounds. Please use coordinates within the same campus area.",
            "hint": "For demo, try coordinates near: Lat 34.0520, Lon -118.2430"
        }), 400
    
    # Plan path
    path = planner.plan(start_grid, end_grid)
    
    if path is None:
        return jsonify({
            "error": "No path found. The route may be blocked by obstacles.",
            "hint": "Try different start or end coordinates"
        }), 404
    
    # Convert path back to coordinates
    path_coords = [planner.grid_to_coordinates(x, y, campus_origin_lat, campus_origin_lon) for x, y in path]
    
    # Ensure path starts and ends at exact coordinates (frontend will handle this, but good to have accurate path)
    # Note: The frontend will prepend start and append end to ensure connection to markers
    
    return jsonify({
        "path": path_coords,
        "start": {"lat": start_lat, "lon": start_lon},
        "end": {"lat": end_lat, "lon": end_lon},
        "path_length": len(path)
    })

@app.route('/api/emergency', methods=['POST'])
def emergency():
    """Emergency SOS API endpoint"""
    data = request.json
    gps_data = {
        'latitude': data.get('lat', 34.0523),
        'longitude': data.get('lon', -118.2437),
        'signal_strength': data.get('gps_signal', -75)  # Default: outdoor
    }
    wifi_signals = np.array(data.get('wifi_signals', [-60, -58]))
    
    # Send alarm
    alarm_info = emergency_sos.send_alarm(gps_data, wifi_signals)
    
    # Get nearest safe point
    current_pos = positioning.get_position(gps_data, wifi_signals)
    nearest_point, distance = emergency_sos.get_nearest_safe_point(current_pos)
    
    # Plan path to safe point
    current_grid = planner.coordinates_to_grid(current_pos[0], current_pos[1])
    safe_grid = planner.coordinates_to_grid(nearest_point["position"][0], nearest_point["position"][1])
    safe_path = planner.plan(current_grid, safe_grid)
    
    safe_path_coords = None
    if safe_path:
        safe_path_coords = [planner.grid_to_coordinates(x, y) for x, y in safe_path]
    
    return jsonify({
        "alarm_sent": True,
        "current_position": {
            "lat": current_pos[0],
            "lon": current_pos[1],
            "floor": current_pos[2]
        },
        "nearest_safe_point": {
            "name": nearest_point["name"],
            "position": nearest_point["position"],
            "distance": distance
        },
        "safe_path": safe_path_coords,
        "alarm_info": alarm_info
    })

@app.route('/api/activities', methods=['GET'])
def get_activities():
    """Get campus activities with optional filtering"""
    category = request.args.get('category')
    time_filter = request.args.get('time')  # 'today', 'week', etc.
    distance_filter = request.args.get('distance')  # max distance in meters
    user_lat = float(request.args.get('lat', 34.0523))
    user_lon = float(request.args.get('lon', -118.2437))
    
    filtered_activities = campus_activities.copy()
    
    # Filter by category
    if category and category != 'all':
        filtered_activities = [a for a in filtered_activities if a['category'] == category]
    
    # Filter by distance (only if distance filter is set and > 0)
    if distance_filter and float(distance_filter) > 0:
        max_distance = float(distance_filter)
        filtered_activities = [
            a for a in filtered_activities
            if positioning.heuristic((user_lat, user_lon), (a['location']['lat'], a['location']['lon'])) * 111000 < max_distance
        ]
    
    # Add distance to each activity
    for activity in filtered_activities:
        distance = positioning.heuristic(
            (user_lat, user_lon),
            (activity['location']['lat'], activity['location']['lon'])
        ) * 111000  # Convert to meters (rough approximation)
        activity['distance'] = round(distance, 1)
    
    return jsonify({"activities": filtered_activities})

@app.route('/api/activity/<int:activity_id>/route', methods=['GET'])
def get_activity_route(activity_id):
    """Get navigation route to an activity"""
    activity = next((a for a in campus_activities if a['id'] == activity_id), None)
    if not activity:
        return jsonify({"error": "Activity not found"}), 404
    
    user_lat = float(request.args.get('lat', 34.0523))
    user_lon = float(request.args.get('lon', -118.2437))
    
    start_grid = planner.coordinates_to_grid(user_lat, user_lon)
    end_grid = planner.coordinates_to_grid(activity['location']['lat'], activity['location']['lon'])
    
    path = planner.plan(start_grid, end_grid)
    
    if path is None:
        return jsonify({"error": "No path found"}), 404
    
    path_coords = [planner.grid_to_coordinates(x, y) for x, y in path]
    
    return jsonify({
        "path": path_coords,
        "activity": activity
    })

# Study room booking schedule (simulated data)
study_room_schedule = {
    "rooms": [
        {"id": 1, "name": "Study Room A", "capacity": 4},
        {"id": 2, "name": "Study Room B", "capacity": 6},
        {"id": 3, "name": "Study Room C", "capacity": 8},
        {"id": 4, "name": "Study Room D", "capacity": 4},
        {"id": 5, "name": "Study Room E", "capacity": 2}
    ],
    "time_slots": [
        {"time": "08:00-10:00", "available": [1, 2, 3, 4, 5]},
        {"time": "10:00-12:00", "available": [1, 3, 4, 5]},  # Room 2 booked
        {"time": "12:00-14:00", "available": [2, 3, 5]},  # Rooms 1, 4 booked
        {"time": "14:00-16:00", "available": [1, 2, 3, 4, 5]},
        {"time": "16:00-18:00", "available": [3, 4, 5]},  # Rooms 1, 2 booked
        {"time": "18:00-20:00", "available": [1, 2, 4, 5]},  # Room 3 booked
        {"time": "20:00-22:00", "available": [1, 2, 3, 4, 5]}
    ]
}

# Store registrations (in real app, use database)
activity_registrations = []

@app.route('/api/activity/<int:activity_id>/schedule', methods=['GET'])
def get_booking_schedule(activity_id):
    """Get booking schedule for study rooms"""
    if activity_id == 4:  # Study Room Reservation
        return jsonify(study_room_schedule)
    return jsonify({"error": "Booking not available for this activity"}), 404

@app.route('/api/activity/<int:activity_id>/book', methods=['POST'])
def book_study_room(activity_id):
    """Book a study room"""
    data = request.json
    room_id = data.get('room_id')
    time_slot = data.get('time_slot')
    student_name = data.get('student_name')
    student_id = data.get('student_id')
    
    # Validate booking
    if activity_id != 4:
        return jsonify({"error": "Booking not available for this activity"}), 400
    
    # Check if time slot and room are available
    slot = next((s for s in study_room_schedule["time_slots"] if s["time"] == time_slot), None)
    if not slot or room_id not in slot["available"]:
        return jsonify({"error": "This time slot is not available"}), 400
    
    # Book the room (remove from available)
    slot["available"].remove(room_id)
    
    booking = {
        "activity_id": activity_id,
        "room_id": room_id,
        "time_slot": time_slot,
        "student_name": student_name,
        "student_id": student_id,
        "booking_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    activity_registrations.append(booking)
    
    return jsonify({
        "success": True,
        "message": "Room booked successfully!",
        "booking": booking
    })

@app.route('/api/activity/<int:activity_id>/register', methods=['POST'])
def register_activity(activity_id):
    """Register for an activity"""
    data = request.json
    name = data.get('name')
    major = data.get('major')
    phone = data.get('phone')
    student_number = data.get('student_number')
    email = data.get('email', '')
    
    # Validate required fields
    if not all([name, major, phone, student_number]):
        return jsonify({"error": "Please fill in all required fields"}), 400
    
    # Check if activity exists and is joinable
    activity = next((a for a in campus_activities if a['id'] == activity_id), None)
    if not activity:
        return jsonify({"error": "Activity not found"}), 404
    
    if activity.get('type') != 'joinable':
        return jsonify({"error": "Registration not available for this activity"}), 400
    
    registration = {
        "activity_id": activity_id,
        "activity_title": activity['title'],
        "name": name,
        "major": major,
        "phone": phone,
        "student_number": student_number,
        "email": email,
        "registration_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    activity_registrations.append(registration)
    
    return jsonify({
        "success": True,
        "message": "Registration successful!",
        "registration": registration
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

