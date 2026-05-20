"""Unit tests for scripts/lib/masking_logger.py."""

from __future__ import annotations

from lib.masking_logger import mask_string


class TestMaskString:
    def test_masks_google_access_token(self):
        s = "token=ya29.a0AcM612testxxxxxxxxxxx end"
        masked = mask_string(s)
        assert "ya29.a0AcM612testxxxxxxxxxxx" not in masked
        assert "<MASKED:" in masked

    def test_masks_google_refresh_token(self):
        s = "refresh=1//0gabcdefghijklmn end"
        masked = mask_string(s)
        assert "1//0gabcdefghijklmn" not in masked
        assert "<MASKED:" in masked

    def test_masks_meta_token(self):
        s = "EAABbbbbCCCCDDDDeeeeFFFF"
        masked = mask_string(s)
        assert "EAABbbbbCCCCDDDDeeeeFFFF" not in masked

    def test_masks_json_refresh_token_field(self):
        s = '{"refresh_token":"1//0gsomelonglongtoken","other":"keep"}'
        masked = mask_string(s)
        assert "1//0gsomelonglongtoken" not in masked
        assert "keep" in masked

    def test_masks_json_app_secret_field(self):
        s = '{"app_secret":"abc123defgh456jkl789"}'
        masked = mask_string(s)
        assert "abc123defgh456jkl789" not in masked

    def test_leaves_non_tokens_untouched(self):
        s = "This is a normal log line with no secrets"
        assert mask_string(s) == s

    def test_short_values_masked_as_placeholder(self):
        # Short values like <MASKED> (no prefix/suffix)
        s = '{"refresh_token":"short"}'
        masked = mask_string(s)
        assert "short" not in masked
