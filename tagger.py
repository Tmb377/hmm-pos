from collections import defaultdict
from operator import itemgetter
import sys



#open training file
trainFile = open('training.pos', 'r')

#count number of times each pos tag is used
posCount = {}
#count number of instances of each word in training corpus
wordCount = {}
#store probs of each word as a certain pos tag
wordFreq = defaultdict(dict)
POSWordPair = defaultdict(dict)
#store all instances of word, tag pairs
wordPOS = defaultdict(list)
POSWord = defaultdict(list)
#count transitions between pos tags
transProbsCount = defaultdict(list)
#store transition probabilities
transProbs = defaultdict(dict)
#store dict POS:{word:prob}
POSWordFreq =defaultdict(dict)
#variable for storing transition probabilites, starts with start
lastPOS = 'start'
posCount[lastPOS] = 1

def findLeastCommon(tagToCheck):
	#sort list of words by probability to find the least common
	sortedList = sorted(POSWordPair[tagToCheck].items(), key=itemgetter(1), reverse=True)
	return sortedList[len(sortedList)-1][1]

for line in trainFile:
	#check that it is not a blank line
	if line.strip():
		toArray = line.split("\t")
		toArray[1] = toArray[1].rstrip('\n')
		wordPOS[toArray[0]].append(toArray[1])
		POSWord[toArray[1]].append(toArray[0])
		#count number of times word is used
		if toArray[0] not in wordCount:
			wordCount[toArray[0]] = 1
		else:
			wordCount[toArray[0]] += 1
		#count number of times pos tag is used
		if toArray[1] not in posCount:
			posCount[toArray[1]] = 1
		else:
			posCount[toArray[1]] +=1
		#add transition with lastPOS seen
		transProbsCount[lastPOS].append(toArray[1])
		lastPOS = toArray[1]

#begin to calculate statistics 		
numWords = 0
for key in wordCount:
	numWords += wordCount[key]

#calculate transition probabilites
for POStag in transProbsCount:
	numUses = posCount[POStag]
	for tag in transProbsCount[POStag]:	
		transitionProbability = transProbsCount[POStag].count(tag)/numUses
		transProbs[POStag][tag] = transitionProbability

#calculate probabilites for each word being a certain POS
for word in wordPOS:
	numberUsed = wordCount[word]
	for tagUsed in wordPOS[word]:
		if wordPOS[word].count(tagUsed) != 0:
			wordFreq[word][tagUsed] = wordPOS[word].count(tagUsed)/posCount[tagUsed]

#calculate probabilities for each POS being a certain word
for partOfSpeech in POSWord:
	timesUsed = posCount[partOfSpeech]
	for wordsUsed in wordCount:
		if wordsUsed in POSWord[partOfSpeech]:
			pr = POSWord[partOfSpeech].count(wordsUsed)/timesUsed
			POSWordPair[partOfSpeech][wordsUsed] = pr

trainFile.close()

#begin to parse documents for tagging
arguments = sys.argv
argLen = len(arguments);
#make closed class of POS tags 
closedClass = {"COMMA", "(", ")", "HYPH", ":"}


newFile = open(arguments[1], 'r')
writeFile = open(arguments[2], 'w')

currentTag = 'start'
maxProbSeen = 0
maxProbTag = 'NN'
currentProb = -1
for readLine in newFile:
	wordToTag = readLine.rstrip('\n')
	if readLine.strip():
		
		if wordToTag in wordCount:
			
			for possibleTag in transProbs[currentTag]:
			
				transitionProb = transProbs[currentTag][possibleTag]
				
				if possibleTag in wordFreq[wordToTag]:
					
					currentProb = transitionProb * wordFreq[wordToTag][possibleTag]
				
				if currentProb > maxProbSeen:
					maxProbSeen = currentProb
					maxProbTag = possibleTag
			stringToAdd = wordToTag + '\t' + maxProbTag + '\n'
			writeFile.write(stringToAdd)
			currentTag = maxProbTag
			maxProbSeen = 0
			maxProbTag = 'NN'
			currentProb = -1
		else:
			for possibleTag in transProbs[currentTag]:
				if argLen == 4:
					if wordToTag[0].isupper():    #This method
						maxProbTag = "NNP"			#gave 88%
					elif wordToTag[:-2] == "ly":	#accuracy
						maxProbTag = "RB"
					elif wordToTag[:-2] == "ed":
						maxProbTag = "VBD"
					else:
						maxProbTag = "NN"
				if argLen == 3:
					#if possibleTag not in closedClass:
						if possibleTag in transProbs[currentTag]:
							transitionProb = transProbs[currentTag][possibleTag]
							leastCommon = findLeastCommon(possibleTag)
							currentProb = transitionProb * leastCommon
							if currentProb > maxProbSeen:
								maxProbSeen = currentProb
								maxProbTag = possibleTag
				
			stringToAdd = wordToTag + '\t' + maxProbTag + '\n'
			writeFile.write(stringToAdd)
			currentTag = maxProbTag
			maxProbSeen = 0
			maxProbTag = 'NN'
			currentProb = -1
	else:
		writeFile.write('\n')		
newFile.close()
writeFile.close()

