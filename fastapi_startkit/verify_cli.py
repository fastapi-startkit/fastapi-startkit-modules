import sys
import os

# Add the package to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi_startkit.application import Application
from fastapi_startkit.providers.Provider import Provider

class DummyProvider(Provider):
    def register(self):
        if self.application.running_in_console():
            print("Detected: Running in console during register")
        
        # Register a command via provider
        self.commands([self.provider_hello])

    def provider_hello(self):
        """Hello from dummy provider"""
        print("Command from provider is working!")

def test_cli():
    # Instantiate application with a dummy provider and console flag
    app = Application(base_path=os.getcwd(), providers=[DummyProvider], console=True)
    
    print(f"Running in console (before): {app.running_in_console()}")
    
    print("Testing 'hello' command...")
    app.handle_command(["hello"])
    
    print("Testing provider command...")
    app.handle_command(["provider-hello"])

    print(f"Running in console (after): {app.running_in_console()}")

if __name__ == "__main__":
    test_cli()
