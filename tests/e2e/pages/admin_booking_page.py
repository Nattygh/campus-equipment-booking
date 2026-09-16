from tests.e2e.pages.base_page import DEFAULT_TIMEOUT, BasePage


class AdminBookingPage(BasePage):
    def open_pending(self):
        self.open("/admin/bookings")
        return self

    def approve(self, booking_id):
        self.find_clickable(f"approve-booking-{booking_id}").click()
        return self

    def reject(self, booking_id):
        self.find_clickable(f"reject-booking-{booking_id}").click()
        return self

    def activate(self, booking_id):
        self.find_clickable(f"activate-booking-{booking_id}").click()
        return self

    def return_item(self, booking_id):
        self.find_clickable(f"return-booking-{booking_id}").click()
        return self

    def status_of(self, booking_id):
        return self.find(f"admin-booking-status-{booking_id}").text

    def is_listed(self, booking_id):
        return self.exists(f"admin-booking-row-{booking_id}")