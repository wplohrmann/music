use leptos::{component, html::{div, ElementChild}, prelude::*, IntoView};
use reactive_stores::{Field, Store};
use serde::{Deserialize, Serialize};
use std::sync::atomic::{AtomicUsize};

static NEXT_ID: AtomicUsize = AtomicUsize::new(3);

stylance::import_style!(style, "App.module.css");

#[derive(Debug, Store, Serialize, Deserialize)]
struct Note {
    id: usize,
    pitch: f32,
    duration: f32,
    start: f32,
}

#[derive(Debug, Store, Serialize, Deserialize)]
struct Channel {
    id: usize,
    name: String,
    #[store(key: usize = |note| note.id)]
    notes: Vec<Note>,
}

#[derive(Debug, Store, Serialize, Deserialize)]
struct State {
    #[store(key: usize = |channel| channel.id)]
    channels: Vec<Channel>,
    bpm: f32,
}

fn data() -> State {
    State {
        channels: vec![
            Channel {
                id: 0,
                name: "Channel 1".to_string(),
                notes: vec![Note {
                    id: 0,
                    pitch: 60.0,
                    duration: 1.0,
                    start: 0.0,
                }, Note {
                    id: 1,
                    pitch: 64.0,
                    duration: 0.5,
                    start: 1.0,
                }],
            },
            Channel {
                id: 1,
                name: "Channel 2".to_string(),
                notes: vec![Note {
                    id: 3,
                    pitch: 62.0,
                    duration: 1.0,
                    start: 0.0,
                }],
            },
        ],
        bpm: 120.0,
    }
}

#[component]
fn ChannelComponent(
    #[prop(into)] channel: Field<Channel>,
) -> impl IntoView {
    view! {
        <div class=style::channel>
            <div class=style::channelTop>
                {channel.name().get()}
            </div>
            <div class=style::channelNotes>
                <For 
                    each=move || channel.notes()
                    key=|note| note.id().get()
                    let:note
                >
                    <div>{format!("Note: pitch {}, duration {}, start {}", note.pitch().get(), note.duration().get(), note.start().get())}</div>
                </For>
            </div>
        </div>
    }
}

#[component]
pub fn App() -> impl IntoView {
    let store = Store::new(data());
    store.bpm().set(140.0);

    view! {
        <div class=style::container>
            <div class=style::navbar/>
            <For
                each=move || store.channels()
                key=|channel| channel.id().get()
                let:channel
            >
                <ChannelComponent channel />
            </For>
        </div>
    }
}

fn main() {
    leptos::mount::mount_to_body(App)
}
