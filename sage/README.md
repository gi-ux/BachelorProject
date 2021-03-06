# SAGE 

### Clear file

Before execute SAGE is strongly recommended cleaning the file of characters, mentions and links.

To do this, a scrip has been created that can take a dataframe and clean a specified field ("text" in our case).

The script will then create a .txt file in the "data" folder with a specified name. 

<pre><code> python text_wrapper.py "input_filename.csv" --output_file "output_filename" --col_name "column_name" --hashtags bool_value </code></pre>

### How to run

There are two ways of executing the script:

1) Generate a .csv file containing word,word_count to be used in the notebook:

<pre><code> python file_generator.py "filename" --outfilename "output_filename"</code></pre>

### Params for .csv generator

- **filename**: this specifies the file to generate output file
- **--outfilename**: this is the name of the output file

2) Run the SAGE script to get information about multiple files specified as input:

<pre><code> python print_info.py "filename" --max_vocab_size int_value --base_rate_smoothing=float_value --num_keywords=int_value </code></pre>

### Params for information printer

- **filename**: this specifies files to analyze
- **--max_vocab_size**: this indicates that SAGE will consider only the 1000 most frequent words, if value = 0 all words are considered
- **--base_rate_smoothing**: this smooths the baseline language model. Lower values will cause SAGE to emphasize more rare words; higher values will cause it emphasize more frequent words
- **--num_keywords**: this is the number of keywords to output