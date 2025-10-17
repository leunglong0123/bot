"""
Scheduled booking script for PolyU facilities
Logs in ahead of time and submits booking at exact target time
"""
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta
import time
import pytz


class ScheduledBooking:
    def __init__(self):
        self.session = requests.Session()
        self.csrf_token = None
        self.hkt = pytz.timezone('Asia/Hong_Kong')

        # Set browser-like headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                         'AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/141.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,'
                     'image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
        })

    def login(self, username, password):
        """Login and establish authenticated session"""
        print(f"[{self._get_hkt_time()}] 🔐 Logging in...")

        # Initial request to establish cookies
        login_url = (
            "https://www40.polyu.edu.hk/starspossfbstud/secure/"
            "ui_cncl_book/cncl_book_submit.do"
        )
        self.session.get(login_url)

        # Submit login credentials
        login_submit_url = (
            "https://www40.polyu.edu.hk/starspossfbstud/j_security_check"
        )
        login_data = {
            'j_username': username,
            'j_password': password,
            'buttonAction': 'loginButton'
        }

        response = self.session.post(
            login_submit_url,
            data=login_data,
            allow_redirects=True
        )

        # Verify login success
        if "error" in response.url.lower() or "login" in response.url.lower():
            print(f"[{self._get_hkt_time()}] ❌ Login failed!")
            return False

        print(f"[{self._get_hkt_time()}] ✅ Login successful!")
        print(f"   Session cookies: {len(self.session.cookies)} cookies stored")
        return True

    def extract_csrf_token(self):
        """Extract CSRF token from booking page"""
        print(f"[{self._get_hkt_time()}] 🔑 Extracting CSRF token...")

        booking_url = (
            "https://www40.polyu.edu.hk/starspossfbstud/secure/"
            "ui_make_book/make_book_submit.do"
        )
        response = self.session.get(booking_url)

        if response.status_code != 200:
            print(
                f"[{self._get_hkt_time()}] "
                f"❌ Failed to access booking page: {response.status_code}"
            )
            return None

        # Parse HTML for CSRF token
        soup = BeautifulSoup(response.text, 'html.parser')
        csrf_input = soup.find('input', {'name': 'CSRFToken'})

        if csrf_input and csrf_input.get('value'):
            self.csrf_token = csrf_input['value']
            print(
                f"[{self._get_hkt_time()}] "
                f"✅ CSRF Token: {self.csrf_token}"
            )
            return self.csrf_token

        # Fallback: regex search
        csrf_match = re.search(
            r'CSRFToken["\s:]+([a-f0-9\-]+)',
            response.text
        )
        if csrf_match:
            self.csrf_token = csrf_match.group(1)
            print(
                f"[{self._get_hkt_time()}] "
                f"✅ CSRF Token: {self.csrf_token}"
            )
            return self.csrf_token

        print(f"[{self._get_hkt_time()}] ❌ CSRF token not found")
        return None

    def prepare_booking_request(self, facility_data):
        """
        Prepare booking form data based on your curl request

        facility_data example:
        {
            'facility_id': '1751',
            'facility_name': 'Volleyball Court No. 3',
            'start_datetime': '25 Oct 2025 08:30',
            'end_datetime': '25 Oct 2025 09:30',
            'fb_user_id': '442240'
        }
        """
        # Build multipart form data matching your curl request
        form_data = {
            'dataSetId': '18',
            'boBookingType.id': '1',
            'boBookingType.value': 'INDV',
            'boBookingMode.value': 'SPORT',
            'boBookingMode.id': '1',
            'userRefNum': '',
            'fbUserId': facility_data.get('fb_user_id', '442240'),
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
            'searchFormString': (
                f"fbUserId={facility_data.get('fb_user_id', '442240')}"
                f"&bookType=INDV&dataSetId=18&actvId=6"
                f"&searchDate=25+Oct+2025&ctrId=1&facilityId="
            ),
            'extlPtyDclrId': '',
            'boMakeBookFacilities[0].ctrId': '1',
            'boMakeBookFacilities[0].centerName': 'Shaw Sports Complex',
            'boMakeBookFacilities[0].facilityId': facility_data['facility_id'],
            'boMakeBookFacilities[0].facilityName': facility_data['facility_name'],
            'boMakeBookFacilities[0].startDateTime': facility_data['start_datetime'],
            'boMakeBookFacilities[0].endDateTime': facility_data['end_datetime'],
            'declare': 'on',
            'CSRFToken': self.csrf_token
        }

        return form_data

    def submit_booking(self, facility_data):
        """Submit the booking request"""
        print(f"[{self._get_hkt_time()}] 🚀 SUBMITTING BOOKING REQUEST...")

        booking_url = (
            "https://www40.polyu.edu.hk/starspossfbstud/secure/"
            "ui_make_book/make_book_submit.do"
        )

        form_data = self.prepare_booking_request(facility_data)

        # Update headers for form submission
        self.session.headers.update({
            'Origin': 'https://www40.polyu.edu.hk',
            'Referer': booking_url,
            'Content-Type': 'application/x-www-form-urlencoded',
        })

        # Send the request
        start_time = time.time()
        response = self.session.post(booking_url, data=form_data)
        elapsed = (time.time() - start_time) * 1000  # Convert to ms

        print(
            f"[{self._get_hkt_time()}] "
            f"📬 Response received in {elapsed:.0f}ms"
        )
        print(f"   Status code: {response.status_code}")
        print(f"   Final URL: {response.url}")

        # Check for success indicators in response
        if response.status_code == 200:
            if "success" in response.text.lower():
                print(f"[{self._get_hkt_time()}] ✅ BOOKING SUCCESSFUL!")
                return True
            elif "error" in response.text.lower():
                print(f"[{self._get_hkt_time()}] ⚠️  Possible error in response")
                # You can parse the response to get specific error message
            else:
                print(f"[{self._get_hkt_time()}] ℹ️  Booking submitted")

        return response

    def wait_until_exact_time(self, target_time_hkt, offset_ms=0):
        """
        Wait until exact target time in HKT

        Args:
            target_time_hkt: datetime object in HKT timezone
            offset_ms: milliseconds to subtract (for network latency compensation)
        """
        # Adjust for network latency (send slightly early)
        adjusted_target = target_time_hkt - timedelta(milliseconds=offset_ms)

        while True:
            now_hkt = datetime.now(self.hkt)
            remaining = (adjusted_target - now_hkt).total_seconds()

            if remaining <= 0:
                break

            if remaining > 60:
                # More than 1 minute away - show countdown every 10s
                print(
                    f"[{self._get_hkt_time()}] "
                    f"⏳ Waiting... {int(remaining)}s until submission"
                )
                time.sleep(10)
            elif remaining > 10:
                # 10-60 seconds away - show every second
                print(
                    f"[{self._get_hkt_time()}] "
                    f"⏳ {remaining:.1f}s remaining..."
                )
                time.sleep(1)
            elif remaining > 1:
                # Last 10 seconds - show every 0.5s
                print(
                    f"[{self._get_hkt_time()}] "
                    f"⏰ {remaining:.2f}s..."
                )
                time.sleep(0.5)
            else:
                # Last second - busy wait for precision
                print(f"[{self._get_hkt_time()}] 🎯 Final countdown...")
                while datetime.now(self.hkt) < adjusted_target:
                    time.sleep(0.001)  # 1ms precision
                break

        print(f"[{self._get_hkt_time()}] ⚡ TIME REACHED! FIRING REQUEST NOW!")

    def _get_hkt_time(self):
        """Get current HKT time as formatted string"""
        return datetime.now(self.hkt).strftime('%H:%M:%S.%f')[:-3]

    def run_scheduled_booking(
        self,
        username,
        password,
        facility_data,
        target_time_str,
        network_offset_ms=200
    ):
        """
        Complete workflow: login early, wait, then submit at exact time

        Args:
            username: Login username
            password: Login password
            facility_data: Booking details dict
            target_time_str: Target time in HKT, e.g., "08:30:00"
            network_offset_ms: Send request this many ms early (default 200ms)
        """
        print("="*70)
        print("🎯 SCHEDULED BOOKING SYSTEM")
        print("="*70)

        # Step 1: Login
        if not self.login(username, password):
            print("❌ Login failed. Aborting.")
            return False

        # Step 2: Extract CSRF token
        if not self.extract_csrf_token():
            print("❌ Failed to get CSRF token. Aborting.")
            return False

        # Step 3: Parse target time
        today = datetime.now(self.hkt).date()
        target_datetime = datetime.strptime(
            f"{today} {target_time_str}",
            "%Y-%m-%d %H:%M:%S"
        )
        target_datetime = self.hkt.localize(target_datetime)

        print("\n" + "="*70)
        print(f"✅ READY TO BOOK!")
        print(f"   Target time: {target_datetime.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        print(f"   Network offset: {network_offset_ms}ms early")
        print(f"   Facility: {facility_data['facility_name']}")
        print("="*70 + "\n")

        # Step 4: Wait until exact time
        self.wait_until_exact_time(target_datetime, network_offset_ms)

        # Step 5: Submit booking
        response = self.submit_booking(facility_data)

        print("\n" + "="*70)
        print("📋 BOOKING PROCESS COMPLETE")
        print("="*70)

        return response


# Example usage
if __name__ == "__main__":
    # Configuration
    USERNAME = "username"
    PASSWORD = "password"

    # Booking details
    FACILITY_DATA = {
        'facility_id': '1751',
        'facility_name': 'Volleyball Court No. 3',
        'start_datetime': '25 Oct 2025 08:30',
        'end_datetime': '25 Oct 2025 09:30',
        'fb_user_id': '442240'
    }

    # Target submission time (HKT)
    TARGET_TIME = "08:30:00"  # Will submit at exactly 08:30:00 HKT
    NETWORK_OFFSET_MS = 200  # Send 200ms early to account for network latency

    # Run the scheduled booking
    scheduler = ScheduledBooking()
    scheduler.run_scheduled_booking(
        username=USERNAME,
        password=PASSWORD,
        facility_data=FACILITY_DATA,
        target_time_str=TARGET_TIME,
        network_offset_ms=NETWORK_OFFSET_MS
    )
