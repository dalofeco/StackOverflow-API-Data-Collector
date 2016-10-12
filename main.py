from stackoverflow import StackOverflow
from QuestionsCollection import QuestionsCollection
from Question import Question
import pickle

DEFAULT_FILE_NAME = 'questionsCollection'
AUTO_LOAD = False

collection = QuestionsCollection()

if AUTO_LOAD:
	# Load questions and answers from file
	collection.loadFromFile('QA')
	# Process the questions (only take eligible ones and build id array and a bunch of other stuff)
	collection.processQuestions()

# User Input Interactive Loop
userInput = 'z'
while userInput != 'X' and userInput != 'XS':
	# Show more options
	if userInput == 'M':
		print "More Options:\n\tDU: Delete Unsatisfiable Questions\n\tDFP: Delete Failed Parse\n\tUID: Get Unanswered Question IDS\n\tPN: Print Number of Questions\n\t"
	else:
		print "Options:\n\tL: Load Questions\n\tS: Save Questions\n\tXS: Save and Quit\n\tX: Quit without Saving\n\tRQ: Request Questions from API\n\tRA: Requests Answers for Questions from API\n\tPA: Parse Answers\n\tA: Approve Questions\n\tP: Print Approved With Filter\n\tM: Show More Options"
	
	userInput = raw_input('What do you want to do? ').upper()

	if userInput == 'L':
		# Load questions and answers from file
		collection = QuestionsCollection.load(DEFAULT_FILE_NAME)
		print 'Loaded!'

	elif userInput == 'LL':
		#Legacy Load:
		collection = QuestionsCollection()
		collection.loadFromFile('QA2')
		print 'Legacy Loaded!'

	elif userInput == 'LS':
		#Legacy Save:
		collection.saveToFile('QA2')
		print 'Legacy Saved!'

	if userInput == 'RQ': 
		START_PAGE = collection.next_page_to_fetch
		starting = raw_input('Starting at page ' + str(START_PAGE) + '? or start at page: ')
		if starting != '':
			try:
				START_PAGE = int(starting)
				print 'Starting at: ' + str(START_PAGE)
			except:
				START_PAGE = collection.next_page_to_fetch
		NUM_OF_PAGES = int(input("How many pages would you like to fetch? : "))
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

			except:
				print "Error fetching questions. API is probably be blocking your IP from excessive requests."
			finally:
				# Process the questions (only take eligible ones and build id array and a bunch of other stuff)
				collection.processQuestions()
		else:
			collection.next_page_to_fetch = START_PAGE
			


	elif userInput == 'RA':
		try:
			# Fetch the answers
			so = StackOverflow()
			so.fetchAnswersForQuestionsCollection(collection)
		except Exception as e:
			print e
			print "Error fetching answers. There are no answers to fetch?"

	elif userInput == 'PA':
		collection.parseAnswers()
		print 'Answers parsed! Use \'DFP\' to delete failed parses. (not recommended if HTML encoding on answers doesn\'t matter)'

	elif userInput == 'DFP':
		collection.deleteFailedParse()

	elif userInput == 'A':
		collection.verifyAllQuestions()
		print 'Done verifying questions!'
	
	elif userInput == 'P':
		collection.printApprovedQuestionsWithFilter(raw_input("Please input a filter (a tag/keyword)(or nothing to print all): "))

	elif userInput == 'PN': 
		collection.printNumOfQuestions()

	elif userInput == 'XS' or userInput == 'S':
		collection.save(DEFAULT_FILE_NAME)
		print 'Saved!'

	elif userInput == 'DU':
		numberDeleted = collection.deleteUnsatisfiableQuestions()
		print 'Deleted ' + str(numberDeleted) + ' unsatisfiable questions!'

	elif userInput == 'UID':
		# unanswered ids
		count = 0
		ids = collection.getUnansweredQuestionIDs()
		for i in ids:
			print i
			count += 1

		print 'Length: ' + str(count)




