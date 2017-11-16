from selenium.webdriver import Chrome, ChromeOptions


def init_chrome_driver(maximized, headless, surpress_notifications):
    options = ChromeOptions()
    if surpress_notifications:
        prefs = {"profile.default_content_setting_values.notifications": 2}
        options.add_experimental_option("prefs", prefs)
    if maximized:
        options.add_argument("--start-maximized")
    if headless:
        options.add_argument("--headless")
    return Chrome(chrome_options=options)


def init_firefox_driver(maximized, headless, surpress_notifications):
    raise Exception("Firefox driver init function not implemented")


def init_driver(driver_name, maximized=True, headless=True, 
    surpress_notifications=True):
    """ 
    Permet de crer et de configurer le browser 
    Args:   string driver_name Le driver de navigateur a utiliser: 
        chrome, firefox...
    Kwargs: bool maximized True pour agrandir la fenetre
            bool headless True pour avoir un navigateur sans affichage
            bool surpress_notifications True pour blocker les notificatiosn
    Retourne le webdriver browser
    """

    if driver_name == 'chrome':
        return init_chrome_driver(maximized, headless, surpress_notifications)
    elif driver_name == 'firefox':
        return init_firefox_driver(maximized, headless, surpress_notifications)
    else:
        raise Exception('The webdriver "%s" is not supported' % driver_name)