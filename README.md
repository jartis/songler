# Songler
Song picker / request tracker / etc for Twitch

## Keyboard shortcuts (Wheel)

`W` - Show/hide the song wheel
`R` - Show/hide the request queue
`C` - Show/hide the control panel

## Todo

* Request add Sources: Chat (bits), donations (Streamlabs integration), uhhh other things?
* "Winner" flash / confetti for last song on wheel?
* Wheel Layout (pie chart wheel vs. slot machine spinner?)
* Eat a food! Get a snackies! (Add Hydrate / End Stream / Snacko / Bankrupt to the wheel?!?)
* Special effects for certain songs / wheel options? (show icon / play sound?)
* Choice of different "click" sounds for wheel spin
* Configuration for wheel palettes / random wheel colors
* No adjacent wheel slots with matching colors
* Show selected title on hover (Different from spinner title)
* "Last Ignored"? Recently ignored songs should creep up less frequently?
* Toggle resquester name display
* Lock in "config mode" to ignore canvas clicks?
* End-of-session reports (for import to practice trackers?)
* Based on normalization, "fun reports" like most played artists?
* Error handling for adding song if the server catches fire
* Limits on requests for non logged in users
* Toggle "Allow anonymous requests"
* Add Fields to Personal profile
* Link Twitch account to existing account
* Link streamlabs account? Other accounts?
* Maybe document the db structure in a good formal way?
* "Object" out the, y'know, objects in the python backend
* Put a toaster on the wheel page!!!
* Set control values on config load
* Interstitial "Initialize" page for making a stream overlay?
* Fix displayname on songlist page (Use DB Canonicalization)
* Password changing / recovery
* Track separate usernames per system? (DisplayName independent?)
* Add most recent 'Last Played' to song info page
* Nightbot command integration
* DDG tabs / lyrics / lead sheet auto search (feeling ducky)
* CI/CD for pushing to LightSail
* Change last played date and play count from song management page
* Document the wheel features a little better...
* Update breadcrumbs / navbar when on appropriate page
* Clean up all string interpolation
* `Enter` to save song in song adding modal
* Auto clear fields on modal dismiss

## Done

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

## Questions

1. Due to the latency of streaming, is websocket-style speed of connection necessary? Would a 30s/1m poll be enough to handle things? Note that this would ABSOLUTELY require an event queue of some kind, but websocket communication "might not".
  * Right now, the wheel polls on a 5 second timer. I will probably increase that time, and go with a poll instead of something immediate like websockets - if I'm already streaming, even though it's a tiny connection... although WS is pub/sub so it would send heartbeats but only a payload if there WAS a payload. Merits further debate.
2. What do we do to build the initial wheel? How parameterizable should that be? Is the wheel completely optional for the complete overlay? (ie., use the queue(s) without a wheel)
  * I think making the wheel visibility toggle-able is a good call, so you can have the queue without the wheel, or turn it on-and-off on the fly. Queue visibility is kind of necessary, though, IMHO. Keyboard shortcuts for enable/disable wheel?
3. What's the structure for authorization and the assorted streamer/viewer pages? What auth mechanism do I want to use?
4. Does ytid belong on a SONG level, or a SONGLIST entry level? 
   * This is going to live at a SONGLIST level, you may want a different version/link than another user. 

## Notes

* I'm currently using UID 1 in my local DB for testing, and UID 2 for my actual tracking
