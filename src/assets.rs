// src/assets.rs

use bevy::{
    asset::{
        io::Reader, // This imports the trait
        AssetLoader,
        // AsyncReadExt, // This trait IS required for reader.read_to_end()
        LoadContext,
    },
    prelude::*,
    reflect::TypePath,
    tasks::ConditionalSendFuture, // It's imported from `bevy::` directly
};
use serde::de::DeserializeOwned;
use thiserror::Error;

#[derive(Default, TypePath)]
pub struct RonAssetLoader<T> {
    _phantom: std::marker::PhantomData<T>,
}

#[derive(Debug, Error)]
pub enum RonLoaderError {
    #[error("Could not load asset: {0}")]
    Io(#[from] std::io::Error),
    #[error("Could not parse RON: {0}")]
    Ron(#[from] ron::error::SpannedError),
}

//
// THIS IS THE FIX:
// Changed 'RonLoaderError<T>' to 'RonAssetLoader<T>'
//
impl<T: DeserializeOwned + Asset + TypePath + Send + Sync + 'static> AssetLoader for RonAssetLoader<T> {
    type Asset = T;
    type Settings = ();
    type Error = RonLoaderError;

    fn load(
        &self,
        reader: &mut dyn Reader,
        _settings: &Self::Settings,
        _load_context: &mut LoadContext,
    ) -> impl ConditionalSendFuture<Output = Result<Self::Asset, Self::Error>> {
        // Return the async block directly, without Box::pin
        async move {
            let mut bytes = Vec::new();
            reader.read_to_end(&mut bytes).await?; // This uses AsyncReadExt

            let custom_asset = ron::de::from_bytes::<T>(&bytes)?;

            Ok(custom_asset)
        }
    }

    fn extensions(&self) -> &[&str] {
        &["ron"]
    }
}
