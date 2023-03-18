# from dataprep.clean import clean_df
import pandas as pd
import math
"""
Clean a DataFrame column containing text data.
"""
import re
import string
from functools import partial, update_wrapper
from typing import Any, Callable, Dict, List, Optional, Set, Union
from unicodedata import normalize

import dask.dataframe as dd
import numpy as np
import pandas as pd

english_stopwords = {
    "i",
    "me",
    "my",
    "myself",
    "we",
    "our",
    "ours",
    "ourselves",
    "you",
    "you're",
    "you've",
    "you'll",
    "you'd",
    "your",
    "yours",
    "yourself",
    "yourselves",
    "he",
    "him",
    "his",
    "himself",
    "she",
    "she's",
    "her",
    "hers",
    "herself",
    "it",
    "it's",
    "its",
    "itself",
    "they",
    "them",
    "their",
    "theirs",
    "themselves",
    "what",
    "which",
    "who",
    "whom",
    "this",
    "that",
    "that'll",
    "these",
    "those",
    "am",
    "is",
    "are",
    "was",
    "were",
    "be",
    "been",
    "being",
    "have",
    "has",
    "had",
    "having",
    "do",
    "does",
    "did",
    "doing",
    "a",
    "an",
    "the",
    "and",
    "but",
    "if",
    "or",
    "because",
    "as",
    "until",
    "while",
    "of",
    "at",
    "by",
    "for",
    "with",
    "about",
    "against",
    "between",
    "into",
    "through",
    "during",
    "before",
    "after",
    "above",
    "below",
    "to",
    "from",
    "up",
    "down",
    "in",
    "out",
    "on",
    "off",
    "over",
    "under",
    "again",
    "further",
    "then",
    "once",
    "here",
    "there",
    "when",
    "where",
    "why",
    "how",
    "all",
    "any",
    "both",
    "each",
    "few",
    "more",
    "most",
    "other",
    "some",
    "such",
    "no",
    "nor",
    "not",
    "only",
    "own",
    "same",
    "so",
    "than",
    "too",
    "very",
    "s",
    "t",
    "can",
    "will",
    "just",
    "don",
    "don't",
    "should",
    "should've",
    "now",
    "d",
    "ll",
    "m",
    "o",
    "re",
    "ve",
    "y",
    "ain",
    "aren",
    "aren't",
    "couldn",
    "couldn't",
    "didn",
    "didn't",
    "doesn",
    "doesn't",
    "hadn",
    "hadn't",
    "hasn",
    "hasn't",
    "haven",
    "haven't",
    "isn",
    "isn't",
    "ma",
    "mightn",
    "mightn't",
    "mustn",
    "mustn't",
    "needn",
    "needn't",
    "shan",
    "shan't",
    "shouldn",
    "shouldn't",
    "wasn",
    "wasn't",
    "weren",
    "weren't",
    "won",
    "won't",
    "wouldn",
    "wouldn't",
}

NULL_VALUES = {
    np.nan,
    float("NaN"),
    "#N/A",
    "#N/A N/A",
    "#NA",
    "-1.#IND",
    "-1.#QNAN",
    "-NaN",
    "-nan",
    "1.#IND",
    "1.#QNAN",
    "<NA>",
    "N/A",
    "NA",
    "NULL",
    "NaN",
    "n/a",
    "nan",
    "null",
    "",
    None,
}

REGEX_BRACKETS = {
    "angle": re.compile(r"(\<)[^<>]*(\>)"),
    "curly": re.compile(r"(\{)[^{}]*(\})"),
    "round": re.compile(r"(\()[^()]*(\))"),
    "square": re.compile(r"(\[)[^\[\]]*(\])"),
}
REGEX_DIGITS = re.compile(r"\d+")
REGEX_DIGITS_BLOCK = re.compile(r"\b\d+\b")
REGEX_HTML = re.compile(r"<[A-Za-z/][^>]*>|&(?:[a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});")
REGEX_PUNCTUATION = re.compile(rf"[{re.escape(string.punctuation)}]")
REGEX_URL = re.compile(r"(?:https?://|www\.)\S+")
REGEX_WHITESPACE = re.compile(r"[\n\t]|[ ]{2,}")

class DataFrameCleaner:
    def __init__(self, df, column, pipeline, stopwords):
        self.df = df
        self.column = column
        self.pipeline = pipeline
        self.stopwords = stopwords

    def _to_dask(self, df: Union[pd.DataFrame, dd.DataFrame]) -> dd.DataFrame:
        """Convert a dataframe to a dask dataframe."""
        if isinstance(df, dd.DataFrame):
            return df

        df_size = df.memory_usage(deep=True).sum()
        npartitions = math.ceil(df_size / 128 / 1024 / 1024)  # 128 MB partition size
        return dd.from_pandas(df, npartitions=npartitions)
    
    def clean_text(self,
        df: Union[pd.DataFrame, dd.DataFrame],
        column: str,
        pipeline: Optional[List[Dict[str, Any]]] = None,
        stopwords: Optional[Set[str]] = None,
    ) -> pd.DataFrame:
        """
        Clean text data in a DataFrame column.
        Read more in the :ref:`User Guide <clean_text_user_guide>`.
        Parameters
        ----------
            df
                A pandas or Dask DataFrame containing the data to be cleaned.
            column
                The name of the column containing text data.
            pipeline
                A list of cleaning functions to be applied to the column. If None,
                use the default pipeline. See the :ref:`User Guide <clean_text_custom_pipeline>`
                for more information on customizing the pipeline.
                (default: None)
            stopwords
                A set of words to be removed from the column. If None, use NLTK's
                stopwords.
                (default: None)
        Examples
        --------
        Clean a column of text data using the default pipeline.
        >>> df = pd.DataFrame({"text": ["This show was an amazing, fresh & innovative idea in the \
    70's when it first aired."]})
        >>> clean_text(df, 'text')
                                                    text
        0  show amazing fresh innovative idea first aired
        """
        df = self.to_dask(df)

        pipe = self._get_default_pipeline(stopwords) if not pipeline else self._get_custom_pipeline(pipeline)

        for func in pipe:
            df[column] = df[column].apply(func, meta=object)

        df = df.compute()

        return df

    def default_text_pipeline(self) -> List[Dict[str, Any]]:
        """
        Return a list of dictionaries representing the functions in the default pipeline.
        Use as a template for creating a custom pipeline.
        Read more in the :ref:`User Guide <clean_text_user_guide>`.
        Examples
        --------
        >>> default_text_pipeline()
        [{'operator': 'fillna'}, {'operator': 'lowercase'}, {'operator': 'remove_digits'},
        {'operator': 'remove_html'}, {'operator': 'remove_urls'}, {'operator': 'remove_punctuation'},
        {'operator': 'remove_accents'}, {'operator': 'remove_stopwords', 'parameters':
        {'stopwords': None}}, {'operator': 'remove_whitespace'}]
        """
        return [
            {"operator": "fillna"},
            {"operator": "lowercase"},
            {"operator": "remove_digits"},
            {"operator": "remove_html"},
            {"operator": "remove_urls"},
            {"operator": "remove_punctuation"},
            {"operator": "remove_accents"},
            {"operator": "remove_stopwords", "parameters": {"stopwords": None}},
            {"operator": "remove_whitespace"},
        ]

    def _get_default_pipeline(self,
        stopwords: Optional[Set[str]] = None,
    ) -> List[Callable[..., Any]]:
        """
        Return a list of functions defining the default pipeline.
        """
        return [
            self._fillna,
            self._lowercase,
            self._remove_digits,
            self._remove_html,
            self._remove_urls,
            self._remove_punctuation,
            self._remove_accents,
            lambda x: self._remove_stopwords(x, stopwords),
            self._remove_whitespace,
        ]

    def _get_custom_pipeline(self, pipeline: List[Dict[str, Any]]) -> List[Callable[..., Any]]:
        """
        Return a list of functions defining a custom pipeline.
        """
        func_dict = self._get_func_dict()
        custom_pipeline: List[Callable[..., Any]] = []

        for component in pipeline:
            # Check whether function is built in or user defined
            operator = (
                func_dict[component["operator"]]
                if isinstance(component["operator"], str)
                else component["operator"]
            )
            # Append the function to the pipeline
            # If parameters are specified, create a partial function to lock in
            # the values and prevent them from being overwritten in subsequent loops
            if "parameters" in component:
                custom_pipeline.append(self._wrapped_partial(operator, component["parameters"]))
            else:
                custom_pipeline.append(operator)

        return custom_pipeline

    def _get_func_dict(self) -> Dict[str, Callable[..., Any]]:
        """
        Return a mapping of strings to function names.
        """
        return {
            "fillna": self._fillna,
            "lowercase": self._lowercase,
            "sentence_case": self._sentence_case,
            "title_case": self._title_case,
            "uppercase": self._uppercase,
            "remove_accents": self._remove_accents,
            "remove_bracketed": self._remove_bracketed,
            "remove_digits": self._remove_digits,
            "remove_html": self._remove_html,
            "remove_prefixed": self._remove_prefixed,
            "remove_punctuation": self._remove_punctuation,
            "remove_stopwords": self._remove_stopwords,
            "remove_urls": self._remove_urls,
            "remove_whitespace": self._remove_whitespace,
            "replace_bracketed": self._replace_bracketed,
            "replace_digits": self._replace_digits,
            "replace_prefixed": self._replace_prefixed,
            "replace_punctuation": self._replace_punctuation,
            "replace_stopwords": self._replace_stopwords,
            "replace_text": self._replace_text,
            "replace_urls": self._replace_urls,
        }

    def _fillna(self,text: Any, value: Any = np.nan) -> Any:
        """
        Replace all null values with NaN (default) or the supplied value.
        """
        return value if text in NULL_VALUES else str(text)

    def _lowercase(self,text: Any) -> Any:
        """
        Convert all characters to lowercase.
        """
        return str(text).lower() if pd.notna(text) else text

    def _sentence_case(self,text: Any) -> Any:
        """
        Convert first character to uppercase and remaining to lowercase.
        """
        return str(text).capitalize() if pd.notna(text) else text

    def _title_case(self,text: Any) -> Any:
        """
        Convert first character of each word to uppercase and remaining to lowercase.
        """
        return str(text).title() if pd.notna(text) else text

    def _uppercase(self,text: Any) -> Any:
        """
        Convert all characters to uppercase.
        """
        return str(text).upper() if pd.notna(text) else text

    def _remove_accents(self,text: Any) -> Any:
        """
        Remove accents (diacritic marks).
        """
        return (
            normalize("NFD", str(text)).encode("ascii", "ignore").decode("ascii")
            if pd.notna(text)
            else text
        )

    def _remove_bracketed(self,text: Any, brackets: Union[str, Set[str]], inclusive: bool = True) -> Any:
        """
        Remove text between brackets.
        Parameters
        ----------
        brackets
            The bracket style.
                - "angle": <>
                - "curly": {}
                - "round": ()
                - "square": []
        inclusive
            If True (default), remove the brackets along with the text in between.
            Otherwise, keep the brackets.
        """
        if pd.isna(text):
            return text

        text = str(text)
        value = "" if inclusive else r"\g<1>\g<2>"
        if isinstance(brackets, set):
            for bracket in brackets:
                text = re.sub(REGEX_BRACKETS[bracket], value, text)
        else:
            text = re.sub(REGEX_BRACKETS[brackets], value, text)

        return text

    def _remove_digits(self,text: Any) -> Any:
        """
        Remove all digits.
        """
        return re.sub(REGEX_DIGITS, "", str(text)) if pd.notna(text) else text

    def _remove_html(self,text: Any) -> Any:
        """
        Remove HTML tags.
        """
        return re.sub(REGEX_HTML, "", str(text)) if pd.notna(text) else text

    def _remove_prefixed(self,text: Any, prefix: Union[str, Set[str]]) -> Any:
        """
        Remove substrings that start with the prefix(es).
        """
        if pd.isna(text):
            return text

        text = str(text)
        if isinstance(prefix, set):
            for pre in prefix:
                text = re.sub(rf"{pre}\S+", "", text)
        else:
            text = re.sub(rf"{prefix}\S+", "", text)

        return text

    def _remove_punctuation(self,text: Any) -> Any:
        """
        Remove punctuation marks.
        """
        return re.sub(REGEX_PUNCTUATION, " ", str(text)) if pd.notna(text) else text

    def _remove_stopwords(self,text: Any, stopwords: Optional[Set[str]] = None) -> Any:
        """
        Remove a set of words from the text.
        If `stopwords` is None (default), use NLTK's stopwords.
        """
        if pd.isna(text):
            return text

        stopwords = english_stopwords if not stopwords else stopwords
        return " ".join(word for word in str(text).split() if word.lower() not in stopwords)

    def _remove_urls(self,text: Any) -> Any:
        """
        Remove URLS.
        """
        return re.sub(REGEX_URL, "", str(text)) if pd.notna(text) else text

    def _remove_whitespace(self,text: Any) -> Any:
        """
        Remove extra spaces along with tabs and newlines.
        """
        return re.sub(REGEX_WHITESPACE, " ", str(text)).strip() if pd.notna(text) else text