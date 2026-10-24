# RailMotion — Animated Railway Booking Desktop Application

A modern, dark-navy railway booking demo built entirely with **Python + Tkinter**.
The navigation menu **is a train**: six clickable carriages drawn with
`tkinter.Canvas` roll off the right edge of the window and re-enter as a compact
header while the destination page slides in from the left.
  python main.py

Everything ships in a single file: **`main.py`** (standard library only —
`tkinter`, `tkinter.ttk`, `tkinter.messagebox`, `datetime`, `math`, `random`,
`re`). No third-party packages are required.

---

## 1. Running the project (VS Code)

1. Install **Python 3.8+** from python.org (the Windows/macOS installers include
   Tk; on Linux also run `sudo apt install python3-tk`).
2. Open the project folder in VS Code and install the **Python extension**.
3. Select the interpreter: `Ctrl+Shift+P` → *Python: Select Interpreter* →
   choose your installed Python.
4. Open `main.py` and press **F5** (Run → Start Debugging), **or** run it in the
   integrated terminal:

   ```bash
   python main.py
   Optional automated self-test (runs navigation + validation checks, prints a report, exits non-zero on failure):

bash
Copy
python main.py --smoke
Default window size is 1150 × 760, minimum 1000 × 700.

2. Project structure
text
Copy
main.py      The complete application (single file, sectioned)
README.md    This document
main.py is organised into numbered sections so it stays easy to read:

Section	Contents
2. Theme & styling	Colour palette (#07111F, #45E6D0, #BBA4FF, #FFB866, …), font picker (Segoe UI when available), fnt(), mix(), rounded_rect()
3. Demo data	Cities, fictional trains, travel classes, email/date regexes, page names
4. Reusable widgets	RailButton (hover effects), Card (accent strip), ScrollableFrame, make_label(), make_entry()
5. Train drawing	TrainRenderer — background (sky gradient, stars, moon, skyline, sleepers, rails) and the whole train as Canvas items sharing the tag train
6. Pages	IntroPage, HomePage, LoginPage, SignupPage, TicketsPage, BookingsPage, OffersPage (all extend PageBase)
7. App + navigation	RailMotionApp(tk.Tk) — window shell, animation state machine, demo data services
8. Smoke test	run_smoke_test() used by --smoke
9. Entry point	main() + argparse
3. Implemented features
Animated train navigation (core feature)

Train drawn entirely with tkinter.Canvas: six carriages + engine at the front-right with pointed nose, windscreen, headlight (with beam while moving), windows, couplers, rotating wheel spokes, rails and sleepers, parallax skyline, star field, moon, night-sky gradient.
Every train component carries the Canvas tag train, so one canvas.move("train", dx, 0) per frame guarantees the engine and all carriages always move together from one shared train_x coordinate.
State machine with exactly three phases — idle, exit, enter — and a single root.after() callback (_ensure_anim refuses to schedule a second loop). Clicks during a transition are ignored, so animations can never overlap.
Transition sequence: destination page is built before the train starts → train accelerates off the right edge → the Canvas is resized to a compact 160 px navigation header (or back to the tall intro canvas) and the train is redrawn beyond the left edge → it eases to a consistent centred park position while the page slides in from the left → the selected carriage is highlighted → the page becomes interactive.
Per-carriage hover glow (purple) and selection glow (cyan), hand cursor over carriages, click hit-testing from stored hit boxes (works after every redraw), headlight beam only while moving, wheels spinning while rolling.
Window resizing is debounced and re-draws the train at the new size; a pending resize during an animation is applied when the train parks.
Pages

Intro — RAILMOTION title, YOUR JOURNEY STARTS HERE, SELECT A CARRIAGE TO BEGIN YOUR JOURNEY, six labelled chips, futuristic railway background.
Home — WELCOME ABOARD., subtitle, hero panel A NEW WAY TO EXPERIENCE RAIL TRAVEL with Choose a route. Start an adventure. and EXPLORE TICKETS, decorative route strip, QUICK ACCESS section with Tickets / Login / Sign Up cards (all buttons navigate).
Login — email + password, demo credentials printed on the card, validation (both fields required, email lower-cased, unknown account rejected, wrong password rejected), success dialog then navigation to Home.
Sign Up — full name, email, password, confirm; validation (all fields, email format, minimum 6 characters, passwords match, duplicate e-mail rejected), success dialog then navigation to Login.
Tickets — source/destination dropdowns (ttk.Combobox), YYYY-MM-DD date, passengers 1–6 (ttk.Spinbox), travel class dropdown, SEARCH TRAINS; rejects identical cities, malformed/past dates and out-of-range passenger counts via messagebox; results show name, route, departure time and base fare × passengers total with a SAVE DEMO BOOKING button each.
Bookings (My Journeys) — saved bookings with train, route, date, passengers, class, total fare and REMOVE (confirmed with askyesno, refreshed in place); empty state with a FIND A TRAIN button.
Offers — WELCOME10 / WEEKEND / TOGETHER cards with headings, code chips, descriptions and cyan/purple/orange accents, plus an illustrative-only note.
Demo data (memory only)

Fictional trains: Coastal Express, Southern Star, City Link, Deccan Runner, Western Connect across Chennai, Bengaluru, Coimbatore, Mysuru, Hyderabad, Mumbai, Pune.
One seeded demo account: demo@railmotion.in / rail123.
Accounts and bookings live in plain Python dicts/lists — nothing is written to disk and everything disappears on exit. Not secure authentication.
4. Testing the train navigation animation
Manual test (about a minute):

Start python main.py. The intro screen shows the complete train centred on a futuristic night background.
Move the mouse across the carriages — each one glows purple and the cursor becomes a hand.
Click TICKETS. Watch the whole train (all six carriages and engine) accelerate to the right and leave the screen, the Canvas shrink to the compact header, the train re-enter from the left and park centred with the TICKETS carriage glowing cyan, while the Tickets page slides in from the left.
Click HOME, then BOOKINGS, then LOGIN in quick succession — clicks while the train is moving are ignored; only the first is honoured and the animation always finishes with the train parked and the page live.
Click the RAIL MOTION logo in the top bar — the Canvas grows back to the tall intro layout and the train parks centred again.
Resize the window while on any page — the train re-scales and stays clickable.
Confirm the train never disappears, never sticks halfway, and no dialog opens instead of the destination page.
Automated checks used during development:

bash
Copy
python main.py --smoke      # 55 checks: navigation through every page,
                            # rapid-click guard, validation, bookings
5. Verification report
What was actually run (all passing):

python -m py_compile main.py — syntax valid, no duplicate/malformed definitions.
python main.py --smoke — 55/55 checks: intro state, six hit boxes, carriage hit-testing, navigation to all seven pages (including intro ↔ page mode switches), page visibility after every transition, carriage highlight, train position inside the window after every transition, rapid double-click guard, login/sign-up/search validation paths, fare maths (₹450 × 2 = ₹900), booking save/remove.
A GUI driver ran the real app on a virtual display and passed 44/44 checks: hover highlight, a real synthesized click on a carriage, mid-animation and settled screenshots of all seven pages, every navigation button (EXPLORE TICKETS, quick-access cards, SAVE DEMO BOOKING, REMOVE, FIND A TRAIN, brand logo, Login/Sign-Up cross-links), messagebox wiring for every validation path, in-place booking refresh, and window resizing (1150×760 → 1000×700 → back) with hit-testing re-verified afterwards.
13 screenshots were captured and visually inspected (intro, hover, train exiting, train arriving, and every page).
Two real defects were found by these tests and fixed:

The header grid row absorbed free window space, so the Canvas never became the compact navigation header — row weights corrected.
Non-ASCII glyphs/status text rendering fell back incorrectly in the test environment (font stack), which was corrected for testing by using an Xft-enabled Tk.
6. Limitations
Demo only — accounts and bookings are in memory; restarting the program loses them. Authentication is not secure and must not be used for real data.
All train schedules, fares and offers are fictional; no ticket can be bought and no discount can be redeemed.
Animations use root.after() frame stepping, so smoothness depends on the machine; on very slow hosts the transition simply takes longer (it never blocks the event loop).
The train is redrawn on window resize rather than scaled continuously, so a resize during an animation is applied once the train parks.
Tk draws on the host OS, so exact widget chrome (dropdown popups, spinbox arrows, message-box buttons) differs slightly between Windows, macOS and Linux; the palette, layout and behaviour do not.
Keyboard navigation reaches every widget by Tab, but carriage selection is mouse-driven (click/hover); there is no keyboard shortcut per carriage.
tools/ and shots/ in this workspace are the development test harness (headless display, screenshot driver, captured screenshots). They are not needed to run the application — only main.py is.
