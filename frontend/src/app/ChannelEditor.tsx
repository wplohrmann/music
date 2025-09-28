import { useAppSelector, useAppDispatch } from "./hooks"
import styles from "./ChannelEditor.module.css"
import type { RootState } from "./store"
import React, { useState } from "react"

// Types
type Note = {
  id: string
  pitch: number
  start_time: number
  duration: number
}
type Channel = {
  id: string
  name: string
  volume: number
  notes: Note[]
}

export const ChannelEditor: React.FC = () => {
  const dispatch = useAppDispatch()
  const channels: Channel[] = useAppSelector((state: RootState) => state.channelsState.channels)
  const selectedNoteId = useAppSelector((state: RootState) => state.channelsState.selectedNoteId)

  // Grid settings
  const grid = {
    pitchMin: 220, // Hz
    pitchMax: 880, // Hz
    gridHeight: 400, // px
    gridWidth: 800, // px
    timeMax: 16, // beats
    pitchStep: 20, // Hz per grid row
    timeStep: 1, // beat per grid col
  }

  const [draggedNote, setDraggedNote] = useState<null | { channelId: string; noteId: string }> (null)
  const [dragOffset, setDragOffset] = useState<{ x: number; y: number } | null>(null)

  const handleAddNote = (channelId: string) => {
    const newNote = {
      id: `note-${Date.now().toString()}`,
      pitch: 440,
      start_time: 0,
      duration: 1,
    }
    dispatch({
      type: "channels/addNote",
      payload: { channelId, note: newNote },
    })
  }

  const handleSelectNote = (noteId: string) => {
    dispatch({
      type: "channels/selectNote",
      payload: noteId,
    })
  }

  // Drag logic
  const handleNoteMouseDown = (
    e: React.MouseEvent,
    channelId: string,
    noteId: string
  ) => {
    if (!e.metaKey) return // Only start drag if Cmd is held
    e.preventDefault()
    setDraggedNote({ channelId, noteId })
    setDragOffset({ x: e.clientX, y: e.clientY })
    handleSelectNote(noteId)
  }

  // Mouse move is not used for live preview
  // Mouse move is not used for live preview
  // (function removed)

  const handleMouseUp = (e: MouseEvent) => {
    if (!draggedNote || !dragOffset) return
    // Calculate new position
    const channel = channels.find(c => c.id === draggedNote.channelId)
    if (!channel) return
    const note = channel.notes.find(n => n.id === draggedNote.noteId)
    if (!note) return

    // Get grid container position
    const gridElem = document.getElementById(`grid-${channel.id}`)
    if (!gridElem) return
    const rect = gridElem.getBoundingClientRect()
    const relX = e.clientX - rect.left
    const relY = e.clientY - rect.top

    // Snap to grid
    const snappedTime = Math.max(0, Math.min(grid.timeMax, Math.round(relX / (grid.gridWidth / grid.timeMax))))
    const snappedPitch = Math.max(grid.pitchMin, Math.min(grid.pitchMax,
      Math.round(grid.pitchMin + ((grid.gridHeight - relY) / grid.gridHeight) * (grid.pitchMax - grid.pitchMin) / grid.pitchStep) * grid.pitchStep
    ))

    dispatch({
      type: "channels/moveNote",
      payload: {
        channelId: channel.id,
        noteId: note.id,
        newStart: snappedTime,
        newPitch: snappedPitch,
      },
    })
    setDraggedNote(null)
    setDragOffset(null)
  }

  React.useEffect(() => {
    if (draggedNote) {
      window.addEventListener("mouseup", handleMouseUp)
      return () => {
        window.removeEventListener("mouseup", handleMouseUp)
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [draggedNote])

  // Position note in grid
  const getNoteStyle = (note: Note) => {
    const x = (note.start_time / grid.timeMax) * grid.gridWidth
    const y = grid.gridHeight - ((note.pitch - grid.pitchMin) / (grid.pitchMax - grid.pitchMin)) * grid.gridHeight
    const width = (note.duration / grid.timeMax) * grid.gridWidth
    return {
      position: "absolute" as const,
      left: x,
      top: y,
      width: Math.max(40, width),
      height: 24,
      zIndex: note.id === selectedNoteId ? 2 : 1,
      cursor: "grab",
      background: note.id === selectedNoteId ? "#aaf" : "#eee",
      border: "1px solid #888",
      borderRadius: 4,
      boxShadow: note.id === selectedNoteId ? "0 2px 8px #88f4" : "none",
      userSelect: "none" as const,
    }
  }

  return (
    <div className={styles.channelEditor}>
      <div>
        {channels.map(channel => (
          <div key={channel.id} className={styles.channel}>
            <h3>{channel.name} (Volume: {channel.volume})</h3>
            <button onClick={() => { handleAddNote(channel.id) }}>
              + New Note
            </button>
            <div
              id={`grid-${channel.id}`}
              className={styles.notes}
              style={{
                position: "relative",
                width: grid.gridWidth,
                height: grid.gridHeight,
                border: "1px solid #ccc",
                background: "linear-gradient(90deg, #f8f8f8 95%, #e0e0e0 100%)",
                marginBottom: 24,
                overflow: "hidden",
              }}
            >
              {/* Render grid lines */}
              {Array.from({ length: grid.timeMax + 1 }).map((_, i) => (
                <div
                  key={"v-" + String(i)}
                  style={{
                    position: "absolute",
                    left: (i / grid.timeMax) * grid.gridWidth,
                    top: 0,
                    width: 1,
                    height: grid.gridHeight,
                    background: "#ddd",
                  }}
                />
              ))}
              {Array.from({ length: Math.floor((grid.pitchMax - grid.pitchMin) / grid.pitchStep) + 1 }).map((_, i) => (
                <div
                  key={"h-" + String(i)}
                  style={{
                    position: "absolute",
                    left: 0,
                    top: (i / ((grid.pitchMax - grid.pitchMin) / grid.pitchStep)) * grid.gridHeight,
                    width: grid.gridWidth,
                    height: 1,
                    background: "#eee",
                  }}
                />
              ))}
              {/* Render notes */}
              {channel.notes.map(note => (
                <div
                  key={note.id}
                  style={getNoteStyle(note)}
                  onMouseDown={e => { handleNoteMouseDown(e, channel.id, note.id) }}
                  tabIndex={0}
                  role="button"
                  aria-pressed={note.id === selectedNoteId}
                  title={`Pitch: ${String(note.pitch)} Hz, Start: ${String(note.start_time)}, Duration: ${String(note.duration)}`}
                >
                  {`Pitch: ${String(note.pitch)}Hz`}
                  <br />
                  {`Start: ${String(note.start_time)}`}
                  <br />
                  {`Dur: ${String(note.duration)}`}
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
