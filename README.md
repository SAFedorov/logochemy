# logochemy
 
 Simple byte-pair and multi-byte encoding.

`bpe_reduce` iteratively merges the most frequent tokens in the text provided as a list of tokens. E.g.
 ```python
from logochemy import bpe_reduce

text = list("per aspera ad astra")
bpe_reduce(text, niter=4)
 ```
produces the merge log
```
Input tokens:       19, vocabulary size = 8, n(c1) =      3, n(c2) =      5, n(c1, c2) =      3.
Replacing (' ', 'a')
Input tokens:       16, vocabulary size = 8, n(c1) =      3, n(c2) =      2, n(c1, c2) =      2.
Replacing ('r', 'a')
Input tokens:       14, vocabulary size = 8, n(c1) =      3, n(c2) =      2, n(c1, c2) =      2.
Replacing (' a', 's')
Input tokens:       12, vocabulary size = 8, n(c1) =      2, n(c2) =      2, n(c1, c2) =      2.
Replacing ('p', 'e')
```
and outputs
```
['pe', 'r', ' as', 'pe', 'ra', ' a', 'd', ' as', 't', 'ra']
```

`mbe_reduce` is similar, but can merge multiple tokens in one go, e.g.
```python
from logochemy import mbe_reduce

text = list("per aspera ad astra")
mbe_reduce(text, nmax=6, niter=2)
```
merges
```
Input tokens:       19, f =  5.26e-02, k = 8, (n-1)*f*k*ln(k) =  4.378
Replacing [('p', 'e', 'r', ' ', 'a', 's')]
Input tokens:       14, f =  7.14e-02, k = 9, (n-1)*f*k*ln(k) =  7.063
Replacing [('per as', 'p', 'e', 'r', 'a', ' ')]
```
and outputs
```
['per aspera ', 'a', 'd', ' ', 'a', 's', 't', 'r', 'a']
```