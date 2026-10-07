# PyCharm Setup Guide for CampusNav

## Step-by-Step Instructions

### 1. Open the Project
- **File** → **Open**
- Navigate to: `D:\Year_3-first semester\Human-Computer Interaction\Homework06\smart-campus-prototype-fixed`
- Click **OK**

### 2. Configure Python Interpreter
- **File** → **Settings** (or `Ctrl+Alt+S`)
- Go to: **Project** → **Python Interpreter**
- If no interpreter is selected:
  - Click the gear icon ⚙️ → **Add**
  - Select your Python 3.9+ interpreter
  - Click **OK**

### 3. Install Dependencies
PyCharm will usually detect `requirements.txt` and show a notification at the top.
- Click **Install requirements** in the notification, OR
- Open Terminal in PyCharm: **View** → **Tool Windows** → **Terminal**
- Run: `pip install -r requirements.txt`

### 4. Create Run Configuration
- Click the dropdown next to the run button (top right) → **Edit Configurations...**
- Click **+** → **Python**
- Configure:
  - **Name**: `CampusNav Flask App`
  - **Script path**: Click folder icon → select `app.py`
  - **Working directory**: Should auto-fill to project root
  - **Python interpreter**: Select your Python interpreter
- Click **OK**

### 5. Run the Application
- Click the green ▶️ **Run** button (or press `Shift+F10`)
- Wait for: `Running on http://0.0.0.0:5000`
- Open browser: **http://localhost:5000**

## Alternative: Run from Terminal
1. Open Terminal in PyCharm: **View** → **Tool Windows** → **Terminal**
2. Run: `python app.py`
3. Open browser: **http://localhost:5000**

## Troubleshooting

### Port Already in Use
If port 5000 is busy:
- Edit `app.py` line 221
- Change: `port=5000` to `port=5001`
- Access: **http://localhost:5001**

### Module Not Found
- Make sure Python interpreter is set correctly
- Reinstall dependencies: `pip install -r requirements.txt`

### Debug Mode
- Set breakpoints by clicking left of line numbers
- Run in Debug mode: Click 🐛 **Debug** button (or `Shift+F9`)
- Step through code with F8 (Step Over) or F7 (Step Into)

## Quick Tips
- **Auto-format code**: `Ctrl+Alt+L` (Windows) or `Cmd+Option+L` (Mac)
- **Run current file**: Right-click `app.py` → **Run 'app'**
- **View logs**: Check the Run/Debug console at the bottom

