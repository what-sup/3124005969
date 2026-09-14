"""Text normalization and tokenization helpers."""

import logging
import unicodedata

import jieba

# The dependency may otherwise emit initialization messages on stderr.
jieba.setLogLevel(logging.ERROR)


class _InMemoryTokenizer(jieba.Tokenizer):
    """Initialize jieba's bundled dictionary without creating a cache file."""

    def initialize(self, dictionary=None) -> None:
        if dictionary is not None and dictionary != self.dictionary:
            raise ValueError("自定义词典不是本程序支持的输入")
        if self.initialized:
            return
        with self.lock:
            if self.initialized:
                return
            self.FREQ, self.total = self.gen_pfdict(self.get_dict_file())
            self.initialized = True


_TOKENIZER = _InMemoryTokenizer()


def normalize_text(text: str) -> str:
    """Normalize Unicode width and line endings without changing word order."""
    normalized = unicodedata.normalize("NFKC", text)
    return normalized.replace("\r\n", "\n").replace("\r", "\n")


def _is_meaningful(token: str) -> bool:
    """Return whether a token contains at least one letter, digit, or CJK character."""
    return any(map(str.isalnum, token))


def tokenize(text: str) -> list[str]:
    """Normalize and segment text, omitting whitespace- and punctuation-only tokens."""
    tokens: list[str] = []
    for raw_token in _TOKENIZER.lcut(normalize_text(text), HMM=True):
        token = raw_token.strip().casefold()
        if token and _is_meaningful(token):
            tokens.append(token)
    return tokens
