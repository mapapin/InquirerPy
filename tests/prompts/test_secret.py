import unittest
from unittest.mock import ANY, call, patch

from prompt_toolkit.buffer import Buffer
from prompt_toolkit.enums import EditingMode
from prompt_toolkit.input import create_pipe_input
from prompt_toolkit.output import DummyOutput

from InquirerPy.prompts.secret import SecretPrompt
from InquirerPy.validator import PasswordValidator


class TestSecret(unittest.TestCase):
    def setUp(self):
        self.inp = create_pipe_input()

    def tearDown(self):
        self.inp.close()

    def test_prompt_result(self):
        self.inp.send_text("what\n")
        secret_prompt = SecretPrompt(
            message="hello",
            style={"answer": ""},
            default="yes",
            qmark="~",
            editing_mode="default",
            input=self.inp,
            output=DummyOutput(),
        )
        result = secret_prompt.execute()
        self.assertEqual(result, "yeswhat")
        self.assertEqual(secret_prompt.status, {"answered": True, "result": "yeswhat"})

    @patch.object(Buffer, "validate_and_handle")
    def test_prompt_validation(self, mocked_validate):
        def _hello():
            secret_prompt.session.app.exit(result="yes")

        mocked_validate.side_effect = _hello
        self.inp.send_text("afas\n")
        secret_prompt = SecretPrompt(
            message="what",
            style={},
            validate=PasswordValidator(length=8),
            input=self.inp,
            output=DummyOutput(),
        )
        result = secret_prompt.execute()
        mocked_validate.assert_called_once()
        self.assertEqual(result, "yes")
        self.assertEqual(secret_prompt.status["answered"], False)
        self.assertEqual(secret_prompt.status["result"], None)

    def test_prompt_message(self):
        secret_prompt = SecretPrompt(
            message="fooboo", style={}, qmark="[?]", editing_mode="vim"
        )
        message = secret_prompt._get_prompt_message()
        self.assertEqual(
            message,
            [
                ("class:questionmark", "[?]"),
                ("class:question", " fooboo"),
                ("class:instruction", " "),
            ],
        )

        secret_prompt.status["answered"] = True
        secret_prompt.status["result"] = "hello"
        message = secret_prompt._get_prompt_message()
        self.assertEqual(
            message,
            [
                ("class:questionmark", "[?]"),
                ("class:question", " fooboo"),
                ("class:answer", " *****"),
            ],
        )

    @patch("InquirerPy.prompts.input.SimpleLexer")
    @patch("InquirerPy.prompts.secret.SecretPrompt._get_prompt_message")
    @patch("InquirerPy.base.Style.from_dict")
    @patch("InquirerPy.base.KeyBindings")
    @patch("InquirerPy.prompts.input.PromptSession")
    def test_callable_called(
        self,
        MockedSession,
        MockedKeyBindings,
        MockedStyle,
        mocked_message,
        MockedLexer,
    ):
        kb = MockedKeyBindings()
        style = MockedStyle()
        lexer = MockedLexer()
        SecretPrompt(
            message="what",
            style={},
            default="111",
            qmark="[!]",
            editing_mode="vim",
        )

        MockedSession.assert_called_once_with(
            message=mocked_message,
            key_bindings=kb,
            style=style,
            completer=None,
            validator=ANY,
            validate_while_typing=False,
            input=None,
            output=None,
            editing_mode=EditingMode.VI,
            lexer=lexer,
            is_password=True,
            multiline=False,
        )
        MockedStyle.assert_has_calls([call({})])
        MockedLexer.assert_has_calls([call("class:input")])
