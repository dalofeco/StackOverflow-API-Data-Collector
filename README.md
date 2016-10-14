# StackOverflow-API-Data-Collector
A python program that fetches question and answer data from the StackOverflow website, and delivers approved question and answer pairs that comply with your filter for further analysis.
## Usage:
Download and execute "stackoverflow.py" using python with no arguments. An interactive terminal window should show up.
  You can now, build your collection of StackOverflow API Questions!  
  
## Essential Commands:  
#### No Collection Loaded:  
  * B: Build New Questions Collection
  * L: Load Existing Questions Collection  

#### Collection Loaded:
  * RQ: Request Questions from API
  * RA: Request Answers for Questions from API
  * PN: Print Number of Questions
  * PS: Process Questions (delete unsatisfiable questions)
  * S: Save
  * XS: Save and Quit
  * X: Quit without Saving
  * A: Approve (goes through all answered questions that satisfy the score requirements, allowing user to approve or disapprove)
  * P: Print Approved Questions with Filter (asks for a keyword filter that checks question and answer for matches)
  
## Dependencies:
1. Pickle (for file saving)
2. Requests (python library for making HTTP requests)
3. LXML (HTML parsing library, used for legacy answer searching [without using API])
4. HTML2Text.py (Included): HTML parsing library by Aaron Swartz

## NOTES:
1. For now, only questions tagged with 'C++' and 'visual-studio' will be fetched by the program. To change this, modify the url in the 'stackoverflow.py' method requestQuestionsFromAPI(). 
2. Only one questions collection can be saved at once. Saving will overwrite the previous.
3. An API key is recommended to increase the number of questions and answers that can be fetched from the StackExchange server. To add your own, request a key from StackExchange and add it to the API_KEY global variable in 'stackoverflow.py'

## Future Changes:
1. Allow custom tag search (easy) [stackoverflow.py]
2. Allow API key input through user interaction (without modifying stackoverflow.py)
3. Add option to export all user-approved question and answer pairs to a JSON file (with filter)
