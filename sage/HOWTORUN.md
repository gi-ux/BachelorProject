# SAGE 

### How to run
Example:

<pre><code> python runSage.py "filename" --generate bool_value --filename "output_filename" --max_vocab_size int_value --base_rate_smoothing=float_value --num_keywords=int_value </code></pre>

### Params

- **filename**: this specifies a file glob to analyze.
- **--generate**: this is a flag that is False by default, if True a .csv will be written.
- **--filename**: this is the name of the file if the previous flag is True.
- **--max_vocab_size**: this indicates that SAGE will consider only the 1000 most frequent words, if value = 0 all words are considered
- **--base_rate_smoothing**: this smooths the baseline language model. Lower values will cause SAGE to emphasize more rare words; higher values will cause it emphasize more frequent words.
- **--num_keywords**: this is the number of keywords to output.