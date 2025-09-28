// Types
export type Note = {
  id: string;
  pitch: number; // Hz
  start_time: number; // seconds or beats
  duration: number; // seconds or beats
  velocity?: number;
  // Add more note props as needed
};

export type Channel = {
  id: string;
  name: string;
  volume: number;
  notes: Note[];
  // Add more channel props as needed
};

// Initial dummy data
const initialState: Channel[] = [
  {
    id: "channel-1",
    name: "Piano",
    volume: 0.8,
    notes: [
      { id: "note-1", pitch: 440, start_time: 0, duration: 1 },
      { id: "note-2", pitch: 494, start_time: 1.5, duration: 0.5 },
    ],
  },
  {
    id: "channel-2",
    name: "Synth",
    volume: 0.6,
    notes: [
      { id: "note-3", pitch: 330, start_time: 0.4, duration: 2 },
    ],
  },
];

// Redux slice
import { createSlice } from "@reduxjs/toolkit";

type ChannelsState = {
  channels: Channel[];
  selectedNoteId: string | null;
};

const initialChannelsState: ChannelsState = {
  channels: initialState,
  selectedNoteId: null,
};

const channelsSlice = createSlice({
  name: "channels",
  initialState: initialChannelsState,
  reducers: {
    addNote: (
      state,
      action: { payload: { channelId: string; note: Note } }
    ) => {
      const { channelId, note } = action.payload;
      const channel = state.channels.find(c => c.id === channelId);
      if (channel) {
        channel.notes.push(note);
      }
    },
    selectNote: (
      state,
      action: { payload: string }
    ) => {
      state.selectedNoteId = action.payload;
    },
    // More actions can be added here
  },
});

export const channelsReducer = channelsSlice.reducer;
export const channelsActions = channelsSlice.actions;
