# Minimalist Todo (Pygame)

A desktop todo list application built entirely with Python and Pygame. The interface embraces a clean black-and-white theme, animated wave-like background, and focused modal view for item details.

## Features
- Left-aligned todo list with uniform item sizes and clipped text for long entries.
- Borderless bottom-left input with animated underline and subtle vibration while typing.
- Checkbox and delete controls on each item to mark completion or remove tasks.
- Click any item to view its full text in a centered modal with blurred background.
- Animated white wave lines on a black background that react to mouse movement.
- Lightweight alert system for empty submissions and other errors.

## Getting Started
### Prerequisites
- Python 3.10+

### Installation
1. Create and activate a virtual environment (recommended).
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application
```bash
python main.py
```

The Pygame window will open with the todo interface. Click the input at the bottom-left or press Enter to start typing, then press Enter again to add the todo.

## Known Limitations
- The list does not scroll; if many items are added they may extend beyond the visible area.
- The blur effect is simulated by scaling surfaces and may appear softer on high-resolution displays.

## Project Structure
- `main.py` – entry point that launches the application.
- `todo_app/app.py` – main event loop, rendering, and interaction logic.
- `todo_app/animations.py` – wave background animation and input vibration helper.
- `todo_app/utils.py` – helper functions for text clipping and surface blur.
- `todo_app/models.py` – simple data model for todo items.

