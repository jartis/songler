# Songler
Song picker / request tracker / etc for Twitch

## Todo

* Request add Sources: Chat (bits), donations (Streamlabs integration), uhhh other things?
* "Winner" flash / confetti for last song on wheel?
* Configuration for wheel position/size
* Wheel Layout (pie chart wheel vs. slot machine spinner?)
* Eat a food! Get a snackies! (Add Hydrate / End Stream / Snacko / Bankrupt to the wheel?!?)
* Special effects for certain songs / wheel options? (show icon / play sound?)
* Choice of different "click" sounds for wheel spin
* Configuration for wheel palettes / random wheel colors
* Make titles on wheel inverse/contrast slice color
* No adjacent wheel slots with matching colors
* Error handling on click-to-play
* Some way to remove songs from a (non-moving) wheel - an X on the outside?
* Dashboard for configuring your song list
* Some kind of user/auth system
* Request security and whatnot
* Public display of a user's songlist
* Request from songlist page

## Done

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
1. What do we do to build the initial wheel? How parameterizable should that be? Is the wheel completely optional for the complete overlay? (ie., use the queue(s) without a wheel)

   