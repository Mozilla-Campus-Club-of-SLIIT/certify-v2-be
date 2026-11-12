from reportlab.lib import colors

from services.certificate_pdf import _to_pdf_color


def test_three_digit_hex_white():
    assert _to_pdf_color("#FFF") == colors.Color(1, 1, 1, 1)


def test_three_digit_hex_red():
    assert _to_pdf_color("#F00") == colors.Color(1, 0, 0, 1)


def test_six_digit_unchanged():
    assert _to_pdf_color("#FF0000") == colors.Color(1, 0, 0, 1)

