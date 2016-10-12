# so = stackexchange.Site(stackexchange.StackOverflow, 'j6XYWgnl9uQbzCtYHyoACA((')
# content = urllib2.urlopen()
import pickle
import requests
from Question import Question
from QuestionsCollection import QuestionsCollection

class StackOverflow:
	def requestQuestionsFromAPI(self, startPage, numOfPages):
		# Requests questions from the API 100 at a time
		# Input: startPage, int for inital page, and endPage, int for the number of pages
		# Output: An array with JSON objects for question items (as recieved from api.stackexchange.com)

		# strings representing variables in request URL
		PG_NUM = "<PG_NUM>"
		questionsJSONar = []

		url = "http://api.stackexchange.com/2.2/questions?page=<PG_NUM>&pagesize=100&fromdate=1159574400&todate=1483056000&order=desc&sort=activity&tagged=c%2B%2B&site=stackoverflow&filter=!9YdnSIN18"
		for index in range(startPage, numOfPages+startPage):
			url1 = url.replace(PG_NUM, str(index))
			response = requests.get(url1)
			questionsJSONar.append(response.json())
			try:
				questions = []
				for questionJSON in questionsJSONar:
					if questionJSON is not None:
						questions += questionJSON['items']
			except: 
				print "Can't fetch questions..." + 'Page Number: ' + str(index)
				return questions

		return questions

	def fetchAnswersForQuestionsCollection(self, questionsCollection):
		# Fetches answers for Question objects passed in 
		# Input: List with Question IDs
		# Output: Array with JSON objects for answer items (key) (as recieved from api.stackexchange.com)
		IDS = "<IDS>"
		responsesAr = []
		baseURL =	"https://api.stackexchange.com/2.2/questions/<IDS>/answers?fromdate=1159660800&order=desc&sort=activity&site=stackoverflow&filter=!9YdnSMKKT"
		idStrings = []
		questionIDs = questionsCollection.getUnansweredQuestionIDs()
		numOfQuestions = len(questionIDs)
		idIndex = 0

	# Keep track of the current question being checked
		questionsIndex = 0;

		restQuestionsNum = numOfQuestions%100

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

			idIndex = hundredsQuestionNum


		# Add the first one manually
		idStrings.append('')
		idStrings[idIndex] += str(questionIDs[questionsIndex])	
		questionsIndex +=1

		# And loop through the rest
		for i in range(1, restQuestionsNum):
			idStrings[idIndex] += ';' + str(questionIDs[questionsIndex])
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

		SCORE_MIN = 20

		numRecieved = len(responses)
		numApproved = 0

		for answer in responses:
			index = questionsCollection.question_id_index[str(answer['question_id'])]

			if answer['is_accepted'] and answer['score'] >= SCORE_MIN:
				questionsCollection.questions[index].answer = answer['body'].encode('UTF-8')
				questionsCollection.questions[index].answer_score = answer['score']
				questionsCollection.questions[index].answerFetched = True
				numApproved+=1
			else:
				questionsCollection.questions[index].answerUnsatisfiable = True
				# questionsCollection.removeQuestionByID(answer['question_id'])

		# Process the questions (only take eligible ones and build id array and a bunch of other stuff)
		questionsCollection.processQuestions()

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






