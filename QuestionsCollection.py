import pickle
import requests
from Question import Question
from lxml import html

class QuestionsCollection:
# 	'Class that contains questions along with their answers, and saves them locally.'
	questions = []
	question_id_index = {}  # Stores question id (key) pointing to index in arrayselssize = 0
	next_page_to_fetch = 1
	size = 0
	htmlparse = True 		   # Set to True if you want to parse answer HTMLs (may hide some links, but provides clearer text)
	SCORE_MIN = 20				 # Minimum score allowed for questions and answers

	def initWithQuestions(self, questions, name):
		# // Initialize the class 
		# // Input: questions (array) & a name (string)
		self.questions = questions
		self.size = len(questions)

	# Add a single JSON question object
	def addQuestionJSON(self, questionJSON):
	# // Add a question through it's JSON object representation 
	# // Input: JSON object
		# Create a question object from JSON
		question = Question()
		question.createQuestionFromJSON(questionJSON)

		# Add to local questions array and update size
		self.questions.append(question)
		self.size += 1

		# Add to id index dictionary
		self.question_id_index[str(question.question_id)] = self.size-1

	def addQuestionsJSON(self, questionsJSON):
	# Add an array of JSON question objects
	# IN: questionsJSON is an array of JSON question objects, as recieved from StackExchange API
		for questionJSON in questionsJSON:
			self.addQuestionJSON(questionJSON) 

	# Add a single question object
	def addQuestion(self, question):
		# Directly add question (trusted)
		if type(question) is Question:
			self.questions.append(question)
			self.question_id_index[question.question_id] = len(questions)-1
			self.size += 1

	# Add an array of question objects
	def addQuestions(self, questions):
		for question in questions:
			self.addQuestion(question);

	def addAnswersJSON(self, answersJSON):
		# answersJSON is an array of JSON answer objects, as recieved from StackExchange API

		# Keep track of number of 'approved' questions
		numApproved = 0

		for answer in answersJSON:
			index = self.question_id_index[str(answer['question_id'])]
			# Add JSON data to question object
			
			# If return value is True, means answer was approved
			if self.questions[index].addAnswerFromJSON(answer, self.SCORE_MIN):
				numApproved+= 1

		# Process the questions (only take eligible ones, build id array, delete unsatisfiable, and a bunch of other stuff)
		self.processQuestions()

		return numApproved

  # Print questions info (title and score)
	def printQuestions(self):
		for question in self.questions:
			print question.title + ' ; Score= ' + str(question.question_score)
		print "Length: " + str(len(self.questions))

	def printAnswers(self):
		count = 0
		for question in self.questions:
			if question.answerFetched:
				count+=1
				print question.answer
				
		print "Answers #: " + str(count)

	def parseAnswers(self):
		for question in self.questions:
			question.parseAnswer()

	def printNumOfQuestions(self):
		print len(self.questions)

	def printApprovedQuestions(self):
		numOfQ = 0
		questionNumber = 1
		for question in self.questions:
			if question.approved:
				print str(questionNumber) + '. '+ question.title + '\n'
				print question.answer
				numOfQ += 1

			questionNumber +=1

		print 'Length: ' + str(numOfQ) + '\n'

	def printApprovedQuestionsWithFilter(self, filterA):
	# Filter is a string that will be queried in the question and answer to find relevancy
		if filterA == '':
			self.printApprovedQuestions()
		else:
			numOfQ = 0
			questionNumber = 1
			for question in self.questions:
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

		# def deleteUnsatisfiableQuestions(self):
		# 	number = 0
		# 	for question in self.questions:
		# 		if question.answerFetched == True and question.answer == '':


	# Return all question's answer IDs
	def getAllAnswerIDs(self):
		ids = []
		for question in self.questions:
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
		for question in self.questions:
			question.answer = self.fetchAnswerValue(question.answer_id)

	########### DATA MANAGEMENT METHODS ############

	def processQuestions(self):

		index = 0
		for question in self.questions:
			# Verify that the question data is within parameters, and does not have an unsatisfiable answer
			question.verifyData()
			# Build question id index dictionary
			self.question_id_index[str(question.question_id)] = index

			if (question.isAnswered == True) and (question.question_score < self.SCORE_MIN):
				question.answerUnsatisfiable = True

			elif question.answerFetched:
				if question.answer_score < self.SCORE_MIN:
					question.answerUnsatisfiable = True
				# Try parsing the answer HTML only if hasn't failed before
				elif not question.parseFailed and self.htmlparse == True:
					question.parseAnswer()

			index+= 1

		self.deleteUnsatisfiableQuestions()


	def deleteFailedParse(self):
		index = 0
		for question in self.questions:
			if question.parseFailed == True:
				self.questions.pop(index)
			index += 1

	def deleteUnsatisfiableQuestions(self):
		initialLen = len(self.questions)
		# # Only keep all elements with satisfiable answers
		# self.questions[:] = [q for q in self.questions if not q.answerUnsatisfiable]
		indexes = []
		index = 0
		for q in self.questions:
			if q.answerUnsatisfiable == True:
				indexes.append(index)
			index+=1

		if indexes == []:
			print 'No questions to delete...'

		else:
			self.deleteQuestionIndexes(indexes)
			print 'Success Deleting Unsatisfiable'

		# for q in self.questions:
		# 	if q.answerUnsatisfiable:
		# 		print '+'
		finalLen = len(self.questions)

		return initialLen - finalLen

	def deleteQuestionIndexes(self, questionIndexes):
		# Sort indexes in reverse order (to chew off the higher indexes, so lower are unaffected)
		questionIndexes.sort(reverse=True)
		for index in questionIndexes:
			self.removeQuestion(index+1)   # +1 since function takes question number, not index
			print 'Removing index ' + str(index) + ' out of ' + str(len(self.questions))

	def buildQuestionIDIndex(self):
		index = 0
		for question in self.questions:
			self.question_id_index[str(question.question_id)] = index
			index +=1

	def getApprovedQuestions(self):
	  approvedQuestions = []
	  for question in self.questions:
	  	if question.isAnswered == True:
	  		if question.question_score > self.SCORE_MIN:
	  			approvedQuestions.append(question)

	  return approvedQuestions

	def getUnansweredQuestionIDs(self):
		unanswered = []
		for question in self.questions:
			if not question.answerFetched:
				unanswered.append(question.question_id)

		return unanswered

	def removeQuestion(self, questionNumber):
		self.questions.pop(questionNumber-1)

	def removeQuestionByID(self, questionID):
		index = self.question_id_index[str(questionID)]
		# if index is out of bounds
		if (index >= len(self.questions)) or (index < 0):
			print "Attempting to remove question " + str(questionID) + ' with index ' + str(index) + ' out of ' + str(len(self.questions)) + ' questions.'
		else:
			self.questions.pop(index)
			self.updateIDDictAfter(index)

	def updateIDDictAfter(self, index):
		for i in range(index, len(self.questions)):
			self.question_id_index[str(self.questions[i].question_id)] = i 

	def approveQuestion(self, questionNumber):
		self.questions[questionNumber-1].approve()

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

	# Legacy Save
	def saveToFile(self, name):
		self.saveQuestionsToFile(name)
		self.saveAnswersToFile(name)

	# Legacy Load
	def loadFromFile(self, name):
		self.loadAnswersFromFile(name)
		self.loadQuestionsFromFile(name)


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


	def saveAnswersToFile(self, name):
		# Input: QuestionsCollection name (string)
		saveFile = open('answers/'+str(name), "wb")
		pickle.dump(self.answers, saveFile)
		saveFile.close()

	def loadAnswersFromFile(self, name):
		# Loads answers from file at answers/<name>
		# Input: Collection name (string)
		# Output: Answers array
		loadFile = open('answers/'+str(name), "rb")
		self.answers = pickle.load(loadFile)
		loadFile.close()

	def verifyAllQuestions(self):
		questionNumber = 1
		for question in self.questions:
			if not question.approved:
				if question.answerFetched:
					if not self.verifyQuestion(questionNumber):
						return False
			questionNumber += 1

		return True

	def verifyQuestion(self, questionNumber):
		# NOTE: Parameter is question number, not array index.
		if questionNumber < 1 or questionNumber > len(self.questions):
			print "ERROR in QuestionCollection.verifyQuestion(): index not in range"
			return
		index = questionNumber - 1
		print '\n'
		question = self.questions[index]
		userInput = 'z'
		print str(questionNumber) + '. ' + question.title + '\n'
		while userInput != 'I':
			print "Input 'a' to print the answer, 'as' for answer score, 'qs' for question score,\n'q' for question, d' to delete, 'i' to ignore, and 'p' to approve: " 
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
				self.removeQuestion(questionNumber)
				questionNumber-=1
				userInput = 'I'
			elif userInput == 'I':
				print 'Ignoring...\n'
			elif userInput == 'P':
				self.approveQuestion(questionNumber)
				userInput = 'I'
			elif userInput == 'Q':
				print str(questionNumber) + '. ' + question.title + '\n'
			elif userInput == 'X':
				return False

		# END QUESTION VERIFICATION WHILE LOOP

		return True

	# END VERIFY QUESTION FUNCTION


	


