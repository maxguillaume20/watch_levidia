import keyboard


from selenium import webdriver
from selenium.webdriver import FirefoxOptions
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
        self.skip_episode = False

    def run(self):
        self.load()
        self.execute()

    def load(self):
        episode_links = self.open_episodes_page()
        self.total_episodes = len(episode_links)
        self.driver.quit()

    def execute(self):
        while len(self.watched_episodes) < self.total_episodes:
            episode_links = self.open_episodes_page()
            episode_link = self.select_episode_link(episode_links)
            self.click_link(episode_link)
            wootly_link = self.check_for_wootly_link()
            if wootly_link is not None:
                wootly_link.click()
                self.handle_video_player_popup()
                self.play_video()
                self.close_windows()
                self.enter_fullscreen()
                self.wait_until_end_of_episode()
            self.driver.quit()

    def open_episodes_page(self):
        opts = FirefoxOptions()

        self.driver = webdriver.Firefox(options=opts)
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

    def close_windows(self):
        video_window = self.driver.current_window_handle
        handles = list(self.driver.window_handles)
        for handle in handles:
            if handle != video_window:
                self.driver.switch_to.window(handle)
                self.driver.close()
        time.sleep(LevidiaWatcher.SLEEP_TIME)
        self.driver.switch_to.window(video_window)

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

    def play_video(self):
        iframe = self.driver.find_element(by=By.TAG_NAME, value="Iframe")
        self.driver.switch_to.frame(iframe)
        prime = self.driver.find_element(by=By.CLASS_NAME, value="play-button")
        prime.click()
        time.sleep(LevidiaWatcher.SLEEP_TIME)
        return iframe

    def enter_fullscreen(self):
        iframe = self.driver.find_element(by=By.TAG_NAME, value="Iframe")
        iframe.click()
        iframe.click()
        self.driver.switch_to.frame(iframe)
        self.driver.execute_script("document.querySelector('video').requestFullscreen()")

    def wait_until_end_of_episode(self):
        self.skip_episode = False
        duration = self.driver.execute_script("return document.querySelector('video').duration")
        if duration is not None:
            keyboard.add_hotkey("space", self.skip)
            start_time = time.time()
            while time.time() - start_time < duration and not self.skip_episode:
                continue
            keyboard.remove_all_hotkeys()

    def skip(self):
        self.skip_episode = True


if __name__ == "__main__":
    watcher = LevidiaWatcher()
    watcher.run()
