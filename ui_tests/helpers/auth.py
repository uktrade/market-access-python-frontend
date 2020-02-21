from ui_tests import settings


def sso_sign_in(browser):
    browser.visit(settings.TEST_SSO_LOGIN_URL)

    browser.fill("username", settings.TEST_SSO_EMAIL)
    browser.fill("password", settings.TEST_SSO_PASSWORD)
    browser.find_by_css("input[type=submit]").first.click()
