from django import template

register = template.Library()


# Matching labels with what React producing
# see ./core/frontend/src/js/react/commodities/CodeInput.js
CODE_BOX_LABELS = {
    0: "First",
    1: "Second",
    2: "Third",
    3: "Fourth",
    4: "Fifth",
}


@register.filter
def code_box_label(counter):
    """Used to help generate the label text for commodity input boxes"""
    try:
        return CODE_BOX_LABELS[counter]
    except KeyError:
        return ""
