# DAW (Digital Audio Workstation) - Project Plan

## Features

### 1. Channel-Based Note Editor
**Summary:** The frontend displays multiple channels, each containing a set of notes that can be created, moved, selected, and deleted. Notes snap to specific pitches and beats for precise editing.

**Detailed Description:**
- **Frontend:**
  - Render a vertical stack of channels, each representing an instrument or track.
  - Within each channel, display notes as draggable blocks that snap to a grid (pitch on Y-axis, beat/time on X-axis).
  - Implement controls for creating new notes (e.g., click or drag), selecting notes (single/multi-select), moving notes (drag-and-drop with snapping), and deleting notes (keyboard or button).
  - Visual feedback for selected notes and grid snapping.
- **Backend:**
  - Store note data per channel (pitch, start time, duration, velocity, etc.) in a structured format (e.g., JSON).
  - Provide API endpoints for saving, loading, and updating note arrangements.

### 2. Playback Engine
**Summary:** Users can play back the current arrangement by sending note data to the backend, which generates audio for each channel and returns WAV files for playback. Playback can be paused and resumed.

**Detailed Description:**
- **Frontend:**
  - Serialize the current note arrangement and send it to the backend via an API call.
  - Receive one WAV file per channel and play them in sync using the Web Audio API.
  - Provide controls for play, pause, and resume.
  - Display playback progress visually (e.g., playhead moving across channels).
- **Backend:**
  - FastAPI server receives note data and generates audio for each channel (e.g., using a synthesis library or MIDI-to-audio engine).
  - Return WAV files for each channel in the response.
  - Support efficient audio generation for real-time or near-real-time playback.

### 3. Note Manipulation Tools
**Summary:** Users can select, move, and delete notes using intuitive UI tools. Multi-selection and keyboard shortcuts are supported for efficient editing.

**Detailed Description:**
- **Frontend:**
  - Implement selection tools (click, shift-click, drag-select) for single and multiple notes.
  - Enable moving notes with drag-and-drop, snapping to grid.
  - Support deleting selected notes via keyboard (e.g., Delete key) or UI buttons.
  - Provide undo/redo functionality for editing actions.
- **Backend:**
  - Update note data in response to frontend actions.
  - Ensure data integrity and support batch updates for multi-note operations.

### 4. Channel Management
**Summary:** Users can add, remove, and rename channels to organize their music. Each channel can have its own instrument or sound settings.

**Detailed Description:**
- **Frontend:**
  - UI controls for adding new channels, removing existing ones, and renaming channels.
  - Allow configuration of channel properties (e.g., instrument type, volume).
- **Backend:**
  - Store channel metadata and settings.
  - Provide API endpoints for channel management operations.

### 5. Project Persistence
**Summary:** Users can save and load projects, preserving all channels and notes. Projects can be exported and imported for sharing or backup.

**Detailed Description:**
- **Frontend:**
  - Save the current state (channels, notes, settings) to local storage or via API.
  - Load saved projects and restore the editor state.
  - Export/import project files (e.g., JSON format).
- **Backend:**
  - Store projects in a database or file system.
  - Provide endpoints for saving, loading, exporting, and importing projects.

