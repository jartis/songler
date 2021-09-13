# Songler
Song picker / request tracker / etc for Twitch (et al?)

## Documentation

### Keyboard shortcuts (Wheel)

`W` - Show/hide the song wheel
`R` - Show/hide the request queue
`C` - Show/hide the control panel

### Nightbot Commands

*Note:* In order to use this command in NightBot on your channel, you must have your Twitch
account connected to your user account on Minstrelize.

API Endpoints and sample commands:

- `/api/v1/nbrand` - Place a random request on behalf of the user.
  - !random : `$(urlfetch https://minstrelize.com/api/v1/nbrand)`
- `/api/v1/nbreq` - Fuzzy search for artist/title and request closest (public) match.
  - !sr : `$(urlfetch https://minstrelize.com/api/v1/nbreq?s=$(querystring))`
- `/api/v1/nbws` - Withdraw calling user's last request for the current channel
  - !ws : `$(urlfetch https://minstrelize.com/api/v1/nbws)`

## Todo

### General

* Request add Sources: Chat (bits), donations (Streamlabs integration), uhhh other things?
* "Last Ignored"? Recently ignored songs should creep up less frequently?
* Update breadcrumbs / navbar when on appropriate page
* Add a 404 page
* Move user options into a new table (config?)
* Add config option for "rate limit requests"
* How to handle multiple requests for same slid (priority? Hotlist?)
* "Hotlist" overlay - Chime for aging requests?
* Fix local dates/times in DB for plays table
* Make Mobile Friendly

### Wheel Overlay

* "Winner" flash / confetti for last song on wheel?
* Wheel Layout (pie chart wheel vs. slot machine spinner?)
* Eat a food! Get a snackies! (Add Hydrate / End Stream / Snacko / Bankrupt to the wheel?!?)
* Special effects for certain songs / wheel options? (show icon / play sound?)
* Choice of different "click" sounds for wheel spin
* Configuration for wheel palettes / random wheel colors
* No adjacent wheel slots with matching colors
* Show selected title on hover (Different from spinner title)
* Put a toaster on the wheel page!!!
* Lock in "config mode" to ignore canvas clicks?
* Interstitial "Initialize" page for making a stream overlay?
* Toggle show/hide requester names on wheel from getShowNames
* Set control values on config load

### Stream Tracking / Management

* End-of-session reports (for import to practice trackers?)
* Based on normalization, "fun reports" like most played artists?
* Limits on requests for non logged in users
* DDG tabs / lyrics / lead sheet auto search (feeling ducky)

### Song List Management

* `Enter` to save song in song adding modal
* Add moderator abilities (user XX can mod my stream)

### User Management / Viewing

* Add Fields to Personal profile
* Link Other accounts? (YouTube / FB / PayPal / etc)
* Password Recovery
* Verify password on change from profile page?
* Users created with Streamlabs don't have an email: Add a nag?

### Refactoring / Tech Debt

* Maybe document the db structure in a good formal way?
* "Object" out the, y'know, objects in the python backend
* Document the wheel features a little better...
* Clean up all string interpolation
* Consistent styling / table generation across pages

### Nightbot Integration

* Fix fuzzy song matching (Increased pct threshold to 90 from 75...)
* Additional stats / commands
* !toast
* !crash

## Done

* ~~Add most recent 'Last Played' to song info page~~
* ~~Error handling for adding song if the server catches fire~~
* ~~Move all DB functionality out of Auth~~
* ~~Move all DB functionality out of Rendering (if any)~~
* ~~Move all DB functionality out of Nightbot~~
* ~~Change last played date and play count from song management page~~
* ~~Move all DB functionality into a separate file from API~~
* ~~Break "plays" out into a separate table, instead of "last played"~~
* ~~Document Nightbot API endpoint / command integration~~
* ~~'rr' / 'random' command for "add a random-eligible song"~~
* ~~'WS' endpoint to withdraw request / cancel last request~~
* ~~Fix play button in request list manager~~
* ~~Nightbot command integration~~
* ~~Link Streamlabs account?~~
* ~~Toggle "Allow anonymous requests"~~
* ~~CI/CD for pushing to LightSail~~ Push locally with a batch file
* ~~Toggle resquester name display~~
* ~~Auto clear fields on modal dismiss~~
* ~~Track separate usernames per system? (DisplayName independent?)~~
* ~~Link Twitch account to existing account~~
* ~~Password changing~~
* ~~Fix displayname on songlist page (Use DB Canonicalization)~~
* ~~Ignore "The" on string sorting~~
* ~~Auto-fix casing~~
* ~~Turn off browser autocomplete in song adding modal~~
* ~~Error handling for adding song that is already on user's songlist~~
* ~~Request queue page that is NOT the wheel overlay (with the youtube link, etc)~~
* ~~Center search box in navbar somehow? (It moves based on username length)~~ I just moved it.
* ~~Add toggle for "wheel-able" songs, separate from public~~
* ~~Limits on requests for logged in users~~
* ~~Request security and whatnot~~
* ~~Password strength on user registration page~~
* ~~Change dbconf (secrets) to pull from environment vars~~
* ~~Serve this shiz up someplace public!~~
* ~~Search options for finding all songs by an artist~~
* ~~Toggle for Live Request Polling (15s)~~
* ~~Display page for Artists (all songs by, etc)~~
* ~~Edit songs from list~~ - No editing songs on list. Delete/readd to keep "songs" up to date.
* ~~Save display configuration~~
* ~~Public profile pages? (Or links to pages in search)~~
* ~~Toggle in userinfo (?) to only show wheel option if you, y'know, have a wheel / songlist~~
* ~~Search options for finding a user's songlist~~
* ~~Search options for finding a song~~
* ~~Fix "Rob P - The Pretender" bug in request~~
* ~~LocalStorage / DB Storage of display prefs~~
* ~~Remove (delete) songs from songlist~~
* ~~Sort songlist displays by column headers~~
* ~~Add requester info to requests from public page~~
* ~~Lock header rows when scrolling songlist~~ Not necessary with pagination
* ~~Paginate song dashboard / public lists?~~
* ~~Show requester names in song list?~~
* ~~Navbar entry for songlist editing~~
* ~~New User Registration~~
* ~~Some kind of user/auth system~~
* ~~Keyboard shortcuts?~~
* ~~Don't refill wheel with played or ignored songs from this session~~
* ~~Toggleable queue visibility~~
* ~~Toggleable wheel visibility?~~
* ~~Move configurables into central object for jsonification / saving~~
* ~~Normalize "songs" to "artists" and "titles" separately?~~
* ~~Add new songs to list~~
* ~~Dashboard for configuring your song list~~
* ~~Public display of a user's songlist~~
* ~~Request from songlist page~~
* ~~API endpoint for public list for user~~
* ~~Normalize out "Songs" for multiple users~~
* ~~Highlight song slices on hover~~
* ~~Some way to remove songs from a (non-moving) wheel - an X on the outside?~~
* ~~Refill button for the wheel~~
* ~~Make titles on wheel inverse/contrast slice color~~
* ~~Configuration for request list position/size~~
* ~~Configuration for wheel position/size~~
* ~~Error handling on click-to-play~~
* ~~"Play" from queue vs. "Remove" from queue~~
* ~~Change play count for "Played", not for "Removed"~~
* ~~Update "Last Played" on "Play"~~
* ~~Reveal "Remove" X on hover over song?~~
* ~~Pull songs from external source~~
* ~~Chime on wheel stop?~~
* ~~Fixed number of audio clones to prevent too much overlap~~
* ~~Request Queue? Priority request tracking?~~
* ~~Clear out songs from the queue by clicking~~
* ~~Wheel Clicky Sounds~~
* ~~Wheel palettes?~~
* ~~Show currently highlighted song larger under wheel~~
