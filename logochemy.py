import re
from math import log, log2
from collections import Counter
from itertools import tee


def merge(splitting, tokens):
    """Merges sequences of tokens in the splitting of a text."""

    # Prepares an extended splitting.
    # ['abcd', 'de', 'f'] -> ['abcd', None, None, None, 'de', None, 'f']
    espl = extend_(splitting)

    text = ''.join(splitting)
    espl = merge_e(espl, (tokens,), text)

    return [x for x in filter(None, espl)]


def merge_e(espl, token_seqs, text):
    """Merges multiple non-overlapping sequences of tokens. For efficiency, 
    the function operates on extended splittings and additionally requires
    as a string the same text that was splitted.

    Args:
        espl: an extended splitting of the text.
        token_seqs: the sequences of tokens to be merged. 
        text: the full text as a string.

    Returns: a new extended splitting."""

    espl = espl.copy()  # Makes a copy of the input list, which will be modified
    n = len(espl)

    seq_strs =  [''.join(t) for t in token_seqs]
    for s in seq_strs:
        nc = len(s)  # The number of characters in the new token

        # Make a regular expression for matching the sequences to be merged.
        if len(set(s)) == nc:
            sre = re.compile(re.escape(s))
        else:
            # Look-ahead expressions are a little slower but work even 
            # in the presence of repeated characters in the tokens.
            sre = re.compile('(?=(' + re.escape(s) + '))') 

        for m in sre.finditer(text):
            start = m.start()
            end = start + nc
            if espl[start] and (end==n or espl[end]):  
                # The match corresponds to an existing pair of tokens
                espl[start] = text[start:end]
                for i in range(start+1, end):
                    espl[i] = None

    return espl


def count_n(it, n):
    """Counts overlapping n-element sequences from an iterator."""
    il = tee(it, n)
    for i, iter_i in enumerate(il):
        for _ in range(i):
            next(iter_i)
    return Counter(zip(*il))


def bpe_reduce(splitting: list, niter=1):
    """Byte-pair encoding.

    Args:
        niter: the number of iteration of token merging.
    
    Returns:
        A new splitting of the same text, output as a new list of tokens.
    """

    def mutual_information_kf(c):
        c1, c2 = c
        p1 = token_cnt1[c1] / token_n
        p2 = token_cnt1[c2] / token_n
        p21 = token_cnt2[(c1, c2)] / token_cnt1[c1]  # p(c2|c1)
        return mutual_information(p1, p2, p21)
    
    text = ''.join(splitting)
    espl = extend_(splitting)

    for _ in range(niter):

        token_n = len(espl) - espl.count(None)

        # Counts tokens and pairs
        token_cnt1 = Counter(filter(None, espl)) 
        token_cnt2 = count_n(filter(None, espl), 2)

        # Pair of tokens to merge
        rep = sorted(token_cnt2, key=mutual_information_kf)[-1]
        
        vs = len(token_cnt1)  # The vocabulary size
        print((f'Input tokens: {token_n:8}, vocabulary size = {vs}, '
               f'n(c1) = {token_cnt1[rep[0]]:6}, n(c2) = {token_cnt1[rep[1]]:6},' 
               f' n(c1, c2) = {token_cnt2[rep]:6}.'))
        print(f'Replacing {str(rep)}')

        espl = merge_e(espl, (rep,), text=text)

    return [x for x in filter(None, espl)]  # Returns a normal splitting


def mbe_reduce(splitting: list, nmax=2, niter=1, mpi=1):
    """Reduces the splitting of a text given as a list of string tokens 
    by merging the most frequent n-token sequences of the lenght at most nmax.
    mpi non-overlapping token sequences can be merged at a time.
    
    Byte-pair encoding (BPE) is realized by the default settings, nmax=2, mpi=1.

    Args:
        nmax: the maximum length of the sequence of tokens to be replaced 
            by a single token at a time.
        mpi: the number of merges per one iteration of frequency counting. More 
            merges per iteration make the encoding faster but less dense.
        niter: the number of iteration of token merging.
    
    Returns:
        A new splitting of the same text, output as a new list of tokens.
    """

    def kf(cnt: Counter):
        """ The key function used to sort the list of counters of repetitions 
        of n-token sequences according to the expected reduction in the 
        total number of tokens if the most frequent sequence of length n 
        is merged into one token."""

        t, n = cnt.most_common(1)[0]  # (token sequence, number of counts)
        return n * (len(t)-1)
    
    text = ''.join(splitting)
    espl = extend_(splitting)

    for _ in range(niter):
        token_cnts = [count_n(filter(None, espl), i) for i in range(2, nmax+1)]
        rep = []  # Sequences of tokens to merge
        affected_tok = []

        for i in range(mpi):
            max_cnt = max(token_cnts, key=kf)
            max_tok, max_count = max_cnt.most_common(1)[0]
            rep.append(max_tok)
            affected_tok.extend(max_tok)

            if i < mpi-1:
                # Sets the counts of sequences of tokens overlapping with the 
                # previously picked sequences to -1, thus precluding them from 
                # being picked in the next round. 
                # No need for this on the last step.
                for cnt in token_cnts:
                    for k in cnt:
                        if any(tok in k for tok in affected_tok):
                            cnt[k] = -1
        
        vs = len(Counter(filter(None, espl)))  # The vocabulary size
        l = len(espl) - espl.count(None)
        freq = max_count / l  # The frequency of the last merged combination
        
        # (n-1)*f*k*ln(k) > 1 should be fulfilled for the merge to be justified
        print(f'Input tokens: {l:8}, f = {freq : 0.2e}, k = {vs}, ' 
              f'(n-1)*f*k*ln(k) = {(len(max_tok)-1)*freq*vs*log(vs) : 0.3f}')

        print(f'Replacing {str(rep)}')

        espl = merge_e(espl, rep, text)

    return [x for x in filter(None, espl)]  # Returns a normal splitting


def mbe_reduce_from_log(splitting: list, file_name: str):
    """Takes an input splitting of a text and applies the token mergers 
    found by the reduce function and recorded in a log. 
    Logs consist of entries such as

    Input tokens:  2122217, f =  3.06e-05, k = 7746, (n-1)*f*k*ln(k) =  2.125
    Replacing [('f', 'am'), ('g', 'at')]
    """
    print(f'Initial tokens: {len(splitting):8}')

    text = ''.join(splitting)
    espl = extend_(splitting)

    with open(file_name, 'r') as f:
        for i, line in enumerate(f):
            if line.startswith('Replacing'):
                rep = eval(line[10:])
                espl = merge_e(espl, rep, text)
            
            if i % 200 == 0:
                print(f'Processing line {i}')

    new_splitting = [x for x in filter(None, espl)]
    print(f'Final tokens: {len(new_splitting):8}')
    return new_splitting


def xlog2(x, eps=1e-15):
    return x*log2(x) if x>eps else 0


def conditional_entropy(p1: float, p2: float, p21: float) -> float:
    """The conditional entropy of two events H(2|1). 

    Args:
        p1: the probability of event 1. 
        p2: the probability of event 2. 
        p21: the conditional probability of 2 given 1, p(2|1). 
    """
    
    p2n1 = (p2 - p21 * p1) / (1 - p1)  # p(2 | not 1)
    return - ((xlog2(p21) + xlog2(1 - p21)) * p1 
              + (xlog2(p2n1) + xlog2(1 - p2n1)) * (1-p1))


def mutual_information(p1: float, p2: float, p21: float) -> float:
    """ The mutual information of two events I(1,2) = H(2) - H(2|1). 

    Args:
        p1: the probability of event 1. 
        p2: the probability of event 2. 
        p21: the conditional probability of 2 given 1, p(2|1). 
    """

    p2n1 = (p2 - p21 * p1) / (1 - p1)  # p(2 | not 1)
    h2 = - xlog2(p2) - xlog2(1 - p2)  # H(2)
    h21 = - ((xlog2(p21) + xlog2(1 - p21)) * p1 
             + (xlog2(p2n1) + xlog2(1 - p2n1)) * (1-p1))  # H(2|1)
    return h2 - h21


def extend_(spl: list) -> list:
    """Augments the splitting of a text into tokens by empty entries such that 
    the length of the list matches the number of characters in the text.

    ['abcd', 'de', 'f'] -> ['abcd', None, None, None, 'de', None, 'f']
    """
    espl = []
    for t in spl:
        espl.extend([t] + [None]*(len(t)-1))
    return espl