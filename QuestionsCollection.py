import pickle
import requests
from Question import Question
from lxml import html
import sys

class QuestionsCollection:
# 	'Class that contains questions along with their answers, and saves them locally.'
	questions = []
	question_id_index = {}  # Stores question id (key) pointing to index in array
	answers = []
	size = 0
	next_page_to_fetch = 1

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

		# Avoid any append errors from crashing the program
		#try:
			# Add to local array and update size
		self.question_id_index[str(question.question_id)] = len(self.questions)-1
		#except:
		#	print "Couldn't add question. Failed to append to array."

	# Add an array of JSON question objects
	def addQuestionsJSON(self, questionsJSON):
		# questionsJSON is an array of JSON question objects, as recieved from StackExchange API
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
		for answerJSON in answersJSON:
			try:
				index = self.question_id_index[answerJSON['question_id']]
				self.questions[index].answer = 'answer'
			except:
				print 'Couldn\'t find question for answer.'

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


	def printQA(self, question):
		print 'Question:\n '
		print question.title
		print '\nAnswer:\n '
		print question.answer

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

	SCORE_MIN = 20

	def processQuestions(self):
		self.buildQuestionIDIndex()

		for index in reversed(range(0 ,len(self.questions))):
			question = self.questions[index]
			question.verifyData()
			# Build question id index dictionary
			self.question_id_index[str(question.question_id)] = index
			if (question.isAnswered != True) or (question.question_score < self.SCORE_MIN):
				self.questions.pop(index)
			elif question.answerFetched:
				if question.answer_score < self.SCORE_MIN:
					self.questions.pop(index)
				elif not question.parseFailed:
					question.parseAnswer()


	def deleteFailedParse(self):
		index = 0
		for question in self.questions:
			if question.parseFailed == True:
				self.questions.pop(index)
			index += 1

	def deleteUnsatisfiableQuestions(self):
		initialLen = len(self.questions)
		# # Only keep all elements with satisfiable answers
		self.questions[:] = [q for q in self.questions if not q.answerUnsatisfiable]
		# for q in self.questions:
		# 	if q.answerUnsatisfiable:
		# 		print '+'
		finalLen = len(self.questions)

		return initialLen - finalLen

	def deleteQuestionIndexes(self, questionIndexes):
		questionIndexes.sort()
		# Reverse for loop to iterate through indexes of questionIndexes array (reverse loop to avoid issues when deleting [index shifting])
		for n in range(len(questionIndexes)-1, -1, -1):
			print questionIndexes[n]
			# Add one to question index, since removeQuestion takes questionNumber as argument
			self.removeQuestion(questionIndexes[n]+1)

	def buildQuestionIDIndex(self):
		index = 0
		for question in self.questions:
			self.question_id_index[str(question.question_id)] = index
			index +=1

	def getApprovedQuestions(self):
	  approvedQuestions = []
	  for question in self.questions:
	  	if question.isAnswered == True:
	  		if question.question_score > SCORE_MIN:
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

	@staticmethod
	def load(name):
		saveFile = open(name, 'rb')
		collection = pickle.load(saveFile)
		saveFile.close()
		collection.buildQuestionIDIndex()
		collection.processQuestions()

		return collection

	@staticmethod
	def loadBackup(name):
		return QuestionsCollection.load(name+'.bak')


	def save(self, name):
		# Save the file by dumping with pickle
		saveFile = open(name, 'wb')
		pickle.dump(self, saveFile)
		saveFile.close()

		# Save a backup just in case.
		backupSaveFile = open(name+'.bak', 'wb')
		pickle.dump(self, backupSaveFile)
		backupSaveFile.close()

	def saveToFile(self, name):
		self.saveQuestionsToFile(name)
		self.saveAnswersToFile(name)

	def loadFromFile(self, name):
		self.loadAnswersFromFile(name)
		self.loadQuestionsFromFile(name)
		self.buildQuestionIDIndex()


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
			if (not question.approved) and question.answerFetched:
				if not (self.verifyQuestion(questionNumber)):
					return False
			questionNumber += 1

		return True

	def verifyQuestion(self, questionNumber):
		# NOTE: Parameter is question number, not array index.
		if questionNumber < 1 or questionNumber > len(self.questions):
			print "ERROR in QuestionCollection.verifyQuestion(): index not in range"
			sys.exit(-1)
		index = questionNumber -1
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


	


