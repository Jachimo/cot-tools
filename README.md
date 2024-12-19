# CoT Tools

> Tools for working with Cursor on Target (CoT) messages

## Background

* **What is Cursor on Target?** - CoT is a simple, XML-based messaging
  format [originally designed at Mitre Corp. in 2005][mitre] to
  facilitate the exchange of tactical data between military
  information systems.  It provides a (reasonably) easy-to-parse way
  of sending "who/what/where" information over a network, and can be
  useful in many contexts outside its original military application.
* **Why do I care?** - I don't know, maybe you don't!  But if you're
  reading this, maybe you are working on a CoT-fluent application, or
  trying to create or consume CoT messages for some reason.  These
  tools were created for my own use while doing things like that.
* **Who owns the CoT spec?** - I'm honestly not sure.  There are
  several 'flavors' of CoT in use in the world, including the original
  XML-based version from the 2005 Mitre paper by Michael Butler (see
  above), and newer "CoT-derived" (arguably not actually CoT!) formats
  used by [CivTAK][], ATAK, WinTAK, and others.  Like [much of the
  modern Internet][ietf], CoT seems to be defined "de facto" by
  implementation rather than "de jure" by a rigid standardization
  process.

[mitre]: https://apps.dtic.mil/sti/citations/ADA637348
[CivTAK]: https://www.civtak.org/
[ietf]: https://www.ietf.org/runningcode/

## Tools

The 'tools' in this repo are pretty straightforward Python scripts,
and hopefully the code is mostly self-explanatory.

### CoT Message Generator

This script generates and sends out CoT messages according to the
original Mitre spec, which is raw XML inside a UDP datagram.
Specifically, it sends CoT "event" messages with a fixed lat/lon
location that you can specify in the code.

The destination address is also configurable, but defaults to
239.2.3.1 on port 6969, which is the default multicast address and
port used by ATAK and something of a de facto standard.

Note that as of 2024, ATAK doesn't seem to parse these messages
anymore, or at least I haven't been able to get it to do so.  It
appears that the ATAK developers have moved completely over to a newer
'flavor' of CoT which uses Protocol Buffers rather than XML,
presumably for message compactness. 

### CoT Message Receiver

This is the other end of the CoT channel, and starts a multicast
listener on 239.2.3.1:6969, displaying received messages in the
terminal.  It's useful for seeing whether a device is *really* sending
what you think it's sending (provided you know the address and port
it's sending to).

In addition to the basic Receiver, there's also a variant
(`cot-message-receiver-mysql.py`) which parses and stores received messages in a
MySQL database for later analysis.  It does some very basic duplicate
filtering based on type, event time, and callsign to avoid filling up
the DB with junk if the same message bounces around multiple times.
