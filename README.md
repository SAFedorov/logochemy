# logochemy
 
Simple byte-pair and multi-byte encoding.

## Usage
Start from a text given as a list of tokens (single characters in the example below). Up to 10^6-10^7 tokens should be workable on a cpu.

 ```python
 text = list("there was also a beaver, that paced on the deck, or would sit making lace in the bow")

vocab = set(text)
print(f"Text length in tokens: {len(text)}")
print(f"Vocabulary size: {len(set(text))}")  # Number of unique tokens
 ```

 ```
Text length in tokens: 84
Vocabulary size: 22
 ```

Applying `bpe_reduce` will iteratively merge the most frequent tokens in the text. E.g. the following code
 ```python
from logochemy import bpe_reduce

text_ = bpe_reduce(text, niter=3)

assert "".join(text) == "".join(text_)
print("\n", text[:5], "->", text_[:4], "\n")
# The joined string is unchanged, but splitting into tokens is different. 

vocab_ = set(text_)
print(f"Output text length in tokens: {len(text_)}")
print(f"Output vocabulary size: {len(set(text_))}")
 ```
produces the output
```
Input tokens:       84, vocabulary size = 22, n(c1) =      9, n(c2) =     17, n(c1, c2) =      4.
Replacing ('e', ' ')
Input tokens:       80, vocabulary size = 23, n(c1) =      6, n(c2) =      4, n(c1, c2) =      4.
Replacing ('t', 'h')
Input tokens:       76, vocabulary size = 23, n(c1) =     13, n(c2) =      4, n(c1, c2) =      3.
Replacing (' ', 'th')

 ['t', 'h', 'e', 'r', 'e'] -> ['th', 'e', 'r', 'e '] 

Output text length in tokens: 73
Output vocabulary size: 24
```

`mbe_reduce` is similar, but can merge multiple tokens in one go, e.g.
```python
from logochemy import mbe_reduce

text_ = mbe_reduce(text, nmax=4, niter=2)

assert "".join(text) == "".join(text_)  
print("\n", text[:5], "->", text_[:3], "\n")

vocab_ = set(text_)
print(f"Output text length in tokens: {len(text_)}")
print(f"Output vocabulary size: {len(set(text_))}")
```
outputs
```
Input tokens:       84, f =  3.57e-02, k = 22, (n-1)*f*k*ln(k) =  4.857
Replacing [('t', 'h', 'e')]
Input tokens:       78, f =  2.56e-02, k = 23, (n-1)*f*k*ln(k) =  5.547
Replacing [('n', ' ', 'the', ' ')]

 ['t', 'h', 'e', 'r', 'e'] -> ['the', 'r', 'e'] 

Output text length in tokens: 72
Output vocabulary size: 24
```