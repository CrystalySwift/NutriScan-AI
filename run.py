# run.py
import subprocess
import sys

def install_requirements():
    """Install required packages"""
    print("📦 Installing requirements...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    print("✅ Requirements installed!")

def run_app():
    """Run the Streamlit app"""
    print("🚀 Starting Food Nutrition Assistant...")
    print("🌐 Open your browser and go to: http://localhost:8501")
    print("📝 Demo credentials:")
    print("   Email: demo@example.com")
    print("   Password: demo123")
    print("\nPress Ctrl+C to stop the application")
    
    subprocess.run(["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"])

if __name__ == "__main__":
    try:
        install_requirements()
        run_app()
    except KeyboardInterrupt:
        print("\n👋 Application stopped")
    except Exception as e:
        print(f"❌ Error: {e}")