from django import forms


class MultipleValueField(forms.MultipleChoiceField):
    """
    Allows multiple values, but is not restricted to values in 'choices'
    """
    def valid_value(self, value):
        return True
