import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from src.agents.graph import create_graph

def generate_diagram():
    print("Generating graph diagram...")
    try:
        app = create_graph()
        png_data = app.get_graph().draw_mermaid_png()
        
        output_path = "docs/architecture/diagram.png"
        
        with open(output_path, "wb") as f:
            f.write(png_data)
            
        print(f"Diagram saved to: {output_path}")
    except Exception as e:
        print(f"Error generating diagram: {e}")

if __name__ == "__main__":
    generate_diagram()
