from asyncio.log import logger
from base.base import BasePage
from playwright.sync_api import expect\


class GeneratePage(BasePage):
    GENERATE_DRAFT = "//button[@title='Generate Draft']"
    TYPE_QUESTION = "//textarea[@placeholder='Type a new question...']"
    SEND_BUTTON = "//div[@aria-label='Ask question button']"
    SHOW_CHAT_HISTORY_BUTTON="//span[text()='Show template history']"
    HIDE_CHAT_HISTORY_BUTTON = "//span[text()='Hide Chat History']"
    CHAT_HISTORY_ITEM = "//div[@aria-label='Hide template history']"
    SHOW_CHAT_HISTORY = "//span//i"
    CHAT_HISTORY_NAME = "div[aria-label='chat history list']"
    CHAT_CLOSE_ICON = "button[title='Hide']"
    CHAT_HISTORY_OPTIONS = "//button[@id='moreButton']"
    CHAT_HISTORY_DELETE = "//button[@role='menuitem']"

    def __init__(self, page):
        self.page = page

    def enter_a_question(self, text):
        # Type a question in the text area
        self.page.wait_for_timeout(3000)
        self.page.locator(self.TYPE_QUESTION).fill(text)
        self.page.wait_for_timeout(3000)

    def click_send_button(self):
        # Type a question in the text area
        self.page.locator(self.SEND_BUTTON).click()
        self.page.wait_for_timeout(10000)

    def click_generate_draft_button(self):
        # Type a question in the text area
        self.page.locator(self.GENERATE_DRAFT).click()
        self.page.wait_for_timeout(15000)

    def show_chat_history(self):
        """Click to show chat history if the button is visible."""
        show_button = self.page.locator(self.SHOW_CHAT_HISTORY_BUTTON)
        if show_button.is_visible():
            show_button.click()
            self.page.wait_for_timeout(2000)
            expect(self.page.locator(self.CHAT_HISTORY_ITEM)).to_be_visible()
        else:
            logger.info("'Show' button not visible — chat history may already be shown.")


    def close_chat_history(self):
        """Click to close chat history if visible."""
        hide_button = self.page.locator(self.HIDE_CHAT_HISTORY_BUTTON)
        if hide_button.is_visible():
            hide_button.click()
            self.page.wait_for_timeout(2000)
        else:
            logger.info("Hide button not visible. Chat history might already be closed.")

    def delete_chat_history(self):

        chat_history = self.page.locator("//span[contains(text(),'No chat history.')]")
        if chat_history.is_visible():
            self.page.wait_for_load_state("networkidle")
            self.page.locator("button[title='Hide']").wait_for(state="visible", timeout=5000)
            self.page.locator("button[title='Hide']").click()

        else:
            self.page.locator(self.CHAT_HISTORY_OPTIONS).click()
            self.page.locator(self.CHAT_HISTORY_DELETE).click()
            self.page.get_by_role("button", name="Clear All").click()
            self.page.get_by_label("hide button").click()
            self.page.wait_for_load_state("networkidle")
            self.page.wait_for_timeout(2000)