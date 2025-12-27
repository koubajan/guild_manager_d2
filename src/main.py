from gui import App

if __name__ == "__main__":
    try:
        # Run GUI application
        app = App()
        app.mainloop()
    except Exception as e:
        print(f"Critical error: {e}")