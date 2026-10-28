# BeamNG.drive 1% lows: AvenorOS vs Windows 11

Both runs are read by the same script, `bench/beamng-lows`, so both numbers mean the same thing. The 1% low is the average FPS of the slowest 1% of frames. The 0.1% low does the same for the slowest 0.1%.

## Keep these the same on both

- G14 plugged in, the same GPU mode (Optimus on both, or Ultimate on both), the same fan profile, and the laptop left to cool for 5 minutes before each run.
- The same BeamNG.drive version, renderer settings, resolution and refresh rate, with V-Sync and any frame cap off.
- The same test: one saved replay (`.rpl`), copied to both installs and played from the start. Record 120 seconds.
- Three runs on each OS. Use the median.

## AvenorOS

1. In Steam, turn on Steam Play for all titles, then set BeamNG.drive to the same Proton version every time.
2. Set these launch options:

       MANGOHUD_CONFIG=no_display,output_folder=$HOME/bench,log_duration=120,autostart_log=15 gamemoderun mangohud %command%

3. Start the game and the replay. Logging starts 15 seconds after launch, so start the replay before that.
4. Run `bench/beamng-lows ~/bench/<file>.csv`.

## Windows 11

1. Install CapFrameX. It uses PresentMon.
2. In CapFrameX, set the capture time to 120 seconds and pick a hotkey.
3. Start the game and the replay, then press the hotkey.
4. Export the capture as CSV, copy it over, and run `bench/beamng-lows windows.csv`.

To compare one Windows run with one AvenorOS run, run `bench/beamng-lows windows.csv avenor.csv`.
