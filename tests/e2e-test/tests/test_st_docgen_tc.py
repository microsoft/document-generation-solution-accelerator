import io
import logging
import time

import pytest
from config.constants import (URL, add_section, browse_question1, browse_question2,
                              generate_question1, invalid_response, invalid_response1)
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

@pytest.mark.smoke
def test_template_history_delete(login_logout, request):
    """
    Test Case: BYOc-DocGen-User should be able to delete saved template history thread
    
    Preconditions:
    1. User should have BYOc DocGen web url
    2. User should have saved template history threads
    
    Steps:
    1. Login to BYOc DocGen web url
    2. Click on 'Generate' tab
    3. Click on 'Show template history' button
    4. Select a session thread and click on Delete icon
    5. Verify delete confirmation popup is displayed with correct content
    6. Click on Delete button in popup
    7. Verify session thread is deleted successfully
    """
    
    request.node._nodeid = "TC - Validate template history delete functionality"
    
    page = login_logout
    home_page = HomePage(page)
    generate_page = GeneratePage(page)

    log_capture = io.StringIO()
    handler = logging.StreamHandler(log_capture)
    logger.addHandler(handler)

    try:
        # Step 1: Navigate to home page and validate login
        logger.info("Step 1: Verify login is successful and Document Generation page is displayed")
        start = time.time()
        home_page.open_home_page()
        home_page.validate_home_page()
        duration = time.time() - start
        logger.info("Execution Time for 'Validate home page is loaded': %.2fs", duration)

        # Step 2: Click on 'Generate' tab
        logger.info("Step 2: Navigate to Generate page")
        start = time.time()
        home_page.click_generate_button()
        generate_page.validate_generate_page()
        logger.info("Generate chat conversation page is displayed successfully")
        duration = time.time() - start
        logger.info("Execution Time for 'Navigate to Generate page': %.2fs", duration)

        # Step 3: Click on 'Show template history' button
        logger.info("Step 3: Click on 'Show template history' button")
        start = time.time()
        generate_page.show_chat_history()
        
        # Verify template history window is displayed
        logger.info("Template history window with saved history threads is displayed")
        duration = time.time() - start
        logger.info("Execution Time for 'Show template history': %.2fs", duration)

        # Step 4: Get initial thread count and click delete icon
        logger.info("Step 4: Select a session thread and click on Delete icon")
        start = time.time()
        
        # Get the count of threads before deletion
        generate_page.select_history_thread(thread_index=0)
        
        # Click delete icon on the first thread
        generate_page.delete_thread_by_index(thread_index=0)
        
        duration = time.time() - start
        logger.info("Execution Time for 'Click delete icon': %.2fs", duration)

        logger.info("Test - Template history delete functionality completed successfully")

    finally:
        logger.removeHandler(handler)