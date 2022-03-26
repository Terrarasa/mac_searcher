Mac Searcher
=================

This is a CLI based tool to quickly search against the OUI database provided by IEEE. It's based on the library mac_vendor_lookup by Johann Bauer https://github.com/bauerj, but I've re-written it to download a cache file to desktop for offline queries and written it to not use async calls. 

## Install

Simply clone this repo into your desired location. The first run of the tool will require an internet connection to download the latest OUI database.

```git
git clone https://github.com/Terrarasa/mac_searcher.git
```

## Basic Usage

By passing a mac using the -m argument, you can search for a single mac address against the database.

```python
py mac_searcher.py -m 98:60:CA:22:2F:5F
98:60:CA:22:2F:5F : Apple, Inc.
```

You can also output a single search to a file using the -o argument

```python
py mac_searcher.py -m 98:60:CA:22:2F:5F -o out.txt
Output file out.txt written to successfully!
```

## CSV input/output

This tool can read and write csv files. Each MAC should be entered on a new row. The output will have each mac and vendor in separate columns on their own row

```python
py mac_searcher.py -i macs.csv --outfile out.csv
Output file out.csv written to successfully!
```

## Update the vendor list

The tool will download a copy of the vendor list on first run. This is stored in the same directory as the tool itself. To download a fresh copy of the database, run:

```python
py mac_searcher.py -u
```
