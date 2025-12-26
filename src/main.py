from gui import App

if __name__ == "__main__":
    try:
        # Spusti GUI aplikaci
        app = App()
        app.mainloop()
    except Exception as e:
        print(f"Fatal Err: {e}")