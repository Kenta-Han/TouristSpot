import math
from tqdm import tqdm
import codecs

## スポット毎の{"単語"：重み(tfidf_kantou),"単語"：重み(tfidf_kantou)...}
def Kantou(spot):
	now_spot = spot[0][0]
	spot_alone = {}
	spot_all = []
	for word in spot:
		if now_spot != word[0]:
			now_spot = word[0]
			spot_all.append(spot_alone)
			spot_alone = {}
			spot_alone[word[1]] = word[2]
		else:
			spot_alone[word[1]] = word[2]
	spot_all.append(spot_alone)
	return spot_all

## スポット毎の{"単語"：重み(tfidf/kld_season),"単語"：重み(tfidf/kld_season),...}
def Season(spot):
	now_spot = spot[0][0]
	spot_alone = {}
	spot_all = []
	for word in spot:
		if now_spot != word[0]:
			now_spot = word[0]
			if word[3] == None:
				word[3] = 0
				spot_all.append(spot_alone)
				spot_alone = {}
				spot_alone[word[1]] = word[3]
			else:
				spot_all.append(spot_alone)
				spot_alone = {}
				spot_alone[word[1]] = word[3]
		else:
			if word[3] == None:
				word[3] = 0
				spot_alone[word[1]] = word[3]
			else:
				spot_alone[word[1]] = word[3]
	spot_all.append(spot_alone)
	return spot_all

## スポット毎の{"単語"：重み(tfidf/kld_type),"単語"：重み(tfidf/kld_type),...}
def Type(spot):
	now_spot = spot[0][0]
	spot_alone = {}
	spot_all = []
	for word in spot:
		if now_spot != word[0]:
			now_spot = word[0]
			if word[4] == None:
				word[4] = 0
				spot_all.append(spot_alone)
				spot_alone = {}
				spot_alone[word[1]] = word[4]
			else:
				spot_all.append(spot_alone)
				spot_alone = {}
				spot_alone[word[1]] = word[4]
		else:
			if word[4] == None:
				word[4] = 0
				spot_alone[word[1]] = word[4]
			else:
				spot_alone[word[1]] = word[4]
	spot_all.append(spot_alone)
	return spot_all
