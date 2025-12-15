<img style="vertical-align: middle;" src="data/icons/hicolor/scalable/apps/io.github.diegopvlk.Tomatillo.svg" width="112" height="112" align="left">

### Tomatillo

Focus better, work smarter.

<br>

<!-- <a href='https://flathub.org/apps/io.github.diegopvlk.Tomatillo'><img width='240' alt='Get it on Flathub' src='https://flathub.org/api/badge?svg&locale=en'/></a> -->

### Description

Tomatillo is a Pomodoro Timer app for your productivity tasks.<br>
Work for a set time, then take a short break. After several cycles, take a longer break.

### Features

- **Notifications** — Reminders with sound alert.
- **Custom timers** — Set individual durations for focus sessions, short breaks, and long breaks.
- **Custom session count** — Choose the amount of sessions before a longer break.
- **Autostart sessions** — Automatically begin the next focus or break interval.

### Screenshot

<p align="center"><img src="screenshots/focus.png"/></p>

<div>
  <details>
    <summary>Other Screenshots (Expand):</summary><br>
      <p align="center"><img src="screenshots/preferences.png"/></p>
      <p align="center"><img src="screenshots/break.png"/></p>
      <p align="center"><img src="screenshots/long-break.png"/></p>
      <p align="center"><img src="screenshots/focus-dark.png"/></p>
  </details>
</div>

### Donate

If you want to help with a donation (thank you!), you can use:

- [PayPal](https://www.paypal.com/donate?hosted_button_id=DVL7H35GA66X6)
- [Ko-fi](https://ko-fi.com/diegopvlk)
- Pix: diego.pvlk@gmail.com

### Code of Conduct

This project follows the [GNOME Code of Conduct](https://conduct.gnome.org).

### Build from source

Clone the repo in GNOME Builder and press run.<br>
Or install manually with meson:

```
git clone https://github.com/diegopvlk/Tomatillo.git
cd Tomatillo
mkdir build
cd build
meson setup .. --prefix=$HOME/.local
ninja
ninja install
tomatillo
```
