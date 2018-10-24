import math

class SimCalculator():
	## コサイン類似度
	def absolute(self, vector):
		squared_distance = sum([vector[i] ** 2 for i in range(len(vector))])
		distance = math.sqrt(squared_distance)
		return distance

	def sim_cos(self, v1, v2):
		numerator = 0
		for i in range(len(v1)):
			numerator += v1[i] * v2[i]
		denominator = self.absolute(v1) * self.absolute(v2)
		return numerator / denominator
