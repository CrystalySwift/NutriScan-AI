# run_with_model.py
import os
import sys
import subprocess

def main():
    print("🚀 FOOD NUTRITION ASSISTANT - WITH KERAS MODEL")
    print("=" * 60)
    
    # Check for model
    model_name = 'best_food_effnet.keras'
    
    if not os.path.exists(model_name):
        print(f"❌ {model_name} not found in current directory!")
        print("\n📁 Files in directory:")
        for f in os.listdir('.'):
            if f.endswith(('.keras', '.h5')):
                print(f"  🤖 {f}")
        
        print(f"\n⚠️  Please ensure '{model_name}' is in this directory")
        print(f"💡 Or rename your model file to '{model_name}'")
        
        rename = input(f"\nDo you want to rename a model file to '{model_name}'? (y/n): ")
        if rename.lower() == 'y':
            model_files = [f for f in os.listdir('.') if f.endswith(('.keras', '.h5'))]
            if model_files:
                print("\nAvailable model files:")
                for i, f in enumerate(model_files, 1):
                    print(f"  {i}. {f}")
                
                try:
                    choice = int(input(f"\nSelect file to rename (1-{len(model_files)}): "))
                    if 1 <= choice <= len(model_files):
                        old_name = model_files[choice-1]
                        import shutil
                        shutil.copy(old_name, model_name)
                        print(f"✅ Copied {old_name} to {model_name}")
                    else:
                        print("❌ Invalid choice")
                except:
                    print("❌ Invalid input")
            else:
                print("❌ No model files found")
        
        return
    
    print(f"✅ Found model: {model_name}")
    size_mb = os.path.getsize(model_name) / (1024 * 1024)
    print(f"📏 Model size: {size_mb:.1f} MB")
    
    # Check class names
    if os.path.exists('class_names.txt'):
        with open('class_names.txt', 'r', encoding='utf-8') as f:
            class_count = len(f.readlines())
        print(f"🏷️  Class names: {class_count} foods")
    else:
        print("🏷️  Class names: Will be auto-generated")
    
    # Check DeepSeek API
    api_key = os.environ.get('DEEPSEEK_API_KEY')
    if api_key:
        print(f"🔑 DeepSeek API: Available ({api_key[:10]}...)")
    else:
        print("🔑 DeepSeek API: Will input in app")
    
    print("\n" + "=" * 60)
    print("🎯 STARTING APPLICATION...")
    print("=" * 60)
    print("\n📝 INSTRUCTIONS:")
    print("1. Open browser to: http://localhost:8501")
    print("2. Login with: demo@example.com / demo123")
    print("3. Enter DeepSeek API key in sidebar")
    print("4. Click 'Upload Gambar' tab")
    print("5. Upload food photos for automatic analysis!")
    print("\n" + "=" * 60)
    
    input("Press Enter to start...")
    
    # Start Streamlit
    subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])

if __name__ == "__main__":
    main()