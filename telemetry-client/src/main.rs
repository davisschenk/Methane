extern crate pretty_env_logger;
#[macro_use]
extern crate log;

use futures_util::{SinkExt, StreamExt};
use pretty_env_logger::env_logger::{Builder, Env};
use serialport::{available_ports, SerialPortType};
use std::collections::HashMap;
use std::io::{BufRead, BufReader};
use std::sync::{
    atomic::{AtomicUsize, Ordering},
    Arc,
};
use tokio::sync::{mpsc, watch, RwLock};
use tokio_stream::wrappers::UnboundedReceiverStream;
use tokio_stream::wrappers::WatchStream;
use warp::ws::{Message, WebSocket};
use warp::Filter;

const BAUDRATE: u32 = 57600;
const MANUFACTURER: &str = "Future Technology Devices International, Ltd";

const INDEX_HTML: &str = include_str!("main.html");

// Front-end dependencies included in executable for ease of use and portibility
const BOOTSTRAP: &str = include_str!("static/bootstrap.min.js");
const CHART_JS: &str = include_str!("static/chart.js");
const CHART_JS_ADAPTER: &str = include_str!("static/chartjs-adapter-date-fns.bundle.min.js");
const JQUERY: &str = include_str!("static/jquery.min.js");
const LEAFLET: &str = include_str!("static/leaflet.js");

// Type which holds user ids and a channel to send them messages
type Users = Arc<RwLock<HashMap<usize, mpsc::UnboundedSender<Message>>>>;

static NEXT_USER_ID: AtomicUsize = AtomicUsize::new(1);

fn find_telemetry_radio() -> Option<String> {
    match available_ports() {
        Ok(ports) => {
            for port in ports {
                if let SerialPortType::UsbPort(info) = port.port_type {
                    if let Some(m) = info.manufacturer {
                        if m == MANUFACTURER {
                            return Some(port.port_name);
                        }
                    }
                }
            }
        }

        Err(_e) => {
            error!("Failed to find telemetery radio on serial port.");
            std::process::exit(1);
        }
    }

    None
}

fn connect_telemetry_radio(sender: watch::Sender<String>) {
    let port_name = find_telemetry_radio();

    let port_name = match port_name {
        Some(s) => {
            info!("Connecting to {s}");
            s
        }
        None => panic!("Couldnd find telemetry radio!"),
    };

    match serialport::new(&port_name, BAUDRATE)
        .timeout(std::time::Duration::from_secs(60))
        .open()
    {
        Ok(port) => {
            let mut reader = BufReader::new(port);

            loop {
                let mut message = String::new();
                match reader.read_line(&mut message) {
                    Ok(amt) => {
                        info!("Read {} from telemetry radio", amt);

                        sender.send(message).expect("Failed to send message");
                    }
                    Err(e) => {
                        error!("Failed to read line: {e}!");
                    }
                }
            }
        }
        Err(e) => {
            error!("Failed to open \"{}\". Error: {}", &port_name, e);
            std::process::exit(1);
        }
    }
}

async fn handle_user(ws: WebSocket, users: Users, watch: watch::Receiver<String>) {
    let my_id = NEXT_USER_ID.fetch_add(1, Ordering::Relaxed);

    info!("User connected to ws: {}", my_id);

    // Split the socket into a sender and receive of messages.
    let (mut user_ws_tx, _user_ws_rx) = ws.split();

    // Use an unbounded channel to handle buffering and flushing of messages
    // to the websocket...
    let (tx, rx) = mpsc::unbounded_channel();
    let mut rx = UnboundedReceiverStream::new(rx);

    // Add user to our state
    users.write().await.insert(my_id, tx);

    let mut watch = WatchStream::new(watch);

    loop {
        tokio::select! {
        Some(v) = rx.next() => {
            if let Err(e) = user_ws_tx.send(v).await {
                error!("Disconnecting client from websocket: {}", e);
                break
            };
        }
        Some(v) = watch.next() => {
            if let Err(e) = user_ws_tx.send(Message::text(v)).await {
                error!("Disconnecting client from websocket: {}", e);
                break
            };
        }
        }
    }

    user_disconnected(my_id, &users).await;
}

async fn user_disconnected(id: usize, users: &Users) {
    info!("User {} disconnected from websocket", id);
    users.write().await.remove(&id);
}

#[tokio::main]
async fn main() {
    Builder::from_env(Env::default().default_filter_or("info")).init();

    let users = Users::default();
    let users = warp::any().map(move || users.clone());

    let (broadcast_tx, broadcast_rx): (watch::Sender<String>, watch::Receiver<String>) =
        watch::channel("No Data".to_string());
    let broadcast_rx = warp::any().map(move || broadcast_rx.clone());

    tokio::task::spawn_blocking(move || connect_telemetry_radio(broadcast_tx));

    // GET /ws -> websocket upgrade
    let serial = warp::path("ws")
        .and(warp::ws())
        .and(users)
        .and(broadcast_rx)
        .map(|ws: warp::ws::Ws, users, broadcast_rx| {
            ws.on_upgrade(|websocket| handle_user(websocket, users, broadcast_rx))
        });

    // GET / -> index.html
    let index = warp::path::end().map(|| warp::reply::html(INDEX_HTML));

    // TODO: Try and come up with better way to serve static files while including them in binary
    let bootstrap = warp::path("bootstrap.min.js")
        .map(|| warp::reply::with_header(BOOTSTRAP, "content-type", "text/javascript"));
    let chart_js = warp::path("chart.js")
        .map(|| warp::reply::with_header(CHART_JS, "content-type", "text/javascript"));
    let chart_js_adapter = warp::path("chartjs-adapter-date-fns.bundle.min.js")
        .map(|| warp::reply::with_header(CHART_JS_ADAPTER, "content-type", "text/javascript"));
    let jquery = warp::path("jquery.min.js")
        .map(|| warp::reply::with_header(JQUERY, "content-type", "text/javascript"));
    let leaflet = warp::path("leaflet.js")
        .map(|| warp::reply::with_header(LEAFLET, "content-type", "text/javascript"));

    let static_files = warp::path("static").and(
        bootstrap
            .or(chart_js)
            .or(chart_js_adapter)
            .or(jquery)
            .or(leaflet),
    );

    let routes = warp::get().and(index.or(serial).or(static_files));

    webbrowser::open("http://localhost:8080").unwrap();
    warp::serve(routes).run(([0, 0, 0, 0], 8080)).await;
}
