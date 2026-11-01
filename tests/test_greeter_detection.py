import unittest

from PIL import Image, ImageDraw

from greeter_vm_test import has_centered_login_prompt


class GreeterDetectionTests(unittest.TestCase):
    def test_detects_centered_login_panel_and_controls(self):
        image = Image.new("RGB", (100, 100), (5, 25, 55))
        draw = ImageDraw.Draw(image)
        draw.rectangle((40, 40, 59, 64), fill=(45, 45, 45))
        draw.rectangle((45, 48, 51, 53), fill=(240, 240, 240))

        self.assertTrue(has_centered_login_prompt(image))

    def test_rejects_background_without_login_panel(self):
        image = Image.new("RGB", (100, 100), (5, 25, 55))

        self.assertFalse(has_centered_login_prompt(image))


if __name__ == "__main__":
    unittest.main()
