import pickle
import requests
from Question import Question
from lxml import html

class QuestionsCollection:
# 	'Class that contains questions along with their answers, and saves them locally.'

	questions = {}  # Stores question id (key) pointing to question objects
	next_page_to_fetch = 1
	size = 0
	htmlparse = True 		   # Set to True if you want to parse answer HTMLs (may hide some links, but provides clearer text)
	SCORE_MIN = 20				 # Minimum score allowed for questions and answers
	tags = [] 				# List that holds tags related to the collection (to search on stackoverflow)	

	# Add a single JSON question object
	def addQuestionJSON(self, questionJSON):
	# // Add a question through it's JSON object representation 
	# // Input: JSON object
		# Create a question object from JSON
		question = Question()
		question.createQuestionFromJSON(questionJSON)

		# Add to question to question id dictionary and update size
		self.questions[str(question.question_id)] = question
		self.size += 1


	def addQuestionsJSON(self, questionsJSON):
	# Add an array of JSON question objects
	# IN: questionsJSON is an array of JSON question objects, as recieved from StackExchange API
		for questionJSON in questionsJSON:
			self.addQuestionJSON(questionJSON) 

	# Add a single question object
	def addQuestion(self, question):
		# Directly add question (trusted)
		if type(question) is Question:
			self.questions[str(question.question_id)] = question 	# add to dict
			self.size += 1 										  # update collection size

	# Add an array of question objects
	def addQuestions(self, questions):
		for qid, question in questions.iteritems():
			self.addQuestion(question);

	def addAnswersJSON(self, answersJSON):
	# answersJSON is an array of JSON answer objects, as recieved from StackExchange API
		# Keep track of number of 'approved' questions
		numApproved = 0

		for answer in answersJSON:
		# If return value is True, means answer was approved
			if self.questions[str(answer['question_id'])].addAnswerFromJSON(answer, self.SCORE_MIN):	# Add JSON data to question object
			#   [ 				QUESTION OBJECT 							] -> (add answer function from answer with minimum score of: )
				
				numApproved+= 1

		# Process the questions (only take eligible ones, build id array, delete unsatisfiable, and a bunch of other stuff)
		self.processQuestions()

		return numApproved

  # Print questions info (title and score)
	def printQuestions(self):
		for qid, question in self.questions.iteritems():
			print question.title + ' ; Score= ' + str(question.question_score)
		print "Length: " + str(len(self.questions))

	def printAnswers(self):
		count = 0
		for qid, question in self.questions.iteritems():
			if question.answerFetched:
				count+=1
				print question.answer
				
		print "Answers #: " + str(count)


	def printNumOfQuestions(self):
		print len(self.questions)

	def printApprovedQuestions(self):
		approvedQ = 0
		questionNumber = 1
		for qid, question in self.questions.iteritems():
			if question.approved:
				print str(questionNumber) + '. '+ question.title + '\n'
				print question.answer
				approvedQ += 1

			questionNumber +=1

		print 'Length: ' + str(approvedQ) + '\n'

	def printApprovedQuestionsWithFilter(self, filterA):
	# Filter is a string that will be queried in the question and answer to find relevancy
		if filterA == '':
			self.printApprovedQuestions()
		else:
			numOfQ = 0
			questionNumber = 1
			for qid, question in self.questions.iteritems():
				if question.approved:
					if filterA in question.title or filterA in question.answer:
						print str(questionNumber) + '. '+ question.title + '\n'
						if len(question.answer) > 1000:
							print "this answer is TOO LONG > 1000 chars\n"
						else: 
							print question.answer + '\n'
						numOfQ += 1
				questionNumber += 1
			print 'Length: ' + str(numOfQ)

	# Return all question's answer IDs
	def getAllAnswerIDs(self):
		ids = []
		for qid, question in self.questions.iteritems():
			if question.isAnswered:
				ids.append(question.answer_id)

		return ids

	########## SERVER CONNECTION METHODS ############
	
	def fetchAnswerValue(self, answerID):
		stringAnswer = ''
		page = requests.get("http://www.stackoverflow.com/a/"+str(answerID))
		tree = html.fromstring(page.content)
		answer = tree.xpath('//div[@class="answer accepted-answer"]/table/tr/td[@class="answercell"]/div[@class="post-text"]/descendant::*/text()')  #div[@class="post-text"]/*/text()
		
		for element in answer:
			stringAnswer += element.encode('UTF-8')

		return stringAnswer

	def fetchAnswerValues(self):
		for qid, question in self.questions.iteritems():
			question.answer = self.fetchAnswerValue(question.answer_id)

	########### DATA MANAGEMENT METHODS ############

	def verifyAllQuestions(self):
		# Assume success
		returnValue = True

		questionNumber = 1
		for qid, question in self.questions.iteritems():
			if not question.approved:
				if question.answerFetched:
					if not self.verifyQuestion(question, questionNumber):
						returnValue = False
						break		
			questionNumber += 1

		self.processQuestions()

		return returnValue


	def verifyQuestion(self, question, questionNumber):
		# NOTE: Parameter is question number, not array index.
		# IN: Question to verify
		# OUT: return true to verify next question, false to stop (if called by verifyAllQuestions)
		print '\n'
		userInput = 'z'
		print str(questionNumber) + '. ' + question.title + '\n'
		while userInput != 'I':
			print "Input 'a' to print the answer, 'as' for answer score, 'qs' for question score, 'x' to quit (continue later)\n'q' for question, 'qb' for question body, d' to delete, 'i' to ignore, and 'p' to approve: " 
			userInput = raw_input("Options: a, as, qs, q, d, i, p: ")
			userInput = userInput.upper()
			print '\n'
			if userInput == 'A':
				print question.answer + '\n'
			elif userInput == 'AS': 
				print 'Answer Score: ' + str(question.answer_score) + '\n'
			elif userInput == 'QS':
				print 'Question Score: ' + str(question.question_score) + '\n'
			elif userInput == 'QB':
				print question.question_body + '\n'
			elif userInput == 'D':
				self.questions[str(question.question_id)].markUnsatisfiable()
				userInput = 'I'
			elif userInput == 'I':
				print 'Ignoring...\n'
			elif userInput == 'P':
				self.approveQuestion(question.question_id)
				userInput = 'I'
			elif userInput == 'Q':
				print str(questionNumber) + '. ' + question.title + '\n'
			elif userInput == 'X':
				return False

		# END QUESTION VERIFICATION WHILE LOOP

		return True

	# END VERIFY QUESTION FUNCTION

	def processQuestions(self):
		print 'Processing questions... 	'

		for qid, question in self.questions.iteritems():
			# Verify that the question data is within parameters, and does not have an unsatisfiable answer
			question.verifyData()

			# If question has no accepted answer or the score is too low:
			if (question.isAnswered == False) or (question.question_score < self.SCORE_MIN):
				question.answerUnsatisfiable = True 
				print 'Question has no answer or score too little. Deleting...'
			
			elif question.answerFetched == True: # If question answer has been fetched
				# and the answer score is too low
				if (question.answer_score < self.SCORE_MIN): 
					question.answerUnsatisfiable = True
					print 'Answer score too low. Deleting...'
				# (or) and the answer hasn't failed parse AND html parse is on
				elif not question.parseFailed and self.htmlparse == True:
					question.parseAnswer() # parse the answer

		# Delete all unsatisfiable questions from system.
		self.deleteUnsatisfiableQuestions()

	def parseAnswers(self):
		for qid, question in self.questions.iteritems():
			question.parseAnswer()

	def deleteFailedParse(self):
		idsToDelete = []
		for qid, question in self.questions.iteritems():
			if question.parseFailed == True:
				idsToDelete.append(qid)
		
		numDeleted = self.deleteQuestions(idsToDelete)

		print 'Successfully deleted ' + str(numDeleted) + ' failed parse questions.'

	def deleteUnsatisfiableQuestions(self):
		qidsToDelete = []

		# # Only keep all elements with satisfiable answers
		for qid, q in self.questions.iteritems():
			if q.answerUnsatisfiable == True:
				qidsToDelete.append(qid)

		numDeleted = self.deleteQuestions(qidsToDelete)

		print 'Successfully deleted ' + str(numDeleted) + ' unsatisfiable questions.'

	def deleteQuestions(self, qids):
		# Deletes questions for question ids (qids = list)
		# Returns num of qids successfully deleted
		num = 0
		for qid in qids:
			try:
				self.deleteQuestion(qid)
				num+=1
			except Exception as e:
				print "Could not delete question " + str(qid) + ": " + str(e)
		return num

	# Deletes the question from the dictionary corresponding to the question ID 
	def deleteQuestion(self, qid):
		try:
			del self.questions[str(qid)]
		except:
			print 'Could not delete question with id ' + str(qid) + '.' 


	def getUnansweredQuestionIDs(self):
		unanswered = []
		for qid, question in self.questions.iteritems():
			if not question.answerFetched:
				unanswered.append(qid)
		return unanswered

	def getUnfetchedAnswerIDs(self):
		unanswered = []
		for qid, question in self.questions.iteritems():
			if not question.answerFetched:
				unanswered.append(question.answer_id)
		return unanswered

	def approveQuestion(self, qid):
		self.questions[str(qid)].approve()

	########## FILE SAVING METHODS ##########

	# Load the question collection from file
	@staticmethod
	def createFromFile(name):
		# Set questionCollection (variable to be returned) to None in case of error
		questionCollection = None
		if type(name) is str:
			questionCollection = QuestionsCollection()
			questionCollection.loadFromFile(name)
		else:
			print "Cannot load question collection from name that is not of string type."

		return questionCollection

	def load(self, name):
		# Load Basic Question Collection Info
		loadFile = open(name, 'rb')
		collection = pickle.load(loadFile)
		loadFile.close()

		# Load Questions Array
		collection.loadQuestionsFromFile(name+str('Q'))
		collection.processQuestions()

		return collection

	def loadBackup(self, name):
		return self.load(name+'.bak')

	def save(self, name):
		# Save the file by dumping with pickle
		saveFile = open(name, 'wb')
		pickle.dump(self, saveFile)
		saveFile.close()

		# Save a backup just in case.
		backupSaveFile = open(name+'.bak', 'wb')
		pickle.dump(self, backupSaveFile)
		backupSaveFile.close()

		self.saveQuestionsToFile(name + str('Q'))

	def saveQuestionsToFile(self, name):
		saveFile = open('questions/'+str(name), "wb")
		pickle.dump(self.questions, saveFile)
		saveFile.close()

	def loadQuestionsFromFile(self, name):
		# Loads question from file at questions/<name>
		# Input: Collection name (string)
		# Output: Questions array
		loadFile = open('questions/'+str(name), "rb")
		self.questions = pickle.load(loadFile)
		loadFile.close()
		self.size = len(self.questions)

		# Legacy Save
	def saveToFile(self, name):
		self.saveQuestionsToFile(name)
		self.saveAnswersToFile(name)

	# Legacy Load
	def loadFromFile(self, name):
		self.loadAnswersFromFile(name)
		self.loadQuestionsFromFile(name)


# END QuestionsCollection.py




	


