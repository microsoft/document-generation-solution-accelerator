from base.base import BasePage


class GeneratePage(BasePage):
    GENERATE_DRAFT = "//button[@title='Generate Draft']"
    TYPE_QUESTION = "//textarea[@placeholder='Type a new question...']"
    SEND_BUTTON = "//div[@aria-label='Ask question button']"

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

    def click_generate_draft_button(self):
        # Type a question in the text area
        self.page.locator(self.GENERATE_DRAFT).click()
        self.page.wait_for_timeout(15000)
