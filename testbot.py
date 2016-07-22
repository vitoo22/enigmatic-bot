from selenium import webdriver
# from selenium.webdriver.firefox.webdriver import FirefoxProfile
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from random import randint
import time, datetime
import sqlite3


# profile = FirefoxProfile("/Users/vituz/Library/Application Support/Firefox/Profiles/5nzbhuh7.default/")
browser = webdriver.Firefox()

hashtags = ['travel', 'travels', 'sea', 'adventure', 'globetrotter', 'world']

url_jar = []

db = sqlite3.connect('instaDB.db')

days = 2
hours = 24*days
waiting_time = 60*hours
times_per_hour = 20

username = 'vitoo22'
password = 'Serginho27!'

def login(username, password):
	browser.get('https://www.instagram.com/accounts/login/')
	# global cookies
	# cookies = browser.get_cookies()
	# print(cookies)
	user = WebDriverWait(browser, 10).until(
		EC.element_to_be_clickable((
			By.XPATH, "/html/body/span/div/article/div/div[1]/div/form/div[1]/input")))
	passs = WebDriverWait(browser, 10).until(
		EC.element_to_be_clickable((
			By.XPATH, "/html/body/span/div/article/div/div[1]/div/form/div[2]/input")))
	user.send_keys(username)
	passs.send_keys(password)
	login_button = WebDriverWait(browser, 10).until(
			EC.element_to_be_clickable((
				By.XPATH, "/html/body/span/div/article/div/div[1]/div/form/span/button")))
	login_button.click()
	time.sleep(1)
	print("Login done")
	# return cookies

def follow(times_per_hour):
	start = time.time()
	global total_follow
	total_follow = 0
	# follow x new users based on a random hashtag from hashtags.
# !!!!!  devo implementare di non seguire user che sono presenti nella tabella old_people del database !!!!!
	for times in range(0, times_per_hour):
		hashtag = hashtags[randint(0,len(hashtags)-1)]
		browser.get('https://www.instagram.com/explore/tags/' + hashtag + '/')
		# target and open most recent picture
		new_targeted_picture = WebDriverWait(browser, 10).until(
			EC.element_to_be_clickable((
				By.XPATH, "/html/body/span/section/main/article/div[2]/div[1]/div[1]/a[1]")))
		new_targeted_picture.click()
		# target and open related user's profile.
		new_followed_person = WebDriverWait(browser, 10).until(
			EC.element_to_be_clickable((
				By.XPATH,"/html/body/div[2]/div/div[2]/div/article/header/div/a[1]")))
		new_followed_person.click()
		# target button for follow.
		to_be_clicked_for_follow = WebDriverWait(browser, 10).until(
			EC.element_to_be_clickable((
				By.XPATH,"/html/body/span/section/main/article/header/div[2]/div[1]/span/button")))
		# verify if already following or not following, then act accordingly.
		if to_be_clicked_for_follow.text == 'Follow':
			to_be_clicked_for_follow.click()
			time.sleep(randint(3,6))
			new_followed_person_url = browser.current_url
			user = new_followed_person_url.replace("https://www.instagram.com/", "")
			user = user.replace("/", "")
			url_jar.append(new_followed_person_url)
			total_follow += 1
			# update database table url_jar with this user's details.
			c = db.cursor()
			c.execute('''INSERT INTO url_jar ("time", "url", "username", "hashtag") 
				VALUES (?, ?, ?, ?)''', 
				(datetime.datetime.now(), new_followed_person_url, user, hashtag))
			db.commit()
			c.close()
		else:
			new_followed_person_url = browser.current_url
			user = new_followed_person_url.replace("https://www.instagram.com/", "")
			user = user.replace("/", "")
		print(total_follow, user)
	# browser.close()
	end = time.time()
	global time_for_follow
	time_for_follow = end - start
	print("Following done")
	print(time_for_follow)
	return url_jar, total_follow, time_for_follow


def unfollow():
	start = time.time()
	global total_unfollow
	total_unfollow = 0
	users_to_be_unfollowed = []
	c = db.cursor()
	# populate users_to_be_unfollowed list from url_jar db table.
	for row in c.execute('''SELECT * FROM url_jar'''):
		interval = datetime.datetime.now() - datetime.datetime.strptime(row[0][0:18], '%Y-%m-%d  %H:%M:%S')
		if interval > datetime.timedelta(minutes=waiting_time):
			users_to_be_unfollowed.append(row)
	# go through all the users in the url_jar table and act accordingly.
	for user in users_to_be_unfollowed:
		interval = datetime.datetime.now() - datetime.datetime.strptime(user[0][0:18], '%Y-%m-%d  %H:%M:%S')
		if interval > datetime.timedelta(minutes=waiting_time):
			browser.get('https://www.instagram.com/' + user[2])
			# try if element is there, if yes check if we are following user or not and then act accordingly.
			try:
				if total_unfollow < times_per_hour:
					# get element, which is the follow/unfollow instagram button.
					element = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((
							By.XPATH,"/html/body/span/section/main/article/header/div[2]/div[1]/span/button")))
					# if we are not following the user: delete instance from url_yar and move on.
					if element.text == "Follow":
						c.execute('''DELETE FROM url_jar WHERE username=?''', (user[2],))
						db.commit()
					# if we are following the user: click to unfollow, remove instance form url_yar and add instance to old_people. 
					elif element.text == "Following":
						element.click()
						time.sleep(1)
						total_unfollow += 1
						c.execute('''INSERT INTO old_people ("start_time", "url", "username", "end_time", "hashtag") 
							VALUES (?, ?, ?, ?, ?)''', 
							(user[0], user[1], user[2], datetime.datetime.now(), user[3]))
						c.execute('''DELETE FROM url_jar WHERE username=?''', (user[2],))
						db.commit()
				else:
					break
			# if element is not there, catch timeout exception and act accordingly.
			except TimeoutException:
				c.execute('''DELETE FROM url_jar WHERE username=?''', (user[2],))
				db.commit()
			print(total_unfollow, user[2])
	browser.close()
	c.close()
	end = time.time()
	print("Unfollowing done")
	global time_for_unfollow
	time_for_unfollow = end - start
	print(time_for_unfollow)
	return total_unfollow, time_for_unfollow


def final_stats():
	total_time = time_for_follow + time_for_unfollow
	print("Total time: {}".format(total_time/60))
	print("total followed users: {}".format(total_follow))
	print("total unfollowed users: {}".format(total_unfollow))
	if total_follow != total_unfollow:
		print("There is a mismatch in the follow/unfollow count: {}".format(total_follow - total_unfollow))
	c = db.cursor()
	start_of_last_hour = datetime.datetime.now() - datetime.timedelta(minutes=60)
	print(start_of_last_hour)
	number_of_users_followed_in_last_hour = c.execute(
		'''SELECT COUNT(*) FROM url_jar 
		WHERE time >= ?''', (start_of_last_hour,))
	print("Last hour followed users: {}".format(
		number_of_users_followed_in_last_hour.fetchone()[0]))
	number_of_users_unfollowed_in_last_hour = c.execute(
		'''SELECT COUNT(*) FROM old_people 
		WHERE end_time >= ?''', (start_of_last_hour,))
	print("Last hour unfollowed users: {}".format(
		number_of_users_unfollowed_in_last_hour.fetchone()[0]))
	browser.close()
	c.close()

login(username, password)
follow(times_per_hour)
unfollow()
final_stats()


# aggiungere al db una tabella che tiene le statistiche

