# setup_guide.py
import os
import shutil

def setup_for_keras_model():
    """
    Setup guide for .keras model
    """
    print("🔄 SETUP FOR .KERAS MODEL")
    print("=" * 60)
    
    # 1. Check current files
    print("\n1. 📁 Checking current directory...")
    files = os.listdir('.')
    print(f"   Files: {files}")
    
    # 2. Look for .keras model
    keras_models = [f for f in files if f.endswith('.keras')]
    h5_models = [f for f in files if f.endswith('.h5')]
    
    print(f"\n2. 🤖 Looking for Keras models...")
    print(f"   .keras files: {keras_models}")
    print(f"   .h5 files: {h5_models}")
    
    # 3. Setup instructions
    print(f"\n3. 📝 SETUP INSTRUCTIONS:")
    
    if 'best_food_effnet.keras' in keras_models:
        print("   ✅ Model sudah ada dengan nama yang benar!")
    elif keras_models:
        # Rename to correct name
        model_file = keras_models[0]
        print(f"   🔄 Renaming {model_file} to best_food_effnet.keras")
        try:
            if os.path.exists('best_food_effnet.keras'):
                backup_name = f"backup_{os.path.basename(model_file)}"
                shutil.move('best_food_effnet.keras', backup_name)
                print(f"   💾 Backup dibuat: {backup_name}")
            
            shutil.copy(model_file, 'best_food_effnet.keras')
            print("   ✅ Model renamed successfully!")
        except Exception as e:
            print(f"   ❌ Error renaming: {e}")
    else:
        print("   ❌ No .keras model found!")
        print("   ℹ️  Please place your best_food_effnet.keras in this directory")
    
    # 4. Check class names
    print(f"\n4. 🏷️ Checking class names...")
    if os.path.exists('class_names.txt'):
        with open('class_names.txt', 'r', encoding='utf-8') as f:
            classes = f.readlines()
        print(f"   ✅ class_names.txt found with {len(classes)} classes")
    else:
        print("   ℹ️  No class_names.txt found (will be auto-created)")
    
    # 5. Test model
    print(f"\n5. 🧪 Testing model...")
    try:
        from image_classifier import test_model_compatibility
        test_model_compatibility()
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 NEXT STEPS:")
    print("1. Run: streamlit run app.py")
    print("2. Open: http://localhost:8501")
    print("3. Enter DeepSeek API key in sidebar")
    print("4. Upload food photos!")
    print("=" * 60)

if __name__ == "__main__":
    setup_for_keras_model()