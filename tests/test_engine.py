import unittest
import xml.etree.ElementTree as ET

from svgforge import TONES, Canvas, T, cols, measure, oklch_to_hex, unmeasured, weighted_cols, wrap


class EngineTest(unittest.TestCase):
    def test_measure_uses_the_width_table(self):
        self.assertAlmostEqual(measure("AB", 10), 13.34)
        self.assertAlmostEqual(measure("AB", 10, bold=True), 13.34 * 1.055)

    def test_unmeasured_glyphs_are_named(self):
        self.assertEqual(unmeasured("a·b—c"), {"·", "—"})
        self.assertEqual(unmeasured("plain ASCII"), set())

    def test_wrap_breaks_on_measured_width(self):
        lines = wrap("one two three four five seven", 12.5, 80)
        self.assertGreater(len(lines), 1)
        self.assertTrue(all(measure(ln, 12.5) <= 80 or " " not in ln for ln in lines))
        self.assertEqual(wrap("a\nb", 12, 500), ["a", "b"])

    def test_oklch_endpoints(self):
        self.assertEqual(oklch_to_hex(1, 0, 0), "#FFFFFF")
        self.assertEqual(oklch_to_hex(0, 0, 0), "#000000")

    def test_accent_aliases_match(self):
        self.assertEqual(T.AMBER, T.ACCENT)
        self.assertEqual(TONES["amber"], TONES["accent"])

    def test_text_never_goes_below_the_floor(self):
        c = Canvas(400, "t")
        c.text(10, 20, "tiny", size=7)
        self.assertIn('font-size="11"', c._n[-1])

    def test_render_is_valid_xml_with_escaped_alt(self):
        c = Canvas(600, 'A "quoted" title')
        y = c.header()
        y = c.card(c.pad, y, 300, "Card", ["one line", "two < three & four"])
        alt = 'An alt with "quotes" & an ampersand.'
        svg = c.render(c.finish(y), alt)
        root = ET.fromstring(svg)
        self.assertEqual(root.get("aria-label"), alt)
        self.assertEqual(root.find("{http://www.w3.org/2000/svg}desc").text, alt)
        self.assertIn("two &lt; three &amp; four", svg)

    def test_columns_fill_the_width(self):
        xs, w = cols(0, 100, 2, gap=20)
        self.assertEqual((xs, w), ([0, 60], 40))
        xs, ws = weighted_cols(0, 120, [2, 1], gap=0)
        self.assertEqual(ws, [80, 40])


if __name__ == "__main__":
    unittest.main()
