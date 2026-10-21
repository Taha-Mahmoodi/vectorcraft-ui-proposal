//! Offscreen 1440x900 @2x renders of the whole VectorCraft window (poster document, ellipse
//! selected). Usage: vc-kittest-shots OUT_DIR [scheme:brightness:tab ...]
use egui::vec2;
use serde_json::json;
use vectorcraft_engine::Session;
use vectorcraft_ui_egui::VectorcraftApp;

fn main() {
    let mut args = std::env::args().skip(1);
    let dir = std::path::PathBuf::from(args.next().expect("OUT_DIR"));
    std::fs::create_dir_all(&dir).unwrap();
    let mut shots: Vec<String> = args.collect();
    if shots.is_empty() {
        for b in ["dark", "mediumDark", "mediumLight", "light"] {
            for tab in ["properties", "layers"] {
                shots.push(format!("flat:{b}:{tab}"));
            }
        }
        for b in ["mediumDark", "light"] {
            for tab in ["properties", "layers"] {
                shots.push(format!("modern:{b}:{tab}"));
            }
        }
    }
    for shot in shots {
        let [scheme, b, tab]: [&str; 3] = shot.splitn(3, ':').collect::<Vec<_>>().try_into().expect("scheme:brightness:tab");
        let mut app = VectorcraftApp::new(Session::new(), Default::default());
        app.run("file.new", json!({"width": 800, "height": 600})).unwrap();
        let mut id = |cmd: &str, p: serde_json::Value| app.session.execute(cmd, &p).unwrap()["id"].as_u64().unwrap();
        let e = id("shape.ellipse", json!({"x":120,"y":150,"width":260,"height":260}));
        let r = id("shape.rectangle", json!({"x":420,"y":210,"width":240,"height":200}));
        let t = id("text.create", json!({"x":120,"y":530,"text":"Poster draft","size":46}));
        for (i, c) in [(e, "#F2B134"), (r, "#2A6F97"), (t, "#1B1B1B")] {
            app.session.execute("select.set", &json!({"ids":[i]})).unwrap();
            app.session.execute("paint.setFill", &json!({"color": c})).unwrap();
            app.session.execute("paint.setStroke", &json!({"none": true})).unwrap();
        }
        app.session.execute("select.set", &json!({"ids":[e]})).unwrap();
        app.session.execute("prefs.set", &json!({"key":"uiColorScheme","value":scheme})).unwrap();
        app.run("window.brightness", json!({"brightness": b})).unwrap();
        app.run("window.panel", json!({"panel": tab})).unwrap();
        let mut ready = false;
        let mut h = egui_kittest::Harness::builder().with_size(vec2(1440.0, 900.0)).with_pixels_per_point(2.0).wgpu().build_ui_state(
            move |ui, app: &mut VectorcraftApp| {
                if !ready {
                    egui_extras::install_image_loaders(ui.ctx());
                    vectorcraft_ui_egui::theme::install_fonts(ui.ctx());
                    ready = true;
                    return;
                }
                app.logic(ui.ctx());
                app.ui(ui);
            },
            app,
        );
        h.input_mut().max_texture_side = Some(8192);
        h.run_steps(8);
        let path = dir.join(format!("kittest-{scheme}-{b}-{tab}.png"));
        h.render().unwrap().save(&path).unwrap();
        let canvas = h.state().canvas_rect.map(|r| [r.min.x, r.min.y, r.width(), r.height()]);
        let meta = json!({"canvas_rect": canvas, "pixels_per_point": h.ctx.pixels_per_point()});
        std::fs::write(path.with_extension("json"), serde_json::to_string_pretty(&meta).unwrap()).unwrap();
        println!("{}", path.display());
    }
}
