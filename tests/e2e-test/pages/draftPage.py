import time
import os
from base.base import BasePage
from pytest_check import check
import logging
logger = logging.getLogger(__name__)


class DraftPage(BasePage):
    Draft_Sections = "//textarea"
    Draft_headings = "//span[@class='fui-Text ___nl2uoq0 fk6fouc f4ybsrx f1i3iumi f16wzh4i fpgzoln f1w7gpdv f6juhto f1gl81tg f2jf649 fepr9ql febqm8h']"
    invalid_response = "The requested information is not available in the retrieved data. Please try another query or topic."
    invalid_response1 = "There was an issue fetching your data. Please try again."

    def __init__(self, page):
        self.page = page

    def validate_draft_sections_loaded(self):
        max_wait_time = 180  # seconds
        poll_interval = 2

        self.page.wait_for_timeout(25000)

        # All draft section containers
        section_blocks = self.page.locator("//div[@class='ms-Stack ___mit7380 f4zyqsv f6m9rw3 fwbpcpn folxr9a f1s274it css-103']")
        total_sections = section_blocks.count()

        logger.info(f"🔍 Total sections found: {total_sections}")

        for index in range(total_sections):
            section = section_blocks.nth(index)

            try:
                section.scroll_into_view_if_needed()
                self.page.wait_for_timeout(500)

                title_element = section.locator("//span[@class='fui-Text ___nl2uoq0 fk6fouc f4ybsrx f1i3iumi f16wzh4i fpgzoln f1w7gpdv f6juhto f1gl81tg f2jf649 fepr9ql febqm8h']")
                title_text = title_element.inner_text(timeout=5000).strip()
            except Exception as e:
                logger.error(f"❌ Could not read title for section #{index + 1}: {e}")
                continue

            logger.info(f"➡️ Validating section [{index + 1}/{total_sections}]: '{title_text}'")

            content_locator = section.locator("//textarea")
            generate_btn = section.locator("//span[@class='fui-Button__icon rywnvv2 ___963sj20 f1nizpg2']")
            spinner_locator = section.locator("//div[@id='section-card-spinner']")

            content_loaded = False

            # 🚨 If spinner is visible inside this section, click generate immediately
            try:
                if spinner_locator.is_visible(timeout=1000):
                    logger.warning(f"⏳ Spinner found in section '{title_text}'. Clicking Generate immediately.")
                    generate_btn.click()
                    self.page.wait_for_timeout(3000)
                    confirm_btn = self.page.locator("//button[@class='fui-Button r1alrhcs ___zqkcn80 fd1o0ie fjxutwb fwiml72 fj8njcf fzcpov4 f1d2rq10 f1mk8lai ff3glw6']")
                    if confirm_btn.is_visible(timeout=3000):
                        confirm_btn.click()
                        logger.info(f"🟢 Clicked Confirm button for section '{title_text}'")
                    else:
                        logger.warning(f"⚠️ Confirm button not visible for section '{title_text}'")
            except Exception as e:
                logger.error(f"❌ Error while clicking Confirm button for section '{title_text}': {e}")

            # ⏳ Retry short wait (15s) for content to load
            short_wait = 15
            short_start = time.time()
            while time.time() - short_start < short_wait:
                try:
                    content = content_locator.text_content(timeout=2000).strip()
                    if content:
                        logger.info(f"✅ Section '{title_text}' loaded after Generate + Confirm.")
                        content_loaded = True
                        break
                except Exception as e:
                    logger.info(f"⏳ Waiting for section '{title_text}' to load... {e}")
                time.sleep(1)

            if not content_loaded:
                logger.error(f"❌ Section '{title_text}' still empty after Generate + Confirm wait ({short_wait}s). Skipping.")

            # Step 1: Wait for content to load normally
            start = time.time()
            while time.time() - start < max_wait_time:
                try:
                    content = content_locator.text_content(timeout=2000).strip()
                    if content:
                        logger.info(f"✅ Section '{title_text}' loaded successfully.")
                        content_loaded = True
                        break
                except Exception as e:
                    logger.info(f"⏳ Waiting for section '{title_text}' to load... {e}")
                time.sleep(poll_interval)

            # Step 2: If still not loaded, click Generate and retry
            if not content_loaded:
                logger.warning(f"⚠️ Section '{title_text}' is empty. Attempting 'Generate'...")

                try:
                    generate_btn.click()
                    logger.info(f"🔄 Clicked 'Generate' for section '{title_text}'")
                except Exception as e:
                    logger.error(f"❌ Failed to click 'Generate' for section '{title_text}': {e}")
                    continue

                # Retry wait
                start = time.time()
                while time.time() - start < max_wait_time:
                    try:
                        content = content_locator.text_content(timeout=2000).strip()
                        if content:
                            logger.info(f"✅ Section '{title_text}' loaded after clicking Generate.")
                            content_loaded = True
                            break
                    except Exception as e:
                        logger.info(f"⏳ Waiting for section '{title_text}' to load after Generate... {e}")
                    time.sleep(poll_interval)

                if not content_loaded:
                    logger.error(f"❌ Section '{title_text}' still empty after retrying.")

                    # Optional: take screenshot
                    screenshot_dir = "screenshots"
                    os.makedirs(screenshot_dir, exist_ok=True)
                    screenshot_path = os.path.join(screenshot_dir, f"section_{index + 1}_{title_text.replace(' ', '_')}.png")
                    try:
                        section.screenshot(path=screenshot_path)
                        logger.error(f"📸 Screenshot saved: {screenshot_path}")
                    except Exception as e:
                        logger.error(f"❌ Generate click failed in section '{title_text}': {e}")
                        continue

            try:
                content = content_locator.text_content(timeout=2000).strip()
                with check:
                    if content == self.invalid_response or content == self.invalid_response1:
                        logger.warning(f"❌ Invalid response found in '{title_text}'. Retrying Generate + Confirm...")

                        try:
                            generate_btn.click()
                            self.page.wait_for_timeout(3000)

                            confirm_btn = self.page.locator("//button[@class='fui-Button r1alrhcs ___zqkcn80 fd1o0ie fjxutwb fwiml72 fj8njcf fzcpov4 f1d2rq10 f1mk8lai ff3glw6']")
                            if confirm_btn.is_visible(timeout=3000):
                                confirm_btn.click()
                                logger.info(f"🟢 Retried Confirm for section '{title_text}'")
                            else:
                                logger.warning(f"⚠️ Confirm button not visible during retry for '{title_text}'")
                        except Exception as e:
                            logger.error(f"❌ Retry Generate/Confirm failed: {e}")

                        retry_start = time.time()
                        while time.time() - retry_start < short_wait:
                            try:
                                content = content_locator.text_content(timeout=2000).strip()
                                if content and content not in [self.invalid_response, self.invalid_response1]:
                                    logger.info(f"✅ Section '{title_text}' fixed after retry.")
                                    break
                            except Exception as e:
                                logger.info(f"⏳ Retrying section '{title_text}'... {e}")
                            time.sleep(1)

                        with check:
                            check.not_equal(content, self.invalid_response, f"❌ '{title_text}' still has invalid response after retry")
                            check.not_equal(content, self.invalid_response1, f"❌ '{title_text}' still has invalid response after retry")

                    else:
                        logger.info(f"🎯 Section '{title_text}' has valid content.")
            except Exception as e:
                logger.error(f"❌ Could not validate content for '{title_text}': {e}")
                logger.info(f"✔️ Completed section: '{title_text}'\n")
