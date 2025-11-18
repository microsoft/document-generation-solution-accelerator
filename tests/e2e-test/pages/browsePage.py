from base.base import BasePage
from playwright.sync_api import expect


class BrowsePage(BasePage):
    TYPE_QUESTION = "//textarea[@placeholder='Type a new question...']"
    SEND_BUTTON = "//div[@aria-label='Ask question button']"
    GENERATE_BUTTON = "//div[contains(@class, 'ms-Stack')]//span[normalize-space()='Generate']"
    DRAFT_TAB_BUTTON = "//span[normalize-space()='Draft']"
    DRAFT_TAB_CONTAINER = "//div[contains(@class, '_navigationButtonDisabled')]"
    RESPONSE_REFERENCE_EXPAND_ICON = "//span[@aria-label='Open references']"
    REFERENCE_LINKS_IN_RESPONSE = "//span[@class='_citationContainer_1qm4u_72']"
    CLOSE_BUTTON = "//button[.='Close']"

    def __init__(self, page):
        self.page = page

    def validate_browse_page(self):
        """Validate that Browse page chat conversation elements are visible"""
        self.page.wait_for_timeout(3000)
        expect(self.page.locator(self.TYPE_QUESTION)).to_be_visible()
        expect(self.page.locator(self.SEND_BUTTON)).to_be_visible()

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

    def click_draft_tab_button(self):
        """Click on Draft tab button"""
        self.page.wait_for_timeout(2000)
        self.page.locator(self.DRAFT_TAB_BUTTON).click()
        self.page.wait_for_timeout(3000)

    def is_draft_tab_enabled(self):
        """Check if Draft tab is enabled (clickable)"""
        self.page.wait_for_timeout(2000)
        draft_button = self.page.locator(self.DRAFT_TAB_BUTTON)
        
        if draft_button.count() > 0:
            # Check if the container has the disabled class
            draft_container = self.page.locator(self.DRAFT_TAB_CONTAINER)
            has_disabled_class = draft_container.count() > 0
            
            # Check if cursor is not-allowed (disabled state)
            cursor_style = draft_container.get_attribute("style") if has_disabled_class else ""
            is_disabled = "cursor: not-allowed" in cursor_style or has_disabled_class
            
            return not is_disabled
        return False

    def is_draft_tab_disabled(self):
        """Check if Draft tab is disabled (not clickable)"""
        self.page.wait_for_timeout(2000)
        draft_button = self.page.locator(self.DRAFT_TAB_BUTTON)
        
        if draft_button.count() > 0:
            # Check if the container has the disabled class
            draft_container = self.page.locator(self.DRAFT_TAB_CONTAINER)
            has_disabled_class = draft_container.count() > 0
            
            # Check if cursor is not-allowed (disabled state)
            if has_disabled_class:
                cursor_style = draft_container.get_attribute("style") or ""
                is_disabled = "cursor: not-allowed" in cursor_style
                return is_disabled
            return False
        return True  # If not visible, consider it disabled

