import numpy as np
import pandas as pd

def independent_column(size, num_choices, probs=None, rng=None):
    """ 
    Generate an 'independent' data column.

    size: length of the Series
    num_choices: number of different choices
    probs: probability of each choice, if None then uniform
    """
    if rng is None:
        rng = np.random.default_rng()
    
    return pd.Series(rng.choice(num_choices, size=size, replace=True, p=probs))


def add_columns(cols, mod=None):
    """
    Add two columns, possibly taking a module operator to make sure that the
    dependency only goes in one direction

    cols: list of columns
    mod: if None no modulo operator is applied, otherwise modulo operator is applied
    """
    result = cols[0].copy()
    for col in cols[1:]:
        result += col
    
    if mod is not None:
        result %= mod

    return result

def invert_column(col):
    """
    Invert a column
    """
    max_value = max(col)
    return max_value - col

def add_noise(col, error_prob):
    """
    Add noise to a column by selecting a random other value from the column 
    with probability error_prob
    """
    rng = np.random.default_rng()
    values = col.unique()
    indices_to_change = (rng.uniform(size=col.shape[0]) < error_prob).nonzero()
    new_data = col.values.copy()
    for index in np.nditer(indices_to_change):    
        old_data = new_data[index]
        new_elem = rng.choice(values)
        while new_elem == old_data:
            new_elem = rng.choice(values)
        new_data[index] = new_elem

    return pd.Series(new_data)


    return new_data
    



# Some specific configurations below
def conf1(rng=None):
    SIZE = 100
    NUM_CHOICES = 3
    a = independent_column(SIZE, NUM_CHOICES, rng=rng)
    b = independent_column(SIZE, 2*NUM_CHOICES, rng=rng)
    c = add_columns([a, b])

    df = pd.DataFrame()
    df['a'] = a
    df['b'] = b
    df['c'] = c
    return df


def conf2(rng=None):
    SIZE = 100
    NUM_CHOICES = 3
    a = independent_column(SIZE, NUM_CHOICES, rng=rng)
    b = independent_column(SIZE, 2*NUM_CHOICES, rng=rng)
    c = add_columns([a, b])
    d = add_columns([a, b], mod=2)
    e = invert_column(c)

    df = pd.DataFrame()
    df['a'] = a
    df['b'] = b
    df['c'] = c
    df['d'] = d
    df['e'] = e

    return df

def conf3(rng=None):
    SIZE = 1000
    NUM_CHOICES = 3
    a = independent_column(SIZE, NUM_CHOICES, rng=rng)
    b = independent_column(SIZE, 2*NUM_CHOICES, rng=rng)
    c = add_columns([a, b])
    d = add_columns([a, b], mod=2)
    e = invert_column(c)

    df = pd.DataFrame()
    df['a'] = a
    df['b'] = b
    df['c'] = c
    df['d'] = d
    df['e'] = e

    return df

def conf4(rng=None):
    SIZE = 1000
    NUM_CHOICES = 3
    a = independent_column(SIZE, NUM_CHOICES, rng=rng)
    b = independent_column(SIZE, 2*NUM_CHOICES, rng=rng)
    c = add_columns([a, b])
    d = add_columns([a, b], mod=2)
    e = invert_column(c)

    df = pd.DataFrame()
    df['a'] = a
    df['b'] = b
    df['c'] = c
    df['d'] = d
    df['e'] = e

    # Add 1 percent noise to column c
    df['c'] = add_noise(df['c'], error_prob=0.01)

    return df

def conf5(rng=None):
    SIZE=100
    NUM_CHOICES = 5
    a = independent_column(SIZE, NUM_CHOICES, rng=rng)
    b = independent_column(SIZE, 2, probs=[0.95,0.05], rng=rng)
    c = add_columns([a, b])

    df = pd.DataFrame()
    df['a'] = a
    df['b'] = b
    df['c'] = c

    return df

def conf6(rng=None):
    SIZE = 1000
    NUM_CHOICES = 3
    a = independent_column(SIZE, NUM_CHOICES, rng=rng)
    b = independent_column(SIZE, 2*NUM_CHOICES, rng=rng)
    c = add_columns([a, b])
    d = add_columns([a, b], mod=2)
    e = invert_column(c)

    df = pd.DataFrame()
    df['a'] = a
    df['b'] = b
    df['c'] = c
    df['d'] = d
    df['e'] = e

    # Add 1 percent noise to column c
    df['c'] = add_noise(df['c'], error_prob=0.01)
    df['d'] = add_noise(df['d'], error_prob=0.01)

    return df


def conf7(rng=None):
    SIZE = 2000
    NUM_CHOICES = 20
    a = independent_column(SIZE, NUM_CHOICES, rng=rng)
    b = independent_column(SIZE, 2*NUM_CHOICES, rng=rng)
    c = add_columns([a, b])
    d = add_columns([a, b], mod=2)
    e = invert_column(c)

    df = pd.DataFrame()
    df['a'] = a
    df['b'] = b
    df['c'] = c
    df['d'] = d
    df['e'] = e

    # Add 1 percent noise to column c and d
    df['c'] = add_noise(df['c'], error_prob=0.01)
    df['d'] = add_noise(df['d'], error_prob=0.01)

    return df

def conf8(rng=None):
    SIZE = 1000
    NUM_CHOICES = 10
    a = independent_column(SIZE, NUM_CHOICES, rng=rng)
    b = independent_column(SIZE, 2, probs=[0.95,0.05], rng=rng)
    c = add_columns([a, b])
    d = add_columns([a, b], mod=2)
    e = invert_column(c)

    df = pd.DataFrame()
    df['a'] = a
    df['b'] = b
    df['c'] = c
    df['d'] = d
    df['e'] = e

    # Add 1 percent noise to column c and d
    df['c'] = add_noise(df['c'], error_prob=0.01)
    df['d'] = add_noise(df['d'], error_prob=0.01)

    return df





if __name__ == "__main__":
    rng = np.random.default_rng(seed=42)
    """     df = conf1(rng)
    df.to_csv("./data/abc.100.clean.csv", index=False)

    df = conf2(rng)
    df.to_csv("./data/abcde.100.clean.csv", index=False)

    df = conf3(rng)
    df.to_csv("./data/abcde.1000.clean.csv", index=False)

    # Add 5 random columns to the dataframe
    df['f'] = independent_column(1000, 10, rng=rng)
    df['g'] = independent_column(1000, 10, rng=rng)
    df['h'] = independent_column(1000, 10, rng=rng)
    df['i'] = independent_column(1000, 10, rng=rng)
    df['j'] = independent_column(1000, 10, rng=rng)

    df.to_csv("./data/abcde.1000.clean.5randomcolumns.csv", index=False)


    df = conf4(rng)
    df.to_csv("./data/abcde.1000.dirty1percent.csv", index=False)

    # Add 5 random columns to the dataframe
    df['f'] = independent_column(1000, 10, rng=rng)
    df['g'] = independent_column(1000, 10, rng=rng)
    df['h'] = independent_column(1000, 10, rng=rng)
    df['i'] = independent_column(1000, 10, rng=rng)
    df['j'] = independent_column(1000, 10, rng=rng)

    df.to_csv("./data/abcde.1000.dirty1percent.5randomcolumns.csv", index=False) """


    #df = conf5(rng)

    #df.to_csv("./data/abc.1000.clean.almostatoc.csv", index=False)

    #df = conf6(rng)
    #df.to_csv("./data/abcde.1000.dirty1percent.candd.csv", index=False)

    df = conf8(rng)
    df['f'] = independent_column(1000, 10, rng=rng)
    df['g'] = independent_column(1000, 10, rng=rng)
    df['h'] = independent_column(1000, 10, rng=rng)

    df.to_csv("./data/abcde.1000.dirty1percent_cd.almostatic_b.3randomcolumns.csv", index=False)





   
