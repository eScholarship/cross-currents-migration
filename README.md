# Cross-Currents eJournal Migration

A simple Python script to migrate a CSV data dump from the current Drupal-based Cross-Currents electronic journal to CDL eScholarship batch ingest format.

## Installation

It's just a Python 3 script, but it has a few dependencies, which you can install with:

`pip install -r ./requirements.txt`

There is also a small utility script, which I found on a StackOverflow page `addbom.sh` which requires the `uconv` script
to be installed, you can do this on a Mac by running `brew install icu4c`. The uconv script is included in icu4c, however,
you may have to add the script to your path. I was lazy and just symlinked it to ~/bin/uconv. You can find the actual command
path with `brew list icu4c | grep uconv`

## Usage

To generate a new tsv file using the migrate.py script, run:

`python ./migrate.py > crosscurrents_test_batch_20200602.tsv && addbom.sh crosscurrents_test_batch_20200602.tsv`

Then open the .tsv file using Excel (tell the import "wizard" it's a tab-delimited file, with no qualifiers), and then review the output.
If it looks good enough, save it as a .xlsx file, and you're ready to load it into Subi.

## Contributing

1. Fork it!
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request :D

## License
[BSD 3-clause](LICENSE.md)