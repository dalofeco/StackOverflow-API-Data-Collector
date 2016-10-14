import pickle
import requests
from Question import Question
from QuestionsCollection import QuestionsCollection

API_KEY = ""

class StackOverflow:
	def requestQuestionsFromAPI(self, startPage, numOfPages):
		# Requests questions from the API 100 at a time
		# Input: startPage, int for inital page, and endPage, int for the number of pages
		# Output: An array with JSON objects for question items (as recieved from api.stackexchange.com)

		# strings representing variables in request URL
		PG_NUM = "<PG_NUM>"
		KEY_PARAM = "&key="
		KEY = "<KEY>"
		questionsJSONar = []
		questions = []
		baseurl = "http://api.stackexchange.com/2.2/questions?page=<PG_NUM>&pagesize=100&fromdate=1159574400&todate=1483056000&order=desc&sort=activity&tagged=c%2B%2B;visual-studio&site=stackoverflow&key=<KEY>&filter=!9YdnSIN18"
		
		# ADD API KEY to URL only if key provided, else remove argument from URL
		if API_KEY == "":
			url = baseurl.replace(KEY,'')
			url = url.replace(KEY_PARAM, '')
		else:
			url = baseurl.replace(KEY, API_KEY)

		# Make requests for each page relevant
		for index in range(startPage, numOfPages+startPage):
			url1 = url.replace(PG_NUM, str(index))
			response = requests.get(url1)
			questionsJSONar.append(response.json())
			for questionJSON in questionsJSONar:
				if questionJSON is not None:
					try:
						questions += questionJSON['items']
					except:
						print "Could not fetch questions: API requests limit exceeded"

		return questions

	def fetchAnswersForQuestionsCollection(self, questionsCollection):
		# Fetches answers for Question objects passed in 
		# Input: List with Question IDs
		# Output: Array with JSON objects for answer items (key) (as recieved from api.stackexchange.com)
		IDS = "<IDS>"
		KEY = "<KEY>"
		KEY_PARAM = "&key="
		responsesAr = []
		url = "https://api.stackexchange.com/2.2/answers/<IDS>?fromdate=1159660800&order=desc&sort=activity&site=stackoverflow&key=<KEY>&filter=!9YdnSMKKT"
		questionIDs = questionsCollection.getUnfetchedAnswerIDs()
		numOfQuestions = len(questionIDs)

		# ADD API KEY to URL only if key provided, else remove argument from URL
		if API_KEY == "":
			baseURL = url.replace(KEY,'')
			baseURL = baseURL.replace(KEY_PARAM, '')
		else:
			baseURL = url.replace(KEY, API_KEY)

		# Keep track of the current url id strings array id
		idStringsIndex = 0
		idStrings = []

		# Keep track of the current question id being checked
		questionsIndex = 0;

		restQuestionsNum = numOfQuestions%100

		# Build id strings for all exact groups of 100 if there are more than 100
		if numOfQuestions > 100:
			hundredsQuestionNum = numOfQuestions/100

			# For each hundred elements, make an id string (API has MAX of 100 elements per request)
			for idIndex in range(0, hundredsQuestionNum):
				# Put int the first id onto the id string
				idStrings.append('')
				idStrings[idIndex] += str(questionIDs[questionsIndex])
				questionsIndex+=1

				#Then loop through the 99 others
				for i in range(1, 100):
					idStrings[idIndex] += ';' + str(questionIDs[questionsIndex])
					questionsIndex+=1

			# Move tracker index variable on to next id string
			idStringsIndex = len(idStrings)

		# Add the first one manually
		idStrings.append('')
		idStrings[idStringsIndex] += str(questionIDs[questionsIndex])	
		questionsIndex +=1

		# And loop through the rest
		for i in range(1, restQuestionsNum):
			idStrings[idStringsIndex] += ';' + str(questionIDs[questionsIndex])
			questionsIndex+=1

		urls = [baseURL] * len(idStrings)	# add a baseURL to request for every id string built
		
		## Requests warning if greater than 10. Since no API key is being used, huge requests can lead to IP blocking.
		if len(urls) > 10: 
			print "Warning, requests exceed 10, are you sure you want to proceed?\nThere are " + str(len(urls)) + "requests.  (Y or N?)"
			userInput = raw_input("Proceed? (Y/N): ")

			# If user does not want to proceed, return None
			if (userInput.upper() != 'Y'):
				return None
			# else: continue

		# build urls with idStrings ### IDS = "<IDS>", a custom tag in baseURL, make requests, and store in array
		index = 0
		for url in urls:
			url1 = url.replace(IDS, idStrings[index])
			response = requests.get(url1)
			responseJSON = response.json()
			responsesAr.append(responseJSON)

			index += 1

		responses = []
		for response in responsesAr:
			if response is not None:
				try:
					responses += response['items'] ## APPEND ALL RESPONSE ITEMS TO A HUGE LIST
				except KeyError:
					print "Error: Couldn't retrieve items API Limit Exceeded."
					return


		numRecieved = len(responses)
		numApproved = questionsCollection.addAnswersJSON(responses)

		print 'Recieved: ' + str(numRecieved) + ' answers.'
		print 'Approved: ' + str(numApproved) + ' answers.'

	## ENDEF fetchAnswersForQuestionsCollection(self, questionsCollection)

	# def parseResponseUnicode(self, response):
	# # HTML Character sequences common in responses, to be further replace with the values below.
	#   quote = '&quot;'
	#   lessthan = "&lt;"
	#   lessthanorequal = "&lt;="
	#   greaterthan = "&gt;"
	#   greaterthanorequal = "&gt;="
	#   singlequote = "&#39;"
	#   amp = "&amp;"
	#   specialChars = [quote, lessthan, lessthanorequal, greaterthan, greaterthanorequal, singlequote, amp]
	#   specialCharsValues = ['"', "<", "<=", ">", ">=", "'", "&"]

	#   # Replace any common HTML characters with the actual character value
	#   index = 0;
	#   for specialChar in specialChars:
	#     if specialChar in response:
	#       response = response.replace(specialChar, specialCharsValues[index])
	#     index = index + 1

	#   return response

## END OF CLASS DECLARATION

# REAL EXECTUION

DEFAULT_FILE_NAME = 'questionsCollection'
AUTO_LOAD = False
COLLECTION_LOADED = False

collection = QuestionsCollection()

if AUTO_LOAD:
	print 'Auto loading...'
	# Load questions and answers from file
	collection.loadFromFile('QA')
	# Process the questions (only take eligible ones and build id array and a bunch of other stuff)
	collection.processQuestions()
	COLLECTION_LOADED = True

# User Input Interactive Loop
userInput = 'z'
while userInput != 'X' and userInput != 'XS':

	# If collection is loaded, show relevant functionality, else, allow user to create or load
	if COLLECTION_LOADED:
		# Show more options
		if userInput == 'M':
			print "More Options:\n\tDFP: Delete Failed Parse\n\tPA: Parse Answers\n\tUID: Get Unanswered Question IDS\n\tPN: Print Number of Questions\n\tPQ: Process Questions\n"
		# Print standard options message
		else:
			print "Options:\n\tL: Load Questions\n\tS: Save Questions\n\tX: Quit without Saving\n\tXS: Save and Quit\n\tRQ: Request Questions from API\n\tRA: Requests Answers for Questions from API\n\tA: Approve Questions\n\tP: Print Approved With Filter\n\tM: Show More Options"
		
		# Get user input
		userInput = raw_input('What do you want to do? ').upper()

		# Load from file
		if userInput == 'L':
			# Load questions and answers from file
			collection = collection.load(DEFAULT_FILE_NAME)
			print 'Loaded!'
			print collection.questions

		# Request Questions from API
		if userInput == 'RQ': 
			START_PAGE = collection.next_page_to_fetch
			starting = raw_input('Starting at page ' + str(START_PAGE) + '? or start at page: ')
			if starting != '':
				try:
					START_PAGE = int(starting)
					print 'Starting at: ' + str(START_PAGE)
				except:
					START_PAGE = collection.next_page_to_fetch
			try:
				NUM_OF_PAGES = int(input("How many pages would you like to fetch? (default 10): "))
			except:
				print 'Assuming default of 10 pages.'
				NUM_OF_PAGES = 10
			print 'Fetching ' + str(NUM_OF_PAGES) + ' pages.'
			if NUM_OF_PAGES != 0:
				try:
					# Request questions
					so = StackOverflow()
					questions_JSON_list = so.requestQuestionsFromAPI(START_PAGE, NUM_OF_PAGES)
				
					# Add new questions to the collection
					collection.addQuestionsJSON(questions_JSON_list)
					# Update next page to fetch for next fetching time
					collection.next_page_to_fetch = START_PAGE + NUM_OF_PAGES
					print "Successfully requested " + str(NUM_OF_PAGES * 100) + " questions!"

				except Exception as e:
					print "Error fetching questions. API is probably be blocking your IP from excessive requests."
					print e
				finally:
					# Process the questions (only take eligible ones and build id array and a bunch of other stuff)
					collection.processQuestions()
			else:
				collection.next_page_to_fetch = START_PAGE
				

		# Request Answers from API
		elif userInput == 'RA':
			try:
				# Fetch the answers
				so = StackOverflow()
				so.fetchAnswersForQuestionsCollection(collection)
			except Exception as e:
				print e
				print "Error fetching answers. There are no answers to fetch?"

		# Parse all unparsed answers
		elif userInput == 'PA':
			collection.parseAnswers()
			print 'Answers parsed! Use \'DFP\' to delete failed parses. (not recommended if HTML encoding on answers doesn\'t matter)'

		# Delete all questions whose answer failed to parse
		elif userInput == 'DFP':
			collection.deleteFailedParse()

		# Start user validation of questions
		elif userInput == 'A':
			collection.verifyAllQuestions()
			print 'Done verifying questions!'
		
		# Print questions with filter
		elif userInput == 'P':
			collection.printApprovedQuestionsWithFilter(raw_input("Please input a filter (a tag/keyword)(or nothing to print all): "))

		# Print number of questions
		elif userInput == 'PN': 
			collection.printNumOfQuestions()

		# Save to file
		elif userInput == 'XS' or userInput == 'S':
			collection.save(DEFAULT_FILE_NAME)
			print 'Saved!'

		# Process Questions
		elif userInput == 'PQ':
			collection.processQuestions()

		# Print unanswered question ids
		elif userInput == 'UID':
			# unanswered ids
			count = 0
			ids = collection.getUnansweredQuestionIDs()
			for i in ids:
				print i
				count += 1

			print 'Length: ' + str(count)

		elif userInput != 'X':
			print 'Could not understand your input, try again...'
	
	# NO COLLECTION LOADED
	else: 
		print "Options:\n\tB: Build New Collection\n\tL: Load Questions Collection\n\tX: Quit\n"
		
		# Get user input
		userInput = raw_input('>> ').upper()
		# Load from file
		if userInput == 'L':
			# Load questions and answers from file
			collection = collection.load(DEFAULT_FILE_NAME)
			print 'Loaded!'
			COLLECTION_LOADED = True

		elif userInput == 'B':
			collection = QuestionsCollection()

			# Get user preference on parsing HTML responses
			userPreference = 'X'
			try:
				userPreference = raw_input('Would you like to parse html responses? (Y/n): ').upper()
			except:
				print "Assuming default input of Y"
			finally:
				if userPreference != 'N':
					collection.htmlparse = True

			scoreMin = 20
			try:
				scoreMinStr = raw_input('What is the minimum accepted question & answer scores? (default: 20)')
				if scoreMinStr == '':
					scoreMin = 20
				else:
					scoreMin = int(scoreMinStr)
			except:
				print 'Assuming default minimum of 20'
			collection.SCORE_MIN = scoreMin

			COLLECTION_LOADED = True




