from tests.e2e.pages.base_page import BasePage


class BookingPage(BasePage):
    def open_booking_form(self, equipment_id):
        self.open(f"/equipment/{equipment_id}/book")
        return self

    def fill_form(self, quantity, start_date, expected_return_date):
        qty = self.find("quantity-input")
        qty.clear()
        qty.send_keys(str(quantity))

        self._set_datetime("start-date-input", start_date)
        self._set_datetime("return-date-input", expected_return_date)

        return self

    def _set_datetime(self, test_id, value):
        element = self.find(test_id)

        self.driver.execute_script(
            """
            const element = arguments[0];
            const value = arguments[1];

            const setter = Object.getOwnPropertyDescriptor(
                HTMLInputElement.prototype,
                'value'
            ).set;

            setter.call(element, value);

            element.dispatchEvent(
                new Event('input', { bubbles: true })
            );

            element.dispatchEvent(
                new Event('change', { bubbles: true })
            );

            return element.value;
            """,
            element,
            value,
        )

    def submit(self):
        button = self.find_clickable("submit-booking")

        self.driver.execute_script(
            """
            const button = arguments[0];
            const form = button.form;

            form.submit();
            """,
            button,
        )

        return self

    def open_my_bookings(self):
        self.open("/bookings")
        return self

    def status_of(self, booking_id):
        return self.find(f"booking-status-{booking_id}").text

    def cancel(self, booking_id):
        self.find_clickable(f"cancel-booking-{booking_id}").click()
        return self

    def has_cancel_button(self, booking_id):
        return self.exists(f"cancel-booking-{booking_id}")