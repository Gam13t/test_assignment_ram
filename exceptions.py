class RequestException(Exception):
    def __init__(
        self, 
        message='RequestException: Request Failed',
        original_exception=None,
    ):
        self.message = message
        self.original_exception = original_exception
        super().__init__(self.message)

    def __str__(self):
        if self.original_exception:
            return f"{self.message} - (Original exception: {self.original_exception})"
        return self.message


