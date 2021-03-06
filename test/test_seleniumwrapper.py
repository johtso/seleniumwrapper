import sys
sys.path.append("./../src")
if sys.version < '2.7':
    import unittest2 as unittest
else:
    import unittest
import mock
import seleniumwrapper
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from seleniumwrapper.wrapper import SeleniumWrapper
from seleniumwrapper.wrapper import SeleniumContainerWrapper
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException, ElementNotVisibleException

class TestSeleniumWrapperFactory(unittest.TestCase):

    def test_factory_functions_raise_typeerror_if_argument_is_not_a_string(self):
        self.assertRaises(TypeError, seleniumwrapper.create, 1)
        self.assertRaises(TypeError, seleniumwrapper.connect, 1, "http://somethings:9999/wd/hub")
        self.assertRaises(TypeError, seleniumwrapper.connect, "android", 1)

    def test_factory_functions_raise_valueerror_if_invalid_drivername_is_given(self):
        self.assertRaises(ValueError, seleniumwrapper.create, 'Chorome')
        self.assertRaises(ValueError, seleniumwrapper.create, 'Firedog')
        self.assertRaises(ValueError, seleniumwrapper.connect, 'Chorome', "http://localhost:8080/wd/hub")
        self.assertRaises(ValueError, seleniumwrapper.connect, 'Firedog', "http://localhost:8080/wd/hub")

    def test_connect_merge_3rd_arguments_with_desired_capabilities(self):
        p = mock.patch("selenium.webdriver.Remote")
        m = p.start()
        p2 = mock.patch("seleniumwrapper.wrapper.SeleniumWrapper")
        m2 = p2.start()
        seleniumwrapper.connect("android", "http://localhost:4444/wd/hub", {"hoge":"hoge"})
        dic = DesiredCapabilities.ANDROID
        dic["hoge"] = "hoge"
        m.assert_called_once_with('http://localhost:4444/wd/hub', dic)
        p2.stop()
        p.stop()

class TestSeleniumWrapper(unittest.TestCase):

    def test_init_raise_if_driver_is_not_a_webdriver_object(self):
        self.assertRaises(TypeError, SeleniumWrapper, 'hoge')

    def test_init_not_raise_if_driver_is_a_webdriver_object(self):
        mocked_driver = mock.Mock(WebDriver)
        SeleniumWrapper(mocked_driver)

    def test_wrapper_should_delegate_unknown_attribute_access_to_wrapped_driver(self):
        mocked_driver = mock.Mock(WebDriver)
        mocked_driver.hoge = lambda d: d
        wrapper = SeleniumWrapper(mocked_driver)
        self.assertEquals(wrapper.hoge(1), 1)

    def test_wrapper_should_raise_AttributeError_if_wrapped_driver_also_dont_have_attribute_with_given_name(self):
        mocked_driver = mock.Mock(WebDriver)
        wrapper = SeleniumWrapper(mocked_driver)
        self.assertRaises(AttributeError, getattr, *[wrapper, 'hoge'])

    def test_wrapper_should_chain_wrapping_if_possible(self):
        mocked_driver = mock.Mock(WebDriver)
        mocked_element = mock.Mock(WebElement)
        mocked_driver.find_element_by_id = lambda given: given
        wrapper = SeleniumWrapper(mocked_driver)
        wrapped_element = wrapper.find_element_by_id(mocked_element)
        unwrapped_element = wrapper.find_element_by_id("hoge")
        self.assertTrue(isinstance(wrapped_element, SeleniumWrapper))
        self.assertFalse(isinstance(unwrapped_element, SeleniumWrapper))

    def test_wrapper_should_respond_to_waitfor(self):
        mocked_driver = mock.Mock(WebDriver)
        mocked_driver.find_element_by_id = lambda target: target
        wrapper = SeleniumWrapper(mocked_driver)
        self.assertEquals(wrapper.waitfor('id', 'hoge'), 'hoge')

    def test_wrapper_should_handle_attr_access_even_if_attr_is_descriptor(self):
        mocked_element = mock.Mock(WebElement)
        class Hoge(WebDriver):
            def __init__(self):
                pass
            @property
            def hoge(self):
                return mocked_element
            @property
            def num(self):
                return 100
        mocked_driver = Hoge()
        wrapper = SeleniumWrapper(mocked_driver)
        self.assertEquals(wrapper.num, 100)
        self.assertTrue(isinstance(wrapper.hoge, SeleniumWrapper), wrapper.hoge)

    def test_click_should_raise_if_element_is_not_stopping_for_time_seconds(self):
        class Hoge(object):
            def __init__(self):
                self.num = 0
            def __getitem__(self, num):
                self.num += 1
                return self.num

        mocked_element = mock.Mock(WebElement)
        mocked_element.location = Hoge()
        wrapper = SeleniumWrapper(mocked_element)
        self.assertRaises(WebDriverException, wrapper.click, **{'timeout':0.5})

    def test_click_should_raise_if_element_is_not_clickable_for_timeout_seconds(self):
        def dummy():
            raise WebDriverException("hoge:fuga:huhuhu")
        mocked_element = mock.Mock(WebElement)
        mocked_element.click = dummy
        mocked_element.value_of_css_property.return_value = 0
        mocked_element.location = {"x":0, "y":0}
        wrapper = SeleniumWrapper(mocked_element)
        self.assertRaises(WebDriverException, wrapper.click, **{'timeout':0.5})

    def test_click_should_raise_if_element_is_not_displayed_for_timeout_seconds(self):
        mocked_element = mock.Mock(WebElement)
        mocked_element.is_displayed = lambda : False
        mocked_element.value_of_css_property.return_value = 0
        mocked_element.location = {"x":0, "y":0}
        wrapper = SeleniumWrapper(mocked_element)
        self.assertRaises(ElementNotVisibleException, wrapper.click, **{'timeout':0.5})

    def test_click_should_raise_if_other_exception_is_thrown(self):
        def dummy():
            raise TypeError()
        mocked_element = mock.Mock(WebElement)
        mocked_element.click = dummy
        wrapper = SeleniumWrapper(mocked_element)
        self.assertRaises(TypeError, wrapper.click, **{'timeout':0.5})

    def test_unwrap_return_its_wrapped_object(self):
        mocked_element = mock.Mock(WebElement)
        wrapper = SeleniumWrapper(mocked_element)
        self.assertIsInstance(wrapper.unwrap, WebElement)

class TestSeleniumWrapperAliases(unittest.TestCase):

    def setUp(self):
        mocky = mock.Mock(WebDriver)
        self.mock = mocky

    def test_waitfor_raise_if_find_element_return_falsy_value(self):
        self.mock.find_element_by_xpath.return_value = None
        wrapper = SeleniumWrapper(self.mock)
        self.assertRaises(NoSuchElementException, wrapper.waitfor, *['xpath', 'dummy'], **{'timeout':0.1})

    def test_waitfor_raise_if_find_elements_return_falsy_value(self):
        self.mock.find_elements_by_xpath.return_value = []
        wrapper = SeleniumWrapper(self.mock)
        self.assertRaises(NoSuchElementException, wrapper.waitfor, *['xpath', 'dummy'], **{'eager':True, 'timeout':0.1})

    def test_waitfor_wraps_its_return_value_if_it_is_wrappable(self):
        mock_elem = mock.Mock(WebElement)
        self.mock.find_element_by_xpath.return_value = mock_elem
        wrapper = SeleniumWrapper(self.mock)
        self.assertIsInstance(wrapper.waitfor("xpath", "dummy"), SeleniumWrapper)

    def test_waitfor_wraps_its_return_value_if_given_eager_arument_is_true(self):
        mock_elem = mock.Mock(WebElement)
        self.mock.find_elements_by_xpath.return_value = [mock_elem]
        wrapper = SeleniumWrapper(self.mock)
        self.assertIsInstance(wrapper.waitfor("xpath", "dummy", eager=True), SeleniumContainerWrapper)

    def test_aliases_work_correctly(self):
        mock_elem = mock.Mock(WebElement)
        self.mock.find_element_by_xpath.return_value = mock_elem
        self.mock.find_element_by_css_selector.return_value = mock_elem
        self.mock.find_element_by_tag_name.return_value = mock_elem
        self.mock.find_element_by_class_name.return_value = mock_elem
        self.mock.find_element_by_id.return_value = mock_elem
        self.mock.find_element_by_name.return_value = mock_elem
        self.mock.find_element_by_link_text.return_value = mock_elem
        self.mock.find_element_by_partial_link_text.return_value = mock_elem
        wrapper = SeleniumWrapper(self.mock)

        self.assertIsInstance(wrapper.xpath("dummy"), SeleniumWrapper)
        self.assertIsInstance(wrapper.css("dummy"), SeleniumWrapper)
        self.assertIsInstance(wrapper.by_tag("dummy"), SeleniumWrapper)
        self.assertIsInstance(wrapper.by_class("dummy"), SeleniumWrapper)
        self.assertIsInstance(wrapper.by_id("dummy"), SeleniumWrapper)
        self.assertIsInstance(wrapper.by_name("dummy"), SeleniumWrapper)
        self.assertIsInstance(wrapper.by_linktxt("dummy"), SeleniumWrapper)
        self.assertIsInstance(wrapper.by_linktxt("dummy", partial=True), SeleniumWrapper)
        self.assertIsInstance(wrapper.href("dummy"), SeleniumWrapper)
        self.assertIsInstance(wrapper.img(alt="dummy"), SeleniumWrapper)
        self.assertIsInstance(wrapper.by_text("dummy", "dummy"), SeleniumWrapper)
        self.assertIsInstance(wrapper.button("dummy"), SeleniumWrapper)

        wrapped_elem = mock.Mock(WebElement)
        wrapped_elem.find_element_by_xpath.return_value = mock_elem
        wrapper = SeleniumWrapper(wrapped_elem)
        self.assertIsInstance(wrapper.parent, SeleniumWrapper)

def suite():
    suite = unittest.TestSuite()
    suite.addTests(unittest.makeSuite(TestSeleniumWrapperAliases))
    suite.addTests(unittest.makeSuite(TestSeleniumWrapper))
    return suite

if __name__ == "__main__":
    s = suite()
    unittest.TextTestRunner(verbosity=2).run(s)
