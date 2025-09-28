import { useAppSelector, useAppDispatch } from "./hooks"
import styles from "./ChannelEditor.module.css"
import type { RootState } from "./store"

export const ChannelEditor: React.FC = () => {
  const dispatch = useAppDispatch()
  const channels = useAppSelector((state: RootState) => state.channelsState.channels)
  const selectedNoteId = useAppSelector((state: RootState) => state.channelsState.selectedNoteId)

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

  return (
    <div className={styles.channelEditor}>
      <h2>Channel-Based Note Editor</h2>
      <div>
        {channels.map(channel => (
          <div key={channel.id} className={styles.channel}>
            <h3>{channel.name} (Volume: {channel.volume})</h3>
            <button onClick={() => { handleAddNote(channel.id) }}>
              + New Note
            </button>
            <div className={styles.notes}>
              {channel.notes.map(note => (
                <div
                  key={note.id}
                  className={
                    note.id === selectedNoteId
                      ? `${styles.note} ${styles.selected}`
                      : styles.note
                  }
                  onClick={() => { handleSelectNote(note.id) }}
                  tabIndex={0}
                  role="button"
                  aria-pressed={note.id === selectedNoteId}
                >
                  Pitch: {note.pitch} Hz, Start: {note.start_time}, Duration: {note.duration}
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
