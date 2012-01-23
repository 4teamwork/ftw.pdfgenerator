class CustomPatternAtPlaceholderWrapper(object):
    """
    Used for creating a custom pattern at a specific placeholder.
    It is used instead of a normal mode, wrapping the real mode and defining
    where to insert the placeholder. See placeholders in interfaces module.
    """

    def __init__(self, mode, placeholder):
        self.mode = mode
        self.placeholder = placeholder
