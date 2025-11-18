from base.base import BasePage
from playwright.sync_api import expect
import logging
logger = logging.getLogger(__name__)
from pytest_check import check


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
    NEW_CHAT_BUTTON = 'button[aria-label="start a new chat button"]'


    def __init__(self, page):
        self.page = page

    def validate_generate_page(self):
        """Validate that Generate page chat conversation elements are visible"""
        self.page.wait_for_timeout(3000)
        expect(self.page.locator(self.TYPE_QUESTION)).to_be_visible()
        expect(self.page.locator(self.SEND_BUTTON)).to_be_visible()

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

    def validate_draft_button_enabled(self):
        self.page.wait_for_timeout(5000)
        generate_draft_button = self.page.locator(self.GENERATE_DRAFT)
        with check:
            if not generate_draft_button.is_enabled():
                logger.error("❌ 'Generate Draft' button is disabled.")
            else:
                logger.info("✅ 'Generate Draft' button is enabled.")
    
    def select_history_thread(self, thread_index=0):
        """Select a history thread from the template history panel."""
        history_threads = self.page.locator('div[role="listitem"]')
        count = history_threads.count()

        # ❗ Fail the test if no threads found
        assert count > 0, "No history threads found — test failed."

        # Optional: fail if the index does not exist
        assert thread_index < count, (
            f"Thread index {thread_index} is out of range. Only {count} thread(s) available."
        )

        history_threads.nth(thread_index).wait_for(state="visible")
        history_threads.nth(thread_index).click()

    def click_new_chat_button(self):
        """Click the new chat button next to the chat box."""
        new_chat_button = self.page.locator(self.NEW_CHAT_BUTTON)

        # Fail the test if button not found or not visible
        assert new_chat_button.is_visible(), "New Chat button is not visible — test failed."

        assert new_chat_button.is_enabled(), "New Chat button is disabled — test failed."

        new_chat_button.click()
        logger.info("New Chat button clicked successfully")
    
    def verify_saved_chat(self, expected_text: str):
        """Verify that the saved chat contains specific expected text."""
        
        # Locator for all chat messages (user + GPT)
        chat_messages = self.page.locator(
            '._chatMessageUserMessage_1dc7g_87, ._answerText_1qm4u_14'
        )

        # Fail if there are no messages at all
        assert chat_messages.count() > 0, "No chat messages found — saved chat did not load."

        # Check if expected text exists in any message
        found = False
        count = chat_messages.count()
        
        for i in range(count):
            message_text = chat_messages.nth(i).inner_text()
            if expected_text in message_text:
                found = True
                break

        assert found, f"Expected text '{expected_text}' not found in saved chat."
        logger.info(f"Verified saved chat contains expected text: {expected_text}")
                
    def delete_thread_by_index(self, thread_index: int = 0):
        """
        Delete a session thread based on its index and verify it is removed.
        
        :param thread_index: Index of the thread to delete (0 = first thread)
        """
        # 1️⃣ Locate all threads
        threads = self.page.locator('div[data-list-index]')
        count = threads.count()
        
        # Fail if no threads exist
        assert count > 0, "No history threads found — cannot delete."
        assert count > thread_index, f"Thread index {thread_index} out of range (total: {count})"

        # 2️⃣ Locate the thread at the given index
        thread = threads.nth(thread_index)

        # 3️⃣ Click the Delete icon in that thread
        delete_icon = thread.locator('button[title="Delete"]')
        assert delete_icon.is_visible(), f"Delete icon not visible for thread at index {thread_index}"
        delete_icon.click()
        logger.info(f"Clicked delete icon on thread at index {thread_index}")

        # 4️⃣ Wait for delete confirmation dialog
        dialog_title = self.page.get_by_text("Are you sure you want to delete this item?")
        dialog_title.wait_for(state="visible", timeout=5000)
        logger.info("Delete confirmation dialog appeared")

        # Verify dialog text is present
        dialog_text = self.page.get_by_text("The history of this chat session will permanently removed")
        assert dialog_text.is_visible(), "Delete confirmation text not visible in dialog"
        logger.info("Delete confirmation text verified")

        # 5️⃣ Click Delete button in the dialog
        delete_button = self.page.get_by_role("button", name="Delete")
        assert delete_button.is_visible(), "Delete button not visible in confirmation dialog"
        delete_button.click()
        logger.info("Clicked Delete in confirmation dialog")

        # Wait for dialog to disappear
        dialog_title.wait_for(state="hidden", timeout=5000)
        logger.info("Delete confirmation dialog closed")

        # 6️⃣ Verify the thread is removed - re-query the threads to avoid stale elements
        self.page.wait_for_timeout(2000)  # allow UI to update
        threads_after = self.page.locator('div[data-list-index]')
        new_count = threads_after.count()
        assert new_count == count - 1, f"Thread at index {thread_index} was not deleted (before: {count}, after: {new_count})"
        logger.info(f"Thread at index {thread_index} successfully deleted. Thread count decreased from {count} to {new_count}")
