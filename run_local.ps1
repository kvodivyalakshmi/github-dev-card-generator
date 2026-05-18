<<<<<<< HEAD
# Run this script to start the backend locally
cd backend

# Create virtual environment if it doesn't exist
if (!(Test-Path ".venv")) {
    echo "Creating virtual environment..."
    python -m venv .venv
}

# Activate virtual environment
echo "Activating virtual environment..."
& .\.venv\Scripts\Activate.ps1

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Run the server
echo "Starting FastAPI server..."
python main.py
=======
# Run this script to start the backend locally
cd backend

# Create virtual environment if it doesn't exist
if (!(Test-Path ".venv")) {
    echo "Creating virtual environment..."
    python -m venv .venv
}

# Activate virtual environment
echo "Activating virtual environment..."
& .\.venv\Scripts\Activate.ps1

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Run the server
echo "Starting FastAPI server..."
python main.py
>>>>>>> ca62818c2cbc4fc30133a98cc1f0a41ad4186545
