class Callout:

    class CSSClasses:
        CALLOUT = "callout"
        CALLOUT_WITH_BUTTON = "callout--with-button"
        CALLOUT_STATES = {
            "success": "callout--success",
            "warn": "callout--warn",
        }

    def __init__(self, state=None, heading=None, text=None, button=None):
        """
        Creates a Callout object that can be used to create callout blocks in templates.

        :param state:       STRING - ("success", "warn") - to apply optional styling
        :param heading:     STRING - heading text to display
        :param text:        STRING - description text to display
        :param button:      CalloutButton - button to display
        """
        self.state = state
        self.heading = heading
        self.text = text
        self.button = button

        # self.allowed_keys = {"state", "heading", "text", "button"}
        # self.__dict__.update((k, v) for k, v in args.items() if k in self.allowed_keys)

    @property
    def css_class(self):
        css_class = self.CSSClasses.CALLOUT
        if self.state:
            css_class += f" {self.CSSClasses.CALLOUT_STATES.get(self.state.lower(), '')}"

        if self.button and self.button.visible:
            css_class += f" {self.CSSClasses.CALLOUT_WITH_BUTTON}"

        return css_class


class CalloutButton:

    class CSSClasses:
        BUTTON = "callout__button"
        BUTTON_TYPES = {
            "start": "callout__button--start",
        }

    def __init__(self, form_action=None, form_method="POST", text=None, href=None, button_type=None):
        """
        Helper to add a form or simple button to Callout.
        """
        self.form_action = form_action
        self.form_method = form_method
        self.text = text
        self.href = href
        self.button_type = button_type

    @property
    def visible(self):
        return self.form_action or self.href

    @property
    def button_css_class(self):
        css_class = self.CSSClasses.BUTTON
        if self.button_type:
            css_class += f" {self.CSSClasses.BUTTON_TYPES.get(self.button_type.lower(), '')}"
        return css_class
