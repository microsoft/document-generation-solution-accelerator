from base.base import BasePage
from playwright.sync_api import expect
import logging
logger = logging.getLogger(__name__)


class GeneratePage(BasePage):
    GENERATE_DRAFT = "//button[@title='Generate Draft']"
    TYPE_QUESTION = "//textarea[@placeholder='Type a new question...']"
    SEND_BUTTON = "//div[@aria-label='Ask question button']"
    SHOW_CHAT_HISTORY_BUTTON = "//span[text()='Show template history']"
    HIDE_CHAT_HISTORY_BUTTON = "//span[text()='Hide Chat History']"
    CHAT_HISTORY_ITEM = "//body//div[@id='root']//div[@role='presentation']//div[@role='presentation']//div[1]//div[1]//div[1]//div[1]//div[1]//div[1]"
    SHOW_CHAT_HISTORY = "//span//i"
    CHAT_HISTORY_NAME = "div[aria-label='chat history list']"
    CHAT_CLOSE_ICON = "button[title='Hide']"
    CHAT_HISTORY_OPTIONS = "//button[@id='moreButton']"
    CHAT_HISTORY_DELETE = "//button[@role='menuitem']"
    CHAT_HISTORY_CLOSE = "//i[@data-icon-name='Cancel']"

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
        locator = self.page.locator("//p[contains(text(),'Generating template...this may take up to 30 secon')]")
        stop_button = self.page.locator("//div[@aria-label='Stop generating']")

        try:
            # Wait up to 60s for the element to become **hidden**
            locator.wait_for(state="hidden", timeout=60000)
        except TimeoutError:
            msg = "❌ TIMED-OUT: Not recieved response within 60 sec."
            logger.info(msg)  # ✅ log to console/log file
            raise AssertionError(msg)

        finally:
            if stop_button.is_visible():
                stop_button.click()
                logger.info("Clicked on 'Stop generating' button after timeout.")
            else:
                logger.info("'Stop generating' button not visible.")

        self.page.wait_for_timeout(5000)

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
            logger.info("Chat history is not generated")

    def close_chat_history(self):
        """Click to close chat history if visible."""
        hide_button = self.page.locator(self.HIDE_CHAT_HISTORY_BUTTON)
        if hide_button.is_visible():
            hide_button.click()
            self.page.wait_for_timeout(2000)
        else:
            logger.info(
                "Hide button not visible. Chat history might already be closed."
            )

    def delete_chat_history(self):

        self.page.locator(self.SHOW_CHAT_HISTORY_BUTTON).click()
        self.page.wait_for_timeout(4000)
        chat_history = self.page.locator("//span[contains(text(),'No chat history.')]")
        if chat_history.is_visible():
            self.page.wait_for_load_state("networkidle")
            self.page.locator("button[title='Hide']").wait_for(
                state="visible", timeout=5000
            )
            self.page.locator("button[title='Hide']").click()

        else:
            self.page.locator(self.CHAT_HISTORY_OPTIONS).click()
            self.page.locator(self.CHAT_HISTORY_DELETE).click()
            self.page.wait_for_timeout(5000)
            self.page.get_by_role("button", name="Clear All").click()
            self.page.wait_for_timeout(5000)
            expect(self.page.locator("//span[contains(text(),'No chat history.')]")).to_be_visible()
            self.page.locator(self.CHAT_HISTORY_CLOSE).click()
            self.page.wait_for_load_state("networkidle")
            self.page.wait_for_timeout(2000)
