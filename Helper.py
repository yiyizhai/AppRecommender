from pymongo import MongoClient
from dataservice import DataService
import operator
import math
import time

class Helper(object):

	@classmethod
	def cosine_similarity(cls, app_list1, app_list2):
		match_count = cls.__count_match(app_list1, app_list2)
		return float(match_count) / math.sqrt( len(app_list1) * len(app_list2))

	@classmethod
	def __count_match(cls, list1, list2):
		count = 0
		for element in list1:
			if element in list2:
				count += 1
		return count

def calculate_top_5(app, user_download_history,result):
	#create a dict to store each other app and its similarity to this app 
	app_similarity = {}

	for apps in user_download_history:
		#calculate the similarity
		similarity = Helper.cosine_similarity([app], apps)
		for other_app in apps:
			if app_similarity.has_key(other_app):
				app_similarity[other_app] = similarity + app_similarity[other_app]
			else:
				app_similarity[other_app] = similarity
	if not app_similarity.has_key(app):
		return

	app_similarity.pop(app)
	sorted_tups = sorted(app_similarity.items(), key = operator.itemgetter(1), reverse = True)
	top_5_app = [sorted_tups[0][0], sorted_tups[1][0], sorted_tups[2][0], sorted_tups[3][0],sorted_tups[4][0]]
	if not result.has_key(app):
		result[app] = top_5_app
	#print("top_5_app " + str(app) + ":\t" + str(top_5_app))
	#DataService.update_app_info({'app_id': app}, {'$set': {'top_5_app': top_5_app}})

def main():
	try:
		start = time.clock()
		client = MongoClient('localhost', 27017)
		DataService.init(client)

		user_download_history = DataService.retrieve_user_download_history()
		app_ids = DataService.retrieve_all_app_id()

		top_5_apps = {}
		
		for appp in app_ids:
			calculate_top_5(appp, user_download_history.values(),top_5_apps)

		for users in user_download_history.keys():
			users_app = user_download_history[users]
			all_possible_app = {}
			#sorted_tups = calculate_top_5_user(users, user_download_history,top_5_apps,all_possible_app)
			for used_app_id in users_app:
				top_5_possible_app = top_5_apps[used_app_id]
				for i in top_5_possible_app:
					if i in all_possible_app:
						all_possible_app[i] = all_possible_app[i] + 1
					else:
						all_possible_app[i] = 1
			sorted_tups = sorted(all_possible_app.items(), key = operator.itemgetter(1), reverse = True)
			top_5_user_app = [sorted_tups[0][0], sorted_tups[1][0], sorted_tups[2][0], sorted_tups[3][0],sorted_tups[4][0]]
			print("top_5_app " + str(users) + ":\t" + str(top_5_user_app))

		end = time.clock()
		print "time elapsed = " + str(end - start)
	except Exception as e:
		print(e)
	finally:
		if 'client' in locals():
			client.close()

if __name__ == "__main__":
	main()