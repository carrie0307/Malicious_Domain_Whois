from pyvirtualdisplay import Display
from selenium import webdriver
import selenium
import time


def get_final_url(url):
	with Display(backend="xvfb", size=(1440, 900)):
		driver = webdriver.Chrome()
		driver.maximize_window()
		driver.get(url)
		url = driver.current_url
		driver.quit()
		return url


if __name__ == '__main__':
	start = time.time()
	print get_final_url('http://016.emmfpg.xyz/')
	print str(time.time() - start)
