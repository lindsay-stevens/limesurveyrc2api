class LimeSurveyError(Exception):
    """Base class for exceptions in LimeSurvey."""
    def __init__(self, method, *args):
        base_err = "Error during query"
        message = [base_err, method]
        if args is not None:
            message += [str(x) for x in args]
        self.message = " | ".join(message)
