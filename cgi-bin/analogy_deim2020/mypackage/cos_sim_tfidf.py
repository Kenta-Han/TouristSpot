# -*- coding: utf-8 -*-
import math

class SimCalculator():
	## コサイン類似度
	def _absolute(self, vector):
		## ベクトルの長さ(絶対値)を返す
		squared_distance = sum([i[1] ** 2 for i in vector])
		distance = math.sqrt(squared_distance)
		return distance

	def sim_cos(self, v1, v2):
		numerator = 0
		## v1とv2で共通するkeyがあったとき、その値の積を加算していく。2つのベクトルの内積になる。 = sigma(A*B)
		for word in [i[0] for i in v1[1]]:
			if word in [j[0] for j in v2[1]]:
				numerator += v1[1][[i[0] for i in v1[1]].index(word)][1] * v2[1][[j[0] for j in v2[1]].index(word)][1]
		denominator = self._absolute(v1[1]) * self._absolute(v2[1])
		if denominator == 0:
			return 0
		return numerator / denominator
