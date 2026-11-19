package io.github.tyjk.curieosity;

import android.media.AudioManager;
import android.os.Bundle;
import android.view.KeyEvent;
import android.view.View;

import com.google.androidgamesdk.GameActivity;

/** The game's one screen: GameActivity runs the native library (android/src/lib.rs). */
public class MainActivity extends GameActivity {
    static {
        System.loadLibrary("curieosity");
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        // the volume buttons set the game's sound (media) volume, as in any game, not the
        // ringer's, which is what a phone adjusts when nothing is playing at that moment
        setVolumeControlStream(AudioManager.STREAM_MUSIC);
    }

    /**
     * The volume buttons go straight to the system, before GameActivity's input view can take
     * them: returning false here lets the window adjust the volume and show its slider.
     */
    @Override
    public boolean dispatchKeyEvent(KeyEvent event) {
        switch (event.getKeyCode()) {
            case KeyEvent.KEYCODE_VOLUME_UP:
            case KeyEvent.KEYCODE_VOLUME_DOWN:
            case KeyEvent.KEYCODE_VOLUME_MUTE:
                return false;
            default:
                return super.dispatchKeyEvent(event);
        }
    }

    @Override
    public void onWindowFocusChanged(boolean hasFocus) {
        super.onWindowFocusChanged(hasFocus);
        if (hasFocus) {
            hideSystemUi();
        }
    }

    /** The whole screen for the game; a swipe from the edge brings the system bars back for a moment. */
    private void hideSystemUi() {
        View decorView = getWindow().getDecorView();
        decorView.setSystemUiVisibility(
                View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY
                        | View.SYSTEM_UI_FLAG_LAYOUT_STABLE
                        | View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION
                        | View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN
                        | View.SYSTEM_UI_FLAG_HIDE_NAVIGATION
                        | View.SYSTEM_UI_FLAG_FULLSCREEN);
    }
}
