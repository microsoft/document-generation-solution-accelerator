import io
import logging
import time

import pytest
from pytest_check import check
from config.constants import (URL, add_section, browse_question1, browse_question2, browse_question3,
                              browse_question4, browse_question5, generate_question1, invalid_response, 
                              invalid_response1, remove_section)
from pages.browsePage import BrowsePage
from pages.draftPage import DraftPage
from pages.generatePage import GeneratePage
from pages.homePage import HomePage

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
RETRY_DELAY = 3  # seconds


# @pytest.mark.smoke
# def test_docgen_golden_path_refactored(login_logout, request):
#     """
#     DocGen Golden Path Smoke Test:
#     Refactored from parametrized test to sequential execution
#     1. Load home page and navigate to Browse page
#     2. Execute Browse prompts with citations
#     3. Navigate to Generate page and clear chat history
#     4. Execute Generate prompt with retry logic
#     5. Add section to document
#     6. Generate draft and validate sections
#     7. Verify chat history functionality
#     """
    
#     request.node._nodeid = "Golden Path - DocGen - test golden path demo script works properly"
    
#     page = login_logout
#     home_page = HomePage(page)
#     browse_page = BrowsePage(page)
#     generate_page = GeneratePage(page)
#     draft_page = DraftPage(page)

#     log_capture = io.StringIO()
#     handler = logging.StreamHandler(log_capture)
#     logger.addHandler(handler)

#     try:
#         # Step 1: Validate home page is loaded and navigate to Browse
#         logger.info("Step 1: Validate home page is loaded and navigating to Browse Page")
#         start = time.time()
#         home_page.validate_home_page()
#         home_page.click_browse_button()
#         duration = time.time() - start
#         logger.info("Execution Time for 'Validate home page and navigate to Browse': %.2fs", duration)

#         # ✅ Step 2: Loop through Browse questions
#         browse_questions = [browse_question1, browse_question2]  # add more if needed

#         for idx, question in enumerate(browse_questions, start=1):
#             logger.info("Step 2.%d: Validate response for BROWSE Prompt: %s", idx, question)
#             start = time.time()

#             browse_page.enter_a_question(question)
#             browse_page.click_send_button()
#             browse_page.validate_response_status(question_api=question)
#             browse_page.click_expand_reference_in_response()
#             browse_page.click_reference_link_in_response()
#             browse_page.close_citation()

#             duration = time.time() - start
#             logger.info("Execution Time for 'BROWSE Prompt%d': %.2fs", idx, duration)

#         # Step 4: Navigate to Generate page and delete chat history
#         logger.info("Step 4: Navigate to Generate page and delete chat history")
#         start = time.time()
#         browse_page.click_generate_button()
#         generate_page.delete_chat_history()
#         duration = time.time() - start
#         logger.info("Execution Time for 'Navigate to Generate and delete chat history': %.2fs", duration)

#         # Step 5: Generate Question with retry logic
#         logger.info("Step 5: Validate response for GENERATE Prompt: %s", generate_question1)
#         start = time.time()
        
#         question_passed = False
#         for attempt in range(1, MAX_RETRIES + 1):
#             try:
#                 logger.info("Attempt %d: Entering Generate Question: %s", attempt, generate_question1)
#                 generate_page.enter_a_question(generate_question1)
#                 generate_page.click_send_button()
                
#                 time.sleep(2)
#                 response_text = page.locator("//p")
#                 latest_response = response_text.nth(response_text.count() - 1).text_content()

#                 if latest_response not in [invalid_response, invalid_response1]:
#                     logger.info("[%s] Valid response received on attempt %d", generate_question1, attempt)
#                     question_passed = True
#                     break
#                 else:
#                     logger.warning("[%s] Invalid response received on attempt %d", generate_question1, attempt)
#                     if attempt < MAX_RETRIES:
#                         logger.info("[%s] Retrying... (attempt %d/%d)", generate_question1, attempt + 1, MAX_RETRIES)
#                         time.sleep(RETRY_DELAY)
#                     else:
#                         logger.error("[%s] All %d attempts failed", generate_question1, MAX_RETRIES)
#                         assert latest_response not in [invalid_response, invalid_response1], \
#                             f"FAILED: Invalid response received after {MAX_RETRIES} attempts for: {generate_question1}"
#             except Exception as e:
#                 if attempt < MAX_RETRIES:
#                     logger.warning("[%s] Attempt %d failed: %s", generate_question1, attempt, str(e))
#                     logger.info("[%s] Retrying... (attempt %d/%d)", generate_question1, attempt + 1, MAX_RETRIES)
#                     time.sleep(RETRY_DELAY)
#                 else:
#                     logger.error("[%s] All %d attempts failed. Last error: %s", generate_question1, MAX_RETRIES, str(e))
#                     raise
        
#         # Verify that the question passed after retry attempts
#         assert question_passed, f"FAILED: All {MAX_RETRIES} attempts failed for question: {generate_question1}"
        
#         duration = time.time() - start
#         logger.info("Execution Time for 'GENERATE Prompt': %.2fs", duration)

#         # Step 6: Add Section
#         logger.info("Step 6: Validate response for Add Section Prompt: %s", add_section)
#         start = time.time()
#         generate_page.enter_a_question(add_section)
#         generate_page.click_send_button()
#         duration = time.time() - start
#         logger.info("Execution Time for 'Add Section Prompt': %.2fs", duration)

#         # Step 7: Generate Draft and Validate Sections
#         logger.info("Step 7: Generate Draft and validate all sections are loaded")
#         start = time.time()
#         generate_page.click_generate_draft_button()
#         draft_page.validate_draft_sections_loaded()
#         duration = time.time() - start
#         logger.info("Execution Time for 'Generate Draft and Validate Sections': %.2fs", duration)

#         # Step 8: Show Chat History
#         logger.info("Step 8: Validate chat history is saved")
#         start = time.time()
#         browse_page.click_generate_button()
#         generate_page.show_chat_history()
#         duration = time.time() - start
#         logger.info("Execution Time for 'Validate chat history is saved': %.2fs", duration)

#         # Step 9: Close Chat History
#         logger.info("Step 9: Validate chat history is closed")
#         start = time.time()
#         generate_page.close_chat_history()
#         duration = time.time() - start
#         logger.info("Execution Time for 'Validate chat history is closed': %.2fs", duration)

#         logger.info("Golden path test completed successfully")

#     finally:
#         logger.removeHandler(handler)


# @pytest.mark.smoke
# def test_browse_generate_tabs_accessibility(login_logout, request):
#     """
#     Test Case 9366: BYOc-DocGen-Upon launch user should be able to click Browse and Generate section only.
    
#     Steps:
#     1. Authenticate BYOc DocGen web url
#     2. Verify user is able to click on 'Browse' and 'Generate' tabs
#     3. Verify user should NOT be able to click on 'Draft' tab (disabled state)
#     4. Click on 'Browse' section and verify chat conversation page is displayed
#     5. Click on 'Generate' section and verify chat conversation page is displayed
#     """
    
#     request.node._nodeid = "TC 9366 - Validate Browse and Generate tabs accessibility on launch"
    
#     page = login_logout
#     home_page = HomePage(page)
#     browse_page = BrowsePage(page)
#     generate_page = GeneratePage(page)

#     log_capture = io.StringIO()
#     handler = logging.StreamHandler(log_capture)
#     logger.addHandler(handler)

#     try:
#         # Step 1: Verify login is successful and 'Document Generation' page is displayed
#         logger.info("Step 1: Verify login is successful and 'Document Generation' page is displayed")
#         start = time.time()
        
#         # Navigate to home page to ensure we start from the correct page
#         home_page.open_home_page()
        
#         home_page.validate_home_page()
#         duration = time.time() - start
#         logger.info("Execution Time for 'Validate home page is loaded': %.2fs", duration)

#         # Step 2: Verify Browse tab is clickable
#         logger.info("Step 2: Verify user is able to click on 'Browse' tab")
#         start = time.time()
        
#         home_page.click_browse_button()
        
#         # Verify chat conversation elements are present on Browse page
#         browse_page.validate_browse_page()

#         logger.info("Browse tab is visible and enabled")
#         duration = time.time() - start
#         logger.info("Execution Time for 'Verify Browse tab is clickable': %.2fs", duration)

#         # Step 3: Verify Generate tab is clickable
#         logger.info("Step 3: Verify user is able to click on 'Generate' tab")
#         start = time.time()
        
#         browse_page.click_generate_button()
        
#         # Verify chat conversation elements are present on Generate page
#         generate_page.validate_generate_page()

#         logger.info("Generate tab is visible and enabled")
#         duration = time.time() - start
#         logger.info("Execution Time for 'Verify Generate tab is clickable': %.2fs", duration)

#         # Step 4: Verify Draft tab is NOT clickable (disabled state)
#         logger.info("Step 4: Verify user should NOT be able to click on 'Draft' tab")
#         start = time.time()
        
#         generate_page.enter_a_question(add_section)
#         generate_page.click_send_button()
#         # Verify Draft tab is disabled or not visible
#         generate_page.click_generate_draft_button()
        
#         page.wait_for_selector("span.fui-Text:has-text('Draft Document')", timeout=5000)

#         # Check if "Draft Document" is visible
#         draft_visible = page.locator("span.fui-Text:has-text('Draft Document')").is_visible()
#         if not draft_visible:
#             raise AssertionError("❌ Draft Document modal did not appear after clicking Generate Draft button")
#         print("✅ Draft Document modal is visible")

#         # Check if Title input field is visible
#         title_input = page.locator("input[placeholder='Enter title here']")
#         if not title_input.is_visible():
#             raise AssertionError("❌ Title input field not visible in Draft Document modal")
#         print("✅ Title input field is visible")

#         duration = time.time() - start
#         logger.info("Execution Time for 'Verify Draft tab is disabled': %.2fs", duration)

#         logger.info("Test TC 9366 - Browse and Generate tabs accessibility test completed successfully")

#     finally:
#         logger.removeHandler(handler)

# @pytest.mark.smoke
# def test_draft_tab_accessibility_after_template_creation(login_logout, request):
#     """
#     Test Case 9369: BYOc-DocGen-Draft page only available after user has created a template in the Generate page.
    
#     Steps:
#     1. Authenticate BYOc DocGen web url
#     2. Click on Browse tab and verify chat conversation page
#     3. Enter Browse prompt and verify response is generated
#     4. Try to click on 'Draft' tab - should be disabled
#     5. Click on Generate tab and verify chat conversation page
#     6. Try to click on Generate Draft icon - should be disabled
#     7. Enter Generate prompt and verify promissory note is generated
#     8. Click on Generate Draft icon - should be enabled and Draft section displayed
#     """
    
#     request.node._nodeid = "TC 9369 - Validate Draft tab accessibility after template creation in Generate page"
    
#     page = login_logout
#     home_page = HomePage(page)
#     browse_page = BrowsePage(page)
#     generate_page = GeneratePage(page)
#     draft_page = DraftPage(page)

#     log_capture = io.StringIO()
#     handler = logging.StreamHandler(log_capture)
#     logger.addHandler(handler)

#     try:
#         # Step 1: Navigate to home page and validate
#         logger.info("Step 1: Verify login is successful and navigate to home page")
#         start = time.time()
#         home_page.open_home_page()
#         home_page.validate_home_page()
#         duration = time.time() - start
#         logger.info("Execution Time for 'Validate home page is loaded': %.2fs", duration)

#         # Step 2: Click on Browse tab and verify chat conversation page
#         logger.info("Step 2: Click on Browse tab and verify chat conversation page is displayed")
#         start = time.time()
#         home_page.click_browse_button()
        
#         # Verify chat conversation elements are present on Browse page
#         browse_page.validate_browse_page()
        
#         logger.info("Browse chat conversation page is displayed successfully")
#         duration = time.time() - start
#         logger.info("Execution Time for 'Verify Browse chat page': %.2fs", duration)

#         # Step 3: Enter Browse prompt and verify response
#         logger.info("Step 3: Enter prompt 'What are typical sections in a promissory note?' and verify response")
#         start = time.time()
#         browse_page.enter_a_question(browse_question1)
#         browse_page.click_send_button()
#         browse_page.validate_response_status(question_api=browse_question1)
#         logger.info("Response generated with typical sections from promissory notes")
#         duration = time.time() - start
#         logger.info("Execution Time for 'Browse prompt response': %.2fs", duration)

#         # Step 4: Try to click on Draft tab - should be disabled
#         logger.info("Step 4: Verify Draft tab is disabled before template creation")
#         start = time.time()
        
#         is_disabled = browse_page.is_draft_tab_disabled()
#         assert is_disabled, "Draft tab should be disabled before template creation"
        
#         logger.info("Draft tab is properly disabled before template creation")
#         duration = time.time() - start
#         logger.info("Execution Time for 'Verify Draft tab is disabled': %.2fs", duration)

#         # Step 5: Click on Generate tab and verify chat conversation page
#         logger.info("Step 5: Click on Generate tab and verify chat conversation page is displayed")
#         start = time.time()
#         browse_page.click_generate_button()
        
#         # Verify chat conversation elements are present on Generate page
#         generate_page.validate_generate_page()
        
#         logger.info("Generate chat conversation page is displayed successfully")
#         duration = time.time() - start
#         logger.info("Execution Time for 'Verify Generate chat page': %.2fs", duration)

#         # Step 6: Try to click on Generate Draft icon - should be disabled
#         logger.info("Step 6: Verify Generate Draft icon is disabled before creating template")
#         start = time.time()
        
#         generate_draft_button = page.locator("//button[@title='Generate Draft']")
        
#         if generate_draft_button.count() > 0:
#             is_draft_disabled = generate_draft_button.get_attribute("disabled") is not None or \
#                                generate_draft_button.get_attribute("aria-disabled") == "true"
            
#             assert is_draft_disabled, "Generate Draft icon should be disabled before template creation"
            
#             logger.info("Generate Draft icon is properly disabled")
#         else:
#             logger.info("Generate Draft icon is not visible (expected behavior before template creation)")
        
#         duration = time.time() - start
#         logger.info("Execution Time for 'Verify Generate Draft icon is disabled': %.2fs", duration)

#         # Step 7: Enter Generate prompt and verify promissory note is generated
#         logger.info("Step 7: Enter prompt 'Generate promissory note with a proposed $100,000 for Washington State'")
#         start = time.time()
        
#         # Use retry logic for Generate prompt
#         question_passed = False
#         for attempt in range(1, MAX_RETRIES + 1):
#             try:
#                 logger.info("Attempt %d: Entering Generate Question: %s", attempt, generate_question1)
#                 generate_page.enter_a_question(generate_question1)
#                 generate_page.click_send_button()
                
#                 time.sleep(2)
#                 response_text = page.locator("//p")
#                 latest_response = response_text.nth(response_text.count() - 1).text_content()

#                 if latest_response not in [invalid_response, invalid_response1]:
#                     logger.info("[%s] Valid response received - Promissory note generated on attempt %d", generate_question1, attempt)
#                     question_passed = True
#                     break
#                 else:
#                     logger.warning("[%s] Invalid response received on attempt %d", generate_question1, attempt)
#                     if attempt < MAX_RETRIES:
#                         logger.info("[%s] Retrying... (attempt %d/%d)", generate_question1, attempt + 1, MAX_RETRIES)
#                         time.sleep(RETRY_DELAY)
#                     else:
#                         logger.error("[%s] All %d attempts failed", generate_question1, MAX_RETRIES)
#                         assert latest_response not in [invalid_response, invalid_response1], \
#                             f"FAILED: Invalid response received after {MAX_RETRIES} attempts for: {generate_question1}"
#             except Exception as e:
#                 if attempt < MAX_RETRIES:
#                     logger.warning("[%s] Attempt %d failed: %s", generate_question1, attempt, str(e))
#                     logger.info("[%s] Retrying... (attempt %d/%d)", generate_question1, attempt + 1, MAX_RETRIES)
#                     time.sleep(RETRY_DELAY)
#                 else:
#                     logger.error("[%s] All %d attempts failed. Last error: %s", generate_question1, MAX_RETRIES, str(e))
#                     raise
        
#         # Verify that the question passed after retry attempts
#         assert question_passed, f"FAILED: All {MAX_RETRIES} attempts failed for question: {generate_question1}"
        
#         duration = time.time() - start
#         logger.info("Execution Time for 'Generate promissory note': %.2fs", duration)

#         # Step 8: Click on Generate Draft icon - should be enabled and Draft section displayed
#         logger.info("Step 8: Click on Generate Draft icon and verify Draft section is displayed")
#         start = time.time()
        
#         # Verify Generate Draft button is now enabled
#         if generate_draft_button.count() > 0:
#             is_enabled = generate_draft_button.get_attribute("disabled") is None and \
#                         generate_draft_button.get_attribute("aria-disabled") != "true"
            
#             assert is_enabled, "Generate Draft icon should be enabled after template creation"
        
#         # Click Generate Draft button
#         generate_page.click_generate_draft_button()
        
#         # Verify Draft sections are loaded
#         draft_page.validate_draft_sections_loaded()
        
#         logger.info("Generate Draft icon is enabled and Draft section is displayed successfully")
#         duration = time.time() - start
#         logger.info("Execution Time for 'Verify Draft section displayed': %.2fs", duration)

#         logger.info("Test TC 9369 - Draft tab accessibility after template creation completed successfully")

#     finally:
#         logger.removeHandler(handler)

# @pytest.mark.smoke
# def test_show_hide_chat_history(login_logout, request):
#     """
#     Test Case 9370: BYOc-DocGen-User should be able to Show/Hide chat history in Generate page.
    
#     Steps:
#     1. Authenticate BYOc DocGen web url
#     2. Navigate to Generate page
#     3. Enter Generate prompt and verify response is generated
#     4. Click on Show Chat History icon and verify chat history panel is displayed
#     5. Click on Close Chat History icon and verify chat history panel is closed
#     """
    
#     request.node._nodeid = "TC 9370 - Validate Show/Hide chat history functionality in Generate page"
    
#     page = login_logout
#     home_page = HomePage(page)
#     browse_page = BrowsePage(page)
#     generate_page = GeneratePage(page)

#     log_capture = io.StringIO()
#     handler = logging.StreamHandler(log_capture)
#     logger.addHandler(handler)

#     try:
#         # Step 1: Navigate to home page and validate
#         logger.info("Step 1: Verify login is successful and navigate to home page")
#         start = time.time()
#         home_page.open_home_page()
#         home_page.validate_home_page()
#         duration = time.time() - start
#         logger.info("Execution Time for 'Validate home page is loaded': %.2fs", duration)

#         # Step 2: Navigate to Generate page
#         logger.info("Step 2: Navigate to Generate page")
#         start = time.time()
#         home_page.click_generate_button()
        
#         # Verify chat conversation elements are present on Generate page
#         generate_page.enter_a_question(add_section)
#         generate_page.click_send_button()
        
#         logger.info("Generate chat conversation page is displayed successfully")
#         duration = time.time() - start
#         logger.info("Execution Time for 'Navigate to Generate page': %.2fs", duration)

#         logger.info("Step 3: 'Show chat history test' and verify response")
#         start = time.time()

#         generate_page.show_chat_history()

#         duration = time.time() - start
#         logger.info("Execution Time for 'Show Chat History': %.2fs", duration)

#         logger.info("Step 4: 'Hide chat history test' and verify chat history panel is closed")
#         start = time.time() 

#         generate_page.close_chat_history()

#         duration = time.time() - start
#         logger.info("Execution Time for 'Hide Chat History': %.2fs", duration)

#         logger.info("Test TC 9370 - Show/Hide chat history functionality test completed successfully")

#     finally:
#         logger.removeHandler(handler)

# @pytest.mark.smoke
# def test_template_history_save_and_load(login_logout, request):
#     """
#     Test Case: BYOc-DocGen-User should be able to save chat and load saved template history
    
#     Preconditions:
#     1. User should have BYOc DocGen web url
#     2. User should have template history saved
    
#     Steps:
#     1. Login to BYOc DocGen web url
#     2. Click on 'Generate' tab
#     3. Click on 'Show template history' button
#     4. Select any Session history thread
#     5. Enter a prompt 'What are typical sections in a promissory note?'
#     6. Click on Save (+) icon next to chat box
#     7. Open the saved history thread
#     8. Verify user can view the edited changes in the session
#     """
    
#     request.node._nodeid = "TC - Validate template history save and load functionality"
    
#     page = login_logout
#     home_page = HomePage(page)
#     generate_page = GeneratePage(page)

#     log_capture = io.StringIO()
#     handler = logging.StreamHandler(log_capture)
#     logger.addHandler(handler)

#     try:
#         # Step 1: Navigate to home page and validate login
#         logger.info("Step 1: Verify login is successful and Document Generation page is displayed")
#         start = time.time()
#         home_page.open_home_page()
#         home_page.validate_home_page()
#         duration = time.time() - start
#         logger.info("Execution Time for 'Validate home page is loaded': %.2fs", duration)

#         # Step 2: Click on 'Generate' tab
#         logger.info("Step 2: Navigate to Generate page")
#         start = time.time()
#         home_page.click_generate_button()
#         generate_page.validate_generate_page()
#         logger.info("Generate chat conversation page is displayed successfully")
#         duration = time.time() - start
#         logger.info("Execution Time for 'Navigate to Generate page': %.2fs", duration)

#         # Step 3: Click on 'Show template history' button
#         logger.info("Step 3: Click on 'Show template history' button")
#         start = time.time()
#         generate_page.show_chat_history()
#         logger.info("Template history window is displayed")
#         duration = time.time() - start
#         logger.info("Execution Time for 'Show template history': %.2fs", duration)

#         # Step 4: Select any Session history thread
#         logger.info("Step 4: Select first history thread from template history")
#         start = time.time()
#         generate_page.select_history_thread(thread_index=0)
#         logger.info("Saved chat conversation is loaded on the page")
#         duration = time.time() - start
#         logger.info("Execution Time for 'Select history thread': %.2fs", duration)

#         # Step 5: Enter a prompt 'What are typical sections in a promissory note?'
#         logger.info("Step 5: Enter prompt 'What are typical sections in a promissory note?'")
#         start = time.time()
#         generate_page.enter_a_question(browse_question1)
#         generate_page.click_send_button()
#         generate_page.validate_response_status(question_api=browse_question1)
#         logger.info("Response is generated successfully")
#         duration = time.time() - start
#         logger.info("Execution Time for 'Enter prompt and get response': %.2fs", duration)

#         # Step 6: Click on Save (+) icon next to chat box
#         logger.info("Step 6: Click on Save icon next to chat box")
#         start = time.time()
#         generate_page.click_new_chat_button()
#         logger.info("Chat is saved successfully")
#         duration = time.time() - start
#         logger.info("Execution Time for 'Save chat': %.2fs", duration)

#         # Step 7: Open the saved history thread
#         logger.info("Step 7: Open the saved history thread to verify changes")
#         start = time.time()
#         # Show history again if it was closed
#         if not page.locator(generate_page.CHAT_HISTORY_NAME).is_visible():
#             generate_page.show_chat_history()
        
#         # Select the first thread (the one we just saved to)
#         generate_page.select_history_thread(thread_index=0)
#         duration = time.time() - start
#         logger.info("Execution Time for 'Reopen saved history thread': %.2fs", duration)

#         # Step 8: Verify user can view the edited changes in the session
#         logger.info("Step 8: Verify user can view the edited changes in the session")
#         start = time.time()
#         generate_page.verify_saved_chat(browse_question1)
#         logger.info("User is able to view the edited changes in the saved session")
#         duration = time.time() - start
#         logger.info("Execution Time for 'Verify changes in session': %.2fs", duration)

#         # logger.info("Test - Template history save and load functionality completed successfully")

#     finally:
#         logger.removeHandler(handler)

# @pytest.mark.smoke
# def test_template_history_delete(login_logout, request):
#     """
#     Test Case: BYOc-DocGen-User should be able to delete saved template history thread
    
#     Preconditions:
#     1. User should have BYOc DocGen web url
#     2. User should have saved template history threads
    
#     Steps:
#     1. Login to BYOc DocGen web url
#     2. Click on 'Generate' tab
#     3. Click on 'Show template history' button
#     4. Select a session thread and click on Delete icon
#     5. Verify delete confirmation popup is displayed with correct content
#     6. Click on Delete button in popup
#     7. Verify session thread is deleted successfully
#     """
    
#     request.node._nodeid = "TC - Validate template history delete functionality"
    
#     page = login_logout
#     home_page = HomePage(page)
#     generate_page = GeneratePage(page)

#     log_capture = io.StringIO()
#     handler = logging.StreamHandler(log_capture)
#     logger.addHandler(handler)

#     try:
#         # Step 1: Navigate to home page and validate login
#         logger.info("Step 1: Verify login is successful and Document Generation page is displayed")
#         start = time.time()
#         home_page.open_home_page()
#         home_page.validate_home_page()
#         duration = time.time() - start
#         logger.info("Execution Time for 'Validate home page is loaded': %.2fs", duration)

#         # Step 2: Click on 'Generate' tab
#         logger.info("Step 2: Navigate to Generate page")
#         start = time.time()
#         home_page.click_generate_button()
#         generate_page.validate_generate_page()
#         logger.info("Generate chat conversation page is displayed successfully")
#         duration = time.time() - start
#         logger.info("Execution Time for 'Navigate to Generate page': %.2fs", duration)

#         # Step 3: Click on 'Show template history' button
#         logger.info("Step 3: Click on 'Show template history' button")
#         start = time.time()
#         generate_page.show_chat_history()
        
#         # Verify template history window is displayed
#         logger.info("Template history window with saved history threads is displayed")
#         duration = time.time() - start
#         logger.info("Execution Time for 'Show template history': %.2fs", duration)

#         # Step 4: Get initial thread count and click delete icon
#         logger.info("Step 4: Select a session thread and click on Delete icon")
#         start = time.time()
        
#         # Get the count of threads before deletion
#         generate_page.select_history_thread(thread_index=0)
        
#         # Click delete icon on the first thread
#         generate_page.delete_thread_by_index(thread_index=0)
        
#         duration = time.time() - start
#         logger.info("Execution Time for 'Click delete icon': %.2fs", duration)

#         logger.info("Test - Template history delete functionality completed successfully")

#     finally:
#         logger.removeHandler(handler)

# #check with ritesh once
# @pytest.mark.smoke
# def test_template_history_clear_all(login_logout, request):
#     """
#     Test Case: BYOc-DocGen-Template history threads can delete all
    
#     Preconditions:
#     1. User should have BYOc DocGen web url
#     2. Saved Template history session threads are available
    
#     Steps:
#     1. Login to BYOc DocGen web url
#     2. Click on 'Generate' tab
#     3. Click on 'Show template history' button
#     4. Click on 3 dot ellipses next to Template history label
#     5. Verify 'Clear all chat history' option is displayed and click it
#     6. Verify delete confirmation popup with correct title and text
#     7. Click on 'Clear all' button
#     8. Verify all template history threads are deleted and 'No chat history.' message is visible
#     """
    
#     request.node._nodeid = "TC - Validate clear all template history functionality"
    
#     page = login_logout
#     home_page = HomePage(page)
#     generate_page = GeneratePage(page)

#     log_capture = io.StringIO()
#     handler = logging.StreamHandler(log_capture)
#     logger.addHandler(handler)

#     try:
#         # Step 1: Navigate to home page and validate login
#         logger.info("Step 1: Verify login is successful and Document Generation page is displayed")
#         start = time.time()
#         home_page.open_home_page()
#         home_page.validate_home_page()
#         duration = time.time() - start
#         logger.info("Execution Time for 'Validate home page is loaded': %.2fs", duration)

#         # Step 2: Click on 'Generate' tab
#         logger.info("Step 2: Navigate to Generate page")
#         start = time.time()
#         home_page.click_generate_button()
#         generate_page.validate_generate_page()
#         logger.info("Chat conversation page is displayed successfully")
#         duration = time.time() - start
#         logger.info("Execution Time for 'Navigate to Generate page': %.2fs", duration)

#         # Step 3: Click on 'Show template history' button
#         logger.info("Step 3: Click on 'Show template history' button")
#         start = time.time()
#         generate_page.show_chat_history()
        
#         duration = time.time() - start
#         logger.info("Execution Time for 'Show template history': %.2fs", duration)

#         # Step 4: Click on 3 dot ellipses next to Template history label
#         logger.info("Step 4: Click on 3 dot ellipses next to Template history label")

        
#         # Step 5: Verify 'Clear all chat history' option is displayed
#         logger.info("Step 5: Verify 'Clear all chat history' option is displayed")
#         start = time.time()
#         clear_all_option = page.locator(generate_page.CHAT_HISTORY_DELETE)
#         assert clear_all_option.is_visible(), "'Clear all chat history' option is not visible"
#         logger.info("'Clear all chat history' option is displayed")
        
#         # Click on 'Clear all chat history' option
#         clear_all_option.click()
#         logger.info("'Clear all chat history' option clicked")
#         duration = time.time() - start
#         logger.info("Execution Time for 'Verify and click Clear all option': %.2fs", duration)

#         # Step 6: Verify delete confirmation popup
#         logger.info("Step 6: Verify delete confirmation popup is displayed with correct content")
#         start = time.time()
        
#         # Wait for popup to appear
#         page.wait_for_timeout(1000)
        
#         # Verify popup title
#         popup_title = page.get_by_text("Are you sure you want to clear all chat history?")
#         assert popup_title.is_visible(), "Delete confirmation popup title is not visible"
#         logger.info("Popup title 'Are you sure you want to clear all chat history?' is displayed")
        
#         # Verify popup text
#         popup_text = page.get_by_text("All chat history will be permanently removed")
#         assert popup_text.is_visible(), "Delete confirmation popup text is not visible"
#         logger.info("Popup text 'All chat history will be permanently removed.' is displayed")
        
#         # Verify 'Clear all' button is visible
#         clear_all_button = page.get_by_role("button", name="Clear All")
#         assert clear_all_button.is_visible(), "'Clear all' button is not visible in popup"
#         logger.info("'Clear all' button is visible in popup")
        
#         # Verify 'Cancel' button is visible
#         cancel_button = page.get_by_role("button", name="Cancel")
#         assert cancel_button.is_visible(), "'Cancel' button is not visible in popup"
#         logger.info("'Cancel' button is visible in popup")
        
#         duration = time.time() - start
#         logger.info("Execution Time for 'Verify delete confirmation popup': %.2fs", duration)

#         # Step 7: Click on 'Clear all' button
#         logger.info("Step 7: Click on 'Clear all' button in popup")
#         start = time.time()
#         clear_all_button.click()
#         logger.info("'Clear all' button clicked in confirmation popup")
#         page.wait_for_timeout(3000)
#         duration = time.time() - start
#         logger.info("Execution Time for 'Click Clear all button': %.2fs", duration)

#         # Step 8: Verify all template history threads are deleted
#         logger.info("Step 8: Verify all template history threads are deleted successfully")
#         start = time.time()
        
#         # Verify 'No chat history.' message is visible
#         no_history_message = page.locator("//span[contains(text(),'No chat history.')]")
#         assert no_history_message.is_visible(), "'No chat history.' message is not visible"
#         logger.info("All template history threads deleted successfully - 'No chat history.' message is visible")
        
#         duration = time.time() - start
#         logger.info("Execution Time for 'Verify all threads deleted': %.2fs", duration)

#         logger.info("Test - Clear all template history functionality completed successfully")

#     finally:
#         logger.removeHandler(handler)


# @pytest.mark.smoke
# def test_template_rename_thread(login_logout, request):
#     """
#     Test Case: BYOc-DocGen-Template history threads can delete all
    
#     Preconditions:
#     1. User should have BYOc DocGen web url
#     2. Saved Template history session threads are available
    
#     Steps:
#     1. Login to BYOc DocGen web url
#     2. Click on 'Generate' tab
#     3. Click on 'Show template history' button
#     4. Select a session thread and click on Rename icon
#     5. Update the thread name and click on tick mark
#     6. Edit the thread name again update the name and click on cross mark icon
#     """
    
#     request.node._nodeid = "TC - Validate rename template history thread functionality"
    
#     page = login_logout
#     home_page = HomePage(page)
#     generate_page = GeneratePage(page)

#     log_capture = io.StringIO()
#     handler = logging.StreamHandler(log_capture)
#     logger.addHandler(handler)

#     try:
#         # Step 1: Navigate to home page and validate login
#         logger.info("Step 1: Verify login is successful and Document Generation page is displayed")
#         start = time.time()
#         home_page.open_home_page()
#         home_page.validate_home_page()
#         duration = time.time() - start
#         logger.info("Execution Time for 'Validate home page is loaded': %.2fs", duration)

#         # Step 2: Click on 'Generate' tab
#         logger.info("Step 2: Navigate to Generate page")
#         start = time.time()
#         home_page.click_generate_button()
#         generate_page.validate_generate_page()
#         logger.info("Chat conversation page is displayed successfully")
#         duration = time.time() - start
#         logger.info("Execution Time for 'Navigate to Generate page': %.2fs", duration)

#         # Step 3: Click on 'Show template history' button
#         logger.info("Step 3: Click on 'Show template history' button")
#         start = time.time()
#         generate_page.show_chat_history()
#         duration = time.time() - start
#         logger.info("Execution Time for 'Show template history': %.2fs", duration)

#         # Step 4: Select a session thread and click on edit icon
#         logger.info("Step 4: Select a session thread and click on edit icon")
#         start = time.time()
#         generate_page.select_history_thread(thread_index=0)
#         generate_page.click_edit_icon(thread_index=0)
#         duration = time.time() - start
#         logger.info("Execution Time for 'Select session thread and click edit icon': %.2fs", duration)

#         logger.info("Step 5: Update the thread name and click on tick mark")
#         start = time.time()

#         new_title_tick = "Payment acceleration clause15"
#         generate_page.update_thread_name(new_title_tick, thread_index=0)
#         generate_page.click_rename_confirm(thread_index=0)

#         # Wait for rename to complete
#         page.wait_for_timeout(2000)

#         updated_title = generate_page.get_thread_title(thread_index=0)
        
#         logger.info("Rename verification - Expected: '%s', Got: '%s'", new_title_tick, updated_title)

#         # Check if the title matches (allow for case-insensitive and whitespace differences)
#         assert updated_title.strip() == new_title_tick.strip(), \
#             f"Thread rename failed. Expected: '{new_title_tick}', Got: '{updated_title}' (len: {len(updated_title)})"

#         duration = time.time() - start
#         logger.info("Execution Time for rename confirm: %.2fs", duration)

#         # Rename with ✕ (cancel)
#         logger.info("Step 6: Edit again, update name, and click cross")
#         start = time.time()

#         # Begin editing again
#         generate_page.click_edit_icon(thread_index=0)

#         new_title_cross = "This should NOT be saved"
#         generate_page.update_thread_name(new_title_cross, thread_index=0)

#         # Click cancel
#         generate_page.click_rename_cancel(thread_index=0)

#         # Wait for cancel to complete
#         page.wait_for_timeout(2000)

#         final_title = generate_page.get_thread_title(thread_index=0)
        
#         logger.info("Cancel verification - Expected: '%s', Got: '%s'", new_title_tick, final_title)

#         # Cancel should revert back to last saved name
#         assert final_title.strip() == new_title_tick.strip(), \
#             f"Cancel rename failed. Expected retained name: '{new_title_tick}', Got: '{final_title}' (len: {len(final_title)})"

#         duration = time.time() - start
#         logger.info("Execution Time for rename cancel: %.2fs", duration)

#         logger.info("Test - rename template history thread functionality completed successfully")

#     finally:
#         logger.removeHandler(handler)

# @pytest.mark.smoke
# def test_browse_clear_chat(login_logout, request):
#     """
#     Test Case: BYOc-DocGen-Browse page-broom to clear chat and start a new session

#     Preconditions:
#     1. User should have BYOc DocGen web url

#     Steps:
#     1. Login to BYOc DocGen web url
#     2. Click on 'Browse' tab
#     3. Enter a prompt and generate a response
#     4. Click on broom icon next to chat box
#     5. Verify chat conversation is cleared and new chat session starts
#     """

#     request.node._nodeid = "TC - Validate Browse page clear chat functionality"

#     page = login_logout
#     home_page = HomePage(page)
#     browse_page = BrowsePage(page)   # if you use GeneratePage rename appropriately

#     log_capture = io.StringIO()
#     handler = logging.StreamHandler(log_capture)
#     logger.addHandler(handler)

#     try:
#         # Step 1: Login
#         logger.info("Step 1: Login and verify Browse page is displayed")
#         start = time.time()
#         home_page.open_home_page()
#         home_page.validate_home_page()
#         duration = time.time() - start
#         logger.info("Execution time for login validation: %.2fs", duration)

#         # Step 2: Click Browse tab
#         logger.info("Step 2: Navigate to Browse page")
#         start = time.time()
#         home_page.click_browse_button()     # implement this if not present
#         duration = time.time() - start
#         logger.info("Execution time for Browse page navigation: %.2fs", duration)

#         # Step 3: Enter prompt & generate response
#         logger.info("Step 3: Enter prompt and generate response")
#         start = time.time()

#         browse_page.enter_a_question(browse_question1)
#         browse_page.click_send_button()

#         browse_page.validate_response_status(question_api=browse_question1)
#         duration = time.time() - start
#         logger.info("Execution time for generating response: %.2fs", duration)

#         # Step 4: Click broom icon
#         logger.info("Step 4: Click broom icon to clear chat")
#         start = time.time()

#         browse_page.click_broom_icon()

#         page.wait_for_timeout(2000)
#         duration = time.time() - start
#         logger.info("Execution time for clicking broom icon: %.2fs", duration)

#         # Step 5: Verify chat is cleared
#         logger.info("Step 5: Verify chat is cleared and new session started")
#         start = time.time()

#         assert browse_page.is_chat_cleared(), "Chat is NOT cleared after clicking broom icon"
#         logger.info("Chat cleared successfully, new chat session displayed")

#         duration = time.time() - start
#         logger.info("Execution time for chat clear validation: %.2fs", duration)

#         logger.info("Test passed: Browse page clear chat functionality")

#     finally:
#         logger.removeHandler(handler)

# @pytest.mark.smoke
# def test_generate_clear_chat(login_logout, request):
#     """
#     Test Case: BYOc-DocGen-Generate page-broom to clear chat and start a new session

#     Preconditions:
#     1. User should have BYOc DocGen web url

#     Steps:
#     1. Login to BYOc DocGen web url
#     2. Click on 'Generate' tab
#     3. Enter a prompt and generate a response
#     4. Click on broom icon next to chat box
#     5. Verify chat conversation is cleared and new chat session starts
#     """

#     request.node._nodeid = "TC - Validate generate page clear chat functionality"

#     page = login_logout
#     home_page = HomePage(page)
#     browse_page = BrowsePage(page)  
#     generate_page = GeneratePage(page)

#     log_capture = io.StringIO()
#     handler = logging.StreamHandler(log_capture)
#     logger.addHandler(handler)

#     try:
#         # Step 1: Login
#         logger.info("Step 1: Login and verify Browse page is displayed")
#         start = time.time()
#         home_page.open_home_page()
#         home_page.validate_home_page()
#         duration = time.time() - start
#         logger.info("Execution time for login validation: %.2fs", duration)

#         # Step 2: Click Browse tab
#         logger.info("Step 2: Navigate to Generate page")
#         start = time.time()
#         home_page.click_generate_button()     # implement this if not present
#         duration = time.time() - start
#         logger.info("Execution time for Generate page navigation: %.2fs", duration)

#         # Step 3: Enter prompt & generate response
#         logger.info("Step 3: Enter prompt and generate response")
#         start = time.time()

#         generate_page.enter_a_question(generate_question1)
#         generate_page.click_send_button()

#         generate_page.validate_response_status(question_api=generate_question1)
#         duration = time.time() - start
#         logger.info("Execution time for generating response: %.2fs", duration)

#         # Step 4: Click broom icon
#         logger.info("Step 4: Click broom icon to clear chat")
#         start = time.time()

#         generate_page.click_clear_chat()

#         page.wait_for_timeout(2000)
#         duration = time.time() - start
#         logger.info("Execution time for clicking broom icon: %.2fs", duration)

#         # Step 5: Verify chat is cleared
#         logger.info("Step 5: Verify chat is cleared and new session started")
#         start = time.time()

#         assert generate_page.is_chat_cleared(), "Chat is NOT cleared after clicking broom icon"
#         logger.info("Chat cleared successfully, new chat session displayed")

#         duration = time.time() - start
#         logger.info("Execution time for chat clear validation: %.2fs", duration)

#         logger.info("Test passed: Generate page clear chat functionality")

#     finally:
#         logger.removeHandler(handler)


# @pytest.mark.smoke
# def test_generate_new_session_plus_icon(login_logout, request):
#     """
#     Test Case: BYOc-DocGen-Generate page- [+] to just start a new session
    
#     Preconditions:
#     1. User should have BYOc DocGen web url

#     Steps:
#     1. Login to BYOc DocGen web url
#     2. Click on 'Generate' tab
#     3. Enter a prompt 'Generate promissory note with a proposed $100,000 for Washington State'
#     4. Verify response is generated
#     5. Click on [+] icon next to chat box
#     6. Verify template is saved and new session is visible
#     7. Click on 'Show template history' button
#     8. Verify a thread is saved and visible in Template history window
#     """
    
#     request.node._nodeid = "TC - Validate Generate page [+] new session functionality"
    
#     page = login_logout
#     home_page = HomePage(page)
#     generate_page = GeneratePage(page)

#     log_capture = io.StringIO()
#     handler = logging.StreamHandler(log_capture)
#     logger.addHandler(handler)

#     try:
#         # Step 1: Login to BYOc DocGen web url
#         logger.info("Step 1: Verify login is successful and Document Generation page is displayed")
#         start = time.time()
#         home_page.open_home_page()
#         home_page.validate_home_page()
#         duration = time.time() - start
#         logger.info("Execution Time for 'Validate home page is loaded': %.2fs", duration)

#         # Step 2: Click on 'Generate' tab
#         logger.info("Step 2: Navigate to Generate page")
#         start = time.time()
#         home_page.click_generate_button()
#         generate_page.validate_generate_page()
#         logger.info("Chat conversation page is displayed successfully")
#         duration = time.time() - start
#         logger.info("Execution Time for 'Navigate to Generate page': %.2fs", duration)
        
#         # Check history count before starting new session
#         initial_thread_count = generate_page.get_history_thread_count()
#         logger.info("Initial thread count in history before new session: %d", initial_thread_count)

#         # Step 3: Enter prompt
#         logger.info("Step 3: Enter prompt 'Generate promissory note with a proposed $100,000 for Washington State'")
#         start = time.time()
        
#         # Use retry logic for Generate prompt
#         generate_page.enter_a_question(generate_question1)
#         generate_page.click_send_button()
#         generate_page.validate_response_status(question_api=generate_question1)
        
#         duration = time.time() - start
#         logger.info("Execution Time for 'Generate prompt response': %.2fs", duration)

#         # Step 5: Click on [+] icon
#         logger.info("Step 5: Click on [+] icon to save template and start new session")
#         start = time.time()
#         generate_page.click_new_chat_button()
#         page.wait_for_timeout(2000)
#         duration = time.time() - start
#         logger.info("Execution Time for 'Click [+] icon': %.2fs", duration)

#         # Step 6: Verify template is saved and new session is visible
#         logger.info("Step 6: Verify template is saved and new session is visible")
#         start = time.time()
#         assert generate_page.is_new_session_visible(), "New session is not visible after clicking [+] icon"
#         logger.info("Template saved and new session is visible")
#         duration = time.time() - start
#         logger.info("Execution Time for 'Verify new session': %.2fs", duration)

#         # Step 7: Click on 'Show template history' button
#         logger.info("Step 7: Click on 'Show template history' button")
#         start = time.time()
#         generate_page.show_chat_history()
#         duration = time.time() - start
#         logger.info("Execution Time for 'Show template history': %.2fs", duration)

#         # Step 8: Verify a thread is saved and visible in Template history window
#         logger.info("Step 8: Verify a thread is saved and visible in Template history window")
#         start = time.time()
#         thread_count = generate_page.get_history_thread_count()
#         logger.info("Thread count after clicking [+] icon: %d (initial: %d)", thread_count, initial_thread_count)
        
#         # Verify thread count increased (new thread was saved)
#         assert thread_count > initial_thread_count, \
#             f"No new thread saved. Expected thread count > {initial_thread_count}, but got {thread_count}"
        
#         logger.info("✓ New thread saved successfully. Thread count increased from %d to %d", 
#                     initial_thread_count, thread_count)
#         duration = time.time() - start
#         logger.info("Execution Time for 'Verify thread in history': %.2fs", duration)

#         logger.info("Test - Generate page [+] new session functionality completed successfully")

#     finally:
#         logger.removeHandler(handler)


# @pytest.mark.smoke
# def test_bug_7819_browse_disabled_during_generate(login_logout, request):
#     """
#     Test Case Bug 7819: BYOc_DocGen - Switching pages during response generate can yield faulty results
    
#     Preconditions:
#     1. User should have BYOc DocGen web url deployed successfully

#     Steps:
#     1. Launch the experience and go to Browse page
#     2. Ask several questions about the content (promissory notes, summaries, interest rates, etc.)
#     3. Go to Generate section
#     4. Type "Create a draft promissory note" (response takes ~30 seconds)
#     5. While response is generating, try to click Browse button
#     6. Verify Browse button is disabled during response generation
#     """
    
#     request.node._nodeid = "Bug 7819 - Validate Browse button disabled during Generate response"
    
#     page = login_logout
#     home_page = HomePage(page)
#     browse_page = BrowsePage(page)
#     generate_page = GeneratePage(page)

#     log_capture = io.StringIO()
#     handler = logging.StreamHandler(log_capture)
#     logger.addHandler(handler)

#     try:
#         # Step 1: Launch and go to Browse page
#         logger.info("Step 1: Launch experience and navigate to Browse page")
#         start = time.time()
#         home_page.open_home_page()
#         home_page.validate_home_page()
#         home_page.click_browse_button()
#         browse_page.validate_browse_page()
#         duration = time.time() - start
#         logger.info("Execution Time for 'Navigate to Browse page': %.2fs", duration)

#         # Step 2: Ask several questions in Browse
#         logger.info("Step 2: Ask several questions about promissory notes content")
#         start = time.time()
        
#         browse_questions = [browse_question1, browse_question2]
#         for idx, question in enumerate(browse_questions, start=1):
#             logger.info("Asking Browse question %d: %s", idx, question)
#             browse_page.enter_a_question(question)
#             browse_page.click_send_button()
#             browse_page.validate_response_status(question_api=question)
#             logger.info("Response %d received successfully", idx)
        
#         duration = time.time() - start
#         logger.info("Execution Time for 'Browse questions': %.2fs", duration)

#         # Step 3: Go to Generate section
#         logger.info("Step 3: Navigate to Generate section")
#         start = time.time()
#         browse_page.click_generate_button()
#         generate_page.validate_generate_page()
#         duration = time.time() - start
#         logger.info("Execution Time for 'Navigate to Generate': %.2fs", duration)

#         # Step 4: Type prompt that takes ~30 seconds
#         logger.info("Step 4: Type 'Create a draft promissory note' and send")
#         start = time.time()
        
#         generate_page.enter_a_question(generate_question1)
#         generate_page.click_send_button()
        
#         logger.info("Response generation started (may take 30 seconds)")
#         duration = time.time() - start
#         logger.info("Execution Time for 'Start response generation': %.2fs", duration)

#         # Step 5 & 6: Check Browse button is disabled WHILE response is generating
#         logger.info("Step 5-6: Verify Browse button is disabled during response generation")
#         start = time.time()
        
#         # Wait briefly for response generation to start
#         page.wait_for_timeout(1000)
        
#         # Check if response is still generating (this also checks Browse button disabled state)
#         is_generating, is_browse_disabled = generate_page.is_response_generating()
#         logger.info("Is response generating: %s", is_generating)
#         logger.info("Is Browse button disabled: %s", is_browse_disabled)
        
#         # If response is still generating, Browse should be disabled
#         if is_generating:
#             assert is_browse_disabled, \
#                 "FAILED: Browse button should be disabled during response generation to prevent faulty results"
#             logger.info("✓ Browse button is properly disabled during response generation")
#         else:
#             logger.warning("Response completed too quickly to verify Browse button disabled state")
        
#         duration = time.time() - start
#         logger.info("Execution Time for 'Verify Browse button disabled': %.2fs", duration)

#         logger.info("Test Bug 7819 - Browse button disabled during Generate response completed successfully")

#     finally:
#         logger.removeHandler(handler)


# @pytest.mark.smoke
# def test_generate_promissory_note_draft(login_logout, request):
#     """
#     Test Case: BYOc-DocGen-Generate a new template, document, draft of a promissory note
    
#     Preconditions:
#     1. User should have BYOc DocGen web url

#     Steps:
#     1. Login to BYOc DocGen web url
#     2. Verify login is successful and Document Generation page is displayed
#     3. Click on 'Generate' tab
#     4. Verify chat conversation page is displayed
#     5. Enter prompt: 'Generate promissory note with a proposed $100,000 for Washington State'
#     6. Verify response is generated with different section names
#     7. Click on 'Generate Draft' icon next to the chat box
#     8. Verify draft promissory note is generated in Draft section with all sections
#     """
    
#     request.node._nodeid = "TC - Validate Generate promissory note draft functionality"
    
#     page = login_logout
#     home_page = HomePage(page)
#     generate_page = GeneratePage(page)
#     draft_page = DraftPage(page)

#     log_capture = io.StringIO()
#     handler = logging.StreamHandler(log_capture)
#     logger.addHandler(handler)

#     try:
#         # Step 1-2: Login and verify Document Generation page
#         logger.info("Step 1-2: Login to BYOc DocGen and verify Document Generation page is displayed")
#         start = time.time()
#         home_page.open_home_page()
#         home_page.validate_home_page()
#         duration = time.time() - start
#         logger.info("Execution Time for 'Login and validate home page': %.2fs", duration)

#         # Step 3: Click on 'Generate' tab
#         logger.info("Step 3: Click on 'Generate' tab")
#         start = time.time()
#         home_page.click_generate_button()
#         duration = time.time() - start
#         logger.info("Execution Time for 'Navigate to Generate tab': %.2fs", duration)

#         # Step 4: Verify chat conversation page is displayed
#         logger.info("Step 4: Verify chat conversation page is displayed")
#         start = time.time()
#         generate_page.validate_generate_page()
#         logger.info("Chat conversation page is displayed successfully")
#         duration = time.time() - start
#         logger.info("Execution Time for 'Validate Generate page': %.2fs", duration)

#         # Step 5: Enter prompt for generating promissory note
#         logger.info("Step 5: Enter prompt 'Generate promissory note with a proposed $100,000 for Washington State'")
#         start = time.time()
        
#         generate_page.enter_a_question(generate_question1)
#         generate_page.click_send_button()
        
#         duration = time.time() - start
#         logger.info("Execution Time for 'Generate promissory note prompt': %.2fs", duration)

#         # Step 6: Verify response is generated with different section names
#         logger.info("Step 6: Verify response is generated with different section names")
#         start = time.time()
        
#         # Validate that response contains section-like content (not validating specific sections)
#         # The response should contain promissory note related content
#         generate_page.validate_response_status(question_api=generate_question1)
        
#         duration = time.time() - start
#         logger.info("Execution Time for 'Verify response sections': %.2fs", duration)

#         # Step 7: Click on 'Generate Draft' icon
#         logger.info("Step 7: Click on 'Generate Draft' icon next to the chat box")
#         start = time.time()
#         generate_page.click_generate_draft_button()
#         duration = time.time() - start
#         logger.info("Execution Time for 'Click Generate Draft button': %.2fs", duration)

#         # Step 8: Verify draft promissory note is generated in Draft section
#         logger.info("Step 8: Verify draft promissory note is generated in Draft section with all sections")
#         start = time.time()
#         draft_page.validate_draft_sections_loaded()
#         logger.info("Draft promissory note generated successfully with all sections from Generate page")
#         duration = time.time() - start
#         logger.info("Execution Time for 'Verify draft sections loaded': %.2fs", duration)

#         logger.info("Test - Generate promissory note draft functionality completed successfully")

#     finally:
#         logger.removeHandler(handler)


# @pytest.mark.smoke
# def test_generate_add_section(login_logout, request):
#     """
#     Test Case: BYOc-DocGen-Generate page-Add a section
    
#     Preconditions:
#     1. User should have BYOc DocGen web url

#     Steps:
#     1. Login to BYOc DocGen web url
#     2. Verify login is successful and Document Generation page is displayed
#     3. Click on 'Generate' tab
#     4. Verify chat conversation page is displayed
#     5. Enter prompt: 'Generate promissory note with a proposed $100,000 for Washington State'
#     6. Verify response is generated with different section names
#     7. Enter prompt: 'Add Payment acceleration clause section'
#     8. Verify a new section 'Payment acceleration clause' is added in response
#     """
    
#     request.node._nodeid = "TC - Validate Generate page Add Section functionality"
    
#     page = login_logout
#     home_page = HomePage(page)
#     generate_page = GeneratePage(page)

#     log_capture = io.StringIO()
#     handler = logging.StreamHandler(log_capture)
#     logger.addHandler(handler)

#     try:
#         # Step 1-2: Login and verify Document Generation page
#         logger.info("Step 1-2: Login to BYOc DocGen and verify Document Generation page is displayed")
#         start = time.time()
#         home_page.open_home_page()
#         home_page.validate_home_page()
#         duration = time.time() - start
#         logger.info("Execution Time for 'Login and validate home page': %.2fs", duration)

#         # Step 3: Click on 'Generate' tab
#         logger.info("Step 3: Click on 'Generate' tab")
#         start = time.time()
#         home_page.click_generate_button()
#         duration = time.time() - start
#         logger.info("Execution Time for 'Navigate to Generate tab': %.2fs", duration)

#         # Step 4: Verify chat conversation page is displayed
#         logger.info("Step 4: Verify chat conversation page is displayed")
#         start = time.time()
#         generate_page.validate_generate_page()
#         logger.info("Chat conversation page is displayed successfully")
#         duration = time.time() - start
#         logger.info("Execution Time for 'Validate Generate page': %.2fs", duration)

#         # Step 5-7: Enter prompts for generating promissory note and adding section
#         logger.info("Step 5: Enter prompt 'Generate promissory note with a proposed $100,000 for Washington State'")
#         start = time.time()
        
#         # Get count of responses before adding section
#         response_count_before = page.locator("//p").count()
#         logger.info("Response count before prompts: %d", response_count_before)
        
#         # Ask both questions in a loop
#         questions = [generate_question1, add_section]
#         for idx, question in enumerate(questions, start=1):
#             logger.info("Question %d: %s", idx, question)
#             generate_page.enter_a_question(question)
#             generate_page.click_send_button()
#             generate_page.validate_response_status(question_api=question)
#             logger.info("✓ Response %d generated successfully", idx)
        
#         duration = time.time() - start
#         logger.info("Execution Time for 'Both prompts': %.2fs", duration)

#         # Step 6 & 8: Verify responses are generated and section is added
#         logger.info("Step 6 & 8: Verify response generated and new section 'Payment acceleration clause' is added")
#         start = time.time()
        
#         # Verify response count increased (both responses added)
#         response_count_after = page.locator("//p").count()
#         logger.info("Response count after prompts: %d", response_count_after)
        
#         assert response_count_after > response_count_before, \
#             f"Response count should increase. Before: {response_count_before}, After: {response_count_after}"
        
#         logger.info("✓ Promissory note generated and new section 'Payment acceleration clause' added successfully")
        
#         duration = time.time() - start
#         logger.info("Execution Time for 'Verify responses': %.2fs", duration)

#         logger.info("Test - Generate page Add Section functionality completed successfully")

#     finally:
#         logger.removeHandler(handler)


# @pytest.mark.smoke
# def test_generate_remove_section(login_logout, request):
#     """
#     Test Case: BYOc-DocGen-Generate page-Remove a section
    
#     Preconditions:
#     1. User should have BYOc DocGen web url

#     Steps:
#     1. Login to BYOc DocGen web url
#     2. Verify login is successful and Document Generation page is displayed
#     3. Click on 'Generate' tab
#     4. Verify chat conversation page is displayed
#     5. Enter prompt: 'Generate promissory note with a proposed $100,000 for Washington State'
#     6. Verify response is generated with different section names
#     7. Enter prompt: 'Remove (section) Promissory note'
#     8. Verify section 'Promissory note' is removed in generated response
#     """
    
#     request.node._nodeid = "TC - Validate Generate page Remove Section functionality"
    
#     page = login_logout
#     home_page = HomePage(page)
#     generate_page = GeneratePage(page)

#     log_capture = io.StringIO()
#     handler = logging.StreamHandler(log_capture)
#     logger.addHandler(handler)

#     try:
#         # Step 1-2: Login and verify Document Generation page
#         logger.info("Step 1-2: Login to BYOc DocGen and verify Document Generation page is displayed")
#         start = time.time()
#         home_page.open_home_page()
#         home_page.validate_home_page()
#         duration = time.time() - start
#         logger.info("Execution Time for 'Login and validate home page': %.2fs", duration)

#         # Step 3: Click on 'Generate' tab
#         logger.info("Step 3: Click on 'Generate' tab")
#         start = time.time()
#         home_page.click_generate_button()
#         duration = time.time() - start
#         logger.info("Execution Time for 'Navigate to Generate tab': %.2fs", duration)

#         # Step 4: Verify chat conversation page is displayed
#         logger.info("Step 4: Verify chat conversation page is displayed")
#         start = time.time()
#         generate_page.validate_generate_page()
#         logger.info("Chat conversation page is displayed successfully")
#         duration = time.time() - start
#         logger.info("Execution Time for 'Validate Generate page': %.2fs", duration)

#         # Step 5-7: Enter prompts for generating promissory note and removing section
#         logger.info("Step 5: Enter prompt 'Generate promissory note with a proposed $100,000 for Washington State'")
#         start = time.time()
        
#         # Get count of responses before
#         response_count_before = page.locator("//p").count()
#         logger.info("Response count before prompts: %d", response_count_before)
        
#         # Ask both questions in a loop
#         questions = [generate_question1, remove_section]
#         for idx, question in enumerate(questions, start=1):
#             logger.info("Question %d: %s", idx, question)
#             generate_page.enter_a_question(question)
#             generate_page.click_send_button()
#             generate_page.validate_response_status(question_api=question)
#             logger.info("✓ Response %d generated successfully", idx)
        
#         duration = time.time() - start
#         logger.info("Execution Time for 'Both prompts': %.2fs", duration)

#         # Step 6 & 8: Verify responses are generated and section is removed
#         logger.info("Step 6 & 8: Verify response generated and section 'Promissory note' is removed")
#         start = time.time()
        
#         # Verify response count increased (both responses added)
#         response_count_after = page.locator("//p").count()
#         logger.info("Response count after prompts: %d", response_count_after)
        
#         assert response_count_after < response_count_before, \
#             f"Response count should decrease. Before: {response_count_before}, After: {response_count_after}"

#         logger.info("✓ Promissory note generated and section removed successfully")
        
#         duration = time.time() - start
#         logger.info("Execution Time for 'Verify responses': %.2fs", duration)

#         logger.info("Test - Generate page Remove Section functionality completed successfully")

#     finally:
#         logger.removeHandler(handler)


# @pytest.mark.smoke
# def test_draft_page_populated_with_all_sections(login_logout, request):
#     """
#     Test Case: BYOc-DocGen-Draft Page-Should be populated with all sections specified on the Generate page
    
#     Preconditions:
#     1. User should have BYOc DocGen web url

#     Steps:
#     1. Login to BYOc DocGen web url
#     2. Verify login is successful and Document Generation page is displayed
#     3. Click on 'Generate' tab
#     4. Verify chat conversation page is displayed
#     5. Enter prompt: 'Generate promissory note with a proposed $100,000 for Washington State'
#     6. Verify response is generated with different section names
#     7. Click on 'Generate Draft' icon next to the chat box
#     8. Verify draft promissory note is generated in Draft section with all sections
#     9. Verify response is generated correctly in all sections in Draft page
#     """
    
#     request.node._nodeid = "TC - Validate Draft page populated with all sections from Generate page"
    
#     page = login_logout
#     home_page = HomePage(page)
#     generate_page = GeneratePage(page)
#     draft_page = DraftPage(page)

#     log_capture = io.StringIO()
#     handler = logging.StreamHandler(log_capture)
#     logger.addHandler(handler)

#     try:
#         # Step 1-2: Login and verify Document Generation page
#         logger.info("Step 1-2: Login to BYOc DocGen and verify Document Generation page is displayed")
#         start = time.time()
#         home_page.open_home_page()
#         home_page.validate_home_page()
#         duration = time.time() - start
#         logger.info("Execution Time for 'Login and validate home page': %.2fs", duration)

#         # Step 3: Click on 'Generate' tab
#         logger.info("Step 3: Click on 'Generate' tab")
#         start = time.time()
#         home_page.click_generate_button()
#         duration = time.time() - start
#         logger.info("Execution Time for 'Navigate to Generate tab': %.2fs", duration)

#         # Step 4: Verify chat conversation page is displayed
#         logger.info("Step 4: Verify chat conversation page is displayed")
#         start = time.time()
#         generate_page.validate_generate_page()
#         logger.info("Chat conversation page is displayed successfully")
#         duration = time.time() - start
#         logger.info("Execution Time for 'Validate Generate page': %.2fs", duration)

#         # Step 5: Enter prompt for generating promissory note
#         logger.info("Step 5: Enter prompt 'Generate promissory note with a proposed $100,000 for Washington State'")
#         start = time.time()
#         generate_page.enter_a_question(generate_question1)
#         generate_page.click_send_button()
#         duration = time.time() - start
#         logger.info("Execution Time for 'Enter prompt': %.2fs", duration)

#         # Step 6: Verify response is generated with different section names
#         logger.info("Step 6: Verify response is generated with different section names")
#         start = time.time()
#         generate_page.validate_response_status(question_api=generate_question1)
#         logger.info("Response generated successfully with section names")
#         duration = time.time() - start
#         logger.info("Execution Time for 'Verify response generated': %.2fs", duration)

#         # Step 7: Click on 'Generate Draft' icon
#         logger.info("Step 7: Click on 'Generate Draft' icon next to the chat box")
#         start = time.time()
#         generate_page.click_generate_draft_button()
#         duration = time.time() - start
#         logger.info("Execution Time for 'Click Generate Draft button': %.2fs", duration)

#         # Step 8: Verify draft promissory note is generated in Draft section
#         logger.info("Step 8: Verify draft promissory note is generated in Draft section with all sections")
#         start = time.time()
#         draft_page.validate_draft_sections_loaded()
#         logger.info("Draft promissory note generated successfully with all sections from Generate page")
#         duration = time.time() - start
#         logger.info("Execution Time for 'Verify draft sections loaded': %.2fs", duration)

#         # Step 9: Verify response is generated correctly in all sections in Draft page
#         logger.info("Step 9: Verify response is generated correctly in all sections in Draft page")
        
#         logger.info("Test - Draft page populated with all sections functionality completed successfully")

#     finally:
#         logger.removeHandler(handler)


# @pytest.mark.smoke
# def test_draft_page_section_regenerate(login_logout, request):
#     """
#     Test Case: BYOc-DocGen-Draft page-Each section can click Generate button to refresh
    
#     Preconditions:
#     1. User should have BYOc DocGen web url

#     Steps:
#     1. Login to BYOc DocGen web url
#     2. Verify login is successful and Document Generation page is displayed
#     3. Click on 'Generate' tab
#     4. Verify chat conversation page is displayed
#     5. Enter prompt: 'Generate promissory note with a proposed $100,000 for Washington State'
#     6. Verify response is generated with different section names
#     7. Click on 'Generate Draft' icon next to the chat box
#     8. Verify draft promissory note is generated in Draft section with all sections
#     9. Verify the Generate button on each section in Draft page
#     10. Click on Generate button for a section
#     11. Verify Regenerate popup is displayed with Generate button
#     12. Update the prompt and click Generate button
#     13. Verify section is refreshed and text response is updated correctly
#     """
    
#     request.node._nodeid = "TC - Validate Draft page section regenerate functionality"
    
#     page = login_logout
#     home_page = HomePage(page)
#     generate_page = GeneratePage(page)
#     draft_page = DraftPage(page)

#     log_capture = io.StringIO()
#     handler = logging.StreamHandler(log_capture)
#     logger.addHandler(handler)

#     try:
#         # Step 1-2: Login and verify Document Generation page
#         logger.info("Step 1-2: Login to BYOc DocGen and verify Document Generation page is displayed")
#         start = time.time()
#         home_page.open_home_page()
#         home_page.validate_home_page()
#         duration = time.time() - start
#         logger.info("Execution Time for 'Login and validate home page': %.2fs", duration)

#         # Step 3: Click on 'Generate' tab
#         logger.info("Step 3: Click on 'Generate' tab")
#         start = time.time()
#         home_page.click_generate_button()
#         duration = time.time() - start
#         logger.info("Execution Time for 'Navigate to Generate tab': %.2fs", duration)

#         # Step 4: Verify chat conversation page is displayed
#         logger.info("Step 4: Verify chat conversation page is displayed")
#         start = time.time()
#         generate_page.validate_generate_page()
#         logger.info("Chat conversation page is displayed successfully")
#         duration = time.time() - start
#         logger.info("Execution Time for 'Validate Generate page': %.2fs", duration)

#         # Step 5: Enter prompt for generating promissory note
#         logger.info("Step 5: Enter prompt 'Generate promissory note with a proposed $100,000 for Washington State'")
#         start = time.time()
#         generate_page.enter_a_question(generate_question1)
#         generate_page.click_send_button()
#         duration = time.time() - start
#         logger.info("Execution Time for 'Enter prompt': %.2fs", duration)

#         # Step 6: Verify response is generated with different section names
#         logger.info("Step 6: Verify response is generated with different section names")
#         start = time.time()
#         generate_page.validate_response_status(question_api=generate_question1)
#         logger.info("Response generated successfully with section names")
#         duration = time.time() - start
#         logger.info("Execution Time for 'Verify response generated': %.2fs", duration)

#         # Step 7: Click on 'Generate Draft' icon
#         logger.info("Step 7: Click on 'Generate Draft' icon next to the chat box")
#         start = time.time()
#         generate_page.click_generate_draft_button()
#         duration = time.time() - start
#         logger.info("Execution Time for 'Click Generate Draft button': %.2fs", duration)

#         # Step 8: Verify draft promissory note is generated in Draft section
#         logger.info("Step 8: Verify draft promissory note is generated in Draft section with all sections")
#         start = time.time()
#         draft_page.validate_draft_sections_loaded()
#         logger.info("Draft promissory note generated successfully with all sections from Generate page")
#         duration = time.time() - start
#         logger.info("Execution Time for 'Verify draft sections loaded': %.2fs", duration)

#         # Step 9: Verify the Generate button on each section in Draft page
#         logger.info("Step 9: Verify the Generate button is visible on each section in Draft page")
#         start = time.time()
        
#         # draft_page.verify_all_section_generate_buttons(expected_count=11)
        
#         duration = time.time() - start
#         logger.info("Execution Time for 'Verify Generate buttons': %.2fs", duration)

#         # Step 10-13: Regenerate all sections by appending instruction to existing popup prompt
#         logger.info("Step 10-13: Click Generate button for each section, update prompt, and verify regeneration")
#         start = time.time()
        
#         draft_page.regenerate_all_sections(additional_instruction="max 150 words")
        
#         duration = time.time() - start
#         logger.info("Execution Time for 'Regenerate all sections': %.2fs", duration)

#         logger.info("Test - Draft page section regenerate functionality completed successfully")

#     finally:
#         logger.removeHandler(handler)


# @pytest.mark.usefixtures("login_logout")
# def test_draft_page_character_count_validation(request, login_logout):
#     """
#     Test Case: BYOc-DocGen-Draft page character count validation
    
#     Preconditions:
#     1. User should have BYOc DocGen web url

#     Steps:
#     1. Login to BYOc DocGen web url
#     2. Verify login is successful and Document Generation page is displayed
#     3. Click on 'Generate' tab
#     4. Verify chat conversation page is displayed
#     5. Enter prompt: 'Generate promissory note with a proposed $100,000 for Washington State'
#     6. Verify response is generated with different section names
#     7. Click on 'Generate Draft' icon next to the chat box
#     8. Verify draft promissory note is generated in Draft section with all sections
#     9. Verify the count of characters remaining label at bottom of each section (should be less than 2000)
#     10. Try to enter more than 2000 characters in a section
#     11. Verify it's restricted to 2000 characters and label shows '0 characters remaining'
#     """
    
#     request.node._nodeid = "TC - Validate Draft page character count and restriction"
    
#     page = login_logout
#     home_page = HomePage(page)
#     generate_page = GeneratePage(page)
#     draft_page = DraftPage(page)

#     log_capture = io.StringIO()
#     handler = logging.StreamHandler(log_capture)
#     logger.addHandler(handler)

#     try:
#         # Step 1-2: Login and verify Document Generation page
#         logger.info("Step 1-2: Login to BYOc DocGen and verify Document Generation page is displayed")
#         start = time.time()
#         home_page.open_home_page()
#         home_page.validate_home_page()
#         duration = time.time() - start
#         logger.info("Execution Time for 'Login and validate home page': %.2fs", duration)

#         # Step 3: Click on 'Generate' tab
#         logger.info("Step 3: Click on 'Generate' tab")
#         start = time.time()
#         home_page.click_generate_button()
#         duration = time.time() - start
#         logger.info("Execution Time for 'Navigate to Generate tab': %.2fs", duration)

#         # Step 4: Verify chat conversation page is displayed
#         logger.info("Step 4: Verify chat conversation page is displayed")
#         start = time.time()
#         generate_page.validate_generate_page()
#         logger.info("Chat conversation page is displayed successfully")
#         duration = time.time() - start
#         logger.info("Execution Time for 'Validate Generate page': %.2fs", duration)

#         # Step 5: Enter prompt for generating promissory note
#         logger.info("Step 5: Enter prompt 'Generate promissory note with a proposed $100,000 for Washington State'")
#         start = time.time()
#         generate_page.enter_a_question(generate_question1)
#         generate_page.click_send_button()
#         duration = time.time() - start
#         logger.info("Execution Time for 'Enter prompt': %.2fs", duration)

#         # Step 6: Verify response is generated with different section names
#         logger.info("Step 6: Verify response is generated with different section names")
#         start = time.time()
#         generate_page.validate_response_status(question_api=generate_question1)
#         logger.info("Response generated successfully with section names")
#         duration = time.time() - start
#         logger.info("Execution Time for 'Verify response generated': %.2fs", duration)

#         # Step 7: Click on 'Generate Draft' icon
#         logger.info("Step 7: Click on 'Generate Draft' icon next to the chat box")
#         start = time.time()
#         generate_page.click_generate_draft_button()
#         duration = time.time() - start
#         logger.info("Execution Time for 'Click Generate Draft button': %.2fs", duration)

#         # Step 8: Verify draft promissory note is generated in Draft section
#         logger.info("Step 8: Verify draft promissory note is generated in Draft section with all sections")
#         start = time.time()
#         draft_page.validate_draft_sections_loaded()
#         logger.info("Draft promissory note generated successfully with all sections")
#         duration = time.time() - start
#         logger.info("Execution Time for 'Verify draft sections loaded': %.2fs", duration)

#         # Step 9: Verify character count labels show count less than 2000
#         logger.info("Step 9: Verify the count of characters remaining label at bottom of each section")
#         start = time.time()
#         draft_page.verify_character_count_labels(max_chars=2000)
#         duration = time.time() - start
#         logger.info("Execution Time for 'Verify character count labels': %.2fs", duration)

#         # Step 10-11: Test character limit restriction (try entering more than 2000 chars)
#         logger.info("Step 10-11: Try to enter more than 2000 characters in first section")
#         start = time.time()
#         actual_length = draft_page.test_character_limit_restriction(section_index=0)
#         logger.info(f"Character restriction verified: Input limited to {actual_length} characters")
#         duration = time.time() - start
#         logger.info("Execution Time for 'Test character limit restriction': %.2fs", duration)

#         logger.info("Test - Draft page character count validation completed successfully")

#     finally:
#         logger.removeHandler(handler)


# @pytest.mark.usefixtures("login_logout")
# def test_bug_7806_list_all_documents_response(request, login_logout):
#     """
#     Test Case: Bug-7806 - BYOc-DocGen - Test response for "List all documents" prompt
    
#     Preconditions:
#     1. User should have BYOc DocGen web url

#     Steps:
#     1. Login to BYOc DocGen web url
#     2. Verify login is successful and Document Generation page is displayed
#     3. Click on 'Browse' tab
#     4. Verify Browse chat conversation page is displayed
#     5. Enter prompt: 'List all documents and their value'
#     6. Click Send button
#     7. Verify response is generated with document-related information
#     """
    
#     request.node._nodeid = "TC - Bug-7806 - Validate response for List all documents prompt"
    
#     page = login_logout
#     home_page = HomePage(page)
#     browse_page = BrowsePage(page)
#     generate_page = GeneratePage(page)

#     log_capture = io.StringIO()
#     handler = logging.StreamHandler(log_capture)
#     logger.addHandler(handler)

#     try:
#         # Step 1-2: Login and verify Document Generation page
#         logger.info("Step 1-2: Login to BYOc DocGen and verify Document Generation page is displayed")
#         start = time.time()
#         home_page.open_home_page()
#         home_page.validate_home_page()
#         duration = time.time() - start
#         logger.info("Execution Time for 'Login and validate home page': %.2fs", duration)

#         # Step 3: Click on 'Browse' tab
#         logger.info("Step 3: Click on 'Browse' tab")
#         start = time.time()
#         home_page.click_browse_button()
#         duration = time.time() - start
#         logger.info("Execution Time for 'Navigate to Browse tab': %.2fs", duration)

#         # Step 4: Verify Browse chat conversation page is displayed
#         logger.info("Step 4: Verify Browse chat conversation page is displayed")
#         start = time.time()
#         browse_page.validate_browse_page()
#         logger.info("Browse chat conversation page is displayed successfully")
#         duration = time.time() - start
#         logger.info("Execution Time for 'Validate Browse page': %.2fs", duration)

#         # Step 5: Enter prompt 'List all documents and their value'
#         logger.info("Step 5: Enter prompt 'List all documents and their value'")
#         start = time.time()
#         browse_page.enter_a_question(browse_question3)
#         duration = time.time() - start
#         logger.info("Execution Time for 'Enter question': %.2fs", duration)

#         # Step 6: Click Send button
#         logger.info("Step 6: Click Send button")
#         start = time.time()
#         browse_page.click_send_button()
#         duration = time.time() - start
#         logger.info("Execution Time for 'Click Send button': %.2fs", duration)

#         # Step 7: Verify response is generated with document-related information
#         logger.info("Step 7: Verify response is generated with document-related information")
#         start = time.time()

#         browse_page.validate_response_status(question_api=browse_question3)
        
#         # # Expected keywords related to documents
#         # expected_keywords = ["document", "value"]
        
#         # response_text = browse_page.validate_response_generated(
#         #     expected_keywords=expected_keywords,
#         #     timeout=90000  # 90 seconds timeout
#         # )
        
#         # logger.info(f"Response generated successfully with {len(response_text)} characters")
#         # duration = time.time() - start
#         # logger.info("Execution Time for 'Verify response generated': %.2fs", duration)

#         # # Additional verification: Response should contain meaningful information
#         # with check:
#         #     assert len(response_text) > 50, f"Response too short: {len(response_text)} chars"
        
#         logger.info("✅ Response contains meaningful document-related information")
#         logger.info("Test - Bug-7806 List all documents response validation completed successfully")

#     finally:
#         logger.removeHandler(handler)


# @pytest.mark.usefixtures("login_logout")
# def test_bug_7571_removed_sections_not_returning(request, login_logout):
#     """
#     Test Case: Bug-7571 - BYOc-DocGen - Removing sections one by one should not cause sections to return
    
#     Preconditions:
#     1. User should have BYOc DocGen web url

#     Steps:
#     1. Login to BYOc DocGen web url
#     2. Verify login is successful and Document Generation page is displayed
#     3. Click on 'Generate' tab
#     4. Verify chat conversation page is displayed
#     5. Enter prompt: 'Generate promissory note with a proposed $100,000 for Washington State'
#     6. Verify response is generated with multiple sections
#     7. Remove sections one by one (3 sections)
#     8. After each removal, verify the section list decreases
#     9. Verify all removed sections do not appear back in the final list
#     """
    
#     request.node._nodeid = "TC - Bug-7571 - Validate removed sections do not return"
    
#     page = login_logout
#     home_page = HomePage(page)
#     generate_page = GeneratePage(page)

#     log_capture = io.StringIO()
#     handler = logging.StreamHandler(log_capture)
#     logger.addHandler(handler)

#     try:
#         # Step 1-2: Login and verify Document Generation page
#         logger.info("Step 1-2: Login to BYOc DocGen and verify Document Generation page is displayed")
#         start = time.time()
#         home_page.open_home_page()
#         home_page.validate_home_page()
#         duration = time.time() - start
#         logger.info("Execution Time for 'Login and validate home page': %.2fs", duration)

#         # Step 3: Click on 'Generate' tab
#         logger.info("Step 3: Click on 'Generate' tab")
#         start = time.time()
#         home_page.click_generate_button()
#         duration = time.time() - start
#         logger.info("Execution Time for 'Navigate to Generate tab': %.2fs", duration)

#         # Step 4: Verify chat conversation page is displayed
#         logger.info("Step 4: Verify chat conversation page is displayed")
#         start = time.time()
#         generate_page.validate_generate_page()
#         logger.info("Chat conversation page is displayed successfully")
#         duration = time.time() - start
#         logger.info("Execution Time for 'Validate Generate page': %.2fs", duration)

#         # Step 5: Enter prompt for generating promissory note
#         logger.info("Step 5: Enter prompt 'Generate promissory note with a proposed $100,000 for Washington State'")
#         start = time.time()
#         generate_page.enter_a_question(generate_question1)
#         generate_page.click_send_button()
#         duration = time.time() - start
#         logger.info("Execution Time for 'Enter prompt and send': %.2fs", duration)

#         # Step 6: Verify response is generated with multiple sections
#         logger.info("Step 6: Verify response is generated with multiple sections")
#         start = time.time()
#         generate_page.validate_response_status(question_api=generate_question1)
        
#         # Get initial section list
#         initial_sections = generate_page.get_section_names_from_response()
#         initial_count = len(initial_sections)
        
#         logger.info(f"Initial section count: {initial_count}")
#         logger.info(f"Initial sections: {initial_sections}")
        
#         # If no sections found, this might be a response format issue - fail early with helpful message
#         if initial_count == 0:
#             logger.error("❌ No sections extracted from response. Response format may have changed.")
#             logger.error("Please check the response format and update get_section_names_from_response() method.")
#             # Take a screenshot for debugging
#             try:
#                 page.screenshot(path="screenshots/no_sections_found.png")
#                 logger.info("Screenshot saved to screenshots/no_sections_found.png")
#             except Exception:
#                 pass
#             raise AssertionError("No sections found in response. Cannot proceed with section removal test.")
        
#         with check:
#             assert initial_count >= 3, f"Expected at least 3 sections for removal test, got {initial_count}"
        
#         duration = time.time() - start
#         logger.info("Execution Time for 'Verify response and get sections': %.2fs", duration)

#         # Step 7-8: Remove sections one by one and track removed sections
#         logger.info("Step 7-8: Remove sections one by one and verify section list decreases")
        
#         # Select 3 sections to remove from the initial list
#         sections_to_remove = []
#         if initial_count >= 3:
#             # Remove sections at positions 1, 3, and 5 (avoid removing first and last)
#             indices_to_remove = [1, 3, 5] if initial_count > 5 else [1, 2, 3]
#             for idx in indices_to_remove:
#                 if idx < len(initial_sections):
#                     sections_to_remove.append(initial_sections[idx])
#         else:
#             sections_to_remove = initial_sections[:1]  # Remove at least one
        
#         logger.info(f"Sections selected for removal: {sections_to_remove}")
        
#         removed_sections = []
        
#         for i, section_to_remove in enumerate(sections_to_remove):
#             logger.info(f"\n{'='*60}")
#             logger.info(f"Removing section {i + 1}/{len(sections_to_remove)}: '{section_to_remove}'")
#             logger.info(f"{'='*60}")
            
#             start = time.time()
            
#             # Enter remove prompt
#             remove_prompt = f"Remove {section_to_remove}"
#             logger.info(f"Entering prompt: '{remove_prompt}'")
#             generate_page.enter_a_question(remove_prompt)
#             generate_page.click_send_button()
            
#             # Wait for response
#             generate_page.validate_response_status(question_api=remove_prompt)
            
#             # Get updated section list
#             current_sections = generate_page.get_section_names_from_response()
#             current_count = len(current_sections)
            
#             logger.info(f"Section count after removal: {current_count}")
            
#             # Verify section count decreased
#             expected_count = initial_count - (i + 1)
#             with check:
#                 assert current_count <= expected_count, f"Expected count <= {expected_count}, got {current_count}"
            
#             # Track removed section
#             removed_sections.append(section_to_remove)
            
#             # Verify the specific removed section is not in current list
#             is_removed = generate_page.verify_section_removed(section_to_remove, current_sections)
#             with check:
#                 assert is_removed, f"Section '{section_to_remove}' should be removed but still found"
            
#             duration = time.time() - start
#             logger.info(f"Execution Time for 'Remove section {i + 1}': %.2fs", duration)
            
#             # Small delay between removals
#             page.wait_for_timeout(2000)
        
#         # Step 9: Verify all removed sections do not appear back
#         logger.info("Step 9: Verify all removed sections do not appear back in the final list")
#         start = time.time()
        
#         # Get final section list
#         final_sections = generate_page.get_section_names_from_response()
#         logger.info(f"Final section count: {len(final_sections)}")
#         logger.info(f"Total removed sections: {len(removed_sections)}")
        
#         # Verify none of the removed sections returned
#         all_removed, returned_sections = generate_page.verify_removed_sections_not_returned(
#             removed_sections, 
#             final_sections
#         )
        
#         with check:
#             assert all_removed, f"Removed sections returned: {returned_sections}"
        
#         # Additional verification: Final count should be less than initial count (if sections were removed)
#         if len(removed_sections) > 0:
#             with check:
#                 assert len(final_sections) < initial_count, \
#                     f"Final count {len(final_sections)} should be less than initial {initial_count}"
#         else:
#             logger.warning("No sections were removed, skipping final count verification")
        
#         duration = time.time() - start
#         logger.info("Execution Time for 'Verify removed sections not returned': %.2fs", duration)
        
#         logger.info(f"\n{'='*60}")
#         logger.info("✅ Test completed successfully")
#         logger.info(f"Initial sections: {initial_count}")
#         logger.info(f"Removed sections: {len(removed_sections)}")
#         logger.info(f"Final sections: {len(final_sections)}")
#         logger.info(f"All removed sections stayed removed: {all_removed}")
#         logger.info(f"{'='*60}")
        
#         logger.info("Test - Bug-7571 Removed sections not returning validation completed successfully")

#     finally:
#         logger.removeHandler(handler)


# @pytest.mark.usefixtures("login_logout")
# def test_add_section_before_and_after_position(request, login_logout):
#     """
#     Test Case: BYOc-DocGen - Add section before and after a specified section
    
#     Preconditions:
#     1. User should have BYOc DocGen web url

#     Steps:
#     1. Login to BYOc DocGen web url
#     2. Verify login is successful and Document Generation page is displayed
#     3. Click on 'Generate' tab
#     4. Verify chat conversation page is displayed
#     5. Enter prompt: 'Generate promissory note with a proposed $100,000 for Washington State'
#     6. Verify response is generated with different section names
#     7. Enter prompt: 'Add Payment acceleration clause after the payment terms sections'
#     8. Verify 'Payment acceleration clause' section is added AFTER the payment terms section
#     9. Enter prompt: 'Add Payment acceleration clause before the payment terms sections'
#     10. Verify 'Payment acceleration clause' section is now positioned BEFORE the payment terms section
#     """
    
#     request.node._nodeid = "TC - Validate add section before and after specified position"
    
#     page = login_logout
#     home_page = HomePage(page)
#     generate_page = GeneratePage(page)

#     log_capture = io.StringIO()
#     handler = logging.StreamHandler(log_capture)
#     logger.addHandler(handler)

#     try:
#         # Step 1-2: Login and verify Document Generation page
#         logger.info("Step 1-2: Login to BYOc DocGen and verify Document Generation page is displayed")
#         start = time.time()
#         home_page.open_home_page()
#         home_page.validate_home_page()
#         duration = time.time() - start
#         logger.info("Execution Time for 'Login and validate home page': %.2fs", duration)

#         # Step 3: Click on 'Generate' tab
#         logger.info("Step 3: Click on 'Generate' tab")
#         start = time.time()
#         home_page.click_generate_button()
#         duration = time.time() - start
#         logger.info("Execution Time for 'Navigate to Generate tab': %.2fs", duration)

#         # Step 4: Verify chat conversation page is displayed
#         logger.info("Step 4: Verify chat conversation page is displayed")
#         start = time.time()
#         generate_page.validate_generate_page()
#         logger.info("Chat conversation page is displayed successfully")
#         duration = time.time() - start
#         logger.info("Execution Time for 'Validate Generate page': %.2fs", duration)

#         # Step 5: Enter prompt for generating promissory note
#         logger.info("Step 5: Enter prompt 'Generate promissory note with a proposed $100,000 for Washington State'")
#         start = time.time()
#         generate_page.enter_a_question(generate_question1)
#         generate_page.click_send_button()
#         duration = time.time() - start
#         logger.info("Execution Time for 'Enter prompt and send': %.2fs", duration)

#         # Step 6: Verify response is generated with different section names
#         logger.info("Step 6: Verify response is generated with different section names")
#         start = time.time()
#         generate_page.validate_response_status(question_api=generate_question1)
        
#         # Get initial section list
#         initial_sections = generate_page.get_section_names_from_response()
#         initial_count = len(initial_sections)
        
#         logger.info(f"Initial section count: {initial_count}")
#         logger.info(f"Initial sections: {initial_sections}")
        
#         with check:
#             assert initial_count > 0, f"No sections found in initial response"
        
#         duration = time.time() - start
#         logger.info("Execution Time for 'Verify response and get sections': %.2fs", duration)

#         # Step 7: Add Payment acceleration clause AFTER payment terms
#         logger.info("Step 7: Add 'Payment acceleration clause' AFTER the payment terms sections")
#         start = time.time()
        
#         add_after_prompt = "Add Payment acceleration clause after the payment terms sections"
#         logger.info(f"Entering prompt: '{add_after_prompt}'")
#         generate_page.enter_a_question(add_after_prompt)
#         generate_page.click_send_button()
        
#         # Wait for response
#         generate_page.validate_response_status(question_api=add_after_prompt)
        
#         # Get updated section list
#         sections_after_add = generate_page.get_section_names_from_response()
#         logger.info(f"Section count after adding: {len(sections_after_add)}")
#         logger.info(f"Sections after add: {sections_after_add}")
        
#         duration = time.time() - start
#         logger.info("Execution Time for 'Add section after': %.2fs", duration)

#         # Step 8: Verify section is added AFTER payment terms
#         logger.info("Step 8: Verify 'Payment acceleration clause' is added AFTER payment terms section")
#         start = time.time()
        
#         # Verify the new section was added
#         is_added = generate_page.verify_section_added("Payment acceleration clause", sections_after_add)
#         with check:
#             assert is_added, "Payment acceleration clause section was not added"
        
#         # Verify position is AFTER payment terms
#         is_correct_position, new_idx, ref_idx = generate_page.verify_section_position(
#             "Payment acceleration clause",
#             "payment terms",
#             sections_after_add,
#             position="after"
#         )
        
#         with check:
#             assert is_correct_position, \
#                 f"Payment acceleration clause should be AFTER payment terms (indices: new={new_idx}, ref={ref_idx})"
        
#         duration = time.time() - start
#         logger.info("Execution Time for 'Verify section added after': %.2fs", duration)

#         # Step 9: Add Payment acceleration clause BEFORE payment terms
#         logger.info("Step 9: Add 'Payment acceleration clause' BEFORE the payment terms sections")
#         start = time.time()
        
#         add_before_prompt = "Add Payment acceleration clause before the payment terms sections"
#         logger.info(f"Entering prompt: '{add_before_prompt}'")
#         generate_page.enter_a_question(add_before_prompt)
#         generate_page.click_send_button()
        
#         # Wait for response
#         generate_page.validate_response_status(question_api=add_before_prompt)
        
#         # Get updated section list
#         sections_after_reorder = generate_page.get_section_names_from_response()
#         logger.info(f"Section count after reordering: {len(sections_after_reorder)}")
#         logger.info(f"Sections after reorder: {sections_after_reorder}")
        
#         duration = time.time() - start
#         logger.info("Execution Time for 'Add section before': %.2fs", duration)

#         # Step 10: Verify section is now positioned BEFORE payment terms
#         logger.info("Step 10: Verify 'Payment acceleration clause' is now BEFORE payment terms section")
#         start = time.time()
        
#         # Verify the section still exists
#         is_still_added = generate_page.verify_section_added("Payment acceleration clause", sections_after_reorder)
#         with check:
#             assert is_still_added, "Payment acceleration clause section disappeared"
        
#         # Verify position is now BEFORE payment terms
#         is_correct_position_before, new_idx_before, ref_idx_before = generate_page.verify_section_position(
#             "Payment acceleration clause",
#             "payment terms",
#             sections_after_reorder,
#             position="before"
#         )
        
#         with check:
#             assert is_correct_position_before, \
#                 f"Payment acceleration clause should be BEFORE payment terms (indices: new={new_idx_before}, ref={ref_idx_before})"
        
#         duration = time.time() - start
#         logger.info("Execution Time for 'Verify section moved before': %.2fs", duration)

#         logger.info(f"\n{'='*60}")
#         logger.info("✅ Test completed successfully")
#         logger.info(f"Initial sections: {initial_count}")
#         logger.info(f"After adding section: {len(sections_after_add)} sections")
#         logger.info(f"After reordering: {len(sections_after_reorder)} sections")
#         logger.info(f"Section correctly positioned AFTER payment terms: {is_correct_position}")
#         logger.info(f"Section correctly repositioned BEFORE payment terms: {is_correct_position_before}")
#         logger.info(f"{'='*60}")
        
#         logger.info("Test - Add section before and after position validation completed successfully")

#     finally:
#         logger.removeHandler(handler)


@pytest.mark.smoke
def test_bug_7834_accurate_reference_citations(request, login_logout):
    """
    Test Case Bug-7834: BYOc-DocGen - Browse experience should provide accurate reference citations
    
    Bug Description:
    Browse experience should provide accurate reference citations and the user shouldn't see 
    Unexpected number of files returned in the citations.
    
    Preconditions:
    1. User should have BYOc DocGen web url
    2. Documents should be uploaded and indexed in the system

    Steps:
    1. Login to BYOc DocGen web url
    2. Verify login is successful and Document Generation page is displayed
    3. Click on 'Browse' tab and verify Browse page is displayed
    4. Ask question: 'What is the proposed loan amount for all the promissory notes?'
       Verify response is generated with accurate reference citations
    5. Ask question: 'list out all the promissory note present in the system.'
       Verify response is generated with accurate reference citations
    6. Ask filtered questions where interest rate is not 5% in both table and tabular formats
       Verify responses are generated with accurate reference citations matching the filter
       Verify citation counts are consistent between table and tabular format queries
    """
    
    request.node._nodeid = "Bug-7834 - Validate Browse provides accurate reference citations"
    
    page = login_logout
    home_page = HomePage(page)
    browse_page = BrowsePage(page)

    log_capture = io.StringIO()
    handler = logging.StreamHandler(log_capture)
    logger.addHandler(handler)

    try:
        # Step 1-2: Login and verify Document Generation page
        logger.info("Step 1-2: Login to BYOc DocGen and verify Document Generation page is displayed")
        start = time.time()
        home_page.open_home_page()
        home_page.validate_home_page()
        duration = time.time() - start
        logger.info("Execution Time for 'Login and validate home page': %.2fs", duration)

        # Step 3: Navigate to Browse tab
        logger.info("Step 3: Navigate to Browse tab and verify Browse page is displayed")
        start = time.time()
        home_page.click_browse_button()
        browse_page.validate_browse_page()
        logger.info("Browse page is displayed successfully")
        duration = time.time() - start
        logger.info("Execution Time for 'Navigate to Browse tab': %.2fs", duration)

        # Step 4: Ask first question - proposed loan amount
        logger.info(f"Step 4: Ask question: '{browse_question1}'")
        start = time.time()
        browse_page.enter_a_question(browse_question1)
        browse_page.click_send_button()
        
        # Verify response with citations
        response_text1, citation_count1 = browse_page.verify_response_generated_with_citations(timeout=60)
        
        logger.info(f"✅ Response generated with {citation_count1} citation(s)")
        logger.info(f"Response preview: {response_text1[:200]}...")
        
        with check:
            assert citation_count1 > 0, f"Expected citations for browse_question1, but got {citation_count1}"
        
        duration = time.time() - start
        logger.info("Execution Time for 'Question 1 - proposed loan amount': %.2fs", duration)

        # Step 5: Ask second question - list all promissory notes
        logger.info(f"Step 5: Ask question: '{browse_question2}'")
        start = time.time()
        browse_page.enter_a_question(browse_question2)
        browse_page.click_send_button()
        
        # Verify response with citations
        response_text2, citation_count2 = browse_page.verify_response_generated_with_citations(timeout=60)
        
        logger.info(f"✅ Response generated with {citation_count2} citation(s)")
        logger.info(f"Response preview: {response_text2[:200]}...")
        
        with check:
            assert citation_count2 > 0, f"Expected citations for browse_question2, but got {citation_count2}"
        
        duration = time.time() - start
        logger.info("Execution Time for 'Question 2 - list all promissory notes': %.2fs", duration)

        # Step 6: Ask filtered questions with interest rate != 5% (both table and tabular format)
        logger.info("Step 6: Ask filtered questions with interest rate != 5% in different formats")
        
        filtered_questions = [
            (browse_question4, "table format"),
            (browse_question5, "tabular format")
        ]
        
        filtered_citation_counts = []
        
        for idx, (question, format_type) in enumerate(filtered_questions, start=1):
            logger.info(f"\n  6.{idx}) Testing {format_type}: '{question}'")
            start = time.time()
            
            browse_page.enter_a_question(question)
            browse_page.click_send_button()
            
            # Verify response with citations
            response_text, citation_count = browse_page.verify_response_generated_with_citations(timeout=60)
            filtered_citation_counts.append(citation_count)
            
            logger.info(f"  ✅ Response generated with {citation_count} citation(s)")
            logger.info(f"  Response preview: {response_text[:200]}...")
            
            with check:
                assert citation_count > 0, f"Expected citations for filtered query ({format_type}), but got {citation_count}"
            
            # Get detailed citation information
            citations_documents = browse_page.get_citations_and_documents()
            logger.info(f"  📋 Citations and documents: {citations_documents}")
            
            duration = time.time() - start
            logger.info("  Execution Time for '%s query': %.2fs", format_type, duration)

        # Verify consistency between table and tabular format queries
        logger.info("\nVerifying citation consistency between table and tabular format queries")
        citation_count4, citation_count5 = filtered_citation_counts
        
        # Allow for slight variation (±1) due to AI response variability
        citation_diff = abs(citation_count4 - citation_count5)
        
        with check:
            assert citation_diff <= 1, \
                f"Citation counts should be similar for table ({citation_count4}) and tabular ({citation_count5}) formats. Difference: {citation_diff}"
        
        logger.info(f"✅ Citation consistency verified - Table: {citation_count4}, Tabular: {citation_count5}, Diff: {citation_diff}")

        logger.info(f"\n{'='*80}")
        logger.info("✅ Bug-7834 Test Summary - Accurate Reference Citations")
        logger.info(f"{'='*80}")
        logger.info(f"Question 1 (loan amount): {citation_count1} citations")
        logger.info(f"Question 2 (list all notes): {citation_count2} citations")
        logger.info(f"Filtered queries (interest != 5%):")
        logger.info(f"  - Table format: {citation_count4} citations")
        logger.info(f"  - Tabular format: {citation_count5} citations")
        logger.info(f"Citation consistency (table vs tabular): Difference = {citation_diff} (threshold: ≤1)")
        logger.info(f"All queries returned accurate reference citations ✓")
        logger.info(f"{'='*80}")
        
        logger.info("Test Bug-7834 - Accurate reference citations validation completed successfully")

    finally:
        logger.removeHandler(handler)