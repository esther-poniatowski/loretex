# Edge Cases

Words like pre*fix and suf*fix should not become italic.
Words like pre_fix and suf_fix should not become italic.

Markers with spacing: *italic* works, but asterisk*stuck should not.
Underscore with digits: _ok_ but x_1 should stay.

Inline code with special chars: `a_b%#\\` and `x{y}`.

List markers in text: 1.2 should not start a list when inside a sentence.
