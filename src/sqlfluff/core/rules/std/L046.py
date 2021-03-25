"""Implementation of Rule L046."""

from sqlfluff.core.rules.base import BaseRule, LintResult


class Rule_L046(BaseRule):
    """Jinja tags should have a single whitespace on either side.

    | **Anti-pattern**
    | Jinja tags with either no whitespace or very long whitespace
    | are hard to read.

    .. code-block::

        SELECT {{    a     }} from {{ref('foo')}}

    | **Best practice**
    | A single whitespace surrounding Jinja tags, alternatively
    | longer gaps containing newlines are acceptable.

    .. code-block::

        SELECT {{ a }} from {{ ref('foo') }};
        SELECT {{ a }} from {{
            ref('foo')
        }};
    """

    targets_templated = True

    @staticmethod
    def _get_whitespace_ends(s):
        """Remove tag ends and partition off any whitespace ends."""
        main = s[2:-2]
        inner = main.strip()
        pos = main.find(inner)
        return main[:pos], inner, main[pos + len(inner) :]

    def _eval(self, segment, templated_file, memory, **kwargs):
        # Extract some data from the segment. Importantly, all
        # of these have defaults in case we don't have an
        # enriched position marker.
        source_slice = getattr(segment.pos_marker, "source_slice", None)
        is_literal = getattr(segment.pos_marker, "is_literal", None)
        source_str = getattr(templated_file, "source_str", None)

        if source_slice and source_str and not is_literal:
            # Does it actually look like a tag?
            src_raw = source_str[source_slice]
            if not src_raw or src_raw[0] != "{" or src_raw[-1] != "}":
                return LintResult(memory=memory)

            # Dedupe usign a memory of source indexes.
            # This is important because several positions in the
            # templated file may refer to the same position in the
            # source file and we only want to get one violation.
            src_idx = source_slice.start
            if memory and src_idx in memory:
                return LintResult(memory=memory)
            if not memory:
                memory = set()
            memory.add(src_idx)

            # Get the inner section
            ws_pre, inner, ws_post = self._get_whitespace_ends(src_raw)

            # For the following section, whitespace should be a single
            # whitespace OR it should contain a newline.

            # Check the initial whitespace.
            if not ws_pre or (ws_pre != " " and "\n" not in ws_pre):
                return LintResult(memory=memory, anchor=segment)
            # Check latter whitespace.
            if not ws_post or (ws_post != " " and "\n" not in ws_post):
                return LintResult(memory=memory, anchor=segment)

        return LintResult(memory=memory)
