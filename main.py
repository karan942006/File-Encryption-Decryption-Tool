import sys
from gui import App

def main():
    """
    Launches the SecureFile desktop application.
    """
    try:
        # Inform user on console
        print("SecureFile started.")
        app = App()
        app.mainloop()
    except Exception as e:
        # Print errors to stderr if app startup fails
        print(f"Fatal error launching SecureFile: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
