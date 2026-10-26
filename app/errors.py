class PipelineError(Exception):
    """A failure that maps to an ErrorResult code."""

    def __init__(self, code: str, detail: str = ""):
        super().__init__(detail or code)
        self.code = code
        self.detail = detail
