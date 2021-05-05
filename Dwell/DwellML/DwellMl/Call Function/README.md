# Call Functions

This folder contains the source to automatically run all Machine Learning models and ANN for Dwell Analytics when new data is coming in.

### What We Have in This Folder

This folder will contain a call_source.py which will be used as our final script as well as a prototype folder containing version updates (labeled "Call Function vX") for record purposes.
Each prototype folder will contain a copy of the required dataset, a copy of the original scripts containing the necessary functions as well as a call source and folders to print the results.

### Using This Folder for Testing

When testing with the prototype call functions it is highly recommended to save the version folder outside the "prometheus" folder due to directory issues. When saved locally, run "PL_main.py" to execute the call function flow. Once executed, look into the "Graphs" folder, this folder will contain anoter set of folders labeled by functions. In each folder will contain a graph of the function executed named under the timestamp at which the call function was executed.

**The ANN function in the early versions will take some time to exectue (about 10 minutes) but we are seeking to imporove this and others are more updates will be released**

## Version Updates
Below will contain updates on each verson release and the final version (both issues solved, new/existing issues and imporovements needed to be made)

### call_source.py
* Each version folder contains the necessary files within the same directory to run on a local machine. Here, the necessary files are contained in a different directory and when called is not recognized (05/05/2021)

### v1
* Solved: PL_main.py flows smoothly without any code errors
* Issue: Trying to call a function using "call_source.py" because they are contained in a differnet directory
* Improvement: Tune the ANN model to give at least the same accuracy with a shorter runtime
* Improvement: Cleanup and save the accuracies and other numberical statistics shown in the terminal to a seperate .txt file to make it easier to read and record
