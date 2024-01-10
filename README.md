### plot-ntp

This program provides functionality for plotting Network Time Protocol (NTP) peer statistics (peerstats) over time. NTP is a protocol which synchronizes time across devices connected on a network. A device using the NTP protocol will connect to many peers, and will negotiate the correct time using NTP messages from them. This program plots the offsets received from each peer over time, and also provides additional information such as whether a peer's NTP packet was accepted, rejected, is a peer we are synchronized to, etc.
