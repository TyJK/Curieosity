use bevy::prelude::*;

#[derive(Resource, Clone)]
pub struct UiFonts {
    pub main: Handle<Font>,
    pub semibold: Handle<Font>,
    pub bold: Handle<Font>,
    /// DejaVu Sans: used for equations, because Noto Sans has no arrow (U+2192) glyph.
    pub symbols: Handle<Font>,
}

pub fn load_ui_fonts(mut commands: Commands, asset_server: Res<AssetServer>) {
    commands.insert_resource(UiFonts {
        main: asset_server.load("fonts/NotoSans-Regular.ttf"),
        semibold: asset_server.load("fonts/NotoSans-SemiBold.ttf"),
        bold: asset_server.load("fonts/NotoSans-Bold.ttf"),
        symbols: asset_server.load("fonts/DejaVuSans.ttf"),
    });
}
