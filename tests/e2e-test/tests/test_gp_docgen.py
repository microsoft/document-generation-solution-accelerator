import logging
import time

import pytest
from config.constants import (add_section, browse_question1, browse_question2,
                              generate_question1, invalid_response, invalid_response1)
from pages.browsePage import BrowsePage
from pages.draftPage import DraftPage
from pages.generatePage import GeneratePage
from pages.homePage import HomePage
from pytest_check import check

logger = logging.getLogger(__name__)


# ---------- COMMON FIXTURE ----------
@pytest.fixture(scope="function")
def setup_pages(login_logout):
    page = login_logout
    home_page = HomePage(page)
    browse_page = BrowsePage(page)
    generate_page = GeneratePage(page)
    draft_page = DraftPage(page)
    return page, home_page, browse_page, generate_page, draft_page


# ---------- INDIVIDUAL TEST CASES ----------


def test_load_home_and_navigate_to_browse_page(setup_pages, request):
    request.node._nodeid = "Validate Home Page is loaded and navigating to Browse Page"
    _, home, browse, *_ = setup_pages
    start = time.time()

    try:
        logger.info("Loading Home Page and navigating to Browse Page.")
        home.validate_home_page()
        home.click_browse_button()
    except Exception as e:
        logger.error(f"FAILED to load Home Page or navigate to Browse Page: {e}")
        raise

    duration = time.time() - start
    logger.info(
        f"Test 'Home to Browse Page Navigation' completed in {duration:.2f} seconds."
    )


@pytest.mark.parametrize("question", [browse_question1])
def test_browse_prompt1(setup_pages, question, request):
    request.node._nodeid = f"Validate response for BROWSE Prompt1 : {question}"
    page, home, browse, *_ = setup_pages
    start = time.time()

    try:
        logger.info(f"Entering Browse Question 1: {question}")
        browse.enter_a_question(question)
        browse.click_send_button()
        browse.validate_response_status(question_api=question)
        browse.click_expand_reference_in_response()
        browse.click_reference_link_in_response()
        browse.close_citation()
    except Exception as e:
        logger.error(f"FAILED while validating BROWSE Prompt1 '{question}': {e}")
        raise

    duration = time.time() - start
    logger.info(f"Test 'Browse Prompt 1' completed in {duration:.2f} seconds.")


@pytest.mark.parametrize("question", [browse_question2])
def test_browse_prompt2(setup_pages, question, request):
    request.node._nodeid = f"Validate response for BROWSE Prompt2 : {question}"
    page, _, browse, *_ = setup_pages
    start = time.time()

    try:
        logger.info(f"Entering Browse Question 2: {question}")
        browse.enter_a_question(question)
        browse.click_send_button()
        browse.validate_response_status(question_api=question)
        browse.click_expand_reference_in_response()
        browse.click_reference_link_in_response()
        browse.close_citation()
    except Exception as e:
        logger.error(f"FAILED while validating BROWSE Prompt2 '{question}': {e}")
        raise

    duration = time.time() - start
    logger.info(f"Test 'Browse Prompt 2' completed in {duration:.2f} seconds.")


def test_delete_chat_history_before_generate_prompt1(setup_pages, request):
    request.node._nodeid = "Validate delete all chat history "
    _, _, browse, generate, _ = setup_pages
    start = time.time()

    try:
        logger.info("Navigating to Generate Page.")
        browse.click_generate_button()

        logger.info("Deleting chat history before GENERATE Prompt1.")
        generate.delete_chat_history()
    except Exception as e:
        logger.error(f"FAILED to delete chat history before GENERATE Prompt1: {e}")
        raise

    duration = time.time() - start
    logger.info(f"Chat history deletion completed in {duration:.2f} seconds.")


MAX_RETRIES = 3
RETRY_DELAY = 3  # seconds


@pytest.mark.parametrize("question", [generate_question1])
def test_generate_prompt(setup_pages, question, request):
    request.node._nodeid = f"Validate response for GENERATE Prompt1 : {question}"
    page, _, browse, generate, _ = setup_pages
    start = time.time()

    try:

        attempt = 1
        while attempt <= MAX_RETRIES:
            logger.info(f"Attempt {attempt}: Entering Generate Question: {question}")
            generate.enter_a_question(question)
            generate.click_send_button()
            # generate.validate_generate_response_status(question_api=question)

            time.sleep(2)
            response_text = page.locator("//p")
            latest_response = response_text.nth(
                response_text.count() - 1
            ).text_content()

            if latest_response not in [invalid_response, invalid_response1]:
                logger.info(f"Valid response received on attempt {attempt}")
                break
            else:
                logger.warning(f"Invalid response received on attempt {attempt}")
                if attempt == MAX_RETRIES:
                    check.not_equal(
                        latest_response not in [invalid_response, invalid_response1],
                        f"FAILED: Invalid response received after {MAX_RETRIES} attempts for: {question}",
                    )
                else:
                    time.sleep(RETRY_DELAY)
            attempt += 1
    except Exception as e:
        logger.error(f"FAILED while validating GENERATE Prompt1 '{question}': {e}")
        raise

    duration = time.time() - start
    logger.info(f"Test 'Generate Prompt' completed in {duration:.2f} seconds.")


@pytest.mark.parametrize("question", [add_section])
def test_add_section_prompt(setup_pages, question, request):
    request.node._nodeid = f"Validate response for GENERATE Prompt2 : {question}"
    _, _, browse, generate, _ = setup_pages
    start = time.time()

    try:
        logger.info(f"Entering Add Section Question: {question}")
        generate.enter_a_question(question)
        generate.click_send_button()
        # generate.validate_generate_response_status(question_api=question)
    except Exception as e:
        logger.error(f"FAILED while validating Add Section Prompt '{question}': {e}")
        raise

    duration = time.time() - start
    logger.info(f"Test 'Add Section and Draft' completed in {duration:.2f} seconds.")


def test_generate_draft_from_section_prompt(setup_pages, request):
    custom_title = "Validate Generate Draft & all sections are generated successfully"
    request.node._nodeid = custom_title

    _, _, _, generate, draft = setup_pages
    start = time.time()

    try:
        logger.info("Clicking 'Generate Draft' and validating sections.")
        generate.click_generate_draft_button()
        # draft.validate_draft_sections()
        draft.validate_draft_sections_loaded()
    except Exception as e:
        logger.error(f"FAILED while generating or validating draft sections: {e}")
        raise

    duration = time.time() - start
    logger.info(
        f"Test 'Generate Draft and Validate Sections' completed in {duration:.2f} seconds."
    )


def test_show_chat_history_at_end(setup_pages, request):
    request.node._nodeid = "Validate chat history is generated"
    _, _, browse, generate, _ = setup_pages
    start = time.time()

    try:
        logger.info("Navigating to Generate Page.")
        browse.click_generate_button()

        logger.info("Showing chat history after all prompts.")
        generate.show_chat_history()
        generate.close_chat_history()
    except Exception as e:
        logger.error(f"FAILED to show chat history: {e}")
        raise

    duration = time.time() - start
    logger.info(f"Chat history display completed in {duration:.2f} seconds.")
