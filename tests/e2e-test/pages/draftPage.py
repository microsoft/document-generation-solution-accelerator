from base.base import BasePage
from pytest_check import check
import time


class DraftPage(BasePage):
    # Principal_Amount_and_Date = "div:nth-child(3) div:nth-child(2) span:nth-child(1) textarea:nth-child(1)"
    # Borrower_Information = "div:nth-child(3) div:nth-child(2) span:nth-child(1) textarea:nth-child(1)"
    # Payee_Information = "//div[3]//div[2]//span[1]//textarea[1]"
    Draft_Sections = "//textarea"
    Draft_headings = "//span[@class='fui-Text ___nl2uoq0 fk6fouc f4ybsrx f1i3iumi f16wzh4i fpgzoln f1w7gpdv f6juhto f1gl81tg f2jf649 fepr9ql febqm8h']"
    invalid_response = "The requested information is not available in the retrieved data. Please try another query or topic."
    invalid_response1 = "There was an issue fetching your data. Please try again."
    invalid_response2 = " "

    def __init__(self, page):
        self.page = page



    def check_draft_Sections(self, timeout: float = 120.0, poll_interval: float = 0.5):   
        """
        Validates that all draft sections are non-empty and not equal to known invalid responses.

        Args:
            timeout (float): Max wait time in seconds.
            poll_interval (float): Time between checks.
        """
        start_time = time.time()

        while time.time() - start_time < timeout:
            section_count = self.page.locator(self.Draft_Sections).count()

            if section_count >= 13:  # optional, enforce expected count
                all_ready = True

                for i in range(section_count):
                    section_text = self.page.locator(self.Draft_Sections).nth(i).text_content()
                    if not section_text or not section_text.strip():
                        all_ready = False
                        break
                if all_ready:
                    break

            time.sleep(poll_interval)
        else:
            raise TimeoutError("Timeout waiting for all draft sections to have non-empty content")

        # Validation after all sections are ready
        for i in range(section_count):
            section_element = self.page.locator(self.Draft_Sections).nth(i)
            heading_text = self.page.locator(self.Draft_headings).nth(i).text_content()
            content = section_element.text_content().strip()

            with check:
                check.is_not_none(content, f"Draft section '{heading_text}' is None")
                check.not_equal(content, self.invalid_response, f"Invalid response in '{heading_text}' section")
                check.not_equal(content, self.invalid_response1, f"Invalid response in '{heading_text}' section")
                check.not_equal(content, "", f"Draft section '{heading_text}' is empty")
