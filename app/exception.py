class JobNotFoundException(Exception):
    pass


class JobResultsNotFoundException(Exception):
    pass


class JobStatusNotFoundException(Exception):
    pass


class NotInCacheException(Exception):
    pass


class RequestSubmissionException(Exception):
    pass


class RequestTimeoutException(Exception):
    pass
