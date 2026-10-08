# ByteBlower

Excentis traffic generator/analyzer. Distilled from ~370 pages crawled 2026-10-08
(knowledge base, Test Framework and Tcl API nearly fully; Python reference partly; setup site not at all).

## Links

### docs
>**[knowledge base](https://support.excentis.com/knowledge/article/39)**    
>**[test framework](https://api.byteblower.com/test-framework/latest/)**    
>**[python api (byteblowerll)](https://api.byteblower.com/python)**    
>**[python examples](https://github.com/excentis/ByteBlower_python_examples)**    
>**[tcl api](https://api.byteblower.com/tcl)**    
>**[tcl v2 migration](https://api.byteblower.com/tcl/TclApiv2Migrate.html)**    
>**[openmetrics / prometheus](https://api.byteblower.com/prometheus)**    
>**[cli-config-schema.json](https://api.byteblower.com/test-framework/json/cli-config-schema.json)**    
>**[setup.byteblower.com](https://setup.byteblower.com/)** (blocks crawlers; per-model manuals + downloads)    

### test cases
>**[rfc 2544 throughput](https://api.byteblower.com/test-framework/latest/test-cases/rfc-2544/overview.html)**    
>**[tr-398 airtime fairness](https://api.byteblower.com/test-framework/latest/test-cases/tr-398/overview.html)**    
>**[docsis 4.0 atp ll-04.40](https://api.byteblower.com/test-framework/latest/test-cases/docsis-atp/overview.html)**    
>**[low latency / l4s](https://api.byteblower.com/test-framework/latest/test-cases/low-latency/overview.html)**    


<br/>


### Concepts
>**[basic test units](https://support.excentis.com/knowledge/article/88)**    
>**[server components](https://support.excentis.com/knowledge/article/240)**    
>**[link speed / bitrate conventions](https://support.excentis.com/knowledge/article/197)**    
>**[nat discovery](https://support.excentis.com/knowledge/article/109)**    
>**[tcp direction GET/PUT](https://support.excentis.com/knowledge/article/202)**    
>**[tcp congestion / loss recovery](https://support.excentis.com/knowledge/article/194)**    
>**[tcp timing T1-T3](https://support.excentis.com/knowledge/article/204)**    
>**[tcp diagnosis from graphs](https://support.excentis.com/knowledge/article/192)**    
>**[latency cdf / ccdf](https://support.excentis.com/knowledge/article/190)**    
>**[unique frame modifier](https://support.excentis.com/knowledge/article/233)**    
>**[find lost frames (out-of-sequence)](https://support.excentis.com/knowledge/article/170)**    
>**[bpf filter cheatsheet](https://support.excentis.com/knowledge/article/186)**    
>**[l4s](https://support.excentis.com/knowledge/article/322)**    


<br/>


### Setup & ops
>**[static management ip](https://support.excentis.com/knowledge/article/72)**    
>**[time config ntp/ptp](https://support.excentis.com/knowledge/article/245)**    
>**[ptp master on a nuc](https://support.excentis.com/knowledge/article/417)**    
>**[clock sync across machines](https://support.excentis.com/knowledge/article/166)**    
>**[remote access / firewall ports](https://support.excentis.com/knowledge/article/239)**    
>**[quick self-test](https://support.excentis.com/knowledge/article/90)**    
>**[x710 nic firmware](https://support.excentis.com/knowledge/article/160)**    
>**[hardware compatibility](https://support.excentis.com/knowledge/article/175)**    

#### endpoint
>**[endpoint to meeting point topologies](https://support.excentis.com/knowledge/article/108)**    
>**[endpoint autostart](https://support.excentis.com/knowledge/article/183)**    
>**[endpoint limits](https://support.excentis.com/knowledge/article/256)**    
>**[golden client](https://support.excentis.com/knowledge/article/278)**    


<br/>


<br/>


## Study notes

### The idea in one minute

ByteBlower sends traffic it fully controls into a device or network from one side and measures what comes out the other, so any difference is caused by the thing in between. That thing is the device under test: a modem, home gateway, Wi-Fi access point, switch or a whole access network.

Every test answers one of five questions:

| Question | Measured as |
| --- | --- |
| How much can it carry? | Throughput: the highest rate with acceptable loss |
| Does it drop traffic? | Frame loss: sent minus received |
| How long do packets take, and how steady is that? | Latency, jitter and their distribution |
| Does it deliver packets in order? | Out-of-sequence count |
| How would a real application feel? | TCP goodput and round-trip time, voice quality score, video buffering, gaming latency |

The traffic runs between **ports**, which are virtual hosts on the ByteBlower server, or **Endpoints**, which are an app on a real phone or laptop. A typical setup puts one port on the network side and one port or Endpoint on the customer side, then sends downstream, upstream or both.

### Two kinds of test traffic

Every test is built from one of two traffic types, and which one you pick decides what the result means.

|  | Frame Blasting (stateless) | TCP flow (stateful) |
| --- | --- | --- |
| What is sent | UDP frames you define, at a fixed rate you choose | A real TCP session carrying HTTP between a client and a server port |
| Who sets the rate | You. The sender never slows down | TCP. It backs off on loss and fills the available bandwidth |
| What it gives | Exact loss, latency, jitter and reordering at a known load | Goodput, throughput, round-trip time, retransmissions |
| Repeatable? | Yes, the same every run | Roughly; results vary run to run like a real network |
| Use it to | Benchmark: find limits, compare devices, verify a spec | Estimate user experience: what speed does a download get? |
| Pass or fail | Yes, against loss and latency thresholds | No. Measured and reported only |

Two consequences worth remembering:

- Frame blasting can overload a device on purpose. TCP cannot, because it adapts.
- Frame size matters for frame blasting. Small frames stress packet processing; large frames stress the link. This is why throughput tests repeat for several sizes.

A TCP flow's direction comes from the HTTP method. With GET the client downloads; with PUT the client uploads. Behind NAT the inside device must start the connection, so upload tests from a device behind NAT use PUT.

### The measurements

Each measurement is taken by a specific mechanism, and knowing the mechanism tells you when to trust it.

| Measurement | What it checks | How it is taken | Default pass rule in the Test Framework |
| --- | --- | --- | --- |
| Frame loss | Does the device drop traffic at this load? | The receiver counts frames matching a filter unique to the flow; loss is sent minus received | Loss at most 1% |
| Throughput | The highest rate the device forwards | Repeated frame-blasting trials at different rates until loss appears | Depends on the test |
| Latency | One-way delay through the device | The sender writes a timestamp into the last 8 bytes of each frame; the receiver subtracts it from its own clock | Latency at the 99.9th percentile under 5 ms |
| Jitter | How much the delay varies | Derived from the same timestamps | Reported, not judged |
| Latency distribution | The tail: how bad are the worst packets? | A histogram of per-packet latency, drawn as CDF and CCDF up to P99.99 | Same percentile rule |
| Out-of-sequence | Does the device reorder packets? | A running frame number in the payload | Reported, not judged |
| TCP goodput | Rate the application actually receives | Bytes delivered over the transfer time, measured at the receiving side | None |
| TCP throughput | Rate on the wire including headers and retransmissions | TCP stack counters | None |
| Round-trip time | Delay as TCP sees it | Time for a segment to be acknowledged; minimum, average, maximum | None |
| Retransmissions, window | Is loss or a small window holding TCP back? | TCP stack counters over time | None |
| Voice quality | Would a call sound good? | A MOS score computed from loss and delay on a simulated G.711 call | MOS at least 4 |
| Video buffer | Would a stream start quickly and keep playing? | A simulated player buffer filled by segment downloads | Initial wait limit of 5 s; the exact rule is not spelled out |
| Congestion marks | Does the network signal congestion the L4S way? | Count of CE-marked packets on a TCP Prague flow | None |
| Wi-Fi link | Signal and association during the test | RSSI, SSID, BSSID, channel and Tx rate read on the Endpoint | Reported, not judged |

Reading the two that people misread most:

- **Goodput versus throughput.** They should be nearly equal. A large gap means many retransmissions, so the path is losing packets.
- **Latency percentiles.** An average hides the tail. Where a flow's line crosses P99 on the CCDF graph, 99% of packets were faster than that value. Low-latency work is judged on the tail.

### The tests

The docs describe about a dozen ready-made tests, from a two-cable sanity check to full certification procedures.

| Test | What it does | What it checks | Pass means |
| --- | --- | --- | --- |
| Quick self-test | One UDP flow between two server ports cabled back to back | That the ByteBlower itself works | 100% of frames received |
| Loss at a fixed load | One frame-blasting flow at a rate you set | Whether the device drops traffic at that load | Loss under your threshold, default 1% |
| Latency under load | The same flow with timestamps on | Delay, jitter and the latency tail at that load | Loss under threshold and P99.9 latency under 5 ms |
| Throughput sweep (GUI wizard) | Many flows of the same frame at stepped rates in one run | Where loss starts as load rises | You read the limit off the report |
| RFC 2544 throughput | An automatic search for the highest lossless rate, per frame size | Forwarding capacity across small to large frames | Every size reaches its expected rate |
| TCP speed test | An HTTP download or upload for a set time or size | Achievable speed and stability for real transfers | Not judged |
| Voice call | Simulated G.711 RTP stream | Call quality | MOS at least 4 |
| Gaming | Small UDP packets of varying size at a steady rate, as in traditional online gaming | Latency of interactive traffic | Latency under 5 ms |
| Video streaming | Segment downloads filling a player buffer | Start-up delay and stalls | Playback starts within the wait limit |
| Video conference | Combined video, voice and screen-share flows | Each stream's loss, latency or MOS | Each stream meets its own rule |
| L4S | TCP Prague flows, or UDP with L4S markings | Whether low-latency traffic stays fast while classic traffic congests the link | Not judged for TCP; thresholds for UDP |
| TR-398 Airtime Fairness | TCP then UDP to pairs of Wi-Fi stations | Whether an access point shares airtime fairly | Each station keeps over 45% of its solo speed |
| DOCSIS 4.0 ATP LL-04.40 | Classic flows with and without low-latency traffic through a cable modem | Queue management (PIE AQM) behaviour | Loss and latency per interval meet the ATP |
| Home gateway LAN and WAN | Throughput and latency per frame size, LAN to LAN and WAN to LAN, each direction | Routing and NAT performance of a home gateway | You compare against your target |
| Wi-Fi roaming | Low-rate UDP to Endpoints while logging signal and access point | When a device switches access point and what it costs | You read it off the graphs |

The voice, gaming, video, conference and L4S flows belong to the Low Latency test case, which runs any mix of them at once. That mix is the point: you see what one kind of traffic does to another.

Beyond tests, a port can act as a real host for single protocols: get an address by DHCP, join multicast groups with IGMP or MLD, open a PPPoE session, answer or send ping. The docs describe these as building blocks in the API, with no ready-made test or pass rule.

### The standard procedures, step by step

Four tests follow a published procedure; this is what each one actually does.

#### RFC 2544 throughput

It finds, for each frame size, the highest rate the device forwards without exceeding a tolerated loss ([docs](https://api.byteblower.com/test-framework/latest/test-cases/rfc-2544/overview.html)).

1. Start at an initial bitrate and run one trial, 60 seconds in the example.
2. If loss is above the tolerance, halve the rate until a trial passes. If not, raise it until a trial fails.
3. Narrow in: after a pass, go up by half the gap between the last two rates; after a fail, go down by half.
4. Stop when the step is smaller than the wanted accuracy and the last trial passed, or at the iteration limit.
5. Repeat for each frame size. The defaults are 60, 124, 252, 508, 1020, 1276 and 1514 bytes, which are RFC 2544's 64 to 1518 without the 4-byte checksum.

The result per size is the last rate that passed. The test fails if any size ends below its `expected_bitrate`, or if an error stops the run. Read the result as a curve: a device that is fine at 1514 bytes but weak at 60 is limited by packets per second, not by bits per second.

#### TR-398 Airtime Fairness

It checks that a Wi-Fi access point does not let a slow or distant station starve a good one ([docs](https://api.byteblower.com/test-framework/latest/test-cases/tr-398/overview.html)).

1. Three stations run the Endpoint app. Station 1 is always in the best position; the partner varies.
2. Three setups: station 2 close, station 2 at medium distance, and station 3 (legacy mode) close.
3. In each setup, run a TCP download to each station alone. That is its maximum.
4. Then run two UDP downloads at once for 120 seconds: station 1 at 75% of its maximum, the partner at 50%. Together they overload the access point.
5. Repeat for four access point modes: 802.11n at 2.4 GHz, 802.11ac at 5 GHz, 802.11ax at 2.4 and 5 GHz. You move stations and reconfigure by hand between runs.

It passes when each station still receives more than 45% of its own TCP maximum, and the two together exceed the total TR-398 expects for that mode.

#### DOCSIS 4.0 ATP LL-04.40, part 1

It checks how a cable modem's queue management (PIE AQM) reacts to overload, alone and next to low-latency traffic ([docs](https://api.byteblower.com/test-framework/latest/test-cases/docsis-atp/overview.html)).

1. Procedure 1: classic flow 1 for 20 seconds, then classic flow 2 for 20 seconds. Both exceed the modem's configured rate, so loss is guaranteed.
2. Procedure 2: the same, with a low-latency flow running for the full 40 seconds.
3. Loss and latency are computed per 200 ms interval and compared with the ATP's requirements.

The operator prepares the CMTS and modem before each procedure. The docs do not publish the numeric thresholds.

#### Low latency and L4S

It answers a comparative question: when the link congests, which traffic keeps its latency? You run background load and delay-sensitive flows together and compare ([docs](https://api.byteblower.com/test-framework/latest/test-cases/low-latency/overview.html)).

Two published example runs show what the output teaches:

- Basic: a UDP flow starting at 10 seconds cut a running HTTP download by about 4%. Adding gaming and voice cut it by about 60%, mostly due to gaming.
- L4S: while a UDP flow loaded the link, a classic TCP download averaged about 25% under its configured rate with round-trip spikes and retransmissions. The L4S download beside it stayed near its rate with almost no retransmissions.

The overall verdict is FAIL if any single flow misses its loss, latency or MOS threshold.

### What you walk away with

A run produces a verdict, summary numbers and over-time graphs, in forms for people and for machines.

| Output | Contains | Good for |
| --- | --- | --- |
| HTML or PDF report | Overall PASS or FAIL, port setup, per-flow results, graphs over time, latency CDF and CCDF | Reading and sharing a result |
| JSON report | The same numbers, structured | Scripts, dashboards, trend tracking |
| JUnit XML | One test result per flow with failure reasons | CI systems such as Jenkins or GitLab |
| CSV, Excel | Tabular results from the GUI or command-line runner | Spreadsheets |
| Packet capture (pcap) | Raw received frames, filtered | Debugging in Wireshark |
| Live metrics | Bytes, latency and reordering per flow each second, scraped by Prometheus | Real-time Grafana graphs, very long or very large runs |

What the numbers let you conclude:

- **A capacity figure**: this device forwards X Mbit/s at this frame size with under Y loss.
- **A latency profile**: typical delay, jitter and the worst 1% or 0.1% at a given load.
- **A user-experience estimate**: download speed, call quality score, whether video stalls.
- **A fairness or isolation finding**: what one flow costs another when they share the link.
- **A diagnosis**: TCP graphs separate packet loss from buffer bloat from a badly sized window.

Three ways to drive it: the GUI by hand, a JSON file with the Test Framework for repeatable automated runs, or the Python and Tcl APIs for full control and raw counters. The Reference tab covers each.

### What makes a result untrustworthy

A number is only as good as the mechanism behind it; these are the documented ways each one goes wrong.

| If you see | Suspect | Because |
| --- | --- | --- |
| Negative latency | Clocks | Latency compares the sender's and receiver's clocks. On two machines they must be continuously synchronised with PTP or NTP |
| Latency spikes of several seconds | Corrupted packets | The timestamp travels in the payload; a damaged one gives a wild value |
| More frames received than sent | Colliding flows | Two flows with near-identical frames get counted by each other's filter |
| 100% loss toward a device behind a gateway | NAT | Downstream traffic needs a NAT mapping, which must be opened from inside first |
| Low but stable TCP speed, no retransmissions | Window scale too small | The test setup, not the device, is the limit |
| Good TCP speed with huge round-trip time | Window scale too large | The sender is queueing in its own buffers |
| Different bitrate than expected | Counting convention | Rates can count the frame only, frame plus checksum, or everything on the wire (24 more bytes per frame). A 1 Gbit/s link carries only 714 Mbit/s of 60-byte frames |
| A missing latency tail on a 100 Gbit/s system | Sampling | The 5100 may sample received packets for latency |

Limits when the receiving or sending side is an Endpoint on a real device:

- Latency is best-effort. The device clock is set once at registration and can drift, especially on long tests.
- No reordering detection.
- As a receiver it gives average latency only, with no distribution.
- iPhones and iPads never report signal strength.

Every system also has a latency noise floor below which it cannot measure. Excentis publishes it per model, but only as a chart.

### Check yourself

Ten questions covering the notes above; answers follow.

1. Why can frame blasting overload a device while a TCP flow cannot?
2. How does ByteBlower know which received frames belong to which flow?
3. Where does the latency timestamp live, and what does that imply for two machines?
4. Goodput is well below throughput. What is happening?
5. Why does RFC 2544 repeat the search for several frame sizes?
6. In TR-398, what are the two UDP rates and what is the pass line?
7. Which flows never fail a Test Framework run?
8. What MOS does a voice flow need, and what latency rule applies to a UDP flow by default?
9. You measure more frames received than sent. What went wrong?
10. Name three things an Endpoint cannot measure that a server port can.

**Answers**

1. Frame blasting sends at a fixed rate regardless of loss. TCP reduces its rate when it sees loss.
2. A receive-side filter (a trigger) unique to each flow counts matching frames.
3. In the last 8 bytes of the frame payload. Sender and receiver clocks must be synchronised, or latency is wrong and can go negative.
4. Many retransmissions, so the path is dropping packets.
5. Small frames stress per-packet processing and large frames stress link capacity, so the limit differs by size.
6. Station 1 at 75% and its partner at 50% of their own TCP maximum; each must keep more than 45% of that maximum, and the sum must exceed the expected total.
7. HTTP (TCP) flows. They are measured and reported only.
8. MOS of at least 4. Loss at most 1%, and when latency analysis is on, P99.9 latency under 5 ms.
9. Two flows have frames too similar to tell apart, so their filters count each other's frames.
10. Reordering, a latency distribution when receiving, and precise latency in general; on iOS also signal strength.


<br/>


## Algorithms

Every algorithm, formula and decision rule the ByteBlower docs describe, written out. Where the docs name something without explaining it, that is said at the end.

### Rate arithmetic

A frame-blasting stream is defined by three numbers: the frame, the gap between frame starts in nanoseconds, and how many frames to send. Everything else is derived.

On the wire each frame costs 24 bytes more than the frame you define: preamble 7, start delimiter 1, checksum 4, inter-frame pause 12. With frame size S in bytes (no checksum) and a target load R in bits per second:

```latex
\text{frames per second} = \frac{R}{8\,(S + 24)} \qquad \text{gap}_{ns} = \left\lceil \frac{10^{9}}{\text{frames per second}} \right\rceil
```

The gap is rounded up because the API takes whole nanoseconds. Test duration is gap times number of frames.

Worked example at line rate, 1 Gbit/s with 60-byte frames: 84 bytes per frame on the wire gives 1,488,095 frames per second, which is only 714 Mbit/s if you count the frames alone (60/84 = 71.4%).

| Bitrate convention | Bytes counted per frame |
| --- | --- |
| Frame only | S |
| Frame and checksum | S + 4 |
| Physical | S + 24 |

The GUI lets you choose the convention; the Test Framework names them `frame`, `frame_with_fcs` and `physical`, and its `bitrate` setting excludes VLAN tag bytes. Comparing two results that use different conventions is the most common arithmetic mistake.

Other derived rules:

- A flow aimed at a **port group** has its rate divided evenly over the members: 3 Gbit/s to a group of four sends 750 Mbit/s to each.
- The port's MTU caps the layer-3 packet. Frames larger than it cannot be sent; TCP sizes its segments from it. It does not limit received frames.
- A VLAN tag adds 4 bytes per tag to every frame, added on send and required on receive.

### Counting and loss

The server has no concept of a flow. A flow is a transmit counter on one port paired with a receive filter on another, and loss is the difference.

1. The sending stream counts every frame it transmits.
2. On the destination port a **trigger** counts every received frame matching a BPF filter. The GUI and Test Framework generate a filter unique to the flow, typically source and destination address, UDP ports and frame length.
3. Triggers count from the moment they exist, so counters are cleared just before traffic starts.
4. After the stream ends, wait about a second so frames still in flight are counted.
5. Loss follows RFC 1242:

```latex
\text{loss}\,\% = 100 \times \frac{\text{sent} - \text{received}}{\text{sent}}
```

With several flows, the aggregate loss sums sent and received over all flows that have a receiver. Flows with no receiver are background load and are left out.

**Collision detection.** Before a run, the GUI checks that every flow's filter is unique. If two flows have identical or near-identical frames, no unique filter exists, frames are counted twice, and loss goes negative. It warns at start and notes it in the report. Fixes: a per-frame unique modifier on layer 4, a different length, one changed payload byte, or different UDP ports.

**Scouting.** Before the measured traffic, a single scouting frame per stream can be sent so switches and gateways learn addresses (ARP and forwarding entries). The docs give the purpose as initialising network entries such as ARP and verifying the connection. It is not used for traffic sent from an Endpoint.

**Locating loss in time.** The docs give a bisection procedure:

1. Read the over-time graph and zoom in on the dip.
2. Shorten the test. If loss % falls, there are several loss events; if it stays the same, loss is continuous; if it rises, the main event is at the start.
3. Split one long flow into many short back-to-back flows, for example 10 seconds into 20 flows of 500 ms, and read which window lost frames.
4. To identify the exact frames, enable sequence numbers, capture, and read the numbers.

### Latency, jitter and reordering

Both measurements work by writing a tag into the frame payload at send time and reading it at the receiver.

#### Latency

1. Just before a frame leaves, the sender overwrites 8 bytes at the end of the payload with its local time.
2. The receiving port reads the tag and subtracts it from its own local time. That difference is one-way latency.
3. Per sampling interval and cumulatively it keeps minimum, average, maximum, jitter, and counts of valid and invalid packets.

The tag has three formats: microseconds, microseconds with a check code, and ten-nanosecond units. The receiver runs a sanity check on each tag when the format allows it. A frame that matches the filter but fails the check is still counted as received but gives no latency value, so the received count can exceed the count used for latency.

How corruption shows up:

| What happened to the frame | Result |
| --- | --- |
| Ethernet checksum fails | Dropped by the network; counts as loss |
| Checksum valid, timestamp off by more than one minute | Counted as invalid; no latency value |
| Checksum valid, timestamp off by less than one minute | A latency spike of up to seconds |

The tag changes the payload, so it interacts with the UDP checksum. Server models with hardware timestamping could not always recompute it, which produced bad checksums and up to 100% loss on IPv6 (where a zero checksum is not allowed). Current versions default to software timestamping, which corrects the checksum. Because the tag overwrites the end of the frame, two flows must differ somewhere other than their last 8 bytes.

Because the result is a difference of two clocks, both ports on one server share a clock and are exact. Across machines the clocks must be disciplined continuously, or the offset drifts into the result and can make it negative.

#### Latency distribution and percentiles

The distribution receiver sorts each packet's latency into equal-width buckets over a range, default 0 to 1 second, with one extra bucket below the range and one above. Setting the range clears the counters.

The report turns the buckets into a cumulative curve. For a latency x, CDF(x) is the fraction of packets at or below x and CCDF(x) = 1 − CDF(x). Percentile P99 is the x where the CDF reaches 0.99. Both axes are logarithmic and the plot ends at P99.99.

The quality of that curve depends on the buckets, which is what the report warnings test:

| Condition | Meaning |
| --- | --- |
| Fewer than 50 occupied data points | Range too wide for the data; all packets sit in a few buckets |
| Packets below or above the range | The tail is cut off; percentiles there are unknown |
| Fewer than 10,000 received packets | Too few samples for a stable P99.99 |
| Sampled packets | A 100 Gbit/s system measured only a sample; rare outliers may be missing |

The Test Framework's CDF analyser sets its range to 0 up to 50 times the latency threshold, then tests the latency at the configured quantile (default 99.9) against the threshold (default 5 ms).

#### Reordering

1. The sender writes an incrementing sequence number into an 8-byte field at the end of the payload: the first 2 bytes are used for checksum correction, the last 6 are the frame number.
2. The receiver tracks the numbers and counts packets that arrive out of sequence, plus valid and invalid tags and the biggest gap seen.
3. When a frame carries both tags, the sequence field moves ahead of the timestamp; position 16 from the end is the recommended placement.

It reports reordering, not which frames went missing. To find those, capture and read the 6-byte numbers.

The docs note that random-size frames can cause high out-of-sequence counts, without giving the reason.

### Throughput search

Throughput is not measured directly; it is searched for by running loss trials at different rates.

#### RFC 2544 search (Test Framework)

Per frame size, with a tolerated loss, a wanted accuracy and an iteration limit ([docs](https://api.byteblower.com/test-framework/latest/test-cases/rfc-2544/overview.html)):

```text
rate = initial_bitrate                      # e.g. the link's theoretical maximum
run a trial at rate, measure loss

# Phase 1: find a failing and a passing rate
if loss > tolerated:
    repeat: rate = rate / 2                 until a trial passes
else:
    repeat: rate = rate * 2  (or * 1.5)     until a trial fails

# Phase 2: bisect
repeat:
    step = 50% of |difference between the last two rates|
    if last trial passed:  rate = rate + step
    else:                  rate = rate - step
    run a trial
until (step is within accuracy AND last trial passed) OR iterations == max_iterations

result = last rate the device handled within tolerated loss
```

A trial passes when its frame loss is at or below `tolerated_frame_loss`. Each step halves the uncertainty, so reaching accuracy a from a starting gap g takes about log2(g/a) trials.

Frame sizes come from RFC 2544: 64, 128, 256, 512, 1024, 1280 and 1518 bytes with checksum, configured as 60 to 1514 without it. The RFC asks for at least five sizes and trials of at least 60 seconds.

Around the search:

- Before running, inputs are validated: missing parameters, address and gateway in different subnets, server reachable, interface exists.
- Runtime errors (duplicate frames, all frames lost, a layer-3 mismatch) trigger automatic reruns. Recovered errors only raise an error count; exceeding the allowed reruns fails the test.
- Verdict: FAIL if any frame size's result is below its `expected_bitrate`, or an error stopped the run.

#### Manual sweep (GUI)

The throughput wizard is a linear scan, not a search: it creates one flow per load from a start speed to a final speed in fixed increments, all in one scenario, and you read where loss begins.

The documented way to use it is two passes: a coarse batch with widely spaced rates (for example 100 Mbit/s to 1 Gbit/s in 100 Mbit/s steps), then a fine batch around the limit found (for example 10 Mbit/s steps). Latency is then measured at the highest lossless rate.

The GUI also has an RFC 2544 wizard taking frame sizes, the duration of one iteration and the acceptable loss; total run time depends only on the first two.

### NAT discovery

A NAT device rewrites the source address and usually the source port, so the receiver cannot filter on the addresses the sender used. ByteBlower learns the translation before the test ([article](https://support.excentis.com/knowledge/article/109)).

#### Upstream: the sender is behind NAT

1. Build a discovery frame from the real test frame: same MAC addresses, VLAN tags, IP addresses, layer-4 protocol and ports. Replace the payload with a short text plus a unique token. The frame is about 100 bytes.
2. Send it from the port behind NAT at about 10 frames per second (about 8 kbit/s) for at most 20 seconds.
3. On the public side, capture with a filter on the destination address and port, and compare each payload with the token.
4. The source address and source port of the matching frame are the public mapping. The receive filter for the real flow is built from them.

#### Downstream: the receiver is behind NAT

1. Run the upstream discovery from the destination port. This opens a mapping in the NAT device.
2. Rewrite the test frame's destination IP address and UDP port to the public mapping learned.
3. Send. The NAT device forwards the traffic through the mapping.

Results are reused by flows with the same frames and ports. Most NAT devices keep a mapping at least 2 minutes; if a flow starts late, the mapping can expire and a new, different one gives 100% loss. The keep-alive option sends traffic from the inside port to hold the mapping open. Since 2.11.4 the GUI keeps mappings alive until the test starts.

The Tcl helper does the same with 256-byte packets and returns the public IP and port. For IPv6 there is no translation, but a firewall still blocks inbound traffic; the same inside-out discovery opens it.

#### Direction rule for TCP

A connection can only be opened from inside the NAT. So the HTTP method is chosen from where the data source sits:

| Data source | Method | Who opens the connection |
| --- | --- | --- |
| Not behind NAT | GET | The destination (client) connects to the source and downloads |
| Behind NAT | PUT | The source (client) connects out and uploads |

AUTO applies exactly this rule.

### TCP

ByteBlower runs its own TCP stack on each port, so the congestion behaviour is a setting you choose, not whatever an operating system does.

#### Congestion control

Slow start and exponential backoff are always on. Below the slow-start threshold the window grows exponentially; above it, linearly. The selectable part is loss recovery ([article](https://support.excentis.com/knowledge/article/194)):

| Option | Behaviour |
| --- | --- |
| None | Fast retransmit only, no fast recovery |
| New Reno | Fast recovery that handles several dropped packets in one window |
| SACK | The receiver reports exactly which segments are missing. Negotiated at connection setup; falls back to New Reno if the peer lacks it |
| New Reno with Cubic, SACK with Cubic | Adds Cubic window growth, which recovers better on high-latency paths |
| TCP Prague (L4S) | Reacts to ECN congestion marks instead of waiting for loss; the count of CE marks is reported |

The docs call SACK with Cubic the best performer in most situations.

#### Window sizing

The receive window bounds how much data can be in flight. It is an unscaled value of at most 65535 bytes multiplied by a power of two:

```latex
\text{window} = \text{initial window} \times 2^{\,\text{scale}} \qquad \text{target: window} \ge \text{BDP} = \text{RTT} \times \text{bandwidth}
```

The window should be at least the bandwidth-delay product and a multiple of the MTU. Worked example: 1 Gbit/s at 10 ms round trip is 1.25 MB in flight; 65535 × 2^4 is 1.05 MB, too small, so the scale must be 5 or more.

The diagnosis rules follow directly:

| Graph shows | Rule | Cause |
| --- | --- | --- |
| Slow climb to full speed | Threshold reached too early, growth turned linear | Slow-start threshold too low |
| Flat speed below the link rate, no retransmissions | Window smaller than the BDP | Scale too low |
| Full speed, round-trip time above 100 ms | Window far above the BDP; data queues inside the sender | Scale too high |
| Sawtooth speed, retransmissions | Loss is collapsing the window | Packet loss on the path |
| Round-trip time rising steadily | Queues filling | Buffering in the network |

#### Timing points and the throughput formula

A TCP flow is one HTTP request. Each side records three timestamps, T1 to T3, whose meaning depends on the method ([article](https://support.excentis.com/knowledge/article/204)).

|  | T1 | T2 | T3 |
| --- | --- | --- | --- |
| GET, client | Request sent | First response segment received | Last response segment received |
| GET, server | Request received | Response starts | Last response segment acknowledged |
| PUT, client | Request starts | Last request segment acknowledged | Response received |
| PUT, server | First request segment received | Last request segment received | Response sent |

Duration and average throughput are always computed on the side that receives the bulk data:

```latex
\text{GET: } \frac{\text{bytes received by client}}{T_3 - T_2} \qquad \text{PUT: } \frac{\text{bytes received by server}}{T_2 - T_1}
```

Time to first byte in the report is T2 at the client. Goodput counts payload delivered to the application; throughput also counts TCP headers and retransmitted segments.

Connection health checks from the TCP counters:

- At the client, SYN-received and established should coincide. A later SYN-received means a duplicate SYN+ACK: a small gap points at a misbehaving router, a gap longer than the retransmit time at lost ACKs.
- More than one SYN received is suspicious.
- Client SYN-sent to server established is a lower bound on connection setup time.
- Read a counter before its timestamp; a timestamp whose counter is zero raises an error.
- Do not compare last-packet timestamps between client and server on fast or long paths; use round-trip time.

### Traffic models

Application tests are frame-blasting or TCP flows shaped to resemble an application. These are the shapes the docs specify.

| Model | How the traffic is built | Defaults |
| --- | --- | --- |
| Voice | G.711 over RTP at a constant packet interval. 20 ms packetisation gives 50 packets per second of 160 bytes; 10 ms gives 100 per second of 80 bytes | 20 ms |
| Gaming | UDP at a steady packet rate, with a set of frames whose lengths are drawn from a normal distribution, clamped to a minimum and maximum | Mean 110 bytes, deviation 20, min 22, max 1480, 20 distinct frames, 30 packets per second |
| Video | A simulated streaming player described only by its parameters: segment size, segment duration, a play goal and a buffering goal. It runs until stopped | Segment size 2,000,000 (unit not stated), segment duration 2.5 s, play goal 5 s, buffering goal 60 s |
| Conference | Three parallel frame-blasting streams: video, voice and screen share, each with its own rate and check | Set per stream |
| IMIX | A mix of frame sizes, each with a weight setting its share of the frames, optionally shuffled | Shuffled |
| Dynamic frame blasting | A UDP flow whose bitrate moves between a minimum and a maximum, updated once per scaling interval by a scaling rate | 5 to 50 Mbit/s, 5% per step |
| L4S frame blasting | UDP frames carrying a chosen ECN codepoint: not-ECT, classic, L4S or CE |  |
| HTTP | One request for a duration or a size, optionally capped at a maximum bitrate | Unlimited |

Frame modifiers change a stream while it runs:

| Modifier | Rule | Defaults |
| --- | --- | --- |
| Growing size | Send `iteration` frames at a size, then add `step` bytes, from minimum up to maximum | 60 to 1514 bytes, step 1, iteration 1 |
| Random size | Each frame gets a random size between minimum and maximum | 60 to 1514 bytes |
| Incremental field | A field of 1, 2, 4 or 8 bytes at a byte offset counts up by `step` between minimum and maximum | Length 2, range 0 to 65535, step 1 |
| Random field | The same field takes a random value in the range |  |
| Multiburst | Send `burstsize` frames at the stream's rate, stay silent for `interburstgap`, repeat | 100 frames, 1 s gap |

The size modifier applies per frame. On a stream with frames A and B growing from 60, the order is A-60, B-60, A-61, B-61. Older API versions produced A-60, B-61, A-62, B-63. Growing size yields a sawtooth throughput graph; multiburst yields a square wave.

Auto-correction: when a modifier or tag changes a frame, the server can recompute the IP header checksum, IP length, layer-4 checksum and layer-4 length just before sending. These are off by default and cost server resources.

Protocol timers a port uses as a host:

| Protocol | Rule |
| --- | --- |
| DHCPv4 | Discover then Request, each with an initial timeout of 1 s and up to 5 retries; fixed timing or RFC 2131 backoff; renew at half the lease time |
| ARP | Cache checked first; entries valid 120 s |
| IPv6 | Link-local address derived from the MAC (modified EUI-64); gateway learned from router advertisements; source address chosen per RFC 6724 |

### Pass and fail logic

A verdict is a threshold test applied by an analyser attached to a flow. The run fails if any flow fails.

| Analyser | Applies to | Rule | Default |
| --- | --- | --- | --- |
| Frame loss | UDP flows, gaming | Loss % within the maximum | 1.0% |
| Latency and loss | UDP flows | Loss within the maximum and average latency within the threshold | 1.0%, 5 ms |
| Latency CDF and loss | UDP flows | Loss within the maximum and latency at the quantile below the threshold | 1.0%, quantile 99.9, 5 ms |
| Gaming | Gaming flows | 99th-percentile latency below the threshold | 5 ms |
| Voice | Voice flows | Mean opinion score at or above the minimum | 4 |
| Video buffer | Video flows | Wait before playback starts within the maximum | 5 s |
| HTTP, L4S HTTP | TCP flows | None; always reported as "no analysis" |  |

The Low Latency test case adds `min_percentile` and `max_percentile` (defaults 10 and 90) as outlier boundaries for its latency analysis.

Standard-test verdicts:

**RFC 2544.** For every frame size, measured throughput must reach `expected_bitrate`.

**TR-398 Airtime Fairness.** For stations A and B with solo TCP maxima M, sent UDP at 0.75 M for station 1 and 0.50 M for its partner, and measured UDP rates U:

```latex
U_A > 0.45\,M_A \quad\text{and}\quad U_B > 0.45\,M_B \quad\text{and}\quad U_A + U_B > \text{expected throughput for the mode}
```

The two offered loads sum to more than the access point can carry, which forces it to choose who gets airtime. If station 1's solo test fails, the whole configuration is skipped.

**DOCSIS 4.0 ATP LL-04.40.** Two classic flows of 200-byte frames run back to back for 20 s each, the first at a higher rate than the second, both above the modem's configured limit. Loss % and latency are computed per 200 ms interval and compared with the ATP's test points, once without and once with a 40 s low-latency flow alongside.

**Scenario length.** With a maximum run time, every flow is cut at initial wait plus duration and the scenario stops at the maximum. Without one, the scenario runs as long as its longest flow, 10 s if none has a limit, and always waits for size-based TCP flows to finish.

### Timing machinery

#### Scheduling

Every stream and every schedulable action (an HTTP request, a multicast join, a ping) has an initial time to wait. Starting a set of ports starts all those countdowns at the same instant, and each item fires when its own wait expires. That is how flows in a scenario are offset against each other. Items already running are ignored; stopped ones are scheduled again.

The API is synchronous and the server never pushes events, so a script polls: start, sleep, refresh results, repeat.

#### Result sampling

The server keeps results in a fixed-length ring per object:

1. Every sampling interval (default 1 s) it closes one interval sample and one cumulative sample.
2. It keeps the newest few (default 6); each new sample pushes out the oldest.
3. `Refresh` copies whatever is in the ring to the client. The last sample is still open.
4. A client that refreshes less often than the ring's span (6 s by default) loses samples and gets gaps.

Refreshing many results in one batched call matters when comparing a sender with a receiver: separate round trips would read them at different moments. Scripts loop one extra second so frames on an interval boundary are counted.

#### Clock synchronisation

| Pair | How clocks agree | Accuracy stated |
| --- | --- | --- |
| Two ports on one server | One clock | Exact |
| Two servers with PTP (2100, 4100) | Hardware clocks disciplined continuously over a dedicated cable | Within a couple of microseconds |
| Two servers with NTP | Software discipline; on 2100 and 4100 only at startup | Lower; keep latency to the NTP server low |
| Server and Endpoint | The Endpoint sets its clock from the Meeting Point once, at registration, over the same link as test traffic unless a separate management interface is set | Best effort; drifts during long tests |
| Server and Golden Client (NUC with PTP) | PTP with NTP fallback | Well below 1 ms on wired |

A PTP node listens first and becomes master only if it hears no other; a dedicated master is forced with `masterOnly`. PTP gives no wall-clock reference, so PTP-only systems drift from real time while staying aligned with each other.

#### Endpoint run cycle

An Endpoint cannot be commanded live, so a test is shipped to it whole:

1. The Endpoint sends heartbeats to the Meeting Point and waits (Registered).
2. The controller locks it, uploads the scenario (Armed), and asks it to start. The reply is a start time slightly in the future.
3. Both sides wait for that time, then run (Running). By default the Endpoint sends no management traffic during the run.
4. Afterwards it reconnects on its next heartbeat and uploads results, which the Meeting Point relays. The framework waits up to 120 s for them.

With Heartbeat Mode (since 2.19.0) it keeps beating during the run, which allows remote cancel.

#### Report size budget

The GUI limits a report to about 12,000 graphing-hours:

```latex
\text{duration in hours} \times \sum_{\text{flows}} w < 12000 \qquad w = 1 \text{ (frame blasting)},\ 5 \text{ (latency)},\ 5 \text{ (TCP)},\ 1 \text{ (out-of-sequence)}
```

Example: two TCP flows, one plain UDP flow and one UDP flow with latency weigh 17; five days is 120 h, so 2,040. Separately, scenarios with more than 100 flows store no over-time results at all.

### Named but never explained

I re-read the pages for each of these; the docs give parameters or a name and no method. The source of the Test Framework, which is an installable Python package, is where the answers would be.

| Topic | What the docs give | What is missing |
| --- | --- | --- |
| Jitter | A value in every latency result | The definition or formula |
| MOS for voice | "Calculates the Mean Opinion Score" | The model and its inputs |
| Video buffer | Buffer size, play goal, maximum initial wait | Fill and drain logic, stall rule, the exact pass criterion |
| Dynamic frame blasting | Minimum and maximum bitrate, scaling interval, scaling rate | What triggers a step up or down, and what the 5% applies to |
| Gaming packet sizes | Normal distribution with mean, deviation, min, max | Whether deviation is a standard deviation; how samples are clamped and interleaved |
| IMIX | Length and weight per entry | The selection method and the default mix |
| Quantile | Latency at a quantile of the CDF | Bucket count and interpolation |
| RFC 2544 reruns | "Automated workarounds" | How many reruns are allowed; units of `tolerated_frame_loss` and `accuracy` |
| RFC 2544 first phase | "Doubling or increasing by 50%" | Which of the two the code uses |
| Timestamp sanity check | That a check exists and depends on the tag format | What it checks |
| DOCSIS ATP | Procedure and interval | Flow rates and pass thresholds |
| TR-398 | The 45% rule | The expected-throughput table per mode |
| Latency noise floor | A per-model chart | The numbers, published only as an image |

Three things in this tab are my own additions, not from the docs: the estimate of how many RFC 2544 trials bisection needs, the 1 Gbit/s window-scale worked example, and the "Rule" column of the TCP diagnosis table, which states the reasoning behind symptoms and causes the docs list.


<br/>


## Reference

### What ByteBlower is

ByteBlower is a traffic generator and analyzer from Excentis: a 1U server generates and measures traffic, and a client computer drives it. The documentation is spread over four sites, distilled here from about 370 pages crawled on 8 October 2026.

The server chassis holds three isolated systems ([components](https://support.excentis.com/knowledge/article/240)):

- **Traffic generation software**: owns the traffic interfaces and most of the CPU. Updates need no internet on the server.
- **Host operating system**: owns the management interfaces (`man0`, `man1`), reachable over SSH. Default login is `root` / `excentis`.
- **IPMI**: optional remote hardware control (power, boot).

There is no software limit on the number of clients, and sharing one server among users is normal.

| Interface | What it is | Use it when |
| --- | --- | --- |
| ByteBlower GUI | Desktop app with wizards, project files (`.bbp`) and an HTML/PDF reporting engine | Building and running tests by hand |
| ByteBlower-CLT | Command-line runner for the same project files | Scheduling GUI projects from scripts or CI |
| [Test Framework](https://api.byteblower.com/test-framework/latest/) | Python library and CLI driven by a JSON scenario file, with its own HTML/JSON/JUnit reports | Automating standard tests without writing much code |
| [Python API](https://api.byteblower.com/python) (`byteblowerll`) | Low-level object API, same building blocks as the GUI, no reporting engine | Full control and raw results |
| [Tcl API](https://api.byteblower.com/tcl) | Same low-level model in Tcl, plus a higher-layer `ByteBlowerHL` package | Existing Tcl automation |
| [OpenMetrics exporter](https://api.byteblower.com/prometheus) | The GUI serves live metrics on TCP 8123 for Prometheus | Real-time graphs in Grafana, or scenarios over 100 flows |

Model differences that recur throughout the docs:

| Model | Notes |
| --- | --- |
| 1x00 | Oldest series. NTP for time. Cannot measure latency at high speed. |
| 2100 | Hardware-accelerated. PTP supported and preferred. |
| 3100 / 3200 | Software traffic generation on Intel x710 NICs. NTP for time. NIC firmware fix may be needed. |
| 4100 | Hardware-accelerated. PTP supported and preferred. |
| 5100 | Up to 100 Gbps. NTP only. May sample received packets for latency. Upgrades only through the GUI. |

### Core concepts

Every test is flows between ByteBlower Ports, and every interface (GUI, Test Framework, APIs) uses the same vocabulary ([basic test units](https://support.excentis.com/knowledge/article/88)).

| Term | Meaning |
| --- | --- |
| Port | A small virtual host with its own protocol stack, docked to one server interface. Needs a MAC; gets IPv4 (fixed or DHCP) and/or IPv6 (fixed, SLAAC or DHCPv6). Answers ping once it has an address. |
| Interface | Physical attachment point. **Nontrunk** sits on the server itself (`nontrunk-1`). **Trunk** sits on a ByteBlower switch and shares a server connector (`trunk-1-20`). |
| Frame | A layer-2 Ethernet II frame you define, 60 to 10000 bytes excluding FCS. |
| Frame Blasting | Stateless traffic: one port injects frames at a set rate, the destination counts them. Gives exact, repeatable loss and latency. |
| TCP flow | Stateful traffic. Always HTTP over TCP: an HTTP client on one port, an HTTP server on the other. Self-limits to available bandwidth. |
| Flow | One or more frames tracked as one result, from one source to one or more destinations. |
| Scenario | Flows with start times and durations. The runnable unit; one report per run. |
| Batch | Scenarios run one after another. |
| Trigger | A receive-side counter selected by a BPF filter. This is how received frames are attributed to a flow. |
| Endpoint | An app on a phone or laptop acting as a port. Controlled through a Meeting Point, never directly. |

Measurements and how they work:

- **Loss**: frames sent minus frames matched by the destination trigger. If two flows have near-identical frames the filters collide and loss goes negative.
- **Latency**: the sender overwrites the last 8 bytes of the payload with a timestamp; the receiver subtracts it from its own clock. Sender and receiver on different machines need synchronized clocks.
- **Out-of-sequence**: an incrementing frame number in the payload. Reports reordering, not which frames were lost.
- **TCP**: goodput (application rate), throughput (including headers and retransmissions), round-trip time and transmit window.
- **NAT**: when a port is behind NAT, ByteBlower sends about 10 discovery frames per second for up to 20 seconds to learn the public address and port, then counts on those ([NAT](https://support.excentis.com/knowledge/article/109)).

TCP direction follows the HTTP method. GET makes the destination initiate and download; PUT makes the source initiate and upload. AUTO picks PUT when the source is behind NAT, otherwise GET ([TCP timing](https://support.excentis.com/knowledge/article/202)).

Bitrates depend on what you count. Each frame costs 24 extra bytes on the wire (preamble 7, SFD 1, FCS 4, gap 12), so 60-byte frames at 1 Gbps line rate are only 714 Mbps of frame bitrate ([link speed](https://support.excentis.com/knowledge/article/197)).

### Server setup and maintenance

Server administration runs through `byteblower-configurator` over SSH or a keyboard and screen; the management IP defaults to DHCP on `man0`.

| Task | How |
| --- | --- |
| Find the management IP | Server 2.6.0 and later show it on the login screen. Earlier: log in and run `ifconfig man0`. |
| Set a static management IP | Configurator: System Configuration, Network Configuration, select `man0`, Connectivity, static ([article](https://support.excentis.com/knowledge/article/72)). |
| Change the root password | `passwd`, or the configurator. A lost password means reinstalling. |
| Set time | Configurator: Time Configuration. NTP on 1x00, 3x00, 5x00. PTP on 2100 and 4100, using the PTP cable shipped with the unit; NTP there only corrects at startup ([article](https://support.excentis.com/knowledge/article/245)). |
| Regroup trunk interfaces | Possible since server 2.14 for daisy-chained and multi-trunk switches. Contact support to convert a layout. |
| Configure IPMI | `bmc-config --checkout --section=Lan_Conf --filename=ipmi-network.conf`, edit, then `bmc-config --commit --filename=ipmi-network.conf`. |
| Upgrade | GUI upgrade wizard. The client PC needs internet and SSH to the server; the server does not. About 10 minutes with reboots. The only method on the 5100. |
| Downgrade | `excentux-update`, pick the version, reboot. Not for the 5100. Talk to support first: forward compatibility is limited. |
| Check version | `byteblower-get-version`, or the GUI Server view. |

Firewall ports toward the server ([remote access](https://support.excentis.com/knowledge/article/239)):

| TCP port | Use |
| --- | --- |
| 22 | SSH, also used by the GUI upgrade wizard |
| 9002 | GUI or API to the ByteBlower server |
| 9100 | Endpoint heartbeat to the Meeting Point |
| 9101 | GUI or API to the Meeting Point |

Ports 9100 and 9101 only matter with a Meeting Point license. The server has no firewall of its own.

First check after installation is the Quick self-test: cable two trunk ports back to back, open the example `.bbp`, add the server by IP, dock both ports, run. The report should read 100% of frames received ([self-test](https://support.excentis.com/knowledge/article/90)).

For one-way latency across machines, PTP on two 4100 servers stayed within a couple of microseconds. Building your own PTP master on an Intel NUC with `linuxptp` is documented step by step ([time sync](https://support.excentis.com/knowledge/article/417)).

### Endpoint and Meeting Point

The Endpoint is an app that turns a phone, laptop or NUC into a traffic port; the Meeting Point is a daemon on the ByteBlower server that every Endpoint registers with and that relays all commands and results.

A test runs in four states: Contacting, Registered (idle), Armed (scenario received), Running. By default the Endpoint goes silent during a run and uploads results afterwards. Since 2.19.0 Heartbeat Mode keeps it in contact so a run can be cancelled remotely; in the API that is `ScenarioHeartbeatIntervalSet`, in nanoseconds.

The Endpoint must be able to reach the Meeting Point. Three topologies are documented ([connection](https://support.excentis.com/knowledge/article/108)):

1. Through the server's management interface, usually via the gateway's WAN side.
2. Through a spare server interface wired into the test network, when management is fully separate.
3. Through a second management interface plugged into a LAN port of the device under test, when it has no uplink.

Setup:

- Install from the app stores, or download for Windows, macOS and Linux. Android without Google Play: sideload the APK with `adb install ByteBlower.apk`.
- Enter the server's IPv4 address or hostname as the Meeting Point.
- Headless: `byteblower-wireless-endpoint [--management <nic>] [--traffic <nic>] <meetingpoint>`. A systemd unit and a Windows Task Scheduler recipe are documented for autostart ([autostart](https://support.excentis.com/knowledge/article/183)).
- In the GUI the server appears twice: once as wired, once as Meeting Point. Dock the wireless port on the device listed under the Meeting Point.

What an Endpoint cannot do, compared with a server port ([limits](https://support.excentis.com/knowledge/article/256)):

- One frame per Frame Blasting template.
- A UDP port can be used once for transmit and once for receive per scenario.
- No out-of-sequence detection.
- As a destination it reports only average latency, not the distribution.
- Latency is best-effort: the clock syncs to the Meeting Point at registration and is not re-synced during a test.
- iOS reports SSID and BSSID but never RSSI, channel or Tx rate. Android and macOS need location permission for Wi-Fi statistics.

L4S needs server, GUI and Endpoint at 2.22.0 or later. On Linux it needs the L4S team's custom kernel with `tcp_prague` and `sch_dualpi2`; macOS and iOS have Accurate ECN only ([L4S](https://support.excentis.com/knowledge/article/322)).

The "Golden Client" is a reference Endpoint on an Intel NUC with Debian, PTP via `linuxptp` and `chrony`. Wired latency accuracy is reported as well below 1 ms ([Golden Client](https://support.excentis.com/knowledge/article/278)).

### Test Framework

The Test Framework is the fastest route to automation: describe ports and flows in a JSON file, run one command, get HTML, JSON and JUnit XML reports with pass/fail. The docs show version 1.4.2, dated 2026/09/21, for Python 3.7 to 3.11 ([docs](https://api.byteblower.com/test-framework/latest/)).

```bash
python3 -m venv --clear .venv && . ./.venv/bin/activate
pip install -U byteblower-test-framework
byteblower-test-framework --config-file my_test_config.json --report-path reports
```

Every command takes the same three options: `--config-file`, `--config-path` (default `.`) and `--report-path` (default `.`).

| Package | Command | Default config file | What it tests |
| --- | --- | --- | --- |
| `byteblower-test-framework` | `byteblower-test-framework` | `byteblower_test_framework.json` | Any mix of UDP and TCP flows |
| `byteblower-test-cases-low-latency` | `byteblower-test-cases-low-latency` | `low_latency.json` | Low Latency DOCSIS and L4S, with voice, video, gaming and conference traffic |
| `byteblower-test-cases-rfc-2544` | `byteblower-test-cases-rfc-2544-throughput` | `rfc_2544.json` | Highest lossless rate per frame size |
| `byteblower-test-cases-tr-398` | `byteblower-test-cases-tr-398-airtime-fairness` | `tr_398.json` | Wi-Fi airtime fairness across three stations |
| `byteblower-test-cases-docsis-atp` | `byteblower-test-cases-docsis-atp-mulpi-v4-0-ll-04-40-part1` | `part1.json` | DOCSIS 4.0 PIE AQM with and without low-latency traffic |

The same run from Python: `from byteblower_test_framework import run`, then `run(test_config, report_path=..., report_prefix=...)` with the JSON content as a dict.

#### Scenario file

Required root keys are `server`, `ports` and `flows`. Optional: `meeting_point`, `maximum_run_time` (seconds), `report` (`html`, `json`, `junit_xml` booleans) and `enable_scouting_flows`.

```json
{
    "$schema": "https://api.byteblower.com/test-framework/json/cli-config-schema.json",
    "server": "byteblower-server.example.com.",
    "ports": [
        {
            "name": "NSI",
            "port_group": ["classic_nsi"],
            "interface": "trunk-1-3",
            "ipv4": "192.168.1.2",
            "netmask": "255.255.255.0",
            "gateway": "192.168.1.254"
        },
        {
            "name": "CPE",
            "port_group": ["classic_cpe"],
            "interface": "trunk-1-4",
            "ipv4": "dhcp",
            "nat": true
        }
    ],
    "flows": [
        {
            "name": "Downstream UDP",
            "type": "frame_blasting",
            "source": {"port_group": ["classic_nsi"]},
            "destination": {"port_group": ["classic_cpe"]},
            "frame_size": 60,
            "bitrate": 85000000.0,
            "analysis": {
                "latency": true,
                "max_loss_percentage": 1,
                "max_threshold_latency": 20
            }
        },
        {
            "name": "Bidirectional HTTP",
            "type": "http",
            "source": {"port_group": ["classic_nsi"]},
            "destination": {"port_group": ["classic_cpe"]},
            "maximum_bitrate": 20000000.0,
            "initial_time_to_wait": 2.0,
            "duration": 40.0,
            "receive_window_scaling": 12,
            "add_reverse_direction": true
        }
    ],
    "report": {"html": true, "json": true, "junit_xml": false},
    "enable_scouting_flows": true,
    "maximum_run_time": 30.0
}
```

To use an Endpoint, add a root `meeting_point` and replace the port's `interface` with `"uuid": "<endpoint uuid>", "ipv4": true`.

| Port key | Values | Default |
| --- | --- | --- |
| `port_group` | List of names; flows reference groups, and one flow is created per source and destination pair |  |
| `interface` | `nontrunk-N` or `trunk-N-M`. Server ports only |  |
| `uuid` | Endpoint only; excludes `interface` |  |
| `ipv4` | Address or `"dhcp"`; `true` on an Endpoint | `"dhcp"` |
| `ipv6` | `"dhcp"`, `"slaac"` or a list of `{address, prefix_length}`; `true` on an Endpoint | unset |
| `netmask`, `gateway` | Static addressing only | `255.255.255.0`, none |
| `nat` | Port is behind IPv4 NAT; triggers discovery | `false` |
| `firewall` | Port is behind an IPv6 firewall | `false` |
| `mac` | Server ports only | generated |
| `vlans` | List, outer first, of `{id, protocol_id, priority, drop_eligible}` |  |
| `capture` | `{enabled, filter, filename}`; receive side only | off |

| Flow key | Applies to | Meaning | Default |
| --- | --- | --- | --- |
| `type` | all | `frame_blasting` or `http` |  |
| `dscp`, `ecn` | all | Integer or hex string | 0 |
| `initial_time_to_wait` | all | Seconds | 0 |
| `add_reverse_direction` | all | Adds the mirrored flow | `false` |
| `bitrate` or `frame_rate` | UDP | Bits per second excluding VLAN bytes, or frames per second; pick one | 100 fps |
| `frame_size` | UDP | Bytes without CRC, minimum 42 | 1024 |
| `duration` or `number_of_frames` | UDP | Seconds, or a frame count | scenario run time |
| `nat_keep_alive` | UDP | Keeps the NAT entry open | `false` |
| `analysis.max_loss_percentage` | UDP | Fail above this loss | 1.0 |
| `analysis.latency` | UDP | Adds latency over time, CDF and CCDF | `false` |
| `analysis.max_threshold_latency`, `quantile` | UDP | Latency at the quantile must stay under the threshold, in ms | 5.0, 99.9 |
| `duration` or `request_size` | HTTP | Seconds, or bytes; pick one |  |
| `maximum_bitrate` | HTTP | Bits per second | unlimited |
| `receive_window_scaling` | HTTP | 0 to 12 |  |
| `slow_start_threshold` | HTTP | Integer; unit not stated |  |
| `enable_l4s` | HTTP | TCP Prague with CE-mark counting; needs 2.22.0 everywhere | `false` |

HTTP flows are measured but never fail a test. The overall result is FAIL if any flow fails. `rate_limit` (bytes per second) and `napt_keep_alive` are deprecated in favour of `maximum_bitrate` and `nat_keep_alive`.

#### Test cases

- **Low Latency** adds flow types `dynamic_frame_blasting`, `l4s_frame_blasting`, `voice` (G.711, scored by MOS, pass at 4 or above), `video`, `gaming` (latency threshold 5 ms) and `conference`. Video, dynamic and L4S frame blasting do not run on Endpoints.
- **RFC 2544** takes `source`, `destination` and optional `frame_configs` (`size`, `initial_bitrate`, `tolerated_frame_loss`, `accuracy`, `expected_bitrate`). It searches the rate per frame size by halving and doubling, then bisecting. Default sizes are 60, 124, 252, 508, 1020, 1276 and 1514 bytes. It fails when any size lands below `expected_bitrate`.
- **TR-398 Airtime Fairness** takes `dut` and exactly three `wlan_stations` as Endpoints. Each station must reach more than 45% of its own TCP maximum under paired UDP load, and the pair must beat the TR-398 expected total. Moving stations between runs is manual.
- **DOCSIS 4.0 ATP LL-04.40 Part 1** takes `nsi` and `cpe`. It runs two procedures of two 20-second classic flows, the second alongside a 40-second low-latency flow. The pass thresholds are not published in the docs.

#### Python classes

The library behind the CLI lives in `byteblower_test_framework`. Release order is scenario and flows, then ports, then server.

| Module | Classes |
| --- | --- |
| `run` | `Scenario`: `add_flow`, `add_report`, `add_capture`, `run(maximum_run_time=...)`, `report()`, `release()` |
| `host` | `Server(ip_or_host)`, `MeetingPoint(ip_or_host)` |
| `endpoint` | `IPv4Port`, `IPv6Port`, `NatDiscoveryIPv4Port`, `NatDiscoveryIPv6Port`, `IPv4Endpoint`, `IPv6Endpoint` |
| `traffic` | `FrameBlastingFlow`, `HTTPFlow`, `VoiceFlow`, `VideoFlow`, `GamingFlow`; frames `IPv4Frame`, `IPv6Frame`, `MobileFrame`, `Imix` |
| `analysis` | `FrameLossAnalyser`, `LatencyFrameLossAnalyser`, `LatencyCDFFrameLossAnalyser`, `VoiceAnalyser`, `HttpAnalyser`, `L4SHttpAnalyser`, `BufferAnalyser`, `PortCapture` |
| `report` | `ByteBlowerHtmlReport`, `ByteBlowerJsonReport`, `ByteBlowerUnitTestReport` |

The published docs contain no hand-written `Scenario` script, and the method that attaches an analyser to a flow is not on the reference pages. Start from the JSON route or the package source.

### Python API (byteblowerll)

The low-level API is one singleton from which you create servers, ports, streams and receivers, then poll result objects; you build the frame bytes yourself, normally with scapy. Install with `pip install byteblowerll scapy` ([reference](https://api.byteblower.com/python), [examples](https://github.com/excentis/ByteBlower_python_examples)).

```text
ByteBlower.InstanceGet()
  ServerAdd(host, port=9002) -> ByteBlowerServer
    PortCreate('trunk-1-13') -> ByteBlowerPort
      Layer2EthIISet()  -> MacSet
      Layer25VlanAdd()  -> IDSet            (call again to stack; first is outermost)
      Layer3IPv4Set()   -> IpSet, NetmaskSet, GatewaySet | ProtocolDhcpGet().Perform(); Resolve(ip)
      Layer3IPv6Set()   -> IpManualAdd('addr/len') | StatelessAutoconfiguration() | ProtocolDhcpGet().Perform()
      TxStreamAdd()     -> Stream: NumberOfFramesSet, InterFrameGapSet, Start, Stop
        FrameAdd()      -> Frame: BytesSet(hex), FrameTagTimeGet(), FrameTagSequenceGet()
      RxTriggerBasicAdd()        counts frames matching a BPF filter
      RxLatencyBasicAdd()        latency min, average, max, jitter
      RxLatencyDistributionAdd() latency histogram
      RxOutOfSequenceBasicAdd()  reordering
      RxCaptureBasicAdd()        pcap capture
      ProtocolHttpServerAdd() / ProtocolHttpClientAdd()
  MeetingPointAdd(host, port=9101) -> MeetingPoint
    DeviceGet(uuid) -> WirelessEndpoint: Lock, Prepare, Start, ResultGet
      TxStreamAdd() -> StreamMobile;  RxTriggerBasicAdd() -> TriggerBasicMobile;  ProtocolHttpClientAdd()
```

UDP frame blasting between two ports, condensed from the official `back2back/ipv4.py`:

```python
from time import sleep
from byteblowerll.byteblower import ByteBlower
from scapy.layers.inet import UDP, IP, Ether
from scapy.all import Raw

bb = ByteBlower.InstanceGet()
server = bb.ServerAdd('byteblower-server.example.com')

def make_port(interface, mac):
    port = server.PortCreate(interface)
    port.Layer2EthIISet().MacSet(mac)
    port.Layer3IPv4Set().ProtocolDhcpGet().Perform()
    return port

tx = make_port('trunk-1-13', '00:bb:01:00:00:01')
rx = make_port('trunk-1-14', '00:bb:01:00:00:02')
src_ip = tx.Layer3IPv4Get().IpGet()
dst_ip = rx.Layer3IPv4Get().IpGet()
dst_mac = tx.Layer3IPv4Get().Resolve(dst_ip)      # peer MAC, or the gateway's when off-subnet

frame_size, n_frames, gap_ns, udp_port = 512, 10000, 1000000, 4096
scapy_frame = (Ether(src=tx.Layer2EthIIGet().MacGet(), dst=dst_mac)
               / IP(src=src_ip, dst=dst_ip) / UDP(sport=udp_port, dport=udp_port)
               / Raw(b'a' * (frame_size - 42)))

stream = tx.TxStreamAdd()
stream.NumberOfFramesSet(n_frames)
stream.InterFrameGapSet(gap_ns)                    # ns between frame starts: 1000 fps
stream.FrameAdd().BytesSet(''.join(format(b, '02x') for b in bytearray(bytes(scapy_frame))))

trigger = rx.RxTriggerBasicAdd()
trigger.FilterSet('ip dst {} and udp port {}'.format(dst_ip, udp_port))
trigger.ResultClear()                              # triggers count from creation

stream.Start()
sleep(n_frames * gap_ns / 1e9 + 1)                 # one extra second for frames in flight

tx_result, rx_result = stream.ResultGet(), trigger.ResultGet()
tx_result.Refresh(); rx_result.Refresh()
print(tx_result.PacketCountGet(), rx_result.PacketCountGet())

server.PortDestroy(tx); server.PortDestroy(rx)
bb.ServerRemove(server)
```

Variations on that script:

| To measure | Change |
| --- | --- |
| Latency | `frame.FrameTagTimeGet().Enable(True)` and receive with `rx.RxLatencyBasicAdd()`; read `LatencyAverageGet()`, `LatencyMinimumGet()`, `LatencyMaximumGet()`, `JitterGet()` in ns |
| Reordering | `frame.FrameTagSequenceGet().Enable(True)` and `rx.RxOutOfSequenceBasicAdd()`; read `PacketCountOutOfSequenceGet()` |
| IPv6 | `Layer3IPv6Set()`, scapy `IPv6`, filter `ip6 dst ... and udp port ...` |
| TCP | `http_server = p1.ProtocolHttpServerAdd(); http_server.Start()`. On the client: `RemoteAddressSet`, `RemotePortSet`, `HttpMethodSet`, `RequestDurationSet(ns)` or `RequestSizeSet(bytes)`, `RequestStart()`, `WaitUntilConnected(ns)`, `WaitUntilFinished(ns)`. Results via `HttpSessionInfoGet().ResultGet()` |
| Many flows | Start ports together with `server.PortsStart(ByteBlowerPortList)`; refresh everything in one round trip with `bb.ResultsRefresh(AbstractRefreshableResultList)` |
| Over time | `ResultHistoryGet()`, `Refresh()` each second, then `IntervalLatestGet()` or iterate `IntervalGet()` |

Results come in two forms. `ResultGet()` is a cumulative snapshot. `ResultHistoryGet()` is a fixed-length ring of interval and cumulative samples, one per second by default, whose last sample is still open. Both are local copies until you call `Refresh()`.

Units seen in the official examples:

| Quantity | Unit |
| --- | --- |
| Durations, inter-frame gap, timeouts, sampling interval, latency, jitter | nanoseconds, integers |
| Timestamps | POSIX time in nanoseconds |
| Request size, byte counters, congestion window | bytes |
| `Frame.BytesSet` | hex string of the whole Ethernet frame, no CRC |
| `DataRate` | `bitrate()` in bits per second, `MbpsGet()`, `toString()` |

An Endpoint runs a prepared scenario instead of live commands:

1. `endpoint = meetingpoint.DeviceGet(uuid)`, then `endpoint.Lock(True)`.
2. Configure. Transmit uses `FrameMobile.PayloadSet` (UDP payload only) with `DestinationAddressSet`, `DestinationPortSet`, `SourcePortSet` on the stream. Receive uses `FilterUdpSourcePortSet`, `FilterUdpDestinationPortSet`, `FilterSourceAddressSet` and `DurationSet(ns)` instead of BPF.
3. `endpoint.Prepare()`, then `start = endpoint.Start()`, which returns a future start time. Sleep until `start - meetingpoint.TimestampGet()` has passed, then start the wired side.
4. After the run wait a heartbeat or two, call `endpoint.ResultGet()`, refresh the individual results, then `endpoint.Lock(False)`.

Rules that bite:

- `ServerRemove`, `MeetingPointRemove` and `DestroyInstance` invalidate every object under them; touching a stale handle can crash the process.
- A receiver without `FilterSet` counts every frame on the port.
- Read latency getters only when `PacketCountGet()` is non-zero.
- Feature support varies by server and device: check `port.CapabilityIsSupported(name)` before relying on a feature.
- `ServerAdd` raises `ByteBlowerServerUnreachable` or `ByteBlowerServerIncompatible`; `MeetingPointAdd` raises `MeetingPointUnreachable`.

The reference is one very long page and only its first part could be read. Everything after `ByteBlowerLicense` is covered here by method names and by usage in the official examples, not by the reference text. The Tcl class pages describe the same objects in full and are the fallback for parameters and defaults.

### Tcl API

The Tcl API exposes the same objects as Python with dotted method names, and its per-class pages are the most complete description of the low-level model. The docs show version 2.22.2 ([reference](https://api.byteblower.com/tcl)).

| Package | Namespace | Purpose |
| --- | --- | --- |
| `ByteBlower` |  | Lower-layer object API |
| `ByteBlowerHL` | `excentis::ByteBlower` | Higher-layer scenarios as nested lists. Frame blasting only. |
| `excentis_basic` | `excentis::basic` | Frame builders, checksums, address helpers |

Names map mechanically. Python `port.Layer3IPv4Set()` is Tcl `$port Layer3.IPv4.Set`; `TxStreamAdd` is `Tx.Stream.Add`; `RxLatencyBasicAdd` is `Rx.Latency.Basic.Add`; `ResultHistoryGet` is `Result.History.Get`. Durations are nanoseconds but accept suffixes: `$stream InterFrameGap.Set 100ms`. Every object has `Description.Get` and `Destructor`; `$bbServer Destructor` cleans up a whole test.

```tcl
package require ByteBlower
set bb [ ByteBlower Instance.Get ]
set server [ $bb Server.Add "byteblower.lab.company.com" ]
set port [ $server Port.Create "trunk-1-1" ]
[ $port Layer2.EthII.Set ] Mac.Set "00ff1c000001"
[ [ $port Layer3.IPv4.Set ] Protocol.Dhcp.Get ] Perform

set trigger [ $port Rx.Trigger.Basic.Add ]
$trigger Filter.Set "udp port 2002"
$trigger Result.Clear
set result [ $trigger Result.Get ]
$result Refresh
puts [ $result PacketCount.Get ]
```

The higher-layer API runs a whole scenario in one call. A flow is a list of `-tx` and `-rx` components, and `ExecuteScenario` sets up, runs, collects and tears down:

```tcl
set flow [ list -tx [ list -port $srcPort -frame [ list -bytes $frameBytes ] \
                           -numberofframes 1000 -interframegap 1000000 ] \
                -rx [ list -port $dstPort -trigger [ list -type basic -filterFormat bpf \
                           -filter "udp dst port 2002" ] ] ]
set result [ ::excentis::ByteBlower::ExecuteScenario [ list $flow ] ]
# {-tx {NrOfFramesSent 1000 ...} -rx {NrOfFrames 1000}}
```

| Higher-layer proc | Returns |
| --- | --- |
| `ExecuteScenario` | Full counters per flow. Options `-finaltimetowait` (ms, default 5000), `-extended` |
| `ExecuteScenarioRT` | Same, with a callback every `-updateinterval` ms (default 1000) |
| `FlowLatency` | Per flow: frames sent, and received, min, average, max latency and jitter in ns |
| `FlowLossRate` | Loss per RFC 1242 as a percentage, counts, or per flow |
| `FlowOutofsequence` | Frames sent, received, and out of sequence |
| `NatDevice.IP.Get` | Public IP and UDP port of a NAT device |
| `PPPoE.Setup`, `PPPoE.Start`, `PPPoE.MultiPPPoESessions.*` | PPPoE session helpers |

Defaults and limits stated on the Tcl class pages, which describe the same server objects Python uses:

| Item | Value |
| --- | --- |
| Frame bytes | 60 to 8192 bytes, no CRC; can be changed during transmission |
| `NumberOfFrames` | `-1` means continuous |
| MDL (largest frame a port sends) | Default 1514; maximum typically 9014 on nontrunk, 9010 on trunk |
| Result history | One sample per second, 6 kept; refresh at least every 5 seconds or lose samples. Configurable since 2.3.0 |
| DHCP | Initial timeout 1 s, 5 retries, release on port destruction |
| ARP cache | Entries valid 120 s |
| HTTP receive window | Initial 65535 bytes, scaling on, scale value 3 (range 0 to 8) |
| HTTP history | 500 ms samples, 10 kept |
| Dual stack | Not on one port. Create two ports with the same layer 2 settings |
| `Filter.Set` on basic receivers | Resets counters and invalidates history |

Migrating old scripts ([guide](https://api.byteblower.com/tcl/TclApiv2Migrate.html)):

- `Counters.Get` name-value lists became result objects: `[ $trigger Result.Get ] PacketCount.Get`.
- Static calls such as `ByteBlower Server.Add` are deprecated; call them on `[ ByteBlower Instance.Get ]`.
- Typed adders replaced generic ones: `Rx.Trigger.Add` became `Rx.Trigger.Basic.Add`, `Layer3.Set` became `Layer3.IPv4.Set`.
- Frame tags moved: `TimeTag.Enable` became `FrameTag.Time.Get`.
- Size modifiers moved from stream to frame and now apply per frame, which changes the size sequence on multi-frame streams.
- Poll `$httpClient Finished.Get` instead of TCP status strings. The `serverDefault` congestion algorithm is gone; name one.
- IGMP and MLD put the version in the method name: `Session.V2.Add`.

Known bugs listed by the docs: HTTP requests cannot be started through `Schedules.Start` (use `Ports.Start`); `Logging.File.Name.Set` fails silently on a bad path; `ByteBlowerServer::Update` is not implemented; the Telnet client reports no error for an unreachable server ([bugs](https://api.byteblower.com/tcl/bug.html)).

### Reading results

GUI and CLT reports come from one engine; `-regenerate` or the Archive view rebuilds them from stored data in html, pdf, csv, xls, xlsx, json or docx.

**Latency CDF and CCDF.** One line per flow on log axes; further left is lower latency. Where a line crosses P99, 99% of packets arrived within that latency. The plot stops at P99.99 ([article](https://support.excentis.com/knowledge/article/190)).

| Warning | Fix |
| --- | --- |
| Fewer than 50 data points | All packets fall in a narrow band. Narrow the histogram range in Preferences. |
| Packets below or above range | Move the range start or end in Preferences. |
| Fewer than 10,000 received packets | Send more packets or run longer. |
| Sampled packets | Expected on the 5100. On other models, update. |

**TCP graphs.** A large gap between goodput and throughput means retransmissions. A steadily rising round-trip time means buffers filling. A drop in transmit window usually means loss ([diagnosis](https://support.excentis.com/knowledge/article/192)).

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Throughput climbs slowly | Slow-start threshold too low | Set it to infinite |
| Stable but low throughput, no retransmissions | Window scale too low | Raise it; 4 to 6 is normally enough |
| Good throughput, round-trip time over 100 ms | Window scale too high | Lower it to 4 to 6 |
| Unstable throughput, many retransmissions | Packet loss | Rate-limit the flow, try Cubic (high latency) or SACK (Wi-Fi), capture and inspect |

The right receive window is about the bandwidth-delay product, round-trip time times bandwidth.

**TCP timing.** Duration and throughput are always measured on the receiving side: for GET from first to last response segment at the client, for PUT from first to last request segment at the server. Reports also give time to first byte and minimum, average and maximum round-trip time.

**Live metrics.** Since GUI 2.18 the GUI serves OpenMetrics on port 8123; Prometheus scrapes it with a static target `localhost:8123`. Scenarios over 100 flows keep no over-time results in the GUI at all, so this is the only way to graph them ([metrics](https://api.byteblower.com/prometheus)).

| Metric | Meaning | Labels |
| --- | --- | --- |
| `byteblower_gui_traffic_bytes_total` | Bytes sent or received, reset per scenario; UDP and TCP | `flow`, `port`, `direction` |
| `byteblower_gui_latency_average_seconds`, `_minimum_`, `_maximum_`, `_jitter_` | One-way latency over the last second; frame blasting only | `flow`, `source`, `destination`, `latency_type` |
| `byteblower_gui_out_of_sequence` | Reordered packets, reset per scenario | `flow`, `port` |

**Machine-readable results.** The JSON report lists `frameBlastingFlows[]` with `source.sent.packets` and `destinations[].received.packets`. The CLT is the scripted route to it:

```bash
ByteBlower-CLT -project clt_demo.bbp -scenario latency_under_load -output reports/
```

| CLT exit code | Meaning |
| --- | --- |
| 0 | Success |
| 64 | Bad arguments |
| 65 | Project unreadable, usually saved by a newer GUI |
| 66 | Project, scenario or batch not found |
| 70 | Internal error |
| 75 | Temporary failure such as ARP; retry |

The GUI must be closed while the CLT runs, and ports must already be docked in the project.

### Troubleshooting

Most surprising results trace back to clocks, colliding filters, NAT or window settings.

| Symptom | Cause | Fix |
| --- | --- | --- |
| Negative latency | Receiver clock behind the sender's: two servers, or server and Endpoint, not continuously synced | PTP or NTP on both; prefer both ports on one server ([article](https://support.excentis.com/knowledge/article/166)) |
| Latency spikes of seconds | Payload corruption altering the timestamp | Check loss alongside; fix the network |
| Negative loss (more received than sent) | Frames of two flows too similar for unique filters | Enable the Unique Frame Modifier, or change a length, payload byte or UDP port ([article](https://support.excentis.com/knowledge/article/233)) |
| No traffic to a device behind a gateway | NAT not enabled on the port | Set NAT to Yes on the port |
| Endpoint cannot dock or receives nothing | Device has several IP addresses | Pick the traffic interface in the app; set NAT to Yes |
| Endpoint shown as Unsupported | New OS version not yet verified | Usually works; update Meeting Point and Endpoint |
| 100% loss with latency on IPv6 UDP | Timestamp breaking the UDP checksum on old versions | Update; software timestamping is now the default |
| Square-wave throughput on a 3100 or 3200 | x710 NIC firmware flapping the link | Run the NIC firmware update on both NICs ([article](https://support.excentis.com/knowledge/article/160)) |
| Server will not start: "Failed to allocate hostbuffers" | Kernel memory fragmentation | Reboot the server |
| 1300: "No cores found on NUMA node 0" | BIOS lost NUMA setting | Re-save NUMA Support in BIOS, on site |
| Report missing graphs | Scenario has more than 100 flows | Export to Prometheus |
| Report too large or GUI out of memory | Over about 12,000 graphing-hours | Split scenarios, CSV only via CLT, or raise `-Xmx` in `ByteBlower.ini` |
| Upgrade wizard fails | Client cannot reach update servers or SSH | Update the GUI first; check proxy and port 22 |
| Self-test loses frames | Cabling or load | Check link lights and cable; lower the load |

To locate loss in time: read the over-time graph, then shorten the test, then split one flow into many short consecutive flows. To find which frames were lost, enable out-of-sequence, capture, and read the last 6 bytes of the payload as the frame number ([article](https://support.excentis.com/knowledge/article/170)).

A port answers ping as soon as it has an address, which makes a five-line API script a quick reachability probe.

Hardware compatibility ([article](https://support.excentis.com/knowledge/article/175)):

- 3100 and 3200 accept only Intel SFP+ modules.
- 4100: problems with Twinax DAC cables and with 1 Gbit/s SFPs; check NBASE-T SFP+ connectivity before relying on it.
- Netgear M4200, M4300 and Allied Telesis x950 switches: copper SFP+ transceivers either do not work or do not negotiate below 10 Gbit/s.

BPF filters select traffic for triggers and captures. Useful forms: `ip6`, `udp port 80`, `tcp dst port 80`, `tcp[tcpflags] == tcp-syn`, `(tcp[tcpflags] & tcp-fin) > 0`. ECN-echo has no shorthand: `(tcp[tcpflags] & 0x40) > 0` ([cheatsheet](https://support.excentis.com/knowledge/article/186)).

### Coverage

Three of the four sites were crawled nearly completely; the Python reference was only partly readable, and the setup site not at all.

| Site | Pages read | Gaps |
| --- | --- | --- |
| [Knowledge base](https://support.excentis.com/knowledge/article/39) | 102 articles | About 70 article IDs need a login, errored or are gone. Release notes skipped on purpose. Many procedures exist only as screenshots. |
| [Test Framework](https://api.byteblower.com/test-framework/latest/) | 76 | None. Index and tag pages skipped as duplicates. |
| [Tcl API](https://api.byteblower.com/tcl) | 165, including all 127 class pages | Three source-file pages; the annotated higher-layer source. |
| [Python API](https://api.byteblower.com/python) | 5 doc pages, 15 example scripts | The reference page was readable only up to `ByteBlowerLicense`. Later classes are known by name and by example usage. |
| [OpenMetrics](https://api.byteblower.com/prometheus) | 1 | None |
| setup.byteblower.com | 0 | Blocks automated reading. Holds per-model installation manuals and downloads. |

Pages were read through a tool that paraphrases prose, so commands, names and numbers here are as extracted but wording is not verbatim. The JSON examples and the Python example code came through unmodified.

Places where the docs contradict themselves:

- TCP window scale range: 0 to 8 in the GUI article and Tcl reference, 0 to 12 in the TCP example article and the Test Framework schema.
- Maximum frame size: 10000 bytes in the link-speed article, 8192 in the Tcl `Frame` reference.
- Endpoint to Meeting Point port: one article says 9002, the firewall table says 9100.
- Test Framework `report_prefix` default: `byteblower` in the reference, `report` in the quick start.
- Test Framework manual IPv6 key: `prefix_length` in the text, `prefix` in the schema.
- Test Framework VLAN `priority`: described as 3 bits, schema maximum is 3.
- NIC firmware article: says firmware "8.64 or older" but ships package 8.40.
- Result history depth: "5 seconds" on one Tcl page, 6 samples on another.
- Python capability examples in the docs contain syntax errors.

Not documented anywhere that was reachable: DOCSIS ATP pass thresholds, the TR-398 expected-throughput table, units for RFC 2544 `tolerated_frame_loss` and `accuracy`, and the latency noise floor per model (published only as an image).
