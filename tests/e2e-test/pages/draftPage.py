from base.base import BasePage
from pytest_check import check


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

    def check_draft_Sections(self):
        self.page.wait_for_timeout(10000)
        if self.page.locator(self.Draft_Sections).count() >= 1:
            for i in range(self.page.locator(self.Draft_Sections).count()):
                draft_sections_response = self.page.locator(self.Draft_Sections).nth(i)
                draft_heading = (
                    self.page.locator(self.Draft_headings).nth(i).text_content()
                )
                check.not_equal(
                    self.invalid_response,
                    draft_sections_response.text_content(),
                    f"Invalid response for {draft_heading} section",
                )
                check.not_equal(
                    self.invalid_response1,
                    draft_sections_response.text_content(),
                    f"Invalid response for {draft_heading} section",
                )
                check.is_not_none(
                    draft_sections_response.text_content(),
                    f"Invalid response for {draft_heading} section",
                )
