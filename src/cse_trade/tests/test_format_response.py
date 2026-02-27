import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from cse_trade.agents.chatbot import format_response

def test_format_response_basic():
    text = "Hello world"
    assert format_response(text) == "Hello world"

def test_format_response_metadata_wrapper():
    text = "AIMessage(content='Hello world', additional_kwargs={}, response_metadata={'model_name': 'gpt-4o'})"
    # The current regex for AIMessage(content=...) is a bit specific, let's see how it handles it
    assert "Hello world" in format_response(text)

def test_format_response_json_content():
    text = '{"content": "This is the actual response", "metadata": "ignored"}'
    assert format_response(text) == "This is the actual response"

def test_format_response_bullets():
    text = "- Item 1\n- Item 2\n* Item 3"
    formatted = format_response(text)
    assert "• Item 1" in formatted
    assert "• Item 2" in formatted
    assert "• Item 3" in formatted

def test_format_response_dirty_langchain():
    text = "content='Check out these gainers:\\n- BIL: 10%\\n- LOLC: 5%' additional_kwargs={} response_metadata={'id': '123'}"
    formatted = format_response(text)
    print(f"DEBUG: Formatted: {repr(formatted)}")
    assert "Check out these gainers:" in formatted
    assert "• BIL: 10%" in formatted
    assert "additional_kwargs" not in formatted

def test_format_response_signature_leak():
    text = "type: 'text' text: 'The market is up today.' extras: signature: 'HugeGarbageString123456789'"
    formatted = format_response(text)
    assert "The market is up today." in formatted
    assert "HugeGarbageString" not in formatted

def test_format_response_internal_quotes():
    text = "type: 'text' text: 'It\'s a bull market with \"high\" volatility' extras: signature: 'abc'"
    formatted = format_response(text)
    print(f"DEBUG Internal Quotes: {repr(formatted)}")
    assert "It's a bull market with \"high\" volatility" in formatted

if __name__ == "__main__":
    test_format_response_basic()
    test_format_response_metadata_wrapper()
    test_format_response_json_content()
    test_format_response_bullets()
    test_format_response_dirty_langchain()
    test_format_response_signature_leak()
    test_format_response_internal_quotes()
    print("All tests passed!")
