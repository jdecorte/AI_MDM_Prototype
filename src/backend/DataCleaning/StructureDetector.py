import re

class StructureDetector:
    def __init__(self, series, exception_chars, compress):
        self.series = series
        self.exception_chars = exception_chars
        self.compress = compress  

    def find_structure(self):
        self.series = self.series.astype(str)
        regex_pattern_to_remove = '[^a-zA-Z0-9'+ self.exception_chars+']+'
        self.series = self.series.apply(lambda x: re.sub(regex_pattern_to_remove, '', x))
        self.series = self.series.apply(lambda x: re.sub('[a-zA-Z]', 'X', x))
        self.series = self.series.apply(lambda x: re.sub('[0-9]', '9', x))
        if self.compress:
            self.series = self._compress_values_of_series()
        return self.series
    
    def _compress_values_of_series(self):
        # If a character is followed by the same character, this character is removed
        # Example: "XX9" -> "X9"
        self.series = self.series.apply(lambda x: re.sub(r'([X9])\1+', r'\1', x))
        return self.series