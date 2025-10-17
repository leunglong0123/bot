import requests
from bs4 import BeautifulSoup
import re

class PolyUBookingSession:
    def __init__(self):
        # Create a session to persist cookies automatically
        self.session = requests.Session()
        self.csrf_token = None

        # Set headers to mimic browser
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
        })

    def login(self, username, password):
        """Login and establish session with cookies"""
        print("Logging in...")

        # Step 1: GET the login page to establish initial cookies
        login_url = "https://www40.polyu.edu.hk/starspossfbstud/secure/ui_cncl_book/cncl_book_submit.do"
        response = self.session.get(login_url)

        print(f"Initial request status: {response.status_code}")
        print(f"Cookies after initial request: {dict(self.session.cookies)}")

        # Step 2: POST login credentials
        login_submit_url = "https://www40.polyu.edu.hk/starspossfbstud/j_security_check"

        login_data = {
            'j_username': username,
            'j_password': password,
            'buttonAction': 'loginButton'
        }

        response = self.session.post(login_submit_url, data=login_data, allow_redirects=True)

        print(f"Login status: {response.status_code}")
        print(f"Final URL after login: {response.url}")
        print(f"\nCookies after login:")
        for cookie_name, cookie_value in self.session.cookies.items():
            # Truncate long cookie values for readability
            display_value = cookie_value[:50] + "..." if len(cookie_value) > 50 else cookie_value
            print(f"  {cookie_name}: {display_value}")

        # Check if login was successful
        if "error" in response.url.lower() or "login" in response.url.lower():
            print("\n❌ Login failed! Check credentials.")
            return False

        print("\n✅ Login successful!")
        return True

    def extract_csrf_token(self):
        """Extract CSRF token from the booking page"""
        print("\nExtracting CSRF token...")

        # Navigate to make booking page
        booking_url = "https://www40.polyu.edu.hk/starspossfbstud/secure/ui_make_book/make_book_submit.do"
        response = self.session.get(booking_url)

        if response.status_code != 200:
            print(f"❌ Failed to access booking page: {response.status_code}")
            return None

        # Parse HTML to find CSRF token
        soup = BeautifulSoup(response.text, 'html.parser')

        # Look for CSRF token in hidden input field
        csrf_input = soup.find('input', {'name': 'CSRFToken'})

        if csrf_input and csrf_input.get('value'):
            self.csrf_token = csrf_input['value']
            print(f"✅ CSRF Token found: {self.csrf_token}")
            return self.csrf_token

        # Alternative: search in page source using regex
        csrf_match = re.search(r'CSRFToken["\s:]+([a-f0-9\-]+)', response.text)
        if csrf_match:
            self.csrf_token = csrf_match.group(1)
            print(f"✅ CSRF Token found (via regex): {self.csrf_token}")
            return self.csrf_token

        print("❌ CSRF token not found")
        return None

    def get_session_info(self):
        """Return all session info needed for booking requests"""
        return {
            'cookies': dict(self.session.cookies),
            'csrf_token': self.csrf_token,
            'session_object': self.session  # Can be used directly for requests
        }


# Demo usage
if __name__ == "__main__":
    # Initialize session
    booking_session = PolyUBookingSession()

    # Login (replace with your credentials)
    username = "username"
    password = "password"

    if booking_session.login(username, password):
        # Extract CSRF token
        csrf_token = booking_session.extract_csrf_token()

        if csrf_token:
            print("\n" + "="*60)
            print("✅ SESSION READY FOR BOOKING!")
            print("="*60)

            session_info = booking_session.get_session_info()

            print("\n📋 You now have:")
            print(f"  - Session with {len(session_info['cookies'])} cookies")
            print(f"  - CSRF Token: {csrf_token}")
            print("\n💡 You can now use this session to send booking requests!")

            # Show how to use the session
            print("\n" + "="*60)
            print("Example: How to send booking request")
            print("="*60)
            print("""
# Use the session object to make booking requests:
booking_data = {
    'CSRFToken': booking_session.csrf_token,
    'facilityId': '1751',
    'startDateTime': '25 Oct 2025 08:30',
    'endDateTime': '25 Oct 2025 09:30',
    # ... other form fields
}

response = booking_session.session.post(
    'https://www40.polyu.edu.hk/starspossfbstud/secure/ui_make_book/make_book_submit.do',
    data=booking_data
)
            """)
