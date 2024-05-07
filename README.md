# logochemy
 
 Simple byte-pair and multi-byte encoding.

`bpe_reduce` iteratively merges the most frequent tokens in the text provided as a list of tokens. E.g.
 ```python
from logochemy import bpe_reduce

text = list("per aspera")
bpe_reduce(text, niter=2)
 ```
performs the merge sequence
```
Input tokens:       10, vocabulary size = 6, n(c1) =      2, n(c2) =      2, n(c1, c2) =      2.
Replacing ('e', 'r')
Input tokens:        8, vocabulary size = 5, n(c1) =      2, n(c2) =      2, n(c1, c2) =      2.
Replacing ('p', 'er')
```
and outputs
```
['per', ' ', 'a', 's', 'per', 'a']
```

`mbe_reduce` is similar, but can merge multiple tokens in one go, e.g.
```python
from logochemy import mbe_reduce

text = list("per aspera ad astra")
mbe_reduce(text, nmax=4, niter=2)
```
merges
```
Input tokens:       19, f =  1.05e-01, k = 8, (n-1)*f*k*ln(k) =  3.502
Replacing [('p', 'e', 'r')]
Input tokens:       15, f =  1.33e-01, k = 7, (n-1)*f*k*ln(k) =  3.632
Replacing [(' ', 'a', 's')]
```
and outputs
```
['per', ' as', 'per', 'a', ' ', 'a', 'd', ' as', 't', 'r', 'a']
```