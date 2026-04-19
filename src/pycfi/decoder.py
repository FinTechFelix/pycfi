from __future__ import annotations

from dataclasses import dataclass, field

from .map import ATTRIBUTE_MAP, CATEGORY_MAP, GROUP_MAP


@dataclass
class CFIAttribute:
    """A single decoded attribute from positions 3–6 of a CFI code."""

    position: int
    name: str | None
    value: str | None
    options: list[str] = field(default_factory=list)


class CFICode:
    """Decodes an ISO 10962 CFI code into its category, group, and attributes.

    Instantiate with a 6-character CFI code string. Decoded fields are
    available directly on the instance.

    Example::

        code = CFICode("RWSNCA")
        code.category          # "entitlements"
        code.group             # "warrants"
        code.get_attribute("underlying_assets").value  # "equities"
    """

    def __init__(self, code: str, show_options: bool = False) -> None:
        if not isinstance(code, str):
            raise ValueError("CFI code must be of type str.")
        code = code.upper()
        if len(code) != 6:
            raise ValueError("CFI code must be exactly 6 characters long.")

        self.raw: str = code

        category_letter = code[0]
        group_letter = code[1]

        category = CATEGORY_MAP.get(category_letter)
        self.category: str | None = category.lower() if category else None

        group = GROUP_MAP.get(category_letter, {}).get(group_letter)
        self.group: str | None = group.lower() if group else None

        self.attributes: list[CFIAttribute] = []
        mapping_key = (category_letter, group_letter)

        if mapping_key in ATTRIBUTE_MAP:
            for idx, attr_info in enumerate(ATTRIBUTE_MAP[mapping_key]):
                name = attr_info.get("name")
                # Skip not-applicable placeholder positions
                if name and name.startswith("na_"):
                    continue
                raw_char = code[2 + idx]
                attr_value = attr_info["mapping"].get(raw_char)
                options = (
                    [v.lower() for v in attr_info["mapping"].values()]
                    if show_options
                    else []
                )
                self.attributes.append(
                    CFIAttribute(
                        position=idx + 3,
                        name=name,
                        value=attr_value.lower() if attr_value else None,
                        options=options,
                    )
                )
        else:
            for i in range(4):
                self.attributes.append(
                    CFIAttribute(
                        position=i + 3,
                        name=None,
                        value=code[2 + i].lower(),
                    )
                )

    def get_attribute(self, name: str) -> CFIAttribute | None:
        """Return the attribute with the given name, or None if not present."""
        return next((a for a in self.attributes if a.name == name), None)

    def __str__(self) -> str:
        lines = [
            f"CFICode({self.raw!r})",
            f"  Category : {self.category or 'unknown'}",
            f"  Group    : {self.group or 'unknown'}",
        ]
        if self.attributes:
            lines.append("  Attributes:")
            max_name = max(
                (len(a.name) for a in self.attributes if a.name), default=0
            )
            for attr in self.attributes:
                name = attr.name or "unknown"
                value = attr.value or "unknown"
                lines.append(f"    {name:<{max_name}} : {value}")
        return "\n".join(lines)

    def __repr__(self) -> str:
        return (
            f"CFICode({self.raw!r}, "
            f"category={self.category!r}, "
            f"group={self.group!r})"
        )

    def __eq__(self, other: object) -> bool:
        if isinstance(other, CFICode):
            return self.raw == other.raw
        return NotImplemented


if __name__ == "__main__":
    print(CFICode("RWSNCA"))
    print(CFICode("RWSNCA").get_attribute("underlying_assets"))
