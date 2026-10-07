// Global map variables
let navMap = null;
let emergencyMap = null;
let activitiesMap = null;
let currentPathLayer = null;

// Initialize maps when tabs are switched
document.addEventListener('DOMContentLoaded', function() {
    // Tab switching
    const tabButtons = document.querySelectorAll('.tab-btn');
    tabButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabName = btn.getAttribute('data-tab');
            switchTab(tabName);
        });
    });

    // Initialize navigation map
    initNavigationMap();
});

function switchTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    // Show selected tab
    document.getElementById(tabName).classList.add('active');
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

    // Initialize map for the active tab
    if (tabName === 'navigation' && !navMap) {
        initNavigationMap();
    } else if (tabName === 'emergency' && !emergencyMap) {
        initEmergencyMap();
    } else if (tabName === 'activities' && !activitiesMap) {
        initActivitiesMap();
        loadActivities();
    }
}

function initNavigationMap() {
    if (navMap) return;
    
    navMap = L.map('map-container').setView([34.0523, -118.2437], 16);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(navMap);
}

function initEmergencyMap() {
    if (emergencyMap) return;
    
    emergencyMap = L.map('emergency-map-container').setView([34.0523, -118.2437], 16);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(emergencyMap);
}

function initActivitiesMap() {
    if (activitiesMap) return;
    
    activitiesMap = L.map('activities-map-container').setView([34.0523, -118.2437], 16);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(activitiesMap);
}

function planRoute() {
    const startLat = parseFloat(document.getElementById('start-lat').value);
    const startLon = parseFloat(document.getElementById('start-lon').value);
    const endLat = parseFloat(document.getElementById('end-lat').value);
    const endLon = parseFloat(document.getElementById('end-lon').value);

    if (!startLat || !startLon || !endLat || !endLon) {
        alert('Please enter all coordinates');
        return;
    }

    fetch('/api/navigate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            start_lat: startLat,
            start_lon: startLon,
            end_lat: endLat,
            end_lon: endLon
        })
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(data => {
                throw new Error(data.error + (data.hint ? '\n\n' + data.hint : ''));
            });
        }
        return response.json();
    })
    .then(data => {
        if (data.error) {
            alert('Error: ' + data.error + (data.hint ? '\n\n' + data.hint : ''));
            // Draw a simple straight line as fallback for visualization
            drawFallbackRoute(startLat, startLon, endLat, endLon);
            return;
        }

        // Clear previous path
        if (currentPathLayer) {
            navMap.removeLayer(currentPathLayer);
        }

        // Clear previous markers
        navMap.eachLayer(layer => {
            if (layer instanceof L.Marker) {
                navMap.removeLayer(layer);
            }
        });

        // Draw path - ensure it connects directly to start and end markers
        // If path is very short (2 points), it's a direct path - use red color
        // Otherwise use blue for optimized path
        let pathCoords;
        let isDirectPath = data.path.length <= 2;
        
        if (isDirectPath && data.path.length === 2) {
            // Direct path - use exact start and end coordinates
            pathCoords = [
                [data.start.lat, data.start.lon],
                [data.end.lat, data.end.lon]
            ];
        } else {
            // Optimized path - ensure it connects to markers
            pathCoords = [
                [data.start.lat, data.start.lon],  // Start at exact user location
                ...data.path.map(p => [p[0], p[1]]),  // Path points
                [data.end.lat, data.end.lon]  // End at exact destination
            ];
        }
        
        // Use red for direct/shortest path, blue for optimized path
        const pathColor = isDirectPath ? '#F44336' : '#2196F3';
        const pathWeight = isDirectPath ? 5 : 6;
        
        currentPathLayer = L.polyline(pathCoords, {
            color: pathColor,
            weight: pathWeight,
            opacity: 0.8,
            lineJoin: 'round',
            lineCap: 'round'
        }).addTo(navMap);

        // Create custom icons for start (green) and end (red)
        const startIcon = L.divIcon({
            className: 'custom-marker start-marker',
            html: '<div style="background-color: #4CAF50; width: 30px; height: 30px; border-radius: 50%; border: 3px solid white; box-shadow: 0 2px 8px rgba(0,0,0,0.3); display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 16px;">S</div>',
            iconSize: [30, 30],
            iconAnchor: [15, 15]
        });

        const endIcon = L.divIcon({
            className: 'custom-marker end-marker',
            html: '<div style="background-color: #F44336; width: 30px; height: 30px; border-radius: 50%; border: 3px solid white; box-shadow: 0 2px 8px rgba(0,0,0,0.3); display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 16px;">E</div>',
            iconSize: [30, 30],
            iconAnchor: [15, 15]
        });

        // Add markers with custom icons - add them AFTER the path so they appear on top
        const startMarker = L.marker([data.start.lat, data.start.lon], {
            icon: startIcon,
            zIndexOffset: 1000  // Ensure marker appears above path
        })
            .addTo(navMap)
            .bindPopup('<b>📍 Start Point</b><br>Your current location');
        
        const endMarker = L.marker([data.end.lat, data.end.lon], {
            icon: endIcon,
            zIndexOffset: 1000  // Ensure marker appears above path
        })
            .addTo(navMap)
            .bindPopup('<b>🎯 Destination</b><br>Your destination');

        // Open popups to make it clear
        startMarker.openPopup();
        setTimeout(() => endMarker.openPopup(), 500);

        // Fit map to include both markers and entire path with padding
        // pathCoords already includes start and end, so we can use it directly
        const bounds = L.latLngBounds(pathCoords);
        navMap.fitBounds(bounds, {
            padding: [100, 100], // Add padding to ensure whole route and markers are visible
            maxZoom: 18
        });
    })
    .catch(error => {
        console.error('Error:', error);
        alert(error.message || 'Failed to plan route. Please ensure coordinates are within the same campus area.');
        // Draw fallback route
        drawFallbackRoute(startLat, startLon, endLat, endLon);
    });
}

function useCurrentLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            position => {
                const lat = position.coords.latitude;
                const lon = position.coords.longitude;
                document.getElementById('start-lat').value = lat;
                document.getElementById('start-lon').value = lon;
                
                // Check if location is far from campus and suggest using campus coordinates
                const campusLat = 34.0520;
                const campusLon = -118.2430;
                const distance = Math.sqrt(Math.pow(lat - campusLat, 2) + Math.pow(lon - campusLon, 2));
                if (distance > 0.01) {
                    alert('Your location is far from the demo campus. For testing, you can use campus coordinates:\nLat: 34.0520, Lon: -118.2430');
                }
            },
            error => {
                alert('Unable to get current location. Using default campus coordinates.');
                document.getElementById('start-lat').value = 34.0520;
                document.getElementById('start-lon').value = -118.2430;
            }
        );
    } else {
        alert('Geolocation is not supported by your browser. Using default campus coordinates.');
        document.getElementById('start-lat').value = 34.0520;
        document.getElementById('start-lon').value = -118.2430;
    }
}

function drawFallbackRoute(startLat, startLon, endLat, endLon) {
    // Clear previous path
    if (currentPathLayer) {
        navMap.removeLayer(currentPathLayer);
    }
    
    // Clear previous markers
    navMap.eachLayer(layer => {
        if (layer instanceof L.Marker || (layer instanceof L.Polyline && layer !== currentPathLayer)) {
            navMap.removeLayer(layer);
        }
    });
    
    // Draw a simple straight line as fallback - make it more visible
    const fallbackPath = [[startLat, startLon], [endLat, endLon]];
    currentPathLayer = L.polyline(fallbackPath, {
        color: '#FF9800',
        weight: 5,
        opacity: 0.7,
        dashArray: '15, 10'
    }).addTo(navMap);
    
    // Create custom icons for start (green) and end (red)
    const startIcon = L.divIcon({
        className: 'custom-marker start-marker',
        html: '<div style="background-color: #4CAF50; width: 30px; height: 30px; border-radius: 50%; border: 3px solid white; box-shadow: 0 2px 8px rgba(0,0,0,0.3); display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 16px;">S</div>',
        iconSize: [30, 30],
        iconAnchor: [15, 15]
    });

    const endIcon = L.divIcon({
        className: 'custom-marker end-marker',
        html: '<div style="background-color: #F44336; width: 30px; height: 30px; border-radius: 50%; border: 3px solid white; box-shadow: 0 2px 8px rgba(0,0,0,0.3); display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 16px;">E</div>',
        iconSize: [30, 30],
        iconAnchor: [15, 15]
    });
    
    // Add markers with custom icons - add them AFTER the path so they appear on top
    const startMarker = L.marker([startLat, startLon], {
        icon: startIcon,
        zIndexOffset: 1000  // Ensure marker appears above path
    })
        .addTo(navMap)
        .bindPopup('<b>📍 Start Point</b><br>Your current location');
    
    const endMarker = L.marker([endLat, endLon], {
        icon: endIcon,
        zIndexOffset: 1000  // Ensure marker appears above path
    })
        .addTo(navMap)
        .bindPopup('<b>🎯 Destination</b><br>Your destination');
    
    // Open popups
    startMarker.openPopup();
    setTimeout(() => endMarker.openPopup(), 500);
    
    // Fit map to show both points with padding
    const bounds = L.latLngBounds([
        [startLat, startLon],
        [endLat, endLon]
    ]);
    navMap.fitBounds(bounds, {
        padding: [80, 80], // Add padding to ensure both markers are visible
        maxZoom: 18
    });
}

function sendEmergency() {
    // Get current location (or use default)
    let lat = 34.0523;
    let lon = -118.2437;
    let gpsSignal = -75; // Default: outdoor

    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            position => {
                lat = position.coords.latitude;
                lon = position.coords.longitude;
                sendEmergencyRequest(lat, lon, gpsSignal);
            },
            () => {
                // If geolocation fails, assume indoor (weak GPS)
                gpsSignal = -90;
                sendEmergencyRequest(lat, lon, gpsSignal);
            }
        );
    } else {
        sendEmergencyRequest(lat, lon, gpsSignal);
    }
}

function sendEmergencyRequest(lat, lon, gpsSignal) {
    fetch('/api/emergency', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            lat: lat,
            lon: lon,
            gps_signal: gpsSignal,
            wifi_signals: [-60, -58] // Simulated WiFi signals
        })
    })
    .then(response => response.json())
    .then(data => {
        const resultDiv = document.getElementById('emergency-result');
        resultDiv.classList.add('show');
        resultDiv.innerHTML = `
            <h3>✅ Emergency Alert Sent!</h3>
            <p><strong>Your Location:</strong> Lat ${data.current_position.lat.toFixed(6)}, Lon ${data.current_position.lon.toFixed(6)}</p>
            <p><strong>Floor:</strong> ${data.current_position.floor === 0 ? 'Outdoor' : 'Floor ' + data.current_position.floor}</p>
            <p><strong>Nearest Safe Point:</strong> ${data.nearest_safe_point.name}</p>
            <p><strong>Distance to Safe Point:</strong> ${(data.nearest_safe_point.distance * 111000).toFixed(1)} meters</p>
            <p><strong>Time:</strong> ${data.alarm_info.time}</p>
        `;

        // Display on map
        if (emergencyMap) {
            emergencyMap.eachLayer(layer => {
                if (layer instanceof L.Marker || layer instanceof L.Polyline) {
                    emergencyMap.removeLayer(layer);
                }
            });

            // Current position
            L.marker([data.current_position.lat, data.current_position.lon])
                .addTo(emergencyMap)
                .bindPopup('Your Location (Emergency)')
                .openPopup();

            // Safe point
            L.marker([data.nearest_safe_point.position[0], data.nearest_safe_point.position[1]], {
                icon: L.icon({
                    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-green.png',
                    iconSize: [25, 41],
                    iconAnchor: [12, 41]
                })
            })
            .addTo(emergencyMap)
            .bindPopup(data.nearest_safe_point.name);

            // Path to safe point
            if (data.safe_path && data.safe_path.length > 0) {
                const safePathCoords = data.safe_path.map(p => [p[0], p[1]]);
                L.polyline(safePathCoords, {
                    color: '#dc3545',
                    weight: 5,
                    opacity: 0.7,
                    dashArray: '10, 5'
                }).addTo(emergencyMap);
            }

            emergencyMap.setView([data.current_position.lat, data.current_position.lon], 16);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Failed to send emergency alert');
    });
}

function loadActivities() {
    const category = document.getElementById('category-filter').value;
    const distance = document.getElementById('distance-filter').value;
    
    let lat = 34.0523;
    let lon = -118.2437;

    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            position => {
                lat = position.coords.latitude;
                lon = position.coords.longitude;
                fetchActivities(category, distance, lat, lon);
            },
            () => {
                fetchActivities(category, distance, lat, lon);
            }
        );
    } else {
        fetchActivities(category, distance, lat, lon);
    }
}

function filterActivities() {
    loadActivities();
}

function fetchActivities(category, distance, lat, lon) {
    const url = `/api/activities?category=${category}&distance=${distance}&lat=${lat}&lon=${lon}`;
    
    fetch(url)
    .then(response => response.json())
    .then(data => {
        displayActivities(data.activities);
        displayActivitiesOnMap(data.activities);
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function displayActivities(activities) {
    const listDiv = document.getElementById('activities-list');
    
    if (activities.length === 0) {
        listDiv.innerHTML = '<p>No activities found matching your criteria.</p>';
        return;
    }

    listDiv.innerHTML = activities.map(activity => {
        const activityType = activity.type || 'default';
        let actionButtons = '';
        
        if (activityType === 'bookable') {
            // Study room - show Book button
            actionButtons = `<button class="btn btn-primary btn-small" onclick="openBookingModal(${activity.id})">📚 Book</button>`;
        } else if (activityType === 'joinable') {
            // Activities that can be joined - show Register and Navigate buttons
            actionButtons = `
                <button class="btn btn-primary btn-small" onclick="openRegistrationModal(${activity.id}, '${activity.title.replace(/'/g, "\\'")}')">Register</button>
                <button class="btn btn-secondary btn-small" onclick="navigateToActivity(${activity.id})">Navigate</button>
            `;
        } else if (activityType === 'notification') {
            // Just notification - no buttons or only Navigate if needed
            actionButtons = `<button class="btn btn-secondary btn-small" onclick="navigateToActivity(${activity.id})">Navigate</button>`;
        } else {
            // Default - show Navigate button
            actionButtons = `<button class="btn btn-primary btn-small" onclick="navigateToActivity(${activity.id})">Navigate</button>`;
        }
        
        return `
        <div class="activity-item">
            <h3>${activity.title}</h3>
            <div class="meta">
                <span class="category ${activity.category}">${activity.category.charAt(0).toUpperCase() + activity.category.slice(1)}</span>
                <span>📍 ${activity.location.name}</span>
                <span>⏰ ${activity.time}</span>
                <span>📏 ${activity.distance ? activity.distance.toFixed(0) + ' m away' : ''}</span>
            </div>
            <p class="description">${activity.description}</p>
            ${activity.details ? `<p class="details">ℹ️ ${activity.details}</p>` : ''}
            <div class="actions">
                ${actionButtons}
            </div>
        </div>
    `;
    }).join('');
}

function displayActivitiesOnMap(activities) {
    if (!activitiesMap) return;

    // Clear existing markers
    activitiesMap.eachLayer(layer => {
        if (layer instanceof L.Marker) {
            activitiesMap.removeLayer(layer);
        }
    });

    activities.forEach(activity => {
        const categoryColors = {
            academic: '#1976d2',
            sports: '#f57c00',
            cultural: '#7b1fa2',
            facilities: '#388e3c'
        };

        L.marker([activity.location.lat, activity.location.lon], {
            icon: L.divIcon({
                className: 'activity-marker',
                html: `<div style="background: ${categoryColors[activity.category]}; width: 20px; height: 20px; border-radius: 50%; border: 2px solid white;"></div>`,
                iconSize: [20, 20]
            })
        })
        .addTo(activitiesMap)
        .bindPopup(`<b>${activity.title}</b><br>📍 ${activity.location.name}<br>⏰ ${activity.time}${activity.details ? '<br><small>' + activity.details + '</small>' : ''}`);
    });

    if (activities.length > 0) {
        const bounds = activities.map(a => [a.location.lat, a.location.lon]);
        activitiesMap.fitBounds(bounds);
    }
}

function navigateToActivity(activityId) {
    let lat = 34.0523;
    let lon = -118.2437;

    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            position => {
                lat = position.coords.latitude;
                lon = position.coords.longitude;
                fetchActivityRoute(activityId, lat, lon);
            },
            () => {
                fetchActivityRoute(activityId, lat, lon);
            }
        );
    } else {
        fetchActivityRoute(activityId, lat, lon);
    }
}

function fetchActivityRoute(activityId, lat, lon) {
    fetch(`/api/activity/${activityId}/route?lat=${lat}&lon=${lon}`)
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert('Error: ' + data.error);
            return;
        }

        // Switch to navigation tab
        switchTab('navigation');
        
        // Set coordinates
        document.getElementById('start-lat').value = lat;
        document.getElementById('start-lon').value = lon;
        document.getElementById('end-lat').value = data.activity.location.lat;
        document.getElementById('end-lon').value = data.activity.location.lon;

        // Draw route
        setTimeout(() => {
            planRoute();
        }, 100);
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Failed to get route to activity');
    });
}

// Booking Modal Functions
function openBookingModal(activityId) {
    const modal = document.getElementById('booking-modal');
    modal.style.display = 'block';
    
    // Fetch booking schedule
    fetch(`/api/activity/${activityId}/schedule`)
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            document.getElementById('booking-schedule').innerHTML = '<p>Error loading schedule</p>';
            return;
        }
        
        displayBookingSchedule(data, activityId);
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('booking-schedule').innerHTML = '<p>Error loading schedule</p>';
    });
}

function displayBookingSchedule(schedule, activityId) {
    const scheduleDiv = document.getElementById('booking-schedule');
    let html = '<h3>Available Time Slots</h3><table class="schedule-table"><thead><tr><th>Time Slot</th>';
    
    schedule.rooms.forEach(room => {
        html += `<th>${room.name}<br><small>(${room.capacity} people)</small></th>`;
    });
    html += '</tr></thead><tbody>';
    
    schedule.time_slots.forEach(slot => {
        html += `<tr><td><strong>${slot.time}</strong></td>`;
        schedule.rooms.forEach(room => {
            const isAvailable = slot.available.includes(room.id);
            if (isAvailable) {
                html += `<td><button class="btn-available" onclick="selectBookingSlot(${activityId}, ${room.id}, '${slot.time}')">Available</button></td>`;
            } else {
                html += `<td><span class="btn-full">Full</span></td>`;
            }
        });
        html += '</tr>';
    });
    
    html += '</tbody></table>';
    scheduleDiv.innerHTML = html;
}

function selectBookingSlot(activityId, roomId, timeSlot) {
    document.getElementById('book-room-id').value = roomId;
    document.getElementById('book-time-slot').value = timeSlot;
    document.getElementById('booking-form').style.display = 'block';
    document.getElementById('booking-schedule').style.display = 'none';
    
    // Get room name from schedule
    fetch(`/api/activity/${activityId}/schedule`)
    .then(response => response.json())
    .then(data => {
        const room = data.rooms.find(r => r.id === roomId);
        if (room) {
            document.querySelector('#booking-form h3').textContent = `Book ${room.name} - ${timeSlot}`;
        }
    });
}

function closeBookingModal() {
    document.getElementById('booking-modal').style.display = 'none';
    document.getElementById('booking-form').style.display = 'none';
    document.getElementById('booking-schedule').style.display = 'block';
    document.getElementById('book-form').reset();
}

// Registration Modal Functions
function openRegistrationModal(activityId, activityTitle) {
    const modal = document.getElementById('registration-modal');
    document.getElementById('register-activity-id').value = activityId;
    document.getElementById('registration-activity-title').textContent = activityTitle;
    modal.style.display = 'block';
}

function closeRegistrationModal() {
    document.getElementById('registration-modal').style.display = 'none';
    document.getElementById('register-form').reset();
}

// Initialize form handlers when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initForms);
} else {
    initForms();
}

function initForms() {
    // Booking form
    const bookForm = document.getElementById('book-form');
    if (bookForm) {
        bookForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const activityId = 4; // Study Room Reservation
            const roomId = parseInt(document.getElementById('book-room-id').value);
            const timeSlot = document.getElementById('book-time-slot').value;
            const studentName = document.getElementById('book-student-name').value;
            const studentId = document.getElementById('book-student-id').value;
            
            fetch(`/api/activity/${activityId}/book`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    room_id: roomId,
                    time_slot: timeSlot,
                    student_name: studentName,
                    student_id: studentId
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('✅ ' + data.message);
                    closeBookingModal();
                    loadActivities(); // Refresh activities
                } else {
                    alert('Error: ' + data.error);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Failed to book room');
            });
        });
    }
    
    // Registration form
    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const activityId = parseInt(document.getElementById('register-activity-id').value);
            const name = document.getElementById('register-name').value;
            const major = document.getElementById('register-major').value;
            const phone = document.getElementById('register-phone').value;
            const studentNumber = document.getElementById('register-student-number').value;
            const email = document.getElementById('register-email').value;
            
            fetch(`/api/activity/${activityId}/register`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    name: name,
                    major: major,
                    phone: phone,
                    student_number: studentNumber,
                    email: email
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('✅ ' + data.message);
                    closeRegistrationModal();
                } else {
                    alert('Error: ' + data.error);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Failed to register');
            });
        });
    }
    
    // Close modals when clicking outside
    window.onclick = function(event) {
        const bookingModal = document.getElementById('booking-modal');
        const registrationModal = document.getElementById('registration-modal');
        if (event.target === bookingModal) {
            closeBookingModal();
        }
        if (event.target === registrationModal) {
            closeRegistrationModal();
        }
    }
}

