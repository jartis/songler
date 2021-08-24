# Songler
Song picker / request tracker / etc for Twitch

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
* Some kind of user/auth system
* Request security and whatnot
* "Last Ignored"? Recently ignored songs should creep up less frequently?
* Show requester names in song list? (Checkable option?)
* Save display configuration
* Move configurables into central object for jsonification / saving
* Lock in "config mode" to ignore canvas clicks?
* End-of-session reports (for import to practice trackers?)
* Based on normalization, "fun reports" like most played artists?
* Add requester info to requests from public page
* Don't refill wheel with played or ignored songs from this session
* Lock header rows when scrolling songlist
* Edit songs from list
* Paginate song dashboard / public lists?
* Error handling for adding song that is already on user's songlist
* Error handling for adding song if the server catches fire
* Serve this shiz up someplace public!
* Toggleable wheel visibility?
* Keyboard shortcuts?

## Done

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

## Notes

* I'm currently using UID 1 in my local DB for testing, and UID 2 for my actual tracking
