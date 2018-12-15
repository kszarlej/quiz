import sys
import os
from random import shuffle
from collections import defaultdict

from fuzzywuzzy import fuzz, process

sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from questions import questions

class Visitor(object):
	pass

class Categories():
	def __init__(self, questions):
		self.questions = questions
		self.categories = self.generate(questions)

	def generate(self, questions):
		categories = defaultdict(int)

		for q in questions:
			for category in q['categories']:
				categories[category] = categories[category] + 1
				categories['All'] = categories['All'] + 1

		return categories

	def draw(self):
		print('Available categories:')
		for category, qnum in self.categories.items():
			print(f">>> {category} [questions={qnum}]")
		print("")


	def __get_q_by_cat(self, cat):
		if cat == 'All':
			return questions

		temp_questions = []
		for question in self.questions:
			if cat in question['categories']:
				temp_questions.append(question)

		return temp_questions

	def choose_category(self):
		cat = input(f"Choose category: ")
		if cat not in self.categories.keys():
			print("No such category")
			sys.exit(1)

		return self.__get_q_by_cat(cat)

class Question():
	def accept(self, visitor):
		method_name = 'visit_{}'.format(self.type)
		try:
			visit = getattr(visitor, method_name)
		except AttributeError as e:
			print(f"Error. Missing method visit_{self.type} for visitor {visitor}")
			sys.exit(1)

		return visit(self)


	def __init__(self, question):
		self.question = question['question']
		self.type = type
		try:
			self.type = question['type']
		except KeyError:
			self.type = 'default'

		try:
			self.comment = question['comment']
		except KeyError:
			self.comment = None

		try:
			self.choices = question['choices']
		except KeyError:
			self.choices = None

		self.correct_answers = question['answers']

class Ask(Visitor):
	def visit_yesorno(self, q):
		answer = input(f"{q.question} [yes/no]: ")
		q.answer = answer

	def visit_default(self, q):
		answer = input(f"{q.question}: ")
		q.answer = answer

	def visit_comma_seperated_list(self, q):
		answer = input(f"{q.question}. Provide unquoted, comma separated list eg: aws,gcp,alibaba: ")
		q.answer = answer

	def visit_choice(self, q):
		print(f"{q.question}")
		for choice in q.choices:
			print(f"{choice[0]}) {choice[1]}")

		answer = input(f"Choose one: ")
		q.answer = answer

class CheckAnswer(Visitor):
	def visit_yesorno(self, q):
		yes_answers = ['y', 'yes', 'ye', 'yup', 'yep', 'true']
		no_answers = ['n', 'no', 'nope', 'not', 'nono', 'false']

		if q.answer.lower() in yes_answers:
			answer = 'y'

		if q.answer.lower() in no_answers:
			answer = 'n'

		if not answer:
			raise ValueError(f"Answer {q.answer} is incorrect answer.")

		q.iscorrect = answer == q.correct_answers[0]
		return q.iscorrect

	def visit_default(self, q):
		q.iscorrect = q.answer.lower() in q.correct_answers
		return q.iscorrect

	def visit_choice(self, q):
		q.iscorrect = q.answer.lower() == q.correct_answers[0]
		return q.iscorrect

class WriteResult(Visitor):
	def visit_default(self, q):
		if q.iscorrect:
			msg = "\n Correct!"
			if q.comment is not None:
				msg = f"{msg} {q.comment}"
			print(f"{msg}\n")
		else:
			print(f"\n Incorrect! Correct answer is {q.correct_answers}\n")

	def visit_yesorno(self, q):
		self.visit_default(q)

	def visit_comma_seperated_list(self, q):
		self.visit_default(q)

	def visit_choice(self, q):
		self.visit_default(q)

class State():
	def __init__(self, qnum):
		self.qnum = qnum
		self.correct = 0

	def increment(self):
		self.correct += 1


def categories(questions):
	categories = defaultdict(int)

	for q in questions:
		for category in q['categories']:
			categories[category] = categories[category] + 1
			categories['All'] = categories['All'] + 1

	return categories

if __name__ == "__main__":
	"""
	Simple program for quizes in CLI. Uses Visitor pattern
	"""
	state = State(len(questions))

	categories = Categories(questions)
	categories.draw()
	qs = categories.choose_category()
	shuffle(qs)

	for question in qs:
		q = Question(question)
		q.accept(Ask())
		if q.accept(CheckAnswer()):
			state.increment()
		q.accept(WriteResult())

	print(f"Test completed! You scored {state.correct}/{len(qs)} [{state.correct / len(qs) * 100}%]\n")
	return 0
