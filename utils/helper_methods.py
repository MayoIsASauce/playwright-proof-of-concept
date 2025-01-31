from playwright.sync_api import Page

def __get_selector(page: Page, selector: str):
    el = page.query_selector(selector)
    if el is None: raise AssertionError(f"Query Selector '{selector}' not found")
    return el

def element_type(page: Page, selector: str, value: str) -> bool:
    try: el = __get_selector(page, selector)
    except AssertionError: return False

    el.fill(value)
    return True

def element_type_d(page: Page, selector: str, value: str, delay: float) -> bool:
    try: el = __get_selector(page, selector)
    except AssertionError: return False

    el.type(value, delay=delay)
    return True

def element_click(page: Page, selector: str) -> bool:
    try: el = __get_selector(page, selector)
    except AssertionError: return False

    el.click()
    return True

def element_hover(page: Page, selector: str) -> bool:
    try: el = __get_selector(page, selector)
    except AssertionError: return False

    el.hover()
    return True

def is_loading(page: Page) -> bool:
    return page.query_selector("#loading_layer").get_property("style").json_value()['display'] != 'none'