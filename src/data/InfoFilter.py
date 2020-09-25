import logging


class InfoFilter(logging.Filter):
    def filter(self, rec):
        return rec.levelno == logging.INFO
