# How to Restart Flask Server in PyCharm

## Quick Steps:

### Option 1: Stop and Run Again
1. **Find the Run/Debug toolbar** at the top of PyCharm
2. **Click the red square (Stop button)** to stop the server
3. **Click the green play button (Run)** to start it again

### Option 2: Using Terminal
1. **Open Terminal** in PyCharm: View → Tool Windows → Terminal
2. **Press Ctrl+C** in the terminal where Flask is running (to stop it)
3. **Run again**: `python app.py`

### Option 3: Right-click Method
1. **Right-click on `app.py`** in the project tree (left side)
2. Select **Run 'app'** or **Debug 'app'**

## After Restarting:
1. **Refresh your browser** (F5 or Ctrl+R)
2. Go to the **Activities tab**
3. **Set distance filter to 0** (or leave it empty) to see all activities
4. You should now see **12 activities** with detailed information!

## Troubleshooting:
- If you see "Port already in use": The old server is still running. Stop it first (Ctrl+C in terminal)
- If changes don't appear: Make sure you saved all files and restarted the server

