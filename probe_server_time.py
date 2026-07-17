#!/usr/bin/env python3
"""Probe the PolyU booking server's clock via the HTTP Date response header.

Sends the make_book_submit request (or any URL) and compares the server's
Date header against the local clock to estimate:
  - round-trip time (RTT)
  - one-way latency (~RTT/2)
  - server clock offset relative to local clock

Use the result to tune network_offset_ms in book.py.

NOTE: the Date header has 1-second resolution, so a single sample only
bounds the offset to a ~1s window. Use --tick mode to detect the exact
moment the server's second rolls over, which narrows the estimate to
roughly one RTT.

WARNING: if the cookies below are still a valid session, the POST probe
will attempt a REAL booking submission. Expired cookies just produce a
login redirect, which works equally well for timing.
"""

import argparse
import time
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime

import requests

HKT = timezone(timedelta(hours=8))

URL = "https://www40.polyu.edu.hk/starspossfbstud/secure/ui_make_book/make_book_submit.do"

BOUNDARY = "----WebKitFormBoundaryISOB5ecJalTxD2xU"

HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "en-US,en;q=0.9,zh-TW;q=0.8,zh;q=0.7",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "Content-Type": f"multipart/form-data; boundary={BOUNDARY}",
    "Origin": "https://www40.polyu.edu.hk",
    "Referer": URL,
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36",
    "sec-ch-ua": '"Not;A=Brand";v="8", "Chromium";v="150", "Google Chrome";v="150"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
}

COOKIES = {
    "JSESSIONID": "0000q_7wCQQJtIRsYvg0cJMhMk-:1c7t2q6n6",
    "TS01b48e72": "0183ba1f88debddd140ee4f363cc53cf3a7d28b542d40919440b13c488cd960a371f8c15bcc0a8709a0b473189ecea9ab52aa8bbd5",
    "BIGipServerWWW40_HTTPS_POOL": "rd1220o00000000000000000000ffff9e84f80co8443",
    "TS01a87810": "0183ba1f88debddd140ee4f363cc53cf3a7d28b542d40919440b13c488cd960a371f8c15bcc0a8709a0b473189ecea9ab52aa8bbd5",
    "LtpaToken2": "y/vJeI8YctePqPtruW9r3CXTIb3B5m9X3On1/BdDKtTrSj5Ex8YaIWcbb8XODY39hnUB2JRP6uChC0e3YPCysw1b753Sb9Z5j3PIKnc3+4hhOEP98pHRbB7cKDe0b/p6LEFhWa+LDuWZ1UDR07BUHUrB84INltYAsHnsXc+nfCWnhbsrZh5kHW6O4sk5Q8bF1IoULG2TzL4lyYuOjm7iBiHL5ZdQ4wUNPb4zzNHVT2MtO8eC9c0k9halQbbGo+BKXJ1S11cFIoLoyUMbeLR7bgz/xw5623L4XRGwu8udOslS5miJurnWkk8wtdRSSLhVNhihUZqKNjNbiZYUB6ZkOgFoeFu5InomTCLh3xgLyiCkxdsVJS6YnPPdKB588+egdOBjjLg56uD1sG0QZJH54ADzfS64AKZJE7giC1ZoEP4fBF8g0AZ3IVxu7t8d/ziEZosBuyRxLvK+D7pKeUX4RDJjtWNKcJ/WGXRQl7CL/cUCiaSBaAvfG0ZPSOhX2hHHyS8gzPFgnNwHIBi8vKATJKKLYHRCmljAiUItuzg7ifXF9XM84KrRFL+hJuR9RflopLfcVWO3QXD1u6POZ1FR8zpCKe52tCbM9djJBa5O8WQaNoKUkTxhDBNzRTWyQOUj",
    "WASReqURL": "/poss/secure/home.do",
}

FORM_FIELDS = [
    ("dataSetId", "18"),
    ("boBookingType.id", "1"),
    ("boBookingType.value", "INDV"),
    ("boBookingMode.value", "SPORT"),
    ("boBookingMode.id", "1"),
    ("userRefNum", ""),
    ("fbUserId", "442240"),
    ("grpFacilityIds", ""),
    ("repeatOccurrence", "false"),
    ("startDate", ""),
    ("startTime", ""),
    ("endDate", ""),
    ("endTime", ""),
    ("dayOfWeeks", ""),
    ("functionsAvailable", "false"),
    ("brcdNo", ""),
    ("phone", ""),
    ("onBehalfOfFbUserId", ""),
    ("byPassQuota", "false"),
    ("byPassChrgSchm", "false"),
    ("byPassBookingDaysLimit", "false"),
    ("searchFormString", "fbUserId=442240&bookType=INDV&dataSetId=18&actvId=6&searchDate=&ctrId=1&facilityId="),
    ("extlPtyDclrId", ""),
    ("boMakeBookFacilities[0].ctrId", "1"),
    ("boMakeBookFacilities[0].centerName", "Shaw Sports Complex"),
    ("boMakeBookFacilities[0].facilityId", "1751"),
    ("boMakeBookFacilities[0].facilityName", "Volleyball Court No. 3"),
    ("boMakeBookFacilities[0].startDateTime", "25 Jul 2026 13:30"),
    ("boMakeBookFacilities[0].endDateTime", "25 Jul 2026 14:30"),
    ("declare", "on"),
    ("CSRFToken", "0b3c83c4-6687-4f9a-8ee3-5b63e58f1f2e"),
]


def build_body():
    parts = []
    for name, value in FORM_FIELDS:
        parts.append(
            f"--{BOUNDARY}\r\n"
            f'Content-Disposition: form-data; name="{name}"\r\n\r\n'
            f"{value}\r\n"
        )
    parts.append(f"--{BOUNDARY}--\r\n")
    return "".join(parts).encode()


def fmt_hkt(unix_ts):
    return datetime.fromtimestamp(unix_ts, HKT).strftime("%H:%M:%S.%f")[:-3]


def send_probe(session, url, method="POST", body=None):
    """Send one request; return (t_send, t_recv, server_date_unix, status)."""
    t_send = time.time()
    resp = session.request(
        method, url,
        data=body if method == "POST" else None,
        allow_redirects=False,
        timeout=15,
    )
    t_recv = time.time()
    date_hdr = resp.headers.get("Date")
    server_unix = parsedate_to_datetime(date_hdr).timestamp() if date_hdr else None
    return t_send, t_recv, server_unix, resp.status_code


def probe(session, url, method, body, samples, interval):
    """Simple mode: N samples, report RTT and coarse (±0.5s) clock offset."""
    print(f"{'#':>2}  {'sent (HKT)':>14}  {'recv (HKT)':>14}  {'RTT ms':>7}  "
          f"{'server Date (HKT)':>17}  {'offset ms':>9}  status")
    offsets, rtts = [], []
    for i in range(samples):
        t_send, t_recv, server_unix, status = send_probe(session, url, method, body)
        rtt_ms = (t_recv - t_send) * 1000
        rtts.append(rtt_ms)
        if server_unix is not None:
            # Date is generated server-side ~one-way latency after send.
            # Compare against midpoint of send/recv; +0.5s centers the
            # 1s-truncated Date value.
            midpoint = (t_send + t_recv) / 2
            offset_ms = (server_unix + 0.5 - midpoint) * 1000
            offsets.append(offset_ms)
            print(f"{i+1:>2}  {fmt_hkt(t_send):>14}  {fmt_hkt(t_recv):>14}  "
                  f"{rtt_ms:>7.1f}  {fmt_hkt(server_unix):>17}  "
                  f"{offset_ms:>+9.0f}  {status}")
        else:
            print(f"{i+1:>2}  {fmt_hkt(t_send):>14}  {fmt_hkt(t_recv):>14}  "
                  f"{rtt_ms:>7.1f}  {'<no Date header>':>17}  {'':>9}  {status}")
        if i < samples - 1:
            time.sleep(interval)

    print()
    if rtts:
        rtt_min = min(rtts)
        print(f"RTT: min {rtt_min:.1f} ms / avg {sum(rtts)/len(rtts):.1f} ms / max {max(rtts):.1f} ms")
        print(f"One-way latency estimate: ~{rtt_min/2:.0f} ms")
    if offsets:
        avg = sum(offsets) / len(offsets)
        print(f"Server clock offset (server - local): ~{avg:+.0f} ms  (±500 ms, Date header is 1s resolution)")
        # Server receives at server-time = local_send + one_way + offset,
        # so to arrive at server-time T, send (one_way + offset) ms before
        # the local clock reads T.
        print(f"\nSuggested network_offset_ms (send this early so the server receives at T=0):")
        print(f"  one-way latency only:            {rtt_min/2:.0f}")
        print(f"  latency + clock offset (coarse): {rtt_min/2 + avg:.0f}")
        print(f"\nFor a precise clock offset run with --tick.")


def probe_tick(session, url, method, body, duration):
    """Tick mode: poll rapidly and catch the moment the Date header's second
    rolls over. At the rollover, server time is exactly HH:MM:SS.000, so the
    offset is known to within ~RTT."""
    print(f"Polling for Date-header second rollovers for {duration:.0f}s ...")
    results = []
    prev_sec = None
    prev_t = None
    end = time.time() + duration
    while time.time() < end:
        t_send, t_recv, server_unix, status = send_probe(session, url, method, body)
        if server_unix is None:
            print("No Date header on response; cannot use tick mode.")
            return
        if prev_sec is not None and server_unix > prev_sec:
            # Server second rolled over somewhere between prev request's
            # processing time and this one's. Server hit server_unix.000
            # while local midpoint was between the two midpoints.
            mid_prev = prev_t
            mid_now = (t_send + t_recv) / 2
            est_local_at_tick = (mid_prev + mid_now) / 2
            offset_ms = (server_unix - est_local_at_tick) * 1000
            uncertainty_ms = (mid_now - mid_prev) * 1000 / 2
            results.append((offset_ms, uncertainty_ms))
            print(f"  tick -> server {fmt_hkt(server_unix)}  "
                  f"offset {offset_ms:+.0f} ms (±{uncertainty_ms:.0f} ms)")
        prev_sec = server_unix
        prev_t = (t_send + t_recv) / 2

    if not results:
        print("No rollover captured; try a longer --duration.")
        return
    best = min(results, key=lambda r: r[1])
    print(f"\nBest estimate — server clock offset (server - local): "
          f"{best[0]:+.0f} ms (±{best[1]:.0f} ms)")
    print("Positive offset = server clock is ahead of local clock.")
    print("network_offset_ms ≈ one-way latency + offset "
          "(take one-way latency from the simple-mode RTT numbers).")


def main():
    ap = argparse.ArgumentParser(description="Measure server receive time / clock offset")
    ap.add_argument("--url", default=URL, help="target URL (default: make_book_submit.do)")
    ap.add_argument("--get", action="store_true",
                    help="send a GET with no body instead of the booking POST (no side effects)")
    ap.add_argument("--samples", type=int, default=5, help="number of probes (default 5)")
    ap.add_argument("--interval", type=float, default=0.5, help="seconds between probes")
    ap.add_argument("--tick", action="store_true",
                    help="detect Date-header second rollover for a precise clock offset")
    ap.add_argument("--duration", type=float, default=5.0,
                    help="seconds to poll in --tick mode (default 5)")
    args = ap.parse_args()

    method = "GET" if args.get else "POST"
    body = None if args.get else build_body()

    session = requests.Session()
    session.headers.update(HEADERS)
    if args.get:
        session.headers.pop("Content-Type", None)
    session.cookies.update(COOKIES)

    # Warm-up request so TLS/connection setup doesn't pollute the first sample.
    try:
        send_probe(session, args.url, "GET" if args.get else method, body)
    except requests.RequestException as e:
        print(f"Warm-up request failed: {e}")
        return

    if args.tick:
        probe_tick(session, args.url, method, body, args.duration)
    else:
        probe(session, args.url, method, body, args.samples, args.interval)


if __name__ == "__main__":
    main()
