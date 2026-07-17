"""
Generic booking script with configurable sport and time slots
"""
import re
import os
import time
import platform
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from playwright.sync_api import sync_playwright
import requests
from bs4 import BeautifulSoup
import pytz
from booking_config import get_booking_config
from logger import setup_logging, restore_logging


class GenericBooking:
    """Generic booking system for PolyU facilities"""

    def __init__(self, user_id=None, output_dir=None, log_dir="logs"):
        self.playwright = None
        self.browser = None
        self.page = None
        self.csrf_token = None
        self.hkt = pytz.timezone('Asia/Hong_Kong')
        self.cookies = []
        self.session = requests.Session()  # For fast submission
        # Size the connection pool so N concurrent submission threads never
        # block waiting for a free keep-alive connection. Default urllib3
        # pool_maxsize is 10; with 20 threads half the requests would queue.
        _adapter = requests.adapters.HTTPAdapter(
            pool_connections=50, pool_maxsize=50
        )
        self.session.mount("https://", _adapter)
        self.session.mount("http://", _adapter)
        self.user_id = user_id  # For unique debug file naming
        self.username = None  # Will be set during login
        self.output_dir = output_dir  # Directory to save output files
        self.connection_warmed = False  # Track if connection is pre-warmed
        self.logger = None  # Will be set up when run() is called
        self.log_dir = log_dir  # Directory for log files

    def start_browser(self, headless=False):
        """Initialize Playwright browser"""
        print(f"[{self._get_hkt_time()}] 🌐 Starting browser...")
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=headless)

        # Create a new context with browser-like settings
        context = self.browser.new_context(
            user_agent=(
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/141.0.0.0 Safari/537.36'
            ),
            accept_downloads=False,
            locale='en-US',
            timezone_id='Asia/Hong_Kong'
        )

        self.page = context.new_page()
        print(f"[{self._get_hkt_time()}] ✅ Browser started")

    def close_browser(self):
        """Close Playwright browser"""
        if self.page:
            self.page.close()
            self.page = None
        if self.browser:
            self.browser.close()
            self.browser = None
        if self.playwright:
            self.playwright.stop()
            self.playwright = None
        print(f"[{self._get_hkt_time()}] 🚪 Browser closed")

    def login(self, username, password):
        """Login and establish authenticated session"""
        print(f"[{self._get_hkt_time()}] 🔐 Logging in as {username}...")

        # Store username for file naming
        self.username = username

        # Navigate to the correct login page
        login_url = "https://www40.polyu.edu.hk/poss/secure/login/loginhome.do"

        try:
            self.page.goto(login_url, wait_until='networkidle', timeout=30000)

            # Wait for the login form to be visible and ready
            print(f"[{self._get_hkt_time()}] ⏳ Waiting for login form to load...")
            self.page.wait_for_selector('input[name="j_username"]', state='visible', timeout=10000)
            time.sleep(1)  # Additional wait to ensure form is fully ready

            # Fill in login form
            self.page.fill('input[name="j_username"]', username)
            self.page.fill('input[name="j_password"]', password)

            # Wait a bit to ensure form is filled
            time.sleep(0.5)

            # Submit login form and wait for navigation
            print(f"[{self._get_hkt_time()}] 🔄 Submitting login form...")
            with self.page.expect_navigation(wait_until='networkidle', timeout=30000):
                self.page.click('button[type="submit"]')

            # Additional wait to ensure page is fully loaded
            time.sleep(1)

            # Check if login was successful
            current_url = self.page.url
            if "error" in current_url.lower() or "login" in current_url.lower():
                print(f"[{self._get_hkt_time()}] ❌ Login failed!")
                return False

            # Store cookies
            self.cookies = self.page.context.cookies()
            print(
                f"[{self._get_hkt_time()}] "
                f"✅ Login successful! ({len(self.cookies)} cookies)"
            )
            return True

        except Exception as e:
            print(f"[{self._get_hkt_time()}] ❌ Login error: {e}")
            return False

    def extract_csrf_token(self):
        """Extract CSRF token from booking page"""
        print(f"[{self._get_hkt_time()}] 🔑 Extracting CSRF token...")

        try:
            # Navigate to the correct booking page that contains CSRF token
            booking_url = (
                "https://www40.polyu.edu.hk/starspossfbstud/secure/"
                "ui_make_book/make_book.do"
            )
            print(f"[{self._get_hkt_time()}] 📄 Navigating to booking page...")

            # Navigate and wait for networkidle
            self.page.goto(booking_url, wait_until='networkidle', timeout=30000)

            # Wait for the page to fully load
            print(f"[{self._get_hkt_time()}] ⏳ Waiting for page to stabilize...")
            time.sleep(2)

            # Get page content
            page_content = self.page.content()

            # Debug: Save HTML to file for inspection (with username and fbUSERid)
            username_part = self.username if self.username else 'unknown'
            user_id_part = self.user_id if self.user_id else 'unknown'
            debug_filename = f'debug_csrf_page_{username_part}_{user_id_part}.html'
            if self.output_dir:
                debug_filename = os.path.join(self.output_dir, debug_filename)
            else:
                debug_filename = os.path.join(os.getcwd(), debug_filename)
            with open(debug_filename, 'w', encoding='utf-8') as f:
                f.write(page_content)
            print(f"[{self._get_hkt_time()}] 🔍 Saved HTML to {debug_filename}")
            print(f"[{self._get_hkt_time()}] 🔍 Current URL: {self.page.url}")
            print(f"[{self._get_hkt_time()}] 🔍 Page length: {len(page_content)} chars")

            # Try to extract CSRF token using Playwright's selector
            csrf_input = self.page.query_selector('input[name="CSRFToken"]')

            if csrf_input:
                csrf_value = csrf_input.get_attribute('value')
                if csrf_value:
                    self.csrf_token = csrf_value
                    print(
                        f"[{self._get_hkt_time()}] "
                        f"✅ CSRF Token: {self.csrf_token}"
                    )
                    return self.csrf_token

            # Fallback: Parse HTML with BeautifulSoup
            soup = BeautifulSoup(page_content, 'html.parser')

            # Try to find the CSRF input field
            csrf_input = soup.find('input', {'name': 'CSRFToken'})

            # Debug: Show all input fields
            all_inputs = soup.find_all('input')
            print(f"[{self._get_hkt_time()}] 🔍 Found {len(all_inputs)} input fields")
            for inp in all_inputs[:5]:  # Show first 5
                print(f"   - {inp.get('name', 'no-name')}: {inp.get('type', 'no-type')}")

            if csrf_input and csrf_input.get('value'):
                self.csrf_token = csrf_input['value']
                print(
                    f"[{self._get_hkt_time()}] "
                    f"✅ CSRF Token: {self.csrf_token}"
                )
                return self.csrf_token

            # Fallback regex patterns
            csrf_match = re.search(
                r'name=["\']?CSRFToken["\']?\s+value=["\']([a-f0-9\-]+)["\']',
                page_content,
                re.IGNORECASE
            )
            if csrf_match:
                self.csrf_token = csrf_match.group(1)
                print(
                    f"[{self._get_hkt_time()}] "
                    f"✅ CSRF Token (regex): {self.csrf_token}"
                )
                return self.csrf_token

            # Try UUID pattern
            csrf_match = re.search(
                r'value=["\']([a-f0-9\-]{36})["\']',
                page_content
            )
            if csrf_match:
                self.csrf_token = csrf_match.group(1)
                print(
                    f"[{self._get_hkt_time()}] "
                    f"✅ CSRF Token (UUID pattern): {self.csrf_token}"
                )
                return self.csrf_token

            print(f"[{self._get_hkt_time()}] ❌ CSRF token not found")
            return None

        except Exception as e:
            print(f"[{self._get_hkt_time()}] ❌ Error extracting CSRF token: {e}")
            return None

    def transfer_cookies_to_session(self):
        """Transfer cookies from Playwright to requests session for fast submission"""
        print(f"[{self._get_hkt_time()}] 🍪 Transferring cookies to requests session...")

        # Get cookies from Playwright
        playwright_cookies = self.page.context.cookies()

        # Convert and add to requests session
        for cookie in playwright_cookies:
            self.session.cookies.set(
                name=cookie['name'],
                value=cookie['value'],
                domain=cookie.get('domain', ''),
                path=cookie.get('path', '/')
            )

        # Set browser-like headers for requests session
        self.session.headers.update({
            'User-Agent': (
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/141.0.0.0 Safari/537.36'
            ),
            'Accept': (
                'text/html,application/xhtml+xml,application/xml;q=0.9,'
                'image/avif,image/webp,image/apng,*/*;q=0.8'
            ),
            'Accept-Language': 'en-US,en;q=0.9',
        })

        print(
            f"[{self._get_hkt_time()}] "
            f"✅ Transferred {len(playwright_cookies)} cookies"
        )

    def build_form_data(self, config):
        """
        Build form data based on sport type and configuration

        Args:
            config: Dict from get_booking_config()
        """
        sport = config['sport']

        # Base form data (common for all sports)
        form_data = {
            'dataSetId': config['dataset_id'],
            'boBookingType.id': '1',
            'boBookingType.value': 'INDV',
            'boBookingMode.value': 'SPORT',
            'boBookingMode.id': '1',
            'userRefNum': '',
            'fbUserId': config['user_id'],
            'grpFacilityIds': '',
            'repeatOccurrence': 'false',
            'startDate': '',
            'startTime': '',
            'endDate': '',
            'endTime': '',
            'dayOfWeeks': '',
            'functionsAvailable': 'false',
            'brcdNo': '',
            'phone': '',
            'onBehalfOfFbUserId': '',
            'byPassQuota': 'false',
            'byPassChrgSchm': 'false',
            'byPassBookingDaysLimit': 'false',
            'extlPtyDclrId': '',
            'boMakeBookFacilities[0].ctrId': config['center_id'],
            'boMakeBookFacilities[0].centerName': config['center_name'],
            'boMakeBookFacilities[0].facilityId': config['facility_id'],
            'boMakeBookFacilities[0].facilityName': config['facility_name'],
            'boMakeBookFacilities[0].startDateTime': (
                f"{config['date']} {config['start_time']}"
            ),
            'boMakeBookFacilities[0].endDateTime': (
                f"{config['date']} {config['end_time']}"
            ),
            'declare': 'on',
            'CSRFToken': self.csrf_token
        }

        # Sport-specific search string
        if sport == "volleyball":
            form_data['searchFormString'] = (
                f"fbUserId={config['user_id']}&bookType=INDV&"
                f"dataSetId={config['dataset_id']}&actvId={config['activity_id']}&"
                f"searchDate=&ctrId={config['center_id']}&facilityId="
            )
            
        elif sport == "table_tennis":
            form_data['searchFormString'] = (
                f"fbUserId={config['user_id']}&bookType=INDV&"
                f"dataSetId={config['dataset_id']}&actvId={config['activity_id']}&"
                f"searchDate=&ctrId={config['center_id']}&facilityId="
            )
        else:
            # Generic fallback
            form_data['searchFormString'] = (
                f"fbUserId={config['user_id']}&bookType=INDV&"
                f"dataSetId={config['dataset_id']}&actvId={config['activity_id']}&"
                f"searchDate={config['date'].replace(' ', '+')}&"
                f"ctrId={config['center_id']}&facilityId="
            )

        return form_data

    def submit_booking(self, config, num_requests=5, offset_ms_interval=0):
        """Submit booking request - sends N times in parallel with optional staggering"""
        mode = "simultaneous" if offset_ms_interval == 0 else f"staggered ({offset_ms_interval}ms intervals)"
        print(f"[{self._get_hkt_time()}] 🚀 SUBMITTING BOOKING REQUEST ({num_requests} TIMES, {mode})...")
        print(f"   Sport: {config['sport']}")
        print(f"   Facility: {config['facility_name']}")
        print(f"   Time: {config['start_time']} - {config['end_time']}")

        booking_url = (
            "https://www40.polyu.edu.hk/starspossfbstud/secure/"
            "ui_make_book/make_book_submit.do"
        )

        form_data = self.build_form_data(config)

        # Update headers for submission
        self.session.headers.update({
            'Origin': 'https://www40.polyu.edu.hk',
            'Referer': booking_url,
            'Content-Type': 'application/x-www-form-urlencoded',
        })

        # Extract username and user_id for filename
        username = config.get('username', 'unknown')
        fb_user_id = config.get('user_id', 'unknown')

        # Helper function to send a single request
        def send_request(request_num):
            """Send a single booking request and return response with metadata"""
            # Add staggered delay if offset_ms_interval is set
            if offset_ms_interval > 0:
                delay_seconds = (request_num - 1) * offset_ms_interval / 1000.0
                time.sleep(delay_seconds)

            print(f"[{self._get_hkt_time()}] 📤 Sending request #{request_num}/{num_requests}...")
            start_time = time.time()
            response = self.session.post(booking_url, data=form_data)
            elapsed = (time.time() - start_time) * 1000

            print(
                f"[{self._get_hkt_time()}] "
                f"📬 Response #{request_num} received in {elapsed:.0f}ms"
            )
            print(f"   Status: {response.status_code}")

            return {
                'request_num': request_num,
                'response': response,
                'elapsed_ms': elapsed,
                'timestamp': datetime.now(self.hkt).strftime('%Y%m%d_%H%M%S_%f')
            }

        # Send all N requests concurrently using ThreadPoolExecutor
        if offset_ms_interval > 0:
            print(f"[{self._get_hkt_time()}] 🚀 Sending {num_requests} requests with {offset_ms_interval}ms intervals...")
        else:
            print(f"[{self._get_hkt_time()}] 🚀 Sending all {num_requests} requests simultaneously...")
        responses = []
        with ThreadPoolExecutor(max_workers=num_requests) as executor:
            # Submit all N requests simultaneously
            futures = {executor.submit(send_request, i+1): i+1 for i in range(num_requests)}

            # Collect results as they complete
            for future in as_completed(futures):
                result = future.result()
                responses.append(result)

                # Save response to file for inspection (with username and fbUSERid)
                response_filename = (
                    f"booking_response_{username}_{fb_user_id}_"
                    f"{result['timestamp']}_req{result['request_num']}.html"
                )
                if self.output_dir:
                    response_filename = os.path.join(self.output_dir, response_filename)
                else:
                    response_filename = os.path.join(os.getcwd(), response_filename)
                with open(response_filename, 'w', encoding='utf-8') as f:
                    f.write(result['response'].text)
                print(f"[{self._get_hkt_time()}] 💾 Saved response to {response_filename}")

        # Sort responses by request number for consistency
        responses.sort(key=lambda x: x['request_num'])

        # Classify every response and report the best outcome across all N.
        # (A win can land on any request, not just the last one.)
        print(f"\n[{self._get_hkt_time()}] 📊 All {num_requests} requests sent!")

        won = None
        for item in responses:
            resp = item['response']
            outcome, reason = self._classify_response(resp)
            print(
                f"[{self._get_hkt_time()}] "
                f"   req#{item['request_num']}: {outcome.upper()} — {reason}"
            )
            if outcome == 'success':
                won = item

        if won is not None:
            print(f"[{self._get_hkt_time()}] ✅ BOOKING SUCCESSFUL! (req#{won['request_num']})")
            return True

        print(f"[{self._get_hkt_time()}] ❌ BOOKING FAILED — no request won the slot")
        return responses[-1]['response']

    @staticmethod
    def _classify_response(response):
        """Classify a booking response as success / failed / unknown.

        Returns (outcome, reason). Detection is failure-first because the page
        always embeds the JS string `success: function(response){...}`, so a
        naive `"success" in text` check is always true and is NOT a real signal.
        """
        if response.status_code != 200:
            return 'failed', f"HTTP {response.status_code}"

        text = response.text
        low = text.lower()

        # Known failure banners observed in real responses (alert-danger).
        failure_signals = [
            ("reserved by others", "timeslot taken by someone else (lost the race)"),
            ("failed to reserve", "server rejected the reservation"),
            ("is occupied from", "facility already occupied for that slot"),
            ("personal booking in a day", "daily booking quota exceeded"),
            ("maximum", "booking limit exceeded"),
            ("exceed", "quota / booking limit exceeded"),
            ("not allow", "booking not allowed"),
            ("invalid", "invalid request / session"),
        ]
        for needle, reason in failure_signals:
            if needle in low:
                # Pull the actual banner text when available for the log.
                m = re.search(r'alert-danger[^>]*>\s*([^<]{1,160})', text)
                detail = m.group(1).strip() if m else ""
                return 'failed', detail or reason

        # Positive confirmation banner (alert-success) => real win.
        if 'alert-success' in low or 'booking is successful' in low \
                or 'successfully' in low:
            m = re.search(r'alert-success[^>]*>\s*([^<]{1,160})', text)
            detail = m.group(1).strip() if m else ""
            return 'success', detail or "confirmation banner present"

        # 200 with no banner is the booking form re-rendered: no booking was
        # created (no confirmation, no error). Not a win — flag for review.
        return 'unknown', "form re-rendered, no booking created (verify)"

    def wait_until_one_hour_before(self, target_time_hkt):
        """Initial wait - countdown until ~1 hour before target time"""
        one_hour_before = target_time_hkt - timedelta(hours=1)

        while True:
            now_hkt = datetime.now(self.hkt)
            remaining = (one_hour_before - now_hkt).total_seconds()

            if remaining <= 0:
                break

            if remaining > 2400:  # More than 40 minutes
                print(
                    f"[{self._get_hkt_time()}] "
                    f"💤 Initial countdown: {int(remaining/60)} minutes until preparation phase"
                )
                time.sleep(1200)  # Sleep 20 minutes at a time
            elif remaining > 1200:  # 20-40 minutes
                print(
                    f"[{self._get_hkt_time()}] "
                    f"💤 Initial countdown: {int(remaining/60)} minutes until preparation phase"
                )
                time.sleep(240)  # Sleep 4 minutes at a time
            elif remaining > 300:  # 5-20 minutes
                print(
                    f"[{self._get_hkt_time()}] "
                    f"💤 Initial countdown: {int(remaining/60)} minutes until preparation phase"
                )
                time.sleep(60)  # Sleep 1 minute at a time
            elif remaining > 60:  # 1-5 minutes
                print(
                    f"[{self._get_hkt_time()}] "
                    f"💤 Initial countdown: {int(remaining)}s until preparation phase"
                )
                time.sleep(10)  # Sleep 10 seconds at a time
            else:
                print(
                    f"[{self._get_hkt_time()}] "
                    f"⏳ {remaining:.1f}s until preparation phase..."
                )
                time.sleep(5)

        print(f"[{self._get_hkt_time()}] ⚡ ONE HOUR COUNTDOWN BEGINS!")

    def wait_until_browser_start(self, browser_start_time_hkt):
        """Second wait - countdown until browser start time (10 min before target)"""
        while True:
            now_hkt = datetime.now(self.hkt)
            remaining = (browser_start_time_hkt - now_hkt).total_seconds()

            if remaining <= 0:
                break

            if remaining > 2400:  # More than 40 minutes
                print(
                    f"[{self._get_hkt_time()}] "
                    f"💤 Waiting... {int(remaining/60)} minutes until browser start"
                )
                time.sleep(1200)  # Sleep 20 minutes at a time
            elif remaining > 1200:  # 20-40 minutes
                print(
                    f"[{self._get_hkt_time()}] "
                    f"💤 Waiting... {int(remaining/60)} minutes until browser start"
                )
                time.sleep(240)  # Sleep 4 minutes at a time
            elif remaining > 300:  # 5-20 minutes
                print(
                    f"[{self._get_hkt_time()}] "
                    f"💤 Waiting... {int(remaining/60)} minutes until browser start"
                )
                time.sleep(60)  # Sleep 1 minute at a time
            elif remaining > 60:  # 1-5 minutes
                print(
                    f"[{self._get_hkt_time()}] "
                    f"💤 Waiting... {int(remaining)}s until browser start"
                )
                time.sleep(10)  # Sleep 10 seconds at a time
            elif remaining > 10:
                print(
                    f"[{self._get_hkt_time()}] "
                    f"⏳ {remaining:.1f}s until browser start..."
                )
                time.sleep(5)
            else:
                print(
                    f"[{self._get_hkt_time()}] "
                    f"⏰ {remaining:.1f}s until browser start..."
                )
                time.sleep(1)

        print(f"[{self._get_hkt_time()}] ⚡ BROWSER START TIME REACHED!")

    def boost_process_priority(self):
        """Boost process priority for better timing accuracy"""
        try:
            system = platform.system()
            if system == "Windows":
                import psutil
                p = psutil.Process(os.getpid())
                p.nice(psutil.HIGH_PRIORITY_CLASS)
                print(f"[{self._get_hkt_time()}] ⚡ Process priority boosted (Windows)")
            elif system == "Darwin":  # macOS
                os.nice(-10)
                print(f"[{self._get_hkt_time()}] ⚡ Process priority boosted (macOS)")
            elif system == "Linux":
                os.nice(-10)
                print(f"[{self._get_hkt_time()}] ⚡ Process priority boosted (Linux)")
        except (ImportError, PermissionError, OSError) as e:
            print(f"[{self._get_hkt_time()}] ⚠️  Could not boost priority: {e}")
            print(f"[{self._get_hkt_time()}] 💡 Consider running as admin for better accuracy")

    def warm_connection(self, url):
        """Pre-warm network connection to reduce first-request latency"""
        if self.connection_warmed:
            return

        try:
            print(f"[{self._get_hkt_time()}] 🔥 Warming up network connection...")
            # Make a quick HEAD request to establish TCP connection
            self.session.head(url, timeout=5)
            self.connection_warmed = True
            print(f"[{self._get_hkt_time()}] ✅ Connection warmed and ready")
        except Exception as e:
            print(f"[{self._get_hkt_time()}] ⚠️  Connection warm-up failed: {e}")

    def measure_server_offset(self, url, max_seconds=4.0):
        """Measure the offset to fire with, against the *booking server's* clock.

        What matters for winning the race is not how close our PC clock is to
        UTC, but (a) the network latency to the PolyU server and (b) how far
        the server's own clock differs from ours. Both are read directly from
        the HTTP ``Date`` response header of the warmed session.

        The server opens the slot at T on *its* clock, so to have our request
        arrive exactly then we must send it ``one_way_latency + server_offset``
        before our local clock reads T. That sum is returned in milliseconds.

        Returns the suggested offset in ms, or ``None`` if it could not be
        measured (caller should then fall back to the static configured offset).
        """
        from email.utils import parsedate_to_datetime

        print(f"[{self._get_hkt_time()}] 🛰️  Probing server clock via HTTP Date header...")

        def sample():
            t0 = time.time()
            try:
                resp = self.session.get(url, allow_redirects=False, timeout=5)
            except Exception:
                return None
            t1 = time.time()
            date_hdr = resp.headers.get("Date")
            if not date_hdr:
                return None
            return t0, t1, parsedate_to_datetime(date_hdr).timestamp()

        min_rtt = None
        best = None       # (server_offset_ms, uncertainty_ms) at a second-rollover
        prev = None       # (local_midpoint, server_second)
        deadline = time.time() + max_seconds
        while time.time() < deadline:
            s = sample()
            if s is None:
                break
            t0, t1, server_sec = s
            rtt_ms = (t1 - t0) * 1000
            if min_rtt is None or rtt_ms < min_rtt:
                min_rtt = rtt_ms
            mid = (t0 + t1) / 2
            # Detect the moment the server's Date second ticks over. At that
            # instant server time is exactly HH:MM:SS.000, pinning the offset
            # to within roughly the gap between the two straddling samples.
            if prev is not None and server_sec > prev[1]:
                est_local_at_tick = (prev[0] + mid) / 2
                offset_ms = (server_sec - est_local_at_tick) * 1000
                uncertainty_ms = (mid - prev[0]) * 1000 / 2
                if best is None or uncertainty_ms < best[1]:
                    best = (offset_ms, uncertainty_ms)
            prev = (mid, server_sec)
            time.sleep(0.01)  # ~10ms between probes: gentle but catches rollover

        if min_rtt is None:
            print(f"[{self._get_hkt_time()}] ⚠️  Server clock probe failed (no Date header)")
            return None

        one_way = min_rtt / 2
        if best is not None:
            server_offset, unc = best
            suggested = one_way + server_offset
            print(
                f"[{self._get_hkt_time()}] 📡 RTT min {min_rtt:.0f}ms "
                f"(one-way ~{one_way:.0f}ms) | server clock {server_offset:+.0f}ms "
                f"(±{unc:.0f}ms) vs local"
            )
            print(f"[{self._get_hkt_time()}] 🎯 Suggested dynamic offset: {suggested:.0f}ms early")
            return suggested

        # No rollover captured — can only compensate for latency, not clock skew.
        print(
            f"[{self._get_hkt_time()}] ⚠️  No Date rollover captured; "
            f"compensating one-way latency only (~{one_way:.0f}ms)"
        )
        return one_way

    def wait_until_exact_time(self, target_time_hkt, offset_ms=0):
        """Wait until exact target time in HKT with high-resolution timing"""
        adjusted_target = target_time_hkt - timedelta(milliseconds=offset_ms)

        while True:
            now_hkt = datetime.now(self.hkt)
            remaining = (adjusted_target - now_hkt).total_seconds()

            if remaining <= 0:
                break

            if remaining > 60:
                print(
                    f"[{self._get_hkt_time()}] "
                    f"⏳ Waiting... {int(remaining)}s until submission"
                )
                time.sleep(10)
            elif remaining > 10:
                print(
                    f"[{self._get_hkt_time()}] "
                    f"⏳ {remaining:.1f}s remaining..."
                )
                time.sleep(1)
            elif remaining > 1:
                print(
                    f"[{self._get_hkt_time()}] "
                    f"⏰ {remaining:.2f}s..."
                )
                time.sleep(0.5)
            elif remaining > 0.1:
                # High-resolution waiting in final 1 second
                print(f"[{self._get_hkt_time()}] 🎯 Final countdown...")
                while True:
                    now_hkt = datetime.now(self.hkt)
                    remaining_ms = (adjusted_target - now_hkt).total_seconds() * 1000

                    if remaining_ms <= 0:
                        break

                    # Adaptive sleep based on remaining time
                    if remaining_ms > 100:
                        time.sleep(0.01)  # 10ms sleep
                    elif remaining_ms > 10:
                        time.sleep(0.001)  # 1ms sleep
                    else:
                        # Busy-wait for final 10ms for maximum accuracy
                        pass
                break
            else:
                # Final busy-wait
                while datetime.now(self.hkt) < adjusted_target:
                    pass
                break

        actual_time = datetime.now(self.hkt)
        timing_error_ms = (actual_time - target_time_hkt).total_seconds() * 1000
        print(f"[{self._get_hkt_time()}] ⚡ TIME REACHED! FIRING NOW!")
        print(f"[{self._get_hkt_time()}] 📊 Timing accuracy: {timing_error_ms:+.1f}ms from target")

    def _get_hkt_time(self):
        """Get current HKT time as formatted string"""
        return datetime.now(self.hkt).strftime('%H:%M:%S.%f')[:-3]

    def run(
        self,
        sport,
        time_slot,
        booking_date,
        target_time_str,
        network_offset_ms=200,
        headless=False,
        username=None,
        password=None,
        user_id=None,
        custom_start_time=None,
        custom_end_time=None,
        pre_trigger_minutes=15,
        num_requests=5,
        offset_ms_interval=0,
        dynamic_offset=True
    ):
        """
        Complete workflow: wait, login (at pre-trigger time), wait, submit at exact time

        Args:
            sport: "volleyball" or "table_tennis"
            time_slot: Time slot key (e.g., "morning_early")
            booking_date: Date string (e.g., "25 Oct 2025")
            target_time_str: Target submission time (e.g., "08:30:00")
            network_offset_ms: Send request this many ms early (default 200ms)
            headless: Run browser in headless mode (default True)
            username: Optional custom username (overrides config)
            password: Optional custom password (overrides config)
            user_id: Optional custom user_id (overrides config)
            custom_start_time: Optional custom start time (overrides config)
            custom_end_time: Optional custom end time (overrides config)
            pre_trigger_minutes: Minutes before target time to start browser and get token (default 15)
            num_requests: Number of parallel requests to spam (default 5)
            offset_ms_interval: Interval in milliseconds between each request (default 0, simultaneous)
        """
        # Setup logging first
        self.logger = setup_logging(log_dir=self.log_dir, user_id=self.user_id)

        print("="*70)
        print("🎯 GENERIC BOOKING SYSTEM - HIGH ACCURACY MODE")
        print("="*70)

        # Get configuration with custom times if provided
        config = get_booking_config(
            sport,
            time_slot,
            booking_date,
            custom_start_time=custom_start_time,
            custom_end_time=custom_end_time
        )

        # Override with custom credentials if provided
        if username:
            config['username'] = username
        if password:
            config['password'] = password
        if user_id:
            config['user_id'] = user_id

        # Display slot info
        slot_display = time_slot if time_slot else "custom"
        print(f"Sport: {sport.upper()}")
        print(f"Time Slot: {slot_display} ({config['start_time']}-{config['end_time']})")
        print(f"Date: {booking_date}")
        print(f"Log file: {self.logger.log_path}")
        print("="*70 + "\n")

        try:
            # Step 0: System optimization checks
            print("="*70)
            print("🔧 SYSTEM OPTIMIZATION")
            print("="*70)

            # Note: server clock offset is measured live in STAGE 3 (once the
            # session is warmed), not against UTC here — see measure_server_offset.

            # Boost process priority
            self.boost_process_priority()

            print("="*70 + "\n")

            # Step 1: Parse target time
            today = datetime.now(self.hkt).date()
            target_datetime = datetime.strptime(
                f"{today} {target_time_str}",
                "%Y-%m-%d %H:%M:%S"
            )
            target_datetime = self.hkt.localize(target_datetime)

            # Calculate browser start time (pre_trigger_minutes before target)
            browser_start_time = target_datetime - timedelta(minutes=pre_trigger_minutes)

            # Calculate when to start countdown (1 hour before target)
            one_hour_before = target_datetime - timedelta(hours=1)

            now_hkt = datetime.now(self.hkt)

            print(f"⏰ Current time: {self._get_hkt_time()} HKT")
            print(f"⏰ Target time: {target_datetime.strftime('%H:%M:%S')} HKT")
            print(f"⏰ Preparation phase starts: {one_hour_before.strftime('%H:%M:%S')} HKT (T-60 min)")
            print(f"⏰ Browser start time: {browser_start_time.strftime('%H:%M:%S')} HKT (T-{pre_trigger_minutes} min)")
            print("="*70 + "\n")

            # Step 2: Initial countdown - wait until 1 hour before target
            if now_hkt < one_hour_before:
                print("="*70)
                print("📅 STAGE 1: INITIAL COUNTDOWN")
                print("="*70)
                self.wait_until_one_hour_before(target_datetime)
                print("\n" + "="*70)
                print("⏰ STAGE 2: PREPARATION PHASE ACTIVATED")
                print("="*70 + "\n")
            else:
                print("="*70)
                print("⏰ Already within 1 hour of target - skipping initial countdown")
                print("="*70 + "\n")

            # Step 3: Second countdown - wait until browser start time
            if now_hkt < browser_start_time:
                self.wait_until_browser_start(browser_start_time)

            # Step 4: Start browser and login
            print("\n" + "="*70)
            print(f"🌐 STARTING BROWSER AND LOGIN")
            print("="*70 + "\n")
            self.start_browser(headless=headless)

            # Step 5: Login
            if not self.login(config['username'], config['password']):
                print("❌ Login failed. Aborting.")
                return False

            # Step 6: Extract CSRF token
            if not self.extract_csrf_token():
                print("❌ Failed to get CSRF token. Aborting.")
                return False

            # Step 7: Transfer cookies to requests session for fast submission
            self.transfer_cookies_to_session()

            # Step 8: Pre-warm network connection
            booking_url = (
                "https://www40.polyu.edu.hk/starspossfbstud/secure/"
                "ui_make_book/make_book_submit.do"
            )
            self.warm_connection(booking_url)

            # Step 8b: Measure the live offset against the server's own clock
            # and use it in place of the static configured value when available.
            offset_source = "configured (static)"
            if dynamic_offset:
                measured = self.measure_server_offset(booking_url)
                if measured is not None and -2000 <= measured <= 5000:
                    network_offset_ms = measured
                    offset_source = "measured (server clock)"
                else:
                    print(
                        f"[{self._get_hkt_time()}] ⚠️  Keeping static offset "
                        f"{network_offset_ms}ms (measurement unavailable/out of range)"
                    )

            # Step 9: Browser stays open for inspection (never closes)

            print("\n" + "="*70)
            print("✅ STAGE 3: READY TO BOOK!")
            print("="*70)
            print(
                f"   Target: {target_datetime.strftime('%Y-%m-%d %H:%M:%S %Z')}"
            )
            print(f"   Network offset: {network_offset_ms:.0f}ms early [{offset_source}]")
            print(f"   Facility: {config['facility_name']}")
            print(f"   Time: {config['start_time']} - {config['end_time']}")
            print("="*70 + "\n")

            # Step 10: Final countdown - wait until exact submission time
            self.wait_until_exact_time(target_datetime, network_offset_ms)

            # Step 11: Submit (using fast requests session)
            response = self.submit_booking(config, num_requests=num_requests, offset_ms_interval=offset_ms_interval)

            print("\n" + "="*70)
            print("📋 BOOKING PROCESS COMPLETE")
            print("="*70)

            return response

        except Exception as e:
            print(f"[{self._get_hkt_time()}] ❌ Error during booking: {e}")
            return False

        finally:
            # Browser stays open for manual inspection (never closes)
            print(f"\n[{self._get_hkt_time()}] 🌐 Browser left open for inspection")
            print(f"[{self._get_hkt_time()}] ⏸️  Process will stay alive to keep browser open...")
            print(f"[{self._get_hkt_time()}] 💡 Press Ctrl+C to close all browsers and exit")

            # Keep process alive indefinitely to prevent browser from closing
            try:
                while True:
                    time.sleep(60)  # Sleep forever
            except KeyboardInterrupt:
                print(f"\n[{self._get_hkt_time()}] 🛑 Shutting down...")
                self.close_browser()
            finally:
                # Close logging before exiting
                if self.logger:
                    restore_logging(self.logger)


# Example usage
if __name__ == "__main__":
    # Quick configuration
    SPORT = "volleyball"          # "volleyball" or "table_tennis"
    TIME_SLOT = "morning_early"   # "morning_early", "morning_mid", etc.
    BOOKING_DATE = "25 Oct 2025"
    TARGET_TIME = "08:30:00"      # Exact submission time (HKT)
    NETWORK_OFFSET_MS = 200       # Fallback offset if the live probe fails
    DYNAMIC_OFFSET = True         # Measure offset vs server clock right before firing

    # Run booking
    booking = GenericBooking()
    booking.run(
        sport=SPORT,
        time_slot=TIME_SLOT,
        booking_date=BOOKING_DATE,
        target_time_str=TARGET_TIME,
        network_offset_ms=NETWORK_OFFSET_MS,
        dynamic_offset=DYNAMIC_OFFSET
    )
