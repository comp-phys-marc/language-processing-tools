# NLP Workspace

Each of these utilities allow a user to perform a particular
file / text processing action.

The tools allow a user to download and pre-process files using
Microsoft's entity extraction software, train and manage NLP models 
on those files, and programmatically compare file contents from any 
stage of the workflow.

## Example Usage

Note that the utilities can treat any file as either plain text or markup.

### Fetching Data

Download a file:

    python download.py -u https://www.file-source.com/file.xml -f file.xml
    
### Generate

Generate a new file based on some examples:

    generate.py -i example.txt,other.txt -s hello,hi -n greetings -p 1

### Preprocessing

Extract all cell numbers and home phone numbers from the file and save them to numbers.xml:

    python extract.py -s file.xml -f cell,home -t PhoneNumber,PhoneNumber -o numbers.xml

Search for a specific word in the file:

    python extract.py -s file.xml -f word -t any -o found.xml

Search for all dates in the file:

    python extract.py -s file.xml -f any -t DateTime -o found.xml

Search for emails in the content of a specific tag:

    python extract.py -s file.xml -f any -t Email -c tagname -o found.xml

Search for all dates in the file:

    python extract.py -s tests/test.xml -f any -t URL -o found.xml

### Encoding

Encode a set of files to a vector representation:

    python encode.py -n found -f found.xml -t XML -p 1

### Saving

Save a set of files in vector form to the cloud:

    python store.py -s found -k your-api-key -i found-index

### Comparing

Compare a local vector file to the 3 most common ones in the cloud:

    python store.py -c local -k your-api-key -i found-index -t 3

## Download

This command line utility enables a user to download files from the internet for use in the workspace.

    download.py -u <url> -f <filename>

    <url> is the url of the desired resource.

    <filename> is the name of the destination in the local filesystem.

## Extract

This command line utility enables a user to extract features (type, value) from unstructured text or structured
markup language like XML or HTML.

    extract.py -s <source> -c <context> -o <outfile> -f <features> -t <types> -p <proximity>

    <source> is the relative path to the input file from which to extract information.

    <context> is the tag name of the top-level element in an HTML or XML file that is included in the feature extraction.

    <outfile> is the JSON file to which the results should be written.

    <features> is the ordered, comma delimited list of feature names to extract.

    <types> is the ordered, comma delimited list of the features' types. These can include any of the following:

        PhoneNumber, Email, URL, Mention, Hashtag, IpAddress, Age, Currency, 
        Temperature, Dimension, Number, Ordinal, Percent, DateTime, Boolean

    <proximity> features and their values are associated by their proximity to one another in the source file. 
    You may override the default proximity, which assumes they will be found on the same line.

## Encode

This command line utility enables a user to encode and persist files as vector representations.

    encode.py -n <run_name> -f <files> -t <type> -d <directory> -s <seperator> -p <persist>

    <run_name> is a name that should uniquely name this execution.

    <files> is the comma seperated list of files to encode.
    
    <type> gives how the files will be treated (defaults to 'text'). Set as 'XML' or 'HTML' to 
    encode text by tag name indexes.
    
    <directory> is the location of the files.
    
    <seperator> is the seperator style used by the files.
    
    <persist> is whether the results should be persisted so that they can be used in subsequent operations,
    or just printed (defaults to true).

## Store

This command line utility enables a user perform transactions with the data store.

    store.py -c <compare> -s <save> -d <delete> -k <api_key> -i <index>

    <compare> is the name of a locally persisted result that you wish to compare to
    prior results which have been saved to the cloud.

    <save> is the name of a locally persisted result that you wish to save to the cloud.
    
    <delete> is the name of an index to delete.
    
    <top> is the number of top matches to return from a compare (defaults to 1).
    
    <api_key> is the api key you will use to authenticate with the cloud data store.
    
    <index> is the name of the index at which to to compare or save data.

## Generate

This command line utility enables a user to generate text files using an NLP generator
that may be trained on any other sets of text files.

    generate.py -i <input_files> -s <sentence_seeds> -n <name> -p <persist>

    <input_files> is the list of files to use to train the model.

    <sentence_seeds> is the list of sentence fragments to have the NLP complete.

    <name> is the name of the output file data.
    
    <persist> is whether the model should be saved.
    
## Notes

When building for the first time, you may need to ensure pinecone-client==0.8.59 is installed
last so as to avoid a breaking conflict with tensorflow's dependencies. If installed last, pip
will only issue a warning, and the workspace will function properly nonetheless.