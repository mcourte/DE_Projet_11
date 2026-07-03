import sys
import os
import subprocess

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

APP_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app.py")


def main():
    print("Lancement du chatbot Puls-Events...")
    subprocess.run(["streamlit", "run", APP_PATH])


if __name__ == "__main__":
    main()
