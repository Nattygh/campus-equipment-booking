from tests.e2e.pages.base_page import BasePage


class EquipmentPage(BasePage):
    def open_list(self):
        self.open("/equipment")
        return self

    def is_listed(self, equipment_id):
        return self.exists(f"equipment-row-{equipment_id}")

    def status_of(self, equipment_id):
        return self.find(f"equipment-status-{equipment_id}").text

    def click_book(self, equipment_id):
        self.find_clickable(f"book-link-{equipment_id}").click()
        return self

    def has_book_link(self, equipment_id):
        return self.exists(f"book-link-{equipment_id}")

    def open_add_equipment(self):
        self.find_clickable("add-equipment-link").click()
        return self
