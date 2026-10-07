# Quick Start Guide

## Step 1: Install Dependencies

Open a terminal in the project directory and run:

```bash
pip install -r requirements.txt
```

## Step 2: Run the Application

```bash
python app.py
```

You should see output like:
```
 * Running on http://0.0.0.0:5000
```

## Step 3: Open in Browser

Navigate to: **http://localhost:5000**

## Testing the Features

### Navigation
1. Go to the "Navigation" tab
2. Enter coordinates:
   - Start: Lat 34.0520, Lon -118.2430
   - End: Lat 34.0525, Lon -118.2438
3. Click "Plan Route"
4. View the path on the map

### Emergency SOS
1. Go to the "Emergency SOS" tab
2. Click the red "One-Click SOS" button
3. View your location and nearest safe point on the map

### Activities
1. Go to the "Activities" tab
2. Filter by category or distance
3. Click "Navigate" on any activity to get directions

## Default Test Coordinates

The system uses sample coordinates around:
- **Latitude**: 34.0523
- **Longitude**: -118.2437

These are simulated campus coordinates. In a real deployment, you would use actual campus coordinates.

## Troubleshooting

- **Port already in use**: Change the port in `app.py` (line 221): `app.run(debug=True, host='0.0.0.0', port=5001)`
- **Module not found**: Make sure all dependencies are installed: `pip install -r requirements.txt`
- **Map not loading**: Check your internet connection (Leaflet maps require internet)

