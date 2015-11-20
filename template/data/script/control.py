#Put here useful global functions for the game to use in any scene.

from core import utils, module

quotes = [
"My wallet is like an onion, \nWhen I open it, it makes me cry.",
"What you do today can improve all your tomorrows.",
"There are two kinds of people in the world: \nthose who think there are two kinds of people in the world\nand those who don't.",
"Always borrow money from a pessimist. \nHe won't expect it back.",
"Do not argue with an idiot. \nHe will drag you down to his level and beat you with experience.",
"If you steal from one author, it's plagiarism; \nif you steal from many, it's research.",
"When you go into court you are putting your fate\n into the hands of twelve people who weren't \nsmart enough to get out of jury duty.",
"Those people who think they know everything \nare a great annoyance to those of us who do.",
"When tempted to fight fire with fire, \nremember that the Fire Department usually uses water.",
"A bank is a place that will lend you money, \nif you can prove that you don't need it."
]

def _quoteAlphaInterpol(x):
	lab = module.labels["QuoteLine"]
	lab.color.w = x

def changeQuote():
	utils.LinearInterpolation(1, 0, 3, _quoteAlphaInterpol, replaceQuote)

def replaceQuote():
	lab = module.labels["QuoteLine"]
	oldtext = lab.text
	lab.text = quotes[utils.rand10()]
	if lab.text == oldtext: changeQuote()
	utils.LinearInterpolation(0, 1, 3, _quoteAlphaInterpol)
