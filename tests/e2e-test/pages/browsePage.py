from base.base import BasePage


class BrowsePage(BasePage):
    TYPE_QUESTION = "//textarea[@placeholder='Type a new question...']"
    SEND_BUTTON = "//div[@aria-label='Ask question button']"
    GENERATE_BUTTON = "//span[normalize-space()='Generate']"
    RESPONSE_REFERENCE_EXPAND_ICON = "//span[@aria-label='Open references']"
    REFERENCE_LINKS_IN_RESPONSE = "//span[@class='_citationContainer_1qm4u_72']"
    CLOSE_BUTTON = "//button[.='Close']"

    def __init__(self, page):
        self.page = page

    def enter_a_question(self, text):
        # Type a question in the text area
        self.page.locator(self.TYPE_QUESTION).fill(text)
        self.page.wait_for_timeout(2000)

    def click_send_button(self):
        # Type a question in the text area
        self.page.locator(self.SEND_BUTTON).click()
        self.page.wait_for_timeout(10000)

    def click_generate_button(self):
        # Type a question in the text area
        self.page.locator(self.GENERATE_BUTTON).click()
        self.page.wait_for_timeout(5000)

    def click_reference_link_in_response(self):
        # Click on reference link response
        BasePage.scroll_into_view(
            self, self.page.locator(self.REFERENCE_LINKS_IN_RESPONSE)
        )
        self.page.wait_for_timeout(2000)
        reference_links = self.page.locator(self.REFERENCE_LINKS_IN_RESPONSE)
        reference_links.nth(reference_links.count() - 1).click()
        # self.page.locator(self.REFERENCE_LINKS_IN_RESPONSE).click()
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(2000)

    def click_expand_reference_in_response(self):
        # Click on expand in response reference area
        self.page.wait_for_timeout(5000)
        expand_icon = self.page.locator(self.RESPONSE_REFERENCE_EXPAND_ICON)
        expand_icon.nth(expand_icon.count() - 1).click()
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(2000)

    def close_citation(self):
        self.page.wait_for_timeout(3000)
        self.page.locator(self.CLOSE_BUTTON).click()
        self.page.wait_for_timeout(2000)
