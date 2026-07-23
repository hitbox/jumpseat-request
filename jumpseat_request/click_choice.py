import click

class ModelChoice(click.ParamType):
    """
    Click paramater option with choices from datbase.
    """

    name = 'model_choice'

    def __init__(self, query_factory, value_getter=None):
        self.query_factory = query_factory
        self.value_getter = value_getter

    def convert(self, value, param, context):
        choices = self.query_factory()
        match = next((c for c in choices if self.value_getter(c) == value.casefold()), None)
        if match is None:
            self.fail(
                f'{value!r} is not a valid choice.'
                f' Valid choices: {list(self.value_getter(c) for c in choices)}',
                param,
                context,
            )
        return match
