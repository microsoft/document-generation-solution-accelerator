import logging
import time
import pytest
from pytest_check import check

from config.constants import (
    add_section,
    browse_question1,
    browse_question2,
    generate_question1,
    invalid_response,
)
from pages.browsePage import BrowsePage
from pages.draftPage import DraftPage
from pages.generatePage import GeneratePage
from pages.homePage import HomePage

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

@pytest.mark.parametrize("question", [browse_question1])
def test_browse_prompt1(setup_pages, question, request):
    request.node._nodeid = f"Validate response for BROWSE Prompt1 : {question}"
    page, home, browse, _, _ = setup_pages
    start = time.time()

    logger.info("Loading Home Page and navigating to Browse Page.")
    home.validate_home_page()
    home.click_browse_button()

    logger.info(f"Entering Browse Question 1: {question}")
    browse.enter_a_question(question)
    browse.click_send_button()
    browse.validate_response_status(question_api=question)
    browse.click_expand_reference_in_response()
    browse.click_reference_link_in_response()
    browse.close_citation()

    duration = time.time() - start
    logger.info(f"[EXECUTION TIME] Browse Prompt 1 completed in {duration:.2f} seconds.")


@pytest.mark.parametrize("question", [browse_question2])
def test_browse_prompt2(setup_pages, question, request):
    request.node._nodeid = f"Validate response for BROWSE Prompt2 : {question}"
    page, _, browse, _, _ = setup_pages
    start = time.time()

    logger.info(f"Entering Browse Question 2: {question}")
    browse.enter_a_question(question)
    browse.click_send_button()
    browse.click_expand_reference_in_response()
    browse.click_reference_link_in_response()
    browse.close_citation()

    duration = time.time() - start
    logger.info(f"[EXECUTION TIME] Browse Prompt 2 completed in {duration:.2f} seconds.")


MAX_RETRIES = 3
RETRY_DELAY = 3  # seconds

@pytest.mark.parametrize("question", [generate_question1])
def test_generate_prompt(setup_pages, question, request):
    request.node._nodeid = f"Validate response for GENERATE Prompt1 : {question}"
    page, _, browse, generate, _ = setup_pages
    start = time.time()

    logger.info("Navigating to Generate Page.")
    browse.click_generate_button()

    logger.info("Deleting existing chat history after Generate page load.")
    generate.show_chat_history()
    generate.delete_chat_history()

    browse.validate_response_status(question_api=browse_question2)

    attempt = 1
    while attempt <= MAX_RETRIES:
        logger.info(f"Attempt {attempt}: Entering Generate Question: {question}")
        generate.enter_a_question(question)
        generate.click_send_button()

        time.sleep(2)
        response_text = page.locator("//p")
        latest_response = response_text.nth(response_text.count() - 1).text_content()

        if latest_response != invalid_response:
            logger.info(f"Valid response received on attempt {attempt}")
            generate.validate_response_status(question_api=question)
            break
        else:
            logger.warning(f"Invalid response received on attempt {attempt}")
            if attempt == MAX_RETRIES:
                check.not_equal(invalid_response, latest_response, f"Invalid response for: {question}")
            else:
                time.sleep(RETRY_DELAY)
        attempt += 1

    duration = time.time() - start
    logger.info(f"[EXECUTION TIME] Generate Prompt completed in {duration:.2f} seconds.")


@pytest.mark.parametrize("question", [add_section])
def test_add_section_prompt(setup_pages, question, request):
    request.node._nodeid = f"Validate response for GENERATE Prompt2 : {question}"
    _, _, browse, generate, _ = setup_pages
    start = time.time()

    logger.info("Navigating to Generate Page.")
    browse.click_generate_button()

    logger.info("Deleting existing chat history after Generate page load.")
    generate.show_chat_history()
    generate.delete_chat_history()

    logger.info(f"Entering Add Section Question: {question}")
    generate.enter_a_question(question)
    generate.click_send_button()
    browse.validate_response_status(question_api=question)

    duration = time.time() - start
    logger.info(f"[EXECUTION TIME] Add Section and Draft completed in {duration:.2f} seconds.")


def test_generate_draft_from_section_prompt(setup_pages, request):
    custom_title = "Validate Generate Draft & all sections are generated successfully"
    request.node._nodeid = custom_title

    _, _, browse, generate, draft = setup_pages
    start = time.time()

    logger.info("Navigating to Generate Page.")
    browse.click_generate_button()

    logger.info("Deleting existing chat history after Generate page load.")
    generate.show_chat_history()
    generate.delete_chat_history()

    logger.info("Clicking 'Generate Draft' and validating sections.")
    generate.click_generate_draft_button()
    draft.check_draft_Sections()

    duration = time.time() - start
    logger.info(f"[EXECUTION TIME] Generate Draft and Validate Sections completed in {duration:.2f} seconds.")
