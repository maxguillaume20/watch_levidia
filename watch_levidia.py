from selenium.webdriver import Firefox, FirefoxProfile
from selenium.webdriver.common.by import By
import time
import random

tv_show_url = "https://www.levidia.ch/tv-show.php?watch=its-always-sunny-in-philadelphia"


class LevidiaWatcher(object):

    SLEEP_TIME = 3

    def __init__(self):
        self.driver = None              #type: Firefox
        self.watched_episodes = []
        self.total_episodes = 0

    def execute(self):
        self.load()
        self.run()

    def load(self):
        episode_links = self.open_episodes_page()
        self.total_episodes = len(episode_links)
        self.driver.quit()

    def run(self):
        while len(self.watched_episodes) < self.total_episodes:
            episode_links = self.open_episodes_page()
            episode_link = self.select_episode_link(episode_links)

            self.click_link(episode_link)

            wootly_link = self.check_for_wootly_link()
            if wootly_link is not None:
                wootly_link.click()
                self.handle_video_player_popup()

                self.driver.find_element(by=By.TAG_NAME, value="Iframe").click()
                time.sleep(LevidiaWatcher.SLEEP_TIME)

                video_window = self.driver.current_window_handle
                self.close_all_other_windows(video_window)
                time.sleep(LevidiaWatcher.SLEEP_TIME)

                self.driver.switch_to.frame(self.driver.find_element(by=By.TAG_NAME, value="Iframe"))
                time.sleep(LevidiaWatcher.SLEEP_TIME)

                duration = self.driver.execute_script("return document.querySelector('video').duration")
                time.sleep(duration)
            self.driver.quit()

    def open_episodes_page(self):
        self.driver = Firefox(firefox_profile=FirefoxProfile())
        self.driver.get(tv_show_url)
        time.sleep(LevidiaWatcher.SLEEP_TIME)
        self.wait_for_bad_gateway()
        unwatched_episode_links = []
        episode_links = self.get_all_episodes_links()
        for episode_link in episode_links:
            episode_name = self.get_episode_name(episode_link)
            if episode_name not in self.watched_episodes:
                unwatched_episode_links.append(episode_link)
        return unwatched_episode_links

    def get_episode_name(self, episode_link):
        return episode_link.text.split('\n')[0]

    def click_link(self, link):
        link.click()
        time.sleep(LevidiaWatcher.SLEEP_TIME)
        self.wait_for_bad_gateway()

    def wait_for_bad_gateway(self):
        while "Bad Gateway" in self.driver.page_source:
            self.driver.refresh()
            time.sleep(LevidiaWatcher.SLEEP_TIME)

    def get_all_episodes_links(self):
        return self.driver.find_elements(by=By.CLASS_NAME, value="mlist.links")

    def close_all_other_windows(self, except_window):
        handles = list(self.driver.window_handles)
        for handle in handles:
            if handle != except_window:
                self.driver.switch_to.window(handle)
                self.driver.close()
        time.sleep(LevidiaWatcher.SLEEP_TIME)
        self.driver.switch_to.window(except_window)

    def select_episode_link(self, episode_links):
        random_link = episode_links[random.randint(0, len(episode_links) - 1)]
        self.watched_episodes.append(self.get_episode_name(random_link))
        return random_link.find_element(by=By.TAG_NAME, value="a")

    def check_for_wootly_link(self):
        webplayer_links = self.driver.find_elements(by=By.CLASS_NAME, value="xxx0")
        for link in webplayer_links:
            if link.find_element(by=By.CLASS_NAME, value="kiri.xxx1.xx12").text == "Wootly":
                return link.find_element(by=By.CLASS_NAME, value="xxx.xflv")

    def handle_video_player_popup(self):
        repeat = True
        while repeat:
            repeat = False
            time.sleep(LevidiaWatcher.SLEEP_TIME)
            for handle in self.driver.window_handles:
                if handle != self.driver.current_window_handle:
                    old_handle = self.driver.current_window_handle
                    self.driver.switch_to.window(handle)
            if "Bad Gateway" in self.driver.page_source:
                repeat = True
                self.driver.close()
                self.driver.switch_to.window(old_handle)
        time.sleep(LevidiaWatcher.SLEEP_TIME)


if __name__ == "__main__":
    watcher = LevidiaWatcher()
    watcher.execute()
