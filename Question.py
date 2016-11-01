from html2text import HTML2Text

class Question:
# Class containing all important question details.
	title = ''
	question_body = ''
	top_answer = ''
	answer = ''
	question_id = 0
	answer_id = 0
	question_score = 0
	answer_score = 0
	lastActivityDate = 0
	tags = []
	isAnswered = False
	answerFetched = False
	answerUnsatisfiable = False
	approved = False
	parseFailed = False

	def __addTag__(self, tag):
		if type(tag) is str:
			tags.append(tag)

	def markUnsatisfiable(self):
		self.answerUnsatisfiable = True

	def approve(self):
		self.approved = True

	def parseAnswer(self):
		if self.answerFetched:
			try:
				answer = self.parseResponseUnicode(self.answer)
				h = HTML2Text()
				h.ignore_links = True
				answer = h.handle(answer)
				self.answer = answer
			except Exception as e: 
				print "Couldn't parse answer: " + self.title
				print e
				self.parseFailed = True

	# Set important values from StackExchange's JSON response to local values for this question object
	def createQuestionFromJSON(self, JSON):
		self.title = self.parseResponseUnicode(JSON['title'])
		self.question_id = JSON['question_id']
		self.tags = JSON['tags']
		self.isAnswered = JSON['is_answered']
		self.question_body = JSON['body'].encode('UTF-8')
		# Only has accepted_answer_id if has been answered
		try:
			self.answer_id = JSON['accepted_answer_id']
		except: 
			self.answer_id = 0
			self.isAnswered = False
			self.answerUnsatisfiable = True
			print 'No accepted answer id.'

		self.question_score = JSON['score']
		self.lastActivityDate = JSON['last_activity_date']

	def addAnswerFromJSON(self, JSON, SCORE_MIN):
	# Add answer values to question object
	# IN: Takes in an answer JSON object as recieved from StackExchange API request
	# OUT: Returns true if answer satisfies requirements, else marks question as unsatisfiable.

		if JSON['is_accepted'] == True and JSON['score'] >= SCORE_MIN:
			# If answer has not been recorded or is higher scored, add/replace it.
			if not self.answerFetched or JSON['score'] > self.answer_score:
				self.answer = JSON['body'].encode('UTF-8')
				self.answer_score = JSON['score']
				self.answerFetched = True
		else:
			print 'Answer not accepted'
			self.answerUnsatisfiable = True

		return not self.answerUnsatisfiable

	def verifyData(self):
		# Cannot have answers that are TOO long.
		if len(self.title) > 200 or len(self.answer) > 10000:
			print 'Unsatisfiable; too long.'
			self.answerUnsatisfiable = True
		if len(self.question_body) > 5000:
			self.question_body = 'Body too long: deleted.'

	def parseResponseUnicode(self, response):
		# HTML Character sequences common in responses, to be further replace with the values below.
		quote = '&quot;'
		lessthan = "&lt;"
		lessthanorequal = "&lt;="
		greaterthan = "&gt;"
		greaterthanorequal = "&gt;="
		singlequote = "&#39;"
		amp = "&amp;"
		codeStart = "<code>"
		codeEnd = "</code>"

		specialChars = [quote, lessthan, lessthanorequal, greaterthan, greaterthanorequal, singlequote, amp, codeStart, codeEnd]
		specialCharsValues = ['"', "<", "<=", ">", ">=", "'", "&", '', '']

	    # Replace any common HTML characters with the actual character value
		index = 0;
		for specialChar in specialChars:
			if specialChar in response:
				response = response.replace(specialChar, specialCharsValues[index])
			index = index + 1

		return response