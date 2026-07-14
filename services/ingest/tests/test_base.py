"""Tests for shared adapter utilities."""

from adapters.base import is_bot_challenge_page, parse_key_value_table
from selectolax.parser import HTMLParser


def test_is_bot_challenge_page_detects_waf() -> None:
    html = '<html><body><div id="challenge-container"></div>AwsWafIntegration</body></html>'
    assert is_bot_challenge_page(html, status_code=202) is True


def test_is_bot_challenge_page_allows_normal_html() -> None:
    html = "<html><body><h1>八戸市 空き家</h1></body></html>"
    assert is_bot_challenge_page(html, status_code=200) is False


def test_parse_key_value_table_four_columns() -> None:
    html = """
    <table>
      <tr><th>所在地</th><td>青森県</td><th>価格</th><td>200万円</td></tr>
      <tr><th>間取り</th><td>4LDK</td><th>土地面積</th><td>198㎡</td></tr>
    </table>
    """
    fields = parse_key_value_table(HTMLParser(html))
    assert fields["所在地"] == "青森県"
    assert fields["価格"] == "200万円"
    assert fields["間取り"] == "4LDK"
    assert fields["土地面積"] == "198㎡"
