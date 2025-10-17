"""
Generic booking script with configurable sport and time slots
"""
from playwright.sync_api import sync_playwright
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta
import time
import pytz
from booking_config import get_booking_config


class GenericBooking:
    """Generic booking system for PolyU facilities"""

    def __init__(self):
        self.playwright = None
        self.browser = None
        self.page = None
        self.csrf_token = None
        self.hkt = pytz.timezone('Asia/Hong_Kong')
        self.cookies = []
        self.session = requests.Session()  # For fast submission

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
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        print(f"[{self._get_hkt_time()}] 🚪 Browser closed")

    def login(self, username, password):
        """Login and establish authenticated session"""
        print(f"[{self._get_hkt_time()}] 🔐 Logging in as {username}...")

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

            # Debug: Save HTML to file for inspection
            with open('debug_csrf_page.html', 'w', encoding='utf-8') as f:
                f.write(page_content)
            print(f"[{self._get_hkt_time()}] 🔍 Saved HTML to debug_csrf_page.html")
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
                f"searchDate={config['date'].replace(' ', '+')}&"
                f"ctrId={config['center_id']}&facilityId="
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

    def submit_booking(self, config):
        """Submit booking request"""
        print(f"[{self._get_hkt_time()}] 🚀 SUBMITTING BOOKING REQUEST...")
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

        # Send request
        start_time = time.time()
        response = self.session.post(booking_url, data=form_data)
        elapsed = (time.time() - start_time) * 1000

        print(
            f"[{self._get_hkt_time()}] "
            f"📬 Response received in {elapsed:.0f}ms"
        )
        print(f"   Status: {response.status_code}")

        # Check response
        if response.status_code == 200:
            if "success" in response.text.lower():
                print(f"[{self._get_hkt_time()}] ✅ BOOKING SUCCESSFUL!")
                return True
            if "error" in response.text.lower():
                print(f"[{self._get_hkt_time()}] ⚠️  Possible error in response")
            else:
                print(f"[{self._get_hkt_time()}] ℹ️  Booking submitted")

        return response

    def wait_until_exact_time(self, target_time_hkt, offset_ms=0):
        """Wait until exact target time in HKT"""
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
            else:
                print(f"[{self._get_hkt_time()}] 🎯 Final countdown...")
                while datetime.now(self.hkt) < adjusted_target:
                    time.sleep(0.001)
                break

        print(f"[{self._get_hkt_time()}] ⚡ TIME REACHED! FIRING NOW!")

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
        headless=False
    ):
        """
        Complete workflow: login, wait, submit at exact time

        Args:
            sport: "volleyball" or "table_tennis"
            time_slot: Time slot key (e.g., "morning_early")
            booking_date: Date string (e.g., "25 Oct 2025")
            target_time_str: Target submission time (e.g., "08:30:00")
            network_offset_ms: Send request this many ms early (default 200ms)
            headless: Run browser in headless mode (default True)
        """
        print("="*70)
        print("🎯 GENERIC BOOKING SYSTEM")
        print("="*70)

        # Get configuration
        config = get_booking_config(sport, time_slot, booking_date)

        print(f"Sport: {sport.upper()}")
        print(f"Time Slot: {time_slot} ({config['start_time']}-{config['end_time']})")
        print(f"Date: {booking_date}")
        print("="*70 + "\n")

        try:
            # Step 0: Start browser
            self.start_browser(headless=headless)

            # Step 1: Login
            if not self.login(config['username'], config['password']):
                print("❌ Login failed. Aborting.")
                return False

            # Step 2: Extract CSRF token
            if not self.extract_csrf_token():
                print("❌ Failed to get CSRF token. Aborting.")
                return False

            # Step 3: Transfer cookies to requests session for fast submission
            self.transfer_cookies_to_session()

            # Step 4: Close browser (we have cookies and CSRF token now)
            print(f"[{self._get_hkt_time()}] 🔒 Closing browser (keeping session)...")
            self.close_browser()

            # Step 5: Parse target time
            today = datetime.now(self.hkt).date()
            target_datetime = datetime.strptime(
                f"{today} {target_time_str}",
                "%Y-%m-%d %H:%M:%S"
            )
            target_datetime = self.hkt.localize(target_datetime)

            print("\n" + "="*70)
            print(f"✅ READY TO BOOK!")
            print(
                f"   Target: {target_datetime.strftime('%Y-%m-%d %H:%M:%S %Z')}"
            )
            print(f"   Network offset: {network_offset_ms}ms early")
            print(f"   Facility: {config['facility_name']}")
            print(f"   Time: {config['start_time']} - {config['end_time']}")
            print("="*70 + "\n")

            # Step 6: Wait
            self.wait_until_exact_time(target_datetime, network_offset_ms)

            # Step 7: Submit (using fast requests session)
            response = self.submit_booking(config)

            print("\n" + "="*70)
            print("📋 BOOKING PROCESS COMPLETE")
            print("="*70)

            return response

        except Exception as e:
            print(f"[{self._get_hkt_time()}] ❌ Error during booking: {e}")
            return False

        finally:
            # Ensure browser is closed
            if self.browser:
                self.close_browser()


# Example usage
if __name__ == "__main__":
    # Quick configuration
    SPORT = "volleyball"          # "volleyball" or "table_tennis"
    TIME_SLOT = "morning_early"   # "morning_early", "morning_mid", etc.
    BOOKING_DATE = "25 Oct 2025"
    TARGET_TIME = "08:30:00"      # Exact submission time (HKT)
    NETWORK_OFFSET_MS = 200       # Send 200ms early

    # Run booking
    booking = GenericBooking()
    booking.run(
        sport=SPORT,
        time_slot=TIME_SLOT,
        booking_date=BOOKING_DATE,
        target_time_str=TARGET_TIME,
        network_offset_ms=NETWORK_OFFSET_MS
    )
